import streamlit as st
import json
from datetime import datetime
from core.metrics import get_cpu, get_ram, get_disk
from core.health import readiness, liveness
from infra.logger import struct_log
from core.config import REFRESH_RATE
from streamlit_autorefresh import st_autorefresh


st.set_page_config(page_title="Control Plane", layout="wide")


def icon_svg(name, color="#E5E7EB"):
	icons = {
		"dashboard": "<svg viewBox='0 0 24 24' fill='none' aria-hidden='true'><path d='M4 5h7v7H4V5Zm9 0h7v4h-7V5ZM4 14h7v5H4v-5Zm9 8v-9h7v9h-7Z' fill='{color}'/></svg>",
		"cpu": "<svg viewBox='0 0 24 24' fill='none' aria-hidden='true'><rect x='6' y='6' width='12' height='12' rx='3' fill='{color}'/><path d='M9 1v3M12 1v3M15 1v3M9 20v3M12 20v3M15 20v3M1 9h3M1 12h3M1 15h3M20 9h3M20 12h3M20 15h3' stroke='{color}' stroke-width='1.5' stroke-linecap='round'/></svg>",
		"ram": "<svg viewBox='0 0 24 24' fill='none' aria-hidden='true'><path d='M6 8h12a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2Z' stroke='{color}' stroke-width='1.6'/><path d='M7 8V5m3 3V5m4 3V5m3 3V5M7 19v-3m3 3v-3m4 3v-3m3 3v-3' stroke='{color}' stroke-width='1.4' stroke-linecap='round'/></svg>",
		"disk": "<svg viewBox='0 0 24 24' fill='none' aria-hidden='true'><ellipse cx='12' cy='6' rx='7' ry='3' stroke='{color}' stroke-width='1.6'/><path d='M5 6v8c0 1.7 3.1 3 7 3s7-1.3 7-3V6' stroke='{color}' stroke-width='1.6'/><path d='M5 11c0 1.7 3.1 3 7 3s7-1.3 7-3' stroke='{color}' stroke-width='1.6'/></svg>",
		"shield": "<svg viewBox='0 0 24 24' fill='none' aria-hidden='true'><path d='M12 3 19 6v5c0 4.9-3.1 8.5-7 10-3.9-1.5-7-5.1-7-10V6l7-3Z' stroke='{color}' stroke-width='1.6' stroke-linejoin='round'/><path d='m9.5 12 1.9 1.9 3.5-4' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>",
		"pulse": "<svg viewBox='0 0 24 24' fill='none' aria-hidden='true'><path d='M3 12h4l2-6 4 12 2-6h6' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>",
		"refresh": "<svg viewBox='0 0 24 24' fill='none' aria-hidden='true'><path d='M20 12a8 8 0 1 1-2.2-5.5' stroke='{color}' stroke-width='1.8' stroke-linecap='round'/><path d='M20 4v4h-4' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>",
	}
	svg = icons.get(name, icons["dashboard"]).format(color=color)
	return f"<span class='app-icon'>{svg}</span>"


def metric_card(title, value, icon_name, accent, caption):
	return f"""
	<div class='metric-card' style='--accent:{accent};'>
		<div class='metric-card__top'>
			{icon_svg(icon_name, accent)}
			<span class='metric-card__title'>{title}</span>
		</div>
		<div class='metric-card__value'>{value}</div>
		<div class='metric-card__caption'>{caption}</div>
	</div>
	"""


def format_log_row(entry):
	if isinstance(entry, dict) and entry.get("error"):
		return {
			"level": "ERROR",
			"message": entry["error"],
			"timestamp": "—",
			"extras": "",
		}

	if not isinstance(entry, dict):
		return {
			"level": "INFO",
			"message": str(entry),
			"timestamp": "—",
			"extras": "",
		}

	message = entry.get("message", "")
	timestamp = entry.get("timestamp", "—")
	level = entry.get("level", "INFO")
	extras = entry.get("extras", {})
	if extras:
		extra_text = ", ".join(f"{key}={value}" for key, value in extras.items())
	else:
		extra_text = ""
	return {
		"level": level,
		"message": message,
		"timestamp": timestamp,
		"extras": extra_text,
	}


