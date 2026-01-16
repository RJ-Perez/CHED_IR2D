# AI-Powered FAQ Chatbot with RAG Integration

## Phase 1: Chatbot UI Component & State Foundation ✅
- [x] Create chatbot state with message history, input handling, and UI toggles
- [x] Build floating chatbot button and expandable chat window UI
- [x] Implement message bubbles with user/bot styling and timestamps
- [x] Add typing indicator and loading states
- [x] Integrate chatbot component into main app layout

---

## Phase 2: RAG System & Knowledge Base ✅
- [x] Create documentation knowledge base with app features, guides, and FAQs
- [x] Implement vector-based retrieval system for relevant context matching
- [x] Build context injection system to enhance AI prompts with relevant docs
- [x] Add source citations to bot responses

---

## Phase 3: AI Integration & Human Escalation
- [ ] Integrate Google Gemini AI for response generation with RAG context
- [ ] Implement conversation history for context-aware responses
- [ ] Add human support escalation detection and ticket creation
- [ ] Build escalation confirmation dialog and support queue system

---

# Analytics Route (`/analytics`) - Computation Logic Documentation

## Overview
The Analytics page calculates and displays institutional performance metrics using a weighted scoring system aligned with QS World University Rankings methodology. All computations are performed in `app/states/analytics_state.py` via the `AnalyticsState.on_load()` event handler.

---

## Database Schema & Fields

### Primary Tables

| Table | Purpose |
|-------|---------|
| `institution_scores` | Stores raw metric values per institution |
| `ranking_indicators` | Defines indicator codes and metadata |
| `institutions` | Contains institution profiles and region data |

### Key Database Fields

| Field | Table | Type | Description |
|-------|-------|------|-------------|
| `institution_id` | institution_scores | INTEGER | FK to institutions.id |
| `indicator_id` | institution_scores | INTEGER | FK to ranking_indicators.id |
| `value` | institution_scores | VARCHAR | Raw metric value (numeric as string) |
| `ranking_year` | institution_scores | INTEGER | Assessment year (e.g., 2025) |
| `code` | ranking_indicators | VARCHAR | Indicator identifier (e.g., `academic_reputation`) |
| `region` | institutions | VARCHAR | Institution region for NCR filtering |

### Indicator Codes Reference

| Code | Dimension | Weight in Dimension |
|------|-----------|---------------------|
| `academic_reputation` | Research & Discovery | 60% |
| `citations_per_faculty` | Research & Discovery | 40% |
| `employer_reputation` | Employability | 75% |
| `employment_outcomes` | Employability | 25% |
| `international_research_network` | Global Engagement | 33.3% |
| `international_faculty_ratio` | Global Engagement | 33.3% |
| `international_student_ratio` | Global Engagement | 33.3% |
| `faculty_student_ratio` | Learning Experience | 100% |
| `sustainability_metrics` | Sustainability | 100% |

---

## Mathematical Formulas

### 1. Component Score Calculation

**Formula:**
```
Component_Score = min(100, (Raw_Value / Benchmark) × 100)
```

**Benchmark Values:**

| Metric | Benchmark | Rationale |
|--------|-----------|-----------|
| Academic Reputation | 90.0 | Top-tier university threshold |
| Citations per Faculty | 20.0 | High research impact target |
| Employer Reputation | 90.0 | Industry recognition standard |
| Employment Outcomes | 95.0 | Graduate employment rate target |
| International Research Network | 80.0 | Global collaboration index |
| International Faculty Ratio | 15.0 | % international faculty target |
| International Student Ratio | 10.0 | % international students target |
| Faculty-Student Ratio | 12.0 | Ideal ratio (1:12) |
| Sustainability Metrics | 85.0 | ESG compliance score target |

### 2. Dimension Score Formulas

**Research & Discovery (50% of Overall):**
```
Research_Score = (Academic_Rep_Component × 0.6) + (Citations_Component × 0.4)
```

**Employability & Outcomes (20% of Overall):**
```
Employability_Score = (Employer_Rep_Component × 0.75) + (Employment_Outcomes_Component × 0.25)
```

**Global Engagement (15% of Overall):**
```
Global_Engagement_Score = (Int_Research_Net + Int_Faculty_Ratio + Int_Student_Ratio) / 3
```

**Learning Experience (10% of Overall):**
```
Learning_Experience_Score = Faculty_Student_Ratio_Component
```

**Sustainability (5% of Overall):**
```
Sustainability_Score = Sustainability_Metrics_Component
```

### 3. Overall Readiness Score

**Formula:**
```
Overall_Score = (Research × 0.50) + (Employability × 0.20) + (Global_Engagement × 0.15) + (Learning_Experience × 0.10) + (Sustainability × 0.05)
```

### 4. NCR Average Calculation

