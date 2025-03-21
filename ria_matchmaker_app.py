import streamlit as st
import pandas as pd

@st.cache_data
def load_ria_data():
    df = pd.read_csv("IA_ADV_Base_A_20250201_20250228.csv", encoding="ISO-8859-1")

    df = df.rename(columns={
        "1A": "firm_name",
        "1D": "sec_reg_number",
        "1F1-State": "state",
        "8C1": "performance_fee",
        "5D1k": "client_hnw",
        "5D1m": "client_institutional",
        "1J-Phone": "phone",
        "1J-Email": "email"
    })

    df["performance_fee"] = df["performance_fee"].astype(str).str.strip().str.upper() == "Y"
    df["client_hnw"] = df["client_hnw"].fillna(0).astype(bool)
    df["client_institutional"] = df["client_institutional"].fillna(0).astype(bool)

    df["aum_millions"] = 0
    df["services"] = "general wealth management"

    df = df[[
        "firm_name", "state", "performance_fee", "client_hnw",
        "client_institutional", "aum_millions", "services",
        "email", "phone"
    ]]
    return df[df["firm_name"].notnull()]

ria_data = load_ria_data()

st.title("RIA Matchmaker")
st.caption(f"{len(ria_data)} investment advisers loaded from SEC data.")

aum_input = st.number_input("Minimum AUM ($ millions)", value=100)
state_input = st.selectbox("Preferred State", ["All States"] + sorted(ria_data["state"].dropna().unique()))
fee_preference = st.checkbox("Require performance-based fee model?")
client_type = st.selectbox("You are a:", ["hnw", "institutional"])
interest_input = st.text_input("What services are you looking for?", "estate planning")

def score_firm(firm, user):
    score = 0
    if firm["aum_millions"] >= user["min_aum"]:
        score += 25
    if user["state"] == "All States" or user["state"] == firm["state"]:
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

user_input = {
    "min_aum": aum_input,
    "state": state_input,
    "performance_fee_preference": fee_preference,
    "client_type": client_type,
    "interest": interest_input
}

if st.button("Find Matches"):
    filtered_data = ria_data[
        (ria_data["aum_millions"] >= user_input["min_aum"]) &
        ((user_input["state"] == "All States") | (ria_data["state"] == user_input["state"])) &
        ((user_input["performance_fee_preference"] == ria_data["performance_fee"]) | (not user_input["performance_fee_preference"])) &
        ((user_input["client_type"] == "hnw" and ria_data["client_hnw"]) | (user_input["client_type"] == "institutional" and ria_data["client_institutional"])) &
        (ria_data["services"].str.contains(user_input["interest"], case=False, na=False))
    ]

    filtered_data["Match Score"] = filtered_data.apply(lambda row: score_firm(row, user_input), axis=1)
    filtered_data["Summary"] = filtered_data.apply(lambda row: (
        f"{row['firm_name']} is based in {row['state']}, offering {row['services']}. "
        f"They {'do' if row['performance_fee'] else 'do not'} charge performance-based fees and "
        f"serve {'high-net-worth' if row['client_hnw'] else 'institutional' if row['client_institutional'] else 'general'} clients."
    ), axis=1)

    results = filtered_data.sort_values(by="Match Score", ascending=False)[[
        "firm_name", "Match Score", "Summary", "email", "phone"
    ]]

    st.subheader("Your Matches")
    for _, row in results.iterrows():
        st.markdown(f"**{row['firm_name']}** — Match Score: {row['Match Score']}%")
        st.write(row['Summary'])
        st.markdown(f"📧 **Email**: {row.get('email', 'N/A')}")
        st.markdown(f"📞 **Phone**: {row.get('phone', 'N/A')}")
        st.markdown("---")