st.markdown(
	"""
	<style>
		:root {
			--bg: #0b1020;
			--panel: rgba(13, 20, 40, 0.78);
			--panel-strong: rgba(16, 24, 46, 0.96);
			--line: rgba(148, 163, 184, 0.18);
			--text: #e5eefb;
			--muted: #99a7c0;
			--blue: #60a5fa;
			--cyan: #2dd4bf;
			--green: #4ade80;
			--amber: #fbbf24;
			--red: #f87171;
		}

		.stApp {
			background:
				radial-gradient(circle at top left, rgba(96, 165, 250, 0.18), transparent 28%),
				radial-gradient(circle at top right, rgba(45, 212, 191, 0.12), transparent 22%),
				linear-gradient(180deg, #09101d 0%, #0f172a 45%, #111827 100%);
			color: var(--text);
		}

		.block-container {
			padding-top: 1.5rem;
			padding-bottom: 2rem;
			max-width: 1240px;
		}

		.app-shell {
			border: 1px solid var(--line);
			background: linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(10, 15, 28, 0.92));
			backdrop-filter: blur(16px);
			border-radius: 24px;
			padding: 1.5rem;
			box-shadow: 0 20px 80px rgba(2, 6, 23, 0.35);
		}

		.hero {
			display: flex;
			justify-content: space-between;
			gap: 1rem;
			align-items: flex-start;
			padding-bottom: 1.25rem;
			border-bottom: 1px solid var(--line);
		}

		.hero__eyebrow {
			display: inline-flex;
			align-items: center;
			gap: 0.55rem;
			font-size: 0.82rem;
			text-transform: uppercase;
			letter-spacing: 0.16em;
			color: var(--muted);
		}

		.hero__title {
			font-size: clamp(2rem, 4vw, 3.4rem);
			font-weight: 800;
			line-height: 1.02;
			margin: 0.4rem 0 0.7rem;
			color: var(--text);
		}

		.hero__copy {
			max-width: 760px;
			font-size: 1rem;
			line-height: 1.6;
			color: var(--muted);
			margin: 0;
		}

		.hero__meta {
			display: grid;
			gap: 0.75rem;
			min-width: 250px;
		}

		.meta-pill {
			display: flex;
			align-items: center;
			gap: 0.75rem;
			padding: 0.9rem 1rem;
			border-radius: 16px;
			background: rgba(15, 23, 42, 0.76);
			border: 1px solid var(--line);
		}

		.meta-pill__label {
			font-size: 0.76rem;
			text-transform: uppercase;
			letter-spacing: 0.12em;
			color: var(--muted);
		}

		.meta-pill__value {
			font-size: 0.98rem;
			font-weight: 700;
			color: var(--text);
		}

		.icon-badge,
		.app-icon {
			display: inline-flex;
			align-items: center;
			justify-content: center;
			width: 2rem;
			height: 2rem;
			border-radius: 12px;
			background: rgba(96, 165, 250, 0.12);
			border: 1px solid rgba(96, 165, 250, 0.22);
			flex-shrink: 0;
		}

		.app-icon svg {
			width: 1rem;
			height: 1rem;
		}

		.section-heading {
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 1rem;
			margin: 1.5rem 0 0.9rem;
		}

		.section-heading h2 {
			font-size: 1.05rem;
			margin: 0;
			color: var(--text);
		}

		.section-heading p {
			margin: 0;
			color: var(--muted);
			font-size: 0.92rem;
		}

		.metric-card {
			height: 100%;
			padding: 1rem 1rem 0.95rem;
			border-radius: 18px;
			background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(8, 15, 30, 0.96));
			border: 1px solid var(--line);
			box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
		}

		.metric-card__top {
			display: flex;
			align-items: center;
			gap: 0.75rem;
			margin-bottom: 0.85rem;
		}

		.metric-card__title {
			font-size: 0.88rem;
			font-weight: 700;
			color: var(--muted);
			letter-spacing: 0.02em;
		}

		.metric-card__value {
			font-size: 2rem;
			font-weight: 800;
			line-height: 1;
			color: var(--text);
		}

		.metric-card__caption {
			margin-top: 0.6rem;
			font-size: 0.88rem;
			color: var(--muted);
		}

		.status-row {
			display: grid;
			grid-template-columns: repeat(2, minmax(0, 1fr));
			gap: 0.75rem;
			margin-top: 0.75rem;
		}

		.status-card {
			padding: 0.95rem;
			border-radius: 16px;
			border: 1px solid var(--line);
			background: rgba(15, 23, 42, 0.72);
		}

		.status-card__label {
			font-size: 0.78rem;
			text-transform: uppercase;
			letter-spacing: 0.11em;
			color: var(--muted);
		}

		.status-card__value {
			display: flex;
			align-items: center;
			gap: 0.55rem;
			margin-top: 0.55rem;
			font-size: 1rem;
			font-weight: 700;
			color: var(--text);
		}

		.status-dot {
			width: 0.55rem;
			height: 0.55rem;
			border-radius: 999px;
			box-shadow: 0 0 14px currentColor;
		}

		.status-dot--good {
			color: var(--green);
			background: var(--green);
		}

		.status-dot--bad {
			color: var(--red);
			background: var(--red);
		}

		.status-dot--warn {
			color: var(--amber);
			background: var(--amber);
		}

		.log-list {
			display: grid;
			gap: 0.75rem;
		}

		.log-card {
			padding: 0.95rem 1rem;
			border-radius: 16px;
			border: 1px solid var(--line);
			background: rgba(15, 23, 42, 0.72);
		}

		.log-card__top {
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 1rem;
			margin-bottom: 0.5rem;
		}

		.log-card__level {
			display: inline-flex;
			align-items: center;
			gap: 0.45rem;
			padding: 0.25rem 0.6rem;
			border-radius: 999px;
			font-size: 0.74rem;
			font-weight: 700;
			letter-spacing: 0.08em;
			text-transform: uppercase;
			background: rgba(96, 165, 250, 0.12);
			color: var(--blue);
		}

		.log-card__level[data-level='ERROR'] {
			background: rgba(248, 113, 113, 0.12);
			color: var(--red);
		}

		.log-card__level[data-level='WARNING'] {
			background: rgba(251, 191, 36, 0.12);
			color: var(--amber);
		}

		.log-card__message {
			font-size: 0.98rem;
			font-weight: 600;
			color: var(--text);
			margin: 0;
		}

		.log-card__meta {
			margin-top: 0.35rem;
			font-size: 0.84rem;
			line-height: 1.5;
			color: var(--muted);
			word-break: break-word;
		}

		.footer-actions {
			display: flex;
			justify-content: flex-end;
			margin-top: 1rem;
		}

		.stButton button {
			border-radius: 999px !important;
			border: 1px solid rgba(96, 165, 250, 0.3) !important;
			background: linear-gradient(135deg, rgba(37, 99, 235, 0.95), rgba(14, 165, 233, 0.9)) !important;
			color: white !important;
			padding: 0.65rem 1.15rem !important;
			font-weight: 700 !important;
			box-shadow: 0 12px 30px rgba(37, 99, 235, 0.2) !important;
		}
	</style>
	""",
	unsafe_allow_html=True,
)


