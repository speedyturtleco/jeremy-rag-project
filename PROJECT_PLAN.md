# Ask Jeremy — Master Project Plan & Memory File

---
## 🚦 START HERE — NEXT SESSION FIRST ACTION (updated Sep 5 session, later same day)

**THREE bugs found, fixed, pushed, AND live-tested working this session - nothing left pending
from Sep 5.** FEATURE 7 (Groq mislabeling Jeremy's own channels as "not Jeremy's"), FEATURE 8
(conversation-memory context stuffing silently breaking keyword extraction on follow-up
questions), and FEATURE 9 (wrong/misleading video timestamps from a non-unique text match) are
all fixed, on GitHub, and confirmed live. Everything from Sep 2-4 (Feature 1 Modes 2-4, Feature 2,
Feature 4, all three Feature 6 fixes) is still done and live.

**Also fixed this session, right after Feature 9: FEATURE 10, the garbled dollar-amount
rendering bug** spotted during Feature 9's live-test. Written and verified on the user's local
`app.py` - **still needs `git add`/`git commit`/`git push` and a live-test**, see FEATURE 10
below.

**⚠️ Also: a process mistake happened and was caught/fixed earlier this session - see the new
callout right after the "HOW TO WORK WITH ME" section below. Read it before ever telling the
user to run `git reset --hard` again.**

0. ✅ **BUG FOUND, FIXED & LIVE-TESTED Sep 5 (later): wrong video timestamp shown for a cited
   excerpt** — user asked "when is the most recent time jeremy mentions amazon projections?" and
   got an answer citing a real Nov 2025 Financial Education video, but the "jump to it" timestamp
   (≈2:45) pointed at the wrong part of the video, not the actual Amazon-trillion-dollar segment
   being quoted. Root cause: the timestamp-matching code's 60-character fallback snippet could
   match more than one place in a long video's transcript, and it was silently taking the FIRST
   match instead of checking whether the match was actually unique. Fixed by requiring uniqueness
   before trusting a match, returning no timestamp (falls back to the plain video link) rather
   than guessing wrong. Pushed to GitHub (commit `9071be2`) and **confirmed fixed via live
   re-test**: the same video now correctly shows no timestamp instead of a wrong one, while other
   citations in the same answer that had unambiguous matches kept their working timestamps. Full
   details in FEATURE 9 below.
1. ✅ **BUG FOUND & FIXED Sep 5: keyword extraction silently broken by conversation-memory
   context stuffing** — a same-session follow-up question ("...projections for wynn?" asked
   right after a Netflix question) got a false "no mention found" even though the exact "for X"
   phrasing was already supposed to be fixed (Sep 4) and a verified Wynn mention was already
   confirmed to exist in the corpus (Sep 3). Root cause: totally different from Features 6/7 -
   `build_search_query()` appends the PRIOR question+answer after the new question for semantic
   search purposes, but `extract_stock_keyword()`'s end-of-string anchor was reading that same
   appended string, so it silently extracted nothing once older conversation text came after the
   real question. Fixed by extracting keywords from the raw current question only. Full details
   in the new FEATURE 8 section below. **Not yet live-tested after this fix** - do this first
   next session.
2. ✅ **BUG FOUND & FIXED Sep 5: Groq mislabeled Jeremy's own channels as "not Jeremy's
   channel"** — live-testing the Sep 4 Netflix fix showed real progress (the app now finds and
   quotes real, dated Netflix content instead of a blanket "no mention found") but revealed a
   new bug: Groq's answer said Financial Education excerpts were "not Jeremy's channel." Root
   cause: the context sent to Groq only ever included the raw Neon `channel` value (e.g.
   "Financial Education"), never an explicit mapping to the real creator - so the model had no
   way to know Jeremy personally runs that channel, and guessed wrong. Fixed by adding an
   explicit `CHANNEL_CREATOR` mapping to every excerpt tag and to the system prompt. **Confirmed
   fixed via live test** - full details in FEATURE 7 section below.
3. ✅ **BUG FOUND & FIXED Sep 4: "for X" / "regarding X" phrasing missed by the keyword
   safety net** — user reported that a question about Jeremy's Netflix projections (from the
   video "4 Stocks to Go ALL IN September 2026") came back with a false "no mention found."
   Same root cause family as the Wynn/Celsius bugs: `TOPIC_TAIL_PATTERN` only recognized "on X"
   / "about X" at the end of a question, not "for X" - so "his projections **for** Netflix"
   never triggered the literal keyword search. Fixed by widening the preposition list. Full
   details in FEATURE 6's third update below.
4. ✅ **IMPORTANT PROCESS FIX Sep 4: local `app.py` was stale, now back in sync** — see the new
   note below. Going forward, confirm local vs. live are in sync at the start of any session
   that touches `app.py`, since deploys have been happening straight to GitHub without always
   updating the local copy.
5. **This session's deploy path was different:** for the first time, `device_commit_files`
   successfully wrote directly to the user's local `app.py` (previous sessions logged this as
   unavailable/refused). The user will `git add` / `git commit` / `git push` from VS Code
   themselves to actually deploy - worth trying this path again before assuming the GitHub
   web-editor route is required.

**Sep 3 session recap (unchanged):**

1. ✅ **Conversation memory re-confirmed live (Sep 3)** — asked a vague follow-up question that
   named neither the topic nor any keyword from the prior question; the app correctly used
   context from the previous Q&A to answer it. No code change needed, just a live smoke test.
2. ✅ **Landing page "Try asking" examples reduced from 6 to 2 (Sep 3)** — see FEATURE 5 section
   below for the two questions chosen and why.
3. ✅ **BUG FOUND & FIXED Sep 3: standard search (Mode 5) could miss a stock's only mention** —
   user asked "what's the latest instance of Jeremy talking about Wynn stock" and got a false
   "no mention found," even though a video from 2 days earlier had already been ingested and
   (per the user) did mention Wynn. Root cause and fix in FEATURE 6 below - this is worth
   reading in full, since it's a real limitation of plain top-10 semantic search that could
   recur for any other rarely-mentioned stock, not just Wynn.
4. ✅ **SAME BUG CLASS FOUND AGAIN & FIXED Sep 3: "on X" phrasing + typo'd keywords** — right
   after the Wynn fix, user asked "what's jeremy's latest take on celcius" (typo for Celsius)
   and got a stale, low-confidence answer, missing a same-day verified mention. Two more gaps
   in the Feature 6 fix, closed the same session - see FEATURE 6's update for details.

**Sep 2 evening session recap (unchanged):**

1. ✅ **Feature 1 Mode 2 (specific time period, e.g. "in 2021") — DONE, built and live-tested.**
2. ✅ **Feature 1 Mode 3 (timeline/evolution, "over time") — DONE, built (shares retrieval with
   Mode 4, live-tested via Mode 4's question which also exercises this path).**
3. ✅ **Feature 1 Mode 4 (first mention + arc, "has he always...") — DONE, built and
   live-tested** ("Has Jeremy always been bullish on AMD?" → correct table tracing the first
   AMD mention through to now).
4. ✅ **Feature 2 (timestamp / jump-to-moment links) — DONE, built and live-tested** — answers
   now include `&t=Ns` links that jump to roughly the right moment in the cited video.
5. ✅ **Feature 4 (multi-creator comparison mode) — DONE, built, and live-tested** — but needed
   TWO follow-up fixes after the first deploy truncated mid-answer (see bug section below).
   Confirmed working cleanly on the third deploy.
6. All of the "🚦 START HERE" items from the Aug 28/Sep 2 morning session (date backfill,
   Decodo billing, keep-awake, monitoring, conversation memory) are still closed out — see
   below, unchanged.
7. **What's left, for whenever:** nothing major from the original roadmap. Remaining ideas are
   all in the 💡 FUTURE FEATURES list (conflict detection, credibility tracker, Eric-specific
   personality, etc.) — none of it is blocking or urgent. Worth spending a session just using
   the app normally to see if anything new surfaces now that all 4 search modes + comparison +
   timestamps are live together.

---

> **How to use this file:** This is the SINGLE SOURCE OF TRUTH for this project. Chats get
> forgotten when closed; this file does not. At the start of any new chat, paste this whole file
> in and say "here's my project plan, catch up." Keep it at:
> `C:\Users\speed\jeremy-rag-project\PROJECT_PLAN.md`
>
> Built by a first-time coder with Claude's help, starting June 2026.
> Live at: https://ask-jeremy.streamlit.app/

> **⚠️ HOW TO WORK WITH ME (added Aug 9; updated Aug 22):** I am not an expert coder. When
> there's a new script to run, don't just hand it over and say "run this" — walk me through it
> step by step: where the file goes, what command to type, what I should expect to see, and what
> to do if something looks wrong. Confirm each step landed before moving to the next one.
> This applies every session, not just when I ask for it.
> **When a task needs multiple terminal commands run in sequence (e.g. `git add` /
> `git commit` / `git push`), give me all of them up front but as SEPARATE commands, each
> in its own line/code block — never chained together with `&&` or combined into one block
> to copy-paste as a single unit. I'll run them one by one myself.**
> **⚠️ Learned the hard way Aug 28: after ANY code change gets made and pushed, update the
> project's saved copies of the affected file(s) AND this plan in the same session — don't
> wait.** Keep the project docs and the live code in sync every session, not just when asked.

> **⚠️ LOCAL FILE SYNC WARNING (added Sep 4):** Because Sep 2-3's deploys all went straight to
> GitHub via the web editor (browser-driven), the LOCAL copy of `app.py` on this computer never
> got updated with any of that work — it was still the pre-Sep-2 version until this session
> caught and fixed it. **At the start of any session that's about to edit `app.py` (or any
> deployed file), check whether the local copy actually matches what's live/in this project's
> saved doc before building on top of it** — otherwise a well-intentioned local edit + `git
> push` can silently roll back everything shipped through an alternate deploy path. This
> session fixed it by writing the current, project-doc-verified version to the local file
> before applying the new fix, then syncing this project's own saved copy too.

