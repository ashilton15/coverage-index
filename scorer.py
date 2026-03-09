"""AI scoring module using Claude for Coverage Index."""

from __future__ import annotations

import json
import re
import hashlib
import anthropic
from config import (
    SCORING_PROMPT,
    CLAUDE_MODEL,
    SCORING_MODEL,
    get_outlet_tier_points,
    calculate_total_score,
    extract_score,
)

# In-memory score cache to ensure consistency
# Key: hash of (url, client_name, campaign_name)
# Value: full score result dict
_score_cache: dict[str, dict] = {}


def get_cache_key(url: str, client_name: str, campaign_messages: list) -> str:
    """Generate a cache key from URL and campaign context."""
    # Include key messages in hash to invalidate cache if campaign changes
    content = f"{url}|{client_name}|{','.join(sorted(campaign_messages[:5]))}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cached_score(cache_key: str) -> dict | None:
    """Get cached score result if available."""
    return _score_cache.get(cache_key)


def cache_score(cache_key: str, result: dict) -> None:
    """Cache a score result."""
    _score_cache[cache_key] = result


def clear_score_cache() -> None:
    """Clear the score cache (useful for re-scoring)."""
    _score_cache.clear()


def create_client(api_key: str) -> anthropic.Anthropic:
    """Create Anthropic client."""
    return anthropic.Anthropic(api_key=api_key)


def format_key_messages(messages: list, priority: str) -> str:
    """Format key messages for a specific priority level."""
    if not messages:
        return "  (None specified)"
    return "\n".join(f"  - {msg}" for msg in messages)


# Op-ed URL patterns
OP_ED_URL_PATTERNS = [
    r'/opinion/',
    r'/op-ed/',
    r'/oped/',
    r'/contributor/',
    r'/voice/',
    r'/perspective/',
    r'/commentary/',
    r'/views/',
    r'/opinions/',
]


def detect_op_ed_url(url: str) -> bool:
    """Check if URL pattern suggests an op-ed/opinion piece."""
    if not url:
        return False
    url_lower = url.lower()
    for pattern in OP_ED_URL_PATTERNS:
        if re.search(pattern, url_lower):
            return True
    return False


def check_byline_match(content: str, headline: str, spokespeople: list,
                       raw_html: str = None, author_meta: str = None) -> str | None:
    """
    Check if any spokesperson name appears as the author/byline.
    Returns the matched spokesperson name or None.

    Checks multiple sources:
    1. Author metadata from scraper
    2. Raw HTML for meta tags and byline elements
    3. Content body for byline patterns
    """
    if not spokespeople:
        return None

    # First, check if author metadata directly matches
    if author_meta:
        for spokesperson in spokespeople:
            if spokesperson.lower() in author_meta.lower():
                return spokesperson

    # Second, check raw HTML for author metadata patterns
    if raw_html:
        html_lower = raw_html.lower()

        # Look for spokesperson names in HTML metadata areas
        for spokesperson in spokespeople:
            name_lower = spokesperson.lower()

            # Check common patterns in HTML
            patterns_to_check = [
                f'author">{name_lower}',          # <span class="author">Name
                f'author" content="{name_lower}', # meta author tag
                f'writes {name_lower}',           # "writes Tom Duff Gordon"
                f'by {name_lower}',               # "by Tom Duff Gordon"
                f'>{name_lower}</a>',             # <a href="...">Name</a>
                f'>{name_lower}<',                # >Name< in any tag
            ]

            for pattern in patterns_to_check:
                if pattern in html_lower:
                    return spokesperson

    # Third, check content body with byline patterns
    byline_patterns = [
        r'(?:by|written by|author)[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)',
        r'(?:^|\n)([A-Z][a-z]+ [A-Z][a-z]+)\s+is\s+(?:the|a)\s+',
        r'(?:^|\n)([A-Z][a-z]+ [A-Z][a-z]+),?\s+(?:CEO|President|VP|Director|Head|Chief)',
    ]

    text_to_search = f"{headline}\n{content[:2000]}"  # Check headline and beginning

    for spokesperson in spokespeople:
        # Direct name check (case-insensitive)
        if spokesperson.lower() in text_to_search.lower():
            # Verify it looks like a byline (name appears early, often with title)
            name_parts = spokesperson.split()
            if len(name_parts) >= 2:
                # Check for "By [Name]" or "[Name] is the CEO" patterns
                first_500 = text_to_search[:500].lower()
                name_lower = spokesperson.lower()
                if f"by {name_lower}" in first_500 or f"{name_lower} is" in first_500:
                    return spokesperson

        # Check byline patterns
        for pattern in byline_patterns:
            matches = re.findall(pattern, text_to_search, re.IGNORECASE)
            for match in matches:
                for spkp in spokespeople:
                    if spkp.lower() in match.lower() or match.lower() in spkp.lower():
                        return spkp

    return None


