"""QuickBooks OAuth2 client wrapper with token persistence."""

import os
import sys
import threading
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks

from db import init_db, save_tokens, load_tokens

load_dotenv()

CLIENT_ID = os.getenv("QUICKBOOKS_CLIENT_ID")
CLIENT_SECRET = os.getenv("QUICKBOOKS_CLIENT_SECRET")
REALM_ID = os.getenv("QUICKBOOKS_REALM_ID")
REDIRECT_URI = os.getenv("QUICKBOOKS_REDIRECT_URI", "http://localhost:8099/callback")
ENVIRONMENT = os.getenv("QUICKBOOKS_ENVIRONMENT", "sandbox")

# Parse port from redirect URI
_parsed = urlparse(REDIRECT_URI)
OAUTH_PORT = _parsed.port or 8099


def _log(msg: str):
    """Log to stderr only (stdout is reserved for MCP stdio transport)."""
    print(msg, file=sys.stderr)


class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler that captures the OAuth callback."""

    auth_code = None
    realm_id = None

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/callback" and "code" in params:
            _OAuthCallbackHandler.auth_code = params["code"][0]
            _OAuthCallbackHandler.realm_id = params.get("realmId", [REALM_ID])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h2>Authorization successful!</h2>"
                b"<p>You can close this tab and return to Claude Code.</p>"
                b"</body></html>"
            )
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed.")

    def log_message(self, format, *args):
        """Suppress default logging to stdout."""
        _log(f"OAuth server: {format % args}")


def _do_oauth_flow(auth_client: AuthClient) -> tuple[str, str]:
    """Run interactive OAuth flow. Opens browser, waits for callback.

    Returns (auth_code, realm_id).
    """
    auth_url = auth_client.get_authorization_url(
        [Scopes.ACCOUNTING], state_token="quickbooks-mcp"
    )

    _log(f"\nOpening browser for QuickBooks authorization...")
    _log(f"If the browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", OAUTH_PORT), _OAuthCallbackHandler)
    _log(f"Waiting for OAuth callback on port {OAUTH_PORT}...")

    # Wait for one request
    server.handle_request()
    server.server_close()

    if not _OAuthCallbackHandler.auth_code:
        raise RuntimeError("OAuth callback did not receive an authorization code")

    return _OAuthCallbackHandler.auth_code, _OAuthCallbackHandler.realm_id


def _create_auth_client() -> AuthClient:
    return AuthClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        environment=ENVIRONMENT,
    )


def get_client() -> QuickBooks:
    """Get an authenticated QuickBooks client.

    1. Try loading stored tokens from SQLite
    2. If access token is expired, refresh it
    3. If no tokens exist, run interactive OAuth flow
    """
    init_db()
    auth_client = _create_auth_client()
    tokens = load_tokens()

    if tokens:
        # We have stored tokens — check if access token is still valid
        access_expiry = datetime.fromisoformat(tokens["access_token_expiry"])
        now = datetime.now(timezone.utc)

        if now < access_expiry - timedelta(minutes=5):
            # Access token is still valid
            auth_client.access_token = tokens["access_token"]
            auth_client.refresh_token = tokens["refresh_token"]
            realm_id = tokens["realm_id"]
            _log("Using stored access token (still valid)")
        else:
            # Access token expired — try refresh
            _log("Access token expired, refreshing...")
            auth_client.refresh_token = tokens["refresh_token"]
            try:
                auth_client.refresh()
                realm_id = tokens["realm_id"]

                # Save refreshed tokens
                now_utc = datetime.now(timezone.utc)
                save_tokens(
                    access_token=auth_client.access_token,
                    refresh_token=auth_client.refresh_token,
                    realm_id=realm_id,
                    access_token_expiry=(now_utc + timedelta(hours=1)).isoformat(),
                    refresh_token_expiry=(now_utc + timedelta(days=100)).isoformat(),
                )
                _log("Token refreshed successfully")
            except Exception as e:
                _log(f"Token refresh failed ({e}), starting new OAuth flow...")
                tokens = None

    if not tokens:
        # No valid tokens — run OAuth flow
        auth_code, realm_id = _do_oauth_flow(auth_client)

        # Exchange code for tokens
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)

        now_utc = datetime.now(timezone.utc)
        save_tokens(
            access_token=auth_client.access_token,
            refresh_token=auth_client.refresh_token,
            realm_id=realm_id,
            access_token_expiry=(now_utc + timedelta(hours=1)).isoformat(),
            refresh_token_expiry=(now_utc + timedelta(days=100)).isoformat(),
        )
        _log("OAuth flow complete, tokens saved")

    client = QuickBooks(
        auth_client=auth_client,
        refresh_token=auth_client.refresh_token,
        company_id=realm_id,
        minorversion=75,
    )

    return client


if __name__ == "__main__":
    _log("Testing QuickBooks client connection...")
    client = get_client()
    from quickbooks.objects.company_info import CompanyInfo

    info = CompanyInfo.all(qb=client)
    if info:
        _log(f"Connected to: {info[0].CompanyName}")
        _log(f"Realm ID: {client.company_id}")
    else:
        _log("Connected but could not fetch company info")
