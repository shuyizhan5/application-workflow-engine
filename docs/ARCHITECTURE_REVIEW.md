# AutoResume: Full Architectural Review & Improvement Roadmap

**Date:** 2026-02-21  
**Project Type:** Personal tooling for semi-automated job application workflow  
**Current State:** MVP with CSV data, basic CLI, espanso snippets

---

## PART 1: CURRENT STATE ANALYSIS

### 1.1 Project Structure (Current)
```
AutoResume/
├── README.md
├── classify_jd.py          # Core logic (monolithic)
├── test_classify.py        # Basic tests
├── Profiles.csv            # Data
├── ResumeVariants.csv      # Data
├── QuestionBank.csv        # Data
├── Applications.csv        # Data
├── espanso/
│   └── snippets.yml
└── Resumes/
    └── 2026_Summer/
        ├── ZhouShuyi_Risk_Resume_2026.pdf
        ├── ZhouShuyi_QuantEquity_Resume_2026.pdf
        ├── ZhouShuyi_BA_Resume_2026.pdf
        └── ZhouShuyi_FPA_Resume_2026.pdf
```

### 1.2 Current Strengths
✅ Clear separation of concerns (data vs. code)  
✅ Simple CLI with file/text input  
✅ Extensible keyword map  
✅ CSV-based is "low friction" for Airtable import  
✅ espanso integration is clean  
✅ Test scaffold exists  

### 1.3 Critical Weaknesses Identified

#### Data Layer Issues
- **No schema validation**: Any malformed CSV silently fails
- **No unique IDs**: Hard to track records across tables or detect duplicates
- **No foreign key relationships**: Manual string-linking (e.g., "Resume variant" field in Applications points to freeform text, not a real key)
- **No normalization**: Address fields duplicated across Profiles; keyword_triggers stored as semicolon-delimited strings
- **CSV scalability**: Reading full CSV on every CLI call; no caching/indexing
- **Data integrity risk**: Manual data entry error-prone (e.g., typo in "QuantEquity" vs "Quant Equity Research")

#### CLI/UX Issues
- **Poor output format**: No JSON/structured output; hard to parse programmatically
- **No logging**: Can't debug failures
- **Hardcoded user name**: `ZhouShuyi_*_Resume_2026.pdf` embedded in classify_jd.py
- **No exit codes**: All paths exit 0 or 2, no granular error handling
- **No verbosity levels**: Can't introspect scoring details without modifying code
- **Single responsibility violated**: classify_jd.py handles parsing, classification, AND formatting

#### Configuration & Hardcoding
- **Keyword map hardcoded**: Changing keywords requires code edit + test update
- **Resume filenames hardcoded**: Not data-driven
- **User profile hardcoded**: No multi-user support
- **Role categories hardcoded**: No way to add new categories without code
- **No .env or config.yaml**: Credentials/paths scattered across files

#### Type Safety & Code Quality
- **No type hints**: Hard to refactor or extend safely
- **Minimal docstrings**: Function purposes unclear
- **No enums**: Role categories are magic strings (Risk vs "Risk" vs "risk")
- **Limited error handling**: FileNotFoundError not caught; unclear what happens on malformed CSV
- **No input validation**: JD text can be empty; no sanitization

#### Testing & Reliability
- **Test coverage: ~10%**: Only classify_text() tested; main() / file I/O untested
- **No integration tests**: CSV parsing not tested
- **No snapshot/regression tests**: No way to catch breaking changes
- **No property-based tests**: Edge cases not explored

#### Architecture & Extensibility
- **Single-file CLI**: Hard to add sub-commands (e.g., `autoresume classify` vs `autoresume suggest` vs `autoresume report`)
- **No plugin system**: Can't add custom classifiers without code changes
- **No data layer abstraction**: CSV handling mixed with logic
- **Missing domain models**: No Enum for RoleCategory, Resume, Profile, Application classes
- **No dependency injection**: Hardcoded KEYWORD_MAP; can't swap classifiers
- **No paging/streaming**: If Questions table grows to 1000+ rows, performance degrades

