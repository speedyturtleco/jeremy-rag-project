# Ask Jeremy — Master Project Plan & Memory File

> **How to use this file:** This is the SINGLE SOURCE OF TRUTH for this project. Chats get
> forgotten when closed; this file does not. At the start of any new chat, paste this whole file
> in and say "here's my project plan, catch up." Keep it at:
> `C:\Users\speed\jeremy-rag-project\PROJECT_PLAN.md`
>
> This file MERGES the old `roadmap.md` + planning done in chat. If `roadmap.md` still exists,
> treat THIS file as authoritative and update/retire the old one to avoid drift.
> Built by a first-time coder with Claude's help, starting June 2026.
> Live at: https://ask-jeremy.streamlit.app/

---

## PROJECT OVERVIEW
A RAG app that lets users "talk to" Jeremy Lefebvre's YouTube content across all his channels.
Priority: keep it as FREE / LOW-COST as possible. This is my FIRST build.
Long-term vision: multi-creator consensus tracker, "Speedy Turtle Co" product.

## TECH STACK
- Python, VS Code, Git
- yt-dlp + youtube-transcript-api for downloading transcripts (via Decodo residential proxy)
- Sentence Transformers `all-MiniLM-L6-v2` for embeddings (local, free)
- Neon (PostgreSQL + pgvector, cloud, free tier) — handles ALL storage + vector search
  (Supabase abandoned entirely due to timeout issues)
- Groq API `llama-3.3-70b-versatile` for AI responses (free tier)
- Streamlit for chat interface, deployed on Streamlit Community Cloud (free)
- GitHub for code storage
- Files: `download_transcrips.py` (note misspelled filename), `embed_and_upload.py`, `app.py`,
  `auto_update.py` + `requirements-auto-update.txt` + `.github/workflows/auto_update.yml`
  (daily automated new-video check via GitHub Actions — see Feature 3 below)

