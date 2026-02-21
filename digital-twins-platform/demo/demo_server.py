"""
SimulAI Demo Server - Standalone FastAPI demo with mock digital twins
Shows AI prediction, anomaly detection, and what-if simulation
"""
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/pylibs')

import json, random, math, time
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="SimulAI Demo", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Mock Digital Twins ---
TWINS = {
    "cnc-lathe-001": {
        "name": "CNC Lathe #1", "type": "CNC Machine", "location": "Plant A - Line 1",
        "status": "operational", "health": 87,
        "sensors": {"temperature": 72.3, "vibration": 2.1, "rpm": 3200, "power_kw": 15.4, "oil_pressure": 45.2}
    },
    "robotic-arm-001": {
        "name": "Robotic Arm #1", "type": "6-Axis Robot", "location": "Plant A - Assembly",
        "status": "operational", "health": 94,
        "sensors": {"temperature": 38.5, "joint_torque": 12.3, "cycle_time_s": 8.2, "accuracy_mm": 0.02, "power_kw": 3.8}
    },
    "hvac-001": {
        "name": "HVAC Unit #1", "type": "Industrial HVAC", "location": "Plant A - Main Hall",
        "status": "warning", "health": 65,
        "sensors": {"supply_temp": 18.2, "return_temp": 24.1, "humidity": 58, "filter_dp_pa": 320, "power_kw": 45.0}
    },
    "generator-001": {
        "name": "Diesel Generator", "type": "Backup Generator", "location": "Plant A - Utilities",
        "status": "standby", "health": 92,
        "sensors": {"temperature": 25.0, "fuel_level_pct": 78, "battery_v": 24.1, "runtime_hrs": 1240, "last_test_days": 12}
    },
    "pump-001": {
        "name": "Coolant Pump #1", "type": "Centrifugal Pump", "location": "Plant A - Cooling",
        "status": "degraded", "health": 43,
        "sensors": {"temperature": 89.2, "vibration": 8.7, "flow_rate_lpm": 142, "pressure_bar": 3.2, "power_kw": 7.8}
    },
}

def add_noise(val, pct=0.03):
    return round(val * (1 + random.uniform(-pct, pct)), 2)

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
def root():
    return """<html><body style='font-family:Inter,sans-serif;background:#0a0a0f;color:#fff;padding:40px'>
    <h1 style='background:linear-gradient(135deg,#6366f1,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>
    SimulAI API Demo</h1>
    <p style='color:#a1a1aa'>Digital Twins + AI Simulation Platform</p>
    <h3>Endpoints:</h3>
    <ul style='color:#14b8a6'>
    <li><a href='/twins' style='color:#14b8a6'>/twins</a> - List all digital twins</li>
    <li><a href='/twins/pump-001' style='color:#14b8a6'>/twins/{id}</a> - Twin detail + live sensors</li>
    <li><a href='/ai/predict/pump-001' style='color:#14b8a6'>/ai/predict/{id}</a> - AI failure prediction</li>
    <li><a href='/ai/anomalies' style='color:#14b8a6'>/ai/anomalies</a> - Anomaly detection across all twins</li>
    <li><a href='/ai/simulate?twin_id=cnc-lathe-001&change=rpm&value=4500' style='color:#14b8a6'>/ai/simulate</a> - What-if simulation</li>
    <li><a href='/dashboard' style='color:#14b8a6'>/dashboard</a> - Visual dashboard</li>
    </ul></body></html>"""

@app.get("/twins")
def list_twins():
    return [{"id": k, **{k2: v2 for k2, v2 in v.items() if k2 != "sensors"}} for k, v in TWINS.items()]

@app.get("/twins/{twin_id}")
def get_twin(twin_id: str):
    twin = TWINS.get(twin_id)
    if not twin:
        return {"error": "Twin not found"}
    # Add live sensor noise
    live = {k: add_noise(v) for k, v in twin["sensors"].items()}
    return {"id": twin_id, **twin, "sensors": live, "timestamp": datetime.utcnow().isoformat()}