**SQL Query:**
```sql
SELECT 
    i.code, 
    AVG(CAST(NULLIF(regexp_replace(s.value, '[^0-9.]', '', 'g'), '') AS FLOAT)) as avg_val
FROM institution_scores s
JOIN ranking_indicators i ON s.indicator_id = i.id
JOIN institutions inst ON s.institution_id = inst.id
WHERE s.ranking_year = 2025 
  AND (inst.region LIKE '%NCR%' OR inst.region = 'NCR (National Capital Region)')
GROUP BY i.code
```

### 5. Variance Calculation

**Formula:**
```
Variance = Your_Score - NCR_Average
```

**Display Logic:**
- `Variance > 0` → Green badge with ↗ trending-up icon
- `Variance < 0` → Red badge with ↘ trending-down icon
- `Variance = 0` → Gray badge with "Avg" label

---

## Backend Controller Mapping

### State Class: `AnalyticsState`
**Location:** `app/states/analytics_state.py`

### Event Handlers

| Handler | Trigger | Purpose |
|---------|---------|---------|
| `on_load()` | Page mount | Fetches data, calculates all scores, triggers AI recommendations |
| `generate_ai_recommendations()` | Called by on_load | Generates AI-powered strategic advice via Google Gemini |

### State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `research_score` | int | Research & Discovery dimension (0-100) |
| `employability_score` | int | Employability dimension (0-100) |
| `global_engagement_score` | int | Global Engagement dimension (0-100) |
| `learning_experience_score` | int | Learning Experience dimension (0-100) |
| `sustainability_score` | int | Sustainability dimension (0-100) |
| `overall_score` | int | Weighted overall readiness (0-100) |
| `performance_summary` | list[dict] | Table data with scores, NCR avg, variance |
| `research_comparison_data` | list[dict] | Bar chart data for research metrics |
| `employability_comparison_data` | list[dict] | Bar chart data for employability metrics |
| `global_engagement_comparison_data` | list[dict] | Bar chart data for global engagement |
| `learning_experience_comparison_data` | list[dict] | Bar chart data for learning experience |
| `sustainability_comparison_data` | list[dict] | Bar chart data for sustainability |
| `ai_recommendations` | list[dict] | AI-generated strategic recommendations |

### Helper Methods

| Method | Parameters | Returns | Purpose |
|--------|------------|---------|---------|
| `_parse_float(value)` | str | float | Safely converts string values to float |
| `_calculate_component_score(value, benchmark)` | float, float | float | Applies benchmark normalization formula |
| `_get_fallback_recommendations(...)` | 5 dimension scores | list[dict] | Rule-based recommendations when AI unavailable |

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        on_load() Event                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Fetch HEI Context from HEIState.selected_hei               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Query institution_scores for selected institution_id       │
│     JOIN ranking_indicators ON indicator_id                     │
│     WHERE ranking_year = 2025                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Query NCR Averages (AVG aggregation by region filter)      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Apply _calculate_component_score() to each raw value       │
│     Formula: min(100, value / benchmark × 100)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Calculate Dimension Scores using weighted formulas         │
│     - Research: 60% Academic Rep + 40% Citations               │
│     - Employability: 75% Employer Rep + 25% Outcomes           │
│     - Global: Average of 3 international metrics               │
│     - Learning: Faculty-Student ratio component                │
│     - Sustainability: Sustainability metrics component         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Calculate Overall Score (weighted sum of 5 dimensions)     │
│     50% Research + 20% Employability + 15% Global +            │
│     10% Learning + 5% Sustainability                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. Build comparison_data arrays for Recharts bar charts       │
│     Each array contains: Your Score, NCR Avg, Target           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. Build performance_summary with variance calculations       │
│     Variance = Your Score - NCR Average                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  9. Trigger generate_ai_recommendations() background task      │
│     → Google Gemini API call with performance context          │
│     → Fallback to rule-based recommendations if API fails      │
└─────────────────────────────────────────────────────────────────┘
```

---

## UI Component Mapping

| UI Component | State Variable | Location |
|--------------|----------------|----------|
| Donut Charts (6) | `overall_score`, `research_score`, etc. | `performance_pie_card()` |
| Summary Table | `performance_summary` | `performance_summary_table()` |
| Research Bar Chart | `research_comparison_data` | `research_chart()` |
| Employability Bar Chart | `employability_comparison_data` | `employability_chart()` |
| Global Engagement Bar Chart | `global_engagement_comparison_data` | `global_engagement_chart()` |
| Learning Experience Bar Chart | `learning_experience_comparison_data` | `learning_experience_chart()` |
| Sustainability Bar Chart | `sustainability_comparison_data` | `sustainability_chart()` |
| AI Recommendations Cards | `ai_recommendations` | Foreach loop in `analytics_content_ui()` |
