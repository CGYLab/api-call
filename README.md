# api-call

CLI tool for REST API testing with JWT, API key, and basic auth support.

## Features

- Multiple authentication modes (JWT, API key, basic auth, none)
- Auto token refresh for JWT authentication
- Per-project configuration (`.claude/api-testing/.env`)
- Clean JSON output with `-r` flag
- Works seamlessly with AI coding assistants

## Installation

```bash
# Using uvx (recommended, no install needed)
uvx api-call status

# Using pip
pip install api-call

# Using uv
uv tool install api-call
```

## Quick Start

1. Run any command to auto-create config:

```bash
uvx api-call status
```

2. Edit `.claude/api-testing/.env` with your settings:

```env
PORT=3000
AUTH_MODE=jwt

# For JWT mode
API_TEST_EMAIL=user@example.com
API_TEST_PASSWORD=yourpassword
```

3. Login (JWT mode):

```bash
uvx api-call login
```

4. Make requests:

```bash
uvx api-call get /users -r
uvx api-call post /users -d '{"name":"John","email":"john@example.com"}' -r
uvx api-call put /users/1 -d '{"name":"Jane"}' -r
uvx api-call delete /users/1 -y
```

## Commands

```bash
uvx api-call --help
```

| Command | Description |
|---------|-------------|
| `get` | Make GET requests |
| `post` | Make POST requests |
| `put` | Make PUT requests |
| `delete` | Make DELETE requests |
| `login` | Login and save JWT tokens |
| `refresh` | Manually refresh JWT token |
| `status` | Show config and token status |

## Options

All request commands support:

| Option | Description |
|--------|-------------|
| `-r, --raw` | Output raw JSON (for piping/parsing) |
| `-H, --headers` | Show response headers |
| `-v, --verbose` | Verbose output |
| `--no-auth` | Skip authentication |

POST/PUT specific:

| Option | Description |
|--------|-------------|
| `-d, --data` | JSON data string |
| `-f, --file` | JSON file path |

DELETE specific:

| Option | Description |
|--------|-------------|
| `-y, --yes` | Skip confirmation prompt |

GET specific:

| Option | Description |
|--------|-------------|
| `-q, --query` | Query params (e.g., "page=1&limit=10") |

## Authentication Modes

### JWT Mode (default)

```env
AUTH_MODE=jwt
API_TEST_EMAIL=user@example.com
API_TEST_PASSWORD=yourpassword
AUTH_LOGIN_ENDPOINT=/auth/login
AUTH_REFRESH_ENDPOINT=/auth/refresh
```

### API Key Mode

```env
AUTH_MODE=api-key
API_KEY=your-api-key-here
API_KEY_HEADER=X-API-Key
```

### Basic Auth Mode

```env
AUTH_MODE=basic
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=password
```

### No Auth

```env
AUTH_MODE=none
```

## Configuration

Config is stored in `.claude/api-testing/` in your current working directory:

```
.claude/api-testing/
├── .env          # Your configuration
├── .gitignore    # Prevents committing secrets
└── tokens.jsonl  # JWT tokens (auto-generated)
```

## License

BSD-3-Clause
