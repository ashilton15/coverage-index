"""Configuration and constants for Coverage Index."""

# 7-Tier Scoring Model Definition
SCORING_MODEL = {
    "tier_1_foundational": {
        "name": "Tier 1 - Foundational",
        "max_points": 39,
        "factors": {
            "outlet_tier": {"max": 23, "description": "Quality tier of the outlet"},
            "overall_sentiment": {"max": 7, "description": "Overall sentiment of the article"},
            "article_exclusively_about_client": {"max": 4, "description": "Article is exclusively about the client"},
            "article_type": {"max": 2, "description": "Type of article (feature/news/brief)"},
            "tone_toward_client": {"max": 3, "description": "Specific tone toward the client"}
        }
    },
    "tier_2_messaging": {
        "name": "Tier 2 - Messaging & Voice",
        "max_points": 35,
        "factors": {
            "key_messages_high": {"max": 12, "description": "High priority key messages present (4 pts each, max 3)"},
            "key_messages_medium": {"max": 3, "description": "Medium priority key messages present (1.5 pts each, max 2)"},
            "key_messages_low": {"max": 1, "description": "Low priority key messages present (0.5 pts each, max 2)"},
            "direct_quote_included": {"max": 6, "description": "Direct quote from spokesperson included"},
            "number_of_quotes": {"max": 3, "description": "Number of quotes from spokesperson"},
            "preferred_framing_used": {"max": 5, "description": "Client's preferred framing/narrative used"},
            "data_stat_cited": {"max": 3, "description": "Data or statistic from client cited"},
            "message_accuracy": {"max": 2, "description": "Messages conveyed without distortion"}
        }
    },
    "tier_3_prominence": {
        "name": "Tier 3 - Prominence & Position",
        "max_points": 5,
        "factors": {
            "paragraph_first_mention": {"max": 1.5, "description": "Paragraph of first mention (earlier = better)"},
            "brand_in_opening": {"max": 1, "description": "Brand in opening sentence"},
            "percentage_focused_on_client": {"max": 1.5, "description": "Percentage of article focused on client"},
            "brand_in_closing": {"max": 0.5, "description": "Brand in closing paragraph"},
            "total_brand_mentions": {"max": 0.5, "description": "Total number of brand mentions"}
        }
    },
    "tier_4_credibility": {
        "name": "Tier 4 - Credibility & Spokesperson",
        "max_points": 10,
        "factors": {
            "spokesperson_named": {"max": 2.5, "description": "Spokesperson is named"},
            "framed_as_expert": {"max": 2, "description": "Client framed as expert/authority"},
            "framed_as_innovator": {"max": 2, "description": "Client framed as innovator/leader"},
            "spokesperson_title": {"max": 1.5, "description": "Spokesperson title included"},
            "positive_trend_association": {"max": 1, "description": "Client associated with positive trend"},
            "problem_association": {"max": -1, "description": "Client associated with problem (PENALTY)", "is_penalty": True}
        }
    },
    "tier_5_competitive": {
        "name": "Tier 5 - Competitive Dynamics",
        "max_points": 9,
        "factors": {
            "positioned_as_leader": {"max": 2, "description": "Client positioned as leader vs follower"},
            "mentioned_before_competitors": {"max": 1.5, "description": "Client mentioned before competitors"},
            "share_of_voice": {"max": 1.5, "description": "Share of voice vs competitors"},
            "competitors_mentioned": {"max": -1.5, "description": "Any competitors mentioned (PENALTY)", "is_penalty": True},
            "more_quotes_than_competitors": {"max": 1.5, "description": "Client has more quotes than competitors"},
            "number_competitors_mentioned": {"max": -2.5, "description": "Number of competitors mentioned (PENALTY)", "is_penalty": True},
            "competitor_in_headline": {"max": -0.5, "description": "Competitor in headline (PENALTY)", "is_penalty": True}
        }
    },
    "tier_6_audience_fit": {
        "name": "Tier 6 - Outlet & Audience Fit",
        "max_points": 6.5,
        "factors": {
            "outlet_industry_relevance": {"max": 3.5, "description": "Outlet relevance to client's industry"},
            "outlet_audience_relevance": {"max": 3, "description": "Outlet relevance to target audience"}
        }
    },
    "tier_7_supporting": {
        "name": "Tier 7 - Supporting Details",
        "max_points": 2.5,
        "factors": {
            "cta_or_product_mention": {"max": 0.5, "description": "CTA or product mention"},
            "article_length": {"max": 0.5, "description": "Article length (longer = better)"},
            "brand_only_in_headline": {"max": 0.5, "description": "Brand is the only company in headline"},
            "exclusive_story": {"max": 0.5, "description": "Exclusive story"},
            "journalist_covered_before": {"max": 0.5, "description": "Journalist covered client before"}
        }
    },
    "bonus": {
        "name": "Bonus Points",
        "max_points": 20,
        "factors": {
            "op_ed_by_client": {"max": 10, "description": "Op-ed by client spokesperson in Tier 1 outlet"},
            "brand_in_headline": {"max": 3, "description": "Client brand appears in headline"},
            "syndicated": {"max": 1.5, "description": "Syndicated to other outlets"},
            "ranks_for_keywords": {"max": 1.5, "description": "Ranks for target keywords"},
            "appears_in_google_news": {"max": 1, "description": "Appears in Google News"},
            "open_access": {"max": 0.5, "description": "Open access (no paywall)"}
        }
    }
}

