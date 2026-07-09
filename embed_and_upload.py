import os
import json
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded!")

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
    total_chunks = 0
    for transcript in tqdm(transcripts):
        if not transcript.get('transcript'):
            continue
        chunks = chunk_text(transcript['transcript'])
        for i, chunk in enumerate(chunks):
            embedding = model.encode(chunk).tolist()
            supabase.table('transcripts').insert({
                'video_id': f"{transcript['video_id']}_{i}",
                'title': transcript.get('title', ''),
                'channel': transcript.get('channel', ''),
                'video_type': transcript.get('video_type', 'direct'),
                'upload_date': transcript.get('upload_date', ''),
                'url': transcript.get('url', ''),
                'speaker_verified': transcript.get('speaker_verified', True),
                'chunk_text': chunk,
                'embedding': embedding
            }).execute()
            total_chunks += 1
    print(f"✅ Done! Uploaded {total_chunks} chunks from {json_file}")

if __name__ == "__main__":
    file = Path('transcripts_data/transcripts_Financial_Education.json')
    process_and_upload(file)
    print("\n🎉 Upload complete!")