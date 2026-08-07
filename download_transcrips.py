import os
import json
import time
import random
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

def get_channel_video_ids(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlist_items': '1-9999',
        'cookiefile': 'cookies.txt',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        if 'entries' in result:
            videos = []
            for entry in result['entries']:
                if entry and entry.get('id') and len(entry.get('id', '')) == 11:
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'upload_date': entry.get('upload_date'),
                        'url': f"https://youtube.com/watch?v={entry.get('id')}"
                    })
            return videos
    return []

# ============ NEW: fetch the real upload date for one video ============
def get_upload_date(video_id):
    """Fetch full metadata for a single video and return its upload date
    as a 'YYYYMMDD' string (e.g. '20240315'), or None if it fails.
    Uses the Decodo proxy, same as transcript fetching."""
    proxy_url = f"http://{os.getenv('DECODO_USERNAME')}:{os.getenv('DECODO_PASSWORD')}@gate.decodo.com:10000"
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': 'cookies.txt',
        'proxy': proxy_url,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info.get('upload_date')
    except Exception as e:
        print(f"  Date fetch error for {video_id}: {e}")
        return None
# =======================================================================

def load_existing_transcripts(output_file):
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
            return {t['video_id']: t for t in existing}
    return {}

def save_transcripts(transcripts, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(list(transcripts.values()), f, indent=2, ensure_ascii=False)

def get_transcript(video_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            from youtube_transcript_api.proxies import GenericProxyConfig
            proxy = GenericProxyConfig(
                http_url=f"http://{os.getenv('DECODO_USERNAME')}:{os.getenv('DECODO_PASSWORD')}@gate.decodo.com:10000",
                https_url=f"http://{os.getenv('DECODO_USERNAME')}:{os.getenv('DECODO_PASSWORD')}@gate.decodo.com:10000",
            )
            ytt = YouTubeTranscriptApi(proxy_config=proxy)
            transcript = ytt.fetch(video_id)
            full_text = ' '.join([t.text for t in transcript])
            if full_text and len(full_text.split()) > 100:
                return full_text
        except Exception as e:
            print(f"Error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(15)
    return None

def process_channel(channel_url, channel_name, video_type='direct'):
    print(f"\nProcessing channel: {channel_name}")
    print("Getting video list...")
    output_file = os.path.join('transcripts_data', f"transcripts_{channel_name.replace(' ', '_')}.json")
    existing = load_existing_transcripts(output_file)
    print(f"Already have {len(existing)} transcripts saved")
    videos = get_channel_video_ids(channel_url)
    print(f"Found {len(videos)} videos total")
    new_count = 0
    skip_count = 0
    for i, video in enumerate(videos):
        if video['id'] in existing:
            skip_count += 1
            print(f"Skipping {i+1}/{len(videos)}: {video['title']} (already have it)")
            continue
        print(f"Processing {i+1}/{len(videos)}: {video['title']}")
        time.sleep(random.uniform(5, 10))
        transcript = get_transcript(video['id'])
        if transcript:
            # ============ NEW: fetch the real date if flat extraction didn't give one ============
            if not video['upload_date']:
                time.sleep(random.uniform(2, 4))
                video['upload_date'] = get_upload_date(video['id'])
                print(f"  📅 Upload date: {video['upload_date']}")
            # ======================================================================================
            existing[video['id']] = {
                'video_id': video['id'],
                'title': video['title'],
                'upload_date': video['upload_date'],
                'url': video['url'],
                'channel': channel_name,
                'video_type': video_type,
                'speaker_verified': video_type == 'direct',
                'transcript': transcript
            }
            save_transcripts(existing, output_file)
            new_count += 1
            print(f"✓ Got transcript ({new_count} new, {len(existing)} total)")
        else:
            print(f"✗ No transcript available")
    print(f"\n✅ Done! {len(existing)} total transcripts in {output_file}")
    print(f"   {new_count} new, {skip_count} already existed")
    return existing

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@FinancialEducation/videos"
    channel_name = "Financial Education"
    process_channel(channel_url, channel_name, 'direct')

    # After the test works, you can run other channels by swapping these in:
    #
    # Financial Education (already downloaded — will skip existing videos):
    # channel_url = "https://www.youtube.com/@FinancialEducation/videos"
    # channel_name = "Financial Education"
    # process_channel(channel_url, channel_name, 'direct')
    #
    # Reaction channel (859 videos — the big one, run when ready):
    # channel_url = "https://www.youtube.com/@jeremylefebvremakesmoney7934/videos"
    # channel_name = "Jeremy Lefebvre Makes Money"
    # process_channel(channel_url, channel_name, 'reaction')