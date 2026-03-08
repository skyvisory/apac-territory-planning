import pandas as pd
import numpy as np
from faker import Faker
import os
import random
from datetime import date, timedelta

fake = Faker()
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── CONFIG ────────────────────────────────────────────────────────────────────

SUBREGIONS = {
    "SEA":           {"countries": ["SG", "ID", "MY", "TH", "PH", "VN"], "n_accounts": 600, "n_reps": 6},
    "Greater China": {"countries": ["CN", "HK", "TW"],                   "n_accounts": 480, "n_reps": 4},
    "North Asia":    {"countries": ["JP", "KR"],                          "n_accounts": 400, "n_reps": 3},
    "India":         {"countries": ["IN"],                                 "n_accounts": 320, "n_reps": 3},
    "ANZ":           {"countries": ["AU", "NZ"],                          "n_accounts": 200, "n_reps": 2},
}

INDUSTRIES = ["SaaS", "Fintech", "E-commerce", "Healthcare", "Manufacturing",
              "Logistics", "Education", "Media", "Retail", "Professional Services"]

EMPLOYEE_BANDS = ["1-50", "51-200", "201-500", "501-2000", "2001+"]

SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]

PRODUCTS = ["Core", "Pro", "Enterprise Suite"]

STAGES = ["Prospecting", "Qualified", "Demo", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]

# ── ACCOUNTS ──────────────────────────────────────────────────────────────────

def make_accounts():
    rows = []
    account_id = 1

    for subregion, cfg in SUBREGIONS.items():
        for _ in range(cfg["n_accounts"]):
            country = random.choice(cfg["countries"])

            # Segment weights vary by subregion (bakes in imbalances)
            if subregion == "India":
                segment = random.choices(SEGMENTS, weights=[0.65, 0.25, 0.10])[0]
            elif subregion == "ANZ":
                segment = random.choices(SEGMENTS, weights=[0.20, 0.45, 0.35])[0]
            elif subregion == "Greater China":
                segment = random.choices(SEGMENTS, weights=[0.25, 0.35, 0.40])[0]
            else:
                segment = random.choices(SEGMENTS, weights=[0.40, 0.35, 0.25])[0]

            # ARR potential by segment
            if segment == "SMB":
                estimated_arr = round(random.uniform(5_000, 50_000), -2)
                employee_band = random.choices(EMPLOYEE_BANDS[:3], weights=[0.5, 0.35, 0.15])[0]
            elif segment == "Mid-Market":
                estimated_arr = round(random.uniform(50_000, 250_000), -2)
                employee_band = random.choices(EMPLOYEE_BANDS[1:4], weights=[0.3, 0.5, 0.2])[0]
            else:
                estimated_arr = round(random.uniform(250_000, 2_000_000), -2)
                employee_band = random.choices(EMPLOYEE_BANDS[2:], weights=[0.2, 0.5, 0.3])[0]

            # is_customer rate varies by subregion
            customer_rates = {
                "SEA": 0.22, "Greater China": 0.15, "North Asia": 0.28,
                "India": 0.10, "ANZ": 0.35
            }
            is_customer = int(random.random() < customer_rates[subregion])

            account_status = random.choices(
                ["Active", "Inactive", "Prospect", "Churned"],
                weights=[0.35, 0.15, 0.40, 0.10]
            )[0]
            if is_customer and account_status == "Prospect":
                account_status = "Active"

            rows.append({
                "account_id":    account_id,
                "company_name":  fake.company(),
                "country":       country,
                "subregion":     subregion,
                "industry":      random.choice(INDUSTRIES),
                "employee_band": employee_band,
                "estimated_arr": estimated_arr,
                "segment":       segment,
                "is_customer":   is_customer,
                "account_status": account_status,
            })
            account_id += 1

    return pd.DataFrame(rows)

# ── REPS ──────────────────────────────────────────────────────────────────────