#### Security & Privacy
- **No PII masking in logs**: If user runs with logging, full personal data exposed
- **No data sanitization**: Could fail if Profile contains special characters
- **No "sample data" mode**: Hard to share project without exposing real contact info
- **No encryption for secrets**: If someone wants to store API keys, they'd go unencrypted
- **Resume path traversal risk**: Could theoretically load `../../../../etc/passwd` if path validation weak (currently mitigated by simple glob, but not robust)

---

## PART 2: REFACTORING STRATEGY & PROPOSED STRUCTURE

### 2.1 New Project Structure (Proposed)

```
AutoResume/
├── README.md                          # User guide
├── ARCHITECTURE_REVIEW.md             # This file
├── setup.py / pyproject.toml          # Package metadata
├── requirements.txt
├── .gitignore
├── .env.example                       # Environment variables template
├── config.example.yaml                # Configuration template
│
├── autoresume/                        # Main package
│   ├── __init__.py
│   ├── __main__.py                    # Entry point for `python -m autoresume`
│   ├── cli.py                         # CLI argument parsing & routing
│   ├── config.py                      # Load config from YAML/env
│   │
│   ├── models.py                      # Domain models (Profile, Resume, RoleCategory, etc.)
│   ├── schemas.py                     # Validation schemas (Pydantic or dataclasses)
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loaders.py                 # CSV/JSON loaders
│   │   ├── validators.py              # Schema validation
│   │   └── repository.py              # In-memory data layer abstraction
│   │
│   ├── classifiers/
│   │   ├── __init__.py
│   │   ├── base.py                    # Abstract Classifier interface
│   │   ├── keyword_classifier.py      # Refactored keyword-based classifier
│   │   └── combined_classifier.py     # (Future) ensemble classifier
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── jd_analyzer.py             # High-level JD analysis service
│   │   ├── profile_matcher.py         # Match JD to Profile/Resume
│   │   ├── question_suggester.py      # Suggest answers from QuestionBank
│   │   └── application_tracker.py     # Application statistics
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logging.py                 # Centralized logging
│   │   ├── sanitizer.py               # PII masking, text sanitization
│   │   └── constants.py               # Shared enums & constants
│   │
│   └── tests/                         # Or use tests/ at root level
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_classifiers.py
│       ├── test_data_loaders.py
│       ├── test_services.py
│       └── fixtures/
│           ├── sample_profiles.csv
│           ├── sample_jds.txt
│           └── expected_outputs.json
│
├── data/                              # Data files (user data)
│   ├── Profiles.csv
│   ├── ResumeVariants.csv
│   ├── QuestionBank.csv
│   └── Applications.csv
│
├── config.yaml                        # Project configuration
├── .env                               # Secrets (NOT in git)
│
└── docs/
    ├── DESIGN.md                      # Design decisions
    ├── SCHEMA.md                      # CSV schema documentation
    └── CONTRIBUTING.md                # Development guide
```

### 2.2 Modularization & Abstraction Plan

#### Problem → Solution

| Problem | Current | Proposed |
|---------|---------|----------|
| Monolithic classifier | `classify_jd.py` | `classifiers/base.py` (interface) + `keyword_classifier.py` (impl) |
| Hardcoded keywords | `KEYWORD_MAP` in code | `config.yaml` or database seed |
| CSV chaos | Direct CSV parsing in main | `data/loaders.py` + `data/repository.py` |
| No validation | Silent failures | `data/validators.py` + Pydantic schemas |
| Magic strings | `"Quant Equity Research"` | `models.RoleCategory` enum |
| All-in-one CLI | `classify_text()` + `main()` | `services/` layer + `cli.py` routing |
| No logging | `print()` statements | `utils/logging.py` + structured logs |

---

## PART 3: DETAILED IMPROVEMENT ROADMAP

### Priority Levels
- **P0 (MVP → Production)**: Must-have for quality release
- **P1 (Enhancement)**: Significantly improve UX/code quality
- **P2 (Nice-to-have)**: Feature completeness; lower urgency

---

### P0: CRITICAL IMPROVEMENTS

#### P0.1: Domain Models & Type Safety
**Effort:** 2–3 hours | **Impact:** High (enables all other refactorings)

