"""Tests for the embedding-based JD classifier.

The new classifier returns a ClassificationResult dataclass instead of a plain
dict, and uses cosine similarity rather than keyword counts — so we test that
the *semantically* correct category wins, even when the JD uses synonyms or
paraphrased language that the old keyword matcher would have missed.

Run:
    pip install sentence-transformers pytest
    pytest test_classify.py -v

NOTE: The first run downloads the all-MiniLM-L6-v2 model (~80 MB).
Subsequent runs use the cached model and are fast (~1–2 s each).
"""

import pytest
from classify_jd import classify_text, ClassificationResult


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def classify(text: str) -> ClassificationResult:
    """Shorthand using the default local (sbert) backend."""
    return classify_text(text, backend="sbert")


# ---------------------------------------------------------------------------
# Original 3 tests — rewritten to use the new interface
# ---------------------------------------------------------------------------

def test_quant_equity_keywords():
    """Classic keyword-heavy JD — should still route correctly."""
    jd = (
        "We are hiring a researcher to design factor models, backtest signals, "
        "and manage portfolio construction."
    )
    result = classify(jd)
    assert result.role_category == "Quant Equity Research"
    assert result.resume == "ZhouShuyi_QuantEquity_Resume_2026.pdf"


def test_risk_keywords():
    """Classic risk JD — VaR / stress / scenario language."""
    jd = (
        "Responsibilities include VaR calculations, stress testing, scenario analysis "
        "and exposure reporting."
    )
    result = classify(jd)
    assert result.role_category == "Risk"
    assert result.resume == "ZhouShuyi_Risk_Resume_2026.pdf"


def test_ba_keywords():
    """Classic BA JD — stakeholder / dashboard / KPI language."""
    jd = (
        "Work with stakeholders on dashboards, KPI design, SQL and Tableau "
        "for business insights."
    )
    result = classify(jd)
    assert result.role_category == "Business Analyst"


# ---------------------------------------------------------------------------
# New semantic tests — paraphrased JDs with NO direct keyword matches
# ---------------------------------------------------------------------------

def test_quant_equity_semantic():
    """Paraphrased quant equity JD — no classic keywords like 'backtest'."""
    jd = (
        "Join our systematic strategies team to develop return-forecasting models "
        "using alternative datasets and evaluate their performance across different "
        "market regimes. You will work closely with portfolio managers on execution "
        "and capacity analysis."
    )
    result = classify(jd)
    assert result.role_category == "Quant Equity Research", (
        f"Expected Quant Equity Research, got {result.role_category} "
        f"(scores: {result.scores})"
    )


def test_risk_semantic():
    """Paraphrased risk JD — describes the function without naming 'VaR'."""
    jd = (
        "We are looking for a professional to help our firm understand and quantify "
        "the potential losses in our trading book under extreme market conditions. "
        "You will liaise with regulators and produce capital adequacy reports."
    )
    result = classify(jd)
    assert result.role_category == "Risk", (
        f"Expected Risk, got {result.role_category} (scores: {result.scores})"
    )


def test_fpa_semantic():
    """FP&A JD using corporate finance language, no acronyms."""
    jd = (
        "This role partners with business unit leaders to plan the company's annual "
        "spending targets, tracks actual results against those targets, and prepares "
        "monthly presentations for the executive leadership team."
    )
    result = classify(jd)
    assert result.role_category == "FP&A", (
        f"Expected FP&A, got {result.role_category} (scores: {result.scores})"
    )


def test_swe_semantic():
    """SWE JD described as 'platform engineer' — no 'C++' or 'low-latency'."""
    jd = (
        "We need a platform engineer to build and maintain the infrastructure "
        "supporting our trading systems, including real-time data pipelines, "
        "containerised microservices, and cloud-based deployment workflows."
    )
    result = classify(jd)
    assert result.role_category == "SWE/Quant Dev", (
        f"Expected SWE/Quant Dev, got {result.role_category} (scores: {result.scores})"
    )


# ---------------------------------------------------------------------------
# Result structure tests
# ---------------------------------------------------------------------------

def test_result_has_confidence_score():
    jd = "Seeking a quantitative analyst to build and test equity factor models."
    result = classify(jd)
    assert 0.0 <= result.confidence <= 1.0
    assert 0.0 <= result.similarity <= 1.0


def test_all_roles_present_in_scores():
    jd = "Data analyst role requiring SQL and Tableau."
    result = classify(jd)
    expected_roles = {"Risk", "Quant Equity Research", "Business Analyst", "FP&A", "SWE/Quant Dev"}
    assert set(result.scores.keys()) == expected_roles
    assert set(result.confidence_scores.keys()) == expected_roles


def test_confidence_scores_sum_to_one():
    jd = "Looking for a financial modelling expert with Excel and budgeting experience."
    result = classify(jd)
    total = sum(result.confidence_scores.values())
    assert abs(total - 1.0) < 1e-4, f"Confidence scores sum to {total}, expected ~1.0"


def test_best_confidence_matches_role_category():
    """The role with the highest confidence_score should match role_category."""
    jd = "Risk manager needed for market risk monitoring and regulatory reporting."
    result = classify(jd)
    best_role = max(result.confidence_scores, key=result.confidence_scores.get)
    assert best_role == result.role_category


# ---------------------------------------------------------------------------
# Standalone runner (no pytest)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_quant_equity_keywords,
        test_risk_keywords,
        test_ba_keywords,
        test_quant_equity_semantic,
        test_risk_semantic,
        test_fpa_semantic,
        test_swe_semantic,
        test_result_has_confidence_score,
        test_all_roles_present_in_scores,
        test_confidence_scores_sum_to_one,
        test_best_confidence_matches_role_category,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{passed+failed} tests passed")
