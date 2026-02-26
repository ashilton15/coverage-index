# Coverage Scorer Tool - Planning Document

## Status: ✅ PLANNING COMPLETE

All sections have been filled in through systematic Q&A. Ready for implementation.

**Before starting implementation, gather:**
- [ ] Outlet database (existing list with tiers)
- [ ] Agnostic branding assets (colors, logo)
- [ ] Sample coverage articles for testing

---

## 1. Problem Statement & Purpose

### What problem are we solving?
PR professionals currently rely on vanity metrics (impressions, reach, AVE) that don't reflect the actual quality or business impact of media coverage. There's no standardized way to evaluate whether a piece of coverage actually delivered value.

### Who is this for?
- [x] Individual PR practitioners at Agnostic
- [x] Client-facing reports/dashboards
- [ ] New business pitches/demos (secondary)
- [ ] Other agencies (future SaaS?)

**Decision**: Both internal team use AND client-facing reports are equally important. The tool needs to serve practitioners doing day-to-day evaluation AND produce outputs suitable for client deliverables.

### Primary use case
**Score a batch of coverage** - The primary workflow is evaluating multiple pieces of coverage at once (e.g., a week or month of coverage), not single articles one at a time. This has implications for the UI (bulk input needed) and output (aggregate/comparison views important).

### Success criteria
1. **Client value** - Clients find the scores meaningful and actionable (they can use them to inform strategy)
2. **Better insights** - Surfaces insights that weren't possible with manual evaluation (patterns, trends, comparisons)

---

## 2. Core Functionality

### High-level flow
1. **Input**: User provides batch of coverage (URLs, text, or both)
2. **Analysis**: AI evaluates each piece against client's key messages and scoring criteria
3. **Output**: Numeric scores (0-100) with explanatory notes, viewable individually and in aggregate

### Scoring Factors

