"""
email_report.py - Weekly HTML Email Report
Bluestock Fintech Capstone — Bonus B5
Author: Ruksana Begum
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

PROCESSED = Path("data/processed")
REPORTS   = Path("reports")
REPORTS.mkdir(exist_ok=True)

def generate_report():
    df_fund  = pd.read_csv(PROCESSED / "clean_fund_master.csv")
    df_score = pd.read_csv(PROCESSED / "fund_scorecard.csv")
    df_sip   = pd.read_csv(PROCESSED / "clean_monthly_sip_inflows.csv")

    top5 = df_score.nlargest(5, "composite_score")
    if "scheme_name" not in top5.columns:
        top5 = top5.merge(
            df_fund[["amfi_code","scheme_name","fund_house"]],
            on="amfi_code", how="left")
    latest_sip = df_sip["sip_inflow_crore"].iloc[-1]
    today      = datetime.now().strftime("%d %B %Y")

    rows = ""
    for _, row in top5.iterrows():
        name   = str(row.get("scheme_name","N/A"))[:40]
        score  = row.get("composite_score", 0)
        cagr   = row.get("cagr_3yr_pct", 0)
        sharpe = row.get("sharpe_ratio", 0)
        color  = "#1F7A4C" if cagr > 15 else "#C00000"
        rows  += f"""
        <tr>
          <td style="padding:10px;border-bottom:1px solid #eee">{name}</td>
          <td style="padding:10px;border-bottom:1px solid #eee;text-align:center;
              font-weight:bold;color:#003087">{score:.1f}</td>
          <td style="padding:10px;border-bottom:1px solid #eee;text-align:center;
              color:{color}">{cagr:.1f}%</td>
          <td style="padding:10px;border-bottom:1px solid #eee;text-align:center">{sharpe:.2f}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#F5F7FA;margin:0;padding:20px">
<div style="max-width:700px;margin:auto;background:white;border-radius:12px;
     overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1)">

  <div style="background:#003087;padding:30px;text-align:center">
    <h1 style="color:white;margin:0;font-size:22px">Bluestock MF Analytics</h1>
    <p style="color:#00A3E0;margin:8px 0 0">Weekly Report — {today}</p>
  </div>

  <div style="display:flex;padding:20px;gap:10px;background:#F0F4FF">
    <div style="flex:1;background:#003087;padding:15px;border-radius:8px;text-align:center">
      <div style="font-size:20px;font-weight:bold;color:#FFD700">Rs.81L Cr</div>
      <div style="font-size:11px;color:white;margin-top:4px">Industry AUM</div>
    </div>
    <div style="flex:1;background:#0070C0;padding:15px;border-radius:8px;text-align:center">
      <div style="font-size:20px;font-weight:bold;color:#FFD700">Rs.{latest_sip:,.0f} Cr</div>
      <div style="font-size:11px;color:white;margin-top:4px">Latest SIP Inflow</div>
    </div>
    <div style="flex:1;background:#1F7A4C;padding:15px;border-radius:8px;text-align:center">
      <div style="font-size:20px;font-weight:bold;color:#FFD700">26.12 Cr</div>
      <div style="font-size:11px;color:white;margin-top:4px">Total Folios</div>
    </div>
  </div>

  <div style="padding:25px">
    <h2 style="color:#003087;border-bottom:3px solid #003087;padding-bottom:8px">
      Top 5 Funds This Week
    </h2>
    <table style="width:100%;border-collapse:collapse">
      <thead>
        <tr style="background:#003087;color:white">
          <th style="padding:10px;text-align:left">Fund Name</th>
          <th style="padding:10px;text-align:center">Score</th>
          <th style="padding:10px;text-align:center">3yr CAGR</th>
          <th style="padding:10px;text-align:center">Sharpe</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  <div style="padding:25px;background:#F8F9FF">
    <h2 style="color:#003087">Key Insights</h2>
    <ul style="color:#333;line-height:2">
      <li>SBI MF leads with Rs. 12.5 Lakh Crore AUM</li>
      <li>SIP inflows at Rs. {latest_sip:,.0f} Crore this period</li>
      <li>Small Cap funds: 20-23% 3yr CAGR</li>
      <li>75-80% SIP continuity rate maintained</li>
      <li>B30 cities growing 2.5x faster than T30</li>
    </ul>
  </div>

  <div style="background:#003087;padding:20px;text-align:center">
    <p style="color:#00A3E0;margin:0;font-size:12px">
      Bluestock Fintech | Mutual Fund Analytics Platform<br>
      Ruksana Begum — Data Analyst Intern | June 2026
    </p>
  </div>
</div>
</body></html>"""

    out = REPORTS / "weekly_report.html"
    out.write_text(html, encoding="utf-8")
    print(f"HTML report saved: {out}")
    print("Open reports/weekly_report.html in browser to see it!")
    return html

if __name__ == "__main__":
    generate_report()