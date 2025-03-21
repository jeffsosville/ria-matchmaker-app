import streamlit as st
import pandas as pd

# Sample RIA data
ria_data = pd.DataFrame([
    {
        "name": "Alpha Advisors",
        "aum_millions": 150,
        "state": "NY",
        "performance_fee": True,
        "client_hnw": True,
        "client_institutional": False,
        "services": "retirement, estate planning"
    },
    {
        "name": "Beta Wealth",
        "aum_millions": 75,
        "state": "CA",
        "performance_fee": False,
        "client_hnw": True,
        "client_institutional": True,
        "services": "ESG, crypto, wealth management"
    },
    {
        "name": "Gamma Capital",
        "aum_millions": 200,
        "state": "IL",
        "performance_fee": True,
        "client_hnw": False,
        "client_institutional": True,
        "services": "institutional strategy, hedge funds"
    }
])

# App UI
st.title("RIA Matchmaker")

aum_input = st.number_input("Minimum AUM ($ millions)", value=100)
state_input = st.selectbox("Preferred State", ["", "NY", "CA", "IL"])
fee_preference = st.checkbox("Require performance-based fee model?")
client_type = st.selectbox("You are a:", ["hnw", "institutional"])
interest_input = st.text_input("What services are you looking for?", "estate planning")

# Scoring logic
def score_firm(firm, user):
    score = 0
    if firm["aum_millions"] >= user["min_aum"]:
        score += 25
    if user["state"] == firm["state"]:
        score += 15
    if user["performance_fee_preference"] == firm["performance_fee"]:
        score += 15
    if user["client_type"] == "hnw" and firm["client_hnw"]:
        score += 20
    if user["client_type"] == "institutional" and firm["client_institutional"]:
        score += 20
    if user["interest"].lower() in firm["services"].lower():
        score += 25
    return score

# Handle form
user_input = {
    "min_aum": aum_input,
    "state": state_input,
    "performance_fee_preference": fee_preference,
    "client_type": client_type,
    "interest": interest_input
}

if st.button("Find Matches"):
    ria_data["Match Score"] = ria_data.apply(lambda row: score_firm(row, user_input), axis=1)
    ria_data["Summary"] = ria_data.apply(lambda row: (
        f"{row['name']} is an RIA based in {row['state']} managing ${row['aum_millions']}M. "
        f"They specialize in {row['services']} and "
        f"{'offer' if row['performance_fee'] else 'do not offer'} performance-based fees."
    ), axis=1)

    results = ria_data.sort_values(by="Match Score", ascending=False)[["name", "Match Score", "Summary"]]
    
    st.subheader("Your Matches")
    for _, row in results.iterrows():
        st.markdown(f"**{row['name']}** — Match Score: {row['Match Score']}%")
        st.write(row['Summary'])
        st.markdown("---")
