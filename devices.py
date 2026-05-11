"""
devices.py — Sila2 equipment configuration and card renderer.
"""
from __future__ import annotations
import pandas as pd

# ── Individual device configuration (non-measurement) ────────────────────────

DEVICES: list[dict] = [
    {
        "id": "scale",
        "name": "저울",
        "icon": "scale",
        "model": "A&D FX-3000i",
        "protocol": "RS-232",
        "ip": "192.168.1.10",
        "port": 5001,
        "connected": True,
    },
    {
        "id": "mixer",
        "name": "믹서",
        "icon": "blender",
        "model": "IKA RW 20",
        "protocol": "RS-485",
        "ip": "192.168.1.11",
        "port": 5002,
        "connected": True,
    },
    {
        "id": "furnace",
        "name": "용융로",
        "icon": "local_fire_department",
        "model": "Carbolite RHF 14/8",
        "protocol": "Ethernet",
        "ip": "192.168.1.12",
        "port": 5003,
        "connected": False,
    },
    {
        "id": "anneal",
        "name": "서냉로",
        "icon": "thermostat",
        "model": "Nabertherm L3/11",
        "protocol": "Ethernet",
        "ip": "192.168.1.13",
        "port": 5004,
        "connected": True,
    },
    {
        "id": "process",
        "name": "가공",
        "icon": "precision_manufacturing",
        "model": "Struers Tegramin-25",
        "protocol": "RS-485",
        "ip": "192.168.1.14",
        "port": 5005,
        "connected": True,
    },
]

# ── Measurement instrument group ──────────────────────────────────────────────

MEASUREMENT_DEVICES: list[dict] = [
    {
        "id": "dta",
        "name": "DTA",
        "icon": "thermostat",
        "model": "Netzsch STA 449 F3",
        "protocol": "Ethernet",
        "ip": "192.168.1.16",
        "port": 5007,
        "connected": True,
        "measures": ["Tg"],
    },
    {
        "id": "dsc",
        "name": "DSC",
        "icon": "device_thermostat",
        "model": "TA Instruments DSC 250",
        "protocol": "Ethernet",
        "ip": "192.168.1.17",
        "port": 5008,
        "connected": True,
        "measures": ["Tg"],
    },
    {
        "id": "dilatometer",
        "name": "딜라토미터",
        "icon": "straighten",
        "model": "Netzsch DIL 402 C",
        "protocol": "RS-232",
        "ip": "192.168.1.18",
        "port": 5009,
        "connected": False,
        "measures": ["CTE"],
    },
    {
        "id": "permittivity",
        "name": "유전율측정기",
        "icon": "electrical_services",
        "model": "Agilent E4980A",
        "protocol": "Ethernet",
        "ip": "192.168.1.19",
        "port": 5010,
        "connected": True,
        "measures": ["유전상수", "유전손실"],
    },
]

# ── Measure abbreviation map ──────────────────────────────────────────────────

MEASURE_ABBR: dict[str, str] = {
    "Tg":     "Tg",
    "CTE":    "CTE",
    "유전상수": "ε",
    "유전손실": "tanδ",
}

# ── Status lookups ────────────────────────────────────────────────────────────

def get_device_status(device_id: str) -> bool:
    """Return connection status for the given device id.

    TODO: Replace mock lookup with actual Sila2 connection probe, e.g.:
        channel = SilaClient(host=device["ip"], port=device["port"])
        return channel.is_connected()
    """
    return next(d["connected"] for d in DEVICES if d["id"] == device_id)


def get_measurement_group_status() -> dict:
    """Return summary {total, connected} for the measurement instrument group.

    TODO: Replace with real Sila2 polling when hardware is available.
    Auto-refresh pattern: @st.fragment(run_every="5s") on the card renderer.
    """
    connected = sum(1 for d in MEASUREMENT_DEVICES if d["connected"])
    return {"total": len(MEASUREMENT_DEVICES), "connected": connected}


# ── Protocol badge colors ─────────────────────────────────────────────────────

_PROTOCOL_COLORS: dict[str, str] = {
    "RS-232":   "#f59e0b",   # amber
    "RS-485":   "#3b82f6",   # blue
    "Ethernet": "#10b981",   # emerald
    "USB":      "#8b5cf6",   # violet
}

# ── Individual card HTML builder ──────────────────────────────────────────────

def build_device_card_html(device: dict) -> str:
    """Return a self-contained HTML string for a single device card."""
    connected: bool = device["connected"]
    led_color = "#22c55e" if connected else "#ef4444"
    led_label = "연결됨" if connected else "연결 끊김"
    badge_color = _PROTOCOL_COLORS.get(device["protocol"], "#64748b")

    return f"""
<div style="
    font-family: 'Space Grotesk', sans-serif;
    background: #1d293d;
    border: 1px solid #314158;
    border-radius: 10px;
    padding: 12px 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    min-width: 0;
">
  <!-- LED + name row -->
  <div style="display:flex;align-items:center;gap:6px;width:100%;justify-content:center;">
    <div title="{led_label}" style="
      width: 10px; height: 10px; border-radius: 50%;
      background: {led_color};
      box-shadow: 0 0 6px {led_color};
      flex-shrink: 0;
    "></div>
    <span style="
      font-size: 0.82rem; font-weight: 500;
      color: #e2e8f0; white-space: nowrap;
      overflow: hidden; text-overflow: ellipsis;
    ">{device['name']}</span>
  </div>

  <!-- Model name -->
  <div style="
    font-size: 0.72rem; color: #94a3b8;
    text-align: center; word-break: break-word;
    line-height: 1.3;
  ">{device['model']}</div>

  <!-- Protocol badge -->
  <div style="
    display: inline-block;
    background: {badge_color}22;
    border: 1px solid {badge_color};
    color: {badge_color};
    border-radius: 999px;
    padding: 1px 8px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    white-space: nowrap;
  ">{device['protocol']}</div>

  <!-- IP : Port -->
  <div style="
    font-family: 'Courier New', monospace;
    font-size: 0.65rem;
    color: #64748b;
    text-align: center;
  ">{device['ip']}:{device['port']}</div>
</div>
"""


