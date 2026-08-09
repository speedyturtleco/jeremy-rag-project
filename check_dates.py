import json
from pathlib import Path

def check_dates(json_file):
    path = Path(json_file)
    if not path.exists():
        print(f"⚠️  {json_file} not found, skipping")
        return

    with open(path, 'r', encoding='utf-8') as f:
        transcripts = json.load(f)

    total = len(transcripts)
    has_date = 0
    blank = 0
    blank_titles = []

    for t in transcripts:
        date = t.get('upload_date')
        if date:
            has_date += 1
        else:
            blank += 1
            blank_titles.append(t.get('title', 'Unknown title'))

    print(f"\n📁 {json_file}")
    print(f"   Total videos: {total}")
    print(f"   ✅ Has real date: {has_date} ({has_date/total*100:.1f}%)")
    print(f"   ❌ Blank/missing date: {blank} ({blank/total*100:.1f}%)")

    if blank_titles:
        print(f"\n   First 10 videos with blank dates:")
        for title in blank_titles[:10]:
            print(f"     - {title}")

files = [
    'transcripts_data/transcripts_Financial_Education.json',
    'transcripts_data/transcripts_1000xstocks.json',
    'transcripts_data/transcripts_Jeremy_Lefebvre_Makes_Money.json',
    'transcripts_data/transcripts_Eric_Cuka.json',
]

for f in files:
    check_dates(f)