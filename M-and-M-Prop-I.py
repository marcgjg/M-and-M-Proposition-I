"""
Homemade Leverage — MM Proposition I
--------------------------------------------------
Streamlit app for the GOMBA Corporate Finance homemade-leverage exercise.
Students fill in the numeric cells of both arbitrage tables (buy 1% of the
levered firm vs. borrow + buy 1% of the unlevered firm), check their answers
cell-by-cell, and reflect on why the two Investment rows must be equal.

Drop-in: same pattern as the other apps in the suite (single-file,
session_state driven, no external services required).
"""

import random
import streamlit as st

st.set_page_config(page_title="Homemade Leverage — MM Prop I", page_icon="⚖️", layout="centered")

CELL_KEYS = ["a_inv", "a_ret", "loan_inv", "loan_ret", "share_inv", "share_ret", "tot_inv", "tot_ret"]

CELL_LABELS = {
    "a_inv": "Buy 1% of L — Investment  (1% × E_L = 1% × (V_L − D_L))",
    "a_ret": "Buy 1% of L — Return  (1% × (profit − interest))",
    "loan_inv": "Loan — Investment  (−1% × D_L)",
    "loan_ret": "Loan — Return  (−1% × interest)",
    "share_inv": "Share — Investment  (+1% × V_U)",
    "share_ret": "Share — Return  (+1% × profit)",
    "tot_inv": "Total — Investment  (= 1% × (V_U − D_L))",
    "tot_ret": "Total — Return  (= 1% × (profit − interest))",
}


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
    tot_inv = loan_inv + share_inv
    tot_ret = loan_ret + share_ret
    return dict(a_inv=a_inv, a_ret=a_ret, loan_inv=loan_inv, loan_ret=loan_ret,
                share_inv=share_inv, share_ret=share_ret, tot_inv=tot_inv, tot_ret=tot_ret)


def reset_scenario(break_mode=False):
    st.session_state.scenario = random_scenario()
    st.session_state.correct = correct_values(st.session_state.scenario)
    for k in CELL_KEYS:
        st.session_state[f"input_{k}"] = ""
    st.session_state.checked = False
    st.session_state.flagged_cell = None
    st.session_state.suspect_choice = None
    if break_mode:
        setup_break_mode()


def setup_break_mode():
    flagged = random.choice(CELL_KEYS)
    st.session_state.flagged_cell = flagged
    for k in CELL_KEYS:
        correct_val = st.session_state.correct[k]
        if k == flagged:
            wrong = -correct_val if correct_val != 0 else 1.0
            st.session_state[f"input_{k}"] = str(round(wrong, 2))
        else:
            st.session_state[f"input_{k}"] = str(round(correct_val, 2))


if "scenario" not in st.session_state:
    reset_scenario()

st.title("Homemade Leverage")
st.caption("Fill in every blank cell, then check your ledger. Confirm that buying 1% of the "
           "levered firm and replicating it with borrowed money produce identical outcomes. "
           "No taxes, perfect markets.")

with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    s = st.session_state.scenario
    c1.metric("V_U (unlevered firm)", f"€{s['VU']}m")
    c2.metric("D_L (levered firm's debt)", f"€{s['DL']}m")
    c3.metric("Profit (EBIT)", f"€{s['profit']}m")
    c4.metric("Interest on D_L", f"€{s['interest']}m")

    b1, b2 = st.columns(2)
    break_mode = b1.toggle("Break-it mode", value=st.session_state.get("break_mode", False))
    st.session_state.break_mode = break_mode
    if b2.button("New numbers", use_container_width=True):
        reset_scenario(break_mode=break_mode)
        st.rerun()

if break_mode:
    st.info("One cell below has already been filled in for you — but one of the eight is "
            "wrong. Find it, correct it, then check your answers.")
    if st.session_state.flagged_cell is None:
        setup_break_mode()
    st.session_state.suspect_choice = st.selectbox(
        "Which cell do you think is wrong?",
        options=[""] + CELL_KEYS,
        format_func=lambda k: "— choose a cell —" if k == "" else CELL_LABELS[k],
    )

st.subheader("1. Buy 1% of L's shares")
col1, col2 = st.columns(2)
with col1:
    st.caption(CELL_LABELS["a_inv"])
    st.text_input("Investment", key="input_a_inv", label_visibility="collapsed")
with col2:
    st.caption(CELL_LABELS["a_ret"])
    st.text_input("Return", key="input_a_ret", label_visibility="collapsed")

st.subheader("2. Borrow 1% of D_L, buy 1% of U")
for row, label in [("loan", "Loan"), ("share", "Share"), ("tot", "Total")]:
    st.markdown(f"**{label}**")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(CELL_LABELS[f"{row}_inv"])
        st.text_input("Investment", key=f"input_{row}_inv", label_visibility="collapsed")
    with col2:
        st.caption(CELL_LABELS[f"{row}_ret"])
        st.text_input("Return", key=f"input_{row}_ret", label_visibility="collapsed")

filled = sum(1 for k in CELL_KEYS if st.session_state.get(f"input_{k}", "").strip() != "")
st.caption(f"{filled} of 8 cells filled")

if st.button("Check my answers", type="primary"):
    st.session_state.checked = True

if st.session_state.get("checked"):
    all_correct = True
    for k in CELL_KEYS:
        raw = st.session_state.get(f"input_{k}", "").strip()
        target = st.session_state.correct[k]
        try:
            val = float(raw)
            ok = abs(val - target) < 0.06
        except ValueError:
            ok = False
        if not ok:
            all_correct = False
        icon = "✅" if ok else ("❌" if raw else "⬜")
        st.write(f"{icon} {CELL_LABELS[k]}")

    if break_mode:
        flagged = st.session_state.flagged_cell
        suspect = st.session_state.suspect_choice
        flagged_val = st.session_state.get(f"input_{flagged}", "")
        try:
            flagged_ok = abs(float(flagged_val) - st.session_state.correct[flagged]) < 0.06
        except ValueError:
            flagged_ok = False
        all_correct = all_correct and flagged_ok and suspect == flagged
        if suspect and suspect != flagged:
            st.warning("That's not the wrong cell — look again.")
        elif suspect == flagged and not flagged_ok:
            st.info("Right cell — now enter the correct value.")

    if all_correct:
        st.success("QED — no arbitrage. Both strategies cost the same and pay the same, "
                    "so V_L = V_U.")
        st.markdown("---")
        st.subheader("Now explain it")
        st.write(
            "The Return row is identical for both strategies: 1% × (profit − interest) "
            "either way. Given that, why must the Investment row also be identical — "
            "i.e. why must 1% × (V_L − D_L) equal 1% × (V_U − D_L), and therefore V_L = V_U?"
        )
        st.text_area("Your answer", key="reflection_answer")
        with st.expander("Show model answer"):
            st.write(
                "Two assets that pay exactly the same return in every state of the world "
                "must cost exactly the same today — otherwise you could buy the cheap one, "
                "sell (or short) the expensive one, pocket the price difference risk-free, "
                "and collect a zero net cash flow forever after. That arbitrage can't survive "
                "in equilibrium, so the two investments must be priced equally: "
                "1% × (V_L − D_L) = 1% × (V_U − D_L), which gives V_L = V_U."
            )
