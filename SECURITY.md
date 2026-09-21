# Security Policy

## Reporting Vulnerabilities

Status: Undecided - No dedicated security contact established yet.

For security concerns, please:
- Do not open public issues
- Contact the repository owner privately
- Provide detailed description of the vulnerability
- Include steps to reproduce if applicable

## Security Guidelines

### Secrets and Credentials

- **No secrets in Git** - Never commit passwords, API keys, or tokens
- **No credentials in source code** - Use environment variables or secure configuration
- **Production secrets must be externalized** - Use Frappe site configuration or secret management
- **API credentials must not be committed** - Use environment-specific configuration
- **Database backups containing sensitive data must not be committed** - Store securely

### Code Security

- Validate all user inputs
- Use Frappe's built-in security features
- Follow OWASP guidelines for web applications
- Keep dependencies updated
- Review dependencies for known vulnerabilities

### Access Control

- Use Frappe roles and permissions
- Implement principle of least privilege
- Audit access to sensitive operations
- Log security-relevant events

## Supported Versions

- WMS 0.0.x: Development phase - No security support guarantees yet
- Future versions: Security support policy to be defined

## Security Updates

Security updates will be:
- Documented in CHANGELOG.md
- Released as patches when applicable
- Communicated via release notes