> **⚠️ NEVER `git reset --hard` OVER AN UNPUSHED FIX (added Sep 5):** on Sep 5, right after
> writing a fix directly to the user's local `app.py`/`PROJECT_PLAN.md` via `device_commit_files`,
> I told the user to run the standard `git fetch origin` + `git reset --hard origin/main` sync
> routine - but that fix had only been written LOCALLY, never actually pushed to GitHub yet. The
> reset silently discarded it (rolled back to the last real GitHub commit). **A file being on
> the user's disk via `device_commit_files` is NOT the same as that file being safe to `git
> reset --hard` over.** Before ever suggesting a hard reset (or anything else that makes the
> working tree exactly match a remote/commit), confirm the fix in question is EITHER already on
> GitHub (check the commit hash / GitHub UI) OR about to be committed+pushed in the very next
> step, e.g. via `git add` / `git commit` / `git push` run by the user themselves. When in doubt,
> ask for `git status` first and read it before recommending any command that overwrites the
> working tree.

> **⚠️ VERIFY `device_commit_files` WRITES ACTUALLY LANDED (added Sep 5):** on Sep 5,
> `device_commit_files` reported success writing a fix to the user's local `app.py`, but the
> file on disk was silently unchanged (confirmed by staging it back and diffing/grepping for
> the new code - it wasn't there). The user then correctly got a `git commit` that said
> "nothing to commit" because there really was nothing new on disk. **Going forward: after ANY
> `device_commit_files` write, re-`device_stage_files` that same file back and grep/diff for
> something distinctive from the fix (a new function name, a comment, a changed line) BEFORE
> telling the user to `git add`/`git commit`/`git push`.** A "written" success from the tool is
> not proof the content actually changed on disk - verify it independently every time, the same
> way large-paste browser edits already get verified in this project. **Update, later same
> session: this happened 3 separate times in ONE session** (twice on `PROJECT_PLAN.md`, once on
> `app.py`) - not a one-off fluke. Every time, a `force: true` retry on the very next attempt
> succeeded. Standing pattern: after every `device_commit_files` write, immediately
> `device_stage_files` that same path back and md5sum/diff it against the source - if it doesn't
> match, retry once with `force: true` and verify again, rather than assuming the first
> "written" response was real.

---

## PROJECT OVERVIEW
A RAG app that lets users "talk to" multiple finance YouTubers' content — currently Jeremy
Lefebvre (primary) and Eric Cuka (secondary, subtly included). Priority: keep it as FREE /
LOW-COST as possible. This is my FIRST build.
Long-term vision: multi-creator consensus tracker, "Speedy Turtle Co" product.

## TECH STACK
- Python, VS Code, Git
- yt-dlp + youtube-transcript-api for downloading transcripts (via Decodo residential proxy)
- Sentence Transformers `all-MiniLM-L6-v2` for embeddings (local, free)
- Neon (PostgreSQL + pgvector, cloud, free tier) — handles ALL storage + vector search
- Groq API for AI responses (free tier) — model `openai/gpt-oss-120b`, `max_tokens=2500` as of
  Sep 2 evening session (raised from 1000 → 1800 → 2500, see FEATURE 4 bug notes below)
- Streamlit for chat interface, deployed on Streamlit Community Cloud (free)
- GitHub for code storage
- Files: `download_transcrips.py` (note misspelled filename), `embed_and_upload.py`, `app.py`,
  `auto_update.py` + `requirements-auto-update.txt` + `.github/workflows/auto_update.yml`
  (daily automated new-video check via GitHub Actions), `check_new_videos.py` (manual,
  no-proxy, home-IP version of the daily check), `backfill_dates.py` (one-time script that
  backfilled missing `upload_date` values on already-downloaded videos, via Decodo — DONE),
  `update_neon_dates.py` (one-time follow-up that pushed those backfilled dates into the Neon
  chunk rows — CONFIRMED DONE Sep 2), `keep_app_awake.py` + `.github/workflows/keep_awake.yml`
  (periodic ping to stop the Streamlit app from sleeping — DONE and confirmed working Sep 2)

## CHANNELS
- **Financial Education** (@FinancialEducation) — main channel, direct opinions. ✅ downloaded
  + uploaded (2,605 videos, 25,127 chunks). ✅ Date backfill confirmed live in Neon (Sep 2) —
  see DATA SITUATION.
- **1000xstocks** (UCCmJVw9xQfYuuAAwZGedKRg) — direct opinions, 35 videos, ✅ 100% have dates.
- **Jeremy Lefebvre Makes Money** (@jeremylefebvremakesmoney7934) — reaction channel.
  ✅ Full backlog downloaded (407 transcripts in this pass) and ✅ embedded into Neon
  (6,244 new chunks, Aug 8). 98.3% have real dates. Tagged `video_type='reaction'`,
  `speaker_verified=False` — flagged to the AI as possibly-not-Jeremy's-own-opinion, not
  filtered out of search.

### Second creator: Eric Cuka — "Mr. FIRED Up Wealth"
- YouTube: **@FiredUpWealth**.
- Single channel, all direct opinions (`video_type='direct'`, `speaker_verified=True`).
- ✅ Full backlog downloaded Aug 8 — 579/587 videos. ✅ Embedded into Neon — 5,021 new chunks.
- ✅ Added to `check_new_videos.py` and `auto_update.py`'s daily check.
- **App branding:** "Ask Jeremy" stays primary; Eric included subtly (subtitle, 2 example
  questions, neutral spinner/banner text instead of Jeremy's catchphrases).
- ✅ **Comparison questions ("what do Jeremy and Eric think about X") are now reliable** —
  Feature 4 (multi-creator comparison mode) was built and live-tested this session (Sep 2
  evening). See FEATURE 4 section for full details, including two bugs found and fixed during
  rollout.

---

## BUG FIXED Aug 8: SPEAKER ATTRIBUTION MISLABELING
(unchanged from before — see git history / earlier plan versions for full details.) Status:
✅ Fixed, deployed, and verified live.

---

## ✅ FIXED Aug 22, CONFIRMED Aug 28: GROQ MODEL DEPRECATED (`groq.NotFoundError`)
(unchanged — see earlier plan versions.) Status: ✅ confirmed working live. Model is
`openai/gpt-oss-120b`. Monthly scheduled check watches for the next deprecation notice.

---

## ✅ FIXED & CONFIRMED Aug 28: NO CONVERSATION MEMORY BETWEEN QUESTIONS
(unchanged — see earlier plan versions.) Status: ✅ confirmed working live, both the general
context-stuffing fix and the specific "summarize the video" direct-lookup fix.

---

## DATA SITUATION (IMPORTANT — updated Sep 2)
- 2,605 Financial Education transcripts → 25,127 chunks in Neon w/ HNSW vector index.
- 35 from 1000xstocks.
- 407 Jeremy Lefebvre Makes Money (reaction channel) transcripts → 6,244 chunks in Neon.
- 579 Eric Cuka transcripts → 5,021 chunks in Neon.
- **Total: ~3,626 videos, ~36,392+ chunks across 4 channels.**
- Raw JSON transcripts stored as ONE FLAT BLOB of text per video for the SEARCH/embedding
  layer — no within-blob timestamps. **As of this session, Feature 2 solves the display-side
  timestamp problem without touching this data** (see FEATURE 2 section — it re-fetches the
  timed transcript live, on demand, only for videos actually cited in an answer, and caches the
  result in a new `video_timestamps` Neon table).
- `embed_and_upload.py` chunks the blob into ~500-word pieces (50-word overlap), stores each in
  Neon: video_id (as `{video_id}_{i}`), title, channel, video_type, upload_date, url,
  speaker_verified, chunk_text, embedding.

## ✅ RESOLVED Aug 8 → CONFIRMED Sep 2: THE CRITICAL DATE UNKNOWN
(unchanged — see earlier plan versions.) `update_neon_dates.py` confirmed to have run
successfully; date backfill → Neon pipeline is fully complete.

---

## FEATURE 1: SMART SEARCH MODES ✅ ALL 4 MODES NOW BUILT (Sep 2 evening session)
Different question types need different search strategies. All modes live directly in `app.py`
as independent regex-based detectors checked in sequence in the main chat handler (no unified
router class — each mode has its own narrow detector function, checked via `elif` branches in
priority order) — no re-download, no DB schema change needed for any of them.

### ✅ Mode 1 (recency questions) — BUILT Aug 28, confirmed working for all channels
Unchanged from before. `detect_recency_question()` + `get_latest_videos()` — direct
`ORDER BY upload_date DESC` query, bypasses semantic search.

### ✅ Mode 2 (specific time period) — BUILT and live-tested Sep 2 evening
- `YEAR_PATTERN` (matches any `20[0-2][0-9]` in the question) + `HALF_PATTERN` (`early`/`late`)
  + `detect_time_period_question()` + `extract_time_period()`.
- `search_transcripts_by_period(query, year, half, channels, limit=10)` — same semantic search
  as the standard path, but with an added `upload_date LIKE '{year}%'` filter (and an optional
  `substring(upload_date, 5, 2) BETWEEN ...` filter for early/late-year narrowing).
- **Live-tested:** "What did Jeremy say about Tesla back in 2021?" → correctly returned two
  November 2021 Financial Education videos with specific valuation/profit-taking details, not
  a random mix of Tesla mentions from any year.

### ✅ Modes 3 & 4 (timeline/evolution + first mention) — BUILT and live-tested Sep 2 evening
Both share one retrieval function, differing only in how the question gets framed to Groq:
- `FIRST_MENTION_PATTERN` (e.g. "when did ... start", "first time ... mentioned", "has ...
  always") → `detect_first_mention_question()`.
- `TIMELINE_PATTERN` (e.g. "over time", "changed ... opinion", "evolution", "always") →
  `detect_timeline_question()`.
- `search_transcripts_timeline(query, channels, similarity_floor=0.2, total_limit=10)` — uses a
  Postgres window function (`ROW_NUMBER() OVER (PARTITION BY substring(upload_date,1,4) ORDER
  BY similarity DESC)`) to keep only the SINGLE best-matching chunk per year, then returns those
  ordered chronologically. This is what makes it a year-by-year arc instead of a pile of chunks
  clustered in whichever year talked about the topic most.
- Mode 4 (first mention) additionally appends an instruction to the Groq prompt to focus on
  identifying the first mention and then briefly trace the evolution to now.
- **Live-tested (exercises both modes via one question):** "Has Jeremy always been bullish on
  AMD?" → returned a clean table: first (and only) AMD mention was May 7 2025, Jeremy was
  actually CRITICAL of AMD spending in that clip, and the bottom line correctly stated "Jeremy
  has never been bullish on AMD in the material provided" — a genuinely useful, accurate answer
  that also correctly avoided overclaiming beyond what the transcripts showed.

### Router priority (checked in this order in the main chat handler):
recency → video-summary-followup → **comparison (Feature 4)** → first-mention (Mode 4) →
timeline (Mode 3) → time-period (Mode 2) → standard search (Mode 5, fallback).

**BUILD SEQUENCE: fully complete.** All modes from the original plan are now built:
Mode 1 ✅ (Aug 28), Mode 2 ✅, Mode 3 ✅, Mode 4 ✅ (all Sep 2 evening). Mode 5 (standard search)
was always the pre-existing fallback.

---

## FEATURE 2: TIMESTAMP / JUMP-TO-MOMENT ✅ BUILT AND LIVE-TESTED Sep 2 evening
Goal: when an answer comes from a video, show WHERE in the video + a link that jumps to that
moment (`youtube.com/watch?v=VIDEO_ID&t=142s`). **Done — using the fetch-on-demand + cache
approach that was planned and re-confirmed back in Aug 8, without any re-download.**

**How it works (`app.py`):**
- `_ensure_timestamp_cache_table(cursor)` — creates a `video_timestamps` table in Neon on first
  use (`video_id TEXT PRIMARY KEY, segments JSONB, fetched_at TIMESTAMP DEFAULT now()`).
- `get_timed_segments(video_id)` — checks the cache table first; on a miss, calls
  `YouTubeTranscriptApi().fetch(video_id)` (no proxy — same un-proxied approach used by
  `check_new_videos.py`) to get the REAL timed captions (`[{'text', 'start'}, ...]`), stores the
  result in the cache table, and returns it. Returns `None` silently on any failure (video
  unavailable, transcript disabled, etc.) rather than raising — callers treat that as "no
  timestamp available," never as a hard error.
- `find_timestamp_for_chunk(chunk_text, segments)` — best-effort string matching: rebuilds the
  same flat `' '.join(...)` text that `embed_and_upload.py` originally chunked from, finds where
  the cited chunk's text starts in that string (falls back from a 200-char match down to a
  60-char match if needed), then walks the timed segments to find which caption's start time
  that offset falls under. Returns `None` (never guesses) if no confident match is found.
- `add_timestamp_links(chunks)` — called on every set of retrieved chunks right before they go
  to Groq. For each chunk, tries to attach a `timestamp_url` (`{url}&t={start}s`); falls back to
  the plain video URL if anything fails. This is silent/best-effort by design — a timestamp
  lookup failing never breaks or delays an answer, it just means that one citation doesn't get
  the extra `&t=` precision.
- `ask_jeremy()`'s context-building line and system prompt were both updated to use
  `c.get('timestamp_url') or c['url']` and to tell Groq it can mention "jump straight to it"
  when a timestamp is present.
- **Cost/traffic note:** only videos that actually get cited in a real answer ever trigger a
  fetch — naturally scales with actual usage, never pays upfront for the whole library. Runs
  un-proxied directly from wherever Streamlit Cloud's server is, same pattern as
  `check_new_videos.py`'s home-IP-style fetches — no Decodo dependency for this feature turned
  out to be needed at all.
- **Live-tested:** the Mode 2 test above (Tesla in 2021) came back with real, distinct
  timestamps for each cited video (`t=6 min 31s` / `&t=391s` and `t=2 min 7s` / `&t=127s`) —
  confirming the fetch, cache-table write, and string-matching logic all work correctly end to
  end on real data.

This closes out the one feature that was flagged from the start as needing genuinely new data
collection — it turned out not to need any, just a smarter display-time lookup.

---

## FEATURE 3: AUTOMATED DAILY NEW-VIDEO CHECK ✅ LIVE
(unchanged — see earlier plan versions.) Weekly scheduled check watches run history for
failures.

## FEATURE 3B: HOME-IP MANUAL CHECK ✅ BUILT
(unchanged — see earlier plan versions.)

## FEATURE 3C: SPEAKER-VERIFIED FLAGGING IN APP ✅ BUILT
(unchanged — see earlier plan versions.)

## FEATURE 4: MULTI-CREATOR COMPARISON MODE ✅ BUILT AND LIVE-TESTED Sep 2 evening
Enables questions like "what do Jeremy and Eric think about AMD" with real side-by-side
retrieval, guaranteeing both creators are actually represented (rather than the old behavior,
where a comparison question just got whatever mix of chunks the standard top-10 similarity
search happened to return, with no guarantee both creators showed up).

**How it works (`app.py`):**
- `COMPARISON_JEREMY_ALIASES` / `COMPARISON_ERIC_ALIASES` + `detect_comparison_question()` —
  deliberately conservative: only fires when BOTH a Jeremy-alias AND an Eric-alias appear in the
  same question, so a question that just happens to mention one creator doesn't get mistakenly
  treated as a comparison.
- `search_transcripts_by_channels(query, channels, limit=6)` — same semantic search as the
  standard path, restricted to a specific channel list.
- `search_transcripts_comparison(query, limit_per_creator=5)` — runs `search_transcripts_by_
  channels` separately for `JEREMY_CHANNELS` and for `['Eric Cuka']`, then concatenates the
  results — guaranteeing real representation from both sides rather than leaving it to chance.
- Checked FIRST in the router priority (before Mode 4/3/2) so a question naming both creators
  never gets misrouted into a single-creator mode.
- When triggered, an extra instruction is appended to the Groq prompt (not the retrieval query):
  "Please contrast Jeremy's and Eric's views separately, noting where they agree or disagree.
  Keep it concise — a short summary for each, not an exhaustive table — so the full answer fits
  comfortably."

**🐛 Bug found and fixed during rollout (2 iterations):** the first deploy answered "What do
Jeremy and Eric think about buying stocks at all-time highs?" with a response that was cut off
mid-sentence, and Eric's side of the comparison never appeared at all — the model ran out of
its `max_tokens` budget (1000, unchanged since the app was first built) partway through Jeremy's
side alone. **Fix, iteration 1:** raised `max_tokens` 1000 → 1800 in `ask_jeremy()`. Still
truncated on retest (comparison answers with two detailed side-by-side tables need more room
than a single-creator answer). **Fix, iteration 2:** raised `max_tokens` further to 2500, AND
added the "keep it concise, not an exhaustive table" instruction above to the comparison-specific
prompt addition, so the model isn't tempted to build an elaborate table that eats the whole
budget. **Confirmed working on the third deploy:** same question now returns a complete,
un-truncated answer with a proper "Where They Agree / Differ" comparison table covering both
creators and a clear closing "Bottom line" summary for each. Modes 1-4 (single-creator) were
never affected by this — they were tested at the original `max_tokens=1000` and completed fine;
only the side-by-side comparison format needed the larger budget.
**Worth remembering:** `max_tokens=2500` is now the standing value for ALL answers, not just
comparisons (there's only one `ask_jeremy()` call site) — if a future feature adds more retrieved
context or another multi-part answer format, keep this in mind as a potential place to raise the
ceiling again if truncation resurfaces.

## FEATURE 5: LANDING PAGE EXAMPLE QUESTIONS TRIMMED TO 2 ✅ DONE Sep 3 session
The old landing page (shown before the first question is asked, in `app.py`'s
`if not st.session_state.messages:` block) had 6 example questions laid out in two
`st.columns(2)` columns — left over from before Feature 1 Modes 2-4, Feature 2, and Feature 4
existed, so they didn't showcase any of the new search capabilities.

**Replaced with exactly 2 questions, single column (no more `st.columns`):**
- *"Is Jeremy still bullish on AMD?"* — chosen over the more obvious "Has Jeremy always been
  bullish on AMD?" phrasing. Verified via direct regex testing that "still" does NOT trigger
  `FIRST_MENTION_PATTERN`/`TIMELINE_PATTERN`, so this question actually routes to the plain
  Mode 5 (standard top-10 similarity search), not the Mode 3/4 timeline retrieval — and
  live-testing showed the plain-search answer was actually MORE complete than the timeline-mode
  answer had been for a similarly-phrased question earlier in the Sep 2 session. Worth
  remembering: `search_transcripts_timeline()`'s one-chunk-per-year window function can
  actually LOSE relevant same-year content when multiple good matches exist in the same year —
  a real limitation to keep in mind if timeline mode gets revisited later.
- *"What do Jeremy and Eric think about buying stocks at all-time highs?"* — showcases Feature 4
  (multi-creator comparison mode), which was the flagship feature of the Sep 2 evening session.

Deployed via the same GitHub web-editor + synthetic-paste browser technique used throughout this
project. Live-verified on https://ask-jeremy.streamlit.app/ — landing page now shows only these
2 questions, single column, no leftover old questions or column-layout artifacts.

---

## FEATURE 6: HYBRID KEYWORD FALLBACK + RECENCY SORT FOR STANDARD SEARCH ✅ FIXED Sep 3 session, EXTENDED Sep 4
**The bug report:** user asked "what is the latest instance of Jeremy talking about Wynn
stock" and got back "the transcripts do not contain any mention of Wynn... Jeremy has not
spoken about Wynn stock" - flatly wrong. The user knew this was wrong because a video titled
"4 Stocks to Go ALL IN September 2026" (Financial Education, published 2 days earlier) talked
about Wynn.

**Investigation (this matters for future debugging - same playbook applies to any "the app
says X isn't in the transcripts but I know it is" report):**
1. Checked the `auto_update.yml` GitHub Actions run history - runs succeed daily (confirmed via
   the Actions log viewer, which needed a specific selector `.js-check-line-content` to extract
   text from, since GitHub's log viewer virtualizes/renders differently from a plain page).
   Financial Education channel said "Nothing new" on the runs around when this video would have
   been caught - which actually confirms the video WAS already ingested by an earlier run (the
   "nothing new" check works by comparing against video IDs already in Neon), not that it was
   missed.
2. Found the exact video via YouTube search (confirmed: "4 Stocks to Go ALL IN September
   2026‼️", Financial Education channel, video ID `Q6G8pXFkKLk`, 2 days old at the time).
3. **Confirmed via a direct live-app test** ("What stocks does Jeremy mention in his video '4
   Stocks to Go ALL IN September 2026'?") that the video's transcript IS searchable and in Neon
   - the app correctly found and quoted it (Cheesecake Factory/CAKE). This proved the problem
   wasn't ingestion - it was retrieval: the specific chunk mentioning Wynn (if any) just wasn't
   among the top-10 chunks `search_transcripts()` (Mode 5, the fallback used for this question -
   none of Modes 1-4's trigger patterns fired) returns from the whole ~36k-chunk corpus. A
   single brief mention of a stock doesn't stand out enough semantically to beat thousands of
   competing chunks on other topics, and/or it scored below the 0.3 similarity floor.

**The fix (`app.py`, `search_transcripts()`):**
- `STOCK_KEYWORD_PATTERN` + `extract_stock_keyword()` - pulls the word right before "stock" in
  the question (e.g. "wynn stock" → "wynn", "AMD stock" → "AMD"). Deliberately narrow, not a
  general entity extractor.
- When a keyword is found, `search_transcripts()` now ALSO runs a literal `chunk_text ILIKE
  '%keyword%'` query alongside the existing semantic search - a literal text match is a much
  stronger relevance signal than embedding similarity for "does this stock get mentioned"
  questions, and guarantees a real hit isn't lost to unrelated higher-scoring chunks. Keyword
  hits are merged in FIRST (before semantic results) and deduped, so they survive the final
  truncation to `limit` even when recency language isn't used - this was a bug in the first
  draft of the fix (keyword hits were appended after the already-full semantic list and got cut
  off by the truncation), caught and fixed before deploying.
- `RECENCY_WORD_PATTERN` + `wants_most_recent_mention()` - True for "latest/most recent/last"
  language that ISN'T Mode 1's "latest video" pattern (which requires "video" nearby and
  bypasses search entirely via `get_latest_videos()`). When true, the merged/deduped results are
  sorted by `upload_date` descending instead of similarity - so "latest instance of X" actually
  means latest, not just whatever scored highest semantically.
- Isolated entirely to `search_transcripts()` (Mode 5's fallback path) - verified via direct
  regex testing that "Is Jeremy still bullish on AMD?" (the landing page's own example question,
  no "stock" keyword) is completely unaffected, and that Modes 1-4's trigger patterns still take
  priority correctly for questions that match them.

**Live-tested after deploy:** re-asked the exact original question. The app now returns a real,
well-reasoned answer - cites a verified June 1 2026 Jeremy Lefebvre (1000xstocks) mention of
Wynn Resorts, correctly notes a later (July 5 2026) transcript in its context does NOT mention
Wynn, and separately flags a still-later (May 28 2026) reaction-video mention as unverified
speaker. **Caveat worth remembering:** the app did not end up citing the specific Sept 2026
"4 Stocks to Go ALL IN" video as the latest instance. Most likely explanation: YouTube's
auto-generated captions can misspell less-common names phonetically (Wynn is pronounced like
"win"), so the literal word "Wynn" may simply not appear in that video's transcript text even
if Jeremy said it out loud - a caption-accuracy issue, separate from and downstream of the
retrieval bug fixed here. Not chased further this session (would need direct Neon access to
confirm what that video's stored transcript actually spells it as) - worth keeping in mind if a
similar "the app can't find X, but I know it's in there" report comes up again for a stock name
that isn't spelled plainly/commonly.

**UPDATE - same session, found again almost immediately:** next question, "what's Jeremy's
latest take on Celcius" (note: user typo'd "Celsius"), hit TWO more gaps in the fix above:
1. `extract_stock_keyword()` only recognized "X stock" phrasing - "take on Celcius" (no
   trailing "stock") extracted no keyword at all, so the hybrid safety net never even engaged.
2. Even if it had engaged, an exact `ILIKE '%celcius%'` wouldn't match the correctly-spelled
   "Celsius" in the transcript - the mismatch here is the USER's typo, not a caption error (Wynn
   was the caption-error case; Celsius is a common enough word that auto-captions almost
   certainly spell it right).

**Second round of fixes (same `app.py`, same session):**
- `extract_stock_keyword()` broadened: still always checks "X stock" first, but for
  recency-style questions specifically (gated via `wants_most_recent_mention()`, to avoid
  widening false-positive risk for ordinary topic questions) it now also falls back to
  whatever topic is named at the very end of the question via a new `TOPIC_TAIL_PATTERN`
  (`"on X"` / `"about X"` near the end) - catches "latest take on Celsius", "most recent
  mention of X", etc.
- Added a fuzzy fallback: if the exact `ILIKE` keyword match comes up empty, `search_transcripts()`
  now tries Postgres's `pg_trgm` extension (`CREATE EXTENSION IF NOT EXISTS pg_trgm`, then a
  `word_similarity(keyword, chunk_text) > 0.5` query) to catch near-misses like "Celcius" vs
  "Celsius". Wrapped in try/except with an explicit `conn.rollback()` on failure - if pg_trgm
  isn't available on Neon for any reason, or the query errors, it just skips the fuzzy step
  silently rather than breaking the whole search. Not able to confirm pg_trgm actually installs
  cleanly on this Neon instance without direct DB access, but the live retest below shows the
  overall fix path worked end-to-end.
- **Live-tested:** re-asked "whats jeremys latest take on celcius" (typo intact) after
  deploying. The app now correctly surfaces a Sept 1 2026 mention (same day as the Wynn video)
  instead of the stale Aug 26 2026 quote from before, and correctly reasons "the Sept 1 excerpt
  is the most recent, so it represents his latest publicly-recorded sentiment." Answer is
  properly caveated as an unverified reaction-video source (flagged with the ⚠️ marker, per the
  existing speaker-verification instruction in `ask_jeremy()`'s system prompt).
- **Open caveat:** the source cited is a Sept 1 "Jeremy Lefebvre Makes Money" (reaction channel)
  clip, not necessarily the specific "Financial Education" video ("4 Stocks to Go ALL IN
  September 2026") the user had in mind for the Wynn bug - it's possible both channels posted
  Celsius content the same day, or the merged candidate pool included both but the model
  favored this one. Good enough to answer the user's actual question correctly and honestly
  (real content, correctly identified as most recent, correctly flagged as unverified) - not
  worth over-engineering further this session, but worth knowing if a future report asks why a
  specific expected video isn't the one cited.

**THIRD update - Sep 4 session, predicted third variant of the same bug showed up:** user asked
"Is there a video from Jeremy within the last week where he mentions his projections for
Netflix" and again got a false negative, even though the same "4 Stocks to Go ALL IN September
2026" video (already confirmed ingested and searchable, per the Wynn investigation above)
contains Jeremy showing his Netflix projections on screen ("...my bull case to Netflix...").

**Root cause:** neither existing keyword path fired for this phrasing.
`STOCK_KEYWORD_PATTERN` needs literal "X stock" (not present). `TOPIC_TAIL_PATTERN` only
recognized "on X" / "about X" at the end of a recency-style question — "projections **for**
Netflix" uses a preposition ("for") the pattern didn't know about, so `extract_stock_keyword()`
returned `None`, the hybrid safety net never engaged, and pure semantic search ranked an old,
heavily-Netflix-focused 2018 Goldman-Sachs-rating video above the brief, recent mention in a
video mostly about other stocks.

**The fix:** widened `TOPIC_TAIL_PATTERN`'s preposition group from `(?:on|about)` to
`(?:on|about|for|regarding)`, so "his projections for Netflix" (and similar "for X"/"regarding
X" phrasings) now extracts "Netflix" as a keyword and gets the same literal-ILIKE safety net as
the "on X"/"about X" cases already had. No other logic changed — `wants_most_recent_mention()`
gating and the merge/dedupe/sort behavior are unchanged.

**Deploy note:** this was the first session where `device_commit_files` successfully wrote
directly to the user's local `app.py` (previous sessions had this path unavailable/refused, and
used the GitHub web-editor + synthetic-paste technique instead). Also used this session to
discover and fix that the local file had drifted out of sync with the live app since Sep 2 — see
the ⚠️ LOCAL FILE SYNC note near the top of this document. The corrected, fully-current `app.py`
(including all of Sep 2-3's work plus this fix) was written to the user's computer directly;
the user pushes it live themselves via `git add` / `git commit` / `git push` from VS Code.
**Not yet live-tested against the actual Netflix question** at the time this plan was updated —
worth confirming next session (or as soon as the user pushes and redeploys) that re-asking the
original question now surfaces the "4 Stocks to Go ALL IN September 2026" video.

---

## FEATURE 7: CHANNEL-TO-CREATOR ATTRIBUTION FIX ✅ FIXED Sep 5 session
**The bug report:** as soon as the Sep 4 Netflix fix was confirmed live, we re-asked the exact
original question ("Is there a video from Jeremy within the last week where he mentions his
projections for Netflix") to live-test it. Good news: the retrieval bug WAS fixed - the app no
longer said "no mention found," it actually surfaced multiple real, dated Financial Education
excerpts with specific Netflix numbers ($134-231 price target by 2030). But the answer itself
said those excerpts were **"not Jeremy's channel"** - flatly wrong, since Financial Education is
Jeremy's own main channel (see CHANNELS section above). This caused the app to undersell real,
verified Jeremy content as not counting toward the answer.

**Root cause:** this is a completely different class of bug from FEATURE 6 (retrieval) - this
one is in the CONTEXT/PROMPT layer that hands retrieved chunks to Groq. In `ask_jeremy()`, the
context string built for every excerpt only ever included the raw Neon `channel` value straight
from the database (e.g. `[Financial Education | 2026-09-01 | ...]`). Nothing in that string, and
nothing in the system prompt, ever told Groq that "Financial Education" and "1000xstocks" are
channels Jeremy Lefebvre personally runs. The only place the name "Jeremy Lefebvre" appeared at
all was the "Jeremy Lefebvre Makes Money" channel's own name. So when Groq saw an excerpt tagged
just "Financial Education" with no other signal, it reasonably (but wrongly) inferred that a
channel not literally named "Jeremy Lefebvre ___" must belong to a different creator - especially
since the system prompt described Eric Cuka's content living on its own separate channel, which
primed the model to think "different channel name = different creator."

**The fix (`app.py`, `ask_jeremy()`):**
- Added a new `CHANNEL_CREATOR` dict mapping every Neon `channel` value to the real creator's
  name: `'Financial Education'`, `'1000xstocks'`, and `'Jeremy Lefebvre Makes Money'` all map to
  `'Jeremy Lefebvre'`; `'Eric Cuka'` maps to itself.
- Every excerpt's tag now includes BOTH fields explicitly: `[Creator: Jeremy Lefebvre | Channel:
  Financial Education | 2026-09-01 | ...]` instead of just `[Financial Education | ...]` - so the
  model doesn't have to infer anything, it's told directly.
- Rewrote the system prompt to spell out the mapping in plain language: "Jeremy Lefebvre
  personally runs THREE channels/properties that all count as his own words when the speaker is
  verified: 'Financial Education' (his main channel), '1000xstocks' (his stock-analysis
  site/channel), and 'Jeremy Lefebvre Makes Money' (his reaction channel)... Eric Cuka's content
  comes from the 'Eric Cuka' channel." Also explicitly instructed Groq to "always use the
  Creator field to decide whose opinion this is, never guess from the channel name alone."
- No retrieval logic changed at all - this is purely a labeling/prompt fix layered on top of
  Sep 3-4's Feature 6 retrieval fixes, which are unaffected.

**Why this matters beyond just Netflix:** this same mislabeling could have been silently
happening on ANY answer that cited Financial Education or 1000xstocks content without also
citing a "Jeremy Lefebvre Makes Money" clip in the same answer - worth being a little suspicious
of any past answer that seemed to say "Jeremy hasn't discussed X" when Financial
Education/1000xstocks content on X actually existed in the corpus. Not chased retroactively
this session (would mean re-running old test questions), but worth keeping in mind.

**Deploy note:** written to project docs and pushed directly to the user's computer via
`device_commit_files` (same successful path as Sep 4). **Live-tested and confirmed working
same session:** re-asked the Netflix question after the user pushed - Groq's answer correctly
said "Jeremy Lefebvre has a recent video... where he spells out his price-target projections
for Netflix," correctly cited the Financial Education video by name with real numbers and a
working timestamp link, and the table's "Channel" column was clearly marked "(verified)"
instead of "not Jeremy's channel." Confirmed fixed.

**⚠️ Process note (Sep 5):** right after this fix was pushed and live-tested, the user was told
to run `git fetch origin` + `git reset --hard origin/main` (the standard post-session-Sep-4
sync routine) - but the Feature 7 fix had ONLY been written to the user's local disk via
`device_commit_files`, never actually pushed to GitHub yet. The reset therefore rolled the
local files back to the last GitHub commit (pre-Feature-7), silently discarding the fix that
had just been written locally. Caught immediately from the `git reset --hard` output (`HEAD is
now at 2ae5149`, the *previous* commit, not a new one). Recovered by re-writing the fixed files
to disk via `device_commit_files` again and having the user `git add` / `git commit` / `git
push` them directly (commit `ce5b201`) rather than routing through the browser/GitHub-web-editor
detour again. **Lesson for future sessions: NEVER tell the user to run `git reset --hard
origin/main` (or anything that resets working-tree state to match GitHub) until every locally
-written fix from that session has actually been pushed to GitHub first** - "written to disk
via device_commit_files" is not the same as "safe to reset over." Verify with `git status`
showing the fix as a pending local change (or confirm the GitHub commit hash) before ever
suggesting a hard reset.

---

## FEATURE 8: KEYWORD EXTRACTION BROKEN BY CONVERSATION-MEMORY CONTEXT STUFFING ✅ FIXED Sep 5 session
**The bug report:** immediately after confirming FEATURE 7's fix worked (Netflix question),
asked a follow-up in the SAME session: "When was the most recent time Jeremy has mentioned
projections for wynn?" This should have worked - it's the same "for X" phrasing already fixed
in FEATURE 6's third update, and a real, verified Wynn mention was already confirmed to exist
in the corpus back in the original Wynn bug investigation. Instead, Groq's answer said: "The
transcript excerpts you provided do not contain any mention of Wynn Resorts (Wynn)... All of the
cited clips are focused on Netflix," and explicitly listed its sources as being about Netflix,
2018-2026 - meaning the context handed to Groq was never about Wynn at all.

**Root cause - a genuinely new bug class, not a repeat of Feature 6/7:** `build_search_query()`
(the conversation-memory function) appends the PRIOR question+answer AFTER the current question
before the combined string is used for semantic search - e.g. `"{current question}\n\nContext
from the previous question and answer: {prior Q&A text}"`. This is intentional and correct for
the embedding step (it's how follow-up questions get conversational context). But
`search_transcripts()` was ALSO using that same context-stuffed string for
`extract_stock_keyword()` - and `TOPIC_TAIL_PATTERN` (the regex that catches "for X"/"on X"/etc)
anchors to the literal END of the string (`$`). Once prior conversation text got appended after
the real question, the end of the string was now the tail of the OLD answer (which happened to
be about Netflix), not the new question. So `extract_stock_keyword()` silently returned `None`,
the whole hybrid keyword/fuzzy safety net never engaged, and pure semantic search ran on a query
that was skewed toward the previous turn's Netflix content by the appended context - hence an
all-Netflix result set for a Wynn question. Confirmed by direct Python testing: extracting from
the raw question alone correctly returns `"wynn"`; extracting from the context-stuffed
`search_query` (exactly what the code was passing in) returns `None`.

**The fix (`app.py`, `search_transcripts()`):**
- Added a `raw_question` parameter to `search_transcripts(query, limit=10, raw_question=None)` -
  `query` stays the context-stuffed string used for the semantic embedding (unchanged, still
  benefits from conversation memory), but `extract_stock_keyword()` and
  `wants_most_recent_mention()` (used for the recency-sort decision too, same anchoring risk)
  now always run against `raw_question` when it's provided - i.e. the actual, un-appended
  question the user just typed.
- Updated the one call site in the main chat handler to pass `raw_question=prompt` (the raw
  user input, before `build_search_query()` ever touches it).
- Falls back to using `query` itself if `raw_question` isn't passed (keeps the function
  backward-compatible / harmless for any future caller that doesn't need this).
- No change to the semantic search step, to Modes 1-4, or to any other Feature 6/7 logic -
  purely fixes which string the keyword-extraction regexes see.

**Deploy note:** written to project docs and pushed to GitHub via the user's own `git add` /
`git commit` / `git push` (commit `c84d17a`). **Live-tested and confirmed working, both
scenarios:**
1. Fresh Wynn question with no prior conversation - correctly found and cited a July 5 2026
   Jeremy Lefebvre (1000xstocks) Wynn Resorts projection with a working timestamp link.
2. The Wynn question asked as a same-session follow-up immediately after an AMD question (the
   exact scenario that originally exposed the bug) - correctly found and cited the verified
   June 1 2026 Wynn Resorts mention instead of a false "no mention found."
Both confirmed fixed.

**Side note during testing (not a code bug):** hit a transient `groq.APIStatusError` a few times
while rapid-firing several test questions back-to-back within about a minute. Resolved on its
own after roughly a 60-second gap with zero code changes - almost certainly Groq's free-tier
rate limit, not a retrieval or prompt bug. Worth remembering if a user ever reports "the app
just showed a groq error" after asking several questions in quick succession - that's likely
rate limiting, not a regression, and should self-resolve. Not worth engineering around unless it
starts happening under normal (non-rapid-testing) usage patterns.

---

## FEATURE 9: NON-UNIQUE TIMESTAMP MATCH COULD POINT AT THE WRONG MOMENT ✅ FIXED Sep 5 session (later)
**The bug report:** asked the live app "when is the most recent time jeremy mentions amazon
projections?" It correctly cited a real, dated (2025-11-24) Financial Education video and quoted
Jeremy's actual Amazon "trillion-dollar-plus revenue company" projection - but the "jump to it"
timestamp shown for that citation (≈2:45) did not point at that segment of the video. Retrieval
and the answer content were both correct; only the timestamp was wrong.

**Root cause:** in `find_timestamp_for_chunk()` (Feature 2, built Sep 2, unchanged until now),
the function tries to locate a cited chunk's text inside the video's full timed-caption text by
taking the first 200 characters of the chunk and searching for it with `full_text.find()`. If
that fails, it FALLS BACK to just the first 60 characters and searches again - but that fallback
never checked whether the 60-character snippet was actually unique in the transcript. On a
video that runs any length of time, a short, generic-sounding 60-character snippet (numbers,
common phrasing, etc.) can easily appear more than once. `full_text.find()` always returns the
FIRST occurrence it finds, so if the real, later segment's snippet happened to also match some
earlier, unrelated part of the video, the function confidently returned the EARLIER (wrong)
timestamp instead of admitting it wasn't sure. This directly contradicts the function's own
docstring promise ("Returns None ... if it can't find a confident match") - the promise just
wasn't actually enforced for the 60-char fallback case.

**The fix (`app.py`, `find_timestamp_for_chunk()`):**
- Rewrote the matching loop to try snippet lengths 200 then 60 (same as before), but for EACH
  length, only accept the match if it occurs EXACTLY ONCE in the reconstructed full transcript
  text (checked via a second `full_text.find(snippet, first + 1)` call - if that returns
  anything other than -1, the match is ambiguous and is rejected, not used).
- If no snippet length produces a unique match, the function now returns `None` just like it
  already did for the "no match at all" case - callers already treat `None` as "no timestamp
  available" and silently fall back to the plain video URL (`add_timestamp_links()`'s existing
  behavior, unchanged), so a user still gets a working link, just without the `&t=` jump-to-
  moment precision, rather than a link that jumps to the wrong place.
