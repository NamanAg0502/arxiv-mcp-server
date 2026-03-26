# Data Source Expansion Spec — "All-Knowing CTO" Mode

## Vision

Transform from **academic research tool** → **full-stack technical intelligence server** that answers:
- "What's the best open-source observability tool right now?" (GitHub + Reddit + HN)
- "Is LangGraph replacing LangChain?" (Reddit sentiment + GitHub stars + HN discussion)
- "What inference frameworks are teams actually using?" (Reddit + HN + GitHub trending)
- "Show me everything about Mamba architecture" (arXiv + Reddit + HN + GitHub + blogs)
- "What did the ML community think of Apple's latest paper?" (X + Reddit + HN)

## Current State (10 sources, 31 tools)

| Source | Type | Coverage |
|--------|------|----------|
| arXiv | Academic | Papers, preprints |
| Semantic Scholar | Academic | Citations, influence |
| OpenAlex | Academic | Cross-ref metadata |
| Crossref | Academic | DOIs, references |
| DBLP | Academic | CS bibliography |
| HuggingFace | ML Ecosystem | Models, datasets, trending |
| Papers With Code | ML Ecosystem | Benchmarks, code repos |
| Epoch AI | ML Ecosystem | Model capabilities |
| Lens.org | Patents | Patent-paper cross-refs |
| Local KB | Storage | Saved papers, annotations |

**Gap:** Zero coverage of practitioner signal — what developers actually discuss, adopt, and build.

---

## Proposed New Sources

### Tier 1 — High Value, Free/Easy APIs

#### 1. **GitHub** (REST + GraphQL API)
- **Why:** Ground truth for OSS adoption — stars, forks, releases, trending
- **Auth:** `GITHUB_TOKEN` (free PAT, 5000 req/hr)
- **Key endpoints:**
  - `/search/repositories` — find repos by topic/language/stars
  - `/repos/{owner}/{repo}` — repo metadata, stats
  - `/repos/{owner}/{repo}/releases` — latest releases
  - Trending: scrape `https://github.com/trending` or use unofficial API
- **Tools:**
  - `github_trending` — trending repos by language/timeframe
  - `github_repo_info` — deep repo analysis (stars, activity, contributors, releases)
  - `github_search` — search repos by query, topic, language
  - `github_releases` — recent releases for a repo/topic
  - `github_compare` — compare 2+ repos (stars, activity, community)

#### 2. **Hacker News** (Firebase API — free, no auth)
- **Why:** Early signal for dev tools. If it's on HN front page, devs are paying attention
- **Base URL:** `https://hacker-news.firebaseio.com/v0`
- **Key endpoints:**
  - `/topstories.json` — current front page
  - `/newstories.json` — newest
  - `/beststories.json` — best all-time
  - `/item/{id}.json` — story + comments
  - Algolia search: `https://hn.algolia.com/api/v1/search?query=X`
- **Tools:**
  - `hn_search` — search HN stories + comments
  - `hn_trending` — current front page tech stories
  - `hn_discussion` — get top comments/sentiment for a story
  - `hn_topic_pulse` — aggregate HN mentions of a topic over time

#### 3. **Reddit** (OAuth2 API)
- **Why:** Where practitioners discuss tools honestly — r/MachineLearning, r/LocalLLaMA, r/programming, r/devops, r/ExperiencedDevs
- **Auth:** `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` (free, create app at reddit.com/prefs/apps)
- **Key endpoints:**
  - `/r/{subreddit}/search` — subreddit search
  - `/r/{subreddit}/hot|top|new` — trending posts
  - `/comments/{article}` — post + comments
  - `/search` — cross-subreddit search
- **Target subreddits:** MachineLearning, LocalLLaMA, programming, devops, ExperiencedDevs, golang, rust, Python, node, nextjs, selfhosted, opensource
- **Tools:**
  - `reddit_search` — search across dev subreddits
  - `reddit_trending` — hot posts from curated subreddits
  - `reddit_discussion` — post + top comments with sentiment
  - `reddit_tool_sentiment` — "What does Reddit think of X?" across subreddits

#### 4. **Dev.to / Forem** (API — free, no auth for reading)
- **Why:** Practitioner tutorials and announcements, more accessible than blog posts
- **Base URL:** `https://dev.to/api`
- **Key endpoints:**
  - `/articles?tag=X` — articles by tag
  - `/articles?top=7` — trending last 7 days
  - `/articles/{id}` — full article
- **Tools:**
  - `devto_search` — search articles by keyword/tag
  - `devto_trending` — trending dev articles

### Tier 2 — High Value, Moderate Effort