Create `autoresume/models.py`:

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import date

class RoleCategory(Enum):
    RISK = "Risk"
    QUANT_EQUITY = "Quant Equity Research"
    BUSINESS_ANALYST = "Business Analyst"
    FPA = "FP&A"
    SWE_QUANT_DEV = "SWE/Quant Dev"
    UNCATEGORIZED = "Uncategorized"

@dataclass
class Resume:
    id: str
    variant_name: str
    file_path: str
    tags: List[str]
    target_roles: List[str]
    role_category: RoleCategory

@dataclass
class Profile:
    id: str
    full_legal_name: str
    preferred_name: str
    email: str
    phone: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    zip_code: str
    country: str
    education: str
    work_authorization: str
    relocation: bool
    start_date: date

@dataclass
class Question:
    id: str
    question_type: str
    keyword_triggers: List[str]
    short_answer: str
    medium_answer: str
    long_answer: str
    last_updated: date

@dataclass
class Application:
    id: str
    company: str
    role_title: str
    link: str
    date_found: date
    date_applied: Optional[date]
    status: str  # Enum: ToApply / Applied / OA / Interview / Offer / Rejected
    resume_id: str  # FK to Resume
    profile_id: str  # FK to Profile
    notes: str
    follow_up_date: Optional[date]
    role_category: RoleCategory

@dataclass
class ClassificationResult:
    jd_text: str
    role_category: RoleCategory
    confidence_score: float  # 0.0–1.0
    suggested_resume: Optional[Resume]
    keyword_matches: dict  # {category: [matched_keywords]}
    scores: dict  # {category: score}
```

**Benefits:**
- Type hints enable IDE autocompletion & catch bugs early
- Enum prevents "Risk" vs "risk" bugs
- Dataclass auto-generates `__init__`, `__repr__`, etc.
- Clear contract for data shape

---

#### P0.2: Data Layer Abstraction & CSV Validation
**Effort:** 3–4 hours | **Impact:** High (decouples data from logic)

Create `autoresume/data/repository.py`:

```python
from typing import List, Dict, Optional
from autoresume.models import Profile, Resume, Question, Application
import csv

class DataRepository:
    """In-memory repository for CSV-backed data. 
    
    Responsibility: Load, validate, and provide query access to data.
    Future: Migrate to SQLite backend without changing interface.
    """
    
    def __init__(self):
        self.profiles: Dict[str, Profile] = {}
        self.resumes: Dict[str, Resume] = {}
        self.questions: Dict[str, Question] = {}
        self.applications: Dict[str, Application] = {}
    
    def load_profiles(self, csv_path: str) -> None:
        """Load Profiles.csv into memory with validation."""
        # Implementation: read CSV, validate each row, populate self.profiles
        pass
    
    def get_profile(self, profile_id: str) -> Optional[Profile]:
        return self.profiles.get(profile_id)
    
    def find_resume_by_category(self, role_category: RoleCategory) -> Optional[Resume]:
        """Find best-matching resume for a role category."""
        for resume in self.resumes.values():
            if resume.role_category == role_category:
                return resume
        return None
    
    def find_questions_by_trigger(self, trigger_keyword: str) -> List[Question]:
        """Find questions matching a keyword trigger."""
        results = []
        for question in self.questions.values():
            if any(trigger_keyword in t for t in question.keyword_triggers):
                results.append(question)
        return results
```

Create `autoresume/schemas.py` (using Pydantic or dataclasses-validation):

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date

class ProfileSchema(BaseModel):
    id: str
    full_legal_name: str
    email: EmailStr
    phone: str
    # ... other fields
    
    @validator('email')
    def validate_email(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Email required')
        return v

class ResumeSchema(BaseModel):
    variant_name: str
    file: str  # Path to PDF
    
    @validator('file')
    def validate_file_path(cls, v):
        if not v.endswith('.pdf'):
            raise ValueError('Must be .pdf file')
        return v
```

**Benefits:**
- Centralized data loading logic
- Validates on load → fail fast
- Easy to add database backend later (swap CSV loader for SQL query)
- Decouples business logic from file format

---

