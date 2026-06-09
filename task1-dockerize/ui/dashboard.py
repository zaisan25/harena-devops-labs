# ui/dashboard.py
import streamlit as st
import json
import pandas as pd
from datetime import datetime
from prometheus_client import CollectorRegistry, Gauge, Counter, start_http_server
from core.metrics import get_cpu, get_ram, get_disk
from core.health import readiness, liveness
from core.config import REFRESH_RATE
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(
    page_title="Control Plane Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Prometheus Registry
@st.cache_resource
def get_prometheus_registry():
    registry = CollectorRegistry()
    try:
        start_http_server(8000, registry=registry)
    except OSError:
        pass
    return {
        "cpu": Gauge('control_plane_cpu_percentage', 'CPU %', registry=registry),
        "ram": Gauge('control_plane_ram_percentage', 'RAM %', registry=registry),
        "disk": Gauge('control_plane_disk_percentage', 'Disk %', registry=registry),
        "refresh": Counter('control_plane_ui_refreshes_total', 'Total refreshes', registry=registry)
    }

METRICS = get_prometheus_registry()

# 3. Cached Data
@st.cache_data(ttl=2)
def get_system_data():
    return {
        "cpu": get_cpu(interval=0.1),
        "ram": get_ram(),
        "disk": get_disk(),
        "ready": readiness(),
        "live": liveness(),
        "timestamp": datetime.now().isoformat()
    }

@st.cache_data(ttl=5)
def get_recent_logs(lines=20):
    try:
        with open("/app/logs/app.json.log", "r") as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            parsed = []
            for line in last_lines:
                try:
                    entry = json.loads(line.strip())
                    entry["timestamp"] = entry.get("timestamp", "")[:19].replace("T", " ")
                    parsed.append(entry)
                except:
                    parsed.append({"level": "ERROR", "message": "Malformed log line"})
            return parsed
    except FileNotFoundError:
        return []

# 4. Custom CSS - Professional Dark Theme
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1400px;
    }
    
    /* Header */
    .dashboard-header {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #2d3748;
    }
    .dashboard-header h1 {
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .dashboard-header p {
        color: #94a3b8;
        margin: 0.25rem 0 0 0;
        font-size: 0.875rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
        border-radius: 1rem;
        padding: 1.25rem;
        border: 1px solid #334155;
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        border-color: #60a5fa;
        transform: translateY(-2px);
    }
    .metric-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #94a3b8;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.75rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1.2;
    }
    .metric-unit {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 400;
    }
    .metric-trend {
        margin-top: 0.5rem;
        font-size: 0.75rem;
        color: #60a5fa;
    }
    
    /* Health Cards */
    .health-card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 0.75rem;
        padding: 0.75rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #334155;
    }
    .health-status-ok {
        color: #4ade80;
        font-weight: 600;
    }
    .health-status-fail {
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Log Container */
    .log-container {
        background: #0f172a;
        border-radius: 0.75rem;
        border: 1px solid #334155;
        overflow: hidden;
    }
    .log-header {
        background: #1e293b;
        padding: 0.5rem 1rem;
        border-bottom: 1px solid #334155;
        font-size: 0.75rem;
        font-weight: 600;
        color: #94a3b8;
    }
    
    /* Refresh Indicator */
    .refresh-badge {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        background: #1e293b;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        color: #64748b;
        border: 1px solid #334155;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        transform: translateY(-1px);
    }
    
    /* Info boxes */
    .info-box {
        background: #1e293b;
        border-left: 3px solid #60a5fa;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# 5. Header
st.markdown("""
<div class="dashboard-header">
    <h1>🛸 Control Plane</h1>
    <p>System metrics & structured logging · Auto-refresh every {}s</p>
</div>
""".format(REFRESH_RATE), unsafe_allow_html=True)

# 6. Fetch Data
data = get_system_data()
logs = get_recent_logs()

# Update Prometheus metrics
METRICS["cpu"].set(data["cpu"])
METRICS["ram"].set(data["ram"])
METRICS["disk"].set(data["disk"])

# 7. Metrics Row (4 columns including health summary)
col1, col2, col3, col4 = st.columns(4)

# CPU Card
cpu_color = "#ef4444" if data["cpu"] > 80 else "#f59e0b" if data["cpu"] > 60 else "#4ade80"
col1.markdown(f"""
<div class="metric-card">
    <div class="metric-title">🖥️ CPU Usage</div>
    <div class="metric-value">{data['cpu']:.1f}<span class="metric-unit">%</span></div>
    <div class="metric-trend" style="color:{cpu_color}">
        {'⚠️ High load' if data['cpu'] > 80 else '✓ Normal' if data['cpu'] < 60 else '▲ Elevated'}
    </div>
</div>
""", unsafe_allow_html=True)

# RAM Card
ram_color = "#ef4444" if data["ram"] > 90 else "#f59e0b" if data["ram"] > 75 else "#4ade80"
col2.markdown(f"""
<div class="metric-card">
    <div class="metric-title">💾 Memory Usage</div>
    <div class="metric-value">{data['ram']:.1f}<span class="metric-unit">%</span></div>
    <div class="metric-trend" style="color:{ram_color}">
        {'⚠️ Critical' if data['ram'] > 90 else '▲ Used' if data['ram'] > 75 else '✓ Available'}
    </div>
</div>
""", unsafe_allow_html=True)

# Disk Card
disk_color = "#ef4444" if data["disk"] > 90 else "#f59e0b" if data["disk"] > 80 else "#4ade80"
col3.markdown(f"""
<div class="metric-card">
    <div class="metric-title">💿 Disk Usage</div>
    <div class="metric-value">{data['disk']:.1f}<span class="metric-unit">%</span></div>
    <div class="metric-trend" style="color:{disk_color}">
        {'⚠️ Full' if data['disk'] > 90 else '▲ Filling' if data['disk'] > 80 else '✓ OK'}
    </div>
</div>
""", unsafe_allow_html=True)

# Health Summary Card
ready_status = "✅ Ready" if data["ready"] else "❌ Not Ready"
live_status = "✅ Live" if data["live"] else "❌ Dead"
health_color = "#4ade80" if data["ready"] and data["live"] else "#ef4444"

col4.markdown(f"""
<div class="metric-card">
    <div class="metric-title">🛡️ Health Status</div>
    <div class="metric-value" style="font-size:1.2rem; color:{health_color}">
        {'Operational' if data['ready'] and data['live'] else 'Degraded'}
    </div>
    <div class="metric-trend">
        Readiness: {ready_status}<br>
        Liveness: {live_status}
    </div>
</div>
""", unsafe_allow_html=True)

# 8. Detailed Health Row
st.markdown("---")
st.markdown("### 🔍 System Details")

detail_col1, detail_col2, detail_col3 = st.columns(3)

with detail_col1:
    st.markdown(f"""
    <div class="info-box">
        <strong>📊 Current Load</strong><br>
        CPU: {data['cpu']:.1f}% · RAM: {data['ram']:.1f}% · Disk: {data['disk']:.1f}%
    </div>
    """, unsafe_allow_html=True)

with detail_col2:
    st.markdown(f"""
    <div class="info-box">
        <strong>⏱️ Last Update</strong><br>
        {data['timestamp'][:19].replace('T', ' ')}
    </div>
    """, unsafe_allow_html=True)

with detail_col3:
    refresh_btn = st.button("🔄 Force Refresh", use_container_width=True)
    if refresh_btn:
        METRICS["refresh"].inc()
        st.cache_data.clear()
        st.rerun()

# 9. Logs Section
st.markdown("---")
st.markdown("### 📋 Structured Logs (Last 20 entries)")

if logs:
    # Convert to DataFrame for better display
    df = pd.DataFrame(logs)
    
    # Reorder and select columns
    display_cols = ["timestamp", "level", "module", "message"]
    available_cols = [c for c in display_cols if c in df.columns]
    
    # Add extras if present
    if "extras" in df.columns:
        df["extras"] = df["extras"].apply(lambda x: str(x)[:50] if x else "")
        available_cols.append("extras")
    
    # Apply level-based color formatting
    def color_level(val):
        colors = {"INFO": "#4ade80", "WARNING": "#f59e0b", "ERROR": "#ef4444", "DEBUG": "#94a3b8"}
        return f'<span style="color:{colors.get(val, "#94a3b8")}">● {val}</span>'
    
    # Display as HTML table for styling
    st.markdown('<div class="log-container">', unsafe_allow_html=True)
    st.markdown('<div class="log-header">📄 JSON Log Output</div>', unsafe_allow_html=True)
    
    for idx, row in logs[:10].items():  # Show last 10 in expanded view
        level_colored = color_level(row.get("level", "INFO"))
        timestamp = row.get("timestamp", "")[:19]
        message = row.get("message", "")[:100]
        module = row.get("module", "unknown")
        
        st.markdown(f"""
        <div style="padding:0.5rem 1rem; border-bottom:1px solid #1e293b; font-family:monospace; font-size:0.75rem;">
            <span style="color:#64748b;">[{timestamp}]</span>
            {level_colored}
            <span style="color:#60a5fa;">[{module}]</span>
            <span style="color:#cbd5e1;">{message}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Expandable raw JSON
    with st.expander("📄 View Raw JSON Logs"):
        st.json(logs)
else:
    st.info("📭 No logs found. Waiting for application logs...")

# 10. Auto-refresh
st_autorefresh(interval=REFRESH_RATE * 1000, key="auto_refresh")

# 11. Footer refresh indicator
st.markdown(f"""
<div class="refresh-badge">
    🔄 Auto-refresh every {REFRESH_RATE}s · {datetime.now().strftime("%H:%M:%S")}
</div>
""", unsafe_allow_html=True)

# 12. Update refresh counter metric
METRICS["refresh"].inc()