# Research MCP Server v2 — Consolidated Architecture

## Design Principles (from Anthropic's Multi-Agent Research System)

1. **Fewer, smarter tools** — Tool count directly impacts agent performance. Each tool must earn its slot.
2. **Tool descriptions are the API** — Invest in descriptions, not tool proliferation.
3. **Orchestrator-worker pattern** — Composite tools spawn parallel sub-queries internally, not by multiplying MCP tools.
4. **Graceful degradation** — Every source is optional. Missing API key = skip, not crash.

---

## Tool Consolidation: 31 → 18 existing tools

### Merges

| Current Tools | → Consolidated Tool | Rationale |
|--------------|---------------------|-----------|
| `search_papers` + `arxiv_advanced_query` | **`search`** | Same backend (`_raw_arxiv_search`), advanced_query just adds field params. Merge into one tool with optional structured fields. |
| `kb_save` + `kb_search` + `kb_list` + `kb_annotate` + `kb_remove` | **`kb`** | Classic CRUD on same storage. Single tool with `action` param. Already proven pattern (see `research_context` which uses actions). |
| `research_context` + `research_memory` | **`memory`** | research_context is session-scoped subset of research_memory. Unify with persistence mode flag. |
| `arxiv_citation_graph` + `arxiv_citation_context` | **`citations`** | citation_context calls citation_graph internally anyway. Add `analysis: bool` param to citation_graph. |

### Renames (clarity + drop `arxiv_` prefix since we're multi-source now)

| Current Name | → New Name | Why |
|-------------|-----------|-----|
| `arxiv_semantic_search` | `semantic_search` | Not arxiv-specific anymore |
| `arxiv_compare_papers` | `compare` | Shorter, clearer |
| `arxiv_trend_analysis` | `trends` | Shorter |
| `arxiv_research_digest` | `digest` | Shorter |
| `arxiv_research_lineage` | `lineage` | Shorter |
| `arxiv_export` | `export` | Shorter |
| `multi_search` | `cross_search` | Distinguishes from `search` (single-source) |
| `papers_with_code_search` | `benchmarks` | What users actually want from PWC |
| `hf_trending_papers` | `hf_trending` | Already close |
| `suggest_tools` | `help` | More intuitive |

### Keep As-Is
- `download_paper` — clear, distinct purpose
- `list_papers` — simple, necessary
- `read_paper` — core functionality
- `read_paper_chunks` — distinct from read_paper (structured sections)
- `kg_query` — unique graph query capability
- `model_benchmarks` — Epoch AI, distinct
- `venue_lookup` — DBLP, distinct
- `patent_search` — Lens.org, distinct

### Resulting Existing Tool Set (18 tools)

```
SEARCH & DISCOVERY
  search          — Keyword + structured field search on arXiv
  semantic_search — Embedding-based similarity search
  cross_search    — Parallel search across arXiv, OpenAlex, Crossref

PAPER MANAGEMENT
  download_paper  — Download PDF, convert to markdown
  list_papers     — List downloaded papers
  read_paper      — Read full paper content
  read_paper_chunks — Read paper by sections

ANALYSIS
  citations       — Citation graph + structural analysis (raw or analyzed)
  lineage         — Intellectual influence DAG (depth 3)
  compare         — Side-by-side paper comparison
  trends          — Publication trend analysis
  digest          — Research area summaries

KNOWLEDGE & MEMORY
  kb              — Save/search/list/annotate/remove papers (action param)
  kg_query        — Knowledge graph queries
  memory          — Persistent research memory + session tracking

EXTERNAL SOURCES
  hf_trending     — HuggingFace trending papers/models
  benchmarks      — Papers With Code + SOTA tables
  model_benchmarks — Epoch AI model capabilities
  venue_lookup    — DBLP conference/journal search
  patent_search   — Lens.org patent cross-reference
  export          — BibTeX/markdown/JSON export
  help            — Tool recommendation engine
```

---

## New Sources & Tools: +10 tools → 28 total

### Source Layer: New Clients