#### 5. **X/Twitter** (API v2 — expensive, or use alternatives)
- **Why:** Real-time pulse of ML/AI community. Paper authors, company announcements
- **Problem:** API is $100/mo minimum for basic read. Alternatives:
  - **Nitter** instances (scraping, unreliable)
  - **Social Searcher API** (free tier: 100 req/day)
  - **Apify Twitter Scraper** (pay per use, ~$5/1000 tweets)
  - **SocialData.tools** API (cheaper alternative)
- **Recommendation:** Start with RSS feeds of key accounts + Social Searcher for search
- **Tools:**
  - `x_search` — search recent tweets on a topic
  - `x_key_voices` — what key ML/AI accounts are saying about X

#### 6. **Stack Overflow** (API v2.3 — free, 300 req/day without key, 10k with)
- **Why:** What developers struggle with = what's being adopted
- **Base URL:** `https://api.stackexchange.com/2.3`
- **Auth:** Optional `STACKOVERFLOW_KEY` for higher limits
- **Key endpoints:**
  - `/search/advanced` — advanced search with tag filtering
  - `/questions?tagged=X&sort=activity` — recent questions by tag
  - `/tags/{tag}/info` — tag stats (question count = adoption proxy)
- **Tools:**
  - `so_search` — search questions by topic
  - `so_tag_trends` — tag popularity over time (adoption signal)
  - `so_hot_topics` — trending questions in a technology

#### 7. **Product Hunt** (GraphQL API — free for reading)
- **Why:** Launch announcements for dev tools
- **Auth:** `PRODUCTHUNT_TOKEN` (free developer token)
- **Tools:**
  - `ph_search` — search launches by keyword
  - `ph_trending_devtools` — trending dev tool launches

### Tier 3 — Specialized / Nice-to-Have

#### 8. **npm / PyPI / crates.io** (Package Registries)
- **Why:** Download counts = real adoption data
- **APIs:**
  - npm: `https://registry.npmjs.org/{pkg}` + `https://api.npmjs.org/downloads/point/last-month/{pkg}`
  - PyPI: `https://pypi.org/pypi/{pkg}/json` + BigQuery for downloads
  - crates.io: `https://crates.io/api/v1/crates/{name}`
- **Tools:**
  - `package_stats` — downloads, versions, last updated for any package
  - `package_compare` — compare adoption of competing packages
  - `package_new_releases` — recent releases in a category

#### 9. **Lobsters** (API — free, no auth)
- **Why:** Higher signal-to-noise than HN for dev content
- **Base URL:** `https://lobste.rs`
- **Tools:**
  - `lobsters_search` — search stories
  - `lobsters_trending` — current hottest stories

#### 10. **Technology Radar Sources**
- **ThoughtWorks Tech Radar** — quarterly, scraped/cached
- **CNCF Landscape** — `https://landscape.cncf.io` API for cloud-native tools
- **DB-Engines Ranking** — database popularity
- **Tools:**
  - `tech_radar` — "What's the current consensus on X technology?"

---

## Composite "CTO Intelligence" Tools

These are **meta-tools** that combine multiple sources to answer high-level questions:

### `tech_landscape`
> "Give me the full picture on observability tools in 2026"
- GitHub: search repos by topic, sort by stars
- Reddit: search r/devops, r/sre for discussions
- HN: search for recent discussions
- Package stats: compare downloads
- arXiv: any relevant papers
- **Output:** Structured landscape report with adoption signals

### `tool_evaluation`
> "Should we use Drizzle or Prisma?"
- GitHub: compare repos (stars, issues, PRs, release velocity)
- Reddit: sentiment analysis across threads
- HN: discussion summaries
- SO: question volume trends (adoption proxy)
- Package stats: download trends
- **Output:** Decision matrix with evidence

### `tech_pulse`
> "What's trending in AI infrastructure this week?"
- GitHub: trending repos in ML/AI
- HN: front page tech stories
- Reddit: hot posts from curated subreddits
- Dev.to: trending articles
- HuggingFace: trending papers/models
- **Output:** Weekly briefing

### `community_sentiment`
> "What does the dev community think about Bun?"
- Reddit: aggregate threads with sentiment
- HN: aggregate discussions with sentiment
- Dev.to: recent articles
- GitHub: issue velocity, star trajectory
- **Output:** Sentiment report with direct quotes

### `deep_research`
> "Give me everything about WebTransport for real-time applications"
- arXiv: academic papers
- Semantic Scholar: citation graph
- GitHub: implementations and examples
- HN + Reddit: practitioner discussions
- SO: common questions and solutions
- Dev.to: tutorials
- **Output:** Comprehensive research report with academic + practitioner perspectives

