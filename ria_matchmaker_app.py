import streamlit as st
import pandas as pd

# Load the combined dataset
@st.cache_data
def load_data():
    df = pd.read_csv("ria_data_with_bonus_firms.csv")
    return df[df["firm_name"].notnull()]

ria_data = load_data()

st.title("RIA Matchmaker")
st.caption(f"{len(ria_data)} investment advisers loaded.")

aum_input = st.number_input("Minimum AUM ($ millions)", value=0)
state_input = st.selectbox("Preferred State", ["Any"] + sorted(ria_data["state"].dropna().unique()))
fee_preference = st.checkbox("Require performance-based fee model?")
client_type = st.selectbox("You are a:", ["Any", "High-net-worth", "Institutional"])
interest_input = st.text_input("What services are you looking for?", "")

def score_firm(firm, user):
    score = 0
    if firm["aum_millions"] >= user["min_aum"]:
        score += 25
    if user["state"] == "Any" or user["state"] == firm["state"]:
        score += 15
    if user["performance_fee_preference"] == firm["performance_fee"]:
        score += 15
    if user["client_type"] == "High-net-worth" and firm["client_hnw"]:
        score += 20
    if user["client_type"] == "Institutional" and firm["client_institutional"]:
        score += 20
    if user["interest"].strip() and user["interest"].lower() in str(firm["services"]).lower():
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
    with st.spinner("Matching firms..."):
        filtered_data = ria_data[
            (ria_data["aum_millions"] >= user_input["min_aum"]) &
            ((user_input["state"] == "Any") | (ria_data["state"] == user_input["state"])) &
            ((user_input["performance_fee_preference"] == ria_data["performance_fee"]) | (not user_input["performance_fee_preference"])) &
            ((user_input["client_type"] == "Any") |
             (user_input["client_type"] == "High-net-worth" and ria_data["client_hnw"]) |
             (user_input["client_type"] == "Institutional" and ria_data["client_institutional"])) &
            ((user_input["interest"].strip() == "") | ria_data["services"].str.contains(user_input["interest"], case=False, na=False))
        ]

        if not filtered_data.empty:
            filtered_data["Match Score"] = filtered_data.apply(lambda row: score_firm(row, user_input), axis=1)
            results = filtered_data.sort_values(by="Match Score", ascending=False)

            st.subheader("Your Matches")
            for _, row in results.iterrows():
                st.markdown(f"### {row['firm_name']} — Match Score: {row['Match Score']}%")
                if row.get("is_bonus_firm"):
                    st.markdown("_Limited data available_")
                st.markdown(f"**AUM**: ${row['aum_millions']:.2f}M")
                st.markdown(f"**Email**: {row.get('email', 'N/A')}")
                st.markdown(f"**Phone**: {row.get('phone', 'N/A')}")
                st.markdown(f"**Website**: {row.get('website', 'N/A')}")
                st.markdown(f"**Contact**: {row.get('1J-Name', 'N/A')} ({row.get('1J-Title', 'N/A')})")
                st.markdown("---")
        else:
            st.warning("No matches found. Try adjusting your filters.")