```
src/research_mcp_server/clients/
├── (existing 9 clients)
├── github_client.py       # GitHub REST API — repos, trending, releases
├── hn_client.py            # Hacker News Algolia API — stories, comments
├── reddit_client.py        # Reddit OAuth2 — posts, comments, subreddits
├── devto_client.py         # Dev.to API — articles by tag/trending
├── so_client.py            # Stack Overflow API — questions, tag trends
├── package_client.py       # npm + PyPI + crates.io — unified registry
├── web_client.py           # Lightpanda headless browser — arbitrary web scraping
└── sentiment_client.py     # LLM-based sentiment analysis (Haiku for cost)
```

### New Individual Source Tools (+6)

| Tool | Source | What it does |
|------|--------|-------------|
| **`github`** | GitHub API | Search repos, get repo stats, compare repos, recent releases, trending. Single tool with `action` param: `search\|repo\|compare\|trending\|releases` |
| **`hn`** | Hacker News Algolia | Search stories/comments, get trending, get discussion threads. `action`: `search\|trending\|discussion` |
| **`reddit`** | Reddit API | Search dev subreddits, trending posts, discussion threads. `action`: `search\|trending\|discussion` |
| **`community`** | Dev.to + Lobsters | Search articles, trending posts. `action`: `search\|trending`, `source`: `devto\|lobsters\|both` |
| **`packages`** | npm + PyPI + crates.io | Package stats, compare packages, new releases. `action`: `stats\|compare\|releases` |
| **`web`** | Lightpanda | Scrape any URL, extract structured content. For sources without APIs (X/Twitter, blogs, tech radar sites). |

### New Composite "CTO Intelligence" Tools (+4)

These are the **orchestrator-worker pattern** from Anthropic's research system — each tool spawns parallel sub-queries across multiple sources internally.

| Tool | What it answers | Sources queried |
|------|----------------|-----------------|
| **`tech_pulse`** | "What's trending in AI/ML/dev this week?" | HN trending + Reddit hot + GitHub trending + HF trending + Dev.to trending. Returns unified briefing. |
| **`evaluate`** | "Should we use Drizzle or Prisma?" | GitHub compare + Reddit sentiment + HN discussions + SO tag trends + package download stats. Returns decision matrix. |
| **`sentiment`** | "What does the community think about X?" | Reddit threads + HN discussions + Dev.to articles. LLM-analyzed sentiment with direct quotes. |
| **`deep_research`** | "Everything about WebTransport" | arXiv papers + citations + GitHub repos + Reddit + HN + SO + Dev.to. Full multi-perspective report. |

### Final Tool Inventory (28 tools)

```
SEARCH & DISCOVERY (3)
  search, semantic_search, cross_search

PAPER MANAGEMENT (4)
  download_paper, list_papers, read_paper, read_paper_chunks

ANALYSIS (5)
  citations, lineage, compare, trends, digest

KNOWLEDGE & MEMORY (3)
  kb, kg_query, memory

ACADEMIC SOURCES (4)
  hf_trending, benchmarks, model_benchmarks, venue_lookup, patent_search, export

PRACTITIONER SOURCES (6)
  github, hn, reddit, community, packages, web

CTO INTELLIGENCE (4)
  tech_pulse, evaluate, sentiment, deep_research

META (1)
  help
```

**31 → 28 tools** (consolidated 13, added 10, net -3), but with **dramatically more coverage**.

---

## Lightpanda Integration

### Why Lightpanda over Playwright/Puppeteer
- 11x faster, 9x less memory — critical for MCP server running on local machine
- No Chromium dependency — lighter install
- CDP-compatible — can use Playwright API if needed later
- robots.txt compliance built-in (`--obey_robots`)

### `web` Tool Design

