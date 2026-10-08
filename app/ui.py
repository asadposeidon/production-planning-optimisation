"""Shared visual styling and layout helpers for the Streamlit application."""

import streamlit as st


def apply_theme() -> None:
    """Apply a restrained navy, teal, and warm-gray visual system."""
    st.markdown(
        """
        <style>
        :root {
          --navy: #17324d;
          --teal: #167d7f;
          --teal-dark: #0f6668;
          --ink: #22313f;
          --muted: #64748b;
          --line: #dbe4ea;
          --surface: #ffffff;
          --canvas: #f5f7f9;
          --success: #177245;
          --warning: #a76508;
        }
        .stApp { background: var(--canvas); color: var(--ink); }
        [data-testid="stHeader"] { background: rgba(245,247,249,.94); }
        [data-testid="stSidebar"] { background: var(--navy); border-right: 0; }
        [data-testid="stSidebar"] * { color: #edf5f7 !important; }
        [data-testid="stSidebar"] a { border-radius: 4px !important; }
        [data-testid="stSidebar"] a:hover { background: rgba(255,255,255,.12) !important; }
        h1, h2, h3 { color: var(--navy); letter-spacing: -.02em; }
        h1 { font-size: 2.15rem !important; margin-bottom: .2rem !important; }
        h2 { font-size: 1.35rem !important; margin-top: 1.4rem !important; }
        h3 { font-size: 1.05rem !important; }
        [data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); border-left: 4px solid var(--teal); border-radius: 4px; padding: 14px 16px; box-shadow: 0 2px 8px rgba(23,50,77,.04); }
        [data-testid="stMetricLabel"] { color: var(--muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; }
        [data-testid="stMetricValue"] { color: var(--navy); font-weight: 700; }
        .stButton > button, .stDownloadButton > button { border-radius: 4px !important; border: 1px solid var(--teal) !important; background: var(--teal) !important; color: white !important; font-weight: 600; min-height: 2.4rem; box-shadow: none !important; transition: background .15s ease, border-color .15s ease; }
        .stButton > button:hover, .stDownloadButton > button:hover { background: var(--teal-dark) !important; border-color: var(--teal-dark) !important; }
        .stButton > button:focus, .stDownloadButton > button:focus { box-shadow: 0 0 0 2px rgba(22,125,127,.18) !important; }
        .stTextInput input, .stNumberInput input, .stDateInput input, [data-baseweb="select"] > div { border-radius: 4px !important; border-color: var(--line) !important; }
        [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 4px; overflow: hidden; }
        [data-testid="stAlert"] { border-radius: 4px; }
        .eyebrow { color: var(--teal); font-size: .78rem; text-transform: uppercase; letter-spacing: .12em; font-weight: 700; margin-bottom: .35rem; }
        .subtitle { color: var(--muted); margin-top: 0; margin-bottom: 1.25rem; }
        .status-note { color: var(--muted); font-size: .88rem; border-left: 3px solid var(--teal); padding-left: .75rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    """Render a consistent compact header for a page."""
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)
