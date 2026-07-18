# Jay Marketplace Architecture Diagram

## Overview

Jay Marketplace is a Claude Code plugin marketplace that provides installable AI-agent skill kits. It follows a plugin-based architecture where each kit contains one or more skills that can be installed globally (user scope) or per-repository (project scope).

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code / Codex                          │
│                      (Plugin Host)                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Plugin Installation
                          │ (User/Project/Local scope)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              .claude-plugin/marketplace.json                     │
│  - Lists all 3 plugins (kits)                                    │
│  - Plugin metadata: name, source, description, category, keywords│
│  - Owner info: Jay Ozer (jayozer@gmail.com)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│agent-workflow-  │ │yt-automation-   │ │video-understand-│
│     kit        │ │     kit         │ │    ing-kit      │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│goal-orchestrator│ │5 Skills:         │ │video-understand-│
│                 │ │- yt-search       │ │    ing          │
└─────────────────┘ │- yt              │ └─────────────────┘
                    │- seo             │
                    │- thumbnail       │
                    │- repurpose       │
                    └─────────────────┘
```

## Plugin Structure

Each plugin (kit) follows this structure:

```
<kit>/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (name, version, metadata)
├── README.md                    # Kit documentation
├── requirements-dev.txt         # Dev dependencies (optional)
├── scripts/                     # Helper scripts (optional)
│   └── validate_skills.py       # Skill validation
└── skills/                      # Auto-discovered skills
    └── <skill-name>/
        ├── SKILL.md             # Skill definition (frontmatter + instructions)
        ├── requirements.txt     # Python dependencies (optional)
        └── <helper scripts>     # Referenced via ${CLAUDE_SKILL_DIR}
```

## Skill Architecture

### 1. Goal Orchestrator (agent-workflow-kit)

**Purpose:** Turn broad tasks into verifiable `/goal` commands for autonomous execution

**Workflow:**
```
User Request → Fill Brief → Is /goal-shaped? → Write Completion Condition
                                              │
                                              ├── Yes → Launch /goal → Autonomous Loop
                                              │                │
                                              │                └── Checker Model (Haiku)
                                              │                    │
                                              │                    └── Met/Not-Met → Continue/Stop
                                              │
                                              └── No → Supervised Orchestration
                                                        │
                                                        └── Parallel Subagents (Task tool)
```

**Key Components:**
- **Brief Template:** Universal form for capturing task requirements
- **Completion Condition:** 4-part structure (measurable end state, verification method, constraints, hard cap)
- **Guardrails:** Trusted workspace, auto-approve tools, fence danger, turn cap
- **Fallback:** Supervised multi-agent orchestration with parallel subagents

**Enhanced Features:**
- **Example Templates:** Pre-built goal templates (feature-build, bug-fix, test-suite, documentation, refactor)
- **Brief Templates:** Domain-specific templates (web-development, api-development, data-pipeline, ML)
- **Subgoal Patterns:** Common decomposition patterns (layered-architecture, feature-by-feature, test-driven, research-then-build)
- **Helper Scripts:** `extract_goal.py`, `benchmark_goals.py`, `generate_brief.py`
- **Enhanced Validation:** Content structure validation, broken link detection, required sections checking
- **Deep Documentation:** `GUIDE.md` with goal writing patterns, troubleshooting, token optimization

**Platform Adaptation:**
- Claude Code: Uses `Task`/Agent tool, `TodoWrite`, `Skill` tool, native `/goal` command
- Codex: Uses `spawn_agent`/`wait_agent`, `update_plan`, native skill loading, supervised orchestration only

### 2. Video Understanding (video-understanding-kit)

**Purpose:** Analyze local video files with Gemini multimodal models

**Workflow:**
```
Video File → Validate Setup (GEMINI_API_KEY, deps) → Choose Mode
                                                    │
                                                    ├── quick: Brief summaries
                                                    ├── standard: Timeline with evidence
                                                    └── deep: Detailed inspection (high thinking)
                                                        │
                                                        ▼
                                            Run analyze_video_gemini.py
                                                        │
                                                        ├── Upload to Gemini Files API
                                                        ├── Wait for processing
                                                        ├── Ask Gemini model (default: gemini-3.1-pro-preview)
                                                        ├── Delete upload (default)
                                                        └── Write artifacts:
                                                            ├── analysis.md (human-readable)
                                                            └── analysis.json (structured)
