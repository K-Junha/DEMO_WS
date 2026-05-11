"""
samples.py — Glass composition sample data model and Streamlit renderer.
"""
from __future__ import annotations
import pandas as pd

# ── Column / option constants ─────────────────────────────────────────────────

SAMPLE_COLUMNS: list[str] = [
    "ID",
    "Composition",
    "Status",
    "Learning Impact Score",
    "Target Achievement Score",
]

SAMPLE_STATUS_OPTIONS: list[str] = ["Pending", "Running", "Done", "Error"]

# ── Button CSS (injected via st.markdown) ─────────────────────────────────────
# Scoped to the button row by :has() — outer 3-col HBlock is unique on the page.
# Add = blue, Delete = red, Start = green.
_BUTTON_CSS = """<style>
/* ── Sample table action buttons ─────────────────────────────────────── */

/* Add Sample — blue (#2563eb)
   target: first stColumn of the nested 2-col block inside our 3-col row */
div[data-testid="stHorizontalBlock"]:has(
    > div[data-testid="stColumn"]:nth-child(3):last-child
) div[data-testid="stHorizontalBlock"]
  div[data-testid="stColumn"]:first-child button {
    background-color: #2563eb !important;
    border-color:     #2563eb !important;
    color:            #ffffff !important;
}
div[data-testid="stHorizontalBlock"]:has(
    > div[data-testid="stColumn"]:nth-child(3):last-child
) div[data-testid="stHorizontalBlock"]
  div[data-testid="stColumn"]:first-child button:hover {
    background-color: #1d4ed8 !important;
    border-color:     #1d4ed8 !important;
}

/* Delete Sample — red (#dc2626)
   target: last stColumn of the nested 2-col block */
div[data-testid="stHorizontalBlock"]:has(
    > div[data-testid="stColumn"]:nth-child(3):last-child
) div[data-testid="stHorizontalBlock"]
  div[data-testid="stColumn"]:last-child button {
    background-color: #dc2626 !important;
    border-color:     #dc2626 !important;
    color:            #ffffff !important;
}
div[data-testid="stHorizontalBlock"]:has(
    > div[data-testid="stColumn"]:nth-child(3):last-child
) div[data-testid="stHorizontalBlock"]
  div[data-testid="stColumn"]:last-child button:hover {
    background-color: #b91c1c !important;
    border-color:     #b91c1c !important;
}

/* Start Experiment — green (#16a34a)
   target: last direct stColumn of the 3-col outer row */
div[data-testid="stHorizontalBlock"]:has(
    > div[data-testid="stColumn"]:nth-child(3):last-child
) > div[data-testid="stColumn"]:last-child button {
    background-color: #16a34a !important;
    border-color:     #16a34a !important;
    color:            #ffffff !important;
    width:            100% !important;
}
div[data-testid="stHorizontalBlock"]:has(
    > div[data-testid="stColumn"]:nth-child(3):last-child
) > div[data-testid="stColumn"]:last-child button:hover {
    background-color: #15803d !important;
    border-color:     #15803d !important;
}
</style>"""

# ── Data builders ─────────────────────────────────────────────────────────────

def build_sample_df() -> pd.DataFrame:
    """Return an initial DataFrame with one demo row."""
    return pd.DataFrame([{
        "ID": "S-001",
        "Composition": "SiO2:70, Al2O3:18, B2O3:12",
        "Status": "Pending",
        "Learning Impact Score": None,
        "Target Achievement Score": None,
    }])


def _next_sample_id(df: pd.DataFrame) -> str:
    """Derive next auto-increment ID from the last row."""
    if df.empty:
        return "S-001"
    last_n = int(df["ID"].iloc[-1].split("-")[1])
    return f"S-{last_n + 1:03d}"


def add_sample(
    df: pd.DataFrame,
    composition: str = "",
    status: str = "Pending",
) -> pd.DataFrame:
    """Return a new DataFrame with one row appended."""
    new_row = {
        "ID": _next_sample_id(df),
        "Composition": composition,
        "Status": status,
        "Learning Impact Score": None,
        "Target Achievement Score": None,
    }
    return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)


def delete_last_sample(df: pd.DataFrame) -> pd.DataFrame:
    """Return a new DataFrame with the last row removed (safe on empty df)."""
    if df.empty:
        return df
    return df.iloc[:-1].reset_index(drop=True)


