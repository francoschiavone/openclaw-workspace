"""
SimulAI Demo Server v2 - Multi-page, dynamic, production-feel
"""
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/pylibs')

import json, random, math, time, hashlib
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="SimulAI", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Data ---
TWINS = {
    "cnc-lathe-001": {
        "name": "CNC Lathe #1", "type": "CNC Machine", "location": "Plant A - Line 1",
        "status": "operational", "health": 87, "uptime": 99.2, "mtbf_hrs": 2400,
        "sensors": {"temperature": 72.3, "vibration": 2.1, "rpm": 3200, "power_kw": 15.4, "oil_pressure": 45.2},
        "icon": "⚙️", "img": "cnc"
    },
    "robotic-arm-001": {
        "name": "Robotic Arm #1", "type": "6-Axis Robot", "location": "Plant A - Assembly",
        "status": "operational", "health": 94, "uptime": 99.8, "mtbf_hrs": 4800,
        "sensors": {"temperature": 38.5, "joint_torque": 12.3, "cycle_time_s": 8.2, "accuracy_mm": 0.02, "power_kw": 3.8},
        "icon": "🤖", "img": "robot"
    },
    "hvac-001": {
        "name": "HVAC Unit #1", "type": "Industrial HVAC", "location": "Plant A - Main Hall",
        "status": "warning", "health": 65, "uptime": 95.1, "mtbf_hrs": 1200,
        "sensors": {"supply_temp": 18.2, "return_temp": 24.1, "humidity": 58, "filter_dp_pa": 320, "power_kw": 45.0},
        "icon": "❄️", "img": "hvac"
    },
    "conveyor-001": {
        "name": "Conveyor Belt #3", "type": "Belt Conveyor", "location": "Plant A - Packaging",
        "status": "operational", "health": 78, "uptime": 97.5, "mtbf_hrs": 1800,
        "sensors": {"belt_speed_mps": 1.2, "motor_temp": 55.3, "tension_n": 850, "vibration": 3.1, "power_kw": 8.5},
        "icon": "🏭", "img": "conveyor"
    },
    "pump-001": {
        "name": "Coolant Pump #1", "type": "Centrifugal Pump", "location": "Plant A - Cooling",
        "status": "critical", "health": 43, "uptime": 88.3, "mtbf_hrs": 600,
        "sensors": {"temperature": 89.2, "vibration": 8.7, "flow_rate_lpm": 142, "pressure_bar": 3.2, "power_kw": 7.8},
        "icon": "💧", "img": "pump"
    },
    "generator-001": {
        "name": "Diesel Generator", "type": "Backup Power", "location": "Plant A - Utilities",
        "status": "standby", "health": 92, "uptime": 99.9, "mtbf_hrs": 5000,
        "sensors": {"temperature": 25.0, "fuel_level_pct": 78, "battery_v": 24.1, "runtime_hrs": 1240, "power_kw": 0},
        "icon": "⚡", "img": "generator"
    },
}

ALERTS = [
    {"id": "ALT-001", "twin": "pump-001", "type": "critical", "msg": "Vibration 8.7mm/s exceeds threshold (5.0)", "time": "2 min ago", "sensor": "vibration"},
    {"id": "ALT-002", "twin": "pump-001", "type": "critical", "msg": "Temperature 89.2°C exceeds threshold (80°C)", "time": "5 min ago", "sensor": "temperature"},
    {"id": "ALT-003", "twin": "hvac-001", "type": "warning", "msg": "Filter differential pressure 320Pa (threshold 300Pa)", "time": "12 min ago", "sensor": "filter_dp_pa"},
    {"id": "ALT-004", "twin": "conveyor-001", "type": "warning", "msg": "Belt vibration trending upward: 3.1mm/s", "time": "28 min ago", "sensor": "vibration"},
    {"id": "ALT-005", "twin": "pump-001", "type": "info", "msg": "Maintenance window recommended within 48hrs", "time": "1 hr ago", "sensor": None},
    {"id": "ALT-006", "twin": "cnc-lathe-001", "type": "info", "msg": "Oil pressure within normal range but declining trend", "time": "2 hrs ago", "sensor": "oil_pressure"},
]

def noise(v, p=0.02): return round(v * (1 + random.uniform(-p, p)), 2)

def gen_history(base, hours=24, interval_min=15):
    pts = []
    t = datetime.utcnow() - timedelta(hours=hours)
    for i in range(int(hours * 60 / interval_min)):
        drift = math.sin(i * 0.1) * base * 0.05
        pts.append({"t": (t + timedelta(minutes=i*interval_min)).strftime("%H:%M"), "v": round(base + drift + random.uniform(-base*0.02, base*0.02), 2)})
    return pts

