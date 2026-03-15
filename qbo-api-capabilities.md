# QuickBooks Online API - CRUD Operations Reference

Source: Official Intuit Developer API Explorer at developer.intuit.com
Verified: 2026-03-15

## Base URLs

- **Production**: `https://quickbooks.api.intuit.com`
- **Sandbox**: `https://sandbox-quickbooks.api.intuit.com`
- Endpoint pattern: `/v3/company/{realmId}/{entity}`

---

## Entity CRUD Matrix

| Entity       | Create | Read | Update         | Delete | Query | Void | Send (Email) | Get PDF | Notes |
|-------------|--------|------|----------------|--------|-------|------|-------------|---------|-------|
| Account      | YES    | YES  | Full only      | NO     | YES   | NO   | NO          | NO      | No delete, no sparse update. Name must be unique, no double quotes or colons in Name. |
| Invoice      | YES    | YES  | Full + Sparse  | YES    | YES   | YES  | YES         | YES     | Full CRUD plus void, email send, PDF generation. |
| Payment      | YES    | YES  | Full only      | YES    | YES   | YES  | YES         | YES     | Full CRUD plus void, email send, PDF generation. |
| Purchase     | YES    | YES  | Full only      | YES    | YES   | NO   | NO          | NO      | Covers checks, cash purchases, credit card charges. |
| Bill         | YES    | YES  | Full only      | YES    | YES   | NO   | NO          | NO      | Standard CRUD. |
| Customer     | YES    | YES  | Full + Sparse  | NO     | YES   | NO   | NO          | NO      | NO delete. To deactivate, set Active=false via update. DisplayName must be unique. |
| Vendor       | YES    | YES  | Full only      | NO     | YES   | NO   | NO          | NO      | NO delete. To deactivate, set Active=false via update. |
| JournalEntry | YES    | YES  | Full + Sparse  | YES    | YES   | NO   | NO          | NO      | Full CRUD with both update types. |
| Item         | YES    | YES  | Full only      | NO*    | YES   | NO   | NO          | NO      | No hard delete -- use "Inactivate" (set Active=false). Also supports Category create/read/update/query and Bundle read/query. |

*Item uses "Inactivate" instead of delete.

---

## Detailed Entity Operations

### 1. Account
- **CREATE**: `POST /v3/company/{realmId}/account` -- Required: Name, AccountType. Conditionally required: AcctNum, AccountSubType, TaxCodeRef.
- **READ**: `GET /v3/company/{realmId}/account/{accountId}`
- **UPDATE**: `POST /v3/company/{realmId}/account` (full update only, requires Id + SyncToken in body). Must include all writable fields.
- **DELETE**: NOT AVAILABLE. Accounts cannot be deleted via API. Set Active=false to deactivate.
- **QUERY**: `GET /v3/company/{realmId}/query?query=select * from Account where ...`
- **Special notes**: Account.Name must not contain double quotes or colons. Account.AcctNum must not contain colons. Name must be unique. AcctNum max length varies by locale (US/UK/IN: 7 chars, AU/CA: 20 chars, FR: 6-20 chars).

### 2. Invoice
- **CREATE**: `POST /v3/company/{realmId}/invoice`
- **READ**: `GET /v3/company/{realmId}/invoice/{invoiceId}`
- **UPDATE (Full)**: `POST /v3/company/{realmId}/invoice` (requires Id + SyncToken, all writable fields)
- **UPDATE (Sparse)**: `POST /v3/company/{realmId}/invoice` (requires Id + SyncToken + sparse:true, only changed fields)
- **DELETE**: `POST /v3/company/{realmId}/invoice?operation=delete` (requires Id + SyncToken in body)
- **VOID**: `POST /v3/company/{realmId}/invoice?operation=void` (requires Id + SyncToken in body)
- **QUERY**: `GET /v3/company/{realmId}/query?query=select * from Invoice where ...`
- **SEND (Email)**: `POST /v3/company/{realmId}/invoice/{invoiceId}/send?sendTo=email@example.com`
- **GET PDF**: `GET /v3/company/{realmId}/invoice/{invoiceId}/pdf`
- **Special notes**: Has Business Rules section. Full featured entity.

### 3. Payment
- **CREATE**: `POST /v3/company/{realmId}/payment`
- **READ**: `GET /v3/company/{realmId}/payment/{paymentId}`
- **UPDATE (Full)**: `POST /v3/company/{realmId}/payment` (requires Id + SyncToken)
- **DELETE**: `POST /v3/company/{realmId}/payment?operation=delete`
- **VOID**: `POST /v3/company/{realmId}/payment?operation=void`
- **QUERY**: `GET /v3/company/{realmId}/query?query=select * from Payment where ...`
- **SEND (Email)**: `POST /v3/company/{realmId}/payment/{paymentId}/send?sendTo=email@example.com`
- **GET PDF**: `GET /v3/company/{realmId}/payment/{paymentId}/pdf`

