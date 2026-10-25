# Cloud Security Automation

Hands-on Azure cloud security automation labs, including source code, reproducible setup, monitoring queries, and real troubleshooting notes.

## Projects

| Project | Focus | Status |
|---|---|---|
| [Azure Key Vault Secret Rotation](azure-keyvault-secret-rotation/) | Key Vault, Azure Functions, managed identity, Event Grid, RBAC | HTTP rotation verified; Event Grid handler invocation observed; actual near-expiry delivery not independently verified |

> **Security note:** Labs are educational examples, not production-ready credential rotation services. Never commit keys, connection strings, `.env`, `local.settings.json`, secret values, or unsanitized logs/screenshots.