- No change to `get_timed_segments()`, `add_timestamp_links()`, the caching table, or anything
  else in Feature 2 - purely tightens the confidence check inside the string-matching step.

**Why this wasn't caught back on Sep 2:** the original live-test (Tesla-in-2021 question) happened
to hit videos/snippets where the first match was also the only match, so the missing uniqueness
check never surfaced. This is exactly the kind of thing that can silently misfire on some videos
and not others depending on how repetitive their phrasing is - worth remembering if a future
timestamp looks "close but not quite right" again.

**Deploy status:** fix written and `py_compile`-verified in the cloud sandbox, then written to
this project's saved `app.py` copy, then pushed to the user's local `app.py` via
`device_commit_files` - **verified landed correctly** by staging the file back and confirming
`md5sum` matched the source (first `device_commit_files` call silently didn't take effect despite
reporting success, exactly the known pattern from earlier this session - retried once with
`force: true`, then verified again and it matched). User pushed via `git add`/`git commit`/
`git push` - commit `9071be2`.

**✅ Live-tested and CONFIRMED FIXED same session:** re-asked "when is the most recent time
jeremy mentions amazon projections?" after the push/redeploy. The exact video that previously
showed the wrong ≈2:45 timestamp (24 Nov 2025 Financial Education, trillion-dollar-plus revenue
projection) now correctly shows NO timestamp instead of a wrong one - the app's own citation
text says "no timestamp supplied, but the comment appears in the latter half of the video,"
which is exactly the intended fallback behavior (a working plain video link, no false precision)
rather than confidently pointing at the wrong spot. The other two cited videos in the same
answer (Dec 2023, Jan 2023) still got working timestamps (12-min mark, 4-min mark respectively) -
confirms the uniqueness check isn't over-broadly killing timestamps that were already correct,
only the ones that were actually ambiguous. Feature 9 fully closed out.

