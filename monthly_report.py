#!/usr/bin/env python3
"""Standalone monthly report script for cron.

Usage:
    python monthly_report.py              # Current month
    python monthly_report.py 2026 3       # March 2026

Cron example (1st of each month at 9am):
    0 9 1 * * /Users/joshterry/code/quickbooks/.venv/bin/python /Users/joshterry/code/quickbooks/monthly_report.py
"""

import sys
from datetime import date
from pathlib import Path

# Ensure project is on path
sys.path.insert(0, str(Path(__file__).parent))

from tools.reports import monthly_summary


def main():
    today = date.today()

    if len(sys.argv) >= 3:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
    else:
        # Default to previous month (since cron runs on 1st)
        if today.day <= 5:
            if today.month == 1:
                month = 12
                year = today.year - 1
            else:
                month = today.month - 1
                year = today.year
        else:
            month = today.month
            year = today.year

    print(f"Generating report for {year}-{month:02d}...", file=sys.stderr)

    report = monthly_summary(month=month, year=year)

    # Save to reports directory
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    filename = reports_dir / f"{year}-{month:02d}.txt"
    filename.write_text(report)

    print(f"Report saved to {filename}", file=sys.stderr)
    print(report)


if __name__ == "__main__":
    main()
