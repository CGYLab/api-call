#!/usr/bin/env python3
"""API Call - CLI tool for REST API testing."""

import json
import typer
from rich.console import Console
from typing import Optional
from pathlib import Path
import httpx

from .config import (
    require_setup,
    CONFIG_DIR,
    AUTH_MODE,
    BASE_URL,
    DEFAULT_EMAIL,
    DEFAULT_PASSWORD,
    AUTH_LOGIN_ENDPOINT,
    AUTH_REFRESH_ENDPOINT,
)
from .client import ApiClient, print_response
from .tokens import save_tokens, load_latest_token, is_token_expired

app = typer.Typer(
    name="cc-api-call",
    help="CLI tool for REST API testing with JWT, API key, and basic auth support.",
    add_completion=False,
)
console = Console()


def parse_query_params(query_string: Optional[str]) -> Optional[dict]:
    """Parse query string into dict."""
    if not query_string:
        return None
    params = {}
    for pair in query_string.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value
    return params


@app.command()
def get(
    endpoint: str = typer.Argument(..., help="API endpoint (e.g., /users)"),
    query: Optional[str] = typer.Option(None, "-q", "--query", help='Query params (e.g., "page=1&limit=10")'),
    no_auth: bool = typer.Option(False, "--no-auth", help="Skip authentication"),
    show_headers: bool = typer.Option(False, "-H", "--headers", help="Show response headers"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
    raw: bool = typer.Option(False, "-r", "--raw", help="Raw JSON output"),
):
    """Make GET request to API endpoint."""
    require_setup()
    try:
        client = ApiClient(use_auth=not no_auth)
        params = parse_query_params(query)

        console.print(f"[cyan]GET {endpoint}[/cyan]")
        if params:
            console.print(f"[cyan]Query: {params}[/cyan]")

        response = client.get(endpoint, params=params)
        print_response(response, show_headers=show_headers, verbose=verbose, raw=raw)

        if response.status_code >= 400:
            raise typer.Exit(1)

    except httpx.HTTPError as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise typer.Exit(1)
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def post(
    endpoint: str = typer.Argument(..., help="API endpoint (e.g., /users)"),
    data: Optional[str] = typer.Option(None, "-d", "--data", help="JSON data string"),
    file: Optional[Path] = typer.Option(None, "-f", "--file", help="JSON file path"),
    no_auth: bool = typer.Option(False, "--no-auth", help="Skip authentication"),
    show_headers: bool = typer.Option(False, "-H", "--headers", help="Show response headers"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
    raw: bool = typer.Option(False, "-r", "--raw", help="Raw JSON output"),
):
    """Make POST request to API endpoint."""
    require_setup()
    try:
        json_data = None
        if data:
            json_data = json.loads(data)
        elif file:
            if not file.exists():
                console.print(f"[red]File not found: {file}[/red]")
                raise typer.Exit(1)
            with open(file, "r") as f:
                json_data = json.load(f)
        else:
            console.print("[red]Either -d/--data or -f/--file is required[/red]")
            raise typer.Exit(1)

        client = ApiClient(use_auth=not no_auth)

        console.print(f"[cyan]POST {endpoint}[/cyan]")
        if verbose:
            console.print(f"[cyan]Data: {json.dumps(json_data, indent=2)}[/cyan]")

        response = client.post(endpoint, data=json_data)
        print_response(response, show_headers=show_headers, verbose=verbose, raw=raw)

        if response.status_code >= 400:
            raise typer.Exit(1)

    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
    except httpx.HTTPError as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise typer.Exit(1)
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def put(
    endpoint: str = typer.Argument(..., help="API endpoint (e.g., /users/123)"),
    data: Optional[str] = typer.Option(None, "-d", "--data", help="JSON data string"),
    file: Optional[Path] = typer.Option(None, "-f", "--file", help="JSON file path"),
    no_auth: bool = typer.Option(False, "--no-auth", help="Skip authentication"),
    show_headers: bool = typer.Option(False, "-H", "--headers", help="Show response headers"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
    raw: bool = typer.Option(False, "-r", "--raw", help="Raw JSON output"),
):
    """Make PUT request to API endpoint."""
    require_setup()
    try:
        json_data = None
        if data:
            json_data = json.loads(data)
        elif file:
            if not file.exists():
                console.print(f"[red]File not found: {file}[/red]")
                raise typer.Exit(1)
            with open(file, "r") as f:
                json_data = json.load(f)
        else:
            console.print("[red]Either -d/--data or -f/--file is required[/red]")
            raise typer.Exit(1)

        client = ApiClient(use_auth=not no_auth)

        console.print(f"[cyan]PUT {endpoint}[/cyan]")
        if verbose:
            console.print(f"[cyan]Data: {json.dumps(json_data, indent=2)}[/cyan]")

        response = client.put(endpoint, data=json_data)
        print_response(response, show_headers=show_headers, verbose=verbose, raw=raw)

        if response.status_code >= 400:
            raise typer.Exit(1)

    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
    except httpx.HTTPError as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise typer.Exit(1)
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete(
    endpoint: str = typer.Argument(..., help="API endpoint (e.g., /users/123)"),
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation"),
    no_auth: bool = typer.Option(False, "--no-auth", help="Skip authentication"),
    show_headers: bool = typer.Option(False, "-H", "--headers", help="Show response headers"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
    raw: bool = typer.Option(False, "-r", "--raw", help="Raw JSON output"),
):
    """Make DELETE request to API endpoint."""
    require_setup()
    try:
        if not yes:
            confirm = typer.confirm(f"Delete {endpoint}?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client = ApiClient(use_auth=not no_auth)

        console.print(f"[cyan]DELETE {endpoint}[/cyan]")

        response = client.delete(endpoint)
        print_response(response, show_headers=show_headers, verbose=verbose, raw=raw)

        if response.status_code >= 400:
            raise typer.Exit(1)

    except httpx.HTTPError as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise typer.Exit(1)
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def login(
    email: Optional[str] = typer.Option(None, "-e", "--email", help="User email"),
    password: Optional[str] = typer.Option(None, "-p", "--password", help="User password"),
):
    """Login and save JWT tokens."""
    require_setup()
    if AUTH_MODE != "jwt":
        console.print(f"[yellow]Login only available in JWT mode. Current: {AUTH_MODE}[/yellow]")
        raise typer.Exit(1)

    email = email or DEFAULT_EMAIL
    password = password or DEFAULT_PASSWORD

    if not email or not password:
        console.print("[red]Credentials required. Use -e/-p or set in .env[/red]")
        raise typer.Exit(1)

    try:
        console.print(f"[cyan]Logging in as {email}...[/cyan]")

        response = httpx.post(
            f"{BASE_URL}{AUTH_LOGIN_ENDPOINT}",
            json={"email": email, "password": password},
            timeout=30.0,
        )
        response.raise_for_status()
        response_data = response.json()

        data = response_data.get("data", response_data)
        access_token = data.get("accessToken") or data.get("access_token")
        refresh_token = data.get("refreshToken") or data.get("refresh_token")
        expires_in = data.get("expiresIn") or data.get("expires_in", 900)
        user = data.get("user", {})
        user_email = user.get("email", email)
        user_id = str(user.get("id", ""))

        if not access_token or not refresh_token:
            console.print("[red]Invalid response: missing tokens[/red]")
            raise typer.Exit(1)

        save_tokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            user_email=user_email,
            user_id=user_id,
        )

        console.print(f"[green]Login successful[/green]")
        console.print(f"[green]User: {user_email} (ID: {user_id})[/green]")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Login failed: {e.response.status_code}[/red]")
        raise typer.Exit(1)
    except httpx.HTTPError as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def refresh(
    force: bool = typer.Option(False, "--force", help="Force refresh"),
):
    """Refresh JWT token."""
    require_setup()
    if AUTH_MODE != "jwt":
        console.print(f"[yellow]Refresh only available in JWT mode.[/yellow]")
        raise typer.Exit(1)

    entry = load_latest_token()
    if not entry:
        console.print("[red]No token found. Run login first.[/red]")
        raise typer.Exit(1)

    if not force and not is_token_expired(entry):
        console.print("[green]Token still valid. Use --force to refresh.[/green]")
        return

    refresh_token = entry.get("refresh_token")
    if not refresh_token:
        console.print("[red]No refresh token. Login again.[/red]")
        raise typer.Exit(1)

    try:
        console.print("[cyan]Refreshing token...[/cyan]")

        response = httpx.post(
            f"{BASE_URL}{AUTH_REFRESH_ENDPOINT}",
            json={"refreshToken": refresh_token},
            timeout=30.0,
        )
        response.raise_for_status()
        response_data = response.json()

        data = response_data.get("data", response_data)
        access_token = data.get("accessToken") or data.get("access_token")
        new_refresh_token = data.get("refreshToken") or data.get("refresh_token", refresh_token)
        expires_in = data.get("expiresIn") or data.get("expires_in", 900)

        save_tokens(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=expires_in,
            user_email=entry["user_email"],
            user_id=entry["user_id"],
        )

        console.print(f"[green]Token refreshed[/green]")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Refresh failed: {e.response.status_code}[/red]")
        raise typer.Exit(1)
    except httpx.HTTPError as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status():
    """Show configuration and token status."""
    require_setup()
    console.print("[bold cyan]API Call Status[/bold cyan]")
    console.print("=" * 40)

    console.print(f"\n[bold]Configuration:[/bold]")
    console.print(f"  Config dir: {CONFIG_DIR}")
    console.print(f"  Base URL:   {BASE_URL}")
    console.print(f"  Auth mode:  {AUTH_MODE}")

    if AUTH_MODE == "jwt":
        console.print(f"\n[bold]Token Status:[/bold]")
        entry = load_latest_token()
        if not entry:
            console.print("  [yellow]No token. Run: cc-api-call login[/yellow]")
        else:
            console.print(f"  User:    {entry['user_email']}")
            console.print(f"  Expires: {entry['expires_at']}")
            if is_token_expired(entry):
                console.print("  [yellow]Status: EXPIRED[/yellow]")
            else:
                console.print("  [green]Status: VALID[/green]")


if __name__ == "__main__":
    app()