#### P0.3: Refactor classify_jd.py → Classifier Interface
**Effort:** 2–3 hours | **Impact:** Medium (enables new classifiers)

Create `autoresume/classifiers/base.py`:

```python
from abc import ABC, abstractmethod
from autoresume.models import ClassificationResult, RoleCategory

class Classifier(ABC):
    """Abstract base for JD classifiers."""
    
    @abstractmethod
    def classify(self, jd_text: str) -> ClassificationResult:
        """Classify JD text and return result with confidence."""
        pass
```

Create `autoresume/classifiers/keyword_classifier.py`:

```python
from autoresume.classifiers.base import Classifier
from autoresume.models import ClassificationResult, RoleCategory
from autoresume.data.repository import DataRepository
from autoresume.config import Config
from typing import Dict, List

class KeywordClassifier(Classifier):
    """Keyword-based classifier using configurable rules."""
    
    def __init__(self, config: Config, repo: DataRepository):
        self.config = config
        self.repo = repo
        self.keyword_map: Dict[RoleCategory, List[str]] = self._build_keyword_map()
    
    def _build_keyword_map(self) -> Dict[RoleCategory, List[str]]:
        """Load keyword map from config instead of hardcoding."""
        return self.config.classifier.keyword_map
    
    def classify(self, jd_text: str) -> ClassificationResult:
        """Classify JD with confidence scoring."""
        jd_lower = jd_text.lower()
        scores = {}
        matches = {}
        
        for category, keywords in self.keyword_map.items():
            score = sum(1 for kw in keywords if kw in jd_lower)
            scores[category] = score
            matches[category] = [kw for kw in keywords if kw in jd_lower]
        
        # Calculate confidence: max_score / sum(all_scores)
        max_score = max(scores.values()) if scores else 0
        total_score = sum(scores.values())
        confidence = (max_score / total_score) if total_score > 0 else 0.0
        
        if max_score == 0:
            return ClassificationResult(
                jd_text=jd_text,
                role_category=RoleCategory.UNCATEGORIZED,
                confidence_score=0.0,
                suggested_resume=None,
                keyword_matches=matches,
                scores=scores
            )
        
        best_category = max(scores, key=scores.get)
        suggested_resume = self.repo.find_resume_by_category(best_category)
        
        return ClassificationResult(
            jd_text=jd_text,
            role_category=best_category,
            confidence_score=confidence,
            suggested_resume=suggested_resume,
            keyword_matches=matches,
            scores=scores
        )
```

**Benefits:**
- Easy to add new classifiers (ML-based, rule-based with weights, etc.)
- Dependency injection enables testing without real data
- Testable interface

---

#### P0.4: Config System (config.yaml)
**Effort:** 1–2 hours | **Impact:** High (remove hardcoding)

Create `autoresume/config.py`:

```python
from dataclasses import dataclass
from typing import Dict, List
import yaml
import os
from autoresume.models import RoleCategory

@dataclass
class ClassifierConfig:
    keyword_map: Dict[str, List[str]]

@dataclass
class Config:
    user_name: str
    data_dir: str
    resumes_dir: str
    classifier: ClassifierConfig
    
    @staticmethod
    def from_yaml(path: str) -> 'Config':
        """Load config from YAML file."""
        with open(path, 'r') as f:
            raw = yaml.safe_load(f)
        
        # Convert keyword_map keys from strings to RoleCategory enums
        keyword_map = {}
        for role_str, keywords in raw['classifier']['keyword_map'].items():
            try:
                role = RoleCategory[role_str]
                keyword_map[role] = keywords
            except KeyError:
                raise ValueError(f"Unknown role category: {role_str}")
        
        return Config(
            user_name=raw['user_name'],
            data_dir=raw['data_dir'],
            resumes_dir=raw['resumes_dir'],
            classifier=ClassifierConfig(keyword_map=keyword_map)
        )
```

Create `config.example.yaml`:

