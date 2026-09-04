import os
import re
import json
import streamlit as st
from sentence_transformers import SentenceTransformer
import psycopg2
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

JEREMY_CHANNELS = ['Financial Education', 'Jeremy Lefebvre Makes Money']

# ============ Feature 1, Mode 1: recency questions ("what's the latest video from X") ============
# Maps how a user might refer to a creator to the actual `channel` value(s) in Neon.
# 'jeremy' is ambiguous (his main channel + the reaction channel where he's still the owner),
# so it maps to both - the query below just returns whichever is actually newest.
CHANNEL_ALIASES = {
    'jeremy': ['Financial Education', 'Jeremy Lefebvre Makes Money'],
    'jeremy lefebvre': ['Financial Education', 'Jeremy Lefebvre Makes Money'],
    'financial education': ['Financial Education'],
    '1000xstocks': ['1000xstocks'],
    'eric': ['Eric Cuka'],
    'eric cuka': ['Eric Cuka'],
}

RECENCY_PATTERN = re.compile(
    r'\b(latest|newest|most recent|last)\b.{0,15}\bvideo\b|\bvideo\b.{0,15}\b(latest|newest|most recent)\b',
    re.IGNORECASE
)


def detect_recency_question(question):
    """True if the question is literally asking for the newest/latest video, e.g.
    'what is the latest video from Eric'. Deliberately narrow - only catches the
    specific bug we found (semantic search has no concept of recency), not general
    'what's Jeremy's current opinion' style questions."""
    return bool(RECENCY_PATTERN.search(question))


VIDEO_URL_PATTERN = re.compile(r'youtube\.com/watch\?v=([A-Za-z0-9_-]{6,})')

SUMMARY_FOLLOWUP_PATTERN = re.compile(
    r'\b(summar\w*|breakdown|break\s?down|explain|tell me more about)\b.{0,20}\bvideo\b',
    re.IGNORECASE
)


def detect_video_summary_question(question):
    """True for follow-ups like 'summarize the video' / 'break down that video' that refer
    back to a specific video already mentioned in the conversation, rather than a new topic
    search."""
    return bool(SUMMARY_FOLLOWUP_PATTERN.search(question))


def find_last_mentioned_video_id(history):
    """Scans backward through the conversation for the most recent YouTube URL the app itself
    cited in an answer, and returns just the video ID part of it."""
    for msg in reversed(history):
        if msg['role'] == 'assistant':
            match = VIDEO_URL_PATTERN.search(msg['content'])
            if match:
                return match.group(1)
    return None


def extract_channels_from_question(question):
    """Returns a list of Neon `channel` values mentioned in the question, or None if no
    creator was named (meaning: search across all channels)."""
    q = question.lower()
    matched = []
    for alias, channels in CHANNEL_ALIASES.items():
        if alias in q:
            for c in channels:
                if c not in matched:
                    matched.append(c)
    return matched or None


def get_latest_videos(channels=None, limit=3):
    """Direct ORDER BY upload_date DESC query - bypasses semantic search entirely.
    Returns one representative chunk per video (for context), most recent videos first."""
    conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
    cursor = conn.cursor()
    base_query = """
        SELECT * FROM (
            SELECT DISTINCT ON (regexp_replace(video_id, '_[0-9]+$', ''))
                title, channel, video_type, upload_date, url, speaker_verified, chunk_text
            FROM transcripts
            WHERE upload_date IS NOT NULL AND upload_date != ''
            {channel_filter}
            ORDER BY regexp_replace(video_id, '_[0-9]+$', ''), upload_date DESC
        ) sub
        ORDER BY upload_date DESC
        LIMIT %s
    """
    params = []
    if channels:
        channel_filter = "AND channel = ANY(%s)"
        params.append(channels)
    else:
        channel_filter = ""
    params.append(limit)
    cursor.execute(base_query.format(channel_filter=channel_filter), params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            'title': r[0], 'channel': r[1], 'video_type': r[2], 'upload_date': r[3],
            'url': r[4], 'speaker_verified': r[5], 'chunk_text': r[6], 'similarity': 1.0
        }
        for r in results
    ]