def make_reps():
    rows = []
    rep_id = 1

    quota_by_segment = {"SMB": 400_000, "Mid-Market": 700_000, "Enterprise": 1_200_000}
    capacity_by_segment = {"SMB": 150, "Mid-Market": 80, "Enterprise": 40}

    for subregion, cfg in SUBREGIONS.items():
        for i in range(cfg["n_reps"]):
            if subregion in ["ANZ", "North Asia"]:
                segment_focus = random.choices(SEGMENTS, weights=[0.1, 0.4, 0.5])[0]
            elif subregion == "India":
                segment_focus = random.choices(SEGMENTS, weights=[0.6, 0.3, 0.1])[0]
            else:
                segment_focus = random.choices(SEGMENTS, weights=[0.35, 0.40, 0.25])[0]

            # North Asia reps get higher quota (JP outperformance)
            quota = quota_by_segment[segment_focus]
            if subregion == "North Asia":
                quota = round(quota * random.uniform(1.1, 1.3), -3)

            rows.append({
                "rep_id":        rep_id,
                "rep_name":      fake.name(),
                "subregion":     subregion,
                "segment_focus": segment_focus,
                "quota_usd":     quota,
                "max_accounts":  capacity_by_segment[segment_focus],
            })
            rep_id += 1

    # 2 regional overlay reps
    for _ in range(2):
        rows.append({
            "rep_id":        rep_id,
            "rep_name":      fake.name(),
            "subregion":     "Regional",
            "segment_focus": "Enterprise",
            "quota_usd":     1_500_000,
            "max_accounts":  25,
        })
        rep_id += 1

    return pd.DataFrame(rows)

# ── ASSIGNMENTS ───────────────────────────────────────────────────────────────

def make_assignments(accounts, reps):
    rows = []
    assignment_id = 1

    rep_lookup = reps[reps["subregion"] != "Regional"].copy()

    # Assign each rep a random target load between 60-95% of max_accounts
    rep_targets = {
        rep_id: int(
            rep_lookup.loc[rep_lookup["rep_id"] == rep_id, "max_accounts"].values[0]
            * random.uniform(0.88, 0.98)
        )
        for rep_id in rep_lookup["rep_id"]
    }
    rep_counts = {rep_id: 0 for rep_id in rep_lookup["rep_id"]}

    # Whitespace config: % of accounts LEFT UNASSIGNED per subregion
    whitespace_rates = {
        "SEA":           0.05,
        "Greater China": 0.15,
        "North Asia":    0.03,
        "India":         0.20,
        "ANZ":           0.02,
    }

    for subregion, grp in accounts.groupby("subregion"):
        sub_reps = rep_lookup[rep_lookup["subregion"] == subregion].copy()
        ws_rate = whitespace_rates.get(subregion, 0.10)

        for _, acc in grp.iterrows():
            if random.random() < ws_rate:
                coverage_status = "Unassigned"
                rep_id = None
                assigned_date = None
                last_activity_date = None
                engagement_status = "No Coverage"
            else:
                # Filter to reps with remaining capacity
                available_reps = sub_reps[
                    sub_reps["rep_id"].apply(lambda x: rep_counts[x] < rep_targets[x])
                ]

                # If no reps have capacity, mark as unassigned
                if available_reps.empty:
                    coverage_status = "Unassigned"
                    rep_id = None
                    assigned_date = None
                    last_activity_date = None
                    engagement_status = "No Coverage"
                else:
                    rep = available_reps.sample(1).iloc[0]
                    rep_id = int(rep["rep_id"])
                    rep_counts[rep_id] += 1
                    assigned_date = fake.date_between(
                        start_date=date(2022, 1, 1), end_date=date(2024, 6, 30)
                    )

                    # India SMB: assigned but never touched
                    if subregion == "India" and acc["segment"] == "SMB" and random.random() < 0.45:
                        last_activity_date = None
                        engagement_status = "Stale"
                        coverage_status = "Assigned"
                    else:
                        last_activity_date = fake.date_between(
                            start_date=assigned_date, end_date=date(2025, 3, 1)
                        )
                        days_since = (date(2025, 3, 1) - last_activity_date).days
                        if days_since < 30:
                            engagement_status = "Active"
                        elif days_since < 90:
                            engagement_status = "Warm"
                        else:
                            engagement_status = "Stale"
                        coverage_status = "Assigned"

            rows.append({
                "assignment_id":      assignment_id,
                "account_id":         int(acc["account_id"]),
                "rep_id":             rep_id,
                "assigned_date":      assigned_date,
                "coverage_status":    coverage_status,
                "last_activity_date": last_activity_date,
                "engagement_status":  engagement_status,
            })
            assignment_id += 1

    return pd.DataFrame(rows)

# ── OPPORTUNITIES ─────────────────────────────────────────────────────────────

