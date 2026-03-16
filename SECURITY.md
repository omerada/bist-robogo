# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email your findings to the maintainers (see the repository's "About" section for contact info)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge your report within **48 hours** and aim to release a patch within **7 days** for critical issues.

## Security Considerations

### Credentials & Secrets

- **Never** commit real credentials, API keys, or secrets to the repository
- Use the `.env` file for local secrets (excluded via `.gitignore`)
- The `docker-compose.yml` contains **development-only** placeholder credentials — these must be changed for any non-local deployment
- All sensitive config values use Pydantic `SecretStr` to prevent accidental logging

### Authentication

- JWT-based authentication with configurable expiry
- Passwords hashed with bcrypt
- CORS origins strictly configured

### Data

- All database queries use parameterized statements via SQLAlchemy ORM
- Input validation enforced through Pydantic schemas
- Rate limiting on API endpoints

## Best Practices for Contributors

- Never hardcode secrets in source code
- Use environment variables for all sensitive configuration
- Keep dependencies up to date (`poetry update`, `pnpm update`)
- Run `ruff check` and type checking before submitting PRs
