"""
TeamCapacity Hub – Lite
=======================
A clean Streamlit app to manage team capacity vs. project demand.

HOW TO RUN:
-----------
1. Install dependencies:
   pip install streamlit pandas matplotlib

2. Run the app:
   streamlit run team_capacity_hub.py

3. Open your browser at:
   http://localhost:8501
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TeamCapacity Hub – Lite",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Background */
    .stApp {
        background-color: #0f1117;
        color: #e8eaf0;
    }

    /* Main header */
    .main-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.8rem;
        font-weight: 600;
        color: #e8eaf0;
        letter-spacing: -0.5px;
        margin-bottom: 0;
    }
    .main-sub {
        font-size: 0.85rem;
        color: #6c7280;
        font-family: 'IBM Plex Mono', monospace;
        margin-top: 4px;
        margin-bottom: 28px;
    }

    /* Section headers */
    .section-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #4ade80;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid #1e2130;
    }

    /* KPI cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 32px;
    }
    .kpi-card {
        background: #161b27;
        border: 1px solid #1e2538;
        border-radius: 10px;
        padding: 22px 24px;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }
    .kpi-card.cap::before  { background: #4ade80; }
    .kpi-card.dem::before  { background: #60a5fa; }
    .kpi-card.stat::before { background: #f59e0b; }
    .kpi-card.stat.ok::before  { background: #4ade80; }
    .kpi-card.stat.over::before { background: #f87171; }

    .kpi-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #6c7280;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.2rem;
        font-weight: 600;
        color: #e8eaf0;
        line-height: 1;
    }
    .kpi-unit {
        font-size: 0.9rem;
        color: #6c7280;
        margin-left: 4px;
    }
    .kpi-badge {
        display: inline-block;
        margin-top: 10px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-green  { background: #14291e; color: #4ade80; }
    .badge-red    { background: #2b1515; color: #f87171; }
    .badge-yellow { background: #2b2210; color: #f59e0b; }

    /* Divider */
    .divider { border: none; border-top: 1px solid #1e2130; margin: 28px 0; }

    /* Sidebar tweaks */
    [data-testid="stSidebar"] {
        background-color: #0d1018;
        border-right: 1px solid #1a1f2e;
    }
    [data-testid="stSidebar"] .stMarkdown { color: #9ca3af; }

    /* Dataframe */
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

    /* Buttons */
    .stButton > button {
        background: #1a2235;
        color: #e8eaf0;
        border: 1px solid #2a3448;
        border-radius: 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        padding: 6px 16px;
        transition: all 0.15s;
    }
    .stButton > button:hover {
        background: #232d42;
        border-color: #4ade80;
        color: #4ade80;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input {
        background: #161b27 !important;
        border: 1px solid #1e2538 !important;
        color: #e8eaf0 !important;
        border-radius: 6px !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    .stSelectbox > div > div {
        background: #161b27 !important;
        border: 1px solid #1e2538 !important;
        color: #e8eaf0 !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Default sample data ───────────────────────────────────────────────────────
DEFAULT_MEMBERS = [
    {"Name": "Alice Chen",    "Daily Hours": 7.5},
    {"Name": "Bob Martins",   "Daily Hours": 8.0},
    {"Name": "Clara Osei",    "Daily Hours": 6.0},
    {"Name": "David Park",    "Daily Hours": 7.0},
]

DEFAULT_PROJECTS = [
    {"Project": "Website Redesign",    "Required Hours": 80,  "Priority": "High"},
    {"Project": "API Integration",     "Required Hours": 60,  "Priority": "High"},
    {"Project": "Mobile App v2",       "Required Hours": 120, "Priority": "Medium"},
    {"Project": "Data Pipeline",       "Required Hours": 45,  "Priority": "Low"},
    {"Project": "Internal Dashboard",  "Required Hours": 35,  "Priority": "Low"},
]

SPRINT_DAYS = 10   # default sprint length


# ── Session state ─────────────────────────────────────────────────────────────
if "members" not in st.session_state:
    st.session_state.members = DEFAULT_MEMBERS.copy()
if "projects" not in st.session_state:
    st.session_state.projects = DEFAULT_PROJECTS.copy()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">📊 TeamCapacity Hub</p>', unsafe_allow_html=True)
st.markdown('<p class="main-sub">// lite · sprint capacity planner</p>', unsafe_allow_html=True)


# ── Sidebar – inputs ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    sprint_days = st.number_input("Sprint length (days)", min_value=1, max_value=90,
                                  value=SPRINT_DAYS, step=1)

    st.markdown("---")

    # ── Team members ──
    st.markdown("### 👥 Team Members")
    members_to_remove = []
    for i, m in enumerate(st.session_state.members):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            m["Name"] = st.text_input("Name", value=m["Name"],
                                      key=f"mname_{i}", label_visibility="collapsed")
        with col2:
            m["Daily Hours"] = st.number_input("hrs/day", value=float(m["Daily Hours"]),
                                               min_value=0.5, max_value=24.0, step=0.5,
                                               key=f"mhrs_{i}", label_visibility="collapsed")
        with col3:
            if st.button("✕", key=f"mdel_{i}"):
                members_to_remove.append(i)

    for i in reversed(members_to_remove):
        st.session_state.members.pop(i)
        st.rerun()

    if st.button("＋ Add Member"):
        st.session_state.members.append({"Name": "New Member", "Daily Hours": 8.0})
        st.rerun()

    st.markdown("---")

    # ── Projects ──
    st.markdown("### 📁 Projects")
    projects_to_remove = []
    for i, p in enumerate(st.session_state.projects):
        st.markdown(f"**Project {i+1}**")
        col1, col2 = st.columns([3, 1])
        with col1:
            p["Project"] = st.text_input("Project name", value=p["Project"],
                                          key=f"pname_{i}", label_visibility="collapsed")
        with col2:
            if st.button("✕", key=f"pdel_{i}"):
                projects_to_remove.append(i)
        col3, col4 = st.columns(2)
        with col3:
            p["Required Hours"] = st.number_input("Req. hrs", value=float(p["Required Hours"]),
                                                   min_value=1.0, step=5.0,
                                                   key=f"phrs_{i}", label_visibility="collapsed")
        with col4:
            p["Priority"] = st.selectbox("Priority", ["High", "Medium", "Low"],
                                          index=["High", "Medium", "Low"].index(p["Priority"]),
                                          key=f"ppri_{i}", label_visibility="collapsed")

    for i in reversed(projects_to_remove):
        st.session_state.projects.pop(i)
        st.rerun()

    if st.button("＋ Add Project"):
        st.session_state.projects.append({"Project": "New Project",
                                           "Required Hours": 40.0, "Priority": "Medium"})
        st.rerun()

    st.markdown("---")
    if st.button("↺ Reset to sample data"):
        st.session_state.members = DEFAULT_MEMBERS.copy()
        st.session_state.projects = DEFAULT_PROJECTS.copy()
        st.rerun()


# ── Calculations ──────────────────────────────────────────────────────────────
members_df = pd.DataFrame(st.session_state.members)
projects_df = pd.DataFrame(st.session_state.projects)

total_capacity = members_df["Daily Hours"].sum() * sprint_days
total_demand   = projects_df["Required Hours"].sum()
gap            = total_capacity - total_demand
utilization    = (total_demand / total_capacity * 100) if total_capacity > 0 else 0

if utilization > 100:
    status = "OVERLOADED"
    status_badge = '<span class="kpi-badge badge-red">⚠ OVERLOADED</span>'
    card_cls = "stat over"
elif utilization < 75:
    status = "UNDERUTILIZED"
    status_badge = '<span class="kpi-badge badge-yellow">◌ UNDERUTILIZED</span>'
    card_cls = "stat"
else:
    status = "BALANCED"
    status_badge = '<span class="kpi-badge badge-green">✓ BALANCED</span>'
    card_cls = "stat ok"


# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Sprint Overview</p>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="kpi-card cap">
        <div class="kpi-label">Total Capacity</div>
        <div class="kpi-value">{total_capacity:,.0f}<span class="kpi-unit">hrs</span></div>
        <span class="kpi-badge badge-green">{len(members_df)} members · {sprint_days}d sprint</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card dem">
        <div class="kpi-label">Total Demand</div>
        <div class="kpi-value">{total_demand:,.0f}<span class="kpi-unit">hrs</span></div>
        <span class="kpi-badge" style="background:#162136;color:#60a5fa;">{len(projects_df)} projects</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    gap_sign = "+" if gap >= 0 else ""
    gap_color = "#4ade80" if gap >= 0 else "#f87171"
    st.markdown(f"""
    <div class="kpi-card {card_cls}">
        <div class="kpi-label">Capacity Gap</div>
        <div class="kpi-value" style="color:{gap_color};">{gap_sign}{gap:,.0f}<span class="kpi-unit">hrs</span></div>
        {status_badge}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# utilisation bar
