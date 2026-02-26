# Coverage Index - Revised Scoring Rubric

## Summary of Changes

### Problem Statement
The current rubric scores "good" Tier 1 coverage in the 60s when it should be in the 75-85 range. Op-eds written by the client score poorly because the rubric assumes third-party news coverage format.

### Key Changes
1. **Add Article Type Detection** - Op-eds, bylines, Q&As need different scoring paths
2. **Reduce Prominence Penalty** - From 7 points to 5 points max
3. **Increase Messaging Reward** - From 33 points to 35 points max
4. **Fix Op-Ed Scoring** - Op-eds should auto-score high on messaging, credibility, and prominence
5. **Add Minimum Score Floors** - Certain combinations guarantee minimum scores

---

## Revised Scoring Model

### Total: 104 base + 16 bonus = 120 (capped at 116)

---

## Tier 1: Foundational (36 points) - NO CHANGE

| Factor | Max | Description |
|--------|-----|-------------|
| outlet_tier | 20 | Tier 1=20, Tier 2=13, Tier 3=8, Tier 4=3 |
| overall_sentiment | 7 | Overall sentiment of coverage |
| article_exclusively_about_client | 4 | Solo focus vs. mentioned among others |
| article_type | 2 | Feature (2), News (1.5), Brief (0.5) |
| tone_toward_client | 3 | Positive=3, Neutral=1.5, Negative=0 |

**Rationale**: This tier captures outlet quality and basic sentiment - working correctly.

---

## Tier 2: Messaging & Voice (35 points) - INCREASED FROM 33

| Factor | Max | Description | Change |
|--------|-----|-------------|--------|
| key_messages_high | 12 | High priority messages (4 pts each, up to 3) | +3 |
| key_messages_medium | 3 | Medium priority messages (1.5 pts each, up to 2) | No change |
| key_messages_low | 1 | Low priority messages (0.5 pts each, up to 2) | No change |
| direct_quote_included | 6 | Direct quote from spokesperson | No change |
| number_of_quotes | 3 | Multiple quotes (1 pt each, up to 3) | No change |
| preferred_framing_used | 5 | Client's preferred narrative framing | No change |
| data_stat_cited | 3 | Data or proof points included | No change |
| **NEW: message_accuracy** | 2 | Messages conveyed without distortion | NEW |

**Rationale**: Message delivery is the core PR value. If your messages landed in a Tier 1 outlet, that's a win regardless of where you appear in the article. Increased high-priority message value from 3→4 points each.

---

## Tier 3: Prominence & Position (5 points) - REDUCED FROM 7

| Factor | Max | Description | Change |
|--------|-----|-------------|--------|
| paragraph_first_mention | 1.5 | First 2 paragraphs=1.5, First half=1, Second half=0.5 | Reduced from 3 |
| brand_in_opening | 1 | Brand in opening sentence | Reduced from 3 |
| percentage_focused_on_client | 1.5 | % of article about client | Reduced from 2 |
| brand_in_closing | 0.5 | Brand in closing | Reduced from 1 |
| total_brand_mentions | 0.5 | Number of mentions | Reduced from 1 |

**Rationale**: Prominence matters, but it was over-penalizing good coverage. An article with great messaging and spokesperson quotes shouldn't lose 7+ points just because the client appeared in paragraph 4. Moved 2 points to Tier 2 Messaging.

---

## Tier 4: Credibility & Spokesperson (10 points) - NO CHANGE

| Factor | Max | Description |
|--------|-----|-------------|
| spokesperson_named | 2.5 | Approved spokesperson is named |
| framed_as_expert | 2 | Positioned as expert/authority |
| framed_as_innovator | 2 | Positioned as innovator/leader |
| spokesperson_title | 1.5 | Title/role included |
| positive_trend_association | 1 | Associated with positive trend |
| problem_association | -1 | Associated with problem (PENALTY) |

**Rationale**: Working correctly for standard articles.

---

## Tier 5: Competitive Dynamics (9 points) - NO CHANGE

| Factor | Max | Description |
|--------|-----|-------------|
| positioned_as_leader | 2 | Leader vs. follower positioning |
| mentioned_before_competitors | 1.5 | Appears before competitors |
| share_of_voice | 1.5 | % of competitive mentions |
| competitors_mentioned | -1.5 | Competitors mentioned (PENALTY) |
| more_quotes_than_competitors | 1.5 | More quotes than competitors |
| number_competitors_mentioned | -2.5 | Each competitor = -0.5 (PENALTY) |
| competitor_in_headline | -0.5 | Competitor in headline (PENALTY) |

**Rationale**: Working correctly.

---

## Tier 6: Outlet & Audience Fit (6.5 points) - NO CHANGE

