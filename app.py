import os
import streamlit as st
from sentence_transformers import SentenceTransformer
import psycopg2
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

def ask_jeremy(question, context_chunks):
    context = '\n\n'.join([
        f"[{c['channel']} | {c['upload_date'] or 'Unknown date'} | {c['url']} | "
        f"{'Jeremy speaking, verified' if c['speaker_verified'] else 'UNVERIFIED SPEAKER - reaction video, may not be Jeremy'}]\n"
        f"{c['chunk_text']}"
        for c in context_chunks
    ])
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that answers questions based on Jeremy Lefebvre's YouTube transcripts. Always mention which video the information came from and when it was said. If opinions have changed over time, note that. If the transcripts don't contain enough information, say so clearly. Keep answers concise and well organized. IMPORTANT: If Jeremy used the phrase 'load the boat' about a stock in the transcripts, always highlight that with a 🚢 emoji and make it clear he was extremely bullish. SPEAKER VERIFICATION: each excerpt is tagged either 'Jeremy speaking, verified' or 'UNVERIFIED SPEAKER - reaction video, may not be Jeremy'. These reaction videos are Jeremy reacting to or discussing someone else's content, so the opinion voiced may belong to a guest or the creator he's reacting to, not Jeremy himself. You may still use unverified excerpts to answer, but you must clearly flag them - e.g. '⚠️ from a reaction video, may not be Jeremy's own view' - and never present an unverified excerpt as Jeremy's confirmed opinion."
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
st.markdown('<p class="subtitle">AI-powered insights from Jeremy Lefebvre\'s YouTube content</p>', unsafe_allow_html=True)
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
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)
    with st.chat_message('assistant'):
        with st.spinner('Flipping your flapjacks... 🥞'):
            chunks = search_transcripts(prompt)
            if chunks:
                top_score = chunks[0].get('similarity', 0)
                answer = ask_jeremy(prompt, chunks)
                if top_score > 0.5:
                    answer = "🔥 Holy smokas, this ain't no jokas!\n\n" + answer
            else:
                answer = "Holy smokas, this ain't no jokas — I couldn't find anything on that one! Try rephrasing your question. 🤷"
            st.markdown(answer)
    st.session_state.messages.append({'role': 'assistant', 'content': answer})

st.markdown('<p class="footer">Based on Jeremy Lefebvre\'s public YouTube content · Not financial advice · "Buy the dip, never trip"</p>', unsafe_allow_html=True)