**1. OUTLET AUTHORITY (30% weight)**
Sub-criteria:
- Tier classification (Tier 1/2/3)
- Industry relevance (is this outlet relevant to the client's vertical?)
- Content type (news article vs. blog post vs. opinion/editorial)

Scoring logic: Start with tier base score, adjust for relevance and content type.

**2. MESSAGE PULL-THROUGH (30% weight)**
Sub-criteria:
- Are the client's key themes/messages present?
- Are messages represented accurately (not distorted or taken out of context)?
- Are messages placed prominently (early in article, not buried)?

**3. BRAND PROMINENCE (20% weight)**
Sub-criteria:
- Is the brand mentioned in the lead paragraph?
- What % of the article focuses on this brand vs. other subjects?

**4. SENTIMENT/TONE (15% weight)**
Sub-criteria:
- Overall tone toward the brand (positive / neutral / negative)
- How are quotes framed (favorable vs. critical)?
- Are there implicit criticisms or negative implications?
- How is the brand positioned relative to any competitors mentioned?

**5. SPOKESPERSON VISIBILITY (5% weight)**
Sub-criteria:
- Is a spokesperson named and directly quoted?
- Is the spokesperson positioned as an expert/authority?
- Does the quote advance the client's key messages?

**Removed from scoring:**
- ~~Competitive positioning as standalone factor~~ - Folded into Sentiment (competitive framing)

### Scoring Mechanics
- **Scale**: Numeric 0-100 for each factor AND overall score
- **Weights**: Fixed for MVP. Custom weights per client planned for v2.
- **Priority**: Outlet > Message > Prominence > Sentiment > Spokesperson
- **Output**: Overall score (0-100) plus sub-scores for each factor, plus explanatory notes

**Rough weight distribution (MVP):**
| Factor | Weight |
|--------|--------|
| Outlet Authority | 30% |
| Message Pull-Through | 30% |
| Brand Prominence | 20% |
| Sentiment | 15% |
| Spokesperson | 5% |

### AI/LLM Role
- **Model**: Claude (Anthropic)
- **AI does**: All content analysis - sentiment, message matching, prominence assessment, spokesperson quality. Single prompt per article returns all scores with explanations.
- **Rule-based**: Outlet tier lookup (from database), weight calculations, aggregation math
- **Consistency**: Structured prompt with explicit scoring rubric; same prompt template for all articles
- **Cost**: ~$0.01-0.05 per article acceptable. Batch of 50 articles = $0.50-2.50.
- **Message output format**: Overall message pull-through score with explanatory notes (not per-message breakdown)

---

## 3. User Experience & Workflow

### Primary User Flow
**Step wizard approach:**
1. **Upload**: User uploads Excel spreadsheet containing URLs
2. **Select Client**: Choose which client this coverage is for (loads their key messages, spokespeople)
3. **Review**: Preview the URLs, confirm ready to analyze
4. **Analyze**: Tool scrapes each URL and runs AI analysis (show progress)
5. **Results**: Dashboard summary appears, with ability to drill into individual articles
6. **Export**: Download results as Excel

### Input Methods
- [x] **Excel upload with URLs** (MVP) - User uploads spreadsheet, tool scrapes each URL
- [ ] Manual text paste (future) - For when scraping fails or user prefers
- [ ] PDF/document upload (future)
- [ ] Direct URL paste (future) - Single URL quick analysis

**Note**: URL scraping is primary, with **fallback to manual paste** when scraping fails (paywalls, bot blocking, dynamic content). User prompted to paste article text for failed URLs.

### Output Format
- **Primary view**: Dashboard summary (avg score, distribution, top/bottom performers) with drill-down to individual articles
- **Article detail**: Full breakdown of scores per factor with AI explanations
- **Export**: Excel download with all scores and notes
- **Historical tracking**: Nice to have for v1.1, not MVP. Each analysis is standalone initially.

### UI Preferences
- **Layout**: Step-by-step wizard flow (Upload → Select Client → Review → Analyze → Results)
- **Detail level**: Summary by default, expand for details
- **Responsive**: Desktop-only is acceptable (primary use case is at-desk work)
- **Branding**: Should be Agnostic-branded (colors, logo, look and feel)

---

## 4. Data Architecture

### What data needs to persist?
**Must persist:**
- **Clients**: Name, key messages, spokespeople, industry/vertical
- **Outlets**: Name, domain, tier, category

**Does NOT need to persist (for MVP):**
- **Coverage History**: Results are exported to Excel and discarded from system
- **Users**: No individual accounts - shared password access

### Storage Decision
**Choice: Google Sheets** (retry with better implementation)

| Option | Pros | Cons |
|--------|------|------|
| **Google Sheets** ✓ | Easy sharing, familiar, free, editable outside app | Scale limits, slow, no real DB features |
| Supabase | Real database, free tier, auth built-in | Learning curve, another service |
| Airtable | Spreadsheet-like but more robust | Cost at scale |
| Local JSON/SQLite | Simple, no external deps | No collaboration |

**Rationale**: Familiarity and editability outside the app outweigh the downsides for this use case. Client configs and outlet database are relatively small datasets.

### Previous Build Issues
**Unclear** - specific issues with previous Google Sheets implementation not documented.

**Mitigation**: Keep Sheets usage simple - two sheets (Clients, Outlets), minimal writes, cache reads where possible.

### Authentication
**Shared password** - Simple password protection for the whole app. No individual user accounts needed for MVP.

---

## 5. Technical Stack

### Frontend/UI
**Choice: Streamlit**
- Python-based, quick to build, good for data/dashboard apps
- Previous experience with it
- Step-wizard flow is achievable with `st.session_state`

### AI/LLM Integration
- **Model**: Claude (Anthropic) - Sonnet for cost/quality balance
- **API key**: Stored in Streamlit Cloud secrets (environment variable). Agnostic has one Anthropic account, costs managed centrally. Users don't see or manage the key.
- **Prompt structure**: Single structured prompt per article, returns JSON with all scores and explanations
- **Cost**: ~$0.01-0.05 per article (acceptable)
- **Rate limiting**: Anthropic has generous rate limits; batch processing should stay well under

### Hosting/Deployment
**Choice: Streamlit Community Cloud**
- Free tier available
- Purpose-built for Streamlit apps
- Easy deployment from GitHub
- Custom domain: Not required for MVP
- Uptime: Best-effort (Community Cloud), acceptable for internal tool

### Authentication
- [x] **Simple shared password** - One password for the whole app
- [ ] None (open access with URL)
- [ ] Individual user accounts
- [ ] Google SSO

Implemented via `st.text_input(type="password")` check on app load. Password stored in Streamlit secrets.

---

## 6. Client Configuration

### Per-Client Data
**Required fields:**
- **Client name**: Display name
- **Key messages**: Flexible number (varies widely - some have 2, some have 10). Format: short phrases or brief statements (e.g., "Industry leader in sustainable packaging")
- **Spokespeople**: Names of people to look for. AI handles name variations (John Smith, J. Smith, Mr. Smith, etc.) - no need to enter all variants
- **Industry/vertical**: Category for context (e.g., "B2B Tech", "Consumer Goods", "Healthcare")
- **Competitors**: Names of competitor companies to watch for

**Not needed for MVP:**
- Custom scoring weights (fixed for v1)
- Target outlets list

### Client Setup Workflow
- **Who sets up clients**: Account teams (the team working on that client)
- **How**: In-app UI within Streamlit (not direct Google Sheet editing)
- **Change frequency**: Occasionally - messages/spokespeople may update, but not constantly
- **Storage**: Client data written to Google Sheet, but managed through app UI

---

## 7. Outlet Database

### Outlet Data Fields
- **Name**: Display name (e.g., "The New York Times")
- **Domain**: URL pattern for matching (e.g., "nytimes.com")
- **Tier**: 1, 2, or 3 (see below)
- **Category**: trade, national, regional, broadcast, podcast, blog, etc.

**Tier Definitions:**
| Tier | Description | Examples |
|------|-------------|----------|
| 1 | Top national/international outlets | NYT, WSJ, Forbes, Bloomberg, major broadcast |
| 2 | Strong regional or leading trade publications | Regional papers, top industry trades |
| 3 | Everything else | Local news, niche blogs, smaller trades |

### Outlet Data Population
- **Initial data**: Import from existing list (Agnostic has a list with tiers already)
- **Ongoing**: Add new outlets as encountered
- **Unknown outlets**: When tool encounters outlet not in database, **prompt user to classify it** before continuing. Adds to database for future use.
- **No external API**: Manual curation is fine for this scale

---

## 8. Lessons from Previous Build

### What Worked Well
- **Scoring factors**: The factors measured were right, just needed better execution. Keep the same conceptual framework.

### What Didn't Work
- **Scoring inconsistency**: Results felt random or didn't make sense. Need more deterministic, explainable scoring.
- **Hard to maintain**: Lots of bugs, difficult to update clients/outlets or fix issues.

### Specific Pain Points
**Two main frustrations:**
1. Scoring inconsistencies - output wasn't trustworthy
2. Maintenance burden - bugs and brittleness

**Implications for new build:**
- Use structured AI prompts with explicit scoring rubrics for consistency
- Keep architecture simple - fewer moving parts = fewer bugs
- Write clear code with good separation of concerns
- Add explanations to scores so users can understand/verify them

---

## 9. Scope Definition

### MVP - Must Have for v1
1. **Two input modes**: Single article URL/paste AND batch Excel upload with URLs
2. **URL scraping**: Automatic content extraction from URLs
3. **AI-powered scoring**: All factors evaluated by Claude with explanations
4. **Results dashboard**: Summary view with drill-down to individual articles
5. **Excel export**: Download results
6. **Client management**: In-app UI to add/edit clients (name, messages, spokespeople, industry, competitors)
7. **Outlet database**: Tier lookup with prompt for unknown outlets
8. **Shared password auth**: Simple protection

### Nice to Have - v1.1
1. Historical tracking / trend comparison
2. Per-client custom scoring weights
3. PDF report export (formatted for clients)
4. Fallback text paste when scraping fails

### Future / Out of Scope
1. Individual user accounts
2. SaaS / multi-agency use
3. API integrations (Meltwater, Cision, etc.)
4. Automated monitoring / alerts 

---

## 10. Open Questions & Concerns

### Unresolved Questions
**Prep needed before building:**
1. **Outlet list** - Need the existing outlet database with tiers to import
2. **Branding assets** - Need Agnostic brand colors/logo for UI styling
3. **Sample coverage** - Would help to have example articles for testing the scoring

### Risks & Concerns
1. **URL scraping failures** - Paywalled sites will block scraping. Mitigation: fallback to manual paste.
2. **Google Sheets reliability** - Previous build had issues (unspecified). Mitigation: keep usage simple, minimal writes, good error handling.
3. **AI scoring consistency** - Previous version had inconsistent results. Mitigation: structured prompts with explicit rubric, return explanations with scores.
4. **Two input modes** - Single article + batch adds UI complexity. Mitigation: clean wizard flow, shared analysis pipeline. 

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-26 | Use Claude API for all content analysis | Consistency with Claude Code, good balance of cost/quality |
| 2026-01-26 | 0-100 numeric scoring (not letter grades) | Easier to track trends, more precise |
| 2026-01-26 | Fixed weights for MVP (Outlet 30%, Message 30%, Prominence 20%, Sentiment 15%, Spokesperson 5%) | Simplify v1, add customization in v2 |
| 2026-01-26 | Google Sheets for storage (retry) | Familiarity, editable outside app, acceptable for data volume |
| 2026-01-26 | Streamlit + Streamlit Cloud | Quick to build, previous experience, free hosting |
| 2026-01-26 | 3-tier outlet system | Simple enough to maintain, sufficient granularity |
| 2026-01-26 | Fallback to paste when scraping fails | Realistic given paywall constraints |
| 2026-01-26 | Both single article AND batch input | User requirement - covers all use cases |
| 2026-01-26 | Shared password auth (not individual accounts) | Sufficient security for internal tool, simpler to build |
| 2026-01-26 | Competitive positioning removed as standalone factor | Folded into sentiment/framing, not independently valuable |

---

## Implementation Notes

**Key technical considerations:**

1. **Scraping**: Use `newspaper3k` or `trafilatura` for article extraction. Handle failures gracefully with paste fallback.

2. **AI Prompt Structure**: Single prompt per article that returns structured JSON:
   ```json
   {
     "outlet_relevance": {"score": 85, "explanation": "..."},
     "message_pullthrough": {"score": 70, "explanation": "..."},
     "brand_prominence": {"score": 60, "explanation": "..."},
     "sentiment": {"score": 80, "explanation": "..."},
     "spokesperson": {"score": 50, "explanation": "..."},
     "overall": {"score": 73, "explanation": "..."}
   }
   ```

3. **Google Sheets Structure**:
   - Sheet 1: `clients` (name, messages, spokespeople, industry, competitors)
   - Sheet 2: `outlets` (name, domain, tier, category)

4. **Streamlit Session State**: Track wizard step, current analysis batch, client selection

5. **Error Handling**: Log all scraping/API failures, surface to user clearly