def get_video_chunks(video_id, limit=20):
    """Pulls ALL chunks for one specific video by its YouTube ID, in order - used when the
    user is asking about a specific video already identified in the conversation, rather than
    doing a fresh semantic search."""
    conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, channel, video_type, upload_date, url, speaker_verified, chunk_text "
        "FROM transcripts WHERE video_id LIKE %s ORDER BY video_id LIMIT %s",
        (f"{video_id}_%", limit)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            'title': r[0], 'channel': r[1], 'video_type': r[2], 'upload_date': r[3],
            'url': r[4], 'speaker_verified': r[5], 'chunk_text': r[6], 'similarity': 1.0
        }
        for r in results
    ]
# ===================================================================================================

# ============ Feature 1, Mode 2: specific time period ("back in 2021", "in early 2020") ============
YEAR_PATTERN = re.compile(r'\b(20[0-2][0-9])\b')
HALF_PATTERN = re.compile(r'\b(early|late)\b', re.IGNORECASE)


def detect_time_period_question(question):
    """True if the question names a specific year, e.g. 'what did Jeremy say about
    Tesla back in 2021'. A bare year is enough to trigger this - deliberately simple."""
    return bool(YEAR_PATTERN.search(question))


def extract_time_period(question):
    """Pulls the year (as a string, e.g. '2021') and, if present, whether the question
    narrows to 'early' or 'late' that year (used to filter to the first/second half)."""
    year_match = YEAR_PATTERN.search(question)
    if not year_match:
        return None, None
    year = year_match.group(1)
    half_match = HALF_PATTERN.search(question)
    half = half_match.group(1).lower() if half_match else None
    return year, half


def search_transcripts_by_period(query, year, half=None, channels=None, limit=10):
    """Same semantic search as search_transcripts(), but filtered to chunks whose
    upload_date falls within the given year (upload_date is stored as 'YYYYMMDD' text),
    optionally narrowed to the first or second half of that year."""
    embedding = model.encode(query).tolist()
    conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
    cursor = conn.cursor()
    sql = (
        "SELECT title, channel, video_type, upload_date, url, speaker_verified, chunk_text, "
        "1 - (embedding <=> %s::vector) AS similarity FROM transcripts "
        "WHERE 1 - (embedding <=> %s::vector) > 0.25 AND upload_date LIKE %s"
    )
    params = [embedding, embedding, f"{year}%"]
    if half == 'early':
        sql += " AND substring(upload_date, 5, 2) BETWEEN '01' AND '06'"
    elif half == 'late':
        sql += " AND substring(upload_date, 5, 2) BETWEEN '07' AND '12'"
    if channels:
        sql += " AND channel = ANY(%s)"
        params.append(channels)
    sql += " ORDER BY similarity DESC LIMIT %s"
    params.append(limit)
    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            'title': r[0], 'channel': r[1], 'video_type': r[2], 'upload_date': r[3],
            'url': r[4], 'speaker_verified': r[5], 'chunk_text': r[6], 'similarity': r[7]
        }
        for r in results
    ]
# ===================================================================================================

# ============ Feature 1, Modes 3 & 4: timeline / evolution + first mention ============
# Both share the same retrieval (spread relevant chunks across every year that has one),
# they only differ in how the question is framed to Groq afterward.
FIRST_MENTION_PATTERN = re.compile(
    r'\bwhen did\b.{0,40}\b(start|begin)\b|\bfirst\s+(time|mention(ed)?)\b|\bhas\b.{0,20}\balways\b',
    re.IGNORECASE
)

TIMELINE_PATTERN = re.compile(
    r'\bover time\b|\bchanged\b.{0,20}\b(mind|opinion|view|stance)s?\b|\bevolution\b|\bevolved\b|'
    r'\bhistory of\b|\balways\b',
    re.IGNORECASE
)


def detect_first_mention_question(question):
    """True for 'when did Jeremy start liking X', 'has he always thought Y', 'first time
    he mentioned Z' - questions that want the ORIGIN of an opinion, not just how it changed."""
    return bool(FIRST_MENTION_PATTERN.search(question))


def detect_timeline_question(question):
    """True for general 'has his opinion changed over time' style questions."""
    return bool(TIMELINE_PATTERN.search(question))


