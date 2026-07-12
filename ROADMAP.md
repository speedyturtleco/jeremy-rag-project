# Jeremy RAG Project Roadmap

## Project Overview
A RAG (Retrieval Augmented Generation) application that lets users have 
conversations with Jeremy Lefebvre's YouTube content across all his channels.
Built by a first-time coder with Claude's help starting June 2026.
Live at: https://ask-jeremy.streamlit.app/

## Tech Stack
- Python, VS Code, Git
- yt-dlp + youtube-transcript-api for downloading transcripts
- Sentence Transformers (all-MiniLM-L6-v2) for embeddings
- Neon (PostgreSQL + pgvector, cloud hosted, free tier)
- Groq API (llama-3.3-70b) for AI responses - FREE
- Streamlit for chat interface
- Hugging Face abandoned - moved to Streamlit Community Cloud (free)
- GitHub for code storage

## Channels Being Tracked
- Financial Education (@FinancialEducation) - main channel, direct opinions ✅
- Jeremy Lefebvre Makes Money (@jeremylefebvremakesmoney7934) - reaction channel (pending)
- 1000xstocks (UCCmJVw9xQfYuuAAwZGedKRg) - direct opinions (pending)

## ✅ Completed
- Installed Python, VS Code, Git
- Created GitHub, Supabase, Hugging Face, Neon, Groq accounts
- Downloaded 2,598 Financial Education transcripts
- Uploaded 25,127 chunks to Neon with HNSW vector index
- Built working Streamlit chat interface
- Connected Groq API (llama-3.3-70b) for free AI responses
- Deployed publicly at https://ask-jeremy.streamlit.app/
- Added Jeremy personality: "Ladies and gentlemen", "Flipping your flapjacks 🥞", "Holy smokas this ain't no jokas 🔥", "Load the boat 🚢"
- Added suggested questions with Jeremy catchphrases
- Switched from Supabase (timeout issues) to Neon (fast, free, no timeouts)

## 🔜 Immediate Next Steps
- [ ] **FIX UPLOAD_DATE** — most transcripts have None for date, critical for temporal features
      - yt-dlp wasn't capturing dates properly during download
      - Need to re-fetch dates for existing transcripts or re-download with date fix
- [ ] Download remaining Financial Education failed transcripts (retry with fresh IP)
- [ ] Download 1000xstocks channel (33 videos, direct opinions)
- [ ] Download reaction channel (859 videos, needs speaker diarization later)
- [ ] Upload 1000xstocks and reaction channel to Neon

## 🧠 Smart Search Modes (HIGH PRIORITY - build after date fix)
This is the feature that makes the app dramatically more powerful than standard RAG.
Use Groq to auto-detect which mode to use based on question keywords.

- [ ] **Mode 1 — Recent** 
      Trigger words: "right now", "today", "currently", "best stocks", "should I buy"
      Behavior: Return only chunks from last 6-12 months
      Example: "What are the best stocks to buy right now?"

- [ ] **Mode 2 — Specific Time Period**
      Trigger: Year mentioned in question (2019, 2020, etc.), "back in", "in early/late"
      Behavior: Filter chunks to that specific time window only
      Example: "What did Jeremy say was the best stocks to buy in 2019?"

- [ ] **Mode 3 — Timeline/Evolution**
      Trigger words: "changed", "over time", "always", "history", "evolution", "still"
      Behavior: Return chunks spread across ALL years, ordered chronologically
      Example: "How has Jeremy's opinion on ELF changed over time?"

- [ ] **Mode 4 — First Mention + Arc**
      Trigger words: "when did Jeremy start", "has he always", "first time"
      Behavior: Find earliest mention, then spread chronologically to present
      Example: "When did Jeremy start talking about Celsius and has he become more bullish?"

- [ ] **Mode 5 — Standard (current behavior)**
      Everything else → most semantically similar chunks regardless of date

## 💡 Future Features
- [ ] Automatic new video detection and download (daily scheduler)
- [ ] WhisperX speaker diarization for reaction channel
      - Download audio, separate speakers, only index Jeremy's lines
      - Also store guest opinions separately so users can search "what did guests say about Tesla"
- [ ] Conflict detection (flag when Jeremy changed his mind on a stock)
- [ ] Credibility tracker (did predictions come true?)
- [ ] Multi-creator support (compare Jeremy vs other finance YouTubers)
      - Ask "Which stocks do Jeremy AND Graham Stephan both like right now?"
      - Consensus tracker across multiple creators
- [ ] Vision AI to extract data from 1000xstocks screenshots in videos
- [ ] Password protection option for sharing with specific people
- [ ] "Load the boat" tracker — list all stocks he's ever said load the boat on
- [ ] Switch to Claude Code for future development sessions

## 🌟 Bigger Vision
- Add multiple finance YouTubers to same database
- Consensus tracker across creators
- Could become a public tool finance community would love
- Speedy Turtle Co product!

## 📝 Important Technical Notes
- cookies.txt in project folder (needed for yt-dlp downloads)
- YouTube IP ban clears ~24-48hrs after last request
- Use Decodo residential proxies for bulk downloading ($4/GB, ~100MB per 130 transcripts)
- Home IP works for short bursts (10-15 videos) before rate limiting
- Delays: 15-30 seconds between requests works best
- Neon connection: create fresh connection per query (don't cache - times out)
- Groq token limit: ~6,000 tokens per request, 10 chunks ≈ borderline
- upload_date is currently None for most transcripts — NEEDS FIX
- Supabase kept for regular data storage, Neon handles vector search
- Actually Supabase abandoned entirely, Neon handles everything now

## 🔑 Key Accounts
- GitHub: speedyturtleco
- Streamlit: https://ask-jeremy.streamlit.app/
- Neon: jeremy-rag-project (AWS US East 2 Ohio)
- Groq: free tier
- Decodo: residential proxies (buy per GB as needed, ~$4/GB)

## 📅 Session Log
- June 26: Phase 1 complete - all tools installed, accounts created
- June 27-28: Downloaded all Financial Education transcripts (2,675 first attempt)
- June 29: Downloaded 1000xstocks (33) and reaction channel (853)
- July 1-2: Built embed/upload script, fixed Supabase connection
- July 3: Built working chat interface with Groq, app live on phone!
- July 3: Deployed to Streamlit Community Cloud - https://ask-jeremy.streamlit.app/
- July 4-5: Added Jeremy personality (flapjacks, holy smokas, load the boat)
- July 7-8: Re-downloaded transcripts with Decodo residential proxies (2,598 total)
- July 8: Switched from Supabase to Neon - solved timeout issues
- July 8: App fully working with 25,127 chunks, no timeouts
- July 12: Designed smart search modes (4 temporal modes + standard)
          Identified upload_date fix as critical next step