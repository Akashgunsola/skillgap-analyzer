
# Autonomous Skill Gap Analyzer & Job Targeting System

## Overview
  
This project is an intelligent, product-oriented system designed to empower job seekers by providing data-driven insights into their career progression. The system helps users:

  - Extract structured skills from their resume
  - Identify jobs where they are strong candidates
  - Analyze skill gaps based on real job requirements
  - Generate an optimized learning roadmap
  - Estimate time-to-employability

Unlike traditional resume matchers, this system models **skill dependencies, transferability, and learning effort**, enabling structured decision-making instead of simple keyword matching.

## Problem Statement
  
Job seekers face major hurdles in an increasingly competitive market:

1.  **Inconsistent Job Descriptions:** Job descriptions are often noisy, inconsistent, and difficult to parse accurately.
2.  **Shallow Matching:** Existing resume matchers rely on basic keyword comparison, leading to poor fit recommendations.
3.  **Inefficient Learning:** Learning recommendations are typically unordered and fail to prioritize high-ROI skills.

## Solution
  
This project directly addresses these issues by:

  - Structuring skills into a hierarchical graph (Skill Ontology).
  - Extracting contextual and implicit skill signals from resumes.
  - Normalizing and weighting job requirements.
  - Ranking jobs by realistic fit probability.
  - Generating prioritized, dependency-aware learning paths.

## Core Features (Phase 1)

### 1. Resume Parsing & Skill Extraction

| Capability               | Description                                        |
| :----------------------: | :------------------------------------------------: |
| **Input Support**        | Handles PDF and plain text resumes.                |
| **Preprocessing**        | Cleans and preprocesses raw resume text for NLP.   |
| **Skill Identification** | Extracts explicit and implicit skills.             |
| **Normalization**        | Normalizes skill aliases (e.g., ReactJS → React).  |
| **Proficiency**          | Estimates proficiency using contextual heuristics. |

**Output Example:**

```json
[
 {
  "skill_id": "python",
  "name": "Python",
  "proficiency": 3,
  "evidence_count": 4
 }
]

````

### 2\. Skill Ontology & Dependency Graph

A structured skill knowledge base that defines the relationships and attributes of skills.

| Attribute               | Purpose                                                    |
| :---------------------: | :--------------------------------------------------------: |
| **Canonical Names**     | Standardized names for all skills.                         |
| **Aliases**             | Maps variations to canonical names.                        |
| **Dependencies**        | Parent-child relationships (e.g., Django requires Python). |
| **Difficulty & Effort** | Defines learning difficulty and estimated learning hours.  |
| **Demand Weight**       | Measures current market demand for the skill.              |

**Example Structure:**

``` 
Programming
└── Python
    ├── Django
    ├── Flask
    └── FastAPI

```

This structure enables advanced features such as Skill Transferability Reasoning and Ordered Learning Path Generation.

### 3\. Job Requirement Extraction

The system transforms raw job descriptions into a normalized, structured model.

| Process Step         | Action                                             |
| :------------------: | :------------------------------------------------: |
| **Text Cleaning**    | Removes boilerplate text and noise.                |
| **Skill Extraction** | Identifies required and preferred skills.          |
| **Weighting**        | Assigns importance weights to each skill.          |
| **Normalization**    | Maps skill mentions to the canonical ontology IDs. |

**Structured Job Model:**

``` json
{
  "title": "Backend Developer",
  "extracted_skills": [
    {"skill_id": "python", "weight": 0.9},
    {"skill_id": "django", "weight": 0.7}
  ]
}

