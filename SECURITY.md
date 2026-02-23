# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Edict Guardian seriously. If you have discovered a security vulnerability, please report it responsibly.

### What to Include

Please include the following information:

- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Potential impact** of the vulnerability
- **Possible mitigations** (if any)
- **Your contact information** for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours
- **Triage**: Within 7 days
- **Fix Development**: Depends on severity
- **Disclosure**: After fix is released

### Disclosure Policy

- We follow responsible disclosure practices
- Security fixes are released as soon as possible
- CVEs are assigned for significant vulnerabilities
- Public disclosure occurs after users have had time to update

## Security Best Practices

### For Developers

1. **Never commit secrets**
   - Use `.env` files (already in `.gitignore`)
   - Use environment variables for sensitive data
   - Never hardcode API keys, passwords, or tokens

2. **Dependencies**
   - Keep dependencies updated
   - Review security advisories for dependencies
   - Use `pip-audit` to check for vulnerabilities

3. **Code Review**
   - All code changes require review
   - Security-sensitive changes require additional review
   - Use pre-commit hooks for automated checks

4. **Authentication & Authorization**
   - Use strong password hashing (bcrypt)
   - Implement proper session management
   - Validate all user inputs

### For Deployment

1. **Environment Configuration**
   - Use secure, random secret keys
   - Enable HTTPS everywhere
   - Configure proper CORS settings

2. **Database Security**
   - Use strong database passwords
   - Limit database user permissions
   - Enable SSL for database connections

3. **API Security**
   - Implement rate limiting
   - Use API keys for external access
   - Log and monitor API access

4. **Infrastructure**
   - Keep servers updated
   - Use firewall rules
   - Enable logging and monitoring

## Security Features

### Current Implementation

- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Password Hashing**: bcrypt for password storage
- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Configurable allowed origins
- **Rate Limiting**: (Planned)