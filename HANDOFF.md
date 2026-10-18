# XAUUSD Signal Dataset — Handoff for Claude

## What is attached

`signals_tracker.csv` contains 12 recovered XAUUSD signal records shared by Francisco between 2026-07-13 and 2026-07-27.

Each row may include entry zone, stop loss, take-profit levels, later trade-management updates, reported outcome, and a normalized R-multiple estimate where the data allows it.

## Important limitations

- This is a research/training dataset only. It is not financial advice and must not be used to generate live `buy` or `sell` recommendations.
- The dataset is incomplete: these are the records currently recovered from the local tracker and historical notes. Do not infer that it represents every signal shared.
- Outcomes are channel-reported, not independently market-verified.
- Some records have incomplete data, unmatched management updates, or R estimates based on midpoint entries. Keep those separate from fully specified records.
- Several signals moved stop loss to break-even before targets. Analyze the trader-management outcome separately from a hypothetical no-break-even path.

## Requested analysis

1. Validate and normalize the CSV without inventing missing values.
2. Classify each record: full signal, partial signal, unmatched update, or incomplete outcome.
3. Produce two performance views:
   - **Trader-reported management**: follow reported BE/SL/TP decisions.
   - **Alternative path**: only where explicitly documented; do not simulate missing data.
4. Report counts, win/loss/BE rates, average and median R, payoff ratio, expectancy, and maximum consecutive losses **only for the subset with reliable outcomes**.
5. Identify repeated signal structure: direction, entry-zone width, stop distance, target distances, break-even timing, and outcome pattern.
6. List the exact additional fields required for a robust 50+ signal study.
7. Return a concise research report and a cleaned CSV schema. Do not issue trade instructions or claims of profitability.

## Output format

- Executive summary (5 bullets)
- Data-quality audit
- Metrics table for reliable-outcome subset
- Pattern observations versus unsupported hypotheses
- Missing-data checklist
- Proposed normalized schema
