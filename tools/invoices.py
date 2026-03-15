"""MCP tools for QuickBooks invoice management."""

import json
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.detailline import SalesItemLine, SalesItemLineDetail
from quickbooks.objects.item import Item

from db import log_action
from qb_client import get_client


def list_invoices(status: str = None, max_results: int = 100) -> str:
    """List invoices. Optionally filter by status: 'paid', 'unpaid', 'overdue', or 'all' (default: all)."""
    client = get_client()

    where_clause = ""
    if status == "unpaid":
        where_clause = "Balance > '0'"
    elif status == "paid":
        where_clause = "Balance = '0'"

    if where_clause:
        invoices = Customer_query = Invoice.where(
            where_clause, max_results=max_results, qb=client
        )
    else:
        invoices = Invoice.all(max_results=max_results, qb=client)

    log_action("list_invoices", "read", "Invoice", details=f"status={status}")

    if not invoices:
        return "No invoices found."

    lines = []
    for inv in invoices:
        cust_name = inv.CustomerRef.name if inv.CustomerRef else "Unknown"
        total = inv.TotalAmt or 0
        balance = inv.Balance or 0
        status_str = "Paid" if balance == 0 else f"Due: ${balance:.2f}"
        lines.append(
            f"- [{inv.Id}] {inv.DocNumber or '—'} | {cust_name} | "
            f"${total:.2f} | {status_str} | {inv.TxnDate or '—'}"
        )

    return f"**{len(lines)} invoices:**\n" + "\n".join(lines)


def get_invoice(invoice_id: str) -> str:
    """Get detailed information about a specific invoice by ID."""
    client = get_client()
    inv = Invoice.get(invoice_id, qb=client)
    log_action("get_invoice", "read", "Invoice", invoice_id)

    if not inv:
        return f"Invoice {invoice_id} not found."

    cust_name = inv.CustomerRef.name if inv.CustomerRef else "Unknown"
    total = inv.TotalAmt or 0
    balance = inv.Balance or 0

    line_items = []
    if inv.Line:
        for line in inv.Line:
            if hasattr(line, "SalesItemLineDetail") and line.SalesItemLineDetail:
                detail = line.SalesItemLineDetail
                item_name = detail.ItemRef.name if detail.ItemRef else "Item"
                qty = detail.Qty or 1
                rate = detail.UnitPrice or 0
                line_items.append(f"  - {item_name}: {qty} x ${rate:.2f} = ${line.Amount:.2f}")
            elif hasattr(line, "Description") and line.Description:
                line_items.append(f"  - {line.Description}: ${line.Amount:.2f}")

    result = (
        f"**Invoice {inv.DocNumber or inv.Id}** (ID: {inv.Id})\n"
        f"- Customer: {cust_name}\n"
        f"- Date: {inv.TxnDate or '—'}\n"
        f"- Due Date: {inv.DueDate or '—'}\n"
        f"- Total: ${total:.2f}\n"
        f"- Balance Due: ${balance:.2f}\n"
        f"- Status: {'Paid' if balance == 0 else 'Unpaid'}\n"
    )

    if line_items:
        result += "- Line Items:\n" + "\n".join(line_items)

    return result


def create_invoice(
    customer_id: str,
    line_items: list[dict],
    due_date: str = None,
) -> str:
    """Create a new invoice.

    Args:
        customer_id: The QuickBooks customer ID
        line_items: List of dicts with 'description', 'amount', and optionally 'quantity'
            Example: [{"description": "Coaching Session", "amount": 200}, {"description": "Program Fee", "amount": 500}]
        due_date: Optional due date in YYYY-MM-DD format
    """
    client = get_client()
    invoice = Invoice()
    invoice.CustomerRef = {"value": customer_id}

    if due_date:
        invoice.DueDate = due_date

    invoice.Line = []
    for item in line_items:
        line = SalesItemLine()
        line.Amount = item["amount"]
        line.Description = item.get("description", "")
        qty = item.get("quantity", 1)

        line.SalesItemLineDetail = SalesItemLineDetail()
        line.SalesItemLineDetail.Qty = qty
        line.SalesItemLineDetail.UnitPrice = item["amount"] / qty
        # Use "Services" item if available, otherwise generic
        line.SalesItemLineDetail.ItemRef = {"value": "1", "name": "Services"}

        invoice.Line.append(line)

    invoice.save(qb=client)
    log_action(
        "create_invoice", "create", "Invoice", str(invoice.Id),
        f"Customer: {customer_id}, Total: ${invoice.TotalAmt:.2f}"
    )

    return (
        f"Invoice created: **#{invoice.DocNumber or invoice.Id}** (ID: {invoice.Id})\n"
        f"- Total: ${invoice.TotalAmt:.2f}\n"
        f"- Due: {invoice.DueDate or 'Not set'}"
    )


def list_unpaid_invoices() -> str:
    """List all unpaid/outstanding invoices."""
    return list_invoices(status="unpaid")


def void_invoice(invoice_id: str) -> str:
    """Void an invoice by ID. This cannot be undone."""
    client = get_client()
    inv = Invoice.get(invoice_id, qb=client)

    if not inv:
        return f"Invoice {invoice_id} not found."

    inv.void(qb=client)
    log_action("void_invoice", "void", "Invoice", invoice_id,
               f"Voided invoice #{inv.DocNumber or invoice_id}")

    return f"Invoice #{inv.DocNumber or invoice_id} (ID: {invoice_id}) has been voided."
