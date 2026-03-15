"""MCP tools for QuickBooks payment management."""

from quickbooks.objects.payment import Payment

from db import log_action
from qb_client import get_client


def list_payments(max_results: int = 100) -> str:
    """List recent payments received."""
    client = get_client()
    payments = Payment.all(max_results=max_results, qb=client)

    log_action("list_payments", "read", "Payment")

    if not payments:
        return "No payments found."

    lines = []
    for p in payments:
        cust_name = p.CustomerRef.name if p.CustomerRef else "Unknown"
        amount = p.TotalAmt or 0
        lines.append(
            f"- [{p.Id}] {cust_name} | ${amount:.2f} | {p.TxnDate or '—'}"
        )

    return f"**{len(lines)} payments:**\n" + "\n".join(lines)


def get_payment(payment_id: str) -> str:
    """Get detailed information about a specific payment by ID."""
    client = get_client()
    p = Payment.get(payment_id, qb=client)
    log_action("get_payment", "read", "Payment", payment_id)

    if not p:
        return f"Payment {payment_id} not found."

    cust_name = p.CustomerRef.name if p.CustomerRef else "Unknown"
    amount = p.TotalAmt or 0

    return (
        f"**Payment {p.Id}**\n"
        f"- Customer: {cust_name}\n"
        f"- Amount: ${amount:.2f}\n"
        f"- Date: {p.TxnDate or '—'}\n"
        f"- Method: {p.PaymentMethodRef.name if p.PaymentMethodRef else '—'}"
    )


def record_payment(
    customer_id: str,
    amount: float,
    invoice_id: str = None,
    payment_date: str = None,
) -> str:
    """Record a payment received from a customer.

    Args:
        customer_id: QuickBooks customer ID
        amount: Payment amount
        invoice_id: Optional invoice ID to apply payment to
        payment_date: Optional date in YYYY-MM-DD format (defaults to today)
    """
    client = get_client()
    payment = Payment()
    payment.CustomerRef = {"value": customer_id}
    payment.TotalAmt = amount

    if payment_date:
        payment.TxnDate = payment_date

    if invoice_id:
        payment.Line = [{
            "Amount": amount,
            "LinkedTxn": [{
                "TxnId": invoice_id,
                "TxnType": "Invoice"
            }]
        }]

    payment.save(qb=client)
    log_action(
        "record_payment", "create", "Payment", str(payment.Id),
        f"Customer: {customer_id}, Amount: ${amount:.2f}, Invoice: {invoice_id or 'none'}"
    )

    return (
        f"Payment recorded: **${amount:.2f}** (ID: {payment.Id})\n"
        f"- Customer ID: {customer_id}\n"
        f"- Applied to invoice: {invoice_id or 'Unapplied'}"
    )