### 4. Purchase
- **CREATE**: `POST /v3/company/{realmId}/purchase`
- **READ**: `GET /v3/company/{realmId}/purchase/{purchaseId}`
- **UPDATE (Full)**: `POST /v3/company/{realmId}/purchase` (requires Id + SyncToken)
- **DELETE**: `POST /v3/company/{realmId}/purchase?operation=delete`
- **QUERY**: `GET /v3/company/{realmId}/query?query=select * from Purchase where ...`
- **Special notes**: No void, no email send, no PDF. Covers PaymentType values: Cash, Check, CreditCard.

### 5. Bill
- **CREATE**: `POST /v3/company/{realmId}/bill`
- **READ**: `GET /v3/company/{realmId}/bill/{billId}`
- **UPDATE (Full)**: `POST /v3/company/{realmId}/bill` (requires Id + SyncToken)
- **DELETE**: `POST /v3/company/{realmId}/bill?operation=delete`
- **QUERY**: `GET /v3/company/{realmId}/query?query=select * from Bill where ...`

### 6. Customer
- **CREATE**: `POST /v3/company/{realmId}/customer`
- **READ**: `GET /v3/company/{realmId}/customer/{customerId}`
- **UPDATE (Full)**: `POST /v3/company/{realmId}/customer` (requires Id + SyncToken)
- **UPDATE (Sparse)**: `POST /v3/company/{realmId}/customer` (requires Id + SyncToken + sparse:true)
- **DELETE**: NOT AVAILABLE. Customers cannot be deleted via API. Set Active=false to deactivate.
- **QUERY**: `GET /v3/company/{realmId}/query?query=select * from Customer where ...`
- **Special notes**: Has Business Rules section. DisplayName must be unique across all Customer, Employee, and Vendor objects.

### 7. Vendor
- **CREATE**: `POST /v3/company/{realmId}/vendor`
- **READ**: `GET /v3/company/{realmId}/vendor/{vendorId}`
- **UPDATE (Full)**: `POST /v3/company/{realmId}/vendor` (requires Id + SyncToken)
- **DELETE**: NOT AVAILABLE. Vendors cannot be deleted via API. Set Active=false to deactivate.
- **QUERY**: `GET /v3/company/{realmId}/query?query=select * from Vendor where ...`
- **Special notes**: Has Business Rules section.

### 8. JournalEntry
- **CREATE**: `POST /v3/company/{realmId}/journalentry`
- **READ**: `GET /v3/company/{realmId}/journalentry/{journalentryId}`
- **UPDATE (Full)**: `POST /v3/company/{realmId}/journalentry` (requires Id + SyncToken)
- **UPDATE (Sparse)**: `POST /v3/company/{realmId}/journalentry` (requires Id + SyncToken + sparse:true)
- **DELETE**: `POST /v3/company/{realmId}/journalentry?operation=delete`
- **QUERY**: `GET /v3/company/{realmId}/query?query=select * from JournalEntry where ...`
- **Special notes**: Has Business Rules section.

### 9. Item
- **CREATE Item**: `POST /v3/company/{realmId}/item`
- **CREATE Category**: `POST /v3/company/{realmId}/item` (with Type=Category)
- **READ Item**: `GET /v3/company/{realmId}/item/{itemId}`
- **READ Category**: `GET /v3/company/{realmId}/item/{categoryId}`
- **READ Bundle**: `GET /v3/company/{realmId}/item/{bundleId}`
- **UPDATE Item (Full)**: `POST /v3/company/{realmId}/item` (requires Id + SyncToken)
- **UPDATE Category**: `POST /v3/company/{realmId}/item` (requires Id + SyncToken)
- **DELETE**: NOT AVAILABLE. Use "Inactivate" -- set Active=false via update.
- **QUERY Item**: `GET /v3/company/{realmId}/query?query=select * from Item where Type='Inventory'`
- **QUERY Category**: `GET /v3/company/{realmId}/query?query=select * from Item where Type='Category'`
- **QUERY Bundle**: `GET /v3/company/{realmId}/query?query=select * from Item where Type='Group'`

---

## Report Entities (Read-Only via GET)

Reports are READ-ONLY. They support only Query operations (no create/update/delete). Available reports from the API sidebar:

