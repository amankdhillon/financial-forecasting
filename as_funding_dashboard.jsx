import { useState, useMemo, useEffect, useRef } from "react";
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  ScatterChart, Scatter, ComposedChart, ReferenceLine
} from "recharts";
import "./dashboard.css";

// ── Color tokens (match CSS custom properties for chart usage) ─────
const C = {
  navy: "#1B2A4A", blue: "#2C4A7C", red: "#8B2020", burgundy: "#5C1A2A",
  teal: "#2A7A6A", amber: "#9A7030", violet: "#6B4C8A",
  bg: "#F5F0E8", surface: "#FDFBF7", card: "#FFFFFF",
  border: "#DDD6CA", borderLight: "#E8E2D8",
  text: "#2A2520", textSec: "#6B6560", textMut: "#9A9490",
  spring: "#2A7A6A", winter: "#2C4A7C", fall: "#9A7030",
};
const PAL = [C.navy, C.teal, C.amber, C.red, C.violet, C.blue, C.burgundy, "#5A8A5A", "#8A6A4A", "#4A6A8A"];

// ── Utilities ─────────────────────────────────────────────────────
const fmt = n => n >= 1e6 ? `$${(n / 1e6).toFixed(1)}M` : n >= 1000 ? `$${(n / 1000).toFixed(0)}K` : `$${n}`;
const fmtN = n => n.toLocaleString("en-US");
const qColor = q => q.includes("Spring") ? C.spring : q.includes("Winter") ? C.winter : C.fall;

