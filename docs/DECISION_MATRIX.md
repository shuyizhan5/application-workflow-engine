# AutoResume: Decision Matrix & Implementation Priorities

## 1️⃣ PRIORITY MATRIX (Impact vs. Effort)

```
         High Impact
              ▲
              │  P0.2     P0.1
              │ (Data)   (Models)
              │  ★★★      ★★★
              │
    P1.5      │  P0.5    P0.4
    (Stats)   │  (CLI)   (Config)
     ★★       │  ★★      ★★
              │
              │         P0.6
              │        (Tests)
              │         ★★
    Low       │
              └────────────────────▶ Effort
         Low            High

Top-left (High Impact, Low Effort) → DO FIRST
Bottom-right (Low Impact, High Effort) → DO LAST
```

## Effort-Based View (Sorted by ROI)

| Item | Effort | Impact | ROI | Do |
|------|--------|--------|-----|-----|
| **P0.4** Config system | 1-2h | High | ★★★★★ | ✅ YES |
| **P0.1** Models | 2-3h | High | ★★★★★ | ✅ YES |
| **P0.2** Data layer | 3-4h | High | ★★★★ | ✅ YES |
| **P0.5** CLI refactor | 2-3h | Medium | ★★★★ | ✅ YES |
| **P1.3** Question suggester | 2-3h | Medium | ★★★ | 🟡 MAYBE |
| **P1.5** Analytics | 2-3h | Medium | ★★★ | 🟡 MAYBE |
| **P0.3** Classifier interface | 2-3h | Medium | ★★★ | 🟡 MAYBE |
| **P0.6** Tests | 2-3h | Medium | ★★★ | 🟡 MAYBE |
| **P1.1** Confidence scoring | 1-2h | Low | ★★ | ❌ SKIP v1 |
| **P1.6** Status enum | 30m | Low | ★ | ❌ SKIP v1 |

---

## 2️⃣ THREE SCENARIOS

### Scenario A: "I want production-quality, have 1-2 weeks"

**Do:** P0.1 + P0.2 + P0.4 + P0.5 + P0.6 (Tier 1 complete)  
**Skip:** P1.x for now  
**Time:** 12-18 hours over 1-2 weeks  
**Result:** Solid foundation, extensible, testable, configurable

### Scenario B: "I need it done in 1-2 days, minimum viable"

**Do:** P0.1 + P0.2 + P0.4 + P0.5 (skip P0.6 tests)  
**Skip:** All P1.x  
**Time:** 8-12 hours (1-2 days of intensive work)  
**Result:** Refactored, configurable, not fully tested

### Scenario C: "I'm happy with current state, just want incremental improvements"

**Do:** Only P0.4 (config system) + P1.3 (question suggester)  
**Skip:** Major refactoring  
**Time:** 3-5 hours  
**Result:** Remove hardcoding, add one useful feature

---

## 3️⃣ DEPENDENCY GRAPH

```
┌─────────────────────────────────────────────┐
│  P0.1: Models (dataclasses + enums)         │  ← Start here
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    P0.2       P0.4        P0.3
   (Data)     (Config)   (Interface)
    Layer      System     Base Classifier
        │          │          │
        └──────────┼──────────┘
                   ▼
            P0.5: CLI Refactor ← Needs all above
                   │
                   ▼
            P0.6: Tests ← Test all above
                   │
        ┌──────────┼──────────┬──────────┐
        ▼          ▼          ▼          ▼
      P1.1      P1.3       P1.5       P1.6
    (Weights) (Questions) (Stats)    (Enum)
      [P2]

Legend:
[P2] = Can be skipped without breaking anything
```

**Key insight:** P0.1 is the critical dependency for everything else.

---

## 4️⃣ TIME-BASED BREAKDOWN

### If you have 8 hours (1 day)

```
P0.1 Models           2h  [████████  ]
P0.2 Data layer       3h  [████████████        ]
P0.4 Config           1h  [████  ]
P0.5 CLI              2h  [████████  ]
────────────────────────
TOTAL                 8h

Result: Refactored foundation, not fully tested
```

### If you have 16 hours (2 days)

```
P0.1 Models           2-3h [████████  ]
P0.2 Data layer       3-4h [████████████        ]
P0.4 Config           1-2h [████-██  ]
P0.3 Classifier       2-3h [████████  ]
P0.5 CLI              2-3h [████████  ]
P0.6 Tests (partial)  2-3h [████████  ]
────────────────────────
TOTAL                 12-18h

Result: Production-quality Tier 1 foundation
```

