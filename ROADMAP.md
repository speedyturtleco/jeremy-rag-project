# Jeremy RAG Project Roadmap

## Project Overview
A RAG (Retrieval Augmented Generation) application that lets users have 
conversations with Jeremy Lefebvre's YouTube content across all his channels.
Built by a first-time coder with Claude's help starting June 2026.

## Tech Stack
- Python, VS Code, Git
- yt-dlp + youtube-transcript-api for downloading transcripts
- Sentence Transformers (all-MiniLM-L6-v2) for embeddings
- Supabase (vector database, cloud hosted)
- Groq API (llama-3.3-70b) for AI responses - FREE
- Streamlit for chat interface
- Hugging Face Spaces for hosting (coming soon)

## Channels Being Tracked
- Financial Education (@FinancialEducation) - main channel, direct opinions
- Jeremy Lefebvre Makes Money (@jeremylefebvremakesmoney7934) - reaction channel
- 1000xstocks (UCCmJVw9xQfYuuAAwZGedKRg) - direct opinions

## ✅ Completed
- Installed Python, VS Code, Git
- Created GitHub, Supabase, Hugging Face accounts
- Downloaded 2,675 Financial Education transcripts
- Downloaded 853 reaction channel transcripts (need quality fix)
- Downloaded 33 1000xstocks transcripts (need quality fix)
- Created Supabase vector database with match_transcripts function
- Built working Streamlit chat interface
- Connected Groq API for free AI responses
- App working locally on Dell and phone via home WiFi

## 🔜 In Progress / Next Steps
- [ ] Wait for YouTube IP ban to clear (Saturday July 5)
- [ ] Re-download all Financial Education transcripts with proper text
- [ ] Re-download 1000xstocks transcripts with proper text
- [ ] Re-download reaction channel transcripts with proper text
- [ ] Re-upload all transcripts to Supabase with proper chunking
- [ ] Fix upload_date capture so dates show in answers
- [ ] Deploy to Hugging Face Spaces (public URL for phone/friends)

## 💡 Future Features (To Build)
- [ ] Automatic new video detection and download (daily scheduler)
- [ ] WhisperX speaker diarization for reaction channel
- [ ] Temporal ranking (newer opinions weighted higher)
- [ ] Conflict detection (flag when Jeremy changed his mind)
- [ ] Opinion evolution tracker (how views on stocks changed over time)
- [ ] Credibility tracker (did predictions come true?)
- [ ] Multi-creator support (compare Jeremy vs other finance YouTubers)
- [ ] Vision AI to extract data from 1000xstocks screenshots in videos
- [ ] Deploy publicly for friends and family to use
- [ ] Password protection option for sharing with specific people

## 🌟 Bigger Vision
- Add multiple finance YouTubers to same database
- Ask "Which stocks do Jeremy AND Graham Stephan both like right now?"
- Consensus tracker across multiple creators
- Could become a public tool finance community would love

## 📝 Important Notes
- cookies.txt in project folder (needed for yt-dlp downloads)
- YouTube IP ban clears ~48hrs after last request - don't run download scripts until Saturday
- Financial Education transcripts were downloaded correctly (first 48 with youtube-transcript-api)
- Other channels got bad URL data instead of text - need redownload
- Supabase URL format: https://ymntocyywakjcwpqnylv.supabase.co (no /rest/v1/ at end)
- Groq model: llama-3.3-70b-versatile
- App runs on http://localhost:8501
- Phone access on home WiFi: http://[Dell's IPv4]:8501

## 📅 Session Log
- June 26: Phase 1 complete - all tools installed, accounts created
- June 27-28: Downloaded all Financial Education transcripts (2,675)
- June 29: Downloaded 1000xstocks (33) and reaction channel (853)
- July 1-2: Built embed/upload script, fixed Supabase connection
- July 3: Built working chat interface with Groq, app live on phone!
## 🧠 Smart Search Modes (HIGH PRIORITY)
- [ ] Fix upload_date capture — critical for all temporal features
- [ ] Mode 1: Recent search — "best stocks right now" → last 6-12 months only
- [ ] Mode 2: Specific time period — "what was Jeremy buying in 2019?" → filter by year
- [ ] Mode 3: Timeline/Evolution — "how has opinion changed?" → spread across all years
- [ ] Mode 4: First mention + arc — "when did Jeremy start talking about Celsius?" → oldest to newest
- [ ] Auto-detect which mode based on question keywords using Groq