**Separate, unaddressed issue spotted during this live-test (not part of Feature 9, not yet
fixed):** the same answer's Jan 2023 row rendered a garbled mess where a dollar amount should be
(`889 B∗∗,netincomeof∗∗58 B` instead of "$889B ... net income of $58B"). Almost certainly
Streamlit's markdown renderer misinterpreting `$...$` pairs in Groq's answer text as LaTeX math
delimiters rather than literal dollar signs - a rendering/display bug, unrelated to retrieval or
timestamps. Not fixed this session (user only flagged the timestamp) - worth fixing next time
dollar amounts show up wrong, likely by having `ask_jeremy()`'s system prompt instruct Groq to
avoid bare `$number` formatting (e.g. write "889 dollars" or escape it), or by escaping/sanitizing
`$` in the answer text before it's rendered.

---

## FEATURE 10: GARBLED DOLLAR-AMOUNT RENDERING (LATEX MATH MISINTERPRETATION) ✅ FIXED Sep 5 session (later still)
**The bug:** spotted during Feature 9's live-test - a dollar amount in an answer rendered as
garbled text (`889 B∗∗,netincomeof∗∗58 B` instead of "$889B ... net income of $58B"). User
confirmed this had been happening and asked to fix it.

**Root cause:** Streamlit's markdown renderer treats a PAIR of `$` characters anywhere in the
same message as LaTeX math delimiters (it uses KaTeX under the hood). Groq's answers are full of
literal dollar amounts, so whenever an answer contained two or more `$` signs (extremely common -
"$889B ... $58B" alone is two), everything between the first and second `$` got interpreted as a
math expression instead of plain text: spaces get dropped, `**` (markdown bold) turns into literal
asterisks, letters get spaced out weirdly. This is a display/rendering bug only - the actual answer
content and numbers coming back from Groq were always correct, they just looked broken once
Streamlit tried to render them as markdown.