// ── Data Fetching Hook ────────────────────────────────────────────
function useDashboardData() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}dashboard_data.json`)
      .then(r => { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then(setData)
      .catch(setError);
  }, []);

  return { data, error };
}

// ── Shared Components ─────────────────────────────────────────────

function AnimNum({ value, prefix = "$" }) {
  const [d, setD] = useState(0);
  useEffect(() => {
    const start = performance.now();
    const step = ts => {
      const p = Math.min((ts - start) / 1000, 1);
      setD(Math.round((1 - Math.pow(1 - p, 3)) * value));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [value]);
  return <span>{prefix}{d.toLocaleString()}</span>;
}

function Stat({ label, value, prefix = "$", sub, color = C.navy }) {
  return (
    <div className="stat" style={{ borderTop: `2px solid ${color}33` }}>
      <div className="stat-label">{label}</div>
      <div className="stat-value"><AnimNum value={value} prefix={prefix} /></div>
      {sub && <div className="stat-sub" style={{ color }}>{sub}</div>}
    </div>
  );
}

function Section({ children, title, sub }) {
  return (
    <div className="section">
      {title && (
        <div className="section-header">
          <h2 className="section-title">{title}</h2>
          {sub && <p className="section-sub">{sub}</p>}
        </div>
      )}
      {children}
    </div>
  );
}

function Card({ children, flush = false, style = {} }) {
  return (
    <div className={`card${flush ? " card--flush" : ""}`} style={style}>
      {children}
    </div>
  );
}

function TT({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="tooltip">
      <div className="tooltip-label">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="tooltip-row">
          <div className="tooltip-dot" style={{ background: p.color || C.teal }} />
          <span className="tooltip-value">{typeof p.value === "number" ? fmt(p.value) : p.value}</span>
          <span className="tooltip-name">{p.name}</span>
        </div>
      ))}
    </div>
  );
}

// ── TAB: OVERVIEW ─────────────────────────────────────────────────
function OverviewTab({ QO, QL, QF, QS, GRAND, seasonality, academicYears }) {
  const trend = useMemo(() =>
    QO.map(q => { const s = QS.find(x => x.q === q); return { name: QL[q], total: s.t, events: s.n, avg: s.a, q }; }),
    [QO, QL, QS]
  );

  const maxSeasonAvg = Math.max(...seasonality.map(s => s.avg), 1);

  return (
    <div>
      <div className="stat-grid">
        <Stat label="Total Funded" value={GRAND.total} sub={`${QO.length} quarters`} />
        <Stat label="Events Funded" value={GRAND.events} prefix="" sub="Across all quarters" color={C.teal} />
        <Stat label="Unique Orgs" value={GRAND.orgs} prefix="" sub="Student organizations" color={C.blue} />
        <Stat label="Avg Per Event" value={Math.round(GRAND.total / GRAND.events)} sub="Grand average" color={C.violet} />
      </div>

      <Section title="Spending Trajectory" sub="Total funding awarded per quarter over time">
        <Card>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={trend}>
              <defs>
                <linearGradient id="gT" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={C.navy} stopOpacity={0.15} />
                  <stop offset="100%" stopColor={C.navy} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} vertical={false} />
              <XAxis dataKey="name" tick={{ fill: C.textSec, fontSize: 11, fontFamily: "'JetBrains Mono'" }} axisLine={{ stroke: C.border }} tickLine={false} />
              <YAxis tick={{ fill: C.textMut, fontSize: 10 }} tickFormatter={fmt} axisLine={false} tickLine={false} />
              <Tooltip content={<TT />} />
              <Area type="monotone" dataKey="total" name="Total" stroke={C.navy} fill="url(#gT)" strokeWidth={2} dot={{ r: 4, fill: C.navy, stroke: C.bg, strokeWidth: 2 }} activeDot={{ r: 6 }} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      </Section>

      <div className="grid-2">
        <Section title="Quarter-Type Seasonality" sub="Average spending by quarter type">
          <Card>
            {seasonality.map((qt, i) => {
              const color = qt.type === "Spring" ? C.spring : qt.type === "Winter" ? C.winter : C.fall;
              return (
                <div key={i} className="season-item">
                  <div className="season-header">
                    <span className="season-label" style={{ color }}>{qt.type}</span>
                    <span className="season-value">{fmt(qt.avg)}<span className="suffix">avg</span></span>
                  </div>
                  <div className="season-track">
                    <div className="season-fill" style={{ width: `${(qt.avg / maxSeasonAvg) * 100}%`, background: color, animationDelay: `${0.2 + i * 0.1}s` }} />
                  </div>
                  <div className="season-meta">
                    <span>~{qt.avgE} events</span>
                    <span>~{fmt(qt.avgPer)}/event</span>
                    <span>{qt.samples} sample{qt.samples > 1 ? "s" : ""}</span>
                  </div>
                </div>
              );
            })}
            {seasonality.length >= 2 && (
              <div className="callout">
                <div className="callout-heading" style={{ color: C.teal }}>Key Finding</div>
                <div className="callout-body">
                  {seasonality[0].type} quarters average <strong style={{ color: qColor(seasonality[0].type) }}>{fmt(seasonality[0].avg)}</strong>
                  {seasonality.length >= 3 && <> &mdash; {Math.round(((seasonality[0].avg / seasonality[2].avg) - 1) * 100)}% more than {seasonality[2].type}.</>}
                </div>
              </div>
            )}
          </Card>
        </Section>

        <Section title="Academic Year Comparison" sub="Year-over-year totals (partial years noted)">
          <Card>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={academicYears} layout="vertical" barCategoryGap="20%">
                <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} horizontal={false} />
                <XAxis type="number" tick={{ fill: C.textMut, fontSize: 10 }} tickFormatter={fmt} axisLine={false} tickLine={false} />
                <YAxis dataKey="year" type="category" tick={{ fill: C.text, fontSize: 12, fontFamily: "'JetBrains Mono'" }} width={60} axisLine={false} tickLine={false} />
                <Tooltip content={<TT />} />
                <Bar dataKey="total" name="Total" radius={[0, 5, 5, 0]}>
                  {academicYears.map((_, i) => <Cell key={i} fill={PAL[i % PAL.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="ay-badges">
              {academicYears.map((a, i) => (
                <span key={i} className="ay-badge">{a.year} · {a.note} · {fmtN(a.events)} events</span>
              ))}
            </div>
          </Card>
        </Section>
      </div>

      <Section title="Events vs. Spending Efficiency" sub="More events doesn't always mean more total spending">
        <Card>
          <ResponsiveContainer width="100%" height={240}>
            <ComposedChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} vertical={false} />
              <XAxis dataKey="name" tick={{ fill: C.textSec, fontSize: 11, fontFamily: "'JetBrains Mono'" }} axisLine={{ stroke: C.border }} tickLine={false} />
              <YAxis yAxisId="l" tick={{ fill: C.textMut, fontSize: 10 }} tickFormatter={fmt} axisLine={false} tickLine={false} />
              <YAxis yAxisId="r" orientation="right" tick={{ fill: C.textMut, fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<TT />} />
              <Bar yAxisId="r" dataKey="events" name="Events" fill={`${C.blue}33`} radius={[4, 4, 0, 0]} />
              <Line yAxisId="l" type="monotone" dataKey="avg" name="Avg/Event" stroke={C.red} strokeWidth={2} dot={{ r: 3, fill: C.red, stroke: C.bg, strokeWidth: 2 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </Card>
      </Section>
    </div>
  );
}

// ── TAB: QUARTER DEEP DIVE ────────────────────────────────────────
function QuarterTab({ QO, QL, QF, QS }) {
  const [sel, setSel] = useState(null);
  const activeQ = sel || QO[QO.length - 1];
  const d = QS.find(x => x.q === activeQ);
  const c = qColor(activeQ);

  return (
    <div>
      <div className="chip-group">
        {QO.map(q => (
          <button key={q} className={`chip${activeQ === q ? " active" : ""}`} onClick={() => setSel(q)}>
            {QF[q]}
          </button>
        ))}
      </div>

      <div className="stat-grid">
        <Stat label="Total Spent" value={d.t} color={c} />
        <Stat label="Events" value={d.n} prefix="" color={c} />
        <Stat label="Avg/Event" value={d.a} color={c} />
        <Stat label="Median" value={d.md} color={c} />
      </div>

      <div className="grid-2">
        <Section title="Monthly Breakdown">
          <Card>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={d.mo} barCategoryGap="15%">
                <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} vertical={false} />
                <XAxis dataKey="m" tick={{ fill: C.textSec, fontSize: 11, fontFamily: "'JetBrains Mono'" }} axisLine={{ stroke: C.border }} tickLine={false} />
                <YAxis tick={{ fill: C.textMut, fontSize: 10 }} tickFormatter={fmt} axisLine={false} tickLine={false} />
                <Tooltip content={<TT />} />
                <Bar dataKey="t" name="Spending" radius={[5, 5, 0, 0]}>
                  {d.mo.map((_, i) => <Cell key={i} fill={i === 0 ? `${c}55` : c} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Section>

        <Section title="Award Size Distribution">
          <Card>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={d.dist} barCategoryGap="12%">
                <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} vertical={false} />
                <XAxis dataKey="r" tick={{ fill: C.textSec, fontSize: 9, fontFamily: "'JetBrains Mono'" }} axisLine={{ stroke: C.border }} tickLine={false} interval={0} />
                <YAxis tick={{ fill: C.textMut, fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<TT />} />
                <Bar dataKey="c" name="Count" radius={[4, 4, 0, 0]} fill={C.violet} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Section>
      </div>

      <Section title={`Top 10 Organizations — ${QF[activeQ]}`}>
        <Card flush>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Organization</th>
                  <th className="right">Total Awarded</th>
                  <th className="right">Events</th>
                  <th className="right">Avg/Event</th>
                  <th className="right">Share</th>
                </tr>
              </thead>
              <tbody>
                {d.top.map((org, i) => (
                  <tr key={i}>
                    <td className="mono muted">{i + 1}</td>
                    <td className="ellipsis">{org.o}</td>
                    <td className="mono right" style={{ color: c, fontWeight: 700 }}>{fmt(org.t)}</td>
                    <td className="mono right muted">{org.e}</td>
                    <td className="mono right muted">{fmt(Math.round(org.t / org.e))}</td>
                    <td className="right">
                      <div className="share-bar">
                        <div className="share-track">
                          <div className="share-fill" style={{ width: `${(org.t / d.t) * 100}%`, background: c }} />
                        </div>
                        <span className="share-pct">{((org.t / d.t) * 100).toFixed(1)}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </Section>
    </div>
  );
}

// ── TAB: ORG TRACKER ──────────────────────────────────────────────
function OrgTab({ QO, QL, QF, TOP_ORGS, GRAND }) {
  const [selOrg, setSelOrg] = useState(0);
  const org = TOP_ORGS[selOrg];
  const heatData = useMemo(() =>
    QO.map(q => ({ q, label: QL[q], val: org.qb[q] || 0 })),
    [QO, QL, org]
  );

  return (
    <div>
      <Section title="Top 15 All-Time Organizations" sub="Cumulative funding across all tracked quarters">
        <Card flush>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Organization</th>
                  <th className="right">Total</th>
                  <th className="right">Events</th>
                  <th className="right">Avg</th>
                  <th className="right">Quarters</th>
                  <th>Heatmap</th>
                </tr>
              </thead>
              <tbody>
                {TOP_ORGS.map((o, i) => {
                  const mx = Math.max(...Object.values(o.qb));
                  return (
                    <tr key={i} className={`clickable-row${i === selOrg ? " selected" : ""}`} onClick={() => setSelOrg(i)}>
                      <td className="mono muted">{i + 1}</td>
                      <td className="ellipsis" style={{ color: i === selOrg ? C.navy : undefined, fontWeight: i === selOrg ? 700 : 500 }}>{o.o}</td>
                      <td className="mono right" style={{ color: C.navy, fontWeight: 700 }}>{fmt(o.t)}</td>
                      <td className="mono right muted">{o.e}</td>
                      <td className="mono right muted">{fmt(o.av)}</td>
                      <td className="mono right" style={{ color: C.teal }}>{o.nq}/{QO.length}</td>
                      <td>
                        <div className="heatmap-row">
                          {QO.map((q, j) => {
                            const v = o.qb[q] || 0;
                            const op = v > 0 ? 0.25 + 0.75 * (v / mx) : 0.15;
                            return <div key={j} className="heatmap-cell" title={`${QF[q]}: ${v ? fmt(v) : "\u2014"}`} style={{ background: v > 0 ? qColor(q) : C.border, opacity: op }} />;
                          })}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      </Section>

      <Section title={`Deep Dive: ${org.o}`} sub="Click any row above to inspect an organization">
        <div className="grid-2">
          <Card>
            <div style={{ fontSize: 13, color: C.textMut, marginBottom: 12, fontWeight: 600 }}>Quarterly Spending</div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={heatData} barCategoryGap="18%">
                <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} vertical={false} />
                <XAxis dataKey="label" tick={{ fill: C.textSec, fontSize: 10, fontFamily: "'JetBrains Mono'" }} axisLine={{ stroke: C.border }} tickLine={false} />
                <YAxis tick={{ fill: C.textMut, fontSize: 10 }} tickFormatter={fmt} axisLine={false} tickLine={false} />
                <Tooltip content={<TT />} />
                <Bar dataKey="val" name="Spending" radius={[4, 4, 0, 0]}>
                  {heatData.map((d, i) => <Cell key={i} fill={d.val > 0 ? qColor(d.q) : `${C.border}66`} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
          <Card>
            <div style={{ fontSize: 13, color: C.textMut, marginBottom: 14, fontWeight: 600 }}>Organization Profile</div>
            <div className="profile-grid">
              {[
                { l: "Total Funded", v: fmt(org.t), c: C.navy },
                { l: "Total Events", v: org.e, c: C.teal },
                { l: "Avg Per Event", v: fmt(org.av), c: C.blue },
                { l: "Active Quarters", v: `${org.nq} of ${QO.length}`, c: C.violet },
                { l: "Peak Quarter", v: QL[Object.entries(org.qb).sort((a, b) => b[1] - a[1])[0]?.[0] || ""] || "\u2014", c: C.amber },
                { l: "% of Grand Total", v: `${((org.t / GRAND.total) * 100).toFixed(1)}%`, c: C.red },
              ].map((s, i) => (
                <div key={i} className="profile-item">
                  <div className="profile-label">{s.l}</div>
                  <div className="profile-value" style={{ color: s.c }}>{s.v}</div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </Section>
    </div>
  );
}

// ── TAB: FORECASTING ──────────────────────────────────────────────
function ForecastTab({ QO, QL, QS, forecast }) {
  const { projections, fullYearAvg, fullYearTrend } = forecast;

  const compChart = useMemo(() => {
    const actual = QO.map(q => {
      const s = QS.find(x => x.q === q);
      return { name: QL[q], actual: s.t, type: "actual" };
    });
    const forecasted = projections.map(p => ({
      name: p.q.replace("Winter ", "WI '").replace("Spring ", "SP '"),
      forecast: p.avg,
      trendForecast: p.trend,
      type: "forecast",
    }));
    return [...actual, ...forecasted];
  }, [QO, QL, QS, projections]);

  const eventTrend = useMemo(() =>
    QO.map(q => { const s = QS.find(x => x.q === q); return { name: QL[q], events: s.n, avg: s.a }; }),
    [QO, QL, QS]
  );

  const lastActualLabel = QL[QO[QO.length - 1]];

  return (
    <div>
      <div className="forecast-banner">
        <div>
          <div className="forecast-banner-title">Financial Forecasting</div>
          <div className="forecast-banner-desc">
            Two models: <strong style={{ color: C.teal }}>Simple Average</strong> (mean of same quarter type) and <strong style={{ color: C.violet }}>Linear Trend</strong> (regression on sequential data).
          </div>
        </div>
      </div>

      <div className="grid-3">
        {projections.map((p, i) => {
          const color = p.type === "Winter" ? C.winter : p.type === "Spring" ? C.spring : C.fall;
          return (
            <Card key={i} style={{ borderTop: `2px solid ${color}33` }}>
              <div className="forecast-card">
                <div className="forecast-label">{p.q} Forecast</div>
                <div className="forecast-grid">
                  <div className="forecast-model" style={{ background: `${C.teal}08`, borderColor: `${C.teal}22` }}>
                    <div className="forecast-model-label" style={{ color: C.teal }}>Avg Model</div>
                    <div className="forecast-model-value" style={{ color: C.teal }}>{fmt(p.avg)}</div>
                  </div>
                  <div className="forecast-model" style={{ background: `${C.violet}08`, borderColor: `${C.violet}22` }}>
                    <div className="forecast-model-label" style={{ color: C.violet }}>Trend Model</div>
                    <div className="forecast-model-value" style={{ color: C.violet }}>{fmt(p.trend)}</div>
                  </div>
                </div>
                <div className="forecast-note">Based on {p.samples} historical {p.type} quarter{p.samples > 1 ? "s" : ""}</div>
              </div>
            </Card>
          );
        })}
        <Card style={{ borderTop: `2px solid ${C.navy}33` }}>
          <div className="forecast-card">
            <div className="forecast-label">Full Year Projection</div>
            <div className="forecast-grid">
              <div className="forecast-model" style={{ background: `${C.teal}08`, borderColor: `${C.teal}22` }}>
                <div className="forecast-model-label" style={{ color: C.teal }}>Avg Model</div>
                <div className="forecast-model-value" style={{ color: C.teal }}>{fmt(fullYearAvg)}</div>
              </div>
              <div className="forecast-model" style={{ background: `${C.violet}08`, borderColor: `${C.violet}22` }}>
                <div className="forecast-model-label" style={{ color: C.violet }}>Trend Model</div>
                <div className="forecast-model-value" style={{ color: C.violet }}>{fmt(fullYearTrend)}</div>
              </div>
            </div>
            <div className="forecast-note">Fall actual + forecasted quarters</div>
          </div>
        </Card>
      </div>

      <Section title="Actual vs. Forecast Timeline" sub="Historical data with projected future quarters">
        <Card>
          <ResponsiveContainer width="100%" height={280}>
            <ComposedChart data={compChart}>
              <defs>
                <linearGradient id="gA" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={C.navy} stopOpacity={0.12} />
                  <stop offset="100%" stopColor={C.navy} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} vertical={false} />
              <XAxis dataKey="name" tick={{ fill: C.textSec, fontSize: 11, fontFamily: "'JetBrains Mono'" }} axisLine={{ stroke: C.border }} tickLine={false} />
              <YAxis tick={{ fill: C.textMut, fontSize: 10 }} tickFormatter={fmt} axisLine={false} tickLine={false} />
              <Tooltip content={<TT />} />
              <ReferenceLine x={lastActualLabel} stroke={C.textMut} strokeDasharray="5 5" label={{ value: "\u2190 Actual | Forecast \u2192", fill: C.textMut, fontSize: 10, position: "top" }} />
              <Area type="monotone" dataKey="actual" name="Actual" stroke={C.navy} fill="url(#gA)" strokeWidth={2} dot={{ r: 4, fill: C.navy, stroke: C.bg, strokeWidth: 2 }} connectNulls={false} />
              <Line type="monotone" dataKey="forecast" name="Avg Forecast" stroke={C.teal} strokeWidth={2} strokeDasharray="8 4" dot={{ r: 4, fill: C.teal, stroke: C.bg, strokeWidth: 2 }} connectNulls={false} />
              <Line type="monotone" dataKey="trendForecast" name="Trend Forecast" stroke={C.violet} strokeWidth={1.5} strokeDasharray="4 4" dot={{ r: 3, fill: C.violet, stroke: C.bg, strokeWidth: 2 }} connectNulls={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </Card>
      </Section>

      <div className="grid-2">
        <Section title="Events & Efficiency Trend" sub="Event volume vs. per-event spending over time">
          <Card>
            <ResponsiveContainer width="100%" height={240}>
              <ComposedChart data={eventTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} vertical={false} />
                <XAxis dataKey="name" tick={{ fill: C.textSec, fontSize: 10, fontFamily: "'JetBrains Mono'" }} axisLine={{ stroke: C.border }} tickLine={false} />
                <YAxis yAxisId="l" tick={{ fill: C.textMut, fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis yAxisId="r" orientation="right" tick={{ fill: C.textMut, fontSize: 10 }} tickFormatter={v => `$${v}`} axisLine={false} tickLine={false} />
                <Tooltip content={<TT />} />
                <Bar yAxisId="l" dataKey="events" name="Events" fill={`${C.blue}44`} radius={[4, 4, 0, 0]} />
                <Line yAxisId="r" type="monotone" dataKey="avg" name="Avg/Event" stroke={C.red} strokeWidth={2} dot={{ r: 3, fill: C.red }} />
              </ComposedChart>
            </ResponsiveContainer>
          </Card>
        </Section>

        <Section title="Model Methodology" sub="How the forecasts are calculated">
          <Card>
            <div className="method-block" style={{ borderColor: `${C.teal}22` }}>
              <div className="method-title" style={{ color: C.teal }}>Simple Average Model</div>
              <div className="method-desc">Takes the mean of all historical quarters of the same type. Best when spending is stable across years.</div>
            </div>
            <div className="method-block" style={{ borderColor: `${C.violet}22` }}>
              <div className="method-title" style={{ color: C.violet }}>Linear Trend Model</div>
              <div className="method-desc">Fits a line through sequential same-type quarters and extrapolates. Captures directional trends (growth or decline).</div>
            </div>
            <div className="method-block" style={{ borderColor: `${C.amber}22` }}>
              <div className="method-title" style={{ color: C.amber }}>Limitations</div>
              <div className="method-desc">Limited historical samples. External factors (policy changes, enrollment, inflation) not modeled. Treat as directional estimates.</div>
            </div>
          </Card>
        </Section>
      </div>
    </div>
  );
}

// ── TAB: INSIGHTS ─────────────────────────────────────────────────
function InsightsTab({ QO, QL, QS, TOP_ORGS, GRAND, seasonality }) {
  const orgEfficiency = useMemo(() =>
    TOP_ORGS.slice(0, 12).map(o => ({
      name: o.o.length > 18 ? o.o.substring(0, 18) + "\u2026" : o.o,
      total: o.t, events: o.e, avg: o.av, fullName: o.o,
    })),
    [TOP_ORGS]
  );

  const concentration = useMemo(() =>
    QO.map(q => {
      const s = QS.find(x => x.q === q);
      const top3 = s.top.slice(0, 3).reduce((a, b) => a + b.t, 0);
      return { name: QL[q], top3pct: Math.round((top3 / s.t) * 100), rest: 100 - Math.round((top3 / s.t) * 100) };
    }),
    [QO, QL, QS]
  );

  const firstQ = QS[0];
  const lastQ = QS[QS.length - 1];

  return (
    <div>
      <Section title="Funding Concentration Risk" sub="How much of each quarter's budget goes to just 3 organizations?">
        <Card>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={concentration} barCategoryGap="18%">
              <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} vertical={false} />
              <XAxis dataKey="name" tick={{ fill: C.textSec, fontSize: 11, fontFamily: "'JetBrains Mono'" }} axisLine={{ stroke: C.border }} tickLine={false} />
              <YAxis tick={{ fill: C.textMut, fontSize: 10 }} tickFormatter={v => `${v}%`} domain={[0, 100]} axisLine={false} tickLine={false} />
              <Tooltip content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                return (
                  <div className="tooltip">
                    <div className="tooltip-label">{label}</div>
                    <div className="tooltip-value" style={{ color: C.red }}>{payload[0]?.value}% to top 3 orgs</div>
                  </div>
                );
              }} />
              <Bar dataKey="top3pct" name="Top 3 Share" stackId="a" fill={C.red} radius={[0, 0, 0, 0]} />
              <Bar dataKey="rest" name="Others" stackId="a" fill={`${C.teal}44`} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="callout" style={{ borderColor: `${C.red}33` }}>
            <div className="callout-body">
              <strong style={{ color: C.red }}>Concentration varies significantly.</strong> In some quarters, the top 3 orgs absorb 25-30% of all funding.
              Monitoring this helps ensure equitable distribution across the {GRAND.orgs} registered organizations.
            </div>
          </div>
        </Card>
      </Section>

      <div className="grid-2">
        <Section title="Big Spenders vs. Frequent Requesters" sub="High total doesn't always mean high frequency">
          <Card>
            <ResponsiveContainer width="100%" height={260}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke={C.borderLight} />
                <XAxis dataKey="events" name="Events" tick={{ fill: C.textMut, fontSize: 10 }} axisLine={{ stroke: C.border }} tickLine={false} label={{ value: "Events", fill: C.textMut, fontSize: 10, position: "bottom", offset: -2 }} />
                <YAxis dataKey="avg" name="Avg/Event" tick={{ fill: C.textMut, fontSize: 10 }} tickFormatter={v => fmt(v)} axisLine={false} tickLine={false} label={{ value: "Avg/Event", fill: C.textMut, fontSize: 10, angle: -90, position: "insideLeft", offset: 10 }} />
                <Tooltip content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const d = payload[0]?.payload;
                  return (
                    <div className="tooltip">
                      <div style={{ fontSize: 12, color: C.text, fontWeight: 600, marginBottom: 4 }}>{d?.fullName}</div>
                      <div className="tooltip-label">{d?.events} events · {fmt(d?.avg)}/event · {fmt(d?.total)} total</div>
                    </div>
                  );
                }} />
                <Scatter data={orgEfficiency} fill={C.navy}>
                  {orgEfficiency.map((_, i) => <Cell key={i} fill={PAL[i % PAL.length]} />)}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </Card>
        </Section>

        <Section title="Spending Rhythm by Quarter Type" sub="When does spending peak within each quarter?">
          <Card>
            <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
              {[
                { type: "Spring", color: C.spring, peak: "April\u2013May", desc: "Events cluster mid-quarter. June drops off sharply as finals approach." },
                { type: "Winter", color: C.winter, peak: "January\u2013February", desc: "Steady Jan\u2013Feb, then rapid March decline." },
                { type: "Fall", color: C.fall, peak: "October", desc: "Massive October spike (Welcome Week + GBMs). Tapers through Nov\u2013Dec." },
              ].map((p, i) => (
                <div key={i} className="rhythm-card">
                  <div className="rhythm-header">
                    <span className="rhythm-type" style={{ color: p.color }}>{p.type}</span>
                    <span className="rhythm-peak">Peak: {p.peak}</span>
                  </div>
                  <div className="rhythm-desc">{p.desc}</div>
                </div>
              ))}
            </div>
          </Card>
        </Section>
      </div>

      <Section title="Key Takeaways for Budget Planning" sub="Actionable insights from the data">
        <Card>
          <div className="insights-grid">
            {[
              { title: "Spring is King", body: seasonality.length > 0 ? `Spring quarters average ${fmt(seasonality.find(s => s.type === "Spring")?.avg || 0)}.` : "Spring quarters tend to be the highest.", color: C.spring },
              { title: "Declining Avg/Event", body: `From $${firstQ.a}/event (${firstQ.q.replace("_", " ")}) to $${lastQ.a} (${lastQ.q.replace("_", " ")}). More orgs requesting smaller amounts.`, color: C.red },
              { title: "Consistent Giants", body: `The top organizations appear in ${Math.max(...TOP_ORGS.slice(0, 5).map(o => o.nq))} or more quarters. They're the most reliable budget lines.`, color: C.navy },
              { title: "Event Volume Growing", body: `From ${firstQ.n} events to ${lastQ.n} \u2014 a ${Math.round(((lastQ.n / firstQ.n) - 1) * 100)}% increase. Budget per-event is compressing.`, color: C.blue },
              { title: "The $250\u2013500 Sweet Spot", body: "Across all quarters, the $250\u2013500 range is the most common award size.", color: C.violet },
              { title: "Monitor Trends", body: "Watch whether total spending per quarter stabilizes or continues shifting. More data points improve forecast accuracy.", color: C.amber },
            ].map((insight, i) => (
              <div key={i} className="insight" style={{ borderLeftColor: insight.color }}>
                <div className="insight-title">{insight.title}</div>
                <div className="insight-body">{insight.body}</div>
              </div>
            ))}
          </div>
        </Card>
      </Section>
    </div>
  );
}

