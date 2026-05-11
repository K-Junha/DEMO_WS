import streamlit as st
from devices import (
    DEVICES, MEASUREMENT_DEVICES,
    render_device_card, render_measurement_group_card,
    render_measurement_table,
)
from samples import render_sample_table, render_score_chart

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lab Pilot Dashboard",
    page_icon=":material/science:",
    layout="wide",
)

# Prevent scrollbar jitter on narrow viewports
st.html("<style>html { overflow-y: scroll !important; }</style>")

# ── Title bar ─────────────────────────────────────────────────────────────────
st.markdown("# :material/science: Lab Pilot Dashboard")

st.divider()

# ── 2 × 2 Grid layout ────────────────────────────────────────────────────────
#   Row 1: col_left (2/3) + col_right (1/3)  — same height via explicit px
#   Row 2: col_left (2/3) + col_right (1/3)  — same height via explicit px

ROW1_HEIGHT = 350
ROW2_HEIGHT = 280

# Row 1
row1_left, row1_right = st.columns([2, 1])
cell_tl = row1_left.container(border=True, height=ROW1_HEIGHT)   # Controls Panel
cell_tr = row1_right.container(border=True, height=ROW1_HEIGHT)  # Price Chart

# Row 2
row2_left, row2_right = st.columns([2, 1])
cell_bl = row2_left.container(border=True, height=ROW2_HEIGHT)   # Summary Metrics
cell_br = row2_right.container(border=True, height=ROW2_HEIGHT)  # Volatility Chart

# ── Cell content (placeholder) ───────────────────────────────────────────────

with cell_tl:
    st.caption(":material/cable: Connected Devices")
    card_cols = st.columns(6)  # 5 individual + 1 measurement group
    for col, device in zip(card_cols[:5], DEVICES):
        with col:
            render_device_card(device)
    with card_cols[5]:
        render_measurement_group_card(MEASUREMENT_DEVICES)

with cell_tr:
    st.caption(":material/table_chart: 측정 결과")
    render_measurement_table()

with cell_bl:
    st.caption(":material/science: Glass Composition Samples")
    render_sample_table()

with cell_br:
    st.caption(":material/show_chart: Score Trend")
    render_score_chart()