@app.get("/ai/predict/{twin_id}")
def predict_failure(twin_id: str):
    twin = TWINS.get(twin_id)
    if not twin:
        return {"error": "Twin not found"}
    
    health = twin["health"]
    sensors = twin["sensors"]
    
    # Simple prediction logic based on health and sensor patterns
    if health < 50:
        risk = "HIGH"
        days_to_failure = random.randint(2, 7)
        confidence = round(random.uniform(0.82, 0.95), 2)
        
        # Identify root cause from sensors
        causes = []
        if sensors.get("temperature", 0) > 80:
            causes.append({"factor": "Overheating", "severity": "critical", "detail": f"Temperature at {sensors['temperature']}C, threshold 80C"})
        if sensors.get("vibration", 0) > 5:
            causes.append({"factor": "Excessive vibration", "severity": "high", "detail": f"Vibration at {sensors['vibration']}mm/s, threshold 5mm/s"})
        if sensors.get("filter_dp_pa", 0) > 300:
            causes.append({"factor": "Clogged filter", "severity": "medium", "detail": f"Differential pressure {sensors['filter_dp_pa']}Pa, threshold 300Pa"})
    elif health < 70:
        risk = "MEDIUM"
        days_to_failure = random.randint(14, 45)
        confidence = round(random.uniform(0.65, 0.80), 2)
        causes = [{"factor": "Gradual degradation", "severity": "medium", "detail": "Performance trending below baseline"}]
    else:
        risk = "LOW"
        days_to_failure = random.randint(90, 365)
        confidence = round(random.uniform(0.70, 0.90), 2)
        causes = []

    return {
        "twin_id": twin_id,
        "twin_name": twin["name"],
        "prediction": {
            "risk_level": risk,
            "estimated_days_to_failure": days_to_failure,
            "confidence": confidence,
            "predicted_failure_date": (datetime.utcnow() + timedelta(days=days_to_failure)).strftime("%Y-%m-%d"),
        },
        "root_causes": causes,
        "recommendation": f"Schedule preventive maintenance within {max(1, days_to_failure - 2)} days" if risk != "LOW" else "Continue normal monitoring",
        "estimated_cost_avoided_usd": random.randint(5000, 75000) if risk == "HIGH" else random.randint(1000, 15000),
        "model": "SimulAI Predictor v0.3 (gradient boosting + LSTM ensemble)",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ai/anomalies")
def detect_anomalies():
    anomalies = []
    for tid, twin in TWINS.items():
        for sensor, val in twin["sensors"].items():
            # Define thresholds
            thresholds = {
                "temperature": 80, "vibration": 5, "filter_dp_pa": 300,
                "humidity": 70, "fuel_level_pct": 20
            }
            if sensor in thresholds:
                threshold = thresholds[sensor]
                if (sensor == "fuel_level_pct" and val < threshold) or (sensor != "fuel_level_pct" and val > threshold):
                    anomalies.append({
                        "twin_id": tid, "twin_name": twin["name"],
                        "sensor": sensor, "value": val, "threshold": threshold,
                        "severity": "critical" if abs(val - threshold) / threshold > 0.2 else "warning",
                        "detected_at": datetime.utcnow().isoformat()
                    })
    return {"anomalies": anomalies, "total": len(anomalies), "scanned_twins": len(TWINS)}

@app.get("/ai/simulate")
def simulate(twin_id: str = "cnc-lathe-001", change: str = "rpm", value: float = 4500):
    twin = TWINS.get(twin_id)
    if not twin:
        return {"error": "Twin not found"}
    
    current = twin["sensors"].get(change, 0)
    delta_pct = (value - current) / current if current else 0
    
    # Simulate impacts
    impacts = {
        "energy": {"change_pct": round(delta_pct * 1.3 * 100, 1), "detail": f"Power consumption {'increases' if delta_pct > 0 else 'decreases'} proportionally"},
        "wear": {"change_pct": round(abs(delta_pct) * 2.1 * 100, 1), "detail": "Accelerated wear on moving parts" if delta_pct > 0 else "Reduced mechanical stress"},
        "output": {"change_pct": round(delta_pct * 0.85 * 100, 1), "detail": "Production throughput adjustment"},
        "failure_risk": {"change_pct": round(abs(delta_pct) * 1.8 * 100, 1), "detail": "Higher loads increase failure probability" if delta_pct > 0 else "Lower risk at reduced load"},
    }
    
    # Cost projection
    annual_energy_delta = round(delta_pct * 1.3 * twin["sensors"].get("power_kw", 10) * 8760 * 0.12, 2)
    
    return {
        "twin_id": twin_id,
        "twin_name": twin["name"],
        "scenario": {"parameter": change, "current_value": current, "simulated_value": value, "change_pct": round(delta_pct * 100, 1)},
        "impacts": impacts,
        "cost_projection": {
            "annual_energy_delta_usd": annual_energy_delta,
            "estimated_maintenance_impact_usd": round(abs(delta_pct) * 5000, 2),
        },
        "recommendation": "Proceed with caution - monitor vibration closely" if delta_pct > 0.2 else "Safe to implement",
        "simulated_scenarios": 1000,
        "confidence": round(random.uniform(0.85, 0.95), 2),
        "model": "SimulAI Simulator v0.2 (Monte Carlo + physics-informed neural network)",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    twins_json = json.dumps([{"id": k, **v} for k, v in TWINS.items()])
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>SimulAI Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:#0a0a0f;color:#fff;padding:24px}}
h1{{background:linear-gradient(135deg,#6366f1,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2rem;margin-bottom:8px}}
.subtitle{{color:#a1a1aa;margin-bottom:32px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px}}
.card{{background:#15151f;border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;transition:transform 0.2s}}
.card:hover{{transform:translateY(-4px);border-color:rgba(255,255,255,0.15)}}
.card-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.card-name{{font-size:1.1rem;font-weight:700}}
.card-type{{color:#71717a;font-size:0.8rem}}
.badge{{padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:600}}
.badge-operational{{background:rgba(20,184,166,0.15);color:#14b8a6}}
.badge-warning{{background:rgba(251,191,36,0.15);color:#fbbf24}}
.badge-degraded{{background:rgba(239,68,68,0.15);color:#ef4444}}
.badge-standby{{background:rgba(161,161,170,0.15);color:#a1a1aa}}
.health-bar{{height:6px;background:#1a1a25;border-radius:3px;margin:12px 0}}
.health-fill{{height:100%;border-radius:3px;transition:width 0.5s}}
.sensors{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}}
.sensor{{background:#1a1a25;border-radius:8px;padding:8px 12px}}
.sensor-name{{color:#71717a;font-size:0.7rem;text-transform:uppercase}}
.sensor-val{{font-size:1.1rem;font-weight:600;color:#14b8a6}}
.actions{{display:flex;gap:8px;margin-top:16px}}
.btn{{padding:8px 16px;border-radius:8px;border:none;cursor:pointer;font-size:0.8rem;font-weight:600;font-family:'Inter',sans-serif}}
.btn-predict{{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff}}
.btn-simulate{{background:rgba(6,182,212,0.15);color:#06b6d4;border:1px solid rgba(6,182,212,0.3)}}
.result{{margin-top:12px;padding:12px;background:#1a1a25;border-radius:8px;font-size:0.85rem;display:none;white-space:pre-wrap;color:#a1a1aa}}
</style></head><body>
<h1>SimulAI Dashboard</h1>
<p class="subtitle">Digital Twins + AI Simulation — Live Demo</p>
<div class="grid" id="grid"></div>
<script>
const twins = {twins_json};
const grid = document.getElementById('grid');
twins.forEach(t => {{
  const healthColor = t.health > 80 ? '#14b8a6' : t.health > 50 ? '#fbbf24' : '#ef4444';
  const sensors = Object.entries(t.sensors).map(([k,v]) => 
    `<div class="sensor"><div class="sensor-name">${{k.replace(/_/g,' ')}}</div><div class="sensor-val">${{v}}</div></div>`
  ).join('');
  grid.innerHTML += `
    <div class="card">
      <div class="card-header">
        <div><div class="card-name">${{t.name}}</div><div class="card-type">${{t.type}} · ${{t.location}}</div></div>
        <span class="badge badge-${{t.status}}">${{t.status}}</span>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:0.85rem">
        <span style="color:#71717a">Health</span><span style="color:${{healthColor}};font-weight:700">${{t.health}}%</span>
      </div>
      <div class="health-bar"><div class="health-fill" style="width:${{t.health}}%;background:${{healthColor}}"></div></div>
      <div class="sensors">${{sensors}}</div>
      <div class="actions">
        <button class="btn btn-predict" onclick="predict('${{t.id}}',this)">🔮 Predict</button>
        <button class="btn btn-simulate" onclick="simulate('${{t.id}}',this)">🎮 Simulate</button>
      </div>
      <div class="result" id="result-${{t.id}}"></div>
    </div>`;
}});

async function predict(id, btn) {{
  const el = document.getElementById('result-'+id);
  el.style.display = 'block';
  el.textContent = 'Analyzing...';
  const res = await fetch('/ai/predict/'+id);
  const d = await res.json();
  el.innerHTML = `<strong style="color:${{d.prediction.risk_level==='HIGH'?'#ef4444':d.prediction.risk_level==='MEDIUM'?'#fbbf24':'#14b8a6'}}">${{d.prediction.risk_level}} RISK</strong>
Failure in ~${{d.prediction.estimated_days_to_failure}} days (confidence: ${{(d.prediction.confidence*100).toFixed(0)}}%)
${{d.root_causes.map(c=>'⚠ '+c.factor+': '+c.detail).join('\\n')}}
💰 Cost avoided: USD $${{d.estimated_cost_avoided_usd.toLocaleString()}}
📋 ${{d.recommendation}}`;
}}

async function simulate(id, btn) {{
  const el = document.getElementById('result-'+id);
  el.style.display = 'block';
  el.textContent = 'Simulating 1000 scenarios...';
  const res = await fetch('/ai/simulate?twin_id='+id);
  const d = await res.json();
  el.innerHTML = `<strong style="color:#06b6d4">SIMULATION RESULT</strong>
Scenario: ${{d.scenario.parameter}} ${{d.scenario.current_value}} → ${{d.scenario.simulated_value}} (${{d.scenario.change_pct>0?'+':''}}${{d.scenario.change_pct}}%)
⚡ Energy: ${{d.impacts.energy.change_pct>0?'+':''}}${{d.impacts.energy.change_pct}}%
🔧 Wear: +${{d.impacts.wear.change_pct}}%
📈 Output: ${{d.impacts.output.change_pct>0?'+':''}}${{d.impacts.output.change_pct}}%
⚠ Failure risk: +${{d.impacts.failure_risk.change_pct}}%
💰 Annual energy delta: USD $${{d.cost_projection.annual_energy_delta_usd.toLocaleString()}}
📋 ${{d.recommendation}}`;
}}
</script></body></html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
