---
name: dashboarding
description: Design and review operational, analytical, and product dashboards. Use when creating dashboard UX, choosing charts and metrics, defining drilldowns and filters, or reviewing dashboard usability, query cost, and maintainability.
user-invocable: false
---

# Dashboarding

Build dashboards that help a defined audience make a decision or investigate a
condition. This is a design and review guide; it applies to SignalDB UI work,
Grafana dashboards, and dashboard-like product surfaces.

## Start With A Decision

Before choosing a chart, write down:

- **Audience:** Who uses this, and under what conditions? Executives monitoring
  an outcome, operators responding to an alert, and engineers debugging a
  service need different views.
- **Question:** State the one question the dashboard must answer. Split views
  that serve unrelated questions.
- **Action:** Name the next action for an abnormal value: investigate a linked
  trace, change a filter, open a runbook, or alert an owner.
- **Freshness and scope:** Show the time range, timezone, data delay, selected
  tenant/dataset/environment, and any sampling or aggregation assumptions.

A dashboard is an overview, not a report. Put details behind links, filters,
and drilldowns rather than making every possible field visible.

## Arrange The Investigation

Make the page scannable at a glance and usable under pressure:

1. Put the title, current scope, time range, and shared filters first.
2. Put the primary outcome and its status in the upper-left reading position.
3. Progress from summary to explanation to evidence: overall health, trend and
   breakdown, then logs/traces/tables or links to them.
4. Group panels by the question they answer. Use short section titles that name
   the question or system boundary.
5. Keep the primary path on one screen where practical. Do not make a user
   scroll to learn whether the system is healthy.

For related dashboard families, use a deliberate hierarchy:

- Overview: service, product, or fleet health.
- Component: one service, dependency, region, queue, or workload.
- Investigation: a narrow slice with high-cardinality detail.

Every level should link to its children with the current time range and filter
context preserved. Alert notifications should link directly to the relevant
investigation view, not a generic landing page.

## Use Observability Frameworks Deliberately

Use a consistent metric model rather than a grab bag of panels:

| Scope | Primary signals | Use for |
| --- | --- | --- |
| User-facing service | Rate, errors, duration (RED) | User experience, SLOs, symptom-based alerts |
| Infrastructure resource | Utilization, saturation, errors (USE) | Capacity and resource-cause analysis |
| Top-level service health | Latency, traffic, errors, saturation | A small, complete initial health view |

Show distributions or percentiles for latency; averages can hide slow users.
Show error rate with request volume so a percentage has context. Label error
budgets, SLO targets, and thresholds with their meaning and evaluation window.

## Choose Honest Encodings

| Question | Prefer | Avoid |
| --- | --- | --- |
| Change over time | Line chart, optionally annotated with deploys/incidents | Cards alone for a trend |
| Compare categories | Sorted bars | Pie/donut charts with many categories |
| Part of a whole | Stacked bars or a pie with at most 7 categories | Overlapping or unlabeled areas |
| Current state against a target | Single stat with delta and threshold | A gauge without a meaningful target |
| Locate outliers or ranked causes | Sorted table or bar chart | A legend with dozens of series |
| Inspect individual events | Table with stable columns and a detail link | A chart pretending to be event detail |

- Use bars for categorical comparisons and lines for continuous time series.
- Do not use 3D charts. Avoid dual axes; use them only when relationships are
  explicit and units are clearly labelled.
- Start quantitative axes at zero for bar charts. For line charts, a truncated
  axis is acceptable only when it does not obscure material changes and the
  scale is visible.
- Keep axes, time units, aggregation windows, precision, ordering, and series
  colors consistent across related panels. Normalize comparable resources, such
  as CPU by available cores, before comparing them.
- Reserve semantic colors for status and use them consistently. Never make
  color the only indicator of state; include labels, shapes, or text.
- Avoid excessive stacking. It can conceal regressions and makes individual
  series difficult to compare.

## Make Panels Self-Explanatory

Each panel needs a concise question-oriented title, units, aggregation,
thresholds where applicable, and a description when its interpretation is not
obvious. Titles such as `P99 checkout latency, 5m rolling` are useful; `Latency`
is not.

Account for empty, loading, error, partial-data, and permission-denied states.
An empty result must say whether it means no matching data, an invalid filter,
or unavailable data. Never imply zero when the query failed or data is delayed.

## Design Filters And Drilldowns

- Provide only filters that change a common analytical dimension, such as
  tenant, dataset, environment, region, service, or time range.
- Set safe, useful defaults. A production overview should not silently combine
  staging data, and a high-cardinality selector should require a scoped choice
  or search rather than loading every value.
- Make filter scope obvious. Preserve scope in URLs, shared links, and
  drilldowns.
- Use a global time range by default. A panel-specific time range needs a clear
  visible reason.
- Supply investigation links from aggregates to traces, logs, profiles, and
  runbooks. Pass relevant dimensions and the time window, but do not pass
  unvalidated query text or sensitive values.

## Protect Dashboard Performance

- Bound every query by time and scope. Default to a practical recent window.
- Aggregate before visualizing and use a resolution appropriate to the selected
  time range. Do not request raw events to render an overview chart.
- Limit returned series and table rows. Rank or filter high-cardinality values,
  then offer a drilldown for exhaustive inspection.
- Avoid auto-refresh rates faster than data freshness or operator need. Make
  expensive panels opt-in, lazy, or collapsible where the product supports it.
- Show partial results, query errors, and stale data distinctly. Do not hide a
  failed panel behind an empty visualization.

## Maintain A Dashboard System

- Name dashboards by subject and purpose, identify an owner, and label the
  intended environment and audience.
- Reuse variables and templates instead of copying one dashboard per tenant,
  cluster, or service. Use copies only for a materially different question.
- Version-control production dashboard definitions. Test experiments separately
  and delete temporary dashboards when finished.
- Periodically review use, broken links, slow panels, stale queries, thresholds,
  and dashboards without an owner. Remove dashboards that no longer answer a
  decision.

## Review Before Shipping

- Can the intended user identify the dashboard's question, scope, and primary
  state within a few seconds?
- Does every panel earn its space by supporting that question or a defined
  drilldown path?
- Are labels, units, time windows, thresholds, and aggregation methods clear?
- Are comparisons fair: compatible scales, normalized values, and stable color
  meanings?
- Are abnormal states actionable through a trace, log, runbook, owner, or
  next-level dashboard?
- Do loading, empty, error, partial, and stale states communicate the truth?
- Are filters accessible on mobile and keyboard-usable, with information not
  conveyed by color alone?
- Do queries have bounded time and cardinality, appropriate refresh intervals,
  and acceptable load time at realistic data volume?

## Research Basis

- [Grafana dashboard best practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
- [Google Cloud Monitoring dashboards](https://cloud.google.com/monitoring/charts/dashboards)
- [Microsoft Power BI dashboard design tips](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips)
