"""MCP tools for QuickBooks customer management."""

from quickbooks.objects.customer import Customer

from db import log_action
from qb_client import get_client


def list_customers(active_only: bool = True) -> str:
    """List all customers. Set active_only=False to include inactive customers."""
    client = get_client()
    if active_only:
        customers = Customer.filter(Active=True, qb=client)
    else:
        customers = Customer.all(qb=client)

    log_action("list_customers", "read", "Customer")

    if not customers:
        return "No customers found."

    lines = []
    for c in customers:
        email = c.PrimaryEmailAddr.Address if c.PrimaryEmailAddr else "—"
        balance = c.Balance or 0
        lines.append(f"- [{c.Id}] {c.DisplayName} | {email} | Balance: ${balance:.2f}")

    return f"**{len(lines)} customers:**\n" + "\n".join(lines)


def get_customer(customer_id: str) -> str:
    """Get detailed information about a specific customer by their ID."""
    client = get_client()
    customer = Customer.get(customer_id, qb=client)
    log_action("get_customer", "read", "Customer", customer_id)

    if not customer:
        return f"Customer {customer_id} not found."

    email = customer.PrimaryEmailAddr.Address if customer.PrimaryEmailAddr else "—"
    phone = customer.PrimaryPhone.FreeFormNumber if customer.PrimaryPhone else "—"
    balance = customer.Balance or 0

    return (
        f"**{customer.DisplayName}** (ID: {customer.Id})\n"
        f"- Email: {email}\n"
        f"- Phone: {phone}\n"
        f"- Balance: ${balance:.2f}\n"
        f"- Active: {customer.Active}\n"
        f"- Created: {customer.MetaData.get('CreateTime', '—') if customer.MetaData else '—'}"
    )


def create_customer(
    display_name: str,
    email: str = None,
    phone: str = None,
    notes: str = None,
) -> str:
    """Create a new customer. Display name is required. Email, phone, and notes are optional."""
    client = get_client()
    customer = Customer()
    customer.DisplayName = display_name

    if email:
        customer.PrimaryEmailAddr = {"Address": email}
    if phone:
        customer.PrimaryPhone = {"FreeFormNumber": phone}
    if notes:
        customer.Notes = notes

    customer.save(qb=client)
    log_action("create_customer", "create", "Customer", str(customer.Id),
               f"Created: {display_name}")

    return f"Customer created: **{customer.DisplayName}** (ID: {customer.Id})"


def search_customers(query: str) -> str:
    """Search customers by name (partial match supported)."""
    client = get_client()
    customers = Customer.where(
        f"DisplayName LIKE '%{query}%'", qb=client
    )
    log_action("search_customers", "read", "Customer", details=f"query: {query}")

    if not customers:
        return f"No customers found matching '{query}'."

    lines = []
    for c in customers:
        balance = c.Balance or 0
        lines.append(f"- [{c.Id}] {c.DisplayName} | Balance: ${balance:.2f}")

    return f"**{len(lines)} matches for '{query}':**\n" + "\n".join(lines)