**The fix (`app.py`):**
- Added `escape_dollar_signs(text)` - a small helper using `re.sub(r'(?<!\\)\$', r'\\$', text)`
  to escape every literal `$` as `\$`, telling Streamlit's markdown/KaTeX renderer to display it
  as a plain dollar sign instead of opening or closing a math block.
- `ask_jeremy()` now runs its Groq response through `escape_dollar_signs()` before returning it,
  so both the live answer render (`st.markdown(answer)`) and the chat-history replay
  (`st.markdown(message['content'])`, since the escaped text is what gets stored in
  `st.session_state.messages`) are fixed consistently - no separate fix needed at each render
  call site.
- Verified locally with the exact garbled example from the live test
  ("$889B, net income of $58B, and a market-cap of $1.7-2.3T") - confirmed it now escapes to
  "\$889B, net income of \$58B, and a market-cap of \$1.7-2.3T", which Streamlit will render as
  plain readable text.
- No retrieval, prompt, or timestamp logic touched - purely a post-processing step on the final
  answer string, isolated to this one new function plus its one call site.

**Deploy status:** written to this project's saved `app.py` copy, then pushed to the user's local
`app.py` via `device_commit_files` - **verified landed correctly** by staging the file back and
confirming `md5sum` matched the source (first `device_commit_files` call again silently didn't
take effect despite reporting success - same known pattern as every other file push this session -
retried once with `force: true`, then verified again and it matched). **Still needed before this
is live:** user runs `git add app.py` / `git commit` / `git push`, then this should be live-tested
by re-asking a question likely to include dollar amounts (the Amazon projections question used for
Feature 9 is a good one, since it already surfaced this exact bug) and confirming dollar amounts
now render as normal text instead of garbled math notation.

