import os
import re
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

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

def search_transcripts(query, limit=10):
    embedding = model.encode(query).tolist()
    conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute(
        'SELECT title, channel, video_type, upload_date, url, speaker_verified, chunk_text, 1 - (embedding <=> %s::vector) AS similarity FROM transcripts WHERE 1 - (embedding <=> %s::vector) > 0.3 ORDER BY similarity DESC LIMIT %s',
        (embedding, embedding, limit)
    )
    results = cursor.fetchall()
    cursor.close()
    return [
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
def ask_jeremy(question, context_chunks):
    context = '\n\n'.join([
        f"[{c['channel']} | {c['upload_date'] or 'Unknown date'} | {c['url']} | "
        f"{c['channel'] + ' speaking, verified' if c['speaker_verified'] else 'UNVERIFIED SPEAKER - reaction video, may not be the channel owner'}]\n"
        f"{c['chunk_text']}"
        for c in context_chunks
    ])
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that answers questions based on YouTube transcripts from multiple finance content creators, including Jeremy Lefebvre and Eric Cuka. Always mention which creator and video the information came from, when it was said, and include the video URL as a clickable link so the user can watch the source. If the transcripts include more than one creator's view on the same topic, present each person's view separately and note where they agree or disagree, rather than blending them into one answer. If opinions have changed over time for a given creator, note that. If the transcripts don't contain enough information, say so clearly. Keep answers concise and well organized. SPEAKER VERIFICATION: each excerpt is tagged either '{Channel} speaking, verified' or 'UNVERIFIED SPEAKER - reaction video, may not be the channel owner'. Reaction-channel excerpts are that channel's owner reacting to or discussing someone else's content, so the opinion voiced may belong to a guest or the creator being reacted to, not the channel owner. You may still use unverified excerpts to answer, but you must clearly flag them - e.g. '⚠️ from a reaction video, may not be the channel owner's own view' - and never present an unverified excerpt as that person's confirmed opinion. IMPORTANT: If Jeremy Lefebvre used the phrase 'load the boat' about a stock in the transcripts, always highlight that with a 🚢 emoji and make it clear he was extremely bullish."
            },
            {
                "role": "user",
                "content": f"Here are relevant transcript excerpts:\n\n{context}\n\nBased on these transcripts, please answer this question: {question}"
            }
        ],
        max_tokens=1000
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
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- *Is ELF still on the shelf?*")
        st.markdown("- *Should I load the boat on AMD?*")
        st.markdown("- *What does Eric think about buying stocks at all-time highs?*")
    with col2:
        st.markdown("- *What is Jeremy's GVD?*")
        st.markdown("- *What is Eric's F.I.R.E.D. Up philosophy?*")
        st.markdown("- *What does buy the dip, never trip mean to Jeremy?*")
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
        if detect_recency_question(prompt):
            target_channels = extract_channels_from_question(prompt)
            chunks = get_latest_videos(channels=target_channels, limit=3)
        elif detect_video_summary_question(prompt) and find_last_mentioned_video_id(conversation_history):
            chunks = get_video_chunks(find_last_mentioned_video_id(conversation_history))
        else:
            search_query = build_search_query(prompt, conversation_history)
            chunks = search_transcripts(search_query)
        top_channel = chunks[0].get('channel', '') if chunks else ''
        is_jeremy = top_channel in JEREMY_CHANNELS
        spinner_text = 'Flipping your flapjacks... 🥞' if is_jeremy else 'Digging through the transcripts... 🔍'
        with st.spinner(spinner_text):
            if chunks:
                top_score = chunks[0].get('similarity', 0)
                answer = ask_jeremy(prompt, chunks)
                if top_score > 0.5:
                    if is_jeremy:
                        answer = "🔥 Holy smokas, this ain't no jokas!\n\n" + answer
                    else:
                        answer = "🔥 Strong match found!\n\n" + answer
            else:
                answer = "Couldn't find anything on that one! Try rephrasing your question. 🤷"
            st.markdown(answer)
    st.session_state.messages.append({'role': 'assistant', 'content': answer})