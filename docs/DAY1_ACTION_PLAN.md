# AutoResume: Day 1 Action Plan (If Implementing)

**Scope:** Tier 1, Scenario A (production-quality refactoring)  
**Timeline:** Day 1 → P0.1 (Models) + Day 2 → P0.2 (Data) + ...  
**Goal:** Complete first refactoring checkpoint by end of Day 1

---

## 📋 DAY 1 CHECKLIST: Implement P0.1 (Models)

### Step 1: Create package structure (15 min)

```bash
cd /Users/zhanshuyi/Downloads/AutoResume

# Create autoresume package
mkdir -p autoresume
mkdir -p autoresume/tests
mkdir -p autoresume/data
mkdir -p autoresume/classifiers
mkdir -p autoresume/services
mkdir -p autoresume/utils

# Create __init__.py files
touch autoresume/__init__.py
touch autoresume/data/__init__.py
touch autoresume/classifiers/__init__.py
touch autoresume/services/__init__.py
touch autoresume/utils/__init__.py
touch autoresume/tests/__init__.py

# Move data files
mkdir -p data
mv Profiles.csv data/
mv ResumeVariants.csv data/
mv QuestionBank.csv data/
mv Applications.csv data/
```

### Step 2: Create `autoresume/models.py` (45 min)

File: `autoresume/models.py`

Content (copy below):

```python
"""Domain models for AutoResume.

All models use dataclasses for automatic __init__, __repr__, __eq__.
Use these instead of dicts for type safety and IDE autocomplete.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from datetime import date


class RoleCategory(Enum):
    """Standardized job role categories (use instead of magic strings)."""
    RISK = "Risk"
    QUANT_EQUITY = "Quant Equity Research"
    BUSINESS_ANALYST = "Business Analyst"
    FPA = "FP&A"
    SWE_QUANT_DEV = "SWE/Quant Dev"
    UNCATEGORIZED = "Uncategorized"


class ApplicationStatus(Enum):
    """Application workflow status."""
    TO_APPLY = "To Apply"
    APPLIED = "Applied"
    OA = "OA"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"


@dataclass
class Resume:
    """Resume variant (e.g., Risk, QuantEquity, BA, FP&A)."""
    id: str
    variant_name: str
    file_path: str
    tags: List[str]
    target_roles: List[str]
    role_category: RoleCategory
    notes: str = ""
    
    def __post_init__(self):
        """Validate file path."""
        if not self.file_path.endswith('.pdf'):
            raise ValueError(f"Resume must be a PDF file, got {self.file_path}")


@dataclass
class Profile:
    """User profile/identity (can have multiple: UCLA address vs. home address)."""
    id: str
    full_legal_name: str
    preferred_name: str
    email: str
    phone: str
    address_line1: str
    city: str
    state: str
    zip_code: str
    country: str
    education: str
    work_authorization: str
    relocation: bool
    start_date: date
    
    # Optional fields
    address_line2: Optional[str] = None
    links: Optional[List[str]] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class Question:
    """Q&A entry (can have short/medium/long versions)."""
    id: str
    question_type: str
    keyword_triggers: List[str]  # e.g., ["authorization", "sponsorship", "visa"]
    short_answer: str           # 1-2 sentences
    medium_answer: str          # 5-7 sentences
    long_answer: str            # 300-500 words
    last_updated: date = field(default_factory=lambda: date.today())


@dataclass
class Application:
    """Job application tracking."""
    id: str
    company: str
    role_title: str
    link: str
    date_found: date
    status: ApplicationStatus
    role_category: Optional[RoleCategory] = None
    resume_id: Optional[str] = None  # FK to Resume
    profile_id: Optional[str] = None  # FK to Profile
    
    # Optional
    date_applied: Optional[date] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None


@dataclass
class ClassificationResult:
    """Result from JD classification."""
    jd_text: str
    role_category: RoleCategory
    confidence_score: float  # 0.0 - 1.0
    suggested_resume: Optional[Resume] = None
    keyword_matches: dict = field(default_factory=dict)  # {category: [keywords]}
    scores: dict = field(default_factory=dict)  # {category: score}
    
    def __post_init__(self):
        """Validate confidence score."""
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError(f"Confidence score must be 0.0-1.0, got {self.confidence_score}")


# Type hints for common operations
ProfileDict = dict
ResumeDict = dict
QuestionDict = dict
ApplicationDict = dict
```