def search_transcripts_timeline(query, channels=None, similarity_floor=0.2, total_limit=10):
    """Spreads results across ALL years instead of just returning the single best-matching
    chunks (which tend to cluster in whichever year talked about a topic the most). Uses a
    window function to keep only the single best-matching chunk per year, then returns those
    ordered chronologically - giving a year-by-year arc instead of a pile of similar chunks
    from the same time period."""
    embedding = model.encode(query).tolist()
    conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
    cursor = conn.cursor()
    channel_filter = "AND channel = ANY(%s)" if channels else ""
    sql = f"""
        SELECT title, channel, video_type, upload_date, url, speaker_verified, chunk_text, sim
        FROM (
            SELECT title, channel, video_type, upload_date, url, speaker_verified, chunk_text,
                   1 - (embedding <=> %s::vector) AS sim,
                   substring(upload_date, 1, 4) AS yr,
                   ROW_NUMBER() OVER (
                       PARTITION BY substring(upload_date, 1, 4)
                       ORDER BY 1 - (embedding <=> %s::vector) DESC
                   ) AS rn
            FROM transcripts
            WHERE upload_date IS NOT NULL AND upload_date != ''
            {channel_filter}
        ) sub
        WHERE rn = 1 AND sim > %s
        ORDER BY yr ASC
        LIMIT %s
    """
    params = [embedding, embedding]
    if channels:
        params.append(channels)
    params.extend([similarity_floor, total_limit])
    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            'title': r[0], 'channel': r[1], 'video_type': r[2], 'upload_date': r[3],
            'url': r[4], 'speaker_verified': r[5], 'chunk_text': r[6], 'similarity': r[7]
        }
        for r in results
    ]
# ===================================================================================================

# ============ Feature 4: multi-creator comparison mode ============
COMPARISON_JEREMY_ALIASES = ['jeremy', 'financial education', 'jeremy lefebvre']
COMPARISON_ERIC_ALIASES = ['eric', 'eric cuka']


def detect_comparison_question(question):
    """True only when BOTH creators are named in the same question (e.g. 'what do Jeremy
    and Eric think about AMD') - deliberately conservative so a question that just happens
    to mention one creator doesn't get treated as a comparison."""
    q = question.lower()
    mentions_jeremy = any(alias in q for alias in COMPARISON_JEREMY_ALIASES)
    mentions_eric = any(alias in q for alias in COMPARISON_ERIC_ALIASES)
    return mentions_jeremy and mentions_eric


def search_transcripts_by_channels(query, channels, limit=6):
    """Same semantic search as search_transcripts(), restricted to a specific set of
    channels - used to guarantee each creator actually gets represented in a comparison,
    instead of leaving it to chance in one combined top-10 search."""
    embedding = model.encode(query).tolist()
    conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, channel, video_type, upload_date, url, speaker_verified, chunk_text, "
        "1 - (embedding <=> %s::vector) AS similarity FROM transcripts "
        "WHERE 1 - (embedding <=> %s::vector) > 0.25 AND channel = ANY(%s) "
        "ORDER BY similarity DESC LIMIT %s",
        (embedding, embedding, channels, limit)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            'title': r[0], 'channel': r[1], 'video_type': r[2], 'upload_date': r[3],
            'url': r[4], 'speaker_verified': r[5], 'chunk_text': r[6], 'similarity': r[7]
        }
        for r in results
    ]


def search_transcripts_comparison(query, limit_per_creator=5):
    """Runs separate searches for Jeremy's channels and Eric's channel for the same topic,
    then combines them - so both creators are guaranteed real representation."""
    jeremy_chunks = search_transcripts_by_channels(query, JEREMY_CHANNELS, limit_per_creator)
    eric_chunks = search_transcripts_by_channels(query, ['Eric Cuka'], limit_per_creator)
    return jeremy_chunks + eric_chunks