def detect_article_type(url: str, content: str, headline: str, spokespeople: list,
                        raw_html: str = None, author_meta: str = None) -> dict:
    """
    Detect article type and whether it's a client op-ed.

    Returns:
        dict with: is_op_ed_format, is_client_op_ed, matched_spokesperson, article_type
    """
    is_op_ed_format = detect_op_ed_url(url)
    matched_spokesperson = check_byline_match(
        content, headline, spokespeople,
        raw_html=raw_html, author_meta=author_meta
    )

    # Client op-ed requires BOTH: op-ed format AND spokesperson as author
    is_client_op_ed = is_op_ed_format and matched_spokesperson is not None

    # Determine article type
    if is_client_op_ed:
        article_type = "client_op_ed"
    elif is_op_ed_format:
        article_type = "external_op_ed"
    else:
        article_type = "standard"

    return {
        "is_op_ed_format": is_op_ed_format,
        "is_client_op_ed": is_client_op_ed,
        "matched_spokesperson": matched_spokesperson,
        "article_type": article_type,
    }


def apply_op_ed_overrides(scores: dict, matched_spokesperson: str) -> dict:
    """Apply scoring overrides for client op-eds."""
    # Auto-max Tier 3 Prominence (5/5)
    if "tier_3_prominence" in scores:
        for factor in scores["tier_3_prominence"]:
            if isinstance(scores["tier_3_prominence"][factor], dict):
                max_val = SCORING_MODEL["tier_3_prominence"]["factors"].get(factor, {}).get("max", 1)
                scores["tier_3_prominence"][factor] = {
                    "score": max_val,
                    "explanation": f"Auto-maxed: Client op-ed (author is the article)"
                }
            else:
                max_val = SCORING_MODEL["tier_3_prominence"]["factors"].get(factor, {}).get("max", 1)
                scores["tier_3_prominence"][factor] = max_val

    # Auto-boost Tier 4 Credibility (8/10)
    if "tier_4_credibility" in scores:
        overrides = {
            "spokesperson_named": {"score": 2.5, "explanation": f"{matched_spokesperson} is the author"},
            "framed_as_expert": {"score": 2, "explanation": "Author position implies expertise"},
            "framed_as_innovator": {"score": 2, "explanation": "Op-ed platform implies thought leadership"},
            "spokesperson_title": {"score": 1.5, "explanation": "Title typically included in op-ed byline"},
        }
        for factor, override in overrides.items():
            if factor in scores["tier_4_credibility"]:
                scores["tier_4_credibility"][factor] = override

    # Ensure op-ed bonus is applied
    if "bonus" in scores:
        if isinstance(scores["bonus"].get("op_ed_by_client"), dict):
            scores["bonus"]["op_ed_by_client"] = {
                "score": 10,
                "explanation": f"Op-ed written by {matched_spokesperson}"
            }
        else:
            scores["bonus"]["op_ed_by_client"] = 10

    return scores


