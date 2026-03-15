"""QuickBooks MCP Server — connects Claude Code to QuickBooks Online."""

import sys
from mcp.server.fastmcp import FastMCP

from tools.customers import list_customers, get_customer, create_customer, search_customers
from tools.invoices import (
    list_invoices, get_invoice, create_invoice, void_invoice, list_unpaid_invoices,
)
from tools.payments import list_payments, get_payment, record_payment
from tools.expenses import list_expenses, get_expense, record_expense
from tools.accounts import list_accounts, get_account
from tools.reports import profit_and_loss, balance_sheet, monthly_summary
from db import get_audit_log

mcp = FastMCP("quickbooks")

# --- Customers ---

@mcp.tool()
def qb_list_customers(active_only: bool = True) -> str:
    """List all QuickBooks customers. Set active_only=False to include inactive."""
    return list_customers(active_only)

@mcp.tool()
def qb_get_customer(customer_id: str) -> str:
    """Get detailed info about a customer by their QuickBooks ID."""
    return get_customer(customer_id)

@mcp.tool()
def qb_create_customer(
    display_name: str,
    email: str = None,
    phone: str = None,
    notes: str = None,
) -> str:
    """Create a new customer in QuickBooks. Only display_name is required."""
    return create_customer(display_name, email, phone, notes)

@mcp.tool()
def qb_search_customers(query: str) -> str:
    """Search customers by name (partial match)."""
    return search_customers(query)

# --- Invoices ---

@mcp.tool()
def qb_list_invoices(status: str = None, max_results: int = 100) -> str:
    """List invoices. Filter by status: 'paid', 'unpaid', or 'all' (default)."""
    return list_invoices(status, max_results)

@mcp.tool()
def qb_get_invoice(invoice_id: str) -> str:
    """Get detailed info about an invoice by its QuickBooks ID."""
    return get_invoice(invoice_id)

@mcp.tool()
def qb_create_invoice(
    customer_id: str,
    line_items: list[dict],
    due_date: str = None,
) -> str:
    """Create a new invoice. line_items is a list of dicts with 'description' and 'amount' keys.
    Example: [{"description": "Coaching Session", "amount": 200}]"""
    return create_invoice(customer_id, line_items, due_date)

@mcp.tool()
def qb_void_invoice(invoice_id: str) -> str:
    """Void an invoice. This cannot be undone."""
    return void_invoice(invoice_id)

@mcp.tool()
def qb_list_unpaid_invoices() -> str:
    """List all unpaid/outstanding invoices."""
    return list_unpaid_invoices()

# --- Payments ---

@mcp.tool()
def qb_list_payments(max_results: int = 100) -> str:
    """List recent payments received."""
    return list_payments(max_results)

@mcp.tool()
def qb_get_payment(payment_id: str) -> str:
    """Get detailed info about a payment by ID."""
    return get_payment(payment_id)

@mcp.tool()
def qb_record_payment(
    customer_id: str,
    amount: float,
    invoice_id: str = None,
    payment_date: str = None,
) -> str:
    """Record a payment received. Optionally link it to an invoice."""
    return record_payment(customer_id, amount, invoice_id, payment_date)

# --- Expenses ---

@mcp.tool()
def qb_list_expenses(max_results: int = 100) -> str:
    """List recent business expenses."""
    return list_expenses(max_results)

@mcp.tool()
def qb_get_expense(expense_id: str) -> str:
    """Get detailed info about an expense by ID."""
    return get_expense(expense_id)

@mcp.tool()
def qb_record_expense(
    amount: float,
    account_id: str,
    description: str = None,
    vendor_name: str = None,
    payment_type: str = "Cash",
    expense_date: str = None,
) -> str:
    """Record a business expense. payment_type can be 'Cash', 'Check', or 'CreditCard'."""
    return record_expense(amount, account_id, description, vendor_name, payment_type, expense_date)

# --- Accounts ---

@mcp.tool()
def qb_list_accounts(account_type: str = None) -> str:
    """List chart of accounts. Optionally filter by type: 'Bank', 'Income', 'Expense', etc."""
    return list_accounts(account_type)

@mcp.tool()
def qb_get_account(account_id: str) -> str:
    """Get detailed info about an account by ID."""
    return get_account(account_id)

# --- Reports ---

@mcp.tool()
def qb_profit_and_loss(start_date: str = None, end_date: str = None) -> str:
    """Get Profit & Loss report. Dates in YYYY-MM-DD format. Defaults to current year."""
    return profit_and_loss(start_date, end_date)

@mcp.tool()
def qb_balance_sheet(as_of_date: str = None) -> str:
    """Get Balance Sheet report. Date in YYYY-MM-DD format. Defaults to today."""
    return balance_sheet(as_of_date)

@mcp.tool()
def qb_monthly_summary(month: int = None, year: int = None) -> str:
    """Get comprehensive monthly summary: P&L, unpaid invoices, payments received."""
    return monthly_summary(month, year)

# --- Audit ---

@mcp.tool()
def qb_audit_log(limit: int = 20) -> str:
    """View recent audit log entries showing all QuickBooks actions taken."""
    entries = get_audit_log(limit)
    if not entries:
        return "No audit log entries yet."

    lines = [f"**Last {len(entries)} actions:**"]
    for e in entries:
        lines.append(
            f"- [{e['timestamp'][:19]}] {e['tool_name']} | {e['action']} | "
            f"{e['entity_type'] or ''} {e['entity_id'] or ''} | {e['details'] or ''}"
        )
    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