```yaml
user_name: "Zhou Shuyi"
data_dir: "./data"
resumes_dir: "./Resumes/2026_Summer"

classifier:
  keyword_map:
    RISK: ["var", "stress", "scenario", "exposure", "limit", "risk report", "basel"]
    QUANT_EQUITY: ["factor", "alpha", "backtest", "signal", "portfolio construction"]
    BUSINESS_ANALYST: ["stakeholder", "dashboard", "kpi", "sql", "tableau"]
    FPA: ["budget", "forecast", "variance", "financial model"]
    SWE_QUANT_DEV: ["c++", "java", "low-latency", "systems"]
```

**Benefits:**
- No code changes to add keywords
- Easier to share project without exposing hardcoded data
- Environment-aware (dev vs. prod configs)

---

#### P0.5: Improved CLI with JSON Output & Logging
**Effort:** 2–3 hours | **Impact:** Medium (better UX, machine-parseable)

Create `autoresume/cli.py`:

```python
import argparse
import sys
import json
import logging
from pathlib import Path

from autoresume.config import Config
from autoresume.data.repository import DataRepository
from autoresume.classifiers.keyword_classifier import KeywordClassifier
from autoresume.utils.logging import setup_logging

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autoresume",
        description="Semi-automated job application workflow"
    )
    
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file (default: config.yaml)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (for scripting)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # classify command
    classify_parser = subparsers.add_parser("classify", help="Classify a job description")
    classify_parser.add_argument("--text", help="JD text inline")
    classify_parser.add_argument("--file", help="Path to JD text file")
    
    return parser

def cmd_classify(args, config: Config, repo: DataRepository) -> int:
    """Handle 'classify' subcommand."""
    if not args.text and not args.file:
        logging.error("Must provide --text or --file")
        return 2
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                jd_text = f.read()
        except FileNotFoundError:
            logging.error(f"File not found: {args.file}")
            return 1
    else:
        jd_text = args.text
    
    classifier = KeywordClassifier(config, repo)
    result = classifier.classify(jd_text)
    
    if args.json:
        output = {
            "role_category": result.role_category.value,
            "confidence_score": result.confidence_score,
            "suggested_resume": result.suggested_resume.file_path if result.suggested_resume else None,
            "scores": {k.name: v for k, v in result.scores.items()},
            "matches": {k.name: v for k, v in result.keyword_matches.items()}
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Role Category: {result.role_category.value}")
        print(f"Confidence: {result.confidence_score:.2%}")
        print(f"Suggested Resume: {result.suggested_resume.file_path if result.suggested_resume else 'None'}")
        print("Scores:")
        for k, v in result.scores.items():
            print(f"  {k.name}: {v}")
    
    return 0

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    
    setup_logging(verbose=args.verbose)
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        config = Config.from_yaml(args.config)
    except FileNotFoundError:
        logging.error(f"Config not found: {args.config}")
        return 1
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return 1
    
    repo = DataRepository()
    try:
        repo.load_profiles(f"{config.data_dir}/Profiles.csv")
        repo.load_resumes(f"{config.data_dir}/ResumeVariants.csv")
        repo.load_questions(f"{config.data_dir}/QuestionBank.csv")
        repo.load_applications(f"{config.data_dir}/Applications.csv")
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return 1
    
    if args.command == "classify":
        return cmd_classify(args, config, repo)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Create `autoresume/__main__.py`:

```python
import sys
from autoresume.cli import main

if __name__ == "__main__":
    sys.exit(main())
```

**Usage:**

```bash
# Text input, human-readable output
python -m autoresume classify --text "Build factor models and backtest signals"

# File input, JSON output (for scripting)
python -m autoresume classify --file jd.txt --json

# Verbose logging
python -m autoresume classify --text "..." -v

# Custom config
python -m autoresume --config custom.yaml classify --text "..."
```

**Benefits:**
- Sub-commands extensible (future: `suggest-answers`, `track-applications`, etc.)
- JSON output enables piping to other tools
- Logging for debugging
- Proper exit codes (0=success, 1=error, 2=usage error)
- Graceful error handling

---

#### P0.6: Improved Testing
**Effort:** 2–3 hours | **Impact:** Medium (catch regressions)

Create `autoresume/tests/test_classifiers.py`:

```python
import pytest
from autoresume.classifiers.keyword_classifier import KeywordClassifier
from autoresume.models import RoleCategory
from autoresume.config import Config
from autoresume.data.repository import DataRepository

