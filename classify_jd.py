#!/usr/bin/env python3
"""Simple keyword-based JD classifier.

Usage:
  python3 classify_jd.py --text "job description..."
  python3 classify_jd.py --file path/to/jd.txt

Returns a suggested Role Category and Resume Variant filename.
"""
import argparse
import sys

# Keyword map: category -> (keywords list, resume_variant)
KEYWORD_MAP = [
    ("Risk", ["var", "stress", "scenario", "exposure", "limit", "risk report", "basel"], "ZhouShuyi_Risk_Resume_2026.pdf"),
    ("Quant Equity Research", ["factor", "alpha", "backtest", "signal", "portfolio construction", "cross-sectional"], "ZhouShuyi_QuantEquity_Resume_2026.pdf"),
    ("Business Analyst", ["stakeholder", "dashboard", "kpi", "sql", "tableau", "requirements"], "ZhouShuyi_BA_Resume_2026.pdf"),
    ("FP&A", ["budget", "forecast", "variance", "financial model", "planning", "p&l"], "ZhouShuyi_FPA_Resume_2026.pdf"),
    ("SWE/Quant Dev", ["c++", "java", "software", "low-latency", "systems", "engineer"], "ZhouShuyi_BA_Resume_2026.pdf"),
]

def classify_text(text: str):
    t = text.lower()
    scores = {}
    matches = {}
    for category, keywords, resume in KEYWORD_MAP:
        scores[category] = 0
        matches[category] = []
        for k in keywords:
            if k in t:
                scores[category] += 1
                matches[category].append(k)

    # choose highest score
    best = max(scores.items(), key=lambda x: x[1])
    if best[1] == 0:
        return {
            "role_category": "Uncategorized",
            "resume": None,
            "scores": scores,
            "matches": matches,
        }

    role = best[0]
    resume = next(r for c,k,r in KEYWORD_MAP if c==role)
    return {"role_category": role, "resume": resume, "scores": scores, "matches": matches}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="JD text inline")
    parser.add_argument("--file", help="Path to JD text file")
    args = parser.parse_args()

    if not args.text and not args.file:
        print("Provide --text or --file", file=sys.stderr)
        sys.exit(2)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.text

    out = classify_text(text)
    print("Role Category:", out["role_category"]) 
    print("Suggested resume:", out["resume"]) 
    print("Scores:")
    for k,v in out["scores"].items():
        print(f"  {k}: {v}")
    print("Matches (per category):")
    for k,v in out["matches"].items():
        if v:
            print(f"  {k}: {', '.join(v)}")

if __name__ == "__main__":
    main()