```python
web_tool = types.Tool(
    name="web",
    description="""Fetch and extract structured content from any URL using a headless browser.
    Handles JavaScript-rendered pages. Use for sources without APIs:
    - Tech blogs, company engineering blogs
    - X/Twitter profiles and threads (via nitter or direct)
    - Conference talk pages
    - Tech radar sites (ThoughtWorks, CNCF)
    - Any URL the other tools can't reach""",
    inputSchema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to fetch"},
            "extract": {
                "type": "string",
                "enum": ["article", "comments", "links", "structured", "raw"],
                "description": "Extraction mode",
                "default": "article"
            },
            "selector": {
                "type": "string",
                "description": "Optional CSS selector to target specific content"
            },
            "wait_for": {
                "type": "string",
                "description": "Optional CSS selector to wait for before extracting (JS-rendered content)"
            }
        },
        "required": ["url"]
    }
)
```

### Lightpanda Setup
```toml
# pyproject.toml — no Python dependency needed
# Lightpanda runs as external binary, communicate via CDP (websocket)

# Optional dependency for CDP communication:
[project.optional-dependencies]
web = ["websockets>=12.0"]
```

```python
# clients/web_client.py
# Connects to Lightpanda via CDP, or falls back to httpx for simple pages
# Auto-detects if Lightpanda is available, degrades to httpx + BeautifulSoup
```

### Installation (optional, for `web` tool)
```bash
# macOS
brew install nicholasgasior/tap/lightpanda
# or download binary from lightpanda.io
```

---

## Sentiment Analysis via LLM

### Design
- Use **Claude Haiku** (cheapest, fastest) for sentiment analysis
- Called internally by `sentiment` and `evaluate` composite tools
- Processes batches of Reddit/HN comments in one call

### Client

```python
# clients/sentiment_client.py
class SentimentAnalyzer:
    """LLM-based sentiment analysis using Claude Haiku."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")  # Required for sentiment tools
        self.model = "claude-haiku-4-5-20251001"

    async def analyze_discussions(
        self,
        topic: str,
        threads: List[Dict],  # [{source, title, comments: [...]}]
    ) -> Dict:
        """Analyze sentiment across discussion threads.

        Returns:
            {
                "overall_sentiment": "positive|negative|mixed|neutral",
                "confidence": 0.0-1.0,
                "key_praise": ["fast", "good DX", ...],
                "key_concerns": ["immature ecosystem", ...],
                "representative_quotes": [...],
                "adoption_signal": "growing|stable|declining",
                "summary": "..."
            }
        """
```

### Cost Estimate
- Haiku: ~$0.25/M input, ~$1.25/M output
- Typical sentiment call: ~2K input tokens (comments), ~500 output tokens
- Cost per call: ~$0.001 (basically free)
- Budget: ~1000 sentiment analyses for $1

---

## Environment Variables (updated)

```env
# === Required for base functionality ===
# (none — arXiv is free)

# === Recommended (free, unlocks more sources) ===
GITHUB_TOKEN=ghp_...                    # GitHub PAT — free, 5000 req/hr
REDDIT_CLIENT_ID=...                    # reddit.com/prefs/apps — free
REDDIT_CLIENT_SECRET=...                # reddit.com/prefs/apps — free

# === Optional (enhanced functionality) ===
SEMANTIC_SCHOLAR_API_KEY=...            # Higher S2 rate limits
ANTHROPIC_API_KEY=...                   # For sentiment analysis (Haiku)
STACKOVERFLOW_KEY=...                   # Higher SO rate limits
OPENALEX_EMAIL=...                      # Polite pool (100 req/s)
CROSSREF_EMAIL=...                      # Polite pool
LENS_API_TOKEN=...                      # Patent search
HF_TOKEN=...                            # HuggingFace higher limits

# === Not required (no-auth APIs) ===
# Hacker News, Dev.to, Lobsters, npm, PyPI, crates.io — all free, no auth
```

---

## Rate Limiting Strategy

