"""
auto_update.py
---------------
Meant to run on a schedule (via GitHub Actions) to catch NEW videos only.

What it does, per channel:
  1. List current videos on the channel (free - no proxy needed).
  2. Check which of those video IDs are already in Neon.
  3. Take only the newest N not-yet-uploaded videos (SAFETY CAP - see MAX_NEW_PER_CHANNEL_PER_RUN).
     This script is NOT for bulk backfilling. Bulk backfill = download_transcrips.py, run manually.
  4. Download the transcript (uses Decodo proxy - this is the only step that costs bandwidth).
  5. Chunk + embed + insert directly into Neon.

Does not maintain local transcripts_data/*.json files, since GitHub Actions runners are
ephemeral (nothing written to disk persists between runs). Neon is the single source of
truth for "have we already got this video" - so nothing is lost between runs.
"""

import os
import time
import random
from dotenv import load_dotenv
import psycopg2
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
from sentence_transformers import SentenceTransformer

load_dotenv()

# ---- SAFETY CAP ----
# Max NEW videos to pull per channel per run. Keeps a scheduled run from accidentally
# turning into a full backfill (e.g. reaction channel has ~850+ videos not yet in Neon).
MAX_NEW_PER_CHANNEL_PER_RUN = 5

CHANNELS = [
    {
        "name": "Financial Education",
        "url": "https://www.youtube.com/@FinancialEducation/videos",
        "video_type": "direct",
    },
    {
        "name": "1000xstocks",
        "url": "https://www.youtube.com/channel/UCCmJVw9xQfYuuAAwZGedKRg/videos",
        "video_type": "direct",
    },
    {
        "name": "Jeremy Lefebvre Makes Money",
        "url": "https://www.youtube.com/@jeremylefebvremakesmoney7934/videos",
        "video_type": "reaction",
    },
]

DECODO_PROXY_URL = f"http://{os.getenv('DECODO_USERNAME')}:{os.getenv('DECODO_PASSWORD')}@gate.decodo.com:10000"


def get_neon_connection():
    return psycopg2.connect(os.getenv("NEON_DATABASE_URL"))


def get_existing_video_ids(conn):
    """All base video IDs (without the _<chunk_index> suffix) already in Neon, across all channels."""
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT video_id FROM transcripts")
    rows = cursor.fetchall()
    cursor.close()
    ids = set()
    for row in rows:
        ids.add(row[0].rsplit("_", 1)[0])
    return ids


def get_channel_video_list(channel_url):
    """Lightweight listing - no proxy needed. Returns videos in the order yt-dlp lists them
    (newest first for /videos tabs)."""
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "playlist_items": "1-30",  # only need to glance at the newest handful
        "cookiefile": "cookies.txt",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        videos = []
        if result and "entries" in result:
            for entry in result["entries"]:
                if entry and entry.get("id") and len(entry.get("id", "")) == 11:
                    videos.append({
                        "id": entry.get("id"),
                        "title": entry.get("title"),
                        "upload_date": entry.get("upload_date"),
                        "url": f"https://youtube.com/watch?v={entry.get('id')}",
                    })
        return videos


def get_upload_date(video_id):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "cookiefile": "cookies.txt",
        "proxy": DECODO_PROXY_URL,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info.get("upload_date")
    except Exception as e:
        print(f"  Date fetch error for {video_id}: {e}")
        return None


def get_transcript(video_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            proxy = GenericProxyConfig(
                http_url=DECODO_PROXY_URL,
                https_url=DECODO_PROXY_URL,
            )
            ytt = YouTubeTranscriptApi(proxy_config=proxy)
            transcript = ytt.fetch(video_id)
            full_text = " ".join([t.text for t in transcript])
            if full_text and len(full_text.split()) > 100:
                return full_text
        except Exception as e:
            print(f"  Transcript error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(15)
    return None


def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def process_new_video(conn, model, video, channel_name, video_type):
    print(f"  Fetching transcript for: {video['title']}")
    transcript = get_transcript(video["id"])
    if not transcript:
        print("  X No transcript available - skipping")
        return 0

    if not video["upload_date"]:
        time.sleep(random.uniform(2, 4))
        video["upload_date"] = get_upload_date(video["id"])

    chunks = chunk_text(transcript)
    cursor = conn.cursor()
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        cursor.execute(
            """
            INSERT INTO transcripts
            (video_id, title, channel, video_type, upload_date, url, speaker_verified, chunk_text, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                f"{video['id']}_{i}",
                video["title"],
                channel_name,
                video_type,
                video["upload_date"],
                video["url"],
                video_type == "direct",
                chunk,
                embedding,
            ),
        )
    conn.commit()
    cursor.close()
    print(f"  Uploaded {len(chunks)} chunks")
    return len(chunks)


def main():
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    conn = get_neon_connection()
    existing_ids = get_existing_video_ids(conn)
    print(f"Neon currently has {len(existing_ids)} distinct videos.\n")

    summary = {}
    any_new_found = False

    for channel in CHANNELS:
        print(f"Checking channel: {channel['name']}")
        try:
            videos = get_channel_video_list(channel["url"])
        except Exception as e:
            print(f"  X Could not list videos for {channel['name']}: {e}")
            summary[channel["name"]] = "LIST_FAILED"
            continue

        new_videos = [v for v in videos if v["id"] not in existing_ids]
        new_videos = new_videos[:MAX_NEW_PER_CHANNEL_PER_RUN]

        if not new_videos:
            print("  Nothing new.\n")
            summary[channel["name"]] = 0
            continue

        any_new_found = True
        print(f"  Found {len(new_videos)} new video(s) (capped at {MAX_NEW_PER_CHANNEL_PER_RUN}/run)")
        total_chunks = 0
        for video in new_videos:
            time.sleep(random.uniform(5, 10))
            total_chunks += process_new_video(conn, model, video, channel["name"], channel["video_type"])
        summary[channel["name"]] = total_chunks
        print()

    conn.close()

    print("=" * 50)
    print("SUMMARY")
    for name, result in summary.items():
        print(f"  {name}: {result}")
    print("=" * 50)

    if not any_new_found:
        print("No new videos found across any channel this run.")


if __name__ == "__main__":
    main()
