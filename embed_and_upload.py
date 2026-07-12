import os
import json
import time
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import psycopg2
from dotenv import load_dotenv

load_dotenv()

print("Connecting to Neon...")
conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
cursor = conn.cursor()
print("Connected!")

print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded!")

def get_uploaded_video_ids():
    cursor.execute("SELECT DISTINCT video_id FROM transcripts")
    rows = cursor.fetchall()
    ids = set()
    for row in rows:
        vid = row[0].rsplit('_', 1)[0]
        ids.add(vid)
    print(f"Already uploaded: {len(ids)} videos")
    return ids

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks

def process_and_upload(json_file):
    print(f"\nProcessing {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        transcripts = json.load(f)
    print(f"Found {len(transcripts)} transcripts")
    
    uploaded_ids = get_uploaded_video_ids()
    total_chunks = 0
    skipped = 0
    
    for transcript in tqdm(transcripts):
        if not transcript.get('transcript'):
            continue
        if transcript['video_id'] in uploaded_ids:
            skipped += 1
            continue
        
        chunks = chunk_text(transcript['transcript'])
        for i, chunk in enumerate(chunks):
            embedding = model.encode(chunk).tolist()
            cursor.execute("""
                INSERT INTO transcripts 
                (video_id, title, channel, video_type, upload_date, url, speaker_verified, chunk_text, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                f"{transcript['video_id']}_{i}",
                transcript.get('title', ''),
                transcript.get('channel', ''),
                transcript.get('video_type', 'direct'),
                transcript.get('upload_date', ''),
                transcript.get('url', ''),
                transcript.get('speaker_verified', True),
                chunk,
                embedding
            ))
            total_chunks += 1
        
        conn.commit()
    
    print(f"✅ Done! Uploaded {total_chunks} new chunks, skipped {skipped} already uploaded")

if __name__ == "__main__":
    file = Path('transcripts_data/transcripts_Financial_Education.json')
    process_and_upload(file)
    cursor.close()
    conn.close()
    print("\n🎉 Upload complete!")