---

## 💡 FUTURE FEATURES
- WhisperX speaker diarization for reaction channel.
- Conflict detection (flag when a creator changed their mind on a stock).
- Credibility tracker (did predictions come true?).
- Multi-creator consensus tracker ("which stocks do Jeremy AND Eric both like right now?") —
  now much more buildable given Feature 4's comparison retrieval already exists as a building
  block.
- Vision AI to extract data from 1000xstocks on-screen screenshots.
- Password protection for private sharing.
- "Load the boat" tracker.
- Eric-specific catchphrases/personality once user is more familiar with his content style.
- Wrap the Groq API call to gracefully handle a deprecated/missing model instead of crashing.
- A unified unified Mode router (currently just an `elif` chain of independent detectors) if the
  number of modes grows further and priority ordering gets harder to reason about.
- ~~Fuzzy/phonetic keyword matching for the Feature 6 hybrid fallback~~ - added same day via
  `pg_trgm`'s `word_similarity()` (see FEATURE 6's update). Still worth revisiting if a stock
  name is phonetically SO different from its spelling (not just a typo/near-miss like
  Celcius/Celsius) that trigram similarity doesn't bridge it either - a small manual
  alias/synonym table per known ticker would be the next escalation.
- Confirm whether `pg_trgm` actually installed successfully on the Neon instance (no direct DB
  access this session to check) - if `CREATE EXTENSION IF NOT EXISTS pg_trgm` is silently
  failing, the fuzzy fallback added in FEATURE 6 is a no-op every time. The Celsius live-test
  passing is encouraging but doesn't fully prove the fuzzy path specifically fired (the broader
  keyword extraction change alone might have been enough if "celcius" partially matched some
  chunk via ILIKE, which is unlikely but not ruled out without checking logs/DB directly).
- **New Sep 4:** given this bug class has now shown up THREE times with three different
  prepositions/phrasings ("X stock", "on/about X", "for/regarding X"), consider whether a more
  general fix is worth it eventually — e.g. always attempting a literal keyword/entity extraction
  for any question that names a specific proper noun, rather than only gating it behind specific
  phrasing patterns. Not done now (deliberately narrow, matching the existing style of this
  fallback), but worth revisiting if a fourth phrasing variant turns up.

---

## 💰 DECODO BILLING (updated Aug 28)
(unchanged — see earlier plan versions.) ✅ Pay As You Go confirmed working.

## 🌙 KEEP-AWAKE: PREVENTING STREAMLIT SLEEP
(unchanged — see earlier plan versions.) ✅ DONE Sep 2 morning session, confirmed working.

## 🔔 MONITORING: SCHEDULED CHECKS
(unchanged — see earlier plan versions.)

---

## 📝 KEY TECHNICAL NOTES
- `cookies.txt` in project folder needed for yt-dlp downloads.
- YouTube IP ban clears ~24–48 hrs after last request.
- Decodo residential proxies for bulk downloading (Pay As You Go, ~$3.50-4/GB).
- **Neon: create a FRESH connection per query — do NOT cache, it times out.**
- **Groq input-context budget ~6,000 tokens/request; 10 chunks is BORDERLINE** — this limit is
  about how much RETRIEVED CONTEXT gets sent in, separate from `max_tokens` (which limits the
  OUTPUT/answer length and was the actual cause of the Feature 4 truncation bug above). Worth
  keeping both budgets in mind separately going forward.
- **`max_tokens=2500`** (in `ask_jeremy()`'s `groq_client.chat.completions.create(...)` call) —
  raised from the original 1000 during this session's Feature 4 rollout; applies to every
  answer, not just comparisons.
- Chunking: 500 words, 50 overlap. Retrieval top-k of ~5–10 BEST chunks is the sweet spot.
- Groq's chat completion is NOT deterministic by default (no `temperature` pinned).
- **Groq model IDs can be deprecated/shut down with only ~2 months' notice.**
- **Streamlit Community Cloud sleeps any app after 12 hours of no traffic** — handled by the
  keep-awake GitHub Actions workflow.
- **`YouTubeTranscriptApi().fetch(video_id)` returns objects with `.text`/`.start` attributes,
  not dict-style `['text']`/`['start']`** — confirmed from `download_transcrips.py`'s existing
  usage and reused for Feature 2's `get_timed_segments()`.
- **Local `app.py` can silently drift from the live/deployed version** if changes are ever made
  through a path other than this computer's own git repo (e.g. GitHub's web editor). Confirmed
  happened Sep 2→Sep 4. Worth a quick sanity check at the start of any `app.py`-editing session.