@pytest.fixture
def mock_config():
    return Config(
        user_name="Test User",
        data_dir="./data",
        resumes_dir="./Resumes",
        classifier=ClassifierConfig(keyword_map={
            RoleCategory.QUANT_EQUITY: ["factor", "backtest", "alpha"],
            RoleCategory.RISK: ["var", "stress", "scenario"],
            RoleCategory.BUSINESS_ANALYST: ["dashboard", "kpi"],
        })
    )

@pytest.fixture
def repo(mock_config):
    repo = DataRepository()
    # Populate with test data
    return repo

def test_classify_quant_equity(repo, mock_config):
    classifier = KeywordClassifier(mock_config, repo)
    result = classifier.classify("We need a researcher to build factors and backtest signals")
    
    assert result.role_category == RoleCategory.QUANT_EQUITY
    assert result.confidence_score > 0
    assert "factor" in result.keyword_matches[RoleCategory.QUANT_EQUITY]

def test_classify_uncategorized(repo, mock_config):
    classifier = KeywordClassifier(mock_config, repo)
    result = classifier.classify("We need a senior manager for operations")
    
    assert result.role_category == RoleCategory.UNCATEGORIZED
    assert result.confidence_score == 0

def test_confidence_score(repo, mock_config):
    classifier = KeywordClassifier(mock_config, repo)
    
    # Many matches → high confidence
    result1 = classifier.classify("factor backtest alpha signal")
    assert result1.confidence_score > 0.5
    
    # Single match → lower confidence
    result2 = classifier.classify("We need someone with factor experience")
    assert result2.confidence_score < result1.confidence_score
```

**Benefits:**
- Regression detection (catch breaking changes)
- Confidence in refactoring
- Edge cases explored

---

### Summary of P0 Effort & Order

| Item | Effort | Dependency |
|------|--------|-----------|
| P0.1: Models | 2-3h | None |
| P0.2: Data layer | 3-4h | P0.1 |
| P0.3: Classifier interface | 2-3h | P0.1, P0.2 |
| P0.4: Config system | 1-2h | P0.1 |
| P0.5: CLI refactor | 2-3h | P0.1, P0.2, P0.3, P0.4 |
| P0.6: Testing | 2-3h | P0.1, P0.2, P0.3 |
| **P0 Total** | **12–18 hours** | — |

**Recommend order:** P0.1 → P0.2 → P0.4 → P0.3 → P0.5 → P0.6

---

### P1: SIGNIFICANT ENHANCEMENTS

#### P1.1: Confidence Scoring & Match Details
**Effort:** 1–2 hours | **Impact:** Medium (better UX for tie-breaking)

- **What:** Weight keywords by importance; penalize generic keywords; bonus for exact phrase matches
- **Implementation:** Extend KeywordClassifier with configurable weights in config.yaml
- **Example:**
  ```yaml
  classifier:
    keyword_weights:
      QUANT_EQUITY:
        - keyword: "factor"
          weight: 2
        - keyword: "backtest"
          weight: 2
        - keyword: "analysis"
          weight: 0.5  # Lower for generic term
  ```

#### P1.2: Schema Normalization & Migration
**Effort:** 3–5 hours | **Impact:** Medium (future-proofs data)

- **What:** Move from CSV → SQLite (optional migration, backwards-compatible)
- **How:** Add `data/migrate.py` to convert CSV → SQLite schema
- **Benefits:** Query language, indexing, ACID transactions, scalability
- **When:** If adding 100+ applications or complex filtering

#### P1.3: Question Bank Auto-Suggestion
**Effort:** 2–3 hours | **Impact:** Medium (saves time on Q&A filling)

- **What:** Given a JD, suggest relevant questions from QuestionBank
- **Implementation:** `services/question_suggester.py`
  ```python
  class QuestionSuggester:
      def suggest(self, jd_text: str, role_category: RoleCategory) -> List[Question]:
          """Suggest questions likely to appear for this role."""
  ```
- **Logic:** Match keywords from QuestionBank against JD; rank by match count

#### P1.4: Duplicate Application Detection
**Effort:** 1–2 hours | **Impact:** Low (nice-to-have, prevents re-applying)

- **What:** Warn if company + role title already in Applications
- **Implementation:** `services/application_tracker.py`
  ```python
  def check_duplicate(company: str, role_title: str) -> bool:
      """Return True if similar application exists."""
  ```

#### P1.5: Basic Application Analytics
**Effort:** 2–3 hours | **Impact:** Medium (motivational insights)

- **What:** Generate stats: "Applied to 23 roles, 5 interviews, 1 offer"
- **Implementation:** `services/application_tracker.py`
  ```python
  def get_stats() -> Dict:
      return {
          "total_applications": 23,
          "by_status": {"To Apply": 10, "Applied": 8, "Interview": 5, "Offer": 1},
          "by_role_category": {"Quant Equity": 12, "Risk": 8, "BA": 3},
          "conversion_rate": 0.22  # Interview / Applied
      }
  ```
- **Usage:** `autoresume stats` → outputs dashboard

#### P1.6: Enum for Application Status
**Effort:** 30 min | **Impact:** Low (prevents typos)

```python
class ApplicationStatus(Enum):
    TO_APPLY = "To Apply"
    APPLIED = "Applied"
    OA = "OA"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