# ===================================================================================================

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# ============ Hybrid keyword fallback for the standard search (Mode 5) ============
# Bug found Sep 3: "what's the latest instance of Jeremy talking about Wynn stock" came back
# with "no mention found," even though a video from 2 days earlier had already been ingested
# and DID mention Wynn - the plain top-10 semantic search across the whole ~36k-chunk corpus
# just didn't surface that one brief mention; it scored below other chunks (or below the 0.3
# floor) since a single passing mention of a stock doesn't stand out semantically. This adds a
# literal keyword safety net for "X stock" style questions, and - when the question is asking
# for the MOST RECENT mention of a topic rather than the latest video overall - sorts results
# by date so "latest" actually means latest instead of just "most semantically similar."
#
# Second bug found same day: "what's Jeremy's latest take on Celcius" (note the typo - should
# be "Celsius") ALSO came back wrong (a low-value unverified reaction-video clip) even though
# a verified, much more recent mention existed in the same Sept 2026 video as the Wynn bug.
# Two separate gaps caused this:
#   1. extract_stock_keyword() only recognized "X stock" phrasing, not "take on X" - broadened
#      below to also catch a topic named at the end of a recency-style question.
#   2. The user's literal typo ("Celcius") doesn't exact-match the correctly-spelled "Celsius"
#      in the transcript, so a plain ILIKE keyword match finds nothing. Added a fuzzy fallback
#      (Postgres pg_trgm's word_similarity) that only kicks in when the exact match comes up
#      empty - best-effort and wrapped in try/except so a missing extension or any DB hiccup
#      just skips the fuzzy step instead of breaking the whole search.
#
# Third bug found Sep 4: "projections for Netflix" was missed entirely - the topic-tail
# extraction below only recognized "on X" / "about X" phrasing, not "for X". Widened the
# preposition list to also catch "for" and "regarding" so a question like "his projections
# for Netflix" (from the "4 Stocks to Go ALL IN September 2026" video) gets the same keyword
# safety net as the "on X"/"about X" phrasings already did.
STOCK_KEYWORD_PATTERN = re.compile(r'\b([A-Za-z][A-Za-z.\-]{1,15})\s+stock\b', re.IGNORECASE)
TOPIC_TAIL_PATTERN = re.compile(r'\b(?:on|about|for|regarding)\s+([A-Za-z][A-Za-z.\-]{1,20})\b\s*[?.!]*\s*$', re.IGNORECASE)
RECENCY_WORD_PATTERN = re.compile(r'\b(latest|newest|most recent|last)\b', re.IGNORECASE)


def wants_most_recent_mention(question):
    """True for 'latest/most recent/last' language that ISN'T Mode 1's 'latest VIDEO' question
    (that one bypasses semantic search entirely via get_latest_videos) - e.g. 'latest instance
    of Jeremy talking about wynn stock'. Used to sort hybrid results by date instead of
    similarity so recency questions about a topic actually surface the newest match, and to
    gate the broader (higher false-positive-risk) topic-tail keyword extraction below."""
    return bool(RECENCY_WORD_PATTERN.search(question)) and not detect_recency_question(question)


def extract_stock_keyword(question):
    """Pulls a likely stock/topic keyword out of the question. Always catches 'X stock'
    phrasing (e.g. 'wynn stock', 'AMD stock'). For recency-style questions only ('latest take
    on X', 'most recent mention of X', 'projections for X') also falls back to whatever topic
    is named at the very end of the question - broader and more false-positive-prone, so it's
    deliberately gated to only the recency-question case rather than applying to every question
    (which could risk dragging in an ILIKE-matched-but-not-actually-relevant chunk for a plain
    topic question)."""
    match = STOCK_KEYWORD_PATTERN.search(question)
    if match:
        return match.group(1)
    if wants_most_recent_mention(question):
        tail_match = TOPIC_TAIL_PATTERN.search(question)
        if tail_match:
            return tail_match.group(1)
    return None
# ===================================================================================================

