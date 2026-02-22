#!/usr/bin/env python3
"""Semantic JD classifier using embedding cosine similarity.

Each role category is represented by a rich natural-language anchor description.
The classifier embeds both the JD and every anchor, then picks the closest one
via cosine similarity — no keyword lists, no brittle string matching.

Backends
--------
sentence-transformers (default, local, free):
    pip install sentence-transformers
    Model: all-MiniLM-L6-v2  (~80 MB, ~50 ms/query on CPU)

openai (higher accuracy, requires API key):
    pip install openai
    export OPENAI_API_KEY=sk-...
    python3 classify_jd.py --text "..." --backend openai

Usage
-----
    python3 classify_jd.py --text "job description..."
    python3 classify_jd.py --file path/to/jd.txt
    python3 classify_jd.py --text "..." --json
    python3 classify_jd.py --text "..." --backend openai
    python3 classify_jd.py --text "..." --explain      # show top-3 with scores
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# ---------------------------------------------------------------------------
# Role definitions — each anchor is a paragraph-level description of what
# the role actually does.  Richer text → better embedding geometry.
# ---------------------------------------------------------------------------

@dataclass
class RoleSpec:
    name: str
    resume: str
    anchor: str                        # natural-language role description
    secondary_anchors: List[str] = field(default_factory=list)  # extra context


ROLES: List[RoleSpec] = [
    RoleSpec(
        name="Risk",
        resume="ZhouShuyi_Risk_Resume_2026.pdf",
        anchor=(
            "This role focuses on financial risk management within a bank, asset manager, or "
            "hedge fund. Responsibilities include quantifying market risk using Value-at-Risk "
            "(VaR), Expected Shortfall, and stress testing frameworks. The analyst builds and "
            "validates risk models, monitors portfolio exposure against regulatory limits "
            "(Basel III/IV, FRTB), and produces daily risk reports for senior management. "
            "Strong skills in credit risk, counterparty exposure, scenario analysis, and "
            "liquidity risk are expected. Python or R for data pipelines and risk analytics is "
            "common. The candidate should understand Greeks, sensitivities, PnL attribution, "
            "and communicate findings to trading desks and risk committees."
        ),
        secondary_anchors=[
            "Credit risk, counterparty risk, market risk, operational risk analyst.",
            "Regulatory capital, stress test, CCAR, scenario, limit breach monitoring.",
        ],
    ),

    RoleSpec(
        name="Quant Equity Research",
        resume="ZhouShuyi_QuantEquity_Resume_2026.pdf",
        anchor=(
            "This quantitative research role involves designing systematic investment strategies "
            "for equity markets. The researcher discovers and tests alpha signals using large "
            "financial datasets, implements factor models (value, momentum, quality, low-vol), "
            "and runs rigorous backtests to evaluate signal decay, turnover, and transaction "
            "costs. Portfolio construction techniques such as mean-variance optimization, "
            "risk-factor neutralization, and position sizing are core responsibilities. The "
            "candidate is expected to use Python (pandas, numpy, statsmodels) or MATLAB, work "
            "with tick and alternative data, and collaborate with portfolio managers to deploy "
            "live strategies. Cross-sectional and time-series research methods are standard."
        ),
        secondary_anchors=[
            "Equity long/short, statistical arbitrage, factor investing, alpha generation.",
            "Alternative data, machine learning for return prediction, signal research.",
        ],
    ),

    RoleSpec(
        name="Business Analyst",
        resume="ZhouShuyi_BA_Resume_2026.pdf",
        anchor=(
            "This business analyst or data analyst role bridges business stakeholders and "
            "technical teams. The analyst gathers requirements, documents workflows, and "
            "translates business needs into data solutions. Daily work involves writing SQL "
            "queries against enterprise data warehouses, building dashboards in Tableau, Power "
            "BI, or Looker, and defining KPIs to track operational performance. The candidate "
            "facilitates cross-functional meetings, produces functional specifications, and "
            "works with engineering on data pipelines. Strong communication, structured "
            "problem-solving, and the ability to present data insights to non-technical "
            "audiences are essential. Experience with Agile, JIRA, or product management "
            "workflows is a plus."
        ),
        secondary_anchors=[
            "Data analyst, product analyst, operations analyst, strategy analyst.",
            "Reporting, visualization, insight generation, business intelligence.",
        ],
    ),

    RoleSpec(
        name="FP&A",
        resume="ZhouShuyi_FPA_Resume_2026.pdf",
        anchor=(
            "This Financial Planning & Analysis role sits within corporate finance and owns the "
            "annual budgeting cycle, rolling forecasts, and long-range financial planning. The "
            "analyst builds and maintains complex Excel or Python financial models, performs "
            "variance analysis comparing actuals versus plan, and prepares management reporting "
            "packages for CFO and board-level audiences. Responsibilities include P&L "
            "ownership, headcount planning, and partnering with business unit leaders to "
            "explain drivers of revenue and cost. Strong GAAP knowledge, scenario modeling, "
            "and the ability to distill financial trends into executive-ready presentations are "
            "critical. Exposure to ERP systems (SAP, Oracle, Workday Adaptive) is common."
        ),
        secondary_anchors=[
            "Corporate finance, financial controller, management accounting, budgeting.",
            "Revenue forecast, cost center analysis, P&L, EBITDA, headcount planning.",
        ],
    ),

    RoleSpec(
        name="SWE/Quant Dev",
        resume="ZhouShuyi_SWEQuantDev_Resume_2026.pdf",
        anchor=(
            "This software engineering or quantitative developer role requires building robust, "
            "high-performance systems for financial applications. The engineer designs and "
            "implements trading infrastructure, low-latency execution engines, or data "
            "pipelines in C++, Java, or Python. Responsibilities may include order management "
            "systems, market data feeds, backtesting frameworks, or real-time risk engines. "
            "Strong computer science fundamentals — algorithms, data structures, concurrency, "
            "distributed systems — are expected. The candidate collaborates with quants to "
            "productionize research, optimize compute-intensive code, and maintain system "
            "reliability. Experience with cloud platforms (AWS, GCP), containerization "
            "(Docker, Kubernetes), and CI/CD pipelines is valued."
        ),
        secondary_anchors=[
            "Software engineer, backend engineer, infrastructure, platform engineering.",
            "Systems programming, microservices, API development, database engineering.",
        ],
    ),
]

# ---------------------------------------------------------------------------
# Embedding backends
# ---------------------------------------------------------------------------

def _embed_sbert(texts: List[str]) -> List[List[float]]:
    """Local embeddings via sentence-transformers (no API key needed)."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except ImportError:
        print(
            "sentence-transformers is not installed.\n"
            "Run:  pip install sentence-transformers\n"
            "Or use the OpenAI backend:  --backend openai",
            file=sys.stderr,
        )
        sys.exit(1)

    # Model is cached after first download (~80 MB).
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vecs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return [v.tolist() for v in vecs]


