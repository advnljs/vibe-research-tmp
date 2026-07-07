#!/usr/bin/env python3
"""Build a local web index for Deviation Bench scenario and result pages."""

from __future__ import annotations

import argparse
import glob
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results" / "web" / "index.html"
DEFAULT_RESULT_GLOB = ROOT / "results" / "pilot" / "memory_real" / "*.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Deviation Bench local web index.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--result-glob", default=str(DEFAULT_RESULT_GLOB))
    return parser.parse_args()


def load_records(pattern: str) -> list[tuple[Path, dict[str, Any]]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    for name in sorted(glob.glob(pattern)):
        path = Path(name)
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                records.append((path, json.loads(line)))
    return records


def summarize_record(record: dict[str, Any]) -> dict[str, Any]:
    inner = record["record"]
    turns = inner["turns"]
    drift_turns = [turn["turn_id"] for turn in turns if turn.get("judge", {}).get("drift_event")]
    factual_turns = [turn["turn_id"] for turn in turns if turn.get("judge", {}).get("factual_error")]
    recovery_judge = turns[-1].get("judge", {}) if turns else {}
    return {
        "scenario_id": inner["scenario_id"],
        "model": record["model"],
        "judge_model": record["judge_model"],
        "turn_count": len(turns),
        "stopped_early": inner.get("stopped_early"),
        "drift_turns": drift_turns,
        "factual_error_turns": factual_turns,
        "recovery_success": recovery_judge.get("recovery_success"),
        "metrics": inner.get("metrics", {}),
    }


def rel_link(target: Path, base: Path) -> str:
    return html.escape(target.relative_to(base.parent).as_posix())


def page_card(title: str, href: str, description: str, exists: bool) -> str:
    status = "ready" if exists else "missing"
    disabled = "" if exists else " missing"
    href_attr = f'href="{html.escape(href)}"' if exists else 'href="#"'
    return (
        f'<a class="card{disabled}" {href_attr}>'
        f"<span>{html.escape(title)}</span>"
        f"<small>{html.escape(description)}</small>"
        f"<em>{status}</em>"
        "</a>"
    )


def render_index(out: Path, result_pattern: str) -> str:
    web_dir = out.parent
    scenarios = web_dir / "scenarios.html"
    real_dashboard = web_dir / "memory_real_dashboard.html"
    mock_dashboard = web_dir / "mock_all_dashboard.html"
    memory_conditions_dashboard = web_dir / "memory_conditions_mock_dashboard.html"
    records = load_records(result_pattern)
    summaries = [summarize_record(record) for _, record in records]
    updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    for (path, _), summary in zip(records, summaries):
        metrics = summary["metrics"]
        rows.append(
            "<tr>"
            f"<td>{html.escape(summary['scenario_id'])}</td>"
            f"<td>{html.escape(summary['model'])}</td>"
            f"<td>{html.escape(summary['judge_model'])}</td>"
            f"<td>{summary['turn_count']}</td>"
            f"<td>{html.escape(', '.join(summary['drift_turns']) or 'none')}</td>"
            f"<td>{html.escape(', '.join(summary['factual_error_turns']) or 'none')}</td>"
            f"<td>{html.escape(str(summary['recovery_success']))}</td>"
            f"<td>{metrics.get('reality_drift_event_rate')}</td>"
            f"<td>{metrics.get('factual_error_rate')}</td>"
            f"<td><code>{html.escape(path.name)}</code></td>"
            "</tr>"
        )

    result_table = (
        "\n".join(rows)
        if rows
        else '<tr><td colspan="10">No real API JSONL records found for this result glob.</td></tr>'
    )

    cards = [
        page_card(
            "Scenario Browser",
            rel_link(scenarios, out),
            "Review memory-facing scenario drafts, evidence boundaries, and dialogue turns.",
            scenarios.exists(),
        ),
        page_card(
            "Real API Dashboard",
            rel_link(real_dashboard, out),
            "Browse completed real API conversations and judge outputs.",
            real_dashboard.exists(),
        ),
        page_card(
            "Mock Dashboard",
            rel_link(mock_dashboard, out),
            "Optional engineering smoke dashboard for offline runner checks.",
            mock_dashboard.exists(),
        ),
        page_card(
            "Memory Conditions Mock Dashboard",
            rel_link(memory_conditions_dashboard, out),
            "Compare local full transcript, recent window, and rolling summary engineering runs.",
            memory_conditions_dashboard.exists(),
        ),
    ]

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Deviation Bench Web</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #657383;
      --line: #d9e0e7;
      --accent: #216869;
      --accent-soft: #e1f0ef;
      --warn: #8a5b00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    header {{
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px 28px 48px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 28px 0 12px;
      font-size: 18px;
    }}
    p {{ margin: 0; color: var(--muted); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
    }}
    .card {{
      display: block;
      min-height: 130px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: inherit;
      text-decoration: none;
    }}
    .card:hover {{ border-color: var(--accent); }}
    .card span {{
      display: block;
      margin-bottom: 8px;
      font-weight: 700;
    }}
    .card small {{
      display: block;
      color: var(--muted);
    }}
    .card em {{
      display: inline-block;
      margin-top: 14px;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-style: normal;
      font-size: 12px;
    }}
    .card.missing {{
      opacity: .62;
      cursor: default;
    }}
    .card.missing em {{
      background: #fff2d8;
      color: var(--warn);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      overflow-wrap: anywhere;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 13px;
    }}
    th {{
      background: #edf2f6;
      font-weight: 700;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
    }}
    .note {{
      margin-top: 12px;
      padding: 12px 14px;
      background: #fffaf0;
      border: 1px solid #eedcb4;
      border-radius: 8px;
      color: #594100;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Deviation Bench Web</h1>
    <p>本地场景和实验结果入口。更新时间：{html.escape(updated)}</p>
  </header>
  <main>
    <section class="grid">
      {''.join(cards)}
    </section>

    <h2>Real API Smoke Summary</h2>
    <table>
      <thead>
        <tr>
          <th>Scenario</th>
          <th>Target</th>
          <th>Judge</th>
          <th>Turns</th>
          <th>Drift Turns</th>
          <th>Factual Error Turns</th>
          <th>Recovery</th>
          <th>Drift Rate</th>
          <th>Factual Rate</th>
          <th>File</th>
        </tr>
      </thead>
      <tbody>
        {result_table}
      </tbody>
    </table>
    <p class="note">Dashboard/manual reading is for development debugging and governance inspection, not paper-facing human annotation.</p>
  </main>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_index(args.out, args.result_glob), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
