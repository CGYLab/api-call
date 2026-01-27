"""HTTP client with automatic authentication and token refresh."""

import httpx
import base64
from typing import Optional, Any
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
import json

from .config import (
    BASE_URL,
    AUTH_MODE,
    API_KEY,
    API_KEY_HEADER,
    BASIC_AUTH_USERNAME,
    BASIC_AUTH_PASSWORD,
)
from .tokens import load_latest_token, is_token_expired, save_tokens

console = Console()


class ApiClient:
    """HTTP client with auto-auth and token refresh."""

    def __init__(self, use_auth: bool = True):
        self.base_url = BASE_URL
        self.use_auth = use_auth
        self.auth_mode = AUTH_MODE
        self.token_entry = None

        if use_auth and self.auth_mode == "jwt":
            self._load_token()

    def _load_token(self) -> None:
        """Load token from storage (JWT mode only)."""
        self.token_entry = load_latest_token()
        if not self.token_entry:
            console.print("[red]No token found. Please run api-login first.[/red]")
            raise SystemExit(1)

    def _get_headers(self) -> dict:
        """Get headers with auth based on configured mode."""
        headers = {"Content-Type": "application/json"}

        if not self.use_auth:
            return headers

        if self.auth_mode == "jwt":
            # JWT Bearer Token mode
            if not self.token_entry:
                self._load_token()

            # Check if token is expired and refresh if needed
            if is_token_expired(self.token_entry):
                self._refresh_token()

            headers["Authorization"] = f"Bearer {self.token_entry['access_token']}"

        elif self.auth_mode == "api-key":
            # API Key mode
            if not API_KEY:
                console.print("[red]API_KEY not configured in .env[/red]")
                raise SystemExit(1)
            headers[API_KEY_HEADER] = API_KEY

        elif self.auth_mode == "basic":
            # Basic Auth mode
            if not BASIC_AUTH_USERNAME or not BASIC_AUTH_PASSWORD:
                console.print("[red]BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD required in .env[/red]")
                raise SystemExit(1)
            credentials = f"{BASIC_AUTH_USERNAME}:{BASIC_AUTH_PASSWORD}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"

        elif self.auth_mode == "none":
            # No authentication
            pass

        else:
            console.print(f"[red]Unknown AUTH_MODE: {self.auth_mode}. Use: jwt, api-key, basic, or none[/red]")
            raise SystemExit(1)

        return headers

    def _refresh_token(self) -> None:
        """Refresh the access token using refresh token."""
        from .config import AUTH_REFRESH_ENDPOINT

        console.print("[yellow]Token expired. Refreshing...[/yellow]")

        if not self.token_entry or not self.token_entry.get("refresh_token"):
            console.print("[red]No refresh token available. Please login again.[/red]")
            raise SystemExit(1)

        try:
            response = httpx.post(
                f"{self.base_url}{AUTH_REFRESH_ENDPOINT}",
                json={"refreshToken": self.token_entry["refresh_token"]},
                timeout=30.0,
            )
            response.raise_for_status()
            response_data = response.json()

            # Extract token data from wrapped response
            data = response_data.get("data", response_data)
            access_token = data.get("accessToken") or data.get("access_token")
            refresh_token = data.get("refreshToken") or data.get("refresh_token", self.token_entry["refresh_token"])
            expires_in = data.get("expiresIn") or data.get("expires_in", 900)

            # Save new tokens
            save_tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                user_email=self.token_entry["user_email"],
                user_id=self.token_entry["user_id"],
            )

            # Reload token
            self._load_token()
            console.print("[green]Token refreshed successfully[/green]")

        except httpx.HTTPError as e:
            console.print(f"[red]Failed to refresh token: {e}[/red]")
            console.print("[yellow]Please login again with api-login[/yellow]")
            raise SystemExit(1)

    def get(self, endpoint: str, params: Optional[dict] = None) -> httpx.Response:
        """Make GET request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        response = httpx.get(url, headers=headers, params=params, timeout=30.0)
        return response

    def post(self, endpoint: str, data: Any) -> httpx.Response:
        """Make POST request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        response = httpx.post(url, headers=headers, json=data, timeout=30.0)
        return response

    def put(self, endpoint: str, data: Any) -> httpx.Response:
        """Make PUT request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        response = httpx.put(url, headers=headers, json=data, timeout=30.0)
        return response

    def delete(self, endpoint: str) -> httpx.Response:
        """Make DELETE request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        response = httpx.delete(url, headers=headers, timeout=30.0)
        return response


def print_response(
    response: httpx.Response,
    show_headers: bool = False,
    verbose: bool = False,
    raw: bool = False
) -> None:
    """Pretty print HTTP response."""
    # If raw mode, just output the JSON without formatting
    if raw:
        try:
            json_data = response.json()
            print(json.dumps(json_data, indent=2))
        except json.JSONDecodeError:
            print(response.text)
        return

    # Status
    status_color = "green" if 200 <= response.status_code < 300 else "red"
    console.print(f"\n[{status_color}]Status: {response.status_code}[/{status_color}]")

    # Headers
    if show_headers or verbose:
        console.print("\n[bold]Headers:[/bold]")
        for key, value in response.headers.items():
            console.print(f"  {key}: {value}")

    # Body
    console.print("\n[bold]Response:[/bold]")
    try:
        json_data = response.json()

        # Check for URL fields and print them separately to avoid truncation
        url_fields = ['url', 'authUrl', 'auth_url', 'redirectUrl', 'redirect_url', 'callbackUrl', 'callback_url']
        has_url = False

        # Check nested data object first
        data = json_data.get('data', {})
        for field in url_fields:
            if isinstance(data, dict) and field in data:
                console.print(f"\n[bold cyan]{field}:[/bold cyan]")
                console.print(f"[green]{data[field]}[/green]", soft_wrap=False, no_wrap=True)
                has_url = True

        # Check top-level fields
        for field in url_fields:
            if field in json_data and not has_url:
                console.print(f"\n[bold cyan]{field}:[/bold cyan]")
                console.print(f"[green]{json_data[field]}[/green]", soft_wrap=False, no_wrap=True)
                has_url = True

        if has_url:
            console.print("\n[bold]Full Response:[/bold]")

        # Print full JSON with wide width to prevent truncation
        json_str = json.dumps(json_data, indent=2)
        # Create console with very wide width to prevent URL truncation
        wide_console = Console(width=500)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        wide_console.print(Panel(syntax, border_style="blue"))
    except json.JSONDecodeError:
        console.print(response.text)

    # Request details in verbose mode
    if verbose:
        console.print("\n[bold]Request:[/bold]")
        console.print(f"  Method: {response.request.method}")
        console.print(f"  URL: {response.request.url}")