```python
# utils/rate_limiter.py — extend existing rate limiters

RATE_LIMITS = {
    # Existing
    "arxiv": RateLimit(requests=1, per_seconds=3),
    "s2": RateLimit(requests=1, per_seconds=1),
    "openalex": RateLimit(requests=10, per_seconds=1),
    "crossref": RateLimit(requests=50, per_seconds=1),
    "dblp": RateLimit(requests=1, per_seconds=1),
    "hf": RateLimit(requests=10, per_seconds=1),
    "pwc": RateLimit(requests=5, per_seconds=1),
    "lens": RateLimit(requests=1, per_seconds=6),  # 10/min

    # New
    "github": RateLimit(requests=30, per_seconds=60),  # 5000/hr
    "hn": RateLimit(requests=10, per_seconds=1),        # Algolia generous
    "reddit": RateLimit(requests=1, per_seconds=1),     # 60/min OAuth
    "devto": RateLimit(requests=10, per_seconds=1),     # Generous
    "lobsters": RateLimit(requests=1, per_seconds=2),   # Be polite
    "so": RateLimit(requests=30, per_seconds=1),        # 300/day or 10k/day
    "npm": RateLimit(requests=10, per_seconds=1),
    "pypi": RateLimit(requests=10, per_seconds=1),
    "crates": RateLimit(requests=1, per_seconds=1),
    "lightpanda": RateLimit(requests=2, per_seconds=1), # Local, but be polite to targets
    "haiku": RateLimit(requests=5, per_seconds=1),      # Anthropic API
}
```

---

## Caching Strategy

```python
# store/cache.py — unified cache with TTL tiers

CACHE_TTL = {
    "trending": timedelta(minutes=15),    # HN/Reddit/GitHub trending
    "search": timedelta(hours=1),         # Search results
    "stats": timedelta(hours=24),         # Package stats, repo info
    "sentiment": timedelta(hours=6),      # Sentiment analysis results
    "paper_metadata": timedelta(days=7),  # arXiv/S2 paper info
    "web_scrape": timedelta(hours=2),     # Lightpanda scrapes
}

# Uses existing aiosqlite infrastructure
# Table: cache(key TEXT PRIMARY KEY, value TEXT, ttl_group TEXT, expires_at TIMESTAMP)
```

---

## Implementation Phases

### Phase 0: Consolidation (existing tools, no new sources)
1. Merge `search_papers` + `arxiv_advanced_query` → `search`
2. Merge 5 KB tools → `kb(action=...)`
3. Merge `research_context` + `research_memory` → `memory`
4. Merge `arxiv_citation_graph` + `arxiv_citation_context` → `citations`
5. Rename all `arxiv_*` prefixed tools
6. Update server.py registrations
7. Add backwards-compat aliases (old names → new handlers) for transition
8. Update `help` tool registry
9. Tests pass

### Phase 1: No-Auth Sources
10. `hn_client.py` + `hn` tool
11. `devto_client.py` + `community` tool (Dev.to + Lobsters)
12. `package_client.py` + `packages` tool
13. Unified cache layer (`store/cache.py`)

### Phase 2: Auth Sources
14. `github_client.py` + `github` tool
15. `reddit_client.py` + `reddit` tool
16. `so_client.py` (feed into `community` tool or standalone)
17. `web_client.py` + `web` tool (Lightpanda integration)

### Phase 3: Intelligence Layer
18. `sentiment_client.py` (Haiku-based)
19. `tech_pulse` composite tool
20. `evaluate` composite tool
21. `sentiment` composite tool
22. `deep_research` composite tool

### Phase 4: Polish
23. Update pyproject.toml with optional dependency groups
24. Update README with new tool docs
25. Update CLAUDE.md
26. Full test suite
27. MCP config examples for all env vars

---

## Naming Convention

**Philosophy:** Tools are verbs or nouns that answer "what does this do?" in one word.

- **No prefixes** — we're not just arxiv anymore
- **Action tools** use action params: `kb(action="save")`, `github(action="trending")`
- **Composite tools** are named for the question they answer: `evaluate`, `sentiment`, `tech_pulse`
- **Source tools** are named for their source: `github`, `hn`, `reddit`, `community`, `packages`, `web`

**Backwards compatibility:** Old names (`search_papers`, `arxiv_advanced_query`, `kb_save`, etc.) registered as aliases in `_TOOL_HANDLERS` for one version cycle, then removed.
