from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent.parent / "outputs" / "xeip-principal-engineer-review.html"
review = (ROOT / "docs" / "principal-engineer-review.md").read_text()

rows = []
in_table = False
for line in review.splitlines():
    if line.startswith("| Area "):
        in_table = True
        continue
    if in_table and line.startswith("| ---"):
        continue
    if in_table and line.startswith("| "):
        cells = [html.escape(cell.strip()) for cell in line.strip("|").split("|")]
        rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
    elif in_table:
        break

html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>XEIP Principal Engineer Review</title>
<style>
body{{margin:0;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f5f7f8;color:#14201d}}main{{max-width:1180px;margin:0 auto;padding:28px}}h1{{font-size:34px;margin:0 0 8px;letter-spacing:0}}p{{color:#53665f;line-height:1.5}}table{{width:100%;border-collapse:collapse;background:white;border:1px solid #dfe8e4;border-radius:8px;overflow:hidden}}td,th{{padding:12px;border-bottom:1px solid #e6ede9;vertical-align:top;font-size:13px;line-height:1.45}}td:first-child{{font-weight:800;color:#176b57;white-space:nowrap}}.band{{background:white;border:1px solid #dfe8e4;border-radius:8px;padding:18px;margin:18px 0}}.pill{{display:inline-block;background:#e8f3ef;color:#176b57;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:800;margin-right:6px}}@media(max-width:760px){{main{{padding:18px}}table,tr,td{{display:block}}td:first-child{{white-space:normal;background:#f7faf9}}}}
</style>
</head>
<body><main>
<span class="pill">Principal Engineer Review</span><span class="pill">Enterprise Remediation Complete</span>
<h1>XEIP Gap Analysis and Redesign</h1>
<p>The original scaffold was demo-grade. The remediation added deny-by-default auth, tenant-scoped governance, typed schemas, RAG abstention, model cards, approval gates, audit events, data-quality profiling, and hardened deployment manifests.</p>
<div class="band"><strong>Fortune 500 target state:</strong><p>Run XEIP as a governed AI control plane with enterprise IdP, ABAC/RBAC, append-only audit storage, durable orchestration, secure metadata-filtered RAG, model registry, feature store, SLOs, kill switches, and human approval thresholds for material business actions.</p></div>
<table><tbody>{''.join(rows)}</tbody></table>
</main></body></html>"""

OUT.write_text(html_doc)
print(OUT)

