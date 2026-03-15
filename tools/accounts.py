"""MCP tools for QuickBooks chart of accounts."""

from quickbooks.objects.account import Account

from db import log_action
from qb_client import get_client


def list_accounts(account_type: str = None) -> str:
    """List chart of accounts. Optionally filter by type: 'Bank', 'Income', 'Expense', 'Other Current Asset', etc."""
    client = get_client()

    if account_type:
        accounts = Account.filter(AccountType=account_type, Active=True, qb=client)
    else:
        accounts = Account.filter(Active=True, qb=client)

    log_action("list_accounts", "read", "Account", details=f"type={account_type}")

    if not accounts:
        return f"No accounts found{f' of type {account_type}' if account_type else ''}."

    lines = []
    for a in accounts:
        balance = a.CurrentBalance or 0
        lines.append(
            f"- [{a.Id}] {a.Name} | {a.AccountType} / {a.AccountSubType or '—'} | ${balance:.2f}"
        )

    return f"**{len(lines)} accounts:**\n" + "\n".join(lines)


def get_account(account_id: str) -> str:
    """Get detailed information about a specific account by ID."""
    client = get_client()
    a = Account.get(account_id, qb=client)
    log_action("get_account", "read", "Account", account_id)

    if not a:
        return f"Account {account_id} not found."

    balance = a.CurrentBalance or 0

    return (
        f"**{a.Name}** (ID: {a.Id})\n"
        f"- Type: {a.AccountType}\n"
        f"- Sub-Type: {a.AccountSubType or '—'}\n"
        f"- Classification: {a.Classification or '—'}\n"
        f"- Balance: ${balance:.2f}\n"
        f"- Active: {a.Active}"
    )