```

**Key Components:**
- **Helper Script:** `analyze_video_gemini.py` handles upload, processing, analysis
- **Modes:** quick/standard/deep with different prompt strategies
- **Artifacts:** Saved to `~/video-understanding/<YYYY-MM-DD>-<slug>/`
- **Supported Formats:** mp4, mpeg, quicktime, avi, flv, mpg, webm, wmv, 3gpp

### 3. YouTube Automation Kit (yt-automation-kit)

**Purpose:** End-to-end YouTube video creation pipeline

#### Skill: yt-search

**Purpose:** Research YouTube videos by keywords for content planning

**Workflow:**
```
Keywords → search_youtube.py (yt-dlp) → Filter by days → Sort by views
                                                    │
                                                    ├── Save: ~/yt-research/<date>-<keywords>.md
                                                    ├── Save: ~/yt-research/<date>-<keywords>.json
                                                    └── Download thumbnails to ~/yt-research/<date>-<keywords>-thumbnails/
                                                        │
                                                        ▼
                                            Analysis:
                                            ├── Thumbnail patterns (face/no face, colors, style)
                                            ├── Performance overview (views, likes, comments)
                                            ├── Content patterns (formats, durations, channels)
                                            ├── Title patterns (keywords, formulas)
                                            └── Opportunities (gaps, video ideas)
```

**Output:** Markdown report + JSON with video metadata, thumbnails, analysis

#### Skill: yt (Video Planning)

**Purpose:** Plan YouTube video from reference transcript

**Workflow:**
```
Transcript → Check Video Ideas Tracker (~/youtube/video-ideas.md)
            │
            ├── Duplicate check → Use existing idea context
            ├── Related ideas → Reference for angles
            └── No match → Continue
                    │
                    ▼
        Analyze Source Transcript:
        ├── Structure breakdown (segments, timestamps)
        ├── What works well (hooks, pacing, techniques)
        ├── Weaknesses/gaps (opportunities)
        └── Target audience
                    │
                    ├── Download reference thumbnail (yt-dlp)
                    └── Analyze thumbnail → Save thumbnail.md
                            │
                            ▼
                Web Research (4-6 searches):
                ├── Tool/topic overview
                ├── Competitor landscape
                ├── Existing YouTube content
                ├── Content gaps
                ├── Community sentiment
                └── Recent news
                        │
                        ▼
                Interactive Q&A:
                ├── What's your angle?
                ├── What examples/demos?
                ├── Target audience?
                ├── Include/avoid anything?
                        │
                        ▼
                Generate Video Package (~/youtube/<slug>/):
                ├── titles.md (5 options < 70 chars)
                ├── hooks.md (3 hooks, word-for-word scripts)
                ├── description.md (summary, chapters, tags)
                ├── script.md (full script with [SHOW:] markers)
                ├── analysis.md (transcript analysis + research + sources)
                ├── filming-guide.md (step-by-step recording playbook)
                └── thumbnail.md (reference thumbnail analysis)
                        │
                        ▼
                Generate Thumbnails:
                ├── Read thumbnail.md for style guidance
                ├── Craft 2-3 prompts (reference-informed)
                └── generate_thumbnail.py (Kie.ai APIs)
                        │
                        └── Save to ~/youtube/thumbnails/<date>-<slug>/
```

**Output:** Complete video package with titles, hooks, script, filming guide, thumbnails

#### Skill: seo

**Purpose:** Optimize YouTube titles, descriptions, and tags

**Workflow:**
```
Input (topic or ~/youtube/<slug>/) → Gather Context
                                    │
                                    ├── If video package: Read titles.md, script.md, description.md, analysis.md
                                    ├── If topic string: Use directly
                                    └── Extract: core topic, existing titles, key points
                                            │
                                            ▼
                                Competitive Research:
                                ├── Check existing research from /yt (analysis.md)
                                ├── Fill SEO-specific gaps (2-3 searches):
                                │   ├── YouTube autocomplete suggestions
                                │   ├── Title patterns
                                │   ├── Related keywords
                                │   └── Trending angles
                                └── If no analysis.md: Run full 5-6 searches
                                        │
                                        ▼
                            Generate SEO Content:
                            ├── 5 Title Options (< 70 chars each)
                            │   ├── Character count
                            │   ├── CTR formula used
                            │   ├── Primary keyword
                            │   └── Why it works
                            ├── Title Scorecard (1-5 scale):
                            │   ├── Curiosity
                            │   ├── Specificity
                            │   ├── SEO Strength
                            │   └── Click Factor
                            ├── Optimized Description:
                            │   ├── First 2 lines (search preview)
                            │   ├── Body (2-3% keyword density)
                            │   ├── Chapters section
                            │   └── Tags line
                            ├── Tags (15-20):
                            │   ├── Exact match (3-5)
                            │   ├── Broad match (5-7)
                            │   └── Long-tail (5-8)
                            └── Social Media Titles (if --social):
                                ├── LinkedIn headline (< 150 chars)
                                ├── TikTok/Reels caption (< 100 chars)
                                └── Twitter/X post (< 280 chars)
