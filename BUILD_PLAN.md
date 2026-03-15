# QuickBooks MCP Server — Build Plan

## Step 1: Project Setup ✅
- [x] Create `pyproject.toml` with dependencies: `mcp[cli]`, `python-quickbooks`
- [x] Create `.env` with credentials
- [x] Create `.gitignore`
- [x] Create Python virtual environment and install dependencies
- **Check:** `python -c "import mcp; import quickbooks; print('OK')"` — PASSED

## Step 2: SQLite Database Layer (`db.py`) ✅
- [x] Token storage table (access_token, refresh_token, realm_id, expiry timestamps)
- [x] Audit log table (timestamp, tool_name, action, entity_type, entity_id, details)
- [x] Functions: save_tokens, load_tokens, log_action, get_audit_log
- **Check:** DB initializes, audit log write/read works — PASSED

## Step 3: QuickBooks Client Wrapper (`qb_client.py`) ✅
- [x] OAuth2 authorization flow (local HTTP server on port 8099)
- [x] Token refresh logic (auto-refresh when access token expires)
- [x] Token persistence via `db.py`
- [x] QuickBooks client initialization
- **Check:** Compiles clean, OAuth flow ready — NEEDS LIVE TEST (Step 13)

## Step 4: MCP Tools — Customers (`tools/customers.py`) ✅
- [x] `list_customers`, `get_customer`, `create_customer`, `search_customers`
- **Check:** Imports clean, registered in server — PASSED

## Step 5: MCP Tools — Invoices (`tools/invoices.py`) ✅
- [x] `list_invoices`, `get_invoice`, `create_invoice`, `void_invoice`, `list_unpaid_invoices`
- **Check:** Imports clean, registered in server — PASSED

## Step 6: MCP Tools — Payments (`tools/payments.py`) ✅
- [x] `list_payments`, `get_payment`, `record_payment`
- **Check:** Imports clean, registered in server — PASSED

## Step 7: MCP Tools — Expenses (`tools/expenses.py`) ✅
- [x] `list_expenses`, `get_expense`, `record_expense`
- **Check:** Imports clean, registered in server — PASSED

## Step 8: MCP Tools — Accounts (`tools/accounts.py`) ✅
- [x] `list_accounts`, `get_account`
- **Check:** Imports clean, registered in server — PASSED

## Step 9: MCP Tools — Reports (`tools/reports.py`) ✅
- [x] `profit_and_loss`, `balance_sheet`, `monthly_summary`
- [x] Uses `get_report()` method from python-quickbooks SDK
- **Check:** Imports clean, registered in server — PASSED

## Step 10: MCP Server Entry Point (`server.py`) ✅
- [x] 21 tools registered via FastMCP
- [x] Includes `qb_audit_log` tool for reviewing actions
- [x] Stderr-only logging
- **Check:** All 21 tools load and register — PASSED

## Step 11: Monthly Report Script (`monthly_report.py`) ✅
- [x] Standalone script, reuses report tools
- [x] Saves to `reports/YYYY-MM.txt`
- [x] Cron-ready with shebang and path setup
- **Check:** Compiles clean — NEEDS LIVE TEST (Step 13)

## Step 12: MCP Configuration (`.mcp.json`) ✅
- [x] Created with correct venv Python path and server.py
- **Check:** JSON valid — NEEDS CLAUDE CODE RESTART to verify

## Step 13: End-to-End Verification ⏳
- [ ] Restart Claude Code so `.mcp.json` is picked up
- [ ] First run: OAuth flow opens browser, authorize with QuickBooks sandbox
- [ ] Test: "list my customers" — verifies read path
- [ ] Test: "show me my P&L" — verifies reports
- [ ] Test: "create a test invoice" — verifies write path
- [ ] Test: "show audit log" — verifies audit trail
- [ ] Run `monthly_report.py` — verifies cron script