def apply_score_floors(total_score: float, outlet_tier: int, scores: dict,
                       is_client_op_ed: bool, spokespeople: list) -> float:
    """
    Apply minimum score floors based on coverage quality indicators.

    Floors:
    - Tier 1 + client op-ed = min 85 (highest value coverage)
    - Tier 1 + spokesperson quoted + 2+ high messages = min 70
    - Tier 1 + 3+ high messages + positive sentiment = min 72
    - Any outlet + client op-ed + all high messages = min 90
    """
    if not scores:
        return total_score

    # Extract key metrics
    tier_2 = scores.get("tier_2_messaging", {})
    tier_1 = scores.get("tier_1_foundational", {})

    key_messages_high_score = extract_score(tier_2.get("key_messages_high", 0))
    direct_quote_score = extract_score(tier_2.get("direct_quote_included", 0))
    sentiment_score = extract_score(tier_1.get("overall_sentiment", 0))

    # Estimate number of high-priority messages (4 pts each now)
    num_high_messages = key_messages_high_score / 4 if key_messages_high_score else 0

    # Check if spokesperson was quoted (score >= 4 means direct quote)
    spokesperson_quoted = direct_quote_score >= 4

    # Apply floors
    floor = 0

    # Tier 1 + client op-ed = min 85 (highest value coverage)
    if outlet_tier == 1 and is_client_op_ed:
        floor = max(floor, 85)

    # Any outlet + client op-ed + all high messages (3) = min 90
    if is_client_op_ed and num_high_messages >= 3:
        floor = max(floor, 90)

    # Tier 1 + spokesperson quoted + 2+ high messages = min 70
    if outlet_tier == 1 and spokesperson_quoted and num_high_messages >= 2:
        floor = max(floor, 70)

    # Tier 1 + 3+ high messages + positive sentiment (>=5) = min 72
    if outlet_tier == 1 and num_high_messages >= 3 and sentiment_score >= 5:
        floor = max(floor, 72)

    return max(total_score, floor)


