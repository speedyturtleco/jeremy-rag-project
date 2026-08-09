import os
import json
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from download_transcrips import get_upload_date

load_dotenv()

def backfill_dates(json_file):
    path = Path(json_file)
    with open(path, 'r', encoding='utf-8') as f:
        transcripts = json.load(f)

    missing = [t for t in transcripts if not t.get('upload_date')]
    print(f"Found {len(transcripts)} total videos, {len(missing)} missing dates")

    updated = 0
    failed = 0

    for i, transcript in enumerate(missing):
        video_id = transcript['video_id']
        print(f"[{i+1}/{len(missing)}] Fetching date for {video_id}: {transcript.get('title', '')[:60]}")

        date = get_upload_date(video_id)
        if date:
            transcript['upload_date'] = date
            updated += 1
            print(f"  📅 Got date: {date}")
        else:
            failed += 1
            print(f"  ✗ Could not get date")

        # Save progress every 10 videos so interruptions don't lose work
        if (i + 1) % 10 == 0:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(transcripts, f, indent=2, ensure_ascii=False)
            print(f"  💾 Progress saved ({updated} updated so far)")

        time.sleep(random.uniform(3, 6))

    # Final save
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(transcripts, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done! {updated} dates updated, {failed} failed")

if __name__ == "__main__":
    backfill_dates('transcripts_data/transcripts_Financial_Education.json')