st.markdown(
	"""
	<div class='app-shell'>
		<div class='hero'>
			<div>
				<div class='hero__eyebrow'>
					{icon}
					<span>Operational overview</span>
				</div>
				<h1 class='hero__title'>DevOps Control Plane</h1>
				<p class='hero__copy'>A polished live view of system health, resource pressure, and recent structured logs. The dashboard updates automatically and keeps the most relevant operational signals in one place.</p>
			</div>
			<div class='hero__meta'>
				<div class='meta-pill'>
					{pulse_icon}
					<div>
						<div class='meta-pill__label'>Refresh cadence</div>
						<div class='meta-pill__value'>{refresh}s auto update</div>
					</div>
				</div>
				<div class='meta-pill'>
					{shield_icon}
					<div>
						<div class='meta-pill__label'>System status</div>
						<div class='meta-pill__value'>{status_text}</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	""".format(
		icon=icon_svg("dashboard", "#60a5fa"),
		pulse_icon=icon_svg("pulse", "#2dd4bf"),
		shield_icon=icon_svg("shield", "#4ade80"),
		refresh=REFRESH_RATE,
		status_text="All systems nominal" if readiness() and liveness() else "Attention required",
	),
	unsafe_allow_html=True,
)


def read_logs():
	try:
		with open("/app/logs/app.json.log", "r") as f:
			lines = f.readlines()
			last_lines = lines[-10:] if len(lines) > 10 else lines
			parsed = []
			for line in last_lines:
				try:
					parsed.append(json.loads(line.strip()))
				except json.JSONDecodeError:
					parsed.append({"error": "malformed log line"})
			return parsed
	except FileNotFoundError:
		return []