# Outlet tier point values (Tier 1 increased to 23 to reward top-tier placements)
OUTLET_TIER_POINTS = {1: 23, 2: 13, 3: 8, 4: 3}

# UI Colors (black/white minimal)
COLORS = {
    "primary": "#000000",
    "secondary": "#FFFFFF",
    "accent": "#333333",
    "background": "#FAFAFA",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "info": "#3B82F6",
}

# Claude model
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Detailed scoring prompt template
SCORING_PROMPT = '''You are a PR coverage analyst evaluating media coverage quality. Analyze this article and score EVERY factor listed below.

IMPORTANT CALIBRATION NOTES:
- A Tier 1 outlet with positive coverage about the client should typically score 75-90+
- Be GENEROUS with key message detection - look for the CONCEPT/THEME, not exact wording
- Bonus points are ADDITIVE and important - always check for brand in headline
- Competitor penalties only apply if competitors are framed FAVORABLY vs the client

## CLIENT CONTEXT
- **Company**: {client_name}
- **Industry**: {industry}
- **Spokespeople**: {spokespeople}
- **Competitors**: {competitors}

### Key Messages by Priority:
**HIGH PRIORITY (4 pts each if present, max 3):**
{key_messages_high}

**MEDIUM PRIORITY (1.5 pts each if present, max 2):**
{key_messages_medium}

**LOW PRIORITY (0.5 pts each if present, max 2):**
{key_messages_low}

## ARTICLE TO ANALYZE
- **Outlet**: {outlet_name} (Tier {tier}, {outlet_type})
- **Headline**: {headline}
- **Article Type Detected**: {article_type}
- **Client Op-Ed**: {is_client_op_ed}

**Content:**
{content}

---

## SCORING INSTRUCTIONS

Score each factor based on the criteria below. Return exact numeric scores.

### TIER 1 - FOUNDATIONAL (max 39 pts)
- **outlet_tier**: Already determined = {outlet_tier_points} points (Tier {tier})
- **overall_sentiment** (0-7): Overall sentiment of article. 7=very positive/celebratory, 6=positive, 5=mostly positive, 4=neutral, 2=somewhat negative, 0=very negative. Most business news is 4-6.
- **article_exclusively_about_client** (0-4): 4=100% about client, 3=75%+, 2=50%, 1=25%, 0=brief mention
- **article_type** (0-2): 2=in-depth feature/profile/op-ed, 1.5=news article with depth, 1=standard news, 0.5=brief
- **tone_toward_client** (0-3): 3=enthusiastic/glowing, 2=positive/favorable, 1.5=neutral-positive, 1=neutral, 0=negative

### TIER 2 - MESSAGING & VOICE (max 35 pts) - Most important tier after foundational
- **key_messages_high** (0-12): Count HIGH priority messages present × 4 (max 12). Look for the CONCEPT/THEME, not exact wording. If the article conveys the message's intent, count it.
- **key_messages_medium** (0-3): Count MEDIUM priority messages present × 1.5 (max 3). Same - concept matching, not exact phrases.
- **key_messages_low** (0-1): Count LOW priority messages present × 0.5 (max 1). Concept matching.
- **direct_quote_included** (0-6): 6=any spokesperson from list quoted directly by name, 4=other company rep quoted, 2=company paraphrased, 0=not quoted
- **number_of_quotes** (0-3): 3=3+ quotes from company, 2=2 quotes, 1=1 quote, 0=none
- **preferred_framing_used** (0-5): 5=client's narrative dominates, 4=strongly present, 3=partially used, 1=weak, 0=different framing
- **data_stat_cited** (0-3): 3=client data/stats prominently cited, 2=data mentioned, 1=referenced briefly, 0=none
- **message_accuracy** (0-2): 2=messages conveyed accurately without distortion, 1=mostly accurate, 0=distorted or misrepresented

### TIER 3 - PROMINENCE & POSITION (max 5 pts) - Reduced weight, position matters less
- **paragraph_first_mention** (0-1.5): 1.5=paragraph 1-2, 1=first half, 0.5=second half, 0=very late
- **brand_in_opening** (0-1): 1=brand in first sentence/paragraph, 0=not in opening
- **percentage_focused_on_client** (0-1.5): 1.5=75%+, 1=50-74%, 0.5=25-49%, 0=<25%
- **brand_in_closing** (0-0.5): 0.5=brand in closing paragraph, 0=not present
- **total_brand_mentions** (0-0.5): 0.5=5+ mentions, 0.25=3-4 mentions, 0=1-2 mentions

### TIER 4 - CREDIBILITY & SPOKESPERSON (max 10 pts, has penalties)
- **spokesperson_named** (0-2.5): 2.5=any spokesperson from list named by full name, 1.5=other company exec named, 0.5=company referenced, 0=not mentioned
- **framed_as_expert** (0-2): 2=explicitly positioned as expert/authority/thought leader, 1=implied expertise, 0=not framed
- **framed_as_innovator** (0-2): 2=positioned as innovator/pioneer/leader in space, 1=implied innovation, 0=not positioned
- **spokesperson_title** (0-1.5): 1.5=full title included, 1=partial title, 0=no title
- **positive_trend_association** (0-1): 1=client associated with positive industry/market trend, 0.5=neutral trend, 0=no trend
- **problem_association** (0 or -1): -1 PENALTY only if client is explicitly blamed for a problem. Neutral coverage of industry challenges = 0.

### TIER 5 - COMPETITIVE DYNAMICS (max 9 pts, has penalties)
- **positioned_as_leader** (0-2): 2=explicitly positioned as leader, 1=implied, 0=follower/equal
- **mentioned_before_competitors** (0-1.5): 1.5=mentioned first, 0.75=same paragraph, 0=after. Give 1.5 if no competitors mentioned.
- **share_of_voice** (0-1.5): 1.5=dominant voice, 0.75=equal, 0=competitors dominate. Give 1.5 if no competitors mentioned.
- **competitors_mentioned** (0 or -1.5): -1.5 PENALTY ONLY if competitors are framed favorably vs client. If client is clearly the focus/leader, no penalty.
- **more_quotes_than_competitors** (0-1.5): 1.5=more quotes than competitors OR no competitor quotes, 0=fewer
- **number_competitors_mentioned** (0 to -2.5): -0.5 for each competitor framed favorably (max -2.5). Neutral mentions = 0 penalty.
- **competitor_in_headline** (0 or -0.5): -0.5 PENALTY only if competitor name is in headline

### TIER 6 - OUTLET & AUDIENCE FIT (max 6.5 pts)
- **outlet_industry_relevance** (0-3.5): 3.5=industry-specific outlet (e.g., crypto/finance pub for fintech), 2.5=general business/finance outlet, 1.5=general news, 0=completely irrelevant
- **outlet_audience_relevance** (0-3): 3=reaches exact target audience (investors, customers, partners), 2=reaches related audience, 1=general audience, 0=wrong audience

### TIER 7 - SUPPORTING DETAILS (max 2.5 pts)
- **cta_or_product_mention** (0-0.5): 0.5=includes CTA or product mention, 0=none
- **article_length** (0-0.5): 0.5=long-form (800+ words), 0.25=medium, 0=short
- **brand_only_in_headline** (0-0.5): 0.5=only company in headline, 0=others included
- **exclusive_story** (0-0.5): 0.5=exclusive/first-to-report, 0=not exclusive
- **journalist_covered_before** (0-0.5): 0.5=if you can determine journalist covered client before, else 0

### BONUS POINTS (max 16 pts) - ALWAYS CHECK THESE, they are additive
- **op_ed_by_client** (0-10): 10=op-ed written by any listed spokesperson in Tier 1 outlet, 5=Tier 2, 0=not op-ed by client
- **brand_in_headline** (0-3): IMPORTANT - Give 3 points if "{client_name}" or any recognizable form of the brand appears in the headline. Check carefully!
- **syndicated** (0-1.5): 1.5=if syndicated to multiple outlets, 0=single outlet
- **ranks_for_keywords** (0-1.5): 1.5=likely to rank for target keywords based on headline/content, 0.75=somewhat likely
- **appears_in_google_news** (0-1): 1=Tier 1 or major outlet (likely in Google News), 0.5=Tier 2
- **open_access** (0-0.5): 0.5=no paywall, 0=paywalled

---

Return your analysis as JSON with this EXACT structure. For each factor, include both a score AND an explanation.

{{
    "tier_1_foundational": {{
        "outlet_tier": {{"score": {outlet_tier_points}, "explanation": "Tier {tier} outlet"}},
        "overall_sentiment": {{"score": <0-7>, "explanation": "<why this sentiment score>"}},
        "article_exclusively_about_client": {{"score": <0-4>, "explanation": "<% of article about client>"}},
        "article_type": {{"score": <0-2>, "explanation": "<feature/news/brief>"}},
        "tone_toward_client": {{"score": <0-3>, "explanation": "<positive/neutral/negative tone>"}}
    }},
    "tier_2_messaging": {{
        "key_messages_high": {{"score": <0-12>, "explanation": "Found X of 3 high-priority messages: [list which ones]"}},
        "key_messages_medium": {{"score": <0-3>, "explanation": "Found X of 2 medium-priority messages: [list which ones]"}},
        "key_messages_low": {{"score": <0-1>, "explanation": "Found X low-priority messages"}},
        "direct_quote_included": {{"score": <0-6>, "explanation": "<who was quoted and how>"}},
        "number_of_quotes": {{"score": <0-3>, "explanation": "<count of quotes>"}},
        "preferred_framing_used": {{"score": <0-5>, "explanation": "<how client narrative was used>"}},
        "data_stat_cited": {{"score": <0-3>, "explanation": "<what data/stats cited>"}},
        "message_accuracy": {{"score": <0-2>, "explanation": "<accuracy of message conveyance>"}}
    }},
    "tier_3_prominence": {{
        "paragraph_first_mention": {{"score": <0-1.5>, "explanation": "First mentioned in paragraph X"}},
        "brand_in_opening": {{"score": <0-1>, "explanation": "<in first sentence/paragraph/not>"}},
        "percentage_focused_on_client": {{"score": <0-1.5>, "explanation": "~X% focused on client"}},
        "brand_in_closing": {{"score": <0-0.5>, "explanation": "<in closing or not>"}},
        "total_brand_mentions": {{"score": <0-0.5>, "explanation": "X total mentions"}}
    }},
    "tier_4_credibility": {{
        "spokesperson_named": {{"score": <0-2.5>, "explanation": "<who was named>"}},
        "framed_as_expert": {{"score": <0-2>, "explanation": "<how framed as expert or not>"}},
        "framed_as_innovator": {{"score": <0-2>, "explanation": "<how framed as innovator or not>"}},
        "spokesperson_title": {{"score": <0-1.5>, "explanation": "<title included or not>"}},
        "positive_trend_association": {{"score": <0-1>, "explanation": "<trend association>"}},
        "problem_association": {{"score": <0 or -1>, "explanation": "<any problem association - PENALTY>"}}
    }},
    "tier_5_competitive": {{
        "positioned_as_leader": {{"score": <0-2>, "explanation": "<leader positioning>"}},
        "mentioned_before_competitors": {{"score": <0-1.5>, "explanation": "<mention order>"}},
        "share_of_voice": {{"score": <0-1.5>, "explanation": "<voice dominance>"}},
        "competitors_mentioned": {{"score": <0 or -1.5>, "explanation": "<competitor mention penalty if applicable>"}},
        "more_quotes_than_competitors": {{"score": <0-1.5>, "explanation": "<quote comparison>"}},
        "number_competitors_mentioned": {{"score": <0 to -2.5>, "explanation": "<count of competitors mentioned - PENALTY>"}},
        "competitor_in_headline": {{"score": <0 or -0.5>, "explanation": "<competitor in headline - PENALTY>"}}
    }},
    "tier_6_audience_fit": {{
        "outlet_industry_relevance": {{"score": <0-3.5>, "explanation": "<outlet relevance to industry>"}},
        "outlet_audience_relevance": {{"score": <0-3>, "explanation": "<audience fit>"}}
    }},
    "tier_7_supporting": {{
        "cta_or_product_mention": {{"score": <0-0.5>, "explanation": "<CTA/product mention>"}},
        "article_length": {{"score": <0-0.5>, "explanation": "<length assessment>"}},
        "brand_only_in_headline": {{"score": <0-0.5>, "explanation": "<headline exclusivity>"}},
        "exclusive_story": {{"score": <0-0.5>, "explanation": "<exclusivity>"}},
        "journalist_covered_before": {{"score": <0-0.5>, "explanation": "<prior coverage>"}}
    }},
    "bonus": {{
        "op_ed_by_client": {{"score": <0-10>, "explanation": "<op-ed assessment>"}},
        "brand_in_headline": {{"score": <0-3>, "explanation": "<brand in headline or not>"}},
        "syndicated": {{"score": <0-1.5>, "explanation": "<syndication>"}},
        "ranks_for_keywords": {{"score": <0-1.5>, "explanation": "<keyword ranking potential>"}},
        "appears_in_google_news": {{"score": <0-1>, "explanation": "<Google News likelihood>"}},
        "open_access": {{"score": <0-0.5>, "explanation": "<paywall status>"}}
    }},
    "summary": "<2-3 sentence summary of key strengths and weaknesses. DO NOT include any numeric scores in this summary - the score will be calculated separately.>",
    "key_messages_found": ["<list the actual key messages that were present in the article>"],
    "competitors_found": ["<list of competitors mentioned in the article>"]
}}

Return ONLY valid JSON, no other text.'''


