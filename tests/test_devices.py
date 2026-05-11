"""
Tests for DEVICES config and device card renderer.
Run: python -m pytest tests/ -v
"""
import sys
import os
import importlib
import types

# ── Stub out streamlit so tests run without a browser ─────────────────────────
st_stub = types.ModuleType("streamlit")
st_stub.html = lambda *a, **kw: None
st_stub.markdown = lambda *a, **kw: None
sys.modules.setdefault("streamlit", st_stub)

# Now import the module under test (devices.py extracted from app)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import devices  # will be created in Phase A/B


# ── Phase A: DEVICES list ─────────────────────────────────────────────────────

REQUIRED_KEYS = {"id", "name", "icon", "model", "protocol", "ip", "port", "connected"}
EXPECTED_ORDER = ["저울", "믹서", "용융로", "서냉로", "가공"]
VALID_PROTOCOLS = {"RS-232", "RS-485", "Ethernet", "USB"}


def test_devices_count():
    assert len(devices.DEVICES) == 5, "Must have exactly 5 devices (측정 moved to MEASUREMENT_DEVICES)"


def test_devices_order():
    names = [d["name"] for d in devices.DEVICES]
    assert names == EXPECTED_ORDER, f"Order must be {EXPECTED_ORDER}, got {names}"


def test_devices_required_keys():
    for d in devices.DEVICES:
        missing = REQUIRED_KEYS - d.keys()
        assert not missing, f"Device '{d.get('id')}' missing keys: {missing}"


def test_devices_protocol_values():
    for d in devices.DEVICES:
        assert d["protocol"] in VALID_PROTOCOLS, (
            f"Device '{d['id']}' has unknown protocol '{d['protocol']}'"
        )


def test_devices_port_is_int():
    for d in devices.DEVICES:
        assert isinstance(d["port"], int), f"Device '{d['id']}' port must be int"


def test_devices_connected_is_bool():
    for d in devices.DEVICES:
        assert isinstance(d["connected"], bool), (
            f"Device '{d['id']}' connected must be bool"
        )


# ── get_device_status ─────────────────────────────────────────────────────────

def test_get_device_status_returns_bool():
    for d in devices.DEVICES:
        result = devices.get_device_status(d["id"])
        assert isinstance(result, bool), (
            f"get_device_status('{d['id']}') must return bool"
        )


def test_get_device_status_matches_config():
    for d in devices.DEVICES:
        assert devices.get_device_status(d["id"]) == d["connected"]


# ── Phase B: render_device_card ───────────────────────────────────────────────

def test_render_device_card_returns_html_string():
    html = devices.build_device_card_html(devices.DEVICES[0])
    assert isinstance(html, str) and len(html) > 0


def test_render_device_card_contains_model():
    for d in devices.DEVICES:
        html = devices.build_device_card_html(d)
        assert d["model"] in html, f"Card HTML missing model '{d['model']}'"


def test_render_device_card_contains_ip_port():
    for d in devices.DEVICES:
        html = devices.build_device_card_html(d)
        assert f"{d['ip']}:{d['port']}" in html


def test_render_device_card_green_led_when_connected():
    connected_device = next(d for d in devices.DEVICES if d["connected"])
    html = devices.build_device_card_html(connected_device)
    assert "#22c55e" in html, "Connected device must have green LED (#22c55e)"


def test_render_device_card_red_led_when_disconnected():
    disconnected = {**devices.DEVICES[0], "connected": False}
    html = devices.build_device_card_html(disconnected)
    assert "#ef4444" in html, "Disconnected device must have red LED (#ef4444)"


def test_render_device_card_protocol_badge_present():
    for d in devices.DEVICES:
        html = devices.build_device_card_html(d)
        assert d["protocol"] in html, f"Card HTML missing protocol '{d['protocol']}'"


def test_render_device_card_name_present():
    for d in devices.DEVICES:
        html = devices.build_device_card_html(d)
        assert d["name"] in html, f"Card HTML missing name '{d['name']}'"


# ── Phase E: MEASUREMENT_DEVICES ─────────────────────────────────────────────

MEASUREMENT_REQUIRED_KEYS = REQUIRED_KEYS | {"measures"}
EXPECTED_MEASUREMENT_ORDER = ["DTA", "DSC", "딜라토미터", "유전율측정기"]


def test_measurement_devices_count():
    assert len(devices.MEASUREMENT_DEVICES) == 4


def test_measurement_devices_order():
    names = [d["name"] for d in devices.MEASUREMENT_DEVICES]
    assert names == EXPECTED_MEASUREMENT_ORDER


def test_measurement_devices_required_keys():
    for d in devices.MEASUREMENT_DEVICES:
        missing = MEASUREMENT_REQUIRED_KEYS - d.keys()
        assert not missing, f"Measurement device '{d.get('id')}' missing keys: {missing}"