```

---

### P2: NICE-TO-HAVE FEATURES

#### P2.1: Resume Versioning & Tracking
- Store resume edit history; track which version sent to which company
- Implementation: Add `version` and `edited_date` to Resume model; link to Application

#### P2.2: Custom Classifier Plugins
- Allow users to register custom classifiers (e.g., ML-based)
- Implementation: Plugin interface + discovery mechanism

#### P2.3: Airtable API Sync (Optional)
- Bi-directional sync with Airtable (requires user's API key)
- Implementation: `services/airtable_sync.py`
- **Note:** Keep user API key in `.env`, never in git

#### P2.4: Browser Extension (Out of scope for MVP+)
- Right-click on JD → auto-classify + suggest resume
- Requires: Manifest.json, content script, background worker

#### P2.5: DEI Sensitivity & Sample Data Mode
- Add `--sample-data` flag to use anonymized test data (no PII)
- Useful for sharing without exposing personal details
- Implementation: Default to sample data; load real data via flag + env var

---

## PART 4: DETAILED IMPROVEMENT PRIORITIES

### Tier 1: Do First (Biggest Bang for Buck)

| Item | Effort | Impact | Why |
|------|--------|--------|-----|
| P0.1 Models | 2-3h | High | Enables all other work |
| P0.2 Data layer | 3-4h | High | Decouples logic from CSV |
| P0.4 Config | 1-2h | High | Remove hardcoding |
| P0.5 CLI | 2-3h | Medium | Better UX + logging |

**Subtotal: 8–12 hours** → Delivers ~80% of value

### Tier 2: Do Next (Completeness)

| Item | Effort | Impact | Why |
|------|--------|--------|-----|
| P0.3 Classifier interface | 2-3h | Medium | Enables extensibility |
| P0.6 Testing | 2-3h | Medium | Confidence in refactor |
| P1.3 Question suggester | 2-3h | Medium | Saves filling time |
| P1.5 Analytics | 2-3h | Medium | Nice dashboarding |

**Subtotal: 8–12 hours** → Total: 16–24 hours for Tier 1+2

### Tier 3: Nice-to-Have (Future)

- P1.1, P1.2, P1.4, P2.x, P2.4 (browser extension)

---

## PART 5: IMPLEMENTATION CHECKLIST (Tier 1)

- [ ] Create `autoresume/` package structure
- [ ] Implement `models.py` with all dataclasses
- [ ] Implement `schemas.py` with Pydantic validation
- [ ] Implement `data/repository.py` + CSV loaders
- [ ] Implement `config.py` + `config.example.yaml`
- [ ] Refactor `classify_jd.py` → `classifiers/keyword_classifier.py`
- [ ] Implement `cli.py` with sub-commands + JSON output
- [ ] Implement `utils/logging.py`
- [ ] Move CSV files to `data/` folder
- [ ] Update README with new CLI usage
- [ ] Write `setup.py` or `pyproject.toml`
- [ ] Add `.gitignore` for `.env`, `*.pyc`, etc.

---

## PART 6: SECURITY & PRIVACY CHECKLIST

- [ ] Add `.env.example` with no real secrets
- [ ] Add file path validation (prevent `/etc/passwd` access)
- [ ] Add PII masking in logs (sanitize email/phone)
- [ ] Add `--sample-data` flag for sharing
- [ ] Document credential handling (1Password API keys should NOT be in git)
- [ ] Add validation for Resume file paths (must be within `Resumes/` dir)

---

## PART 7: FOLDER STRUCTURE MIGRATION GUIDE

### Before
```
AutoResume/
├── Profiles.csv
├── ResumeVariants.csv
├── QuestionBank.csv
├── Applications.csv
├── classify_jd.py
└── Resumes/2026_Summer/...
```

### After (Tier 1 Complete)
```
AutoResume/
├── setup.py
├── requirements.txt
├── config.example.yaml
├── .gitignore
│
├── autoresume/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── config.py
│   ├── models.py
│   ├── schemas.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loaders.py
│   │   ├── validators.py
│   │   └── repository.py
│   ├── classifiers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── keyword_classifier.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── constants.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_classifiers.py
│       └── fixtures/
│
├── data/
│   ├── Profiles.csv
│   ├── ResumeVariants.csv
│   ├── QuestionBank.csv
│   └── Applications.csv
│
├── config.yaml
├── .env (DO NOT COMMIT)
│
└── docs/
    ├── DESIGN.md
    └── SCHEMA.md
