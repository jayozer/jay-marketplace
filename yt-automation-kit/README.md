# 🎬 The YouTube Automation Kit
**5 Claude Code skills that run my AI YouTube pipeline — research → title → script → thumbnail → repurpose.**
From Tyler · The AI Agency · tylerai.dev

> ⚠️ These are **Claude Code skills** — they run in **Claude Code** (terminal, VS Code, JetBrains, or the Desktop app). They do **not** run in claude.ai web, the mobile apps, or Cowork. New to Claude Code? The included `BLUEPRINT.md` has copy-paste prompts that work in **any** AI.

---

## ✅ Before you start — what you'll need
- **Claude Code** — the app the skills run in → https://claude.com/claude-code
- **Python 3** — the skills are Python scripts. Check with: `python3 --version`
  - **Mac:** usually present, or macOS offers to install it the first time you run `python3` — or get it from https://python.org / `brew install python`
  - **Windows:** install from https://python.org (tick **"Add Python to PATH"**)
- **yt-dlp** — for `yt-search` + `yt`: run `pip install yt-dlp`
- **A Kie.ai API key** — **only** for `thumbnail` (skip it if you don't want AI thumbnails) → https://kie.ai

That's it — **Claude Code provides the AI itself**, so there's no OpenAI/Anthropic key to add.

---

## 📂 What's in here
- `BLUEPRINT.md` — the full system + copy-paste prompts (read this first; works in any AI)
- `skills/yt-search` — research trending videos & titles in your niche
- `skills/seo` — optimize titles, descriptions & tags from competitive research
- `skills/yt` — plan a full video (titles, hooks, script, filming guide)
- `skills/thumbnail` — generate thumbnails with AI *(needs the Kie.ai key)*
- `skills/repurpose` — one video → Shorts/TikTok/Reels + posts

## 🔧 Install (about 2 minutes)
1. Find or create your skills folder: **`~/.claude/skills/`**
2. Copy each folder from **`skills/`** into it → so you have `~/.claude/skills/yt-search/`, `~/.claude/skills/seo/`, etc.
3. **For `thumbnail` only** — add your key. Create or edit **`~/.claude/.env`** and add:
   ```
   KIE_API_KEY=your_kie_key_here
   ```
4. Start (or restart) **Claude Code** — it picks up the new skills automatically.

## ▶️ How to use them
In Claude Code, just ask in plain English (it triggers the right skill):
- *"search youtube for [topic]"* → **yt-search**
- *"optimize this title for youtube"* → **seo**
- *"plan a youtube video about [topic]"* → **yt**
- *"make a thumbnail for [topic]"* → **thumbnail**
- *"repurpose this video into shorts"* → **repurpose**

## 🤝 Stuck? Want it done WITH you?
Setup takes a few minutes, and the real power is **chaining these + building your own.**
👉 **Join The AI Agency (free):** https://www.skool.com/the-ai-agency
Inside **Pro**, I'll get these running with you live on the weekly build call — and we build your own.

— Tyler