def search_transcripts(query, limit=10):
    embedding = model.encode(query).tolist()
    conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute(
        'SELECT title, channel, video_type, upload_date, url, speaker_verified, chunk_text, 1 - (embedding <=> %s::vector) AS similarity FROM transcripts WHERE 1 - (embedding <=> %s::vector) > 0.3 ORDER BY similarity DESC LIMIT %s',
        (embedding, embedding, limit)
    )
    results = cursor.fetchall()

    keyword = extract_stock_keyword(query)
    if keyword:
        cursor.execute(
            "SELECT title, channel, video_type, upload_date, url, speaker_verified, chunk_text, "
            "1 - (embedding <=> %s::vector) AS similarity FROM transcripts "
            "WHERE chunk_text ILIKE %s ORDER BY upload_date DESC NULLS LAST LIMIT %s",
            (embedding, f"%{keyword}%", limit)
        )
        keyword_results = cursor.fetchall()

        if not keyword_results:
            # Exact spelling found nothing - could be a user typo (like "Celcius" for
            # "Celsius") or a phonetic auto-caption misspelling. Try a fuzzy trigram match as
            # a last resort. Best-effort: if pg_trgm isn't available or anything goes wrong,
            # roll back and just proceed without the fuzzy results rather than breaking search.
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
                cursor.execute(
                    "SELECT title, channel, video_type, upload_date, url, speaker_verified, chunk_text, "
                    "1 - (embedding <=> %s::vector) AS similarity FROM transcripts "
                    "WHERE word_similarity(%s, chunk_text) > 0.5 "
                    "ORDER BY upload_date DESC NULLS LAST LIMIT %s",
                    (embedding, keyword, limit)
                )
                keyword_results = cursor.fetchall()
                conn.commit()
            except Exception as e:
                print(f"Fuzzy keyword fallback failed: {e}")
                conn.rollback()
                keyword_results = []

        # Keyword hits are guaranteed a slot, first - an exact (or fuzzy) match on the stock
        # name is a stronger relevance signal than embedding similarity, and needs to survive
        # the final truncation below even when the question doesn't use recency language.
        merged = []
        seen = set()
        for r in keyword_results:
            key = (r[0], r[6])
            if key not in seen:
                merged.append(r)
                seen.add(key)
        for r in results:
            key = (r[0], r[6])
            if key not in seen:
                merged.append(r)
                seen.add(key)
        results = merged

    cursor.close()
    conn.close()

    chunks = [
        {
            'title': r[0],
            'channel': r[1],
            'video_type': r[2],
            'upload_date': r[3],
            'url': r[4],
            'speaker_verified': r[5],
            'chunk_text': r[6],
            'similarity': r[7]
        }
        for r in results
    ]
    if keyword and wants_most_recent_mention(query):
        chunks.sort(key=lambda c: c['upload_date'] or '', reverse=True)
    return chunks[:limit] if len(chunks) > limit else chunks
def build_search_query(prompt, history, max_context_chars=800):
    if not history:
        return prompt
    last_assistant = None
    last_user = None
    for msg in reversed(history):
        if msg['role'] == 'assistant' and last_assistant is None:
            last_assistant = msg['content']
        elif msg['role'] == 'user' and last_assistant is not None and last_user is None:
            last_user = msg['content']
        if last_assistant is not None and last_user is not None:
            break
    if not last_assistant:
        return prompt
    context = f"{last_user or ''} {last_assistant}"[:max_context_chars]
    return f"{prompt}\n\nContext from the previous question and answer: {context}"


# ============ Feature 2: timestamp / jump-to-moment ============
# Fetch-on-demand + cache, per PROJECT_PLAN.md's plan: only videos that actually get cited
# in an answer ever get their timed transcript fetched, and it's cached in Neon afterward so
# a given video only gets fetched once, ever.
def _ensure_timestamp_cache_table(cursor):
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS video_timestamps ("
        "video_id TEXT PRIMARY KEY, segments JSONB, fetched_at TIMESTAMP DEFAULT now())"
    )


