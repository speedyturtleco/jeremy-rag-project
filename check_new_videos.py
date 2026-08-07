"""
check_new_videos.py
--------------------
Run this manually from home whenever you want to check for new Jeremy videos.

What it does:
  1. Looks at the newest 5 videos on each channel (free — just a listing, no proxy needed).
  2. Checks which of those video IDs are already in Neon.
  3. Downloads the transcript + real upload date for any that are missing (home IP, no proxy).
  4. Chunks + embeds + inserts them straight into Neon (same logic as embed_and_upload.py).

No local JSON file is kept — Neon is the single source of truth, same as auto_update.py.

Safety: only checks the newest 5 per channel, so this can never accidentally bulk-download
the reaction channel backlog. Keeps a 15-30s delay between transcript pulls to stay under
home-IP rate limit risk (per project notes: 10-15 videos is a safe burst size).

Usage:
    python check_new_videos.py
"""

import os
import time
import random
import psycopg2
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# ---- Config: same channels as your other scripts ----
CHANNELS = [
    {
        "url": "https://www.youtube.com/@FinancialEducation/videos",
        "name": "Financial Education",
        "video_type": "direct",
    },
    {
        "url": "https://www.youtube.com/channel/UCCmJVw9xQfYuuAAwZGedKRg/videos",
        "name": "1000xstocks",
        "video_type": "direct",
    },
    {
        "url": "https://www.youtube.com/@jeremylefebvremakesmoney7934/videos",
        "name": "Jeremy Lefebvre Makes Money",
        "video_type": "reaction",
    },
]

NEWEST_N = 5          # how many recent videos to check per channel
DELAY_RANGE = (15, 30)  # seconds between transcript pulls, per project notes

print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded!\n")

print("Connecting to Neon...")
conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
cursor = conn.cursor()
print("Connected!\n")


def get_existing_video_ids():
    """All video_ids already stored (strip the _chunkindex suffix)."""
    cursor.execute("SELECT DISTINCT video_id FROM transcripts")
    rows = cursor.fetchall()
    ids = set()
    for row in rows:
        vid = row[0].rsplit('_', 1)[0]
        ids.add(vid)
    return ids


def get_newest_videos(channel_url, n=NEWEST_N):
    """Free listing call - no proxy needed, just metadata."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlist_items': f'1-{n}',
        'cookiefile': 'cookies.txt',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        videos = []
        if result and 'entries' in result:
            for entry in result['entries']:
                if entry and entry.get('id') and len(entry.get('id', '')) == 11:
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'upload_date': entry.get('upload_date'),
                        'url': f"https://youtube.com/watch?v={entry.get('id')}",
                    })
        return videos


def get_upload_date(video_id):
    """Fetch real upload date if the flat listing didn't give one. No proxy - home IP."""
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': 'cookies.txt',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info.get('upload_date')
    except Exception as e:
        print(f"  Date fetch error for {video_id}: {e}")
        return None


def get_transcript(video_id, max_retries=3):
    """No proxy - straight from home IP."""
    for attempt in range(max_retries):
        try:
            ytt = YouTubeTranscriptApi()
            transcript = ytt.fetch(video_id)
            full_text = ' '.join([t.text for t in transcript])
            if full_text and len(full_text.split()) > 100:
                return full_text
        except Exception as e:
            print(f"  Error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(15)
    return None


def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(' '.join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def embed_and_insert(video, channel_name, video_type, transcript_text):
    chunks = chunk_text(transcript_text)
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        cursor.execute("""
            INSERT INTO transcripts
            (video_id, title, channel, video_type, upload_date, url, speaker_verified, chunk_text, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            f"{video['id']}_{i}",
            video.get('title', ''),
            channel_name,
            video_type,
            video.get('upload_date', ''),
            video.get('url', ''),
            video_type == 'direct',
            chunk,
            embedding,
        ))
    conn.commit()
    return len(chunks)


def main():
    existing_ids = get_existing_video_ids()
    print(f"Already have {len(existing_ids)} videos in Neon.\n")

    total_new = 0
    total_chunks = 0

    for channel in CHANNELS:
        print(f"=== Checking {channel['name']} (newest {NEWEST_N}) ===")
        try:
            videos = get_newest_videos(channel['url'])
        except Exception as e:
            print(f"  Could not list videos: {e}\n")
            continue

        new_videos = [v for v in videos if v['id'] not in existing_ids]
        print(f"  Found {len(new_videos)} new out of {len(videos)} checked.")

        for video in new_videos:
            print(f"\n  → New: {video['title']}")
            time.sleep(random.uniform(*DELAY_RANGE))

            transcript_text = get_transcript(video['id'])
            if not transcript_text:
                print(f"    ✗ No transcript available, skipping.")
                continue

            if not video['upload_date']:
                time.sleep(random.uniform(2, 4))
                video['upload_date'] = get_upload_date(video['id'])

            n_chunks = embed_and_insert(video, channel['name'], channel['video_type'], transcript_text)
            print(f"    ✓ Uploaded {n_chunks} chunks (upload_date: {video['upload_date']})")
            total_new += 1
            total_chunks += n_chunks

        print()

    print(f"🎉 Done! {total_new} new videos, {total_chunks} chunks uploaded.")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