// ── MAIN APP ──────────────────────────────────────────────────────
const TABS = [
  { id: "overview", label: "Overview" },
  { id: "quarters", label: "Quarter Drill" },
  { id: "orgs", label: "Org Tracker" },
  { id: "forecast", label: "Forecasting" },
  { id: "insights", label: "Insights" },
];

export default function App() {
  const [tab, setTab] = useState("overview");
  const { data, error } = useDashboardData();

  if (error) return <div className="loading"><div className="loading-text">Failed to load data: {error.message}</div></div>;
  if (!data) return <div className="loading"><div className="loading-text">Loading dashboard data...</div></div>;

  const { QO, QL, QF, QS, TOP_ORGS, GRAND, seasonality, academicYears, forecast } = data;

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div>
            <div className="header-title">
              <div className="header-diamond" />
              <h1>AS Funding Analytics</h1>
            </div>
            <p className="header-sub">Associated Students · Student Org Finance · UCSD</p>
          </div>
          <div className="header-status">
            <div className="header-dot" />
            <span>{QO.length} quarters loaded</span>
          </div>
        </div>
      </header>

      <nav className="nav">
        <div className="nav-inner">
          {TABS.map(t => (
            <button key={t.id} className={`nav-btn${tab === t.id ? " active" : ""}`} onClick={() => setTab(t.id)}>
              {t.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="main">
        {tab === "overview" && <OverviewTab QO={QO} QL={QL} QF={QF} QS={QS} GRAND={GRAND} seasonality={seasonality} academicYears={academicYears} />}
        {tab === "quarters" && <QuarterTab QO={QO} QL={QL} QF={QF} QS={QS} />}
        {tab === "orgs" && <OrgTab QO={QO} QL={QL} QF={QF} TOP_ORGS={TOP_ORGS} GRAND={GRAND} />}
        {tab === "forecast" && <ForecastTab QO={QO} QL={QL} QS={QS} forecast={forecast} />}
        {tab === "insights" && <InsightsTab QO={QO} QL={QL} QS={QS} TOP_ORGS={TOP_ORGS} GRAND={GRAND} seasonality={seasonality} />}
      </main>

      <footer className="footer">
        <span>
          AS Student Org Finance · {QO.length} quarters · {GRAND.orgs} organizations · {fmtN(GRAND.events)} funded events · {fmt(GRAND.total)} total
        </span>
      </footer>
    </div>
  );
}
