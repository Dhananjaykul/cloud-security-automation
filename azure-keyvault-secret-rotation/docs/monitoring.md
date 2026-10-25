# Monitoring and Log Queries

## Azure Portal navigation

| Question | Where to go |
|---|---|
| Did the Function run? | Function App → Functions → `rotate_secret_on_expiry` → Invocations |
| What exception occurred? | Application Insights → Logs / Failures |
| What did Python log? | Function App → Monitoring → Log stream, or Application Insights → Logs |
| Was Event Grid delivering events? | Event Grid System Topic → Metrics |
| Was a new Key Vault version created? | Key Vault → Secrets → `SecureMart-App-Credential` → Versions |
| Where are workspace-based traces stored? | Application Insights → Properties → linked Log Analytics Workspace |
| Are Key Vault data-plane audit logs routed? | Key Vault → Diagnostic settings → destination workspace |

> **Important:** A Log Analytics Workspace existing does not automatically mean Key Vault audit logs are being sent to it. Configure Key Vault diagnostic settings separately. A direct invocation of the Function also does not prove Event Grid delivery.

## Application Insights Logs (application-scoped table names)

```kusto
traces
| where timestamp > ago(24h)
| where message contains "Rotation" or message contains "Near-expiry"
| project timestamp, severityLevel, message
| order by timestamp desc
```

```kusto
exceptions
| where timestamp > ago(24h)
| project timestamp, type, outerMessage
| order by timestamp desc
```

## Log Analytics Workspace (workspace table names)

```kusto
AppTraces
| where TimeGenerated > ago(24h)
| where Message contains "Rotation" or Message contains "Near-expiry"
| project TimeGenerated, SeverityLevel, Message
| order by TimeGenerated desc
```

```kusto
AppExceptions
| where TimeGenerated > ago(24h)
| project TimeGenerated, ExceptionType, OuterMessage
| order by TimeGenerated desc
```

If Function App resource logs are separately routed using diagnostic settings, `FunctionAppLogs` may be available. If Key Vault audit logs are routed using resource-specific tables, `AZKVAuditLogs` may be available; depending on diagnostic configuration, legacy `AzureDiagnostics` may instead be used. Check available tables before writing a dashboard.

## Validation checklist

1. Open the Function's Invocations page; find the expected timestamp and outcome.
2. Open logs and confirm `Received Key Vault Event Grid event` and `Event Grid rotation completed` (or inspect the exception).
3. Confirm the new secret version in Key Vault without viewing or copying its value.
4. For actual Event Grid delivery, inspect system topic metrics and the subscription's delivery status.
5. Record timestamps in UTC and correlate with Function invocation IDs where available.