# --- Shared CSS/JS ---
COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#06060b;--surface:#0f0f18;--surface2:#161625;--border:rgba(255,255,255,0.06);--border2:rgba(255,255,255,0.12);--text:#f4f4f5;--text2:#a1a1aa;--text3:#71717a;--accent:#6366f1;--accent2:#818cf8;--teal:#14b8a6;--cyan:#06b6d4;--red:#ef4444;--amber:#f59e0b;--green:#22c55e}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);overflow-x:hidden}
a{color:inherit;text-decoration:none}

/* NAV */
.nav{display:flex;align-items:center;padding:16px 32px;background:var(--surface);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;backdrop-filter:blur(20px)}
.nav-logo{font-size:1.4rem;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-right:40px}
.nav-links{display:flex;gap:8px}
.nav-link{padding:8px 16px;border-radius:8px;font-size:0.85rem;font-weight:500;color:var(--text2);transition:all 0.2s;cursor:pointer}
.nav-link:hover,.nav-link.active{background:var(--surface2);color:var(--text)}
.nav-link.active{background:rgba(99,102,241,0.15);color:var(--accent2)}
.nav-right{margin-left:auto;display:flex;align-items:center;gap:16px}
.nav-badge{background:var(--red);color:#fff;font-size:0.7rem;padding:2px 8px;border-radius:10px;font-weight:700}
.nav-avatar{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--cyan))}
.nav-user{font-size:0.85rem;color:var(--text2)}

/* LAYOUT */
.page{padding:32px;max-width:1440px;margin:0 auto;animation:fadeIn 0.3s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.page-title{font-size:1.8rem;font-weight:800;margin-bottom:4px}
.page-sub{color:var(--text2);margin-bottom:28px;font-size:0.9rem}

/* CARDS */
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:24px;transition:all 0.25s}
.card:hover{border-color:var(--border2);transform:translateY(-2px)}

/* GRID */
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}

/* KPI */
.kpi{text-align:center;padding:20px}
.kpi-value{font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.kpi-label{color:var(--text3);font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;margin-top:4px}

/* TABLE */
.table{width:100%;border-collapse:collapse}
.table th{text-align:left;padding:12px 16px;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--text3);border-bottom:1px solid var(--border)}
.table td{padding:12px 16px;border-bottom:1px solid var(--border);font-size:0.85rem}
.table tr:hover td{background:var(--surface2)}

/* BADGES */
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.03em}
.badge-operational{background:rgba(34,197,94,0.12);color:var(--green)}
.badge-warning{background:rgba(245,158,11,0.12);color:var(--amber)}
.badge-critical{background:rgba(239,68,68,0.12);color:var(--red)}
.badge-standby{background:rgba(161,161,170,0.12);color:var(--text3)}
.badge-info{background:rgba(6,182,212,0.12);color:var(--cyan)}

/* HEALTH BAR */
.hbar{height:6px;background:var(--surface2);border-radius:3px;overflow:hidden;margin:8px 0}
.hbar-fill{height:100%;border-radius:3px;transition:width 0.8s ease}

