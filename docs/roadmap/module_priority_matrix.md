# Module Priority Matrix

| Module | Portfolio Value | Technical Complexity | Safety Risk | Recommended First PR | Notes |
| --- | --- | --- | --- | --- | --- |
| GitHub README landing page | Very high | Low | Low | GH-SHOWCASE-001 | First impression surface for recruiters and contributors. |
| Risk Score Widget | High | Medium | Low | DASH-RISK-001 | Best early technical showcase because it reinforces safety. |
| Backtest Results Viewer | High | Medium | Low | DASH-BT-001 | Strong quant credibility and easy to explain visually. |
| Walk-Forward Viewer | High | Medium | Low | DASH-WF-001 | Shows out-of-sample discipline and model validation maturity. |
| AI Explanation Feed | High | Medium | Low | DASH-AI-001 | Makes the system understandable and review-friendly. |
| Discord Alerts | Medium | Medium | Low | ALERTS-DISCORD-001 | Keep read-only and informational only. |
| PWA Alerts / Watchlist | Medium | High | Low | ALERTS-PWA-001 | Good product polish with read-only alerts; should follow the showcase layer. |
| Weekly PDF Report | Medium | Medium | Low | REPORTS-001 | Nice recruiter artifact and useful review output. |
| Settings Persistence | Medium | Medium | Medium | GH-SHOWCASE-002 | Must keep safety-critical settings locked and auditable. |
| Audit Log Feed | High | Medium | Low | DASH-RISK-001 | Reinforces trust, traceability, and review-first UX. |
| Live vs Sim Reconciliation Dashboard | Very high | High | Medium | DASH-WF-001 | Useful for credibility, but needs careful wording and clear read-only boundaries. |

## Reading The Matrix

- portfolio value measures how useful the module is for GitHub, recruiter, and community visibility
- technical complexity measures implementation effort and integration surface
- safety risk measures how likely the module is to create unsafe product pressure if not constrained
- recommended first PR identifies the safest and most strategic starting point

## Priority Guidance

1. start with showcase and safety framing
2. move to risk, backtest, and walk-forward proof
3. add explanation and audit layers
4. finish with alerts, persistence, and export surfaces

This order helps the project read as disciplined, credible, and review-first rather than execution-oriented.