def test_measurement_devices_measures_nonempty():
    for d in devices.MEASUREMENT_DEVICES:
        assert isinstance(d["measures"], list) and len(d["measures"]) > 0, (
            f"Device '{d['id']}' must have non-empty measures list"
        )


def test_measurement_devices_dta_measures_tg():
    dta = next(d for d in devices.MEASUREMENT_DEVICES if d["id"] == "dta")
    assert "Tg" in dta["measures"]


def test_measurement_devices_dsc_measures_tg():
    dsc = next(d for d in devices.MEASUREMENT_DEVICES if d["id"] == "dsc")
    assert "Tg" in dsc["measures"]


def test_measurement_devices_dilatometer_measures_cte():
    dil = next(d for d in devices.MEASUREMENT_DEVICES if d["id"] == "dilatometer")
    assert "CTE" in dil["measures"]


def test_measurement_devices_permittivity_measures():
    perm = next(d for d in devices.MEASUREMENT_DEVICES if d["id"] == "permittivity")
    assert "유전상수" in perm["measures"]
    assert "유전손실" in perm["measures"]


def test_get_measurement_group_status_structure():
    status = devices.get_measurement_group_status()
    assert "total" in status and "connected" in status
    assert status["total"] == 4
    assert isinstance(status["connected"], int)


def test_measure_abbr_keys():
    assert "Tg" in devices.MEASURE_ABBR
    assert "CTE" in devices.MEASURE_ABBR
    assert "유전상수" in devices.MEASURE_ABBR
    assert "유전손실" in devices.MEASURE_ABBR


def test_measure_abbr_unicode_values():
    assert devices.MEASURE_ABBR["유전상수"] == "ε"
    assert devices.MEASURE_ABBR["유전손실"] == "tanδ"


# ── Phase F: measurement group card ──────────────────────────────────────────

def test_build_measurement_group_card_html_returns_string():
    html = devices.build_measurement_group_card_html(devices.MEASUREMENT_DEVICES)
    assert isinstance(html, str) and len(html) > 0


def test_measurement_group_card_contains_all_names():
    html = devices.build_measurement_group_card_html(devices.MEASUREMENT_DEVICES)
    for d in devices.MEASUREMENT_DEVICES:
        assert d["name"] in html, f"Group card missing device name '{d['name']}'"


def test_measurement_group_card_green_led_for_connected():
    connected = [d for d in devices.MEASUREMENT_DEVICES if d["connected"]]
    assert len(connected) > 0, "Need at least one connected measurement device"
    html = devices.build_measurement_group_card_html(devices.MEASUREMENT_DEVICES)
    assert "#22c55e" in html


def test_measurement_group_card_red_led_for_disconnected():
    disconnected = [d for d in devices.MEASUREMENT_DEVICES if not d["connected"]]
    assert len(disconnected) > 0, "Need at least one disconnected measurement device"
    html = devices.build_measurement_group_card_html(devices.MEASUREMENT_DEVICES)
    assert "#ef4444" in html


def test_measurement_group_card_contains_measure_abbrs():
    html = devices.build_measurement_group_card_html(devices.MEASUREMENT_DEVICES)
    assert "Tg" in html
    assert "CTE" in html
    assert "ε" in html
    assert "tanδ" in html


# ── Phase H: MEASUREMENT_TABLE_ROWS + build_measurement_df ───────────────────

def test_measurement_table_rows_count():
    assert len(devices.MEASUREMENT_TABLE_ROWS) == 4


def test_measurement_table_rows_keys():
    for row in devices.MEASUREMENT_TABLE_ROWS:
        for key in ("id", "label", "unit"):
            assert key in row, f"Row '{row}' missing key '{key}'"


def test_measurement_table_rows_order():
    ids = [r["id"] for r in devices.MEASUREMENT_TABLE_ROWS]
    assert ids == ["tg", "cte", "dielec", "eps"]


def test_build_measurement_df_shape():
    df = devices.build_measurement_df()
    assert df.shape == (4, 6), f"Expected (4, 6), got {df.shape}"


def test_build_measurement_df_columns():
    df = devices.build_measurement_df()
    expected = ["속성", "예측값", "측정1", "측정2", "측정3", "목표값"]
    assert list(df.columns) == expected, f"Columns mismatch: {list(df.columns)}"


def test_build_measurement_df_prop_labels():
    df = devices.build_measurement_df()
    labels = df["속성"].tolist()
    assert any("Tg" in s for s in labels)
    assert any("CTE" in s for s in labels)
    assert any("유전율" in s for s in labels)
    assert any("유전상수" in s for s in labels)


def test_build_measurement_df_initial_nulls():
    import pandas as pd
    df = devices.build_measurement_df()
    for col in ["예측값", "측정1", "측정2", "측정3", "목표값"]:
        assert df[col].isna().all(), f"Column '{col}' should be all-null initially"