/* BUTTONS */
.btn{padding:10px 20px;border-radius:10px;border:none;cursor:pointer;font-family:'Inter',sans-serif;font-size:0.82rem;font-weight:600;transition:all 0.2s;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:linear-gradient(135deg,var(--accent),#8b5cf6);color:#fff}
.btn-primary:hover{filter:brightness(1.15);transform:translateY(-1px)}
.btn-ghost{background:rgba(255,255,255,0.05);color:var(--text2);border:1px solid var(--border)}
.btn-ghost:hover{background:rgba(255,255,255,0.08);color:var(--text)}
.btn-danger{background:rgba(239,68,68,0.12);color:var(--red);border:1px solid rgba(239,68,68,0.2)}
.btn-sm{padding:6px 14px;font-size:0.75rem;border-radius:8px}

/* CHART PLACEHOLDER */
.chart{background:var(--surface2);border-radius:12px;padding:20px;position:relative;overflow:hidden}
.chart-title{font-size:0.8rem;color:var(--text3);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:12px}
.sparkline{display:flex;align-items:end;gap:2px;height:80px}
.spark-bar{flex:1;background:var(--accent);border-radius:2px 2px 0 0;transition:height 0.3s;opacity:0.7}
.spark-bar:hover{opacity:1}

/* SENSOR */
.sensor-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px}
.sensor-item{background:var(--surface2);border-radius:10px;padding:12px}
.sensor-name{font-size:0.68rem;color:var(--text3);text-transform:uppercase;letter-spacing:0.04em}
.sensor-val{font-size:1.3rem;font-weight:700;color:var(--teal);margin-top:2px}
.sensor-val.warn{color:var(--amber)}
.sensor-val.crit{color:var(--red)}

/* ALERTS */
.alert-item{display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:10px;margin-bottom:8px;transition:all 0.2s}
.alert-item:hover{background:var(--surface2)}
.alert-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.alert-dot.critical{background:var(--red);box-shadow:0 0 8px var(--red)}
.alert-dot.warning{background:var(--amber);box-shadow:0 0 8px var(--amber)}
.alert-dot.info{background:var(--cyan)}
.alert-text{flex:1;font-size:0.85rem}
.alert-twin{color:var(--text3);font-size:0.75rem}
.alert-time{color:var(--text3);font-size:0.75rem;white-space:nowrap}

/* SIMULATION */
.sim-panel{background:var(--surface2);border-radius:12px;padding:24px;border:1px solid var(--border)}
.sim-slider{width:100%;margin:12px 0;accent-color:var(--accent)}
.sim-result{margin-top:16px;padding:16px;background:var(--surface);border-radius:10px;border-left:3px solid var(--accent)}
.impact-bar{display:flex;align-items:center;gap:12px;margin:8px 0}
.impact-label{width:120px;font-size:0.8rem;color:var(--text2)}
.impact-track{flex:1;height:8px;background:var(--surface2);border-radius:4px;overflow:hidden}
.impact-fill{height:100%;border-radius:4px;transition:width 0.5s}

/* PULSE animation for critical */
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
.pulse{animation:pulse 2s infinite}

/* TWIN CARD (dashboard) */
.twin-card{cursor:pointer}
.twin-card .twin-header{display:flex;justify-content:space-between;align-items:start;margin-bottom:14px}
.twin-card .twin-icon{font-size:1.8rem}
.twin-card .twin-name{font-size:1rem;font-weight:700}
.twin-card .twin-type{font-size:0.75rem;color:var(--text3)}
.twin-card .twin-loc{font-size:0.72rem;color:var(--text3);margin-top:2px}
.twin-card .twin-meta{display:flex;gap:16px;margin-top:14px}
.twin-card .twin-meta-item{font-size:0.75rem;color:var(--text3)}
.twin-card .twin-meta-item span{color:var(--text);font-weight:600}

/* SCROLLBAR */
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--surface2);border-radius:3px}
</style>
"""

NAV_HTML = """
<nav class="nav">
  <div class="nav-logo">SimulAI</div>
  <div class="nav-links">
    <a href="/dashboard" class="nav-link {active_dash}">Dashboard</a>
    <a href="/alerts" class="nav-link {active_alerts}">Alerts <span class="nav-badge">3</span></a>
    <a href="/simulation" class="nav-link {active_sim}">Simulation Lab</a>
    <a href="/analytics" class="nav-link {active_analytics}">Analytics</a>
  </div>
  <div class="nav-right">
    <span class="nav-user">Plant A — Rosario</span>
    <div class="nav-avatar"></div>
  </div>
</nav>
"""

def nav(active="dash"):
    return NAV_HTML.format(
        active_dash="active" if active=="dash" else "",
        active_alerts="active" if active=="alerts" else "",
        active_sim="active" if active=="sim" else "",
        active_analytics="active" if active=="analytics" else "",
    )

def page_wrap(title, subtitle, content, active="dash"):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>SimulAI - {title}</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔮</text></svg>">
    {COMMON_CSS}</head><body>{nav(active)}
    <div class="page"><h1 class="page-title">{title}</h1><p class="page-sub">{subtitle}</p>{content}</div></body></html>"""

# ---- ROUTES ----