### If you have 24 hours (3 days + Tier 2)

```
[All of above 16h work]
P1.3 Question suggester  2-3h [████████  ]
P1.5 Analytics           2-3h [████████  ]
────────────────────────
TOTAL                    20-24h

Result: Tier 1 + key Tier 2 features
```

---

## 5️⃣ MILESTONE CHECKPOINTS

### Checkpoint 1: Models & Data (4-5h in)
- [ ] `models.py` complete (Profile, Resume, Question, Application, RoleCategory enum)
- [ ] `data/validators.py` complete (Pydantic schemas)
- [ ] `data/loaders.py` complete (CSV → models)
- [ ] Basic unit tests passing
- **Status:** ✅ Core abstractions in place

### Checkpoint 2: Config & Classifier (6-8h in)
- [ ] `config.yaml` + `config.py` working
- [ ] `classifiers/base.py` + `keyword_classifier.py` refactored
- [ ] Keyword map loaded from config, not hardcoded
- **Status:** ✅ No hardcoding, pluggable classifiers

### Checkpoint 3: CLI & Tests (12-18h in)
- [ ] `cli.py` with sub-commands, JSON output, logging
- [ ] `__main__.py` entry point working (`python -m autoresume`)
- [ ] Test suite with 70%+ coverage
- **Status:** ✅ Production-ready foundation

### Checkpoint 4: Features (20-24h in, optional)
- [ ] Question suggester working
- [ ] Application analytics dashboard
- [ ] Enhanced documentation
- **Status:** ✅ Rich feature set

---

## 6️⃣ RISK ASSESSMENT

### High Risk (Could block progress)
- ❌ **Merging P0.1 + P0.2 takes longer than expected** → Reduce scope (skip edge cases)
- ❌ **Type annotation rabbit hole** → Use simple types first, add generics later

### Medium Risk (Could slow progress)
- ⚠️ **CSV → models mapping is complex** → Use Pydantic to auto-validate & generate
- ⚠️ **Testing data setup** → Use fixtures from `test/fixtures/`

### Low Risk
- ✅ **Small tweaks to CLI** → Easy to iterate
- ✅ **Config YAML format** → Leverage existing YAML libraries

---

## 7️⃣ SUCCESS CRITERIA (Per Milestone)

### Milestone 1: Models & Data ✅
```python
# Should work
profile = Profile(id="p1", full_legal_name="Zhou Shuyi", ...)
resume = Resume(id="r1", variant_name="Risk", role_category=RoleCategory.RISK, ...)
question = Question(id="q1", question_type="Work authorization", ...)

# Should validate
ProfileSchema().validate({"email": "invalid"})  # Should raise error
```

### Milestone 2: Config ✅
```bash
# Should work
python -c "from autoresume.config import Config; cfg = Config.from_yaml('config.yaml'); print(cfg.user_name)"
# Output: Zhou Shuyi
```

### Milestone 3: CLI ✅
```bash
# Should work
python -m autoresume classify --text "..." --json
# {JSON output}

python -m autoresume --help
# Shows subcommands
```

### Milestone 4: Tests ✅
```bash
pytest autoresume/tests/ -v
# 20+ tests, 70%+ coverage
```

---

## 8️⃣ "MINIMUM VIABLE REFACTOR" (If really pressed for time)

**Goal:** Get 60% of value in 4-5 hours

```
KEEP:
- classify_jd.py (as-is)
- CSV files (as-is)
- Resumes/ folder (as-is)

ADD (minimal):
- config.yaml (just keyword map)
- models.py (domain objects only, no validation)
- .gitignore (new)
- .env.example (new)

REFACTOR (light):
- Move KEYWORD_MAP to config.yaml
- Add 3-4 basic type hints
- Add 1-2 unit tests

Time: 4-5h
Benefit: Remove hardcoding, add basic types
Not production-quality, but cleaner
```

---

## 9️⃣ RECOMMENDED DECISION

**For most users:** Go with **Scenario A** (Tier 1 complete) — 1-2 weeks, production-quality  
**If time-constrained:** Go with **Scenario B** (Tier 1 minus tests) — 1-2 days, still solid  
**If just tinkering:** Go with **Scenario C** (config + question suggester) — few hours, incremental  

---

## 🔟 NEXT STEPS

1. **Pick a scenario** (A, B, C, or "Minimum Viable")
2. **Start with P0.1** (models.py)
3. **I'll implement incrementally** with tests for each step
4. **Review after each checkpoint** (1, 2, 3, 4)

**Ready to start? Let me know your preference!**