def delete_selected_samples(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows where the transient 'Select' column is True.

    'Select' is a render-only checkbox column added by data_editor;
    it is not part of SAMPLE_COLUMNS and is dropped from the result.
    If the column is absent the original DataFrame is returned unchanged.
    """
    if "Select" not in df.columns:
        return df
    kept = df[df["Select"] != True].drop(columns=["Select"]).reset_index(drop=True)
    return kept


def _prepare_editor_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return df with 'Select' checkbox column at position 0 for data_editor.

    If Select already exists it is moved to position 0 without resetting
    checked rows. NaN values (from add_sample concat) are filled with False
    so every checkbox renders correctly.
    """
    out = df.copy()
    if "Select" not in out.columns:
        out.insert(0, "Select", False)
    else:
        if out.columns[0] != "Select":
            cols = ["Select"] + [c for c in out.columns if c != "Select"]
            out = out[cols]
        # Fill NaN produced when add_sample concat misses the Select column
        out["Select"] = out["Select"].fillna(False).astype(bool)
    return out


def _save_from_editor(edited_df: pd.DataFrame) -> pd.DataFrame:
    """Persist data_editor output to session state.

    Retains the 'Select' column so the Delete button can read checked rows
    on the next rerun (fixing the bug where Select was stripped immediately).
    """
    return edited_df.reset_index(drop=True)


# ── Score trend chart ─────────────────────────────────────────────────────────

def build_score_chart_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return a long-form DataFrame suitable for an Altair line chart.

    Columns: Sample (1-based int), Metric (str), Score (float cumulative sum).
    None values are treated as 0 for cumulative purposes.
    """
    if df.empty:
        return pd.DataFrame(columns=["Sample", "Metric", "Score"])

    # Work on clean numeric copy (drop Select if present)
    work = df[[c for c in SAMPLE_COLUMNS if c in df.columns]].copy()
    lis = work["Learning Impact Score"].fillna(0.0).cumsum().tolist()
    tas = work["Target Achievement Score"].fillna(0.0).cumsum().tolist()
    n = len(work)
    samples_idx = list(range(1, n + 1))

    rows = (
        [{"Sample": i, "Metric": "Learning Impact Score", "Score": v}
         for i, v in zip(samples_idx, lis)]
        + [{"Sample": i, "Metric": "Target Achievement Score", "Score": v}
           for i, v in zip(samples_idx, tas)]
    )
    return pd.DataFrame(rows)


def render_score_chart() -> None:
    """Render the LIS / TAS cumulative line chart from session_state["samples"]."""
    import streamlit as st
    import altair as alt

    raw = st.session_state.get("samples", build_sample_df())
    # Drop Select column if present before charting
    raw = raw[[c for c in SAMPLE_COLUMNS if c in raw.columns]]
    chart_df = build_score_chart_df(raw)

    has_data = (
        not chart_df.empty
        and chart_df["Score"].sum() > 0
    )

    if not has_data:
        st.markdown(
            "<div style='color:#64748b;font-size:0.82rem;"
            "text-align:center;padding-top:40px;'>"
            "No score data yet — fill in LIS / TAS values in the sample table.</div>",
            unsafe_allow_html=True,
        )
        return

    color_scale = alt.Scale(
        domain=["Learning Impact Score", "Target Achievement Score"],
        range=["#3b82f6", "#10b981"],
    )

    chart = (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("Sample:O", title="Sample #", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Score:Q", title="Cumulative Score"),
            color=alt.Color("Metric:N", scale=color_scale, legend=alt.Legend(orient="bottom")),
            tooltip=["Sample:O", "Metric:N", alt.Tooltip("Score:Q", format=".3f")],
        )
        .properties(height=180)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor="#94a3b8",
            titleColor="#94a3b8",
            gridColor="#314158",
            domainColor="#314158",
        )
        .configure_legend(labelColor="#e2e8f0", titleColor="#94a3b8")
    )
    st.altair_chart(chart, use_container_width=True)


# ── Streamlit renderer ────────────────────────────────────────────────────────

def _add_sample_dialog() -> None:
    """@st.dialog — modal form for adding a new glass composition sample."""
    import streamlit as st

    @st.dialog("Add Sample")
    def _dialog() -> None:
        composition = st.text_input(
            "Composition",
            placeholder="e.g. SiO2:70, Al2O3:18, B2O3:12",
        )
        status = st.selectbox("Status", SAMPLE_STATUS_OPTIONS, index=0)
        st.write("")
        col_add, col_cancel = st.columns(2)
        with col_add:
            if st.button(":material/add: Add", key="dialog_add", type="primary"):
                st.session_state["samples"] = add_sample(
                    st.session_state["samples"],
                    composition=composition,
                    status=status,
                )
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key="dialog_cancel"):
                st.rerun()

    _dialog()


def render_sample_table() -> None:
    """Render the sample list table with action buttons into the current cell."""
    import streamlit as st

    if "samples" not in st.session_state:
        st.session_state["samples"] = build_sample_df()

    # ── Button color CSS ──────────────────────────────────────────────────────
    st.markdown(_BUTTON_CSS, unsafe_allow_html=True)

    # ── Button row: left (add + del) │ spacer │ right (start) ─────────────────
    outer_left, _, outer_right = st.columns([4, 3, 2])

    with outer_left:
        add_col, del_col = st.columns(2)
        with add_col:
            if st.button(":material/add: Add Sample", key="btn_add_sample"):
                _add_sample_dialog()
        with del_col:
            if st.button(":material/remove: Delete Sample", key="btn_del_sample"):
                df = st.session_state["samples"]
                if "Select" in df.columns and df["Select"].any():
                    st.session_state["samples"] = delete_selected_samples(df)
                else:
                    st.toast("No rows selected — tick the ☑ checkbox to select rows.", icon="⚠️")

    with outer_right:
        if st.button(
            ":material/play_arrow: Start Experiment",
            key="btn_start_exp",
            use_container_width=True,
        ):
            st.toast("Experiment started", icon="🔬")

    # ── Table (Select checkbox as first column, render-only) ──────────────────
    df_display = _prepare_editor_df(st.session_state["samples"])

    edited = st.data_editor(
        df_display,
        disabled=["ID"],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Select": st.column_config.CheckboxColumn("Select", width="small"),
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Composition": st.column_config.TextColumn("Composition"),
            "Status": st.column_config.SelectboxColumn(
                "Status", options=SAMPLE_STATUS_OPTIONS
            ),
            "Learning Impact Score": st.column_config.NumberColumn(
                "Learning Impact Score", format="%.3f"
            ),
            "Target Achievement Score": st.column_config.NumberColumn(
                "Target Achievement Score", format="%.3f"
            ),
        },
        key="sample_editor",
    )
    # Preserve Select so the Delete button can read checked rows on next rerun
    st.session_state["samples"] = _save_from_editor(edited)
