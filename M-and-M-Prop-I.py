"""
Homemade Leverage — MM Proposition I (simple version)
--------------------------------------------------
Students fill in 4 cells: Table 1's Investment and Return (buy 1% of L),
and Table 2's Total Investment and Return (borrow + buy 1% of U). The
Loan and Share legs of Table 2 are given, so students focus on the
comparison that proves the point rather than re-deriving every line.
"""

import random
import streamlit as st

st.set_page_config(page_title="Homemade Leverage — MM Prop I", page_icon="⚖️", layout="centered")


def random_scenario():
    VU = random.choice([80, 90, 100, 110, 120, 130, 140, 150, 160])
    DL = round((VU * random.uniform(0.20, 0.50)) / 5) * 5
    profit = round(VU * random.uniform(0.08, 0.14) * 2) / 2
    interest = round(DL * random.uniform(0.04, 0.07) * 10) / 10
    return {"VU": VU, "DL": DL, "profit": profit, "interest": interest}


def correct_values(s):
    VL = s["VU"]  # MM Prop I: V_L = V_U
    EL = VL - s["DL"]
    a_inv = 0.01 * EL
    a_ret = 0.01 * (s["profit"] - s["interest"])
    loan_inv = -0.01 * s["DL"]
    loan_ret = -0.01 * s["interest"]
    share_inv = 0.01 * s["VU"]
    share_ret = 0.01 * s["profit"]
    return dict(a_inv=a_inv, a_ret=a_ret, loan_inv=loan_inv, loan_ret=loan_ret,
                share_inv=share_inv, share_ret=share_ret,
                tot_inv=loan_inv + share_inv, tot_ret=loan_ret + share_ret)


def reset():
    st.session_state.scenario = random_scenario()
    st.session_state.correct = correct_values(st.session_state.scenario)
    for k in ["a_inv", "a_ret", "tot_inv", "tot_ret"]:
        st.session_state[f"input_{k}"] = ""
    st.session_state.checked = False


if "scenario" not in st.session_state:
    reset()

st.title("Homemade Leverage")
st.caption("Compare two ways to get the same payoff: buying 1% of the levered firm outright, "
           "or borrowing to replicate it. Fill in the four blanks below.")

s = st.session_state.scenario
c1, c2, c3, c4 = st.columns(4)
c1.metric("V_U", f"€{s['VU']}m")
c2.metric("D_L", f"€{s['DL']}m")
c3.metric("Profit", f"€{s['profit']}m")
c4.metric("Interest", f"€{s['interest']}m")

if st.button("New numbers"):
    reset()
    st.rerun()

st.subheader("1. Buy 1% of L's shares")
col1, col2 = st.columns(2)
with col1:
    st.caption("Investment — 1% × (V_L − D_L)")
    st.text_input("Investment", key="input_a_inv", label_visibility="collapsed")
with col2:
    st.caption("Return — 1% × (profit − interest)")
    st.text_input("Return", key="input_a_ret", label_visibility="collapsed")

st.subheader("2. Borrow 1% of D_L, buy 1% of U")
correct = st.session_state.correct
st.markdown(
    f"Loan: Investment = `€{round(correct['loan_inv'],2)}m`, "
    f"Return = `€{round(correct['loan_ret'],2)}m`  \n"
    f"Share: Investment = `€{round(correct['share_inv'],2)}m`, "
    f"Return = `€{round(correct['share_ret'],2)}m`"
)
col1, col2 = st.columns(2)
with col1:
    st.caption("Total investment — sum of the two legs")
    st.text_input("Total investment", key="input_tot_inv", label_visibility="collapsed")
with col2:
    st.caption("Total return — sum of the two legs")
    st.text_input("Total return", key="input_tot_ret", label_visibility="collapsed")

if st.button("Check my answers", type="primary"):
    st.session_state.checked = True

if st.session_state.get("checked"):
    all_correct = True
    for k, label in [("a_inv", "Table 1 investment"), ("a_ret", "Table 1 return"),
                      ("tot_inv", "Table 2 total investment"), ("tot_ret", "Table 2 total return")]:
        raw = st.session_state.get(f"input_{k}", "").strip()
        try:
            ok = abs(float(raw) - correct[k]) < 0.06
        except ValueError:
            ok = False
        if not ok:
            all_correct = False
        st.write(("✅ " if ok else "❌ ") + label)

    if all_correct:
        st.success("Both strategies cost the same and pay the same — so V_L = V_U.")
        st.markdown("---")
        st.subheader("Now explain it")
        st.write(
            "Your Table 1 numbers and your Table 2 total should match. Given that the two "
            "strategies pay exactly the same return, why must they also cost exactly the "
            "same today — and what does that tell you about V_L versus V_U?"
        )
        st.text_area("Your answer", key="reflection_answer")
        with st.expander("Show model answer"):
            st.write(
                "Two assets with identical payoffs in every future state must have identical "
                "prices today. If they didn't, you could buy the cheaper one, sell the pricier "
                "one, and pocket a risk-free profit — that opportunity can't survive in a "
                "competitive market. So 1% × (V_L − D_L) must equal 1% × (V_U − D_L), which "
                "means V_L = V_U."
            )
