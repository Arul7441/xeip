import { Activity, Bot, FileSearch, ShieldCheck, TrendingUp, Wrench } from "lucide-react";

const metrics = [
  ["MTTR", "14.8h", "18% better"],
  ["Device Uptime", "98.73%", "+1.2 pts"],
  ["Cost Savings", "$4.82M", "annualized"],
  ["SLA Compliance", "96.8%", "+4.4 pts"],
  ["Inventory Health", "91.2%", "stable"],
  ["Forecast Accuracy", "89.7%", "+6.1 pts"],
];

const agents = [
  ["Support Agent", "Diagnoses technical issues and escalates unresolved cases.", Bot],
  ["Maintenance Agent", "Predicts failures and schedules repairs.", Wrench],
  ["Inventory Agent", "Forecasts toner and parts demand.", Activity],
  ["Contract Agent", "Extracts obligations and monitors SLA risk.", FileSearch],
  ["Compliance Agent", "Audits policy events and masks PII.", ShieldCheck],
  ["Executive Advisor", "Ranks enterprise decisions by business value.", TrendingUp],
];

export default function Home() {
  return (
    <main>
      <aside>
        <div className="brand">XEIP</div>
        <nav>
          <span>Command</span><span>Operations</span><span>Agents</span><span>Risk</span><span>Evidence</span>
        </nav>
      </aside>
      <section className="workspace">
        <header>
          <div>
            <p className="eyebrow">Xerox Enterprise Intelligence Platform</p>
            <h1>Autonomous enterprise operations cockpit</h1>
          </div>
          <button>Run Executive Review</button>
        </header>
        <div className="metric-grid">
          {metrics.map(([label, value, delta]) => <article key={label}><span>{label}</span><strong>{value}</strong><em>{delta}</em></article>)}
        </div>
        <section className="split">
          <div className="panel">
            <h2>Agent Mesh</h2>
            <div className="agent-list">
              {agents.map(([name, desc, Icon]: any) => <div className="agent" key={name}><Icon size={19}/><div><b>{name}</b><p>{desc}</p></div></div>)}
            </div>
          </div>
          <div className="panel">
            <h2>Explainable Recommendation</h2>
            <div className="recommendation">
              <strong>Prioritize 184 devices for preventive fuser replacement.</strong>
              <p>Confidence 91%. Evidence combines high temperature telemetry, repeated 077-900 faults, contract uptime exposure, and spare-part lead time.</p>
              <ul><li>Risk: 13 P1 customers within SLA breach window</li><li>Alternative: remote calibration for low-value devices</li><li>Expected value: $640K avoided downtime</li></ul>
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