| Report Entity | Endpoint |
|---|---|
| AccountListDetail | `/v3/company/{realmId}/reports/AccountList` |
| APAgingDetail | `/v3/company/{realmId}/reports/AgedPayableDetail` |
| APAgingSummary | `/v3/company/{realmId}/reports/AgedPayable` |
| ARAgingDetail | `/v3/company/{realmId}/reports/AgedReceivableDetail` |
| ARAgingSummary | `/v3/company/{realmId}/reports/AgedReceivable` |
| BalanceSheet | `/v3/company/{realmId}/reports/BalanceSheet` |
| Budget | `/v3/company/{realmId}/reports/Budget` |
| CashFlow | `/v3/company/{realmId}/reports/CashFlow` |
| CustomerBalance | `/v3/company/{realmId}/reports/CustomerBalance` |
| CustomerBalanceDetail | `/v3/company/{realmId}/reports/CustomerBalanceDetail` |
| CustomerIncome | `/v3/company/{realmId}/reports/CustomerIncome` |
| FECReport | `/v3/company/{realmId}/reports/FECReport` |
| GeneralLedger | `/v3/company/{realmId}/reports/GeneralLedger` |
| GeneralLedgerFR | `/v3/company/{realmId}/reports/GeneralLedgerFR` |
| InventoryValuationDetail | `/v3/company/{realmId}/reports/InventoryValuationDetail` |
| InventoryValuationSummary | `/v3/company/{realmId}/reports/InventoryValuationSummary` |
| JournalReport | `/v3/company/{realmId}/reports/JournalReport` |
| JournalReportFR | `/v3/company/{realmId}/reports/JournalReportFR` |
| ProfitAndLoss | `/v3/company/{realmId}/reports/ProfitAndLoss` |
| ProfitAndLossDetail | `/v3/company/{realmId}/reports/ProfitAndLossDetail` |
| SalesByClassSummary | `/v3/company/{realmId}/reports/ClassSales` |
| SalesByCustomer | `/v3/company/{realmId}/reports/CustomerSales` |
| SalesByDepartment | `/v3/company/{realmId}/reports/DepartmentSales` |
| SalesByProduct | `/v3/company/{realmId}/reports/ItemSales` |
| TaxSummary | `/v3/company/{realmId}/reports/TaxSummary` |
| TransactionList | `/v3/company/{realmId}/reports/TransactionList` |
| TransactionListByVendor | `/v3/company/{realmId}/reports/TransactionListByVendor` |
| TransactionListByCustomer | `/v3/company/{realmId}/reports/TransactionListByCustomer` |
| TransactionListWithSplits | `/v3/company/{realmId}/reports/TransactionListWithSplits` |
| TrialBalance | `/v3/company/{realmId}/reports/TrialBalance` |
| VendorBalance | `/v3/company/{realmId}/reports/VendorBalance` |
| VendorBalanceDetail | `/v3/company/{realmId}/reports/VendorBalanceDetail` |
| VendorExpenses | `/v3/company/{realmId}/reports/VendorExpenses` |

Reports accept query parameters for filtering (date ranges, accounting method, etc.) but vary by report.

---

## Other Notable Entities in the API (from sidebar)

These entities also exist in the API (not detailed above but visible in the sidebar):

- **Attachable** - file attachments (create/read/update/delete/query)
- **Batch** - batch operations (multiple operations in one request)
- **BillPayment** - bill payment records
- **Budget** - budget data (read-only report)
- **ChangeDataCapture** - polling for changes since a timestamp
- **Class** - class tracking
- **CompanyCurrency** - multi-currency settings
- **CompanyInfo** - company information (read/update only)
- **CreditMemo** - credit memos
- **CreditCardPayment** - credit card payment records
- **CustomerType** - customer type classifications
- **Department** - department/location tracking
- **Deposit** - bank deposits
- **Employee** - employee records
- **Entitlements** - subscription entitlements (read-only)
- **Estimate** - estimates/quotes
- **Exchangerate** - currency exchange rates
- **InventoryAdjustment** - inventory adjustments (QBO Plus/Advanced only)
- **PaymentMethod** - payment method types
- **Preferences** - company preferences (read/update only)
- **PurchaseOrder** - purchase orders
- **RecurringTransaction** - recurring/scheduled transactions (read-only via API)
- **RefundReceipt** - refund receipts
- **ReimburseCharge** - billable expense charges
- **SalesReceipt** - point-of-sale receipts
- **TaxAgency** - tax agencies
- **TaxCode** - tax codes (read/query only in most cases)
- **TaxPayment** - tax payments (read-only)
- **TaxRate** - tax rates
- **TaxService** - tax service/rate creation
- **Term** - payment terms
- **TimeActivity** - time tracking entries
- **Transfer** - bank-to-bank transfers
- **TaxClassification** - tax classifications