```

**Output:** Updates `titles.md` and `description.md` with SEO sections, or standalone `seo.md`

#### Skill: thumbnail

**Purpose:** Generate YouTube thumbnails using Kie.ai image APIs

**Workflow:**
```
Video Title/Concept → Choose Model:
                     │
                     ├── Nano Banana 2 (latest, 14 ref images, Google Search, ~$0.09)
                     ├── Nano Banana Pro (8 ref images, ~$0.09)
                     └── Seedream 4.5 (text-only, fast, ~$0.025)
                             │
                             ▼
                         Determine Mode:
                         │
                         ├── Text-to-image (all models)
                         └── Remix (image + prompt, Nano Banana 2/Pro only)
                                 │
                                 ▼
                             Collect Settings:
                             ├── Aspect ratio (16:9 recommended for YT)
                             ├── Resolution (1K/2K/4K)
                             ├── Number of variants (default: 3)
                             ├── Output format (png/jpg)
                             └── Google Search grounding (Nano Banana 2 only)
                                     │
                                     ▼
                                 Remix Mode Only:
                                 └── Collect Reference Images (up to 14 for NB2, 8 for Pro)
                                         │
                                         ▼
                                     Craft Prompt:
                                     ├── Visual composition
                                     ├── Color palette/mood
                                     ├── Key visual elements
                                     ├── Style direction
                                     └── Lighting
                                             │
                                             ▼
                                         Generate:
                                         └── generate_thumbnail.py
                                             ├── Upload to Kie.ai
                                             ├── Generate images
                                             └── Save to ~/youtube/thumbnails/<date>-<slug>/
```

**Output:** Thumbnail images saved to `~/youtube/thumbnails/<date>-<slug>/` with metadata.json

#### Skill: repurpose

**Purpose:** Repurpose video content into short-form scripts and social posts

**Workflow:**
```
Input (transcript/script/YouTube URL) → Get Source Content
                                        │
                                        ├── Transcript path: Read directly
                                        ├── Script path: Read directly
                                        ├── YouTube URL: Call /transcribe skill first
                                        └── Also read titles.md, description.md if available
                                                │
                                                ▼
                                    Identify Top 5 Moments:
                                    ├── Quotable insights
                                    ├── Surprising facts/stats
                                    ├── Practical tips
                                    ├── Strong opinions
                                    └── Before/after transformations
                                            │
                                            ▼
                                        Ask Platform Preferences:
                                        ├── YouTube Shorts
                                        ├── YouTube Community post
                                        ├── LinkedIn
                                        ├── Twitter/X
                                        └── Instagram/TikTok captions
                                                │
                                                ▼
                                            Generate Content (~/youtube/<slug>/repurposed/):
                                            │
                                            ├── repurposed-shorts.md (3-5 scripts)
                                            │   ├── Title
                                            │   ├── Source timestamp
                                            │   ├── Hook (first 3 seconds)
                                            │   ├── Script (30-60 seconds)
                                            │   ├── Text overlay suggestions
                                            │   └── Suggested format
                                            │
                                            ├── community-post.md (2-3 options)
                                            │   ├── Opening hook
                                            │   ├── Body (2-4 sentences)
                                            │   ├── Video link
                                            │   └── Question/poll
                                            │
                                            ├── linkedin.md (2-3 drafts)
                                            │   ├── Opening hook
                                            │   ├── Body (500-1500 chars)
                                            │   ├── Closing
                                            │   └── Source moment
                                            │
                                            ├── tweets.md (5-7 options)
                                            │   ├── Tweet text (< 280 chars)
                                            │   ├── Source moment
                                            │   └── Thread option
                                            │
                                            └── captions.md (2-3 options)
                                                ├── Hook line
                                                ├── Caption body
                                                ├── Hashtags (exact 5)
                                                └── Source moment
```

**Output:** Multiple content files in `~/youtube/<slug>/repurposed/`

## YouTube Automation Pipeline

The 5 skills work together in a weekly content pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Weekly Content Pipeline                       │
└─────────────────────────────────────────────────────────────────┘

Step 1: /yt-search
├─ Search YouTube by keywords
├─ Download thumbnails
├─ Analyze patterns (thumbnails, titles, content)
└─ Output: ~/yt-research/<date>-<keywords>.md + .json + thumbnails/

Step 2: /transcribe (external skill)
├─ Get transcripts from top video URLs
└─ Output: ~/scripts/transcript_*.txt

Step 3: /yt
├─ Read transcript + research from Step 1
├─ Analyze source video structure
├─ Web research (4-6 searches)
├─ Interactive Q&A for angle
├─ Generate video package:
│  ├─ titles.md
│  ├─ hooks.md
│  ├─ description.md
│  ├─ script.md
│  ├─ analysis.md
│  ├─ filming-guide.md
│  └─ thumbnail.md
└─ Generate thumbnails (Kie.ai)
   └─ Output: ~/youtube/<slug>/ + ~/youtube/thumbnails/<date>-<slug>/

Step 4: /seo
├─ Read video package from Step 3
├─ Competitive research (2-3 searches, reuses /yt research)
├─ Generate SEO-optimized titles (5 options)
├─ Title scorecard (curiosity, specificity, SEO, click factor)
├─ Optimized description
├─ Tags (exact, broad, long-tail)
└─ Social media titles (optional)
   └─ Output: Update titles.md, description.md

Step 5: /repurpose
├─ Read script from Step 3
├─ Identify top 5 moments
├─ Generate platform-specific content:
│  ├─ repurposed-shorts.md (3-5 scripts)
│  ├─ community-post.md (2-3 options)
│  ├─ linkedin.md (2-3 drafts)
│  ├─ tweets.md (5-7 options)
│  └─ captions.md (2-3 options)
└─ Output: ~/youtube/<slug>/repurposed/
```