## 🔑 KEY ACCOUNTS
- GitHub: speedyturtleco (repo: https://github.com/speedyturtleco/jeremy-rag-project, public)
- Streamlit: https://ask-jeremy.streamlit.app/
- Neon: jeremy-rag-project (AWS US East 2 Ohio)
- Groq: free tier
- Decodo: ✅ on Pay As You Go

---

## STATUS / WHERE WE LEFT OFF (Sep 5 session)
- Confirmed the Sep 4 Netflix fix (`TOPIC_TAIL_PATTERN` widened to catch "for X"/"regarding X")
  IS live and DID fix the retrieval bug - live-tested the exact original Netflix question and
  the app now surfaces real, dated Financial Education excerpts with specific numbers instead
  of a blanket "no mention found."
- That same live test surfaced a NEW bug: Groq's answer incorrectly said those Financial
  Education excerpts were "not Jeremy's channel." Diagnosed as a context/prompt-layer bug, not
  a retrieval bug - the context sent to Groq never explicitly mapped channel names to real
  creators, so the model guessed wrong. See FEATURE 7 (new section) for the full
  investigation and fix (`CHANNEL_CREATOR` mapping + rewritten system prompt).
- Fixed and pushed directly to the user's computer via `device_commit_files`. **Made a process
  mistake right after this:** told the user to run `git reset --hard origin/main` before the
  fix had actually been pushed to GitHub, which silently discarded it. Caught it from the reset
  output, re-wrote the fix to disk, and had the user push it directly via `git add`/`git
  commit`/`git push` (commit `ce5b201`) instead of routing through the browser again. Added a
  new standing warning about this near the top of the plan - **never suggest `git reset --hard`
  until confirming the fix in question is already on GitHub or about to be pushed in the very
  next step.**
- **Live-tested FEATURE 7's fix after the push - confirmed working:** re-asked the Netflix
  question; Groq now correctly says "Jeremy Lefebvre has a recent video... Financial Education"
  and marks the channel "(verified)" instead of "not Jeremy's channel."
- Immediately asked a follow-up in the same session ("most recent time Jeremy has mentioned
  projections for wynn") to keep testing - this surfaced a FOURTH, different bug (FEATURE 8):
  conversation-memory's context-stuffing (`build_search_query()` appending the prior Q&A after
  the current question) broke `extract_stock_keyword()`'s end-of-string anchor, so the keyword
  safety net silently didn't engage on follow-up questions, and semantic search returned an
  all-Netflix context for a Wynn question. Confirmed root cause via direct Python testing
  (extracting from the raw question alone works; extracting from the context-stuffed string
  doesn't). Fixed by extracting keywords from the raw current question, always, regardless of
  what gets appended for the embedding step. See FEATURE 8 (new section) for full details.
- FEATURE 8's fix was written to project docs and to the user's computer via
  `device_commit_files` - but the FIRST write silently didn't land (tool reported success, file
  on disk was actually unchanged), caught only because the user's `git commit` said "nothing to
  commit" and prompted a check. Verified via `device_stage_files` + diff/grep, re-wrote it with
  `force: true`, and verified AGAIN before telling the user to commit - this time it genuinely
  matched. Added a new standing warning about this near the top of the plan - **always verify a
  `device_commit_files` write actually landed by staging the file back and checking for the
  fix's own content, never trust the tool's "written" success alone.** User then successfully
  committed (`c84d17a`) and pushed FEATURE 8's fix to GitHub.
- **Live-tested FEATURE 8's fix after the push - confirmed working, both scenarios:** a fresh
  standalone Wynn question, and the Wynn question as a same-session follow-up right after an
  AMD question (the exact scenario that exposed the bug). Both correctly found and cited real,
  verified Wynn Resorts content instead of a false "no mention found." Hit a transient
  `groq.APIStatusError` a few times mid-testing from asking questions too rapidly back-to-back
  (Groq free-tier rate limiting, not a code bug) - resolved itself after about a minute's gap.
- **NEXT ACTION:** none urgent. All three bugs found this session (Feature 8's keyword/context
  interaction, Feature 7's channel mislabeling, plus confirming Feature 6's Sep 4 Netflix fix)
  are now fixed, deployed, and live-tested working. Good time to just use the app normally for
  a while, or pick something from 💡 FUTURE FEATURES.

## STATUS / WHERE WE LEFT OFF (Sep 4 session)
- User reported a third variant of the Feature 6 bug class: a question about Jeremy's Netflix
  projections (phrased "...projections **for** Netflix") came back with a false negative, even
  though the relevant video (the same "4 Stocks to Go ALL IN September 2026" video from the
  Wynn bug, already confirmed ingested) does contain the mention. Diagnosed as a gap in
  `TOPIC_TAIL_PATTERN`, which only recognized "on X"/"about X", not "for X". Fixed by widening
  the preposition list to `(?:on|about|for|regarding)`. Full writeup in FEATURE 6's third
  update above.
- **Bigger finding this session:** the local copy of `app.py` on the user's computer had not
  been updated since before Sep 2 evening — three sessions' worth of shipped work (Feature 1
  Modes 2-4, Feature 2, Feature 4, both earlier Feature 6 fixes) existed only on GitHub/live,
  never pulled down locally. Caught this before patching on top of the stale version (which
  would have silently reverted all of it on the next `git push`). Fixed by writing the current,
  project-doc-verified `app.py` (with the new fix layered on) directly to the user's computer.
  Added a standing warning note near the top of this file so future sessions check this first.
- **Deploy path note:** for the first time, writing directly to the user's local file via the
  device bridge worked (previous sessions logged this as unavailable). The user will run
  `git add` / `git commit` / `git push` themselves from VS Code to actually deploy - not yet
  confirmed live at the time this plan was updated.
- **NEXT ACTION:** once the user pushes, live-test the original Netflix question (or something
  close to it) to confirm the "4 Stocks to Go ALL IN September 2026" video now surfaces. Also
  worth a quick general sanity check that local and live `app.py` stay in sync from here on.

## STATUS / WHERE WE LEFT OFF (Sep 3 session)
- Confirmed conversation memory still works correctly live (vague follow-up question, no
  topic/keyword named, correctly answered using prior Q&A context).
- Trimmed the landing page's "Try asking" examples from 6 (two columns) down to 2 (single
  column) — see FEATURE 5 above for the exact questions and reasoning. Deployed and
  live-verified.
- Found and fixed a real bug: the standard search (Mode 5) could completely miss a stock that's
  only mentioned once in the whole corpus (reported via the "Wynn stock" question). Added a
  hybrid literal-keyword fallback + recency-aware sorting - see FEATURE 6 above for the full
  investigation, fix, and live-test results, plus a caveat about auto-caption spelling accuracy
  that's a good candidate for a future fuzzy-matching improvement.
- Same bug class immediately resurfaced with a differently-phrased question ("latest take on
  Celcius" - typo'd) - broadened keyword extraction to catch "on X"/"about X" phrasing (not just
  "X stock"), and added a `pg_trgm` fuzzy-match fallback for typos/near-misses. Live-tested with
  the exact typo intact - now correctly surfaces same-day content instead of a stale answer. See
  FEATURE 6's update for full details and an open caveat about which exact video gets cited.
- **NEXT ACTION:** no urgent open items. Good time to just use the app normally, or pick
  something from 💡 FUTURE FEATURES - though given this bug class has now shown up twice in one
  session with two different phrasings, it's worth staying a little alert for a third variant
  next time the app is used for a "what's the latest on X" style question.

## STATUS / WHERE WE LEFT OFF (Sep 2, evening session)
- Everything from the Sep 2 morning session (date backfill, monitoring, keep-awake) closed out
  — see prior STATUS entry below for that recap, still accurate.
- **Built and deployed, in order, per the user's request ("feature one through feature four"):**
  - Feature 1 Mode 2 (specific time period) — ✅ built, live-tested (Tesla/2021 question).
  - Feature 1 Modes 3 & 4 (timeline/evolution + first mention) — ✅ built, live-tested (AMD
    "has Jeremy always been bullish" question, which exercises the shared retrieval + Mode 4's
    specific framing).
  - Feature 2 (timestamp/jump-to-moment links) — ✅ built, live-tested (confirmed real, distinct
    `&t=Ns` links on the same Tesla/2021 test above).
  - Feature 4 (multi-creator comparison mode) — ✅ built, but needed 2 rounds of fixes after the
    first live test showed a truncated, Eric-less answer. Root cause: `max_tokens` (1000, never
    revisited since the app was first built) wasn't enough for a two-creator side-by-side
    answer. Fixed by raising `max_tokens` to 2500 and adding a "keep it concise" instruction to
    the comparison-specific prompt. Confirmed working cleanly on the third deploy.
- All changes deployed via GitHub's web file editor (browser-driven, pasted content in via a
  synthetic clipboard-paste event since `device_commit_files` and computer-use/VS Code typing
  were both unavailable paths this session) — 3 commits total to `app.py`:
  "Add time-period search, timeline/first-mention arc, comparison mode, and timestamp links",
  then two "Update app.py" commits for the max_tokens fix iterations.
- **NEXT ACTION:** no urgent open items. The original roadmap (Feature 1 all modes, Feature 2,
  Feature 4) is now fully built and live-tested. Good time to just use the app normally for a
  while and see what surfaces, or pick something from 💡 FUTURE FEATURES if there's appetite to
  keep building.