util_clamped = min(utilization, 100)
bar_color = "#4ade80" if utilization <= 100 else "#f87171"
over_pct = max(0, utilization - 100)

col_bar, col_pct = st.columns([6, 1])
with col_bar:
    st.markdown(f"""
    <div style="background:#1a1f2e;border-radius:4px;height:8px;overflow:hidden;">
        <div style="width:{util_clamped}%;height:100%;background:{bar_color};
                    border-radius:4px;transition:width .4s;"></div>
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#6c7280;
                margin-top:5px;">utilisation · {utilization:.1f}%{"  ·  +" + f"{over_pct:.1f}% OVER CAPACITY" if over_pct else ""}</div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── Bar chart ─────────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Capacity vs Demand</p>', unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(9, 3.5))
fig.patch.set_facecolor("#161b27")
ax.set_facecolor("#161b27")

categories = ["Team Capacity", "Project Demand"]
values     = [total_capacity, total_demand]
colors     = ["#4ade80", "#60a5fa"]

bars = ax.bar(categories, values, color=colors, width=0.45,
              edgecolor="none", zorder=3)

# value labels on bars
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + (max(values) * 0.015),
            f"{val:,.0f} hrs", ha="center", va="bottom",
            fontsize=11, fontweight="600", color="#e8eaf0",
            fontfamily="monospace")

# horizontal reference line
ax.axhline(total_capacity, color="#4ade80", linewidth=0.8,
           linestyle="--", alpha=0.35, zorder=2)

# grid
ax.yaxis.grid(True, color="#1e2538", linewidth=0.7, zorder=0)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
ax.tick_params(colors="#6c7280", labelsize=10)
ax.yaxis.label.set_color("#6c7280")
ax.set_ylabel("Hours", color="#6c7280", fontsize=9)
plt.xticks(fontsize=11, color="#c9d0dc")
plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── Project breakdown table ───────────────────────────────────────────────────
st.markdown('<p class="section-title">Project Breakdown</p>', unsafe_allow_html=True)

priority_order = {"High": 0, "Medium": 1, "Low": 2}
projects_df_sorted = projects_df.copy()
projects_df_sorted["_pord"] = projects_df_sorted["Priority"].map(priority_order)
projects_df_sorted = projects_df_sorted.sort_values("_pord").drop(columns="_pord")

projects_df_sorted["% of Demand"] = (
    projects_df_sorted["Required Hours"] / total_demand * 100
).map("{:.1f}%".format)

projects_df_sorted["% of Capacity"] = (
    projects_df_sorted["Required Hours"] / total_capacity * 100
).map("{:.1f}%".format)

projects_df_sorted["Feasible"] = projects_df_sorted["Required Hours"].apply(
    lambda h: "✓ Yes" if h <= total_capacity else "✗ No"
)

display_df = projects_df_sorted[["Project", "Priority", "Required Hours",
                                  "% of Demand", "% of Capacity", "Feasible"]]
display_df = display_df.rename(columns={"Required Hours": "Req. Hours"})

# Style the dataframe
def style_priority(val):
    colors_map = {"High": "#f87171", "Medium": "#f59e0b", "Low": "#4ade80"}
    c = colors_map.get(val, "#9ca3af")
    return f"color: {c}; font-weight: 600;"

def style_feasible(val):
    return "color: #4ade80;" if "Yes" in val else "color: #f87171;"

styled = (
    display_df.style
    .applymap(style_priority, subset=["Priority"])
    .applymap(style_feasible, subset=["Feasible"])
    .set_properties(**{
        "background-color": "#161b27",
        "color": "#c9d0dc",
        "border-color": "#1e2538",
        "font-size": "13px",
    })
    .set_table_styles([
        {"selector": "th",
         "props": [("background-color", "#0f1117"),
                   ("color", "#6c7280"),
                   ("font-size", "11px"),
                   ("letter-spacing", "1px"),
                   ("text-transform", "uppercase"),
                   ("border-bottom", "1px solid #1e2538")]},
        {"selector": "tr:hover td",
         "props": [("background-color", "#1a2030")]},
    ])
    .hide(axis="index")
)

st.dataframe(display_df, use_container_width=True, hide_index=True)


# ── Member capacity detail ────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<p class="section-title">Member Capacity Detail</p>', unsafe_allow_html=True)

members_display = members_df.copy()
members_display["Sprint Hours"] = members_display["Daily Hours"] * sprint_days
members_display["% of Total Capacity"] = (
    members_display["Sprint Hours"] / total_capacity * 100
).map("{:.1f}%".format)
members_display = members_display.rename(columns={"Daily Hours": "Hrs/Day"})

st.dataframe(members_display, use_container_width=True, hide_index=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;font-family:'IBM Plex Mono',monospace;
            font-size:0.65rem;color:#2e3545;padding:16px 0;">
  TeamCapacity Hub – Lite · built with Streamlit · adjust inputs in the sidebar
</div>
""", unsafe_allow_html=True)
