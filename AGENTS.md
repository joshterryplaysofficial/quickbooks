# QuickBooks MCP Server — Agent Notes

## Project Overview
Local-only MCP server that connects Claude Code to QuickBooks Online for conversational bookkeeping.
Solo single-user app for a simple business.

## QuickBooks Developer App
- **App Name:** Galaxy Nav App
- **Workspace:** Galaxy-Nav
- **App ID:** d12b9762-f5d6-4da5-aed2-abd03aef1355
- **Status:** In Development (created 2026-03-15)
- **Sandbox Company:** Sandbox Company US aa90
- **Realm ID (Company ID):** 9341456610329123
- **Intuit Developer Portal:** https://developer.intuit.com

## OAuth Configuration
- **Redirect URI:** http://localhost:8099/callback (port 8099 chosen to avoid conflicts with other local dev apps)
- **Scopes:** com.intuit.quickbooks.accounting
- **Environment:** sandbox (switch to production after testing)
- **Token Lifetimes:** Access token = 1 hour, Refresh token = 100 days (rolling)

## Tech Stack
- Python 3.10+
- FastMCP (`mcp` package) — stdio transport
- `python-quickbooks` — QuickBooks API SDK
- SQLite — token storage + audit log
- Cron — monthly report automation

## Key Files
- `.env` — credentials (gitignored, rotate before production)
- `server.py` — MCP server entry point
- `qb_client.py` — OAuth + QB client wrapper
- `db.py` — SQLite token storage + audit log
- `tools/` — MCP tool modules (invoices, expenses, customers, reports, accounts)
- `monthly_report.py` — standalone cron script for monthly summaries

## API Notes
- Use `minorversion=75` or higher (versions 1-74 deprecated Aug 2025)
- Sandbox base URL: https://sandbox-quickbooks.api.intuit.com
- Production base URL: https://quickbooks.api.intuit.com
- Rate limits: 500 req/min per realm, 10 concurrent
- Query language uses single quotes, max 1000 results per query
- Entities that cannot be deleted (deactivate only): Account, Customer, Vendor, Item

## Safety Rules
- Read tools operate freely
- Write tools log to SQLite audit table before executing
- Destructive operations (delete, void) require explicit ID confirmation
- Never print tokens to stdout (corrupts MCP stdio transport)