| Factor | Max | Description |
|--------|-----|-------------|
| outlet_industry_relevance | 3.5 | How relevant to client's industry |
| outlet_audience_relevance | 3 | How relevant to target audience |

**Rationale**: Working correctly.

---

## Tier 7: Supporting Details (2.5 points) - NO CHANGE

| Factor | Max | Description |
|--------|-----|-------------|
| cta_or_product_mention | 0.5 | CTA or product mentioned |
| article_length | 0.5 | Longer = better |
| brand_only_in_headline | 0.5 | Only company in headline |
| exclusive_story | 0.5 | Exclusive to this outlet |
| journalist_covered_before | 0.5 | Journalist relationship |

**Rationale**: Minor factors, working correctly.

---

## Bonus Points (16 points) - REVISED DETECTION

| Factor | Max | Description | Change |
|--------|-----|-------------|--------|
| op_ed_by_client | 8 | Op-ed/byline by client spokesperson | IMPROVE DETECTION |
| brand_in_headline | 3 | Client brand in headline | No change |
| syndicated | 1.5 | Picked up by other outlets | No change |
| ranks_for_keywords | 1.5 | Ranks in search for target keywords | No change |
| appears_in_google_news | 1 | In Google News | No change |
| open_access | 0.5 | No paywall | No change |

### OP-ED DETECTION RULES (CRITICAL FIX)

Detect op-ed/byline if ANY of these are true:
- URL contains: `/opinion/`, `/op-ed/`, `/contributor/`, `/voice/`, `/perspective/`
- Byline matches a client spokesperson name
- Article type field indicates "Opinion" or "Commentary"
- AI detects first-person voice from spokesperson perspective

**When op-ed detected, apply these overrides:**
- Tier 2 Messaging: Score based on message presence (should be high since client wrote it)
- Tier 3 Prominence: AUTO-SCORE 5/5 (client is the author, prominence is guaranteed)
- Tier 4 Credibility: AUTO-SCORE 8/10 (spokesperson_named=2.5, framed_as_expert=2, framed_as_innovator=2, title=1.5)
- Bonus: Apply 8-point op-ed bonus

---

## Minimum Score Floors (NEW)

To prevent good coverage from scoring poorly due to structural penalties:

| Condition | Minimum Score |
|-----------|---------------|
| Tier 1 outlet + spokesperson quoted + 2+ high-priority messages | 70 |
| Tier 1 outlet + op-ed by client | 80 |
| Tier 1 outlet + 3+ high-priority messages + positive sentiment | 72 |
| Any outlet + op-ed by client + all high-priority messages | 85 |

**Implementation**: After calculating raw score, check if floor conditions are met. If raw score is below floor, boost to floor value.

---

## Article Type Scoring Paths

### Path A: Standard News Coverage (default)
Use full rubric as designed.

### Path B: Op-Ed / Byline by Client
- Auto-detect via URL patterns or byline matching
- Apply prominence and credibility overrides
- Apply 8-point bonus
- High messaging scores expected (client controls content)

### Path C: Q&A / Interview Format
- Prominence scoring adjusted (Q&A format doesn't have traditional structure)
- Higher weight on quote quality and quantity
- Credibility auto-boosted (extended spokesperson visibility)

### Path D: Brief Mention / Roundup
- Lower prominence expectations
- Score primarily on outlet tier + sentiment + any messages present
- Cap expectations appropriately

---

## Expected Score Recalibration

With these changes, the Toronto Star op-ed would score:

| Tier | Old Score | New Score | Reason |
|------|-----------|-----------|--------|
| T1 Foundational | 29 | 29 | No change |
| T2 Messaging | 19.5 | 24 | Higher message value |
| T3 Prominence | 0 | 5 | Op-ed override (auto-max) |
| T4 Credibility | 1 | 8 | Op-ed override |
| T5 Competitive | 4.5 | 4.5 | No change |
| T6 Audience Fit | 4.5 | 4.5 | No change |
| T7 Supporting | 0.5 | 0.5 | No change |
| Bonus | 2.5 | 11 | +8 op-ed bonus + headline |
| **TOTAL** | **61.5** | **86.5** | +25 points |

This is appropriate - an op-ed in a Tier 1 outlet with strong messaging SHOULD score in the mid-80s.

---

## Implementation Checklist for Claude Code

1. [ ] Add article type detection (op-ed, Q&A, standard, brief)
2. [ ] Implement scoring path overrides for op-eds
3. [ ] Reduce Tier 3 max from 7 to 5
4. [ ] Increase Tier 2 key_messages_high from 9 to 12
5. [ ] Add message_accuracy factor (2 pts) to Tier 2
6. [ ] Implement minimum score floors
7. [ ] Update AI prompt to detect article type and provide reasoning
8. [ ] Test with the Toronto Star op-ed to verify 85+ score

