# AutoResume: Quick Reference Card

## 🔴 Critical Issues (Fix First)

| Issue | Impact | Fix |
|-------|--------|-----|
| Hardcoded keywords | Can't adapt without code edit | → Move to `config.yaml` |
| No data validation | Silently fails on bad CSV | → Add Pydantic schemas |
| No unique IDs | Can't track records across tables | → Add auto-generated IDs |
| Monolithic classifier | Hard to add new classifiers | → Create interface + plugin system |
| No type hints | Bugs caught late | → Add full type annotations |
| No logging | Can't debug failures | → Add structured logging |

---

## ✅ Tier 1 (12-18h) Must-Do Items

```
P0.1 Create models.py            (2-3h)   ← START HERE
  ├─ RoleCategory enum
  ├─ Profile, Resume, Question, Application dataclasses
  └─ ClassificationResult dataclass

P0.2 Create data/ layer           (3-4h)
  ├─ repository.py (in-memory query interface)
  ├─ loaders.py (CSV → models with validation)
  └─ validators.py (Pydantic schemas)

P0.4 Create config system         (1-2h)
  ├─ config.py (load from config.yaml)
  └─ config.example.yaml (keyword map, paths)

P0.3 Classifier interface         (2-3h)
  ├─ classifiers/base.py (ABC)
  └─ classifiers/keyword_classifier.py (refactored impl)

P0.5 Refactor CLI                 (2-3h)
  ├─ cli.py (sub-commands: classify, suggest, stats)
  ├─ JSON output support
  ├─ Proper error handling + exit codes
  └─ __main__.py (python -m autoresume entry)

P0.6 Add tests                    (2-3h)
  ├─ test_models.py
  ├─ test_classifiers.py
  └─ test_data_loaders.py

💰 TOTAL: 12-18h → Transforms to production-quality tool
```

---

## 🟠 Tier 2 (8-12h) Nice-to-Have

- **P1.1** Confidence scoring (weighted keywords) — 1-2h
- **P1.3** Auto-suggest questions from QuestionBank — 2-3h
- **P1.5** Application analytics dashboard — 2-3h
- **P1.6** Application status enum — 30 min

---

## 📂 Folder Structure (Post-Tier-1)

```
AutoResume/
├── autoresume/           ← Main package
│   ├── cli.py
│   ├── models.py
│   ├── config.py
│   ├── data/
│   ├── classifiers/
│   ├── services/
│   ├── utils/
│   └── tests/
├── data/                 ← Move CSVs here
│   ├── Profiles.csv
│   ├── ResumeVariants.csv
│   ├── QuestionBank.csv
│   └── Applications.csv
├── Resumes/2026_Summer/  ← Keep as-is
├── config.yaml           ← New
├── .env.example          ← New
├── .gitignore            ← New
├── setup.py              ← New
└── requirements.txt      ← New
```

---

## 🎯 Before & After (CLI)

### Before
```bash
python3 classify_jd.py --text "..." 
# Output: Unstructured text, no logging, hardcoded user name
```

### After
```bash
# Same usage, better output
python -m autoresume classify --text "..." --json
# {
#   "role_category": "Quant Equity Research",
#   "confidence_score": 0.75,
#   "suggested_resume": "ZhouShuyi_QuantEquity_Resume_2026.pdf",
#   "scores": { ... }
# }

# New features
python -m autoresume suggest-answers --role "Quant Equity"
python -m autoresume analytics
```

---

## 🔒 Security Wins

- ✅ File path validation (prevent `/etc/passwd` access)
- ✅ PII masking in logs (sanitize email/phone)
- ✅ `.env.example` (no secrets in git)
- ✅ `--sample-data` mode (share without exposing personal info)

---

## 💾 Data Integrity Wins

- ✅ Typed models (RoleCategory enum instead of "Risk" vs "risk")
- ✅ Unique IDs for all records (track FK relationships)
- ✅ Validation at load time (fail fast on bad CSV)
- ✅ Pluggable data layer (easy to migrate CSV → SQLite later)

---

## 🚀 Recommendation

**Start with P0.1** (models.py):
1. Define all dataclasses (Profile, Resume, Question, Application, RoleCategory)
2. Then build data layer (P0.2)
3. Then config system (P0.4)
4. Then refactor CLI (P0.5)
5. Add tests (P0.6)

**Expected outcome:** By EOW, have production-quality foundation ready for features.

---

## 📚 Full Details

- **Executive Summary:** `ARCHITECTURE_SUMMARY.md`
- **Detailed Analysis:** `ARCHITECTURE_REVIEW.md` (1200+ lines, all 8 requirements covered)

---

**Status:** ✅ Architecture Review Complete | **Next:** Decision on implementation scope
