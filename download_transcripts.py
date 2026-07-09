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

def load_existing_transcripts(output_file):
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
            return {t['video_id']: t for t in existing}
    return {}

def save_transcripts(transcripts, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(list(transcripts.values()), f, indent=2, ensure_ascii=False)

def get_transcript(video_id):
    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id)
        full_text = ' '.join([t.text for t in transcript])
        if full_text and len(full_text.split()) > 100:
            return full_text
    except Exception as e:
        print(f"Error: {e}")
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
        time.sleep(random.uniform(8, 15))
        transcript = get_transcript(video['id'])
        if transcript:
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