def score_article(
    client: anthropic.Anthropic,
    article_content: str,
    article_headline: str,
    outlet_name: str,
    outlet_type: str,
    outlet_tier: int,
    client_name: str,
    industry: str,
    spokespeople: list,
    key_messages_high: list,
    key_messages_medium: list,
    key_messages_low: list,
    competitors: list,
    article_url: str = "",
    use_cache: bool = True,
    raw_html: str = None,
    author_meta: str = None,
) -> dict:
    """
    Score a single article using Claude with the 7-tier model.

    Returns:
        dict with success, scores (detailed tier breakdown), total_score, grade, error
    """
    # Check cache first for consistent scoring
    cache_key = get_cache_key(article_url, client_name, key_messages_high)
    if use_cache and article_url:
        cached = get_cached_score(cache_key)
        if cached:
            return cached

    outlet_tier_points = get_outlet_tier_points(outlet_tier)

    # Detect article type (op-ed, standard, etc.)
    article_type_info = detect_article_type(
        url=article_url,
        content=article_content,
        headline=article_headline,
        spokespeople=spokespeople,
        raw_html=raw_html,
        author_meta=author_meta
    )

    # Format spokespeople for prompt
    spokespeople_str = ", ".join(spokespeople) if spokespeople else "Not specified"

    # Build the prompt
    prompt = SCORING_PROMPT.format(
        client_name=client_name,
        industry=industry,
        spokespeople=spokespeople_str,
        competitors=", ".join(competitors) if competitors else "None specified",
        key_messages_high=format_key_messages(key_messages_high, "high"),
        key_messages_medium=format_key_messages(key_messages_medium, "medium"),
        key_messages_low=format_key_messages(key_messages_low, "low"),
        outlet_name=outlet_name,
        outlet_type=outlet_type,
        tier=outlet_tier,
        outlet_tier_points=outlet_tier_points,
        headline=article_headline,
        content=article_content[:12000],  # Limit content length
        article_type=article_type_info["article_type"],
        is_client_op_ed="YES - Apply op-ed scoring overrides" if article_type_info["is_client_op_ed"] else "NO",
    )

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            temperature=0,  # Deterministic output for consistent scoring
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse JSON response
        response_text = response.content[0].text.strip()

        # Try to extract JSON if wrapped in markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```") and not in_json:
                    in_json = True
                    continue
                if line.startswith("```") and in_json:
                    break
                if in_json:
                    json_lines.append(line)
            response_text = "\n".join(json_lines)

        scores = json.loads(response_text)

        # Apply op-ed overrides if this is a client op-ed
        if article_type_info["is_client_op_ed"]:
            scores = apply_op_ed_overrides(scores, article_type_info["matched_spokesperson"])

        # Calculate total score using the scoring model
        score_result = calculate_total_score(scores)

        # Apply minimum score floors
        final_score = apply_score_floors(
            total_score=score_result["total_score"],
            outlet_tier=outlet_tier,
            scores=scores,
            is_client_op_ed=article_type_info["is_client_op_ed"],
            spokespeople=spokespeople
        )

        # Update grade if floor was applied
        from config import get_score_grade
        final_grade = get_score_grade(final_score)

        result = {
            "success": True,
            "scores": scores,  # Detailed tier-by-tier scores
            "total_score": final_score,
            "tier_scores": score_result["tier_scores"],
            "grade": final_grade,
            "summary": scores.get("summary", ""),
            "key_messages_found": scores.get("key_messages_found", []),
            "competitors_found": scores.get("competitors_found", []),
            "article_type": article_type_info["article_type"],
            "is_client_op_ed": article_type_info["is_client_op_ed"],
            "matched_spokesperson": article_type_info["matched_spokesperson"],
            "error": None,
        }

        # Cache successful result for consistency
        if article_url:
            cache_score(cache_key, result)

        return result

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "scores": None,
            "total_score": 0,
            "tier_scores": None,
            "grade": "N/A",
            "summary": "",
            "error": f"Failed to parse AI response as JSON: {str(e)}",
        }
    except anthropic.APIError as e:
        return {
            "success": False,
            "scores": None,
            "total_score": 0,
            "tier_scores": None,
            "grade": "N/A",
            "summary": "",
            "error": f"API error: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "scores": None,
            "total_score": 0,
            "tier_scores": None,
            "grade": "N/A",
            "summary": "",
            "error": f"Scoring error: {str(e)}",
        }


def lookup_outlet(domain: str, outlets_df) -> dict:
    """Look up outlet information by domain."""
    import pandas as pd

    if outlets_df is None or domain == "":
        return {"name": "Unknown", "tier": 3, "type": "Online", "found": False}

    if not isinstance(outlets_df, pd.DataFrame) or outlets_df.empty:
        return {"name": "Unknown", "tier": 3, "type": "Online", "found": False}

    # Normalize column names
    outlets_df = outlets_df.copy()
    outlets_df.columns = [str(c).strip() for c in outlets_df.columns]
    col_map = {col.lower(): col for col in outlets_df.columns}
    domain_col = col_map.get("domain")

    if domain_col is None:
        return {"name": "Unknown", "tier": 3, "type": "Online", "found": False}

    # Try exact match first
    match = outlets_df[outlets_df[domain_col].str.lower() == domain.lower()]

    if len(match) > 0:
        row = match.iloc[0]
        return {
            "name": row["name"],
            "tier": int(row["tier"]),
            "type": row["type"],
            "impressions": row.get("reach_estimate", 0),
            "found": True,
        }

    # Try partial match
    for _, row in outlets_df.iterrows():
        outlet_domain = str(row[domain_col]).lower()
        if outlet_domain in domain or domain in outlet_domain:
            return {
                "name": row["name"],
                "tier": int(row["tier"]),
                "type": row["type"],
                "impressions": row.get("reach_estimate", 0),
                "found": True,
            }

    return {"name": "Unknown", "tier": 3, "type": "Online", "found": False}