def get_timed_segments(video_id):
    """Returns cached timed-transcript segments (list of {'text', 'start'}) for a video,
    fetching from YouTube and caching in Neon on first use. Returns None if the transcript
    isn't available or the fetch fails - callers should treat that as 'no timestamp available'
    rather than an error."""
    conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
    cursor = conn.cursor()
    _ensure_timestamp_cache_table(cursor)
    conn.commit()
    cursor.execute("SELECT segments FROM video_timestamps WHERE video_id = %s", (video_id,))
    row = cursor.fetchone()
    if row:
        cursor.close()
        conn.close()
        return row[0]
    segments = None
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt = YouTubeTranscriptApi()
        fetched = ytt.fetch(video_id)
        segments = [{'text': snippet.text, 'start': snippet.start} for snippet in fetched]
        cursor.execute(
            "INSERT INTO video_timestamps (video_id, segments) VALUES (%s, %s) "
            "ON CONFLICT (video_id) DO UPDATE SET segments = EXCLUDED.segments",
            (video_id, json.dumps(segments))
        )
        conn.commit()
    except Exception as e:
        print(f"Timestamp fetch failed for {video_id}: {e}")
        segments = None
    cursor.close()
    conn.close()
    return segments


def find_timestamp_for_chunk(chunk_text, segments):
    """Best-effort: reconstructs the same flat caption text embed_and_upload.py chunked from
    (' '.join of each caption line), finds roughly where this chunk's text starts in that
    string, then walks the segments to find which caption's start time that offset falls in.
    Returns None (rather than guessing) if it can't find a confident match."""
    if not segments:
        return None
    full_text = ' '.join(seg['text'] for seg in segments)
    snippet = chunk_text.strip()[:200]
    idx = full_text.find(snippet)
    if idx == -1:
        snippet = chunk_text.strip()[:60]
        idx = full_text.find(snippet)
    if idx == -1:
        return None
    running = 0
    for seg in segments:
        seg_len = len(seg['text']) + 1  # +1 for the space the join above adds
        if running + seg_len > idx:
            return max(0, int(seg['start']) - 2)  # small buffer so it doesn't start mid-sentence
        running += seg_len
    return None


def add_timestamp_links(chunks):
    """For each chunk, tries to attach a '&t=Ns' timestamp to its video URL pointing at
    roughly where the cited excerpt starts. Best-effort and silent on failure - falls back
    to the plain video URL if anything goes wrong or no confident match is found, so this
    never breaks an answer, it just occasionally can't add the extra precision."""
    for c in chunks:
        c['timestamp_url'] = c['url']
        match = VIDEO_URL_PATTERN.search(c.get('url') or '')
        if not match:
            continue
        video_id = match.group(1)
        try:
            segments = get_timed_segments(video_id)
            start = find_timestamp_for_chunk(c['chunk_text'], segments)
            if start is not None:
                c['timestamp_url'] = f"{c['url']}&t={start}s"
        except Exception as e:
            print(f"Timestamp lookup failed for {video_id}: {e}")
    return chunks
# ===================================================================================================


def ask_jeremy(question, context_chunks):
    context = '\n\n'.join([
        f"[{c['channel']} | {c['upload_date'] or 'Unknown date'} | {c.get('timestamp_url') or c['url']} | "
        f"{c['channel'] + ' speaking, verified' if c['speaker_verified'] else 'UNVERIFIED SPEAKER - reaction video, may not be the channel owner'}]\n"
        f"{c['chunk_text']}"
        for c in context_chunks
    ])
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that answers questions based on YouTube transcripts from multiple finance content creators, including Jeremy Lefebvre and Eric Cuka. Always mention which creator and video the information came from, when it was said, and include the video URL as a clickable link so the user can watch the source (if the URL includes a '&t=Ns' timestamp, that points at roughly the right moment in the video - mention that they can jump straight to it). If the transcripts include more than one creator's view on the same topic, present each person's view separately and note where they agree or disagree, rather than blending them into one answer. If opinions have changed over time for a given creator, note that, and if transcripts span multiple years on the same topic, briefly trace how the view evolved chronologically. If the transcripts don't contain enough information, say so clearly. Keep answers concise and well organized. SPEAKER VERIFICATION: each excerpt is tagged either '{Channel} speaking, verified' or 'UNVERIFIED SPEAKER - reaction video, may not be the channel owner'. Reaction-channel excerpts are that channel's owner reacting to or discussing someone else's content, so the opinion voiced may belong to a guest or the creator being reacted to, not the channel owner. You may still use unverified excerpts to answer, but you must clearly flag them - e.g. '⚠️ from a reaction video, may not be the channel owner's own view' - and never present an unverified excerpt as that person's confirmed opinion. IMPORTANT: If Jeremy Lefebvre used the phrase 'load the boat' about a stock in the transcripts, always highlight that with a 🚢 emoji and make it clear he was extremely bullish."
            },
            {
                "role": "user",
                "content": f"Here are relevant transcript excerpts:\n\n{context}\n\nBased on these transcripts, please answer this question: {question}"
            }
        ],
        max_tokens=2500
    )
    return response.choices[0].message.content