def _embed_openai(texts: List[str]) -> List[List[float]]:
    """Remote embeddings via OpenAI text-embedding-3-small."""
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        print(
            "openai package is not installed.\n"
            "Run:  pip install openai",
            file=sys.stderr,
        )
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print(
            "OPENAI_API_KEY environment variable is not set.\n"
            "Export it or switch to the local backend (default).",
            file=sys.stderr,
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    # Preserve input order.
    ordered = sorted(response.data, key=lambda d: d.index)
    return [d.embedding for d in ordered]


def get_embeddings(texts: List[str], backend: str) -> List[List[float]]:
    if backend == "openai":
        return _embed_openai(texts)
    return _embed_sbert(texts)


# ---------------------------------------------------------------------------
# Cosine similarity
# ---------------------------------------------------------------------------

def _dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(a: List[float]) -> float:
    return math.sqrt(sum(x * x for x in a))


def cosine_similarity(a: List[float], b: List[float]) -> float:
    denom = _norm(a) * _norm(b)
    if denom == 0:
        return 0.0
    return _dot(a, b) / denom


def _softmax(values: List[float], temperature: float = 0.1) -> List[float]:
    """Sharpen the distribution so small similarity differences become clear gaps."""
    scaled = [v / temperature for v in values]
    max_v = max(scaled)
    exps = [math.exp(v - max_v) for v in scaled]
    total = sum(exps)
    return [e / total for e in exps]


# ---------------------------------------------------------------------------
# Core classifier
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    role_category: str
    resume: str
    similarity: float          # raw cosine sim of best match  [0, 1]
    confidence: float          # softmax-normalised probability [0, 1]
    scores: dict               # {role_name: raw cosine sim}
    confidence_scores: dict    # {role_name: softmax probability}


def _build_anchor_texts() -> List[str]:
    """Concatenate primary + secondary anchors into one rich text per role."""
    texts = []
    for role in ROLES:
        parts = [role.anchor] + role.secondary_anchors
        texts.append(" ".join(parts))
    return texts


def classify_text(text: str, backend: str = "sbert") -> ClassificationResult:
    """Embed the JD and find the most similar role category by cosine similarity."""

    anchor_texts = _build_anchor_texts()

    # Embed everything in one batch for efficiency.
    all_texts = anchor_texts + [text]
    all_vecs = get_embeddings(all_texts, backend)

    anchor_vecs = all_vecs[: len(ROLES)]
    jd_vec = all_vecs[-1]

    raw_sims = [cosine_similarity(jd_vec, av) for av in anchor_vecs]
    probs = _softmax(raw_sims)

    scores = {role.name: round(sim, 4) for role, sim in zip(ROLES, raw_sims)}
    confidence_scores = {role.name: round(p, 4) for role, p in zip(ROLES, probs)}

    best_idx = max(range(len(raw_sims)), key=lambda i: raw_sims[i])
    best_role = ROLES[best_idx]

    return ClassificationResult(
        role_category=best_role.name,
        resume=best_role.resume,
        similarity=round(raw_sims[best_idx], 4),
        confidence=round(probs[best_idx], 4),
        scores=scores,
        confidence_scores=confidence_scores,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _confidence_label(confidence: float) -> str:
    if confidence >= 0.80:
        return "HIGH"
    if confidence >= 0.50:
        return "MEDIUM"
    if confidence >= 0.25:
        return "LOW"
    return "AMBIGUOUS"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Semantic JD classifier — embedding cosine similarity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--text", help="Job description text (inline)")
    parser.add_argument("--file", help="Path to a .txt file containing the JD")
    parser.add_argument(
        "--backend",
        choices=["sbert", "openai"],
        default="sbert",
        help="Embedding backend: 'sbert' (local, default) or 'openai' (requires OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON instead of human-readable text",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Show all role scores and confidence values",
    )
    args = parser.parse_args()

    if not args.text and not args.file:
        parser.print_help()
        sys.exit(2)

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        text = args.text

    result = classify_text(text, backend=args.backend)

    if args.json:
        payload = {
            "role_category": result.role_category,
            "resume": result.resume,
            "similarity": result.similarity,
            "confidence": result.confidence,
            "confidence_label": _confidence_label(result.confidence),
            "scores": result.scores,
            "confidence_scores": result.confidence_scores,
        }
        print(json.dumps(payload, indent=2))
        return

    # Human-readable output
    label = _confidence_label(result.confidence)
    print(f"\nRole Category  : {result.role_category}")
    print(f"Resume         : {result.resume}")
    print(f"Similarity     : {result.similarity:.4f}  (raw cosine)")
    print(f"Confidence     : {result.confidence:.1%}  [{label}]")

    if args.explain:
        print("\nAll role scores:")
        sorted_roles = sorted(result.scores.items(), key=lambda x: x[1], reverse=True)
        for role_name, sim in sorted_roles:
            prob = result.confidence_scores[role_name]
            bar = "#" * int(prob * 30)
            print(f"  {role_name:<25} sim={sim:.4f}  conf={prob:.1%}  {bar}")
    print()


if __name__ == "__main__":
    main()
