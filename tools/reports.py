"""MCP tools for QuickBooks financial reports."""

import json
from datetime import datetime, date
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.payment import Payment

from db import log_action
from qb_client import get_client


def _fetch_report(client, report_name: str, params: dict = None) -> dict:
    """Fetch a report using the python-quickbooks get_report method."""
    return client.get_report(report_name, qs=params or {})


def _format_report_rows(rows_data, indent: int = 0) -> list[str]:
    """Recursively format report rows into readable lines."""
    lines = []
    prefix = "  " * indent

    if not rows_data:
        return lines

    row_list = rows_data.get("Row", [])
    for row in row_list:
        row_type = row.get("type", "")

        if row_type == "Section":
            header = row.get("Header", {})
            col_data = header.get("ColData", [])
            if col_data:
                label = col_data[0].get("value", "")
                if label:
                    lines.append(f"{prefix}**{label}**")

            # Recurse into section rows
            if "Rows" in row:
                lines.extend(_format_report_rows(row["Rows"], indent + 1))

            # Summary row
            summary = row.get("Summary", {})
            sum_cols = summary.get("ColData", [])
            if sum_cols:
                label = sum_cols[0].get("value", "")
                values = [c.get("value", "") for c in sum_cols[1:]]
                if label:
                    lines.append(f"{prefix}**{label}**: {' | '.join(values)}")

        elif row_type == "Data":
            col_data = row.get("ColData", [])
            if col_data:
                label = col_data[0].get("value", "")
                values = [c.get("value", "") for c in col_data[1:]]
                lines.append(f"{prefix}{label}: {' | '.join(values)}")

    return lines


def profit_and_loss(
    start_date: str = None,
    end_date: str = None,
) -> str:
    """Get Profit & Loss report.

    Args:
        start_date: Start date YYYY-MM-DD (defaults to start of current year)
        end_date: End date YYYY-MM-DD (defaults to today)
    """
    client = get_client()

    today = date.today()
    if not start_date:
        start_date = f"{today.year}-01-01"
    if not end_date:
        end_date = today.isoformat()

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "minorversion": "75",
    }

    log_action("profit_and_loss", "read", "Report",
               details=f"{start_date} to {end_date}")

    try:
        report = _fetch_report(client, "ProfitAndLoss", params)

        if isinstance(report, dict):
            header = report.get("Header", {})
            report_name = header.get("ReportName", "Profit and Loss")
            period = header.get("DateMacro", f"{start_date} to {end_date}")

            lines = [f"**{report_name}** ({start_date} to {end_date})\n"]

            rows = report.get("Rows", {})
            lines.extend(_format_report_rows(rows))

            return "\n".join(lines) if lines else "Report returned no data."
        else:
            return f"Report data: {report}"
    except Exception as e:
        return f"Error fetching P&L report: {e}"


def balance_sheet(as_of_date: str = None) -> str:
    """Get Balance Sheet report.

    Args:
        as_of_date: Date in YYYY-MM-DD format (defaults to today)
    """
    client = get_client()

    if not as_of_date:
        as_of_date = date.today().isoformat()

    params = {
        "date_macro": "Today" if as_of_date == date.today().isoformat() else None,
        "start_date": as_of_date,
        "end_date": as_of_date,
        "minorversion": "75",
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    log_action("balance_sheet", "read", "Report", details=f"as_of: {as_of_date}")

    try:
        report = _fetch_report(client, "BalanceSheet", params)

        if isinstance(report, dict):
            lines = [f"**Balance Sheet** (as of {as_of_date})\n"]
            rows = report.get("Rows", {})
            lines.extend(_format_report_rows(rows))
            return "\n".join(lines) if lines else "Report returned no data."
        else:
            return f"Report data: {report}"
    except Exception as e:
        return f"Error fetching Balance Sheet: {e}"


def monthly_summary(month: int = None, year: int = None) -> str:
    """Get a comprehensive monthly summary including P&L highlights, outstanding invoices, and recent payments.

    Args:
        month: Month number 1-12 (defaults to current month)
        year: Year (defaults to current year)
    """
    client = get_client()

    today = date.today()
    if not month:
        month = today.month
    if not year:
        year = today.year

    # Date range for the month
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"

    log_action("monthly_summary", "read", "Report",
               details=f"{year}-{month:02d}")

    sections = [f"**Monthly Summary — {year}-{month:02d}**\n"]

    # P&L summary
    try:
        pnl = _fetch_report(client, "ProfitAndLoss", {
            "start_date": start_date,
            "end_date": end_date,
            "minorversion": "75",
        })
        if isinstance(pnl, dict):
            rows = pnl.get("Rows", {})
            pnl_lines = _format_report_rows(rows)
            if pnl_lines:
                sections.append("## Income & Expenses")
                sections.extend(pnl_lines)
                sections.append("")
    except Exception as e:
        sections.append(f"(Could not fetch P&L: {e})\n")

    # Unpaid invoices
    try:
        unpaid = Invoice.where("Balance > '0'", qb=client)
        if unpaid:
            total_outstanding = sum(float(inv.Balance or 0) for inv in unpaid)
            sections.append(f"## Outstanding Invoices ({len(unpaid)} unpaid, ${total_outstanding:.2f} total)")
            for inv in unpaid:
                cust = inv.CustomerRef.name if inv.CustomerRef else "Unknown"
                sections.append(
                    f"- #{inv.DocNumber or inv.Id} | {cust} | "
                    f"${float(inv.Balance or 0):.2f} due | {inv.DueDate or '—'}"
                )
            sections.append("")
        else:
            sections.append("## Outstanding Invoices\nAll invoices are paid!\n")
    except Exception as e:
        sections.append(f"(Could not fetch invoices: {e})\n")

    # Recent payments
    try:
        payments = Payment.where(
            f"TxnDate >= '{start_date}' AND TxnDate < '{end_date}'",
            qb=client
        )
        if payments:
            total_received = sum(float(p.TotalAmt or 0) for p in payments)
            sections.append(f"## Payments Received (${total_received:.2f} total)")
            for p in payments:
                cust = p.CustomerRef.name if p.CustomerRef else "Unknown"
                sections.append(
                    f"- {cust} | ${float(p.TotalAmt or 0):.2f} | {p.TxnDate or '—'}"
                )
            sections.append("")
        else:
            sections.append("## Payments Received\nNo payments this month.\n")
    except Exception as e:
        sections.append(f"(Could not fetch payments: {e})\n")

    return "\n".join(sections)