```

### 4\. Job Fit Ranking Engine

Computes an objective, numerical fit score between the user's profile and a target job.

**Fit Score Formula:**  
$$\\text{Fit Score} = \\sum (\\text{job\_skill\_weight} \\times \\min(\\text{user\_proficiency} / \\text{required\_level}, 1))$$

**Output Categories:**

| Category            | Description                                    |
| :-----------------: | :--------------------------------------------: |
| **Strong Match**    | High alignment; immediate candidate.           |
| **Reachable**       | Close fit; typically 1–2 critical skills away. |
| **Low Probability** | Significant skill gap; long-term target.       |

The system provides explainable reasoning for every score.

### 5\. Skill Gap Analysis

Identifies missing skills required for target jobs and ranks them by learning Return on Investment (ROI).

**Gap Score Formula:**  
$$\\text{Gap Score} = \\text{importance\_weight} \\times \\text{difficulty} / \\text{learning\_hours}$$

This calculation ensures the prioritization of:

  - Core, high-impact skills.
  - Time-efficient learning modules.
  - Avoidance of low-impact or obsolete technologies.

### 6\. Skill Roadmap Generator

Creates an optimized, ordered learning plan tailored to the user's gaps and availability.

| Input Parameters | Constraint                                   |
| :--------------: | :------------------------------------------: |
| **Priority**     | Skill Dependency Graph, Gap Scores           |
| **Pacing**       | User weekly availability                     |
| **Duration**     | Skill difficulty and learning hour estimates |

**Example Output:**

| Timeframe | Recommended Learning     | Target Roles         |
| :-------: | :----------------------: | :------------------: |
| Week 1–2  | Advanced Python concepts | Junior Backend roles |
| Week 3–4  | Django fundamentals      | Junior Backend roles |
| Week 5    | REST API design          | Junior Backend roles |

## System Architecture

``` mermaid
graph TD
    A[Resume Input] --> B(Resume Parser);
    B --> C(Skill Extractor);
    C --> D(Skill Normalizer);
    D --> E(User Skill Profile);
    F[Job Description Input] --> G(Job Requirement Extractor);
    E & G --> H(Fit Engine);
    H --> I(Skill Gap Analyzer);
    I --> J(Roadmap Generator);

```

*(Note: The above is a [Mermaid](https://mermaid.js.org/) graph block, a common way to represent diagrams in Markdown files.)*

## Project Structure

``` 
skillgap-analyzer/
│
├── app/
│   ├── main.py                # Application entry point
│   ├── core/                  # Core logic, configurations
│   ├── resume/
│   │   ├── parser.py
│   │   ├── cleaner.py
│   │   ├── extractor.py
│   │   ├── normalizer.py
│   │   └── proficiency.py
│   ├── skills/
│   │   ├── ontology.json      # Skill graph definition
│   │   └── loader.py
│   └── models/
│       └── skill.py           # Pydantic data models
│
├── data/                      # Input/Output directories (e.g., sample resumes)
├── tests/
├── requirements.txt
└── README.md

```

## Technology Stack

### Backend & Core

  - **Language:** Python 3.10+
  - **API Framework (Phase 2):** FastAPI
  - **Data Validation:** Pydantic

### NLP & Processing

  - **Core NLP:** spaCy
  - **Fuzzy Matching:** RapidFuzz
  - **PDF Handling:** pdfplumber

### Data Storage (Planned)

  - **Relational Data:** PostgreSQL
  - **Graph Data (Optional):** Neo4j (for advanced skill graph storage)

## Algorithms & Modeling

### Skill Normalization

  - Uses alias mapping and fuzzy matching to ensure every skill is mapped to a consistent, canonical skill ID.

### Transferability Inference

  - The Skill Ontology defines parent/child chains, allowing the system to grant partial credit or infer prerequisite knowledge.
      - *Example:* Proficiency in Django implies a baseline knowledge of Python.

### Proficiency Estimation

  - A heuristic model estimates user proficiency based on contextual signals:
      - Frequency of skill mention.
      - Contextual verbs (e.g., "Led," "Developed," "Used").
      - Recency signals (future enhancement).

### Learning Optimization

  - Learning recommendations are ranked by their potential impact, considering:
      - Job importance
      - Market demand
      - Learning difficulty
      - Time investment

## Future Enhancements (Phase 2)

  - **Job Aggregation:** Multi-site job posting collection.
  - **Recruiter/HR Discovery:** Features for identifying relevant recruiters and companies.
  - **Market Trend Analysis:** Real-time feedback on emerging or declining skills.
  - **Confidence Modeling:** Uncertainty modeling around proficiency and fit scores.
  - **Semantic Skill Detection:** Embedding-based modeling for detecting implicit skills.
  - **User Interface:** Real-time dashboard and interactive visualization.

## Installation & Execution

### Installation

``` bash
git clone <repo>
cd skillgap-analyzer
pip install -r requirements.txt
python -m spacy download en_core_web_sm

```

### How to Run

``` bash
python app/main.py

```

*Note: Place sample resumes inside the* `data/sample_resumes/` *directory for processing.*

``` 
 
```
