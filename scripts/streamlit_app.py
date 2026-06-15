"""
streamlit_app.py - Web Dashboard
Bluestock Fintech Capstone — Bonus B2
Author: Ruksana Begum
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

PROCESSED = Path("data/processed")

st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    data = {}
    files = {
        "fund":  "clean_fund_master.csv",
        "nav":   "clean_nav_history.csv",
        "txn":   "clean_investor_transactions.csv",
        "perf":  "clean_scheme_performance.csv",
        "aum":   "clean_aum_by_fund_house.csv",
        "sip":   "clean_monthly_sip_inflows.csv",
        "score": "fund_scorecard.csv",
    }
    for key, fname in files.items():
        path = PROCESSED / fname
        if path.exists():
            data[key] = pd.read_csv(path)
    return data

data = load_data()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Industry Overview",
    "Fund Performance",
    "Investor Analytics",
    "Fund Recommender"
])

if page == "Industry Overview":
    st.title("📊 Industry Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total AUM", "₹81 Lakh Cr", "+15%")
    c2.metric("SIP Inflows", "₹31,002 Cr", "+12%")
    c3.metric("Total Folios", "26.12 Cr", "+8%")
    c4.metric("Active SIPs", "9.35 Cr", "+6%")

    if "aum" in data:
        df = data["aum"]
        agg = df.groupby("fund_house")["aum_lakh_crore"].mean().reset_index()
        fig = px.bar(agg.sort_values("aum_lakh_crore"),
                     x="aum_lakh_crore", y="fund_house",
                     orientation="h",
                     title="AUM by Fund House (Rs Lakh Crore)",
                     color="aum_lakh_crore",
                     color_continuous_scale="Blues")
        st.plotly_chart(fig)

    if "sip" in data:
        df_sip = data["sip"].copy()
        df_sip["month_dt"] = pd.to_datetime(df_sip["month"], errors="coerce")
        df_sip = df_sip.sort_values("month_dt")
        fig2 = px.line(df_sip, x="month_dt", y="sip_inflow_crore",
                       title="Monthly SIP Inflows (Rs Crore)",
                       markers=True, template="plotly_white")
        st.plotly_chart(fig2)

elif page == "Fund Performance":
    st.title("📈 Fund Performance")
    if "perf" in data and "fund" in data:
        df_perf = data["perf"].copy()
        df_fund = data["fund"][["amfi_code","scheme_name",
                                "fund_house","category"]].copy()

        # Check which columns already exist in perf
        extra_cols = [c for c in ["scheme_name","fund_house","category"]
                      if c not in df_perf.columns]
        if extra_cols:
            df = df_perf.merge(
                df_fund[["amfi_code"] + extra_cols],
                on="amfi_code", how="left")
        else:
            df = df_perf.copy()

        # Find actual column names after merge
        name_col = next((c for c in df.columns
                         if "scheme_name" in c), None)
        fh_col   = next((c for c in df.columns
                         if "fund_house" in c), None)
        cat_col  = next((c for c in df.columns
                         if c in ["category","category_x","category_y"]), None)

        c1, c2 = st.columns(2)
        if fh_col:
            fh = ["All"] + sorted(df[fh_col].dropna().unique().tolist())
            sel_fh = c1.selectbox("Fund House", fh)
            if sel_fh != "All":
                df = df[df[fh_col] == sel_fh]

        if cat_col:
            cat = ["All"] + sorted(df[cat_col].dropna().unique().tolist())
            sel_cat = c2.selectbox("Category", cat)
            if sel_cat != "All":
                df = df[df[cat_col] == sel_cat]

        if name_col and "return_3yr_pct" in df.columns:
            fig = px.scatter(df,
                             x="return_3yr_pct",
                             y="std_dev_ann_pct",
                             size="aum_crore",
                             color=cat_col,
                             hover_name=name_col,
                             title="Risk vs Return (Bubble = AUM)")
            st.plotly_chart(fig)

        if "score" in data:
            st.subheader("Fund Scorecard")
            df_sc = data["score"]
            cols  = ["scheme_name","composite_score",
                     "cagr_3yr_pct","sharpe_ratio","alpha"]
            cols  = [c for c in cols if c in df_sc.columns]
            if cols:
                st.dataframe(
                    df_sc[cols].sort_values(
                        "composite_score", ascending=False).head(15))

elif page == "Investor Analytics":
    st.title("👥 Investor Analytics")
    if "txn" in data:
        df = data["txn"].copy()
        c1, c2, c3 = st.columns(3)
        states = ["All"] + sorted(df["state"].dropna().unique().tolist())
        ages   = ["All"] + sorted(df["age_group"].dropna().unique().tolist())
        tiers  = ["All"] + df["city_tier"].dropna().unique().tolist()
        s = c1.selectbox("State", states)
        a = c2.selectbox("Age", ages)
        t = c3.selectbox("City Tier", tiers)
        if s != "All": df = df[df["state"] == s]
        if a != "All": df = df[df["age_group"] == a]
        if t != "All": df = df[df["city_tier"] == t]

        c1, c2 = st.columns(2)
        sd = df.groupby("state")["amount_inr"].sum().reset_index()
        fig1 = px.bar(sd.sort_values("amount_inr"),
                      x="amount_inr", y="state",
                      orientation="h",
                      title="Amount by State",
                      color="amount_inr",
                      color_continuous_scale="Blues")
        c1.plotly_chart(fig1)

        td = df["transaction_type"].value_counts().reset_index()
        td.columns = ["transaction_type", "count"]
        fig2 = px.pie(td,
                      names="transaction_type",
                      values="count",
                      hole=0.4,
                      title="Transaction Type Split")
        c2.plotly_chart(fig2)

elif page == "Fund Recommender":
    st.title("🤖 Fund Recommender")
    risk = st.selectbox("Risk Appetite", ["Low", "Moderate", "High"])
    n    = st.slider("Number of funds", 1, 10, 3)

    if st.button("Get Recommendations"):
        if "perf" in data and "fund" in data:
            df = data["perf"].merge(
                data["fund"][["amfi_code","scheme_name","fund_house",
                              "risk_category","expense_ratio_pct","category"]],
                on="amfi_code", how="left",
                suffixes=("","_fund"))

            name_col = "scheme_name" if "scheme_name" in df.columns else "scheme_name_fund"

            risk_map = {
                "Low"     : ["Low","Moderately Low"],
                "Moderate": ["Moderate","Moderately High"],
                "High"    : ["High","Very High"]
            }
            valid = risk_map.get(risk, ["Moderate"])

            show_cols = [name_col,"fund_house","sharpe_ratio",
                         "return_3yr_pct","expense_ratio_pct","risk_category"]
            show_cols = [c for c in show_cols if c in df.columns]

            risk_col = "risk_category" if "risk_category" in df.columns else "risk_grade"
            if risk_col in df.columns:
                result = (df[df[risk_col].isin(valid)]
                          .nlargest(n, "sharpe_ratio")[show_cols])
            else:
                result = df.nlargest(n, "sharpe_ratio")[show_cols]

            st.success(f"Top {n} funds for {risk} risk:")
            st.dataframe(result)

            fig = px.bar(result,
                         x="sharpe_ratio",
                         y=name_col,
                         orientation="h",
                         title="Recommended Funds by Sharpe Ratio",
                         color="sharpe_ratio",
                         color_continuous_scale="Greens")
            st.plotly_chart(fig)

st.sidebar.markdown("---")
st.sidebar.markdown("**Bluestock Fintech**")
st.sidebar.markdown("Ruksana Begum | June 2026")