@app.get("/", response_class=HTMLResponse)
def root():
    from starlette.responses import RedirectResponse
    return RedirectResponse("/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    # KPIs
    total = len(TWINS)
    healthy = sum(1 for t in TWINS.values() if t["health"] >= 80)
    warnings = sum(1 for t in TWINS.values() if 50 <= t["health"] < 80)
    critical = sum(1 for t in TWINS.values() if t["health"] < 50)
    avg_health = round(sum(t["health"] for t in TWINS.values()) / total, 1)
    
    kpis = f"""
    <div class="grid-4" style="margin-bottom:28px">
      <div class="card kpi"><div class="kpi-value">{total}</div><div class="kpi-label">Active Twins</div></div>
      <div class="card kpi"><div class="kpi-value" style="background:linear-gradient(135deg,var(--green),var(--teal));-webkit-background-clip:text;-webkit-text-fill-color:transparent">{avg_health}%</div><div class="kpi-label">Avg Health</div></div>
      <div class="card kpi"><div class="kpi-value" style="background:linear-gradient(135deg,var(--amber),#f97316);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{warnings}</div><div class="kpi-label">Warnings</div></div>
      <div class="card kpi"><div class="kpi-value" style="background:linear-gradient(135deg,var(--red),#dc2626);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{critical}</div><div class="kpi-label">Critical</div></div>
    </div>"""
    
    # Twin cards
    cards = ""
    for tid, t in TWINS.items():
        hcolor = "var(--green)" if t["health"]>=80 else "var(--amber)" if t["health"]>=50 else "var(--red)"
        cards += f"""
        <a href="/twin/{tid}" class="card twin-card">
          <div class="twin-header">
            <div>
              <div style="display:flex;align-items:center;gap:8px"><span class="twin-icon">{t['icon']}</span><span class="twin-name">{t['name']}</span></div>
              <div class="twin-type">{t['type']}</div>
              <div class="twin-loc">📍 {t['location']}</div>
            </div>
            <span class="badge badge-{t['status']}{"  pulse" if t["status"]=="critical" else ""}">{t['status']}</span>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem">
            <span style="color:var(--text3)">Health Score</span>
            <span style="color:{hcolor};font-weight:700">{t['health']}%</span>
          </div>
          <div class="hbar"><div class="hbar-fill" style="width:{t['health']}%;background:{hcolor}"></div></div>
          <div class="twin-meta">
            <div class="twin-meta-item">Uptime: <span>{t['uptime']}%</span></div>
            <div class="twin-meta-item">MTBF: <span>{t['mtbf_hrs']}h</span></div>
            <div class="twin-meta-item">Power: <span>{t['sensors'].get('power_kw',0)} kW</span></div>
          </div>
        </a>"""
    
    content = kpis + f'<div class="grid-3">{cards}</div>'
    return page_wrap("Dashboard", f"Real-time monitoring — {total} active digital twins • Last updated: {datetime.utcnow().strftime('%H:%M:%S')} UTC", content, "dash")

@app.get("/twin/{twin_id}", response_class=HTMLResponse)
def twin_detail(twin_id: str):
    t = TWINS.get(twin_id)
    if not t:
        return page_wrap("Not Found", "", "<p>Twin not found</p>")
    
    hcolor = "var(--green)" if t["health"]>=80 else "var(--amber)" if t["health"]>=50 else "var(--red)"
    
    # Sensors
    sensors_html = ""
    for sname, sval in t["sensors"].items():
        cls = ""
        thresholds = {"temperature": 80, "vibration": 5, "filter_dp_pa": 300}
        if sname in thresholds and sval > thresholds[sname]:
            cls = "crit"
        elif sname in thresholds and sval > thresholds[sname] * 0.85:
            cls = "warn"
        sensors_html += f'<div class="sensor-item"><div class="sensor-name">{sname.replace("_"," ")}</div><div class="sensor-val {cls}">{noise(sval)}</div></div>'
    
    # Sparklines
    spark_data = gen_history(list(t["sensors"].values())[0])
    bars = ""
    maxv = max(p["v"] for p in spark_data)
    for p in spark_data[-48:]:
        h = max(4, int(p["v"] / maxv * 80))
        bars += f'<div class="spark-bar" style="height:{h}px" title="{p["t"]}: {p["v"]}"></div>'
    
    # AI Prediction
    health = t["health"]
    if health < 50:
        risk, risk_cls, days = "HIGH", "critical", random.randint(2,5)
        conf = round(random.uniform(0.85, 0.95), 2)
    elif health < 75:
        risk, risk_cls, days = "MEDIUM", "warning", random.randint(14,45)
        conf = round(random.uniform(0.70, 0.85), 2)
    else:
        risk, risk_cls, days = "LOW", "info", random.randint(90,365)
        conf = round(random.uniform(0.75, 0.92), 2)
    
    content = f"""
    <a href="/dashboard" style="color:var(--text3);font-size:0.85rem;margin-bottom:20px;display:inline-block">← Back to Dashboard</a>
    
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px">
      <span style="font-size:3rem">{t['icon']}</span>
      <div>
        <h2 style="font-size:1.5rem;font-weight:800">{t['name']}</h2>
        <div style="color:var(--text3)">{t['type']} • {t['location']}</div>
      </div>
      <span class="badge badge-{t['status']}" style="margin-left:auto;font-size:0.85rem;padding:8px 20px">{t['status']}</span>
    </div>
    
    <div class="grid-3" style="margin-bottom:24px">
      <div class="card" style="text-align:center">
        <div style="font-size:2.5rem;font-weight:800;color:{hcolor}">{t['health']}%</div>
        <div class="hbar"><div class="hbar-fill" style="width:{t['health']}%;background:{hcolor}"></div></div>
        <div style="color:var(--text3);font-size:0.8rem;margin-top:8px">Health Score</div>
      </div>
      <div class="card" style="text-align:center">
        <div style="font-size:2.5rem;font-weight:800;color:var(--teal)">{t['uptime']}%</div>
        <div style="color:var(--text3);font-size:0.8rem;margin-top:8px">Uptime (30d)</div>
      </div>
      <div class="card" style="text-align:center">
        <div style="font-size:2.5rem;font-weight:800;color:var(--accent2)">{t['mtbf_hrs']}h</div>
        <div style="color:var(--text3);font-size:0.8rem;margin-top:8px">Mean Time Between Failures</div>
      </div>
    </div>
    
    <div class="grid-2" style="margin-bottom:24px">
      <div class="card">
        <h3 style="font-size:0.95rem;font-weight:700;margin-bottom:16px">Live Sensors</h3>
        <div class="sensor-grid">{sensors_html}</div>
      </div>
      <div class="card">
        <h3 style="font-size:0.95rem;font-weight:700;margin-bottom:16px">Sensor History (24h)</h3>
        <div class="chart"><div class="chart-title">{list(t["sensors"].keys())[0].replace('_',' ').title()}</div>
        <div class="sparkline">{bars}</div></div>
      </div>
    </div>
    
    <div class="card" style="border-left:3px solid {"var(--red)" if risk=="HIGH" else "var(--amber)" if risk=="MEDIUM" else "var(--teal)"}">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <h3 style="font-size:0.95rem;font-weight:700">🔮 AI Failure Prediction</h3>
        <span class="badge badge-{risk_cls}" style="font-size:0.85rem;padding:6px 16px">{risk} RISK</span>
      </div>
      <div class="grid-3">
        <div><div style="color:var(--text3);font-size:0.75rem">Est. Days to Failure</div><div style="font-size:1.5rem;font-weight:700">{days}</div></div>
        <div><div style="color:var(--text3);font-size:0.75rem">Confidence</div><div style="font-size:1.5rem;font-weight:700">{int(conf*100)}%</div></div>
        <div><div style="color:var(--text3);font-size:0.75rem">Cost Avoidable</div><div style="font-size:1.5rem;font-weight:700;color:var(--green)">USD ${random.randint(5,75)}K</div></div>
      </div>
      <div style="margin-top:12px;padding:12px;background:var(--surface2);border-radius:8px;font-size:0.85rem;color:var(--text2)">
        <strong style="color:var(--text)">Model:</strong> SimulAI Predictor v0.3 — Gradient Boosting + LSTM ensemble trained on 2.4M sensor readings
      </div>
    </div>
    """
    return page_wrap(t["name"], f"{t['type']} — {t['location']}", content, "dash")

@app.get("/alerts", response_class=HTMLResponse)
def alerts_page():
    items = ""
    for a in ALERTS:
        twin = TWINS.get(a["twin"], {})
        items += f"""
        <div class="alert-item">
          <div class="alert-dot {a['type']}"></div>
          <div class="alert-text">
            <div>{a['msg']}</div>
            <div class="alert-twin">{twin.get('icon','')} {twin.get('name','Unknown')} • {a['id']}</div>
          </div>
          <div class="alert-time">{a['time']}</div>
          <button class="btn btn-sm btn-ghost">Acknowledge</button>
        </div>"""
    
    # Summary
    crit = sum(1 for a in ALERTS if a['type']=='critical')
    warn = sum(1 for a in ALERTS if a['type']=='warning')
    info = sum(1 for a in ALERTS if a['type']=='info')
    
    content = f"""
    <div class="grid-3" style="margin-bottom:28px">
      <div class="card kpi"><div class="kpi-value" style="background:linear-gradient(135deg,var(--red),#dc2626);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{crit}</div><div class="kpi-label">Critical Alerts</div></div>
      <div class="card kpi"><div class="kpi-value" style="background:linear-gradient(135deg,var(--amber),#f97316);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{warn}</div><div class="kpi-label">Warnings</div></div>
      <div class="card kpi"><div class="kpi-value" style="background:linear-gradient(135deg,var(--cyan),var(--teal));-webkit-background-clip:text;-webkit-text-fill-color:transparent">{info}</div><div class="kpi-label">Informational</div></div>
    </div>
    <div class="card">{items}</div>
    """
    return page_wrap("Alerts", f"{len(ALERTS)} active alerts across all monitored twins", content, "alerts")

@app.get("/simulation", response_class=HTMLResponse)
def simulation_page():
    # Build twin options
    opts = "".join(f'<option value="{tid}">{t["name"]} ({t["type"]})</option>' for tid, t in TWINS.items())
    
    content = f"""
    <div class="grid-2">
      <div class="card">
        <h3 style="font-size:1rem;font-weight:700;margin-bottom:20px">🎮 Simulation Configuration</h3>
        <div style="margin-bottom:16px">
          <label style="font-size:0.8rem;color:var(--text3);display:block;margin-bottom:6px">Select Digital Twin</label>
          <select id="sim-twin" style="width:100%;padding:10px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:'Inter';font-size:0.9rem" onchange="updateSim()">{opts}</select>
        </div>
        <div style="margin-bottom:16px">
          <label style="font-size:0.8rem;color:var(--text3);display:block;margin-bottom:6px">Scenario Type</label>
          <div style="display:flex;gap:8px">
            <button class="btn btn-primary btn-sm" onclick="setScenario('load')">Load Change</button>
            <button class="btn btn-ghost btn-sm" onclick="setScenario('maintenance')">Maintenance Delay</button>
            <button class="btn btn-ghost btn-sm" onclick="setScenario('environment')">Environment</button>
          </div>
        </div>
        <div style="margin-bottom:16px">
          <label style="font-size:0.8rem;color:var(--text3);display:block;margin-bottom:6px">Parameter Adjustment: <span id="sim-val" style="color:var(--accent2);font-weight:700">+25%</span></label>
          <input type="range" class="sim-slider" id="sim-range" min="-50" max="100" value="25" oninput="document.getElementById('sim-val').textContent=(this.value>0?'+':'')+this.value+'%'">
        </div>
        <div style="margin-bottom:16px">
          <label style="font-size:0.8rem;color:var(--text3);display:block;margin-bottom:6px">Simulation Iterations</label>
          <div style="display:flex;gap:8px;align-items:center">
            <input type="number" value="1000" style="width:100px;padding:8px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:'Inter'" id="sim-iter">
            <span style="color:var(--text3);font-size:0.8rem">Monte Carlo runs</span>
          </div>
        </div>
        <button class="btn btn-primary" onclick="runSim()" style="width:100%;justify-content:center;padding:14px" id="sim-btn">▶ Run Simulation</button>
      </div>
      
      <div class="card" id="sim-results">
        <h3 style="font-size:1rem;font-weight:700;margin-bottom:20px">📊 Results</h3>
        <div style="color:var(--text3);text-align:center;padding:60px 0">
          <div style="font-size:3rem;margin-bottom:12px">🎯</div>
          <div>Configure parameters and run a simulation</div>
          <div style="font-size:0.8rem;margin-top:8px">Results will appear here with impact analysis</div>
        </div>
      </div>
    </div>
    
    <div class="card" style="margin-top:20px">
      <h3 style="font-size:1rem;font-weight:700;margin-bottom:16px">📋 Recent Simulations</h3>
      <table class="table">
        <tr><th>Twin</th><th>Scenario</th><th>Change</th><th>Key Impact</th><th>Risk Delta</th><th>Run At</th></tr>
        <tr><td>⚙️ CNC Lathe #1</td><td>Load Change</td><td>RPM +40%</td><td>Wear +85%, Energy +53%</td><td><span style="color:var(--red)">↑ HIGH</span></td><td>2 min ago</td></tr>
        <tr><td>💧 Coolant Pump #1</td><td>Maintenance Delay</td><td>+7 days</td><td>Failure prob. 94%</td><td><span style="color:var(--red)">↑ CRITICAL</span></td><td>15 min ago</td></tr>
        <tr><td>❄️ HVAC Unit #1</td><td>Environment</td><td>Ambient +5°C</td><td>Efficiency -12%</td><td><span style="color:var(--amber)">↑ MEDIUM</span></td><td>1 hr ago</td></tr>
        <tr><td>🏭 Conveyor Belt #3</td><td>Load Change</td><td>Speed +20%</td><td>Motor stress +35%</td><td><span style="color:var(--amber)">↗ LOW→MED</span></td><td>3 hrs ago</td></tr>
      </table>
    </div>
    
    <script>
    function runSim() {{
      const btn = document.getElementById('sim-btn');
      const results = document.getElementById('sim-results');
      btn.textContent = '⏳ Running 1000 simulations...';
      btn.style.opacity = '0.6';
      
      setTimeout(() => {{
        const change = parseInt(document.getElementById('sim-range').value);
        const dir = change > 0 ? 'increase' : 'decrease';
        const abs = Math.abs(change);
        
        results.innerHTML = `
          <h3 style="font-size:1rem;font-weight:700;margin-bottom:20px">📊 Simulation Results</h3>
          <div style="display:flex;gap:12px;margin-bottom:20px">
            <span class="badge badge-${{abs > 30 ? 'critical' : abs > 15 ? 'warning' : 'info'}}" style="font-size:0.85rem;padding:8px 16px">
              ${{abs > 30 ? 'HIGH IMPACT' : abs > 15 ? 'MODERATE' : 'LOW IMPACT'}}
            </span>
            <span style="color:var(--text3);font-size:0.85rem;display:flex;align-items:center">1000 iterations • 95% CI</span>
          </div>
          
          <div style="margin-bottom:16px">
            <div class="impact-bar"><div class="impact-label">Energy Cost</div><div class="impact-track"><div class="impact-fill" style="width:${{Math.min(100,abs*1.3)}}%;background:${{change>0?'var(--amber)':'var(--green)'}}"></div></div><span style="font-size:0.85rem;color:var(--text2);width:60px;text-align:right">${{change>0?'+':''}}${{(change*1.3).toFixed(0)}}%</span></div>
            <div class="impact-bar"><div class="impact-label">Wear Rate</div><div class="impact-track"><div class="impact-fill" style="width:${{Math.min(100,abs*2.1)}}%;background:var(--red)"></div></div><span style="font-size:0.85rem;color:var(--text2);width:60px;text-align:right">+${{(abs*2.1).toFixed(0)}}%</span></div>
            <div class="impact-bar"><div class="impact-label">Throughput</div><div class="impact-track"><div class="impact-fill" style="width:${{Math.min(100,abs*0.85)}}%;background:var(--teal)"></div></div><span style="font-size:0.85rem;color:var(--text2);width:60px;text-align:right">${{change>0?'+':''}}${{(change*0.85).toFixed(0)}}%</span></div>
            <div class="impact-bar"><div class="impact-label">Failure Risk</div><div class="impact-track"><div class="impact-fill" style="width:${{Math.min(100,abs*1.8)}}%;background:var(--red)"></div></div><span style="font-size:0.85rem;color:var(--text2);width:60px;text-align:right">+${{(abs*1.8).toFixed(0)}}%</span></div>
          </div>
          
          <div style="padding:14px;background:var(--surface2);border-radius:10px;font-size:0.85rem;border-left:3px solid ${{abs > 30 ? 'var(--red)' : 'var(--amber)'}}">
            <strong>💡 AI Recommendation:</strong> ${{abs > 30 ? 
              'High risk scenario. Not recommended without additional safeguards and continuous monitoring.' : 
              abs > 15 ? 'Proceed with caution. Increase monitoring frequency and prepare maintenance team.' :
              'Safe to implement. Monitor for 48 hours after change.'
            }}
          </div>
          <div style="margin-top:12px;font-size:0.75rem;color:var(--text3)">Model: SimulAI Simulator v0.2 — Monte Carlo + Physics-Informed Neural Network • Confidence: ${{(85 + Math.random()*10).toFixed(0)}}%</div>
        `;
        btn.textContent = '▶ Run Simulation';
        btn.style.opacity = '1';
      }}, 2000);
    }}
    function setScenario(s) {{ }}
    function updateSim() {{ }}
    </script>
    """
    return page_wrap("Simulation Lab", "Run what-if scenarios on any digital twin using AI-powered Monte Carlo simulation", content, "sim")

@app.get("/analytics", response_class=HTMLResponse)
def analytics_page():
    # Generate sparkline bars for different metrics
    def spark(base, count=36, color="var(--accent)"):
        pts = [base + random.uniform(-base*0.15, base*0.15) + math.sin(i*0.3)*base*0.08 for i in range(count)]
        maxv = max(pts)
        return "".join(f'<div class="spark-bar" style="height:{max(4,int(v/maxv*70))}px;background:{color}"></div>' for v in pts)
    
    content = f"""
    <div class="grid-4" style="margin-bottom:28px">
      <div class="card kpi"><div class="kpi-value">$142K</div><div class="kpi-label">Costs Avoided (YTD)</div></div>
      <div class="card kpi"><div class="kpi-value" style="background:linear-gradient(135deg,var(--green),var(--teal));-webkit-background-clip:text;-webkit-text-fill-color:transparent">97.2%</div><div class="kpi-label">Prediction Accuracy</div></div>
      <div class="card kpi"><div class="kpi-value" style="background:linear-gradient(135deg,var(--amber),#f97316);-webkit-background-clip:text;-webkit-text-fill-color:transparent">23</div><div class="kpi-label">Failures Prevented</div></div>
      <div class="card kpi"><div class="kpi-value" style="background:linear-gradient(135deg,var(--cyan),var(--teal));-webkit-background-clip:text;-webkit-text-fill-color:transparent">4.2M</div><div class="kpi-label">Sensor Readings/Day</div></div>
    </div>
    
    <div class="grid-2" style="margin-bottom:20px">
      <div class="card">
        <div class="chart">
          <div class="chart-title">Fleet Health Score (30 days)</div>
          <div class="sparkline" style="height:100px">{spark(76, 30, "var(--teal)")}</div>
          <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:0.72rem;color:var(--text3)"><span>30d ago</span><span>Today</span></div>
        </div>
      </div>
      <div class="card">
        <div class="chart">
          <div class="chart-title">Energy Consumption kWh (30 days)</div>
          <div class="sparkline" style="height:100px">{spark(450, 30, "var(--accent)")}</div>
          <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:0.72rem;color:var(--text3)"><span>30d ago</span><span>Today</span></div>
        </div>
      </div>
    </div>
    
    <div class="grid-2" style="margin-bottom:20px">
      <div class="card">
        <div class="chart">
          <div class="chart-title">Anomalies Detected (7 days)</div>
          <div class="sparkline" style="height:70px">{spark(8, 7, "var(--red)")}</div>
          <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:0.72rem;color:var(--text3)"><span>7d ago</span><span>Today</span></div>
        </div>
      </div>
      <div class="card">
        <div class="chart">
          <div class="chart-title">Simulations Run (7 days)</div>
          <div class="sparkline" style="height:70px">{spark(12, 7, "var(--cyan)")}</div>
          <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:0.72rem;color:var(--text3)"><span>7d ago</span><span>Today</span></div>
        </div>
      </div>
    </div>
    
    <div class="card">
      <h3 style="font-size:1rem;font-weight:700;margin-bottom:16px">Twin Performance Ranking</h3>
      <table class="table">
        <tr><th>Twin</th><th>Health</th><th>Uptime</th><th>Alerts (7d)</th><th>Predicted Risk</th><th>Energy Efficiency</th></tr>
        <tr><td>🤖 Robotic Arm #1</td><td><span style="color:var(--green);font-weight:700">94%</span></td><td>99.8%</td><td>0</td><td><span class="badge badge-info">LOW</span></td><td>⭐⭐⭐⭐⭐</td></tr>
        <tr><td>⚡ Diesel Generator</td><td><span style="color:var(--green);font-weight:700">92%</span></td><td>99.9%</td><td>0</td><td><span class="badge badge-info">LOW</span></td><td>⭐⭐⭐⭐</td></tr>
        <tr><td>⚙️ CNC Lathe #1</td><td><span style="color:var(--green);font-weight:700">87%</span></td><td>99.2%</td><td>1</td><td><span class="badge badge-info">LOW</span></td><td>⭐⭐⭐⭐</td></tr>
        <tr><td>🏭 Conveyor Belt #3</td><td><span style="color:var(--amber);font-weight:700">78%</span></td><td>97.5%</td><td>1</td><td><span class="badge badge-warning">MEDIUM</span></td><td>⭐⭐⭐</td></tr>
        <tr><td>❄️ HVAC Unit #1</td><td><span style="color:var(--amber);font-weight:700">65%</span></td><td>95.1%</td><td>2</td><td><span class="badge badge-warning">MEDIUM</span></td><td>⭐⭐</td></tr>
        <tr><td>💧 Coolant Pump #1</td><td><span style="color:var(--red);font-weight:700">43%</span></td><td>88.3%</td><td>4</td><td><span class="badge badge-critical">HIGH</span></td><td>⭐</td></tr>
      </table>
    </div>
    """
    return page_wrap("Analytics", "Fleet-wide performance metrics, trends, and AI-driven insights", content, "analytics")

# Keep API endpoints too
@app.get("/api/twins")
def api_twins():
    return [{"id": k, **{k2: v2 for k2, v2 in v.items() if k2 not in ("sensors","icon","img")}} for k, v in TWINS.items()]

@app.get("/api/predict/{twin_id}")
def api_predict(twin_id: str):
    t = TWINS.get(twin_id)
    if not t: return {"error": "not found"}
    h = t["health"]
    risk = "HIGH" if h<50 else "MEDIUM" if h<75 else "LOW"
    return {"twin_id": twin_id, "risk": risk, "days": random.randint(2,365), "confidence": round(random.uniform(0.7,0.95),2)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
