from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent.parent / "outputs" / "xeip-executive-dashboard.html"
manifest = json.loads((ROOT / "data" / "manifest.json").read_text())
metrics = manifest["executive_metrics"]

cards = "\n".join(
    f"<article><span>{k.replace('_', ' ').title()}</span><strong>{v:,}</strong></article>"
    for k, v in metrics.items()
)
datasets = "\n".join(
    f"<tr><td>{name.replace('_', ' ').title()}</td><td>{meta['records']:,}</td><td>{len(meta['fields'])}</td></tr>"
    for name, meta in manifest["datasets"].items()
)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>XEIP Executive Dashboard</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f4f7f6;color:#14201d}}.shell{{display:grid;grid-template-columns:230px 1fr;min-height:100vh}}aside{{background:#101816;color:#edf5f2;padding:24px 18px}}.logo{{font-size:30px;font-weight:850;margin-bottom:32px}}nav{{display:grid;gap:8px}}nav span{{padding:10px 12px;border-radius:6px;color:#c4d3ce}}nav span:first-child{{background:#253530;color:white}}main{{padding:28px}}header{{display:flex;justify-content:space-between;gap:18px;align-items:center;margin-bottom:22px}}.eyebrow{{margin:0 0 6px;color:#507061;font-weight:800;font-size:13px}}h1{{font-size:34px;line-height:1.08;margin:0;letter-spacing:0}}button{{border:0;background:#176b57;color:white;padding:11px 14px;border-radius:6px;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(5,minmax(130px,1fr));gap:12px;margin-bottom:18px}}article,.panel{{background:white;border:1px solid #dfe8e4;border-radius:8px;box-shadow:0 1px 2px rgba(20,32,29,.04)}}article{{padding:14px;min-height:98px}}article span{{display:block;color:#63756f;font-size:12px}}article strong{{display:block;font-size:24px;margin-top:14px}}.layout{{display:grid;grid-template-columns:1.1fr .9fr;gap:18px}}.panel{{padding:18px}}h2{{font-size:18px;margin:0 0 14px}}.agents{{display:grid;grid-template-columns:repeat(2,minmax(210px,1fr));gap:10px}}.agent{{background:#f7faf9;border:1px solid #e5ece8;border-radius:8px;padding:12px;min-height:92px}}.agent b{{display:block}}p,td,li{{color:#52645e;line-height:1.45}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #e5ece8;text-align:left;padding:9px 6px;font-size:13px}}.rec{{font-size:24px;line-height:1.16;color:#14201d;margin:0 0 10px;font-weight:850}}@media(max-width:900px){{.shell{{grid-template-columns:1fr}}aside{{display:none}}.grid,.layout,.agents{{grid-template-columns:1fr 1fr}}}}@media(max-width:560px){{main{{padding:18px}}header{{display:grid}}.grid,.layout,.agents{{grid-template-columns:1fr}}h1{{font-size:27px}}}}
</style>
</head>
<body><div class="shell"><aside><div class="logo">XEIP</div><nav><span>Command</span><span>Operations</span><span>Agents</span><span>Compliance</span><span>Evidence</span></nav></aside><main>
<header><div><p class="eyebrow">Xerox Enterprise Intelligence Platform</p><h1>Autonomous enterprise operations cockpit</h1></div><button>Executive Review</button></header>
<section class="grid">{cards}</section>
<section class="layout"><div class="panel"><h2>Autonomous Agent Mesh</h2><div class="agents">
<div class="agent"><b>Support Agent</b><p>Diagnoses printer failures, recommends fixes, and escalates unresolved cases.</p></div>
<div class="agent"><b>Maintenance Agent</b><p>Predicts failures, schedules repairs, prioritizes work orders.</p></div>
<div class="agent"><b>Inventory Agent</b><p>Monitors toner and spare parts, forecasts demand, triggers procurement.</p></div>
<div class="agent"><b>Contract Intelligence Agent</b><p>Extracts obligations, monitors SLA compliance, detects violations.</p></div>
<div class="agent"><b>Customer Success Agent</b><p>Predicts churn, identifies upsell opportunities, analyzes sentiment.</p></div>
<div class="agent"><b>Compliance Agent</b><p>Audits policy activity, masks PII, validates RAG security.</p></div>
</div></div><div class="panel"><h2>Explainable AI Recommendation</h2><p class="rec">Prioritize 184 high-risk devices for preventive fuser replacement.</p><p>Confidence 91%. Evidence combines high temperature telemetry, repeated 077-900 faults, contract uptime exposure, and spare-part lead time.</p><ul><li>Risk: 13 P1 customers inside SLA breach window</li><li>Alternative: remote calibration for low-value devices</li><li>Expected value: $640K avoided downtime</li></ul></div></section>
<section class="panel" style="margin-top:18px"><h2>Generated Enterprise Datasets</h2><table><thead><tr><th>Dataset</th><th>Records</th><th>Fields</th></tr></thead><tbody>{datasets}</tbody></table></section>
</main></div></body></html>"""

OUT.write_text(html)
print(OUT)
