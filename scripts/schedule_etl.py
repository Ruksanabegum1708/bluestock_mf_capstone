"""
schedule_etl.py
===============
Schedules automatic NAV fetching from mfapi.in
every weekday at 8:00 PM.

Usage:
    python scripts/schedule_etl.py

Keep this running in background!
"""

import schedule
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

RAW = Path("data/raw")

SCHEMES = [
    {"code": 125497, "name": "SBI_SmallCap"},
    {"code": 119551, "name": "SBI_Bluechip"},
    {"code": 120503, "name": "ICICI_Bluechip"},
    {"code": 118632, "name": "Nippon_LargeCap"},
    {"code": 119092, "name": "Axis_Bluechip"},
    {"code": 120841, "name": "Kotak_Bluechip"},
]

def fetch_nav_job():
    log.info("Starting scheduled NAV fetch...")
    today = datetime.now().strftime("%Y-%m-%d")

    for scheme in SCHEMES:
        url = f"https://api.mfapi.in/mf/{scheme['code']}"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            df   = pd.DataFrame(data["data"])
            df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
            df["date"] = pd.to_datetime(df["date"], dayfirst=True)
            df.insert(0, "scheme_code", scheme["code"])
            df.insert(1, "scheme_name", data["meta"]["scheme_name"])
            path = RAW / f"nav_{scheme['name']}_{scheme['code']}.csv"
            df.to_csv(path, index=False)
            log.info(f"  Saved {scheme['name']}: {len(df)} rows")
        except Exception as e:
            log.error(f"  Failed {scheme['name']}: {e}")

    log.info(f"NAV fetch complete for {today}!")

# Schedule every weekday at 8 PM
schedule.every().monday.at("20:00").do(fetch_nav_job)
schedule.every().tuesday.at("20:00").do(fetch_nav_job)
schedule.every().wednesday.at("20:00").do(fetch_nav_job)
schedule.every().thursday.at("20:00").do(fetch_nav_job)
schedule.every().friday.at("20:00").do(fetch_nav_job)

if __name__ == "__main__":
    log.info("ETL Scheduler started!")
    log.info("Auto-fetching NAV every weekday at 8:00 PM")
    log.info("Press Ctrl+C to stop")
    fetch_nav_job()  # Run once immediately
    while True:
        schedule.run_pending()
        time.sleep(60)