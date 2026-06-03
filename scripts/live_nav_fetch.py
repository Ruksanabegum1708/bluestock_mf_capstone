import requests
import pandas as pd
from pathlib import Path
import time

def fetch_data(url):
    try:
        print(f"Fetching data from: {url}")
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f" Skipping (Status {response.status_code}) → {url}")
            return None
        
        return response.json()

    except requests.exceptions.Timeout:
        print(f" Timeout error → {url}")
        return None

    except requests.exceptions.RequestException as e:
        print(f" Request error → {url} : {e}")
        return None


url = "https://api.mfapi.in/mf/125497"
data = fetch_data(url)

if data:

    meta = data["meta"]

    print("\n── Fund Details ──────────────────────")
    print(f"Fund House   : {meta['fund_house']}")
    print(f"Scheme Name  : {meta['scheme_name']}")
    print(f"Scheme Code  : {meta['scheme_code']}")

    df = pd.DataFrame(data["data"])
    df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df = df.sort_values("date").reset_index(drop=True)

    df.insert(0, "scheme_code", meta["scheme_code"])
    df.insert(1, "scheme_name", meta["scheme_name"])
    df.insert(2, "fund_house",  meta["fund_house"])

    print("\n── DataFrame Info ────────────────────")
    print(f"Shape      : {df.shape}")
    print(f"Date range : {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"Latest NAV : ₹{df['nav'].iloc[-1]:.4f}")
    print("\nFirst 3 rows:")
    print(df.head(3))

    Path("data/raw").mkdir(parents=True, exist_ok=True)

    output_path = "data/raw/nav_hdfc_top100_125497.csv"
    df.to_csv(output_path, index=False)

    print(f"\nSaved → {output_path}")
    print(f"Total rows: {len(df):,}")

else:
    print(" Failed to fetch initial fund")

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
    data = fetch_data(url)

    if data is None:
        print(f"⚠ Skipping {scheme['name']}\n")
        continue

    try:
        df = pd.DataFrame(data["data"])
        df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"], dayfirst=True)
        df = df.sort_values("date").reset_index(drop=True)

        df.insert(0, "scheme_code", data["meta"]["scheme_code"])
        df.insert(1, "scheme_name", data["meta"]["scheme_name"])
        df.insert(2, "fund_house",  data["meta"]["fund_house"])

        print(f"\n✔ {scheme['name']}")
        print(f"  Shape      : {df.shape}")
        print(f"  Date range : {df['date'].min().date()} → {df['date'].max().date()}")
        print(f"  Latest NAV : ₹{df['nav'].iloc[-1]:.4f}")

        path = f"data/raw/nav_{scheme['name']}_{scheme['code']}.csv"
        df.to_csv(path, index=False)

        print(f"  Saved → {path}")

        all_frames.append(df)

    except Exception as e:
        print(f" Error processing {scheme['name']}: {e}")

    time.sleep(1)


if all_frames:

    combined = pd.concat(all_frames, ignore_index=True)
    combined_path = "data/raw/nav_all_5_schemes_combined.csv"
    combined.to_csv(combined_path, index=False)

    print(f"\nCombined CSV saved → {combined_path}")
    print(f"Total rows: {len(combined):,}")

else:
    print("No data to combine")