**Steps:**
1. Create file `autoresume/models.py`
2. Copy code above
3. Run basic check: `python3 -c "from autoresume.models import RoleCategory; print(RoleCategory.QUANT_EQUITY)"`

**Expected output:**
```
RoleCategory.QUANT_EQUITY
```

### Step 3: Create `autoresume/utils/constants.py` (10 min)

File: `autoresume/utils/constants.py`

```python
"""Shared constants and defaults."""

from autoresume.models import RoleCategory

# Default sample data values (for testing/demo)
SAMPLE_PROFILES = {
    "p_ucla": {
        "id": "p_ucla",
        "full_legal_name": "Zhou Shuyi",
        "preferred_name": "Shuyi",
        "email": "shuyi.zhou@example.com",
        "phone": "+1-555-0100",
        "address_line1": "123 UCLA Ave",
        "city": "Los Angeles",
        "state": "CA",
        "zip_code": "90095",
        "country": "USA",
        "education": "UCLA - M.S. Financial Engineering",
        "work_authorization": "OPT (F-1) until 2026-08",
        "relocation": True,
        "start_date": "2026-06-01",
    }
}

# Resume variant mapping (for quick lookup)
RESUME_CATEGORIES = {
    RoleCategory.RISK: "ZhouShuyi_Risk_Resume_2026.pdf",
    RoleCategory.QUANT_EQUITY: "ZhouShuyi_QuantEquity_Resume_2026.pdf",
    RoleCategory.BUSINESS_ANALYST: "ZhouShuyi_BA_Resume_2026.pdf",
    RoleCategory.FPA: "ZhouShuyi_FPA_Resume_2026.pdf",
}

# Application status flow
APPLICATION_STATUS_FLOW = [
    "To Apply",
    "Applied",
    "OA",
    "Interview",
    "Offer",
    "Rejected",
]
```

### Step 4: Create `autoresume/tests/test_models.py` (30 min)

File: `autoresume/tests/test_models.py`

```python
"""Unit tests for domain models."""

import pytest
from datetime import date
from autoresume.models import (
    RoleCategory, ApplicationStatus, Resume, Profile, Question, Application, ClassificationResult
)


class TestRoleCategory:
    """Test RoleCategory enum."""
    
    def test_enum_values(self):
        assert RoleCategory.QUANT_EQUITY.value == "Quant Equity Research"
        assert RoleCategory.RISK.value == "Risk"
        assert RoleCategory.BUSINESS_ANALYST.value == "Business Analyst"
    
    def test_enum_count(self):
        # Should have exactly 6 roles
        assert len(RoleCategory) == 6


class TestResume:
    """Test Resume model."""
    
    def test_resume_creation(self):
        resume = Resume(
            id="r1",
            variant_name="Risk",
            file_path="ZhouShuyi_Risk_Resume_2026.pdf",
            tags=["risk", "var"],
            target_roles=["Risk Manager", "Model Risk"],
            role_category=RoleCategory.RISK,
        )
        assert resume.id == "r1"
        assert resume.role_category == RoleCategory.RISK
    
    def test_resume_pdf_validation(self):
        with pytest.raises(ValueError, match="must be a PDF"):
            Resume(
                id="r1",
                variant_name="Risk",
                file_path="resume.docx",  # ← Should fail
                tags=[],
                target_roles=[],
                role_category=RoleCategory.RISK,
            )


class TestProfile:
    """Test Profile model."""
    
    def test_profile_creation(self):
        profile = Profile(
            id="p1",
            full_legal_name="Zhou Shuyi",
            preferred_name="Shuyi",
            email="test@example.com",
            phone="+1-555-0100",
            address_line1="123 Main St",
            city="Los Angeles",
            state="CA",
            zip_code="90001",
            country="USA",
            education="M.S. Financial Engineering",
            work_authorization="OPT",
            relocation=True,
            start_date=date(2026, 6, 1),
        )
        assert profile.full_legal_name == "Zhou Shuyi"
        assert profile.relocation is True


class TestQuestion:
    """Test Question model."""
    
    def test_question_creation(self):
        question = Question(
            id="q1",
            question_type="Work authorization",
            keyword_triggers=["authorization", "visa", "sponsorship"],
            short_answer="F-1 OPT until 2026-08",
            medium_answer="On F-1 OPT until Aug 2026; open to sponsorship.",
            long_answer="I am on F-1 OPT valid until August 2026...",
        )
        assert "authorization" in question.keyword_triggers
        assert len(question.short_answer) < len(question.long_answer)


class TestApplication:
    """Test Application model."""
    
    def test_application_creation(self):
        app = Application(
            id="a1",
            company="ExampleCorp",
            role_title="Quant Researcher",
            link="https://example.com/jobs/123",
            date_found=date(2026, 2, 20),
            status=ApplicationStatus.TO_APPLY,
            role_category=RoleCategory.QUANT_EQUITY,
        )
        assert app.company == "ExampleCorp"
        assert app.status == ApplicationStatus.TO_APPLY


class TestClassificationResult:
    """Test ClassificationResult model."""
    
    def test_classification_result(self):
        result = ClassificationResult(
            jd_text="Build factor models and backtest signals",
            role_category=RoleCategory.QUANT_EQUITY,
            confidence_score=0.85,
        )
        assert result.confidence_score == 0.85
        assert result.role_category == RoleCategory.QUANT_EQUITY
    
    def test_confidence_validation(self):
        with pytest.raises(ValueError, match="0.0-1.0"):
            ClassificationResult(
                jd_text="test",
                role_category=RoleCategory.QUANT_EQUITY,
                confidence_score=1.5,  # ← Invalid
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Step 5: Run tests (10 min)

```bash
cd /Users/zhanshuyi/Downloads/AutoResume

# Install pytest if needed
pip3 install pytest

# Run tests
python3 -m pytest autoresume/tests/test_models.py -v

# Expected output:
# test_models.py::TestRoleCategory::test_enum_values PASSED
# test_models.py::TestRoleCategory::test_enum_count PASSED
# ... (16 tests total, all PASSED)
```

### Step 6: Documentation (10 min)

Update `autoresume/__init__.py`:

```python
"""AutoResume: Semi-automated job application workflow.

This package provides:
- Domain models (Profile, Resume, Question, Application)
- Data layer abstractions (CSV loaders, validators)
- Classifiers (keyword-based, extensible)
- CLI tooling for job description classification
- Application tracking

Quick start:
    from autoresume.models import RoleCategory, Resume
    from autoresume.config import Config
    from autoresume.classifiers.keyword_classifier import KeywordClassifier

    config = Config.from_yaml('config.yaml')
    classifier = KeywordClassifier(config, repo)
    result = classifier.classify("JD text here...")
    print(result.role_category)
"""

__version__ = "0.1.0"
__author__ = "You"
```

---

## ✅ DAY 1 SUCCESS CHECKLIST

- [x] Create `autoresume/` package structure
- [x] Implement `models.py` with all dataclasses
- [x] Implement `utils/constants.py`
- [x] Implement `tests/test_models.py` (16 tests)
- [x] All tests passing
- [x] Type hints enabled

**Result at end of Day 1:**
```
autoresume/
├── __init__.py
├── models.py           ← P0.1 COMPLETE
├── utils/
│   ├── __init__.py
│   └── constants.py
└── tests/
    ├── __init__.py
    └── test_models.py  ← All 16 tests pass ✅
```

**Status:** ✅ P0.1 Complete → Ready for P0.2 (Data Layer)

---

## 🚀 NEXT: DAY 2 PREVIEW (P0.2: Data Layer)

Once P0.1 is complete, Day 2 will implement:

- `data/validators.py` — Pydantic schemas for CSV validation
- `data/loaders.py` — CSV → models transformation
- `data/repository.py` — In-memory query interface
- `tests/test_data_loaders.py` — Integration tests

**Est. Time:** 3-4 hours  
**Dependency:** P0.1 (models) ← completed on Day 1 ✅

---

## 💡 TIPS FOR DAY 1

1. **If stuck on imports:** Make sure you're in the right directory and `__init__.py` files exist
2. **If pytest not found:** Run `pip3 install pytest` before running tests
3. **If type checking issues:** Python 3.7+ supports `from __future__ import annotations`
4. **Commit early:** `git add -A && git commit -m "P0.1: Add domain models"` after tests pass

---

## 📞 SUPPORT

If you hit issues:
1. Check error message carefully
2. Look at test file for expected usage
3. Ensure all imports are correct
4. Verify Python 3.7+ (`python3 --version`)

**Ready to start Day 1? Let me know!**