```

---

## PART 8: ESTIMATED TIMELINE (Tier 1 + 2)

| Phase | Items | Effort | Timeline |
|-------|-------|--------|----------|
| Week 1 (Day 1–2) | Tier 1 setup | 10h | 2–3 days |
| Week 1 (Day 3–5) | Tier 1 testing + polish | 6h | 1–2 days |
| Week 2 (Day 6–7) | Tier 2 features | 8h | 2–3 days |
| Week 2 (Day 8) | Documentation + final polish | 4h | 1 day |
| **Total** | **All** | **28h** | **~1.5 weeks** |

---

## PART 9: SUCCESS METRICS (Post-Implementation)

### Code Quality
- ✅ Type hints coverage: >90%
- ✅ Test coverage: >70% (focus on core logic, data loaders)
- ✅ Cyclomatic complexity: All functions <10

### UX
- ✅ CLI has structured output (JSON support)
- ✅ All errors log clearly with actionable messages
- ✅ Execution time < 500ms for typical JD

### Architecture
- ✅ Data layer abstracts CSV; easy to swap to SQLite
- ✅ Classifiers pluggable; easy to add new ones
- ✅ Configuration externalizable
- ✅ No hardcoded user names / paths

### Security
- ✅ No PII leaks in logs
- ✅ File access restricted to `Resumes/` and `data/` directories
- ✅ Secrets never in git

---

## PART 10: NOT DOING (Scope Boundaries)

❌ **Browser extension** — Out of scope for MVP+; different dependency stack  
❌ **Machine learning classifier** — Save for P2; keyword-based sufficient for 80% of cases  
❌ **Airtable sync** — Requires API key management; keep manual for now  
❌ **Cover letter generation** — Separate project; out of scope  
❌ **Job scraping** — Violates ATS terms; users should manually paste JDs  

---

## Conclusion

This project has strong bones (CSV data + keyword classifier) but needs:

1. **Abstraction layers** (data → models → services → CLI)
2. **Configuration externalization** (remove hardcoding)
3. **Type safety & validation** (catch bugs early)
4. **Better CLI & logging** (improve UX)
5. **Test coverage** (confidence in changes)

Implementing **Tier 1 (P0 items)** takes ~10–12 hours and transforms this from "script" → "production-quality personal tool" that you can confidently share & extend.

**Recommend starting with P0.1 → P0.2 → P0.4, then P0.5 & P0.6 in parallel.**

---

**Next step:** Do you want me to start implementing Tier 1 (models, data layer, config)? I can begin immediately and provide incremental PRs/commits.
