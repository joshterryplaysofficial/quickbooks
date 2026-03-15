"""MCP tools for QuickBooks expense/purchase management."""

from quickbooks.objects.purchase import Purchase

from db import log_action
from qb_client import get_client


def list_expenses(max_results: int = 100) -> str:
    """List recent expenses/purchases."""
    client = get_client()
    expenses = Purchase.all(max_results=max_results, qb=client)

    log_action("list_expenses", "read", "Purchase")

    if not expenses:
        return "No expenses found."

    lines = []
    for e in expenses:
        vendor = ""
        if hasattr(e, "EntityRef") and e.EntityRef:
            vendor = e.EntityRef.name or ""
        amount = e.TotalAmt or 0
        pay_type = e.PaymentType or "—"
        lines.append(
            f"- [{e.Id}] {vendor or 'Unknown'} | ${amount:.2f} | {pay_type} | {e.TxnDate or '—'}"
        )

    return f"**{len(lines)} expenses:**\n" + "\n".join(lines)


def get_expense(expense_id: str) -> str:
    """Get detailed information about a specific expense by ID."""
    client = get_client()
    e = Purchase.get(expense_id, qb=client)
    log_action("get_expense", "read", "Purchase", expense_id)

    if not e:
        return f"Expense {expense_id} not found."

    vendor = ""
    if hasattr(e, "EntityRef") and e.EntityRef:
        vendor = e.EntityRef.name or "Unknown"
    amount = e.TotalAmt or 0

    line_details = []
    if e.Line:
        for line in e.Line:
            desc = ""
            if hasattr(line, "Description"):
                desc = line.Description or ""
            acct = ""
            if hasattr(line, "AccountBasedExpenseLineDetail") and line.AccountBasedExpenseLineDetail:
                if line.AccountBasedExpenseLineDetail.AccountRef:
                    acct = line.AccountBasedExpenseLineDetail.AccountRef.name or ""
            line_details.append(f"  - {desc or acct or 'Item'}: ${line.Amount:.2f}")

    result = (
        f"**Expense {e.Id}**\n"
        f"- Vendor: {vendor}\n"
        f"- Amount: ${amount:.2f}\n"
        f"- Payment Type: {e.PaymentType or '—'}\n"
        f"- Date: {e.TxnDate or '—'}\n"
    )

    if line_details:
        result += "- Line Items:\n" + "\n".join(line_details)

    return result


def record_expense(
    amount: float,
    account_id: str,
    description: str = None,
    vendor_name: str = None,
    payment_type: str = "Cash",
    expense_date: str = None,
) -> str:
    """Record a business expense.

    Args:
        amount: Expense amount
        account_id: QuickBooks bank/payment account ID (e.g., checking account)
        description: What the expense was for
        vendor_name: Who you paid (optional)
        payment_type: 'Cash', 'Check', or 'CreditCard' (default: Cash)
        expense_date: Date in YYYY-MM-DD format (defaults to today)
    """
    client = get_client()
    expense = Purchase()
    expense.PaymentType = payment_type
    expense.AccountRef = {"value": account_id}
    expense.TotalAmt = amount

    if expense_date:
        expense.TxnDate = expense_date

    expense.Line = [{
        "DetailType": "AccountBasedExpenseLineDetail",
        "Amount": amount,
        "Description": description or "",
        "AccountBasedExpenseLineDetail": {
            "AccountRef": {"value": account_id}
        }
    }]

    expense.save(qb=client)
    log_action(
        "record_expense", "create", "Purchase", str(expense.Id),
        f"Amount: ${amount:.2f}, Desc: {description or '—'}"
    )

    return (
        f"Expense recorded: **${amount:.2f}** (ID: {expense.Id})\n"
        f"- Description: {description or '—'}\n"
        f"- Payment Type: {payment_type}\n"
        f"- Date: {expense_date or 'today'}"
    )