---

## Architecture

### New Client Structure
```
src/research_mcp_server/clients/
├── github_client.py      # GitHub REST API
├── hn_client.py           # Hacker News Firebase + Algolia
├── reddit_client.py       # Reddit OAuth2
├── devto_client.py        # Dev.to API
├── so_client.py           # Stack Overflow API
├── ph_client.py           # Product Hunt GraphQL
├── package_client.py      # npm + PyPI + crates.io unified
├── lobsters_client.py     # Lobsters API
└── x_client.py            # X/Twitter (via Social Searcher or direct)
```

### New Tool Structure
```
src/research_mcp_server/tools/
├── github_tools.py        # GitHub search, trending, compare
├── hn_tools.py            # HN search, trending, discussion
├── reddit_tools.py        # Reddit search, trending, sentiment
├── devto_tools.py         # Dev.to search, trending
├── so_tools.py            # Stack Overflow search, trends
├── community_tools.py     # Composite: sentiment, pulse, landscape
├── package_tools.py       # Package registry stats
└── evaluation_tools.py    # Composite: tool_evaluation, deep_research
```

### New Environment Variables
```env
# Tier 1 (recommended)
GITHUB_TOKEN=ghp_...              # GitHub PAT (free)
REDDIT_CLIENT_ID=...              # Reddit app ID (free)
REDDIT_CLIENT_SECRET=...          # Reddit app secret (free)

# Tier 2 (optional)
STACKOVERFLOW_KEY=...             # SO API key (free, higher limits)
PRODUCTHUNT_TOKEN=...             # PH developer token (free)
X_API_BEARER=...                  # Twitter API (paid)

# No auth needed
# Hacker News, Dev.to, Lobsters, npm, PyPI, crates.io
```

### New Dependencies
```toml
# None required — all APIs are HTTP-based, already have httpx
# Optional: praw (Reddit SDK) — but raw httpx is simpler
```

---

## Implementation Priority

### Phase 1 — Highest Signal, Zero Auth
1. **Hacker News** client + tools (free, no auth, high signal)
2. **Dev.to** client + tools (free, no auth)
3. **Lobsters** client + tools (free, no auth)
4. **Package registries** client + tools (free, no auth)

### Phase 2 — High Signal, Free Auth
5. **GitHub** client + tools (free PAT)
6. **Reddit** client + tools (free app registration)
7. **Stack Overflow** client + tools (free key)

### Phase 3 — Composite Intelligence
8. `tech_pulse` meta-tool
9. `tool_evaluation` meta-tool
10. `community_sentiment` meta-tool
11. `tech_landscape` meta-tool
12. `deep_research` meta-tool

### Phase 4 — Premium Sources
13. **X/Twitter** (evaluate cost vs value)
14. **Product Hunt** (if dev tool discovery is valuable)
15. **Tech Radar** sources (CNCF, ThoughtWorks)

---

## Estimated Tool Count After Expansion

| Category | Current | New | Total |
|----------|---------|-----|-------|
| Academic & Papers | 15 | 0 | 15 |
| ML Ecosystem | 6 | 0 | 6 |
| Patents | 1 | 0 | 1 |
| Knowledge Base | 5 | 0 | 5 |
| Research Meta | 4 | 0 | 4 |
| **GitHub** | 0 | 5 | 5 |
| **Hacker News** | 0 | 4 | 4 |
| **Reddit** | 0 | 4 | 4 |
| **Dev.to** | 0 | 2 | 2 |
| **Stack Overflow** | 0 | 3 | 3 |
| **Package Registries** | 0 | 3 | 3 |
| **Lobsters** | 0 | 2 | 2 |
| **Composite CTO** | 0 | 5 | 5 |
| **Total** | **31** | **28** | **~59** |

---

## Open Questions

1. **Tool explosion problem:** 59 tools is a lot for MCP. Should we consolidate into fewer, smarter tools that route internally? (e.g., single `community_search` that queries HN + Reddit + Dev.to)
2. **Rate limiting coordination:** Multiple sources queried in parallel for composite tools — need orchestrated rate limiting
3. **Caching strategy:** Community content changes fast — what's the TTL? (suggest: 15min for trending, 1hr for search, 24hr for stats)
4. **Sentiment analysis:** Do we use the LLM (expensive per call) or a lightweight local model (TextBlob/VADER)?
5. **Response size:** Composite tools will return a LOT of data. Need aggressive summarization or pagination.
6. **Naming convention:** Current tools use `arxiv_` prefix. New tools should use a consistent prefix strategy — or drop prefixes for a unified namespace.
