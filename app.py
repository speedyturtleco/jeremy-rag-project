import os
import streamlit as st
from sentence_transformers import SentenceTransformer
from supabase import create_client
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

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
    .stChatInput { border-radius: 12px; }
    h1 { font-weight: 300; letter-spacing: -1px; }
    .subtitle { color: #888; font-size: 0.9rem; margin-top: -20px; margin-bottom: 30px; }
    .footer { color: #bbb; font-size: 0.75rem; text-align: center; margin-top: 40px; }
    </style>
""", unsafe_allow_html=True)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

def search_transcripts(query, limit=5):
    embedding = model.encode(query).tolist()
    result = supabase.rpc('match_transcripts', {
        'query_embedding': embedding,
        'match_threshold': 0.3,
        'match_count': limit
    }).execute()
    return result.data

def ask_jeremy(question, context_chunks):
    context = '\n\n'.join([
        f"[{c['channel']} | {c['upload_date'] or 'Unknown date'} | {c['url']}]\n{c['chunk_text']}"
        for c in context_chunks
    ])
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that answers questions based on Jeremy Lefebvre's YouTube transcripts. Always mention which video the information came from and when it was said. If opinions have changed over time, note that. If the transcripts don't contain enough information, say so clearly. Keep answers concise and well organized. IMPORTANT: If Jeremy used the phrase 'load the boat' about a stock in the transcripts, always highlight that with a 🚢 emoji and make it clear he was extremely bullish."
            },
            {
                "role": "user",
                "content": f"Here are relevant transcript excerpts:\n\n{context}\n\nBased on these transcripts, please answer this question: {question}"
            }
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

st.markdown("# Ask Jeremy 📈")
st.markdown('<p class="subtitle">AI-powered insights from Jeremy Lefebvre\'s YouTube content</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle"><em>"Buy the dip, never trip" — Jeremy Lefebvre</em></p>', unsafe_allow_html=True)
st.divider()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("### Ladies and gentlemen... ")
    st.markdown("**Try asking:**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- *What stocks does Jeremy like right now?*")
        st.markdown("- *What does Jeremy think about AMD?*")
        st.markdown("- *What stocks does Jeremy say to load the boat on?*")
    with col2:
        st.markdown("- *What is Jeremy's investing strategy?*")
        st.markdown("- *What price does Jeremy think Tesla is worth?*")
        st.markdown("- *What is Jeremy's public account worth?*")
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

st.markdown('<p class="footer">Based on Jeremy Lefebvre\'s public YouTube content · Not financial advice</p>', unsafe_allow_html=True)