def get_outlet_tier_points(tier: int) -> float:
    """Calculate points based on outlet tier."""
    return OUTLET_TIER_POINTS.get(tier, 0)


def calculate_tier_score(tier_scores: dict, tier_key: str) -> float:
    """Calculate total score for a single tier."""
    if tier_key not in tier_scores:
        return 0
    return sum(tier_scores[tier_key].values())


def extract_score(factor_data):
    """Extract numeric score from factor data (handles both old and new format)."""
    if isinstance(factor_data, dict) and "score" in factor_data:
        return factor_data["score"]
    return factor_data


def calculate_total_score(scores: dict) -> dict:
    """
    Calculate total score from individual factor scores.

    Returns dict with total_score, tier_scores, and grade.
    """
    tier_totals = {}
    total = 0

    for tier_key, tier_info in SCORING_MODEL.items():
        tier_sum = 0
        if tier_key in scores:
            for factor_key, factor_data in scores[tier_key].items():
                score = extract_score(factor_data)
                if isinstance(score, (int, float)):
                    tier_sum += score

        tier_totals[tier_key] = {
            "name": tier_info["name"],
            "score": round(tier_sum, 1),
            "max": tier_info["max_points"]
        }

        if tier_key != "bonus":
            total += max(0, tier_sum)  # Don't let individual tiers go negative
        else:
            total += max(0, tier_sum)  # Bonus can only add

    # Cap at 119 (103 base + 16 bonus) - adjusted for new weights
    total = min(119, max(0, total))

    return {
        "total_score": round(total, 1),
        "tier_scores": tier_totals,
        "grade": get_score_grade(total)
    }


def get_score_grade(score: float) -> str:
    """Get letter grade for score."""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    elif score >= 45:
        return "D+"
    elif score >= 40:
        return "D"
    else:
        return "F"


def get_score_color(score: float) -> str:
    """Get color for score display."""
    if score >= 80:
        return COLORS["success"]  # Green
    elif score >= 60:
        return COLORS["info"]  # Blue
    elif score >= 40:
        return COLORS["warning"]  # Amber
    else:
        return COLORS["error"]  # Red
