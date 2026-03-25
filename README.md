# APAC Territory Planning
**Optimising sales territory design and uncovering $521M in whitespace ARR across APAC**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![DuckDB](https://img.shields.io/badge/DuckDB-1.0-yellow)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6-orange)
![Plotly](https://img.shields.io/badge/Plotly-5.0-purple)

---

## Business Problem

APAC sales leadership suspected territories were unbalanced but lacked data to act. With 20 reps covering 2,000 accounts across 5 subregions, the question was whether the problem was headcount, coverage design, or both. $521M in estimated ARR sat in accounts that had never been contacted. Without a structured coverage model, high-value Enterprise accounts were being managed by SMB reps while India reps operated at 54% capacity with the lowest attainment in the region.

---

## Key Results

| Finding | Detail | Business Impact |
|---|---|---|
| Territory ARR is unequal | Gini 0.339 — SMB reps hold $48-77M ARR, Enterprise reps only $11-13M | Coverage design problem, not headcount |
| Load is well balanced | Gini 0.071 — reps have similar account counts | Structural imbalance, not effort |
| $521M whitespace ARR untouched | <3.2% TAM penetration in any subregion | Largest growth lever in APAC |
| 300 priority accounts identified | Avg ARR $1.3M — Tier 1 Enterprise whitespace | Immediate AE direct coverage |
| 234 accounts mismatched | Enterprise accounts assigned to SMB reps | Reassignment list produced |
| India under-penetrated | 54-62% load, 6-16% attainment, $16K avg ARR | Different playbook needed |
| Greater China biggest opportunity | 124 Tier 1 accounts, $146M ARR potential | 1 Enterprise hire unlocks $795K |
| Total revenue impact | 7 recommendations across new hires, BDR, nurture | **$4.2M estimated ARR** |

---

## Key Output

**Territory Rebalancing Scorecard** — 234 accounts flagged for reassignment from SMB to Enterprise reps, with recommended rep by subregion. India Enterprise accounts routed to regional overlay reps.

**Whitespace Priority List** — 1,398 unworked accounts tiered into Tier 1 (direct AE), Tier 2 (BDR sequencing), and Tier 3 (marketing nurture). Top 300 Tier 1 accounts flagged as Priority with $397M combined ARR potential.

**Prioritised Action Plan**

| Priority | Action | Impact | Timeframe |
|---|---|---|---|
| 1 | Hire 1 Enterprise rep — Greater China | $795K | Q1 next FY |
| 2 | Deploy overlay reps on top 25 Tier 1 accounts | $160K | Immediate |
| 3 | Hire 1 Mid-Market rep — SEA | $743K | Q1 next FY |
| 4 | Restructure India to BDR + marketing model | $269K | Q2 next FY |
| 5 | Launch Tier 2 BDR sequencing — Greater China + SEA | $1.1M | Q2 next FY |
| 6 | Move Tier 3 accounts to marketing nurture | $917K | Q2 next FY |
| 7 | Redeploy one SEA SMB rep to India | $220K | Q2 next FY |
| | **Total** | **$4.2M** | |

---

## Analytical Approach

**Coverage analysis first.** Before any modelling, the territory universe was mapped — 2,000 accounts, 20 reps, 5 subregions — to establish baseline penetration rates, rep load, and engagement status. This revealed that ANZ and North Asia had 45% whitespace not because of low priority but because rep capacity simply could not cover the account universe.

**Gini coefficient to diagnose the imbalance.** Rather than eyeballing rep performance, the Gini coefficient was used to separate two distinct problems: load distribution (how many accounts each rep carries) vs ARR opportunity distribution (the revenue potential of those accounts). Load Gini of 0.071 confirmed reps were equally utilised. ARR Gini of 0.339 confirmed the opportunity was not equally distributed. The Lorenz curve made this gap visual for executive communication.

**K-means clustering to prioritise whitespace.** With 1,398 unworked accounts and finite rep capacity, not all whitespace is equal. K-means (k=3, validated by elbow method) segmented accounts by estimated ARR, employee band, and segment into three actionable tiers — each mapped to a distinct coverage motion: direct AE, BDR sequencing, or marketing nurture.

**Revenue impact modelling with conversion rate assumptions.** Recommendations were translated into estimated ARR using observed conversion rates from the dataset, adjusted by coverage motion based on B2B SaaS benchmarks. Assumptions are fully documented and conservative — actual rates should be validated against historical CRM data before use in planning.

---

## Technical Decisions

**K-means over rule-based tiering.** A rule-based approach (e.g. ARR > $500K = Tier 1) would require arbitrary thresholds. K-means discovers natural groupings from the data and produces globally consistent tiers — Priority accounts average $1.3-1.4M ARR across all subregions, confirming the clustering is meaningful.

**Active customer filter applied consistently.** 131 churned or expired customers were excluded across all notebooks. All metrics reflect current active revenue only — historical outcomes are not counted as performance.

**Gini implemented manually.** scipy.stats has no Gini function. The coefficient was implemented from first principles using the cumulative distribution formula, then validated against the Lorenz curve visually.

**Randomly assigned recommended reps with documented caveat.** The rebalancing list identifies which accounts need to move, not who they should go to — that is a judgment call for the sales manager. Random assignment within subregion was used as a placeholder with a clear note in the output.

**DuckDB in-memory throughout.** No persistent database files — all SQL runs on DataFrames registered at notebook startup. All queries saved to `sql/` as single source of truth.

---

## Notebooks

| Notebook | Description |
|---|---|
| 01 · Data Profiling | Schema validation, null checks, coverage rates, rep capacity by subregion |
| 02 · Territory Performance | Quota attainment, pipeline coverage, win rate, choropleth maps by country |
| 03 · Whitespace Analysis | Penetration rate, K-means clustering, priority tier assignment |
| 04 · Territory Balancing | Gini coefficient, Lorenz curve, rebalancing simulation, reassignment list |
| 05 · Recommendations | Revenue impact model, prioritised actions, executive memo, KPIs |
| 06 · SQL Analysis | All key metrics reproduced in pure SQL using chained CTEs |

---

## Outputs

| File | Description |
|---|---|
| `outputs/02_quota_attainment.png` | Quota attainment % by rep, sorted descending |
| `outputs/02_arr_by_country.png` | Customer ARR by country — choropleth map |
| `outputs/02_pipeline_by_country.png` | Open pipeline by country — choropleth map |
| `outputs/03_penetration_rate.png` | TAM penetration rate by subregion |
| `outputs/03_elbow_method.png` | K-means elbow chart — inertia vs k |
| `outputs/03_kmeans_scatter.png` | Cluster scatter plot — ARR vs employee band |
| `outputs/03_whitespace_tiers.png` | Whitespace account count by tier and subregion |
| `outputs/04_lorenz_curve.png` | Lorenz curve — load % vs territory ARR |
| `outputs/04_territory_rebalancing.png` | Before vs after load % by rep |
| `outputs/05_revenue_impact.png` | Estimated ARR impact by recommendation |
| `data/processed/rebalancing_list.csv` | 234 accounts flagged for reassignment with recommended rep |
| `data/processed/whitespace_scored.csv` | 1,398 whitespace accounts with tier and priority flag |

---

## KPIs to Track

| Frequency | Metric | Target |
|---|---|---|
| Weekly | Pipeline ARR by subregion | Whitespace outreach generating opportunities |
| Weekly | New accounts contacted from priority list | Reps working Tier 1 accounts |
| Monthly | Rep load % by subregion | Flag <70% or >95% |
| Monthly | Whitespace conversion rate — priority accounts | Tier 1 → pipeline → customer progression |
| Monthly | Territory ARR Gini | Improving toward <0.25 |
| Monthly | Quota attainment by rep and segment | Flag reps below 50% for coaching |
| Quarterly | Penetration rate by subregion | Increasing TAM capture over time |
| Quarterly | Tier 1 account progression | Whitespace → pipeline → customer funnel |
| Quarterly | Territory rebalancing review | Assignments still reflect account value |
| Quarterly | India coverage model effectiveness | BDR + marketing outperforming direct rep baseline |

---

## Stack

Python 3.11 · DuckDB · pandas · scikit-learn · scipy · Plotly · Faker · Jupyter

---

## How to Run

**1. Clone the repo**
```bash
git clone https://github.com/skyvisory/apac-territory-planning.git
cd apac-territory-planning
```

**2. Install dependencies**
```bash
pip install pandas duckdb scikit-learn plotly faker numpy scipy jupyter
```

**3. Generate synthetic data**
```bash
python scripts/generate_data.py
```

**4. Run notebooks in order**
```
notebooks/01_data_profiling.ipynb
notebooks/02_territory_performance.ipynb
notebooks/03_whitespace_analysis.ipynb
notebooks/04_territory_balancing.ipynb
notebooks/05_recommendations.ipynb
notebooks/06_sql_analysis.ipynb
```

---

## Project Structure

```
apac-territory-planning/
├── data/
│   └── raw/                  # Generated by scripts/generate_data.py
├── notebooks/                # Analysis notebooks 01-06
├── outputs/                  # Chart exports (PNG)
├── scripts/
│   └── generate_data.py      # Synthetic data generation
├── sql/                      # SQL query files
└── README.md
```

---

## Portfolio Context

This is the fourth project in a RevOps analytics portfolio, each building a distinct capability across the revenue lifecycle:

| Project | Objective | Key Technique |
|---|---|---|
| 1 · Customer Churn | Predict churn → save revenue | XGBoost, feature importance |
| 2 · Sales Pipeline | Visualise pipeline → close revenue | SQL window functions, Streamlit |
| 3 · SaaS Expansion | Predict expansion → grow revenue | Logistic regression, SHAP |
| **4 · Territory Planning** | **Plan territories → allocate resources** | **K-means, Gini coefficient** |

Territory planning sits at the intersection of data and org design — translating account-level signals into rep coverage decisions that directly affect revenue capacity.

---

*Synthetic data only — no real company information.*