# ── Measurement group card HTML builder ───────────────────────────────────────

def build_measurement_group_card_html(mdevices: list[dict]) -> str:
    """Return HTML for the measurement group summary card.

    Shows one row per instrument: LED + name + measure abbreviation pills.
    Intended to be rendered alongside a st.popover for full detail.
    """
    rows_html = ""
    for d in mdevices:
        led_color = "#22c55e" if d["connected"] else "#ef4444"
        led_label = "연결됨" if d["connected"] else "연결 끊김"
        abbrs = " ".join(
            f'<span style="'
            f'background:{_get_measure_pill_color(m)}22;'
            f'border:1px solid {_get_measure_pill_color(m)};'
            f'color:{_get_measure_pill_color(m)};'
            f'border-radius:999px;padding:0 5px;'
            f'font-size:0.58rem;font-weight:600;white-space:nowrap;'
            f'">{MEASURE_ABBR.get(m, m)}</span>'
            for m in d["measures"]
        )
        rows_html += f"""
  <div style="display:flex;align-items:center;gap:5px;padding:3px 0;">
    <div title="{led_label}" style="
      width:8px;height:8px;border-radius:50%;flex-shrink:0;
      background:{led_color};box-shadow:0 0 4px {led_color};
    "></div>
    <span style="font-size:0.72rem;color:#e2e8f0;flex:1;
      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
    >{d['name']}</span>
    <div style="display:flex;gap:3px;flex-shrink:0;">{abbrs}</div>
  </div>"""

    return f"""
<div style="
    font-family: 'Space Grotesk', sans-serif;
    background: #1d293d;
    border: 1px solid #314158;
    border-radius: 10px;
    padding: 10px;
    min-width: 0;
">
  <!-- Group header -->
  <div style="font-size:0.78rem;font-weight:600;color:#94a3b8;
    margin-bottom:6px;text-align:center;">측정 장비</div>
  <!-- Instrument rows -->
  {rows_html}
</div>
"""


def _get_measure_pill_color(measure: str) -> str:
    """Return a consistent accent color per measure type."""
    _colors = {
        "Tg":     "#f59e0b",
        "CTE":    "#3b82f6",
        "유전상수": "#10b981",
        "유전손실": "#8b5cf6",
    }
    return _colors.get(measure, "#64748b")


# ── Streamlit render helpers ──────────────────────────────────────────────────

def render_device_card(device: dict) -> None:
    """Render a single device card into the current Streamlit column."""
    import streamlit as st
    st.markdown(
        f":material/{device['icon']}:",
        help=f"{device['name']} — {device['model']}",
    )
    st.html(build_device_card_html(device))


def render_measurement_group_card(mdevices: list[dict]) -> None:
    """Render the measurement group card + popover into the current column."""
    import streamlit as st
    st.markdown(":material/biotech:", help="측정 장비 그룹")
    st.html(build_measurement_group_card_html(mdevices))
    with st.popover("상세보기", use_container_width=True):
        for d in mdevices:
            st.markdown(f"**:material/{d['icon']}: {d['name']}**")
            st.html(build_device_card_html(d))
            st.divider()


# ── Measurement result table ──────────────────────────────────────────────────

MEASUREMENT_TABLE_ROWS: list[dict] = [
    {"id": "tg",     "label": "Tg",    "unit": "°C"},
    {"id": "cte",    "label": "CTE",   "unit": "10⁻⁶/K"},
    {"id": "dielec", "label": "유전율", "unit": "—"},
    {"id": "eps",    "label": "유전상수", "unit": "—"},
]


def build_measurement_df() -> pd.DataFrame:
    """Return an empty 4×6 DataFrame for the measurement result table.

    Columns: 속성 (read-only label), 예측값 (read-only, GlassNet TODO),
             측정1, 측정2, 측정3, 목표값 (user-editable floats).
    """
    rows = []
    for r in MEASUREMENT_TABLE_ROWS:
        rows.append({
            "속성":  f"{r['label']} [{r['unit']}]",
            "예측값": None,
            "측정1":  None,
            "측정2":  None,
            "측정3":  None,
            "목표값": None,
        })
    return pd.DataFrame(rows)


def render_measurement_table() -> None:
    """Render the 4×6 measurement result data_editor into the current cell."""
    import streamlit as st
    df = build_measurement_df()
    st.data_editor(
        df,
        disabled=["속성", "예측값"],
        hide_index=True,
        use_container_width=True,
        column_config={
            "속성":  st.column_config.TextColumn("속성",  width="small"),
            "예측값": st.column_config.NumberColumn("예측값", format="%.4g"),
            "측정1":  st.column_config.NumberColumn("측정1",  format="%.4g"),
            "측정2":  st.column_config.NumberColumn("측정2",  format="%.4g"),
            "측정3":  st.column_config.NumberColumn("측정3",  format="%.4g"),
            "목표값": st.column_config.NumberColumn("목표값", format="%.4g"),
        },
    )