## Data Flow

### Input Sources
- **User arguments:** Command-line arguments passed to skills
- **Environment variables:** API keys (GEMINI_API_KEY, KIE_API_KEY)
- **Files:** Transcripts, scripts, video packages, research reports
- **Web:** YouTube search results, competitive research, web content

### Output Locations
- **Video packages:** `~/youtube/<slug>/`
- **Research reports:** `~/yt-research/<date>-<keywords>.md`
- **Thumbnails:** `~/youtube/thumbnails/<date>-<slug>/`
- **Video analysis:** `~/video-understanding/<YYYY-MM-DD>-<slug>/`
- **Repurposed content:** `~/youtube/<slug>/repurposed/`

### External APIs
- **Gemini API:** Video analysis (video-understanding skill)
- **Kie.ai APIs:** Thumbnail generation (thumbnail skill)
- **YouTube (via yt-dlp):** Video search, metadata, thumbnails (yt-search skill)
- **Web search:** Competitive research (yt, seo skills)

## Installation Scopes

Plugins can be installed at three scopes:

1. **User scope:** Available in every project on the machine (good for general tools like agent-workflow-kit)
   - Location: `~/.claude/skills/`
   
2. **Project scope:** Recorded in repo's `.claude/settings.json`, committed to git
   - Teammates prompted to install when they trust the workspace
   
3. **Local scope:** Recorded in `.claude/settings.local.json` (gitignored)
   - Personal, repo-scoped choice not shared with team

## Key Design Patterns

### 1. Auto-Discovery
- Skills are auto-discovered from `skills/<name>/SKILL.md`
- No need to list skills in plugin.json
- Drop a new SKILL.md and it ships on next update

### 2. ${CLAUDE_SKILL_DIR} Variable
- Bundled scripts referenced via `${CLAUDE_SKILL_DIR}`
- Resolves correctly for personal, project, and plugin installs
- Same SKILL.md works under marketplace install and manual copy

### 3. Frontmatter-Driven Skills
- Each SKILL.md has YAML frontmatter:
  - `name`: Skill identifier
  - `description`: When to trigger the skill
  - `argument-hint`: Expected arguments
  - `allowed-tools`: Tools the skill can use
  - `user-invocable`: Whether users can call it directly

### 4. Artifact-Based Workflow
- Skills save structured artifacts (JSON, Markdown) for follow-up
- Reuse existing artifacts instead of re-running expensive operations
- Enables incremental workflows and iteration

### 5. Platform Adaptation
- Skills written for Claude Code can adapt to Codex
- Tool name translation table in skill docs
- Harness-specific behavior branches

## Dependencies

### Python Dependencies
- **agent-workflow-kit:** None (pure orchestration)
- **video-understanding-kit:** `google-genai` (Gemini API)
- **yt-automation-kit:** `yt-dlp` (YouTube), Kie.ai SDK (thumbnails)

### System Dependencies
- **yt-dlp:** YouTube video/metadata download
- **Python 3:** Required for all helper scripts

### API Keys
- **GEMINI_API_KEY:** For video-understanding skill
- **KIE_API_KEY:** For thumbnail generation skill

## Validation

Each kit can include validation scripts:
- `scripts/validate_skills.py` - Validates skill frontmatter locally
- Run via: `claude plugin validate .` (marketplace) or `claude plugin validate ./<kit>` (individual plugin)

## Summary

Jay Marketplace is a well-structured plugin system that:
- Provides modular, installable AI agent skills
- Uses auto-discovery for easy skill addition
- Supports multiple installation scopes (user/project/local)
- Follows consistent patterns across all kits
- Enables complex workflows through skill composition
- Integrates with external APIs (Gemini, Kie.ai, YouTube)
- Produces structured artifacts for follow-up work
- Adapts to different platforms (Claude Code, Codex)