def make_opportunities(accounts, assignments):
    rows = []
    opp_id = 1

    prospects = accounts[accounts["is_customer"] == 0].copy()
    assigned = assignments[assignments["rep_id"].notna()].set_index("account_id")

    for _, acc in prospects.iterrows():
        if acc["account_id"] not in assigned.index:
            continue
        if random.random() > 0.45:
            continue

        rep_id = int(assigned.loc[acc["account_id"], "rep_id"])
        n_opps = random.choices([1, 2, 3], weights=[0.65, 0.25, 0.10])[0]

        for _ in range(n_opps):
            created_date = fake.date_between(start_date=date(2023, 1, 1), end_date=date(2025, 1, 1))
            close_date = created_date + timedelta(days=random.randint(30, 180))

            stage = random.choices(STAGES, weights=[0.25, 0.22, 0.18, 0.13, 0.07, 0.05, 0.10])[0]
            win_flag = 1 if stage == "Closed Won" else (0 if stage == "Closed Lost" else None)

            arr_potential = round(acc["estimated_arr"] * random.uniform(0.08, 0.20), -2)

            rows.append({
                "opportunity_id": opp_id,
                "account_id":     int(acc["account_id"]),
                "rep_id":         rep_id,
                "stage":          stage,
                "arr_potential":  arr_potential,
                "created_date":   created_date,
                "close_date":     close_date,
                "win_flag":       win_flag,
            })
            opp_id += 1

    return pd.DataFrame(rows)

# ── CUSTOMERS ─────────────────────────────────────────────────────────────────

def make_customers(accounts, assignments):
    rows = []
    customer_id = 1

    customers = accounts[accounts["is_customer"] == 1].copy()
    assigned = assignments[assignments["rep_id"].notna()].set_index("account_id")

    nrr_bands_by_subregion = {
        "SEA":           ["<90%", "90-100%", "100-110%", ">110%"],
        "Greater China": ["<90%", "90-100%", "100-110%", ">110%"],
        "North Asia":    ["<90%", "90-100%", "100-110%", ">110%"],
        "India":         ["<90%", "90-100%", "100-110%", ">110%"],
        "ANZ":           ["<90%", "90-100%", "100-110%", ">110%"],
    }
    nrr_weights = {
        "SEA":           [0.15, 0.35, 0.30, 0.20],
        "Greater China": [0.20, 0.40, 0.25, 0.15],
        "North Asia":    [0.05, 0.25, 0.40, 0.30],   # JP high performance
        "India":         [0.25, 0.40, 0.25, 0.10],
        "ANZ":           [0.10, 0.30, 0.35, 0.25],
    }

    for _, acc in customers.iterrows():
        rep_id = None
        if acc["account_id"] in assigned.index:
            rep_id = int(assigned.loc[acc["account_id"], "rep_id"])

        contract_start = fake.date_between(start_date=date(2023, 1, 1), end_date=date(2025, 1, 1))
        contract_end = contract_start + timedelta(days=random.choice([365, 730]))
        renewal_flag = int(contract_end > date(2025, 3, 1))

        subregion = acc["subregion"]
        nrr_band = random.choices(nrr_bands_by_subregion[subregion], weights=nrr_weights[subregion])[0]

        arr = round(acc["estimated_arr"] * random.uniform(0.05, 0.15), -2)

        rows.append({
            "customer_id":     customer_id,
            "account_id":      int(acc["account_id"]),
            "rep_id":          rep_id,
            "product":         random.choices(PRODUCTS, weights=[0.40, 0.35, 0.25])[0],
            "arr":             arr,
            "contract_start":  contract_start,
            "contract_end":    contract_end,
            "renewal_flag":    renewal_flag,
            "nrr_band":        nrr_band,
        })
        customer_id += 1

    return pd.DataFrame(rows)

# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating accounts...")
    accounts = make_accounts()
    accounts.to_csv(f"{OUTPUT_DIR}/accounts.csv", index=False)
    print(f"  {len(accounts):,} accounts written")

    print("Generating reps...")
    reps = make_reps()
    reps.to_csv(f"{OUTPUT_DIR}/reps.csv", index=False)
    print(f"  {len(reps):,} reps written")

    print("Generating assignments...")
    assignments = make_assignments(accounts, reps)
    assignments.to_csv(f"{OUTPUT_DIR}/assignments.csv", index=False)
    print(f"  {len(assignments):,} assignments written")

    print("Generating opportunities...")
    opportunities = make_opportunities(accounts, assignments)
    opportunities.to_csv(f"{OUTPUT_DIR}/opportunities.csv", index=False)
    print(f"  {len(opportunities):,} opportunities written")

    print("Generating customers...")
    customers = make_customers(accounts, assignments)
    customers.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
    print(f"  {len(customers):,} customers written")

    print("\nDone. Files in data/raw/:")
    for f in os.listdir(OUTPUT_DIR):
        path = f"{OUTPUT_DIR}/{f}"
        size = os.path.getsize(path)
        print(f"  {f:<25} {size:>8,} bytes")