st.set_page_config(
    page_title="Ask Jeremy",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { max-width: 700px; margin: 0 auto; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    h1 { font-weight: 300; letter-spacing: -1px; }
    .subtitle { color: #888; font-size: 0.9rem; margin-top: -20px; margin-bottom: 30px; }
    .footer { color: #bbb; font-size: 0.75rem; text-align: center; margin-top: 40px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("# Ask Jeremy 📈")
st.markdown('<p class="subtitle">AI-powered insights from Jeremy Lefebvre, plus Eric Cuka\'s take</p>', unsafe_allow_html=True)
st.divider()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("### Ladies and gentlemen...")
    st.markdown("**Try asking:**")
    st.markdown("- *Is Jeremy still bullish on AMD?*")
    st.markdown("- *What do Jeremy and Eric think about buying stocks at all-time highs?*")
    st.divider()
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])


if prompt := st.chat_input("Ask anything about Jeremy's stock opinions..."):
    conversation_history = st.session_state.messages.copy()
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)
    with st.chat_message('assistant'):
        prompt_for_groq = prompt
        if detect_recency_question(prompt):
            target_channels = extract_channels_from_question(prompt)
            chunks = get_latest_videos(channels=target_channels, limit=3)
        elif detect_video_summary_question(prompt) and find_last_mentioned_video_id(conversation_history):
            chunks = get_video_chunks(find_last_mentioned_video_id(conversation_history))
        elif detect_comparison_question(prompt):
            search_query = build_search_query(prompt, conversation_history)
            chunks = search_transcripts_comparison(search_query)
            prompt_for_groq = prompt + " (Please contrast Jeremy's and Eric's views separately, noting where they agree or disagree. Keep it concise - a short summary for each, not an exhaustive table - so the full answer fits comfortably.)"
        elif detect_first_mention_question(prompt):
            target_channels = extract_channels_from_question(prompt)
            search_query = build_search_query(prompt, conversation_history)
            chunks = search_transcripts_timeline(search_query, channels=target_channels)
            prompt_for_groq = prompt + " (Focus on identifying the FIRST time this was mentioned, then briefly trace how the view evolved to now.)"
        elif detect_timeline_question(prompt):
            target_channels = extract_channels_from_question(prompt)
            search_query = build_search_query(prompt, conversation_history)
            chunks = search_transcripts_timeline(search_query, channels=target_channels)
        elif detect_time_period_question(prompt):
            year, half = extract_time_period(prompt)
            target_channels = extract_channels_from_question(prompt)
            search_query = build_search_query(prompt, conversation_history)
            chunks = search_transcripts_by_period(search_query, year, half, channels=target_channels)
        else:
            search_query = build_search_query(prompt, conversation_history)
            chunks = search_transcripts(search_query)
        top_channel = chunks[0].get('channel', '') if chunks else ''
        is_jeremy = top_channel in JEREMY_CHANNELS
        spinner_text = 'Flipping your flapjacks... 🥞' if is_jeremy else 'Digging through the transcripts... 🔍'
        with st.spinner(spinner_text):
            if chunks:
                top_score = chunks[0].get('similarity', 0)
                chunks = add_timestamp_links(chunks)
                answer = ask_jeremy(prompt_for_groq, chunks)
                if top_score > 0.5:
                    if is_jeremy:
                        answer = "🔥 Holy smokas, this ain't no jokas!\n\n" + answer
                    else:
                        answer = "🔥 Strong match found!\n\n" + answer
            else:
                answer = "Couldn't find anything on that one! Try rephrasing your question. 🤷"
            st.markdown(answer)
    st.session_state.messages.append({'role': 'assistant', 'content': answer})
