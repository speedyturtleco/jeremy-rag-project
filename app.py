import os
import streamlit as st
from sentence_transformers import SentenceTransformer
from supabase import create_client
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

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
                "content": "You are an AI assistant that answers questions based on Jeremy Lefebvre's YouTube transcripts. Always mention which video the information came from and when it was said. If opinions have changed over time, note that. If the transcripts don't contain enough information, say so clearly."
            },
            {
                "role": "user",
                "content": f"Here are relevant transcript excerpts:\n\n{context}\n\nBased on these transcripts, please answer this question: {question}"
            }
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

st.set_page_config(page_title="Ask Jeremy", page_icon="📈")
st.title("📈 Ask Jeremy")
st.subheader("Ask anything about Jeremy Lefebvre's stock opinions")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input("Ask Jeremy anything about stocks..."):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)
    with st.chat_message('assistant'):
        with st.spinner('Searching Jeremy\'s videos...'):
            chunks = search_transcripts(prompt)
            if chunks:
                answer = ask_jeremy(prompt, chunks)
            else:
                answer = "I couldn't find relevant information in Jeremy's transcripts for that question."
            st.markdown(answer)
    st.session_state.messages.append({'role': 'assistant', 'content': answer})