## CHANNELS
- Financial Education (@FinancialEducation) — main channel, direct opinions ✅ downloaded+uploaded
- 1000xstocks (UCCmJVw9xQfYuuAAwZGedKRg) — direct opinions (35 downloaded recently)
- Jeremy Lefebvre Makes Money (@jeremylefebvremakesmoney7934) — reaction channel (~853, pending;
  needs speaker diarization later so only Jeremy's lines get indexed)

---

## DATA SITUATION (IMPORTANT)
- 2,598 Financial Education transcripts downloaded → 25,127 chunks in Neon w/ HNSW vector index.
- Plus ~35 from 1000xstocks (recently downloaded).
- Raw JSON transcripts stored as ONE FLAT BLOB of text — NO within-video timestamps.
- `embed_and_upload.py` chunks the blob into ~500-word pieces (50-word overlap), stores each in
  Neon: video_id (as `{video_id}_{i}`), title, channel, video_type, upload_date, url,
  speaker_verified, chunk_text, embedding.
- So DB chunks have `upload_date` (for time features) but NO within-video timestamp (can't jump
  to a moment in the video — yet; see Feature 2).

## ⚠️ CRITICAL UNKNOWN TO VERIFY FIRST
Roadmap flagged (twice) that `upload_date` is **None for most transcripts** — and that it's the
critical blocker. The download script was later patched to fetch dates (1000xstocks got real
dates like `20251130`). **BUT it's unconfirmed whether the 25,127 Financial Education chunks
ALREADY IN NEON have real dates or blanks.**
- EVERY time-based search mode depends on these dates existing in the DB.
- **ACTION BEFORE BUILDING SEARCH MODES:** query Neon to check how many chunks have a real
  upload_date vs blank/None. If most are blank, fixing that comes first.

---

## FEATURE 1: SMART SEARCH MODES  (HIGH PRIORITY — the app's killer feature)
Different question types need different search strategies. Use Groq (or fast keyword rules) to
auto-detect which mode a question needs, then search accordingly. All lives in `app.py` — no
re-download, no DB schema change (assuming dates are present).

### The 5 modes (from roadmap, refined in chat):
- **Mode 1 — Recent / Current / Recommendation**
  Triggers: "right now", "today", "currently", "best stocks", "should I buy", "still".
  Behavior: only chunks from last ~6–12 months.
  ⭐ REFINEMENT (chat): for "what should I buy" use MEANING SEARCH + recency, NOT keyword lists.
     Search with a meaning query like "Jeremy is extremely bullish, strong buy, big upside" —
     embeddings catch "load the boat", "back up the truck", "no-brainer", etc. automatically.
     No brittle keyword list to maintain. Optional: small 🚢 bonus for "load the boat".

- **Mode 2 — Specific Time Period**
  Triggers: a year in the question (2019, 2020...), "back in", "in early/late".
  Behavior: filter chunks to that specific time window only.
  Example: "What did Jeremy say to buy in 2019?"

- **Mode 3 — Timeline / Evolution ("over time")**
  Triggers: "changed", "over time", "always", "history", "evolution", "still".
  Behavior: chunks spread across ALL years, ordered chronologically.
  ⭐ REFINEMENT (chat): bucket BY YEAR (content spans many years). Show top few chunks per year.
     Watch out: current `search_transcripts` has BOTH a `>0.3` similarity floor AND `LIMIT 10` —
     both fight against time-spread; bucketing handles it.
  Example: "How has Jeremy's opinion on ELF changed over time?"

- **Mode 4 — First Mention + Arc**
  Triggers: "when did Jeremy start", "has he always", "first time".
  Behavior: find earliest mention, then spread chronologically to present.
  Example: "When did Jeremy start talking about Celsius and has he gotten more bullish?"

- **Mode 5 — Standard (current behavior)**
  Everything else (catchphrase/lore like "Flapjack Flipping Hotel", factual one-offs like
  "what's his GVD") → most semantically similar chunks regardless of date. Already works.

### BUILD SEQUENCE (do NOT build all at once):
0. **VERIFY dates exist in Neon** (see critical unknown above). Fix if needed.
1. **Router skeleton** — one function that detects question mode (start simple: Mode 3 vs
   everything-else, then expand).
2. **Mode 3 (over time / year-bucketing)** first — most different from current, most impressive.
3. **Mode 1 (recent + meaning search)** next.
4. **Modes 2 & 4**, one at a time, testing each.
(Mode 5 already exists as the fallback.)

---

## FEATURE 2: TIMESTAMP / JUMP-TO-MOMENT  (SEPARATE — do LAST)
Goal: when an answer comes from a video, show WHERE in the video + a link that jumps to that
moment (`youtube.com/watch?v=VIDEO_ID&t=142s`).
Problem: current chunks have NO timing (blob flattened before chunking).
**DECISION — Option 3 (fetch-on-demand + cache):**
- Keep blob-based search to find WHICH video answers.
- Re-fetch THAT ONE video's timed transcript on the spot, locate the answer, get start time.
- CACHE the timed transcript so next time that video comes up it's instant + no re-fetch.
- Only videos that come up in answers ever get fetched — avoids re-downloading all 2,598.
Caveat: live re-fetch adds seconds + carries proxy/block risk; caching smooths it over time.
This is the ONLY feature needing NEW data. Keep separate, do LAST.

---

## FEATURE 3: AUTOMATED DAILY NEW-VIDEO CHECK  ✅ LIVE (built Jul 23)
Runs automatically once a day via GitHub Actions — no manual downloading needed anymore for
staying current on new uploads.

- **Files:** `auto_update.py` (repo root), `requirements-auto-update.txt` (repo root),
  `.github/workflows/auto_update.yml` (workflow config).
- **Schedule:** daily at 10:00 UTC = 5:00 AM EST (winter) / 6:00 AM EDT (summer). GitHub Actions
  cron is fixed UTC and does NOT shift for daylight saving — accept the 1hr drift or manually
  flip the cron value twice a year if it matters.
- **Manual trigger also available:** GitHub.com → repo → Actions tab → "Auto-check for new
  Jeremy videos" → "Run workflow" button (no desktop shortcut needed, per decision this session).
- **Failure notifications:** GitHub automatically emails the repo owner if a scheduled run fails
  — this is default behavior, no extra setup was needed.
- **How it works (per channel, each run):**
  1. List current channel videos (free, no Decodo cost — `extract_flat` listing only).
  2. Check which video IDs are already in Neon (global distinct video_id query).
  3. Take only the newest not-yet-uploaded videos, **capped at 5 per channel per run**
     (`MAX_NEW_PER_CHANNEL_PER_RUN` in `auto_update.py`) — this is a deliberate safety limit so
     a scheduled run can never accidentally bulk-backfill (e.g. reaction channel still has
     ~800+ backlog videos not in Neon; those stay untouched unless run manually via
     `download_transcrips.py`).
  4. Download transcript for each new video (THIS is the only step that costs Decodo bandwidth).
  5. Chunk (same 500-word/50-overlap logic) + embed + insert directly into Neon — no local JSON
     file is kept (GitHub Actions runners are ephemeral; Neon is the sole source of truth for
     "already have this video").
- **First live run (Jul 23) results:** caught up on backlog since channels had never been
  checked before — 14 new videos found across all 3 channels (4 Financial Education, 5
  1000xstocks, 5 reaction), 461 chunks uploaded total. One transcript hit a transient
  block on attempt 1, succeeded on retry (existing retry logic worked as designed).
  Going forward, daily runs should find far fewer (0–2ish) new videos per day, not 14.
- **Decodo cost:** confirmed this routes through the Decodo proxy same as manual downloads.
  The 14-video catch-up run cost an estimated ~10–15MB — small relative to the 3GB Decodo plan.
  Ongoing daily cost should be even smaller once there's no backlog to catch up on.
- **⚠️ Known gotcha hit during setup:** dragging files into folders in Windows/VS Code produced
  0-byte empty files on GitHub (happened to ALL THREE files: the yml, the requirements file,
  and auto_update.py). Symptom was workflow runs finishing in ~4–12 seconds with the log
  showing "No event triggers defined in `on`" or a silent no-op pip install. Fixed by editing
  each file directly in GitHub's web editor and pasting full contents in. If editing these
  files again locally, verify file size before pushing (don't trust drag-and-drop blindly).
- **Setup requires 4 GitHub repo secrets** (Settings → Secrets and variables → Actions):
  `DECODO_USERNAME`, `DECODO_PASSWORD`, `NEON_DATABASE_URL`, `COOKIES_TXT` (full raw contents
  of local cookies.txt, pasted as-is — no `=` signs, no quotes, just the value).
- **Maintenance note:** `cookies.txt` / the `COOKIES_TXT` secret will go stale eventually
  (YouTube session cookies expire) — when a scheduled run fails for this reason, the failure
  email will surface it; re-export cookies.txt locally and update the secret value.

---

## 💡 FUTURE FEATURES (from roadmap)
- WhisperX speaker diarization for reaction channel (index only Jeremy's lines; optionally store
  guest opinions separately so users can ask "what did guests say about Tesla")
- Conflict detection (flag when Jeremy changed his mind on a stock)
- Credibility tracker (did his predictions come true?)
- Multi-creator support + consensus tracker ("which stocks do Jeremy AND Graham Stephan both
  like right now?")
- Vision AI to extract data from 1000xstocks on-screen screenshots
- Password protection for private sharing
- "Load the boat" tracker — every stock he's ever said load the boat on
- Possibly switch to Claude Code for future dev sessions

---

## 📝 KEY TECHNICAL NOTES (from roadmap — important!)
- `cookies.txt` in project folder needed for yt-dlp downloads.
- YouTube IP ban clears ~24–48 hrs after last request.
- Decodo residential proxies for bulk downloading (~$4/GB, ~100MB per 130 transcripts).
- Home IP works for short bursts (10–15 videos) before rate limiting.
- Delays: 15–30 sec between requests works best.
- **Neon: create a FRESH connection per query — do NOT cache, it times out.**
- **Groq token limit ~6,000 tokens/request; 10 chunks is BORDERLINE.** (Matters for how many
  chunks we feed the answer step — don't over-stuff, especially in multi-year modes.)
- Chunking: 500 words, 50 overlap. For future timestamp precision, ~30–60 sec/chunk is ideal.
- Retrieval top-k of ~5–10 BEST chunks is the sweet spot (focused + within token budget).

## 🔑 KEY ACCOUNTS
- GitHub: speedyturtleco
- Streamlit: https://ask-jeremy.streamlit.app/
- Neon: jeremy-rag-project (AWS US East 2 Ohio)
- Groq: free tier
- Decodo: residential proxies (buy per GB, ~$4/GB)

---

## STATUS / WHERE WE LEFT OFF
- Merged roadmap.md + chat planning into this single file.
- Confirmed data flow across all 3 code files.
- Confirmed chunks have upload_date FIELD but must VERIFY it's actually populated in Neon.
- Locked decisions: over-time buckets = BY YEAR; "what to buy" = meaning search + recency
  (no keyword lists).
- ✅ Feature 3 (automated daily new-video check) built, tested, and LIVE as of Jul 23 — see
  Feature 3 section above for full details. This was NOT on the critical path for Feature 1,
  so the verification step below is still the next real blocker.
- **NEXT ACTION:** Step 0 — verify upload_date is populated in the Neon DB (quick query),
  THEN build router skeleton + Mode 3 (over-time, year-bucketing) in `app.py`.

## SESSION LOG (from roadmap + recent)
- Jun 26: tools installed, accounts created.
- Jun 27–28: downloaded Financial Education transcripts (2,675 first attempt).
- Jun 29: downloaded 1000xstocks (33) + reaction channel (853).
- Jul 1–2: built embed/upload script, fixed Supabase connection.
- Jul 3: built chat interface w/ Groq; deployed to Streamlit Community Cloud.
- Jul 4–5: added Jeremy personality (flapjacks, holy smokas, load the boat).
- Jul 7–8: re-downloaded w/ Decodo residential proxies (2,598 total).
- Jul 8: switched Supabase → Neon (fixed timeouts); 25,127 chunks live, no timeouts.
- Jul 12: designed smart search modes (4 temporal + standard); flagged upload_date fix as critical.
- (recent) re-ran 1000xstocks download w/ retry logic — 34/35, one video has no retrievable
  transcript (IP/proxy block on that specific video).
- (this session) merged roadmap into master plan; refined Mode 1 (meaning search) + Mode 3
  (year buckets).
- Jul 23: built Feature 3 — automated daily new-video check via GitHub Actions. Decided against
  desktop shortcuts in favor of GitHub.com's built-in "Run workflow" manual trigger button;
  relying on GitHub's default failure-email behavior (no custom notification code needed).
  Settled on daily schedule (not 3x/week) at 5 AM EST / 10:00 UTC. Hit and fixed a drag-and-drop
  bug that silently created 0-byte files for all 3 new files (yml, requirements, script) — fixed
  via GitHub's web editor. First live run successfully caught up on 14 backlogged videos (461
  chunks) across all 3 channels with zero manual intervention. Confirmed this uses Decodo
  bandwidth (~10–15MB for the catch-up run) but should be minimal going forward on a daily
  cadence. Feature 1 (search modes) remains the next real priority — untouched today.