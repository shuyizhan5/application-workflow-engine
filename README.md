
AutoResume

AutoResume is a lightweight application management system designed to streamline job applications.

The current version is an MVP focused on organizing resume variants, managing common application responses, classifying job descriptions, and tracking submissions.

This project prioritizes simplicity and iterative improvement over complex infrastructure.

---

## Overview

AutoResume helps with:

* Managing multiple resume versions
* Organizing frequently used application responses
* Classifying job descriptions by role category
* Tracking application status
* Reducing repetitive manual work during job applications

It is intended as a local productivity tool, not a production SaaS system.

---

## Project Structure

```
AutoResume/
│
├── data/
│   ├── Profiles.csv
│   ├── ResumeVariants.csv
│   ├── QuestionBank.csv
│   └── Applications.csv
│
├── Resumes/
│   └── 2026_Summer/
│
├── classify_jd.py
├── test_classify.py
│
├── espanso/
│   └── snippets.yml
│
└── docs/
```

---

## Current Features (MVP)

* Keyword-based job description classifier
* CSV-driven resume variant management
* Structured question bank (short / medium / long responses)
* Application tracking template
* Optional espanso integration for fast text expansion
* CLI-based classification tool

---

## Quick Start

### 1. Prepare Data

Import the CSV files under `data/` into:

* Airtable
* Excel
* Google Sheets
* Or any structured data tool

### 2. Add Resume Files

Place your actual resume PDFs in:

```
Resumes/2026_Summer/
```

Update the `File` field in `ResumeVariants.csv` to match the correct filenames.

### 3. Run the JD Classifier

```
python3 classify_jd.py --text "We are hiring a Quant Equity Researcher to build factor models."
```

Output includes:

* Suggested role category
* Recommended resume file

---

## Technology Stack

* Python 3
* CSV-based data storage
* Rule-based keyword classification
* Optional espanso text expansion

No database. No web interface. No external dependencies required for MVP.

---

## Project Status

Stage: Functional MVP

Completed:

* Data structure templates
* Basic classification logic
* CLI testing script
* Architecture review documentation

Planned Improvements:

* Modular refactor
* Typed domain models
* Improved testing coverage
* Config-driven keyword system
* Optional SQLite migration

---

## Design Principles

* Keep it simple
* Local-first
* Iterative improvement
* Extendable architecture

This project is intentionally minimal and designed to evolve over time.

---

## Intended Use Case

AutoResume is useful if you:

* Apply to multiple role categories
* Maintain different resume versions
* Reuse structured application responses
* Want a systematic way to track applications
* Prefer lightweight tooling over complex platforms

---

## Disclaimer

This repository contains sample data only.
No personal or sensitive information is included.
Users are responsible for managing their own data securely.