st_autorefresh(interval=REFRESH_RATE * 1000, key="dashboard_refresh")


cpu = get_cpu(interval=0.1)
ram = get_ram()
disk = get_disk()
ready = readiness()
live = liveness()
logs = list(reversed(read_logs()))


st.markdown("<div class='section-heading'><h2>Live metrics</h2><p>Current utilization and readiness across the container</p></div>", unsafe_allow_html=True)

metric_columns = st.columns(5)
metric_data = [
	("CPU", f"{cpu:.1f}%", "cpu", "#60a5fa", "Processor utilization"),
	("Memory", f"{ram:.1f}%", "ram", "#2dd4bf", "Resident memory pressure"),
	("Storage", f"{disk:.1f}%", "disk", "#fbbf24", "Remaining free disk space"),
	("Readiness", "Ready" if ready else "Not ready", "shield", "#4ade80" if ready else "#f87171", "Application readiness probe"),
	("Liveness", "Live" if live else "Down", "pulse", "#4ade80" if live else "#f87171", "Application heartbeat probe"),
]

for column, item in zip(metric_columns, metric_data):
	with column:
		st.markdown(metric_card(*item), unsafe_allow_html=True)


st.markdown("<div class='section-heading'><h2>Operations</h2><p>Recent activity and a quick action to write a refresh event</p></div>", unsafe_allow_html=True)

left_column, right_column = st.columns([1.05, 1.35], gap="large")

with left_column:
	st.markdown(
		"""
		<div class='status-card'>
			<div class='status-card__label'>Health summary</div>
			<div class='status-row'>
				<div>
					<div class='status-card__label'>Readiness</div>
					<div class='status-card__value'><span class='status-dot {ready_class}'></span>{ready_text}</div>
				</div>
				<div>
					<div class='status-card__label'>Liveness</div>
					<div class='status-card__value'><span class='status-dot {live_class}'></span>{live_text}</div>
				</div>
			</div>
			<div class='status-row'>
				<div>
					<div class='status-card__label'>Refresh rate</div>
					<div class='status-card__value'>{refresh}s</div>
				</div>
				<div>
					<div class='status-card__label'>Last update</div>
					<div class='status-card__value'>{last_update}</div>
				</div>
			</div>
		</div>
		""".format(
			ready_class="status-dot--good" if ready else "status-dot--bad",
			live_class="status-dot--good" if live else "status-dot--bad",
			ready_text="Ready" if ready else "Not ready",
			live_text="Live" if live else "Down",
			refresh=REFRESH_RATE,
			last_update=datetime.utcnow().strftime("%H:%M:%S UTC"),
		),
		unsafe_allow_html=True,
	)

	with st.container():
		st.markdown(
			"""
			<div class='footer-actions'>
				<div class='icon-badge'>{icon}</div>
			</div>
			""".format(icon=icon_svg("refresh", "#60a5fa")),
			unsafe_allow_html=True,
		)
		if st.button("Refresh now", use_container_width=True):
			struct_log("info", "UI refreshed", cpu=cpu, ram=ram, disk=disk)
			st.experimental_rerun()

with right_column:
	st.markdown(
		"""
		<div class='status-card'>
			<div class='status-card__label'>Recent structured logs</div>
		</div>
		""",
		unsafe_allow_html=True,
	)

	if logs:
		for entry in logs[:8]:
			row = format_log_row(entry)
			st.markdown(
				f"""
				<div class='log-card'>
					<div class='log-card__top'>
						<div class='log-card__level' data-level='{row['level']}'>{row['level']}</div>
						<div class='log-card__meta'>{row['timestamp']}</div>
					</div>
					<p class='log-card__message'>{row['message']}</p>
					<div class='log-card__meta'>{row['extras'] or 'No additional context'}</div>
				</div>
				""",
				unsafe_allow_html=True,
			)
	else:
		st.markdown(
			"""
			<div class='log-card'>
				<div class='log-card__top'>
					<div class='log-card__level' data-level='INFO'>INFO</div>
					<div class='log-card__meta'>Waiting for first event</div>
				</div>
				<p class='log-card__message'>No logs have been written yet.</p>
				<div class='log-card__meta'>Use the refresh action to emit a structured activity event.</div>
			</div>
			""",
			unsafe_allow_html=True,
		)
