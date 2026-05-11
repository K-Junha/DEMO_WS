"""
Tests for samples.py — Glass composition sample data model.
Run: python -m pytest tests/ -v
"""
import sys
import os
import types

# ── Stub out streamlit so tests run without a browser ─────────────────────────
st_stub = types.ModuleType("streamlit")
st_stub.html = lambda *a, **kw: None
st_stub.markdown = lambda *a, **kw: None
sys.modules.setdefault("streamlit", st_stub)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import samples


# ── Phase I: SAMPLE_COLUMNS + SAMPLE_STATUS_OPTIONS ──────────────────────────

def test_sample_columns_count():
    assert len(samples.SAMPLE_COLUMNS) == 5


def test_sample_columns_names():
    expected = ["ID", "Composition", "Status", "Learning Impact Score", "Target Achievement Score"]
    assert samples.SAMPLE_COLUMNS == expected


def test_sample_status_options_has_pending():
    assert "Pending" in samples.SAMPLE_STATUS_OPTIONS


# ── build_sample_df ───────────────────────────────────────────────────────────

def test_build_sample_df_shape():
    df = samples.build_sample_df()
    assert df.shape == (1, 5), f"Expected (1, 5), got {df.shape}"


def test_build_sample_df_columns():
    df = samples.build_sample_df()
    assert list(df.columns) == samples.SAMPLE_COLUMNS


# ── add_sample / delete_last_sample ──────────────────────────────────────────

def test_add_sample_increments_id():
    df = samples.build_sample_df()           # S-001
    df2 = samples.add_sample(df)             # S-001, S-002
    assert len(df2) == 2
    assert df2["ID"].iloc[-1] == "S-002"


def test_delete_last_sample():
    df = samples.build_sample_df()           # 1 row
    df2 = samples.delete_last_sample(df)
    assert len(df2) == 0


def test_delete_last_sample_empty_safe():
    import pandas as pd
    empty = pd.DataFrame(columns=samples.SAMPLE_COLUMNS)
    result = samples.delete_last_sample(empty)
    assert result.empty


# ── Phase K: add_sample with values + delete_selected_samples ────────────────

def test_add_sample_with_composition():
    df = samples.build_sample_df()
    df2 = samples.add_sample(df, composition="SiO2:80, B2O3:20", status="Running")
    assert df2.iloc[-1]["Composition"] == "SiO2:80, B2O3:20"
    assert df2.iloc[-1]["Status"] == "Running"
    assert df2.iloc[-1]["ID"] == "S-002"


def test_delete_selected_samples_removes_checked():
    import pandas as pd
    df = samples.build_sample_df()
    df2 = samples.add_sample(df)        # S-001, S-002
    df2["Select"] = [True, False]
    result = samples.delete_selected_samples(df2)
    assert len(result) == 1
    assert result.iloc[0]["ID"] == "S-002"


def test_delete_selected_samples_keeps_unchecked():
    import pandas as pd
    df = samples.build_sample_df()
    df["Select"] = [False]
    result = samples.delete_selected_samples(df)
    assert len(result) == 1


def test_delete_selected_samples_no_select_col():
    df = samples.build_sample_df()
    result = samples.delete_selected_samples(df)
    assert len(result) == len(df)


# ── Phase K bug fix: Select must survive the save → delete cycle ──────────────

def test_save_from_editor_retains_select_column():
    """Prove-It: Select stripped on save → delete button never sees selection.

    _save_from_editor must preserve the Select column so the Delete button
    can read it on the next rerun.
    """
    import pandas as pd
    df = samples.build_sample_df()
    df.insert(0, "Select", [True])
    saved = samples._save_from_editor(df)
    assert "Select" in saved.columns, "Select column must be kept for delete to work"
    assert bool(saved["Select"].iloc[0]) is True


def test_prepare_editor_df_adds_select_column():
    """_prepare_editor_df must add a Select=False column when absent."""
    df = samples.build_sample_df()
    display = samples._prepare_editor_df(df)
    assert "Select" in display.columns
    assert display.columns[0] == "Select"
    assert (display["Select"] == False).all()


def test_prepare_editor_df_keeps_existing_select():
    """_prepare_editor_df must not reset an existing Select column."""
    import pandas as pd
    df = samples.build_sample_df()
    df.insert(0, "Select", [True])
    display = samples._prepare_editor_df(df)
    assert bool(display["Select"].iloc[0]) is True


# ── Phase K-bug2: new rows after add must have Select=False not NaN ───────────

def test_prepare_editor_df_fills_nan_select_with_false():
    """Prove-It: add_sample on df-with-Select produces NaN → _prepare_editor_df must fill it.

    Flow:
      1. session_state has Select column (from previous save)
      2. add_sample concat → new row gets NaN for Select
      3. _prepare_editor_df must normalise NaN → False so checkbox renders
    """
    import pandas as pd
    # Simulate session state that already has Select
    df_with_select = samples.build_sample_df()
    df_with_select.insert(0, "Select", [False])

    # add_sample doesn't know about Select, so new row gets NaN
    df_after_add = samples.add_sample(df_with_select)
    assert pd.isna(df_after_add["Select"].iloc[-1]), "precondition: new row has NaN"

    # _prepare_editor_df must convert NaN → False
    display = samples._prepare_editor_df(df_after_add)
    assert display["Select"].iloc[-1] is not None
    assert bool(display["Select"].iloc[-1]) is False, "new row Select must be False, not NaN"


# ── Phase L: build_score_chart_df ────────────────────────────────────────────

def test_build_score_chart_df_columns():
    df = samples.build_sample_df()
    result = samples.build_score_chart_df(df)
    assert list(result.columns) == ["Sample", "Metric", "Score"]


def test_build_score_chart_df_shape():
    """1 sample × 2 metrics = 2 rows (long-form)."""
    df = samples.build_sample_df()
    result = samples.build_score_chart_df(df)
    assert result.shape == (2, 3)


def test_build_score_chart_df_cumulative():
    """LIS cumulative sum: 0.5 + 0.3 = 0.8 at sample 2."""
    import pandas as pd
    df = samples.build_sample_df()
    df = samples.add_sample(df, composition="X", status="Done")
    df.at[0, "Learning Impact Score"] = 0.5
    df.at[1, "Learning Impact Score"] = 0.3
    df.at[0, "Target Achievement Score"] = None
    df.at[1, "Target Achievement Score"] = None
    result = samples.build_score_chart_df(df)
    lis_rows = result[result["Metric"] == "Learning Impact Score"].reset_index(drop=True)
    assert abs(lis_rows.loc[1, "Score"] - 0.8) < 1e-9, f"Expected 0.8, got {lis_rows.loc[1, 'Score']}"


def test_build_score_chart_df_none_as_zero():
    """None values must contribute 0 to cumulative sum."""
    import pandas as pd
    df = samples.build_sample_df()
    df.at[0, "Learning Impact Score"] = None
    df.at[0, "Target Achievement Score"] = None
    result = samples.build_score_chart_df(df)
    assert (result["Score"] == 0.0).all(), "All-None scores must yield 0.0"


def test_build_score_chart_df_empty():
    """Empty DataFrame must return empty result."""
    import pandas as pd
    empty = pd.DataFrame(columns=samples.SAMPLE_COLUMNS)
    result = samples.build_score_chart_df(empty)
    assert result.empty