---

## Things You CANNOT Do via API (But CAN Do in QBO UI)

1. **Delete Accounts, Customers, Vendors, or Items** - API only supports deactivation (Active=false), not hard deletion. The QBO UI also uses "make inactive" so this is consistent.
2. **Reconcile bank accounts** - No bank reconciliation API exists.
3. **Bank feeds / bank connections** - Cannot connect bank accounts or manage bank feed rules via API.
4. **Manage users/roles** - Cannot add/remove QBO users or change permissions.
5. **Payroll operations** - Payroll is a separate product; the accounting API does not cover payroll processing.
6. **Customize templates** - Invoice templates, estimate templates, etc. cannot be managed via API.
7. **Reclassify transactions in bulk** - No bulk reclassification endpoint.
8. **Manage recurring transactions** - RecurringTransaction is READ-ONLY via API. You cannot create or modify recurring transactions.
9. **Manage custom reports** - Only predefined reports are available; you cannot create custom report definitions.
10. **Audit log access** - No API access to the audit log.
11. **Merge duplicates** - Cannot merge duplicate customers, vendors, or accounts via API.
12. **Manage projects** - Limited project support (via Customer sub-customer workaround only).
13. **Inventory lot tracking / serial numbers** - Not available via API.
14. **Direct bank deposit (ACH)** - Requires the separate QuickBooks Payments API.

---

## Sandbox to Production: What's Required

The API works with BOTH sandbox and production accounts. Here is the process to go from sandbox to production (from the official "Publish your app" documentation):

### Steps:
1. **Fill out App Details for Production** - In the Intuit Developer portal under Keys and credentials > Production > App Details. Includes contact email, EULA URL, Privacy Policy URL, host domain, launch URL, disconnect URL, connect/reconnect URL, app categories, regulated industries, and hosting regions. (~30 minutes)

2. **Set up OAuth 2.0** - Ensure OAuth 2.0 authentication is fully implemented. Test connect/disconnect/reconnect flows against sandbox first.

3. **Update Developer Account Profile** - Review contact and account information under My Hub > Account Profile.

4. **Complete the App Assessment Questionnaire** - Under Keys and credentials > Production > Compliance. This is a security/compliance questionnaire that must be approved before production credentials are issued.

5. **Review App Name, Icon, and Settings** - Follow Intuit's naming and logo guidelines. Set up app info under Settings > Basic app info.

6. **Get Production Credentials** - After the questionnaire is approved, toggle "Show Credentials" under Production to get your production Client ID and Client Secret.

### Key differences between sandbox and production:
- **Different base URLs**: sandbox-quickbooks.api.intuit.com vs quickbooks.api.intuit.com
- **Different OAuth credentials**: Separate Client ID and Client Secret for each environment
- **Different realmId values**: Each connected company has its own realmId
- **Same API endpoints and behavior**: The API operations are identical between sandbox and production
- **App Store listing is optional**: You can run a production app privately by sharing its URL directly without listing on the QuickBooks App Store

### Additional production consideration:
- If you want PUBLIC distribution, you must also go through a **three-part app review process** to list on the QuickBooks App Store
- The Intuit App Partner Program is available for partners in US, UK, Australia, and Canada (excluding Quebec)

---

## Update Mechanism Notes

- **Full Update**: Requires sending the ENTIRE object back (all writable fields). Any field omitted is set to empty/null. Always do a Read first, modify fields, then send back.
- **Sparse Update**: Only available on some entities (Invoice, Customer, JournalEntry). Send only Id, SyncToken, sparse:true, and the fields you want to change. Other fields are left untouched.
- **SyncToken**: Required for all updates. Acts as optimistic locking. If another process updated the object, your SyncToken will be stale and the update will fail with a 400 error. Always read the latest SyncToken before updating.
- **Delete mechanism**: Uses `POST` with `?operation=delete` query parameter and Id+SyncToken in the body. This is NOT a `DELETE` HTTP method.
- **Void mechanism**: Uses `POST` with `?operation=void`. Only available on Invoice and Payment.

---

## API Versioning

- The API uses **minor versions** (currently up to 75 as seen in the API Explorer)
- Minor versions are specified via query parameter: `?minorversion=75`
- Minor versions are additive (backward compatible within the same major version)
- Some features require minimum minor versions (e.g., TaxCodeRef on Account requires minorversion=3, TxnLocationType requires minorversion=5)