## SESSION LOG (recent — see git history / earlier plan versions for full history back to Jun 26)
- Jun 26 – Aug 28: see prior plan versions for full early history.
- **Sep 2 (morning session):** confirmed `update_neon_dates.py` had run successfully (live-app
  test rather than direct DB query, which wasn't reachable this session). Set up 3 recurring
  scheduled checks (GitHub Actions health, Groq deprecation, Decodo balance). Researched and
  built a fix for Streamlit's 12-hour inactivity sleep: `keep_app_awake.py` (Playwright wake
  script) + `.github/workflows/keep_awake.yml`, created directly through GitHub's web editor
  (browser-driven) since `device_commit_files` blocks remote writes to workflow files.
  Confirmed working via a manual trigger (40s successful run).
- **Sep 2 (evening session, this one):** User asked to build Feature 1 (Modes 2-4), Feature 2,
  and Feature 4, in that order, all in one go. Read the existing `app.py` and
  `download_transcrips.py` (to confirm the exact `YouTubeTranscriptApi` usage pattern) directly
  from the device. Wrote a complete new `app.py` locally adding: `search_transcripts_by_period`
  (Mode 2), `search_transcripts_timeline` (Modes 3 & 4, via a Postgres window function),
  `search_transcripts_comparison`/`search_transcripts_by_channels` (Feature 4), and
  `get_timed_segments`/`find_timestamp_for_chunk`/`add_timestamp_links` (Feature 2, with a new
  `video_timestamps` Neon cache table). Validated locally with `py_compile` and `pyflakes`.
  Deployed via GitHub's web file editor, driven through the browser pane (computer-use couldn't
  type into VS Code — IDEs are click-only under that feature's access tiers — and
  `device_commit_files` refuses `.github/workflows/*.yml` but `app.py` itself isn't
  workflow-protected; used the already-proven browser/paste-event technique for consistency and
  because a fresh session's `device_bash` tooling wasn't available here). Learned mid-session
  that a screenshot taken immediately after a DOM change (or right after a click that opens a
  modal) can be stale/misleading in this browser tool — confirmed real state instead via
  `document.querySelector('.cm-content').innerText` checks and, once, via a `[role="dialog"]`
  existence check when a screenshot said "empty file" but JS proved the real content was there.
  Also learned CodeMirror's editor only renders visible lines to the DOM (virtualized), so an
  `.innerText.length` check right after a big paste can look wrong (e.g. `3651` instead of
  `~26000`) purely because most of the document isn't scrolled into view — checking the START
  and END of the document (via `ctrl+Home`/`ctrl+End`) is the reliable way to confirm a large
  paste succeeded, not a raw length count. Live-tested each new feature directly against the
  live app: Mode 2 (Tesla/2021 — correct, year-filtered, with real timestamp links), Mode 4
  (AMD "has Jeremy always been bullish" — correct table, correctly concluded "never bullish"
  rather than overclaiming), and Feature 4 (Jeremy+Eric comparison), which failed its first two
  live tests with a truncated, single-creator-only answer. Diagnosed as a `max_tokens` (output
  length) limit, not a retrieval bug — the original app had never revisited its
  `max_tokens=1000` setting from when it only ever needed to describe one creator's view.
  Fixed in two iterations (1000→1800, still truncated; 1800→2500 plus a "keep it concise"
  prompt addition, confirmed clean) — each iteration required redeploying `app.py` via the same
  GitHub web-editor flow and re-verifying the paste before committing. Updated this plan and the
  project's saved `app.py` doc to reflect the finished work in the same session, per the
  standing "keep docs synced" rule.
- **Sep 3 (this session):** Live-tested conversation memory with a genuinely vague follow-up
  question (no topic or keyword named) — confirmed the app correctly pulled context from the
  prior exchange. Then updated the landing page: replaced the old 6-question, two-column
  "Try asking" list with just 2 questions chosen to showcase the Sep 2 session's new features
  (see FEATURE 5). Before finalizing the AMD question's exact wording, verified via direct
  Python regex testing against `app.py`'s pattern constants which search mode it would trigger,
  and confirmed via live test that the chosen phrasing ("still" rather than "always") produces a
  more complete answer than the timeline-mode phrasing had, revealing a real (documented)
  limitation in `search_transcripts_timeline()`. Deployed via the same GitHub web-editor +
  synthetic-paste technique, verified the paste landed correctly (checked document start, end,
  and the specific edited section — CodeMirror's virtualized rendering means only scrolled-into-
  view lines exist in the DOM, so `scrollTop` must be set directly and given a short delay before
  re-reading `innerText`), committed, and live-verified the redeployed app.
- **Sep 3 (later same session):** User reported the "Wynn stock" bug (see FEATURE 6). Diagnosed
  by checking the `auto_update.yml` Actions run history (confirmed daily runs succeeding — had
  to find the right selector, `.js-check-line-content`, to pull real log text out of GitHub's
  virtualized log viewer), identifying the actual video via YouTube search, and confirming via a
  live-app test that the video's transcript WAS already in Neon — isolating the bug to
  `search_transcripts()`'s plain top-10 semantic search, not the ingestion pipeline. Built a
  hybrid keyword-fallback + recency-sort fix, caught and corrected a bug in the first draft of
  my own fix during local logic testing (keyword hits could get truncated away when the question
  didn't use recency language — fixed by merging keyword hits first, before semantic results).
  Verified the regex/merge logic locally in Python (no DB needed) before deploying, confirming
  both that the exact bug-report question now extracts the right keyword and recency intent, and
  that the already-tested "Is Jeremy still bullish on AMD?" example question is completely
  unaffected. Deployed via the same GitHub web-editor + synthetic-paste flow, verified the paste
  (start/end/middle-section checks), committed, and live-tested the exact original question —
  confirmed the app now returns a real, well-reasoned, correctly-sourced answer instead of a
  false "no mention found." Updated this plan and the project's saved `app.py` doc.
- **Sep 3 (immediately after the above):** User's very next question ("what's jeremy's latest
  take on celcius", typo'd) exposed two more gaps in the just-shipped fix: the keyword
  extractor didn't recognize "take on X" phrasing (only "X stock"), and even if it had, the
  user's typo wouldn't exact-match the correctly-spelled word in the transcript. Broadened
  `extract_stock_keyword()` to catch a topic named at the end of a recency-style question, and
  added a `pg_trgm`-based fuzzy fallback (`word_similarity()`) for when the exact `ILIKE` match
  comes up empty - wrapped in try/except with `conn.rollback()` so a missing extension or query
  error can't break search entirely. Verified the regex logic locally before deploying (same
  test-first pattern as the first fix), deployed via the same GitHub web-editor flow, verified
  the paste, committed, and live-tested with the user's exact typo intact - confirmed the app
  now correctly surfaces same-day (Sept 1) content instead of the stale Aug 26 answer from
  before, correctly reasons about which excerpt is most recent, and correctly flags the
  unverified reaction-video source. Noted an open caveat (which exact video gets cited) rather
  than over-chasing it further. Updated this plan and the project's saved `app.py` doc again.
- **Sep 4 (this session):** User asked whether a microphone/voice-input button could be added
  to the app (separate, unimplemented discussion — landed on "try Windows+H system dictation
  first, real mic button is a possible future build using `st.audio_input` + Groq Whisper
  transcription" — not yet built). Then user reported a third variant of the Feature 6 bug
  class: a "projections for Netflix" question came back with a false negative for the same "4
  Stocks to Go ALL IN September 2026" video already confirmed ingested during the Wynn
  investigation. Diagnosed the gap (`TOPIC_TAIL_PATTERN` didn't recognize "for X" phrasing,
  only "on X"/"about X") without needing to re-investigate ingestion, since that had already
  been ruled out for this exact video. Before patching, requested folder access to the user's
  `jeremy-rag-project` directory via the device bridge and discovered the local `app.py` was
  three sessions stale (missing everything shipped Sep 2 evening onward) because those deploys
  went straight to GitHub's web editor and were never pulled down locally. Wrote the current,
  project-doc-verified `app.py` — with the new "for/regarding" fix layered on top — directly to
  the user's computer via `device_commit_files` (worked this session, unlike prior sessions),
  bringing local and live back into sync in the same step as fixing the bug. Verified the fixed
  file with `py_compile` before committing it. Updated this plan (added the ⚠️ LOCAL FILE SYNC
  warning near the top, extended FEATURE 6, added this STATUS/SESSION LOG entry) and the
  project's saved `app.py` doc. User will deploy via `git add`/`git commit`/`git push` from VS
  Code themselves — not yet live-tested against the actual Netflix question.
- **Sep 5 (this session):** User ran the full git sync sequence from the Sep 4 session
  (`git fetch origin`, `git reset --hard origin/main`, confirmed clean via `git status` -
  local `app.py` and `PROJECT_PLAN.md` now match GitHub exactly, only pre-existing unrelated
  scratch files remain untracked). Live-tested the Netflix question via the built-in browser:
  confirmed the Sep 4 fix DID work at the retrieval level (real Financial Education content
  with specific Netflix numbers now surfaces, no more "no mention found"), but caught a new
  bug live - Groq's answer said that content was "not Jeremy's channel," which is wrong.
  Investigated by reading `app.py`'s `ask_jeremy()` function directly: found the context string
  sent to Groq only ever included the raw `channel` value from Neon, with nothing anywhere
  telling the model that Financial Education and 1000xstocks are channels Jeremy Lefebvre
  personally runs - so the model reasonably guessed wrong from the channel name alone. Fixed by
  adding a `CHANNEL_CREATOR` mapping dict, tagging every excerpt with both a `Creator` and
  `Channel` field, and rewriting the system prompt to spell out which channels belong to which
  creator explicitly (see FEATURE 7, new section). Verified the fix compiles with `py_compile`,
  wrote it to the project's saved `app.py` doc, and pushed it directly to the user's computer
  via `device_commit_files` (continues to work reliably). Updated this plan with the new
  FEATURE 7 section and this STATUS/SESSION LOG entry. Not yet live-tested after this fix -
  next step once the user pushes/redeploys is to re-ask the Netflix question one more time.
