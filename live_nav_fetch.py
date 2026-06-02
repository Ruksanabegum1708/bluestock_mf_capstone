import requests
import pandas as pd
from pathlib import Path

# ── Step 1: Call the API ──────────────────────────
url = "https://api.mfapi.in/mf/125497"
print(f"Fetching data from: {url}")

response = requests.get(url, timeout=15)
response.raise_for_status()

# ── Step 2: Parse JSON ────────────────────────────
data = response.json()

# Print meta info
meta = data["meta"]
print("\n── Fund Details ──────────────────────")
print(f"Fund House   : {meta['fund_house']}")
print(f"Scheme Name  : {meta['scheme_name']}")
print(f"Scheme Code  : {meta['scheme_code']}")

# ── Step 3: Convert to DataFrame ─────────────────
df = pd.DataFrame(data["data"])
df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
df["date"] = pd.to_datetime(df["date"], dayfirst=True)
df = df.sort_values("date").reset_index(drop=True)

# Add scheme info columns
df.insert(0, "scheme_code", meta["scheme_code"])
df.insert(1, "scheme_name", meta["scheme_name"])
df.insert(2, "fund_house",  meta["fund_house"])

# ── Step 4: Print info ────────────────────────────
print("\n── DataFrame Info ────────────────────")
print(f"Shape      : {df.shape}")
print(f"Date range : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"Latest NAV : ₹{df['nav'].iloc[-1]:.4f}")
print(f"\nFirst 3 rows:")
print(df.head(3))

# ── Step 5: Save as CSV ───────────────────────────
Path("data/raw").mkdir(parents=True, exist_ok=True)
output_path = "data/raw/nav_hdfc_top100_125497.csv"
df.to_csv(output_path, index=False)
print(f"\n✅ Saved → {output_path}")
print(f"   Total rows: {len(df):,}")

# ── Task 5: Fetch NAV for 5 Key Schemes ──────────
import time

SCHEMES = [
    {"code": 119551, "name": "SBI_Bluechip"},
    {"code": 120503, "name": "ICICI_Bluechip"},
    {"code": 118632, "name": "Nippon_LargeCap"},
    {"code": 119092, "name": "Axis_Bluechip"},
    {"code": 120841, "name": "Kotak_Bluechip"},
]

all_frames = []

for scheme in SCHEMES:
    url = f"https://api.mfapi.in/mf/{scheme['code']}"
    print(f"\nFetching: {scheme['name']} → {url}")

    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data["data"])
    df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df = df.sort_values("date").reset_index(drop=True)

    df.insert(0, "scheme_code", data["meta"]["scheme_code"])
    df.insert(1, "scheme_name", data["meta"]["scheme_name"])
    df.insert(2, "fund_house",  data["meta"]["fund_house"])

    # Print summary
    print(f"  Shape      : {df.shape}")
    print(f"  Date range : {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"  Latest NAV : ₹{df['nav'].iloc[-1]:.4f}")

    # Save individual CSV
    path = f"data/raw/nav_{scheme['name']}_{scheme['code']}.csv"
    df.to_csv(path, index=False)
    print(f"  ✅ Saved → {path}")

    all_frames.append(df)
    time.sleep(0.5)

# Save combined CSV
combined = pd.concat(all_frames, ignore_index=True)
combined.to_csv("data/raw/nav_all_5_schemes_combined.csv", index=False)
print(f"\n✅ Combined CSV saved → data/raw/nav_all_5_schemes_combined.csv")
print(f"   Total rows: {len(combined):,}")