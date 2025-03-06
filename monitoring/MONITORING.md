# Monitoring Architecture Overview

## Core Technologies
- **Prometheus**: Metrics collection and alerting engine
- **Grafana**: Visualization and dashboarding platform
- **cAdvisor**: Container resource usage and performance monitoring
- **Node Exporter**: System metrics collection (CPU, memory, disk, network)
- **Postgres Exporter**: PostgreSQL metrics collection
### Prometheus
**Purpose**: Time-series database for metrics collection and alerting

**Features**:
- Pull-based metrics collection
- Flexible query language (PromQL)
- Alerting rules engine
- Service discovery

**Configuration**:
- 15-second scrape interval
- Configured targets:
  - Self-monitoring (prometheus:9090)
  - Node Exporter (node-exporter:9100)
  - cAdvisor (cadvisor:8080)
  - Postgres Exporter (postgres_exporter:9187)

### Grafana
**Purpose**: Visualization platform for metrics, logs, and alerts

**Features**:
- Interactive dashboards
- Rich visualization options
- Multi-data source support
- User authentication and authorization
- Alerting capabilities

**Configuration**:
- Secure credential management through HashiCorp Vault
### Dashboard Provisioning
**Auto-provisioned Dashboards**:
- System metrics dashboard
- PostgreSQL monitoring dashboard
- Container monitoring (cAdvisor) dashboard

**Configuration**:
- Dashboard auto-discovery from files
- 10-second update interval
- UI updates allowed
- Dashboard edits preserved

### Data Sources
**Prometheus Data Source**:
- Auto-configured as default data source
- Direct proxy access to Prometheus
- Editable by users

### cAdvisor
**Purpose**: Container resource usage monitoring

**Features**:
- CPU, memory, network, and file system usage per container
- Historical resource usage
- Container metadata collection

**Integration**:
- Metrics exposed on port 8080
- Scraped by Prometheus every 15 seconds
- Visualized through dedicated Grafana dashboard

### Node Exporter
**Purpose**: Host-level metrics collection

**Features**:
- CPU statistics
- Memory usage
- Disk I/O
- Network traffic
- System load

**Integration**:
- Metrics exposed on port 9100
- Scraped by Prometheus every 15 seconds
- Visualized in system dashboard

### Postgres Exporter
**Purpose**: PostgreSQL metrics collection

**Features**:
- Query statistics
- Connection metrics
- Transaction rates
- Table/index statistics

**Integration**:
## Security Implementation
### HashiCorp Vault Integration
**Credential Management**:
- Grafana admin credentials stored securely in Vault
- Credentials retrieved at container startup
- AppRole authentication with Vault

**Implementation Details**:
Credentials retrieved at container startup
AppRole authentication with Vault
Implementation Details:

```bash
# Authentication with Vault
VAULT_TOKEN=$(curl --request POST \
    --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
    $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)

# Retrieve Grafana credentials
export GF_SECURITY_ADMIN_USER=$(echo $VAULT_RESPONSE | jq -r .data.data.GF_SECURITY_ADMIN_USER)
export GF_SECURITY_ADMIN_PASSWORD=$(echo $VAULT_RESPONSE | jq -r .data.data.GF_SECURITY_ADMIN_PASSWORD)
```

Alerting Configuration
Alert Rules
CPU Usage:
```bash
- alert: HighCPUUsage
  expr: node_cpu_seconds_total{mode="idle"} < 20
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "High CPU usage detected"
    description: "CPU usage is above 80% for more than 1 minute."
```

### Alert Notifications
**Notification Channels**:
- Email alerts for critical issues
- Webhook integration for automated response
- On-screen notifications in Grafana UI

## Monitoring Coverage
### Application Monitoring
**Microservice Health**:
- Up/down status monitoring
- Response time tracking
- Error rate monitoring
- Request volume metrics

### Infrastructure Monitoring
**Container Health**:
- Resource usage per container
- Restart counts
- Network traffic between services

### Database Monitoring
**PostgreSQL Health**:
- Connection pool utilization
- Transaction rates
- Query performance
- Bloat and vacuum monitoring

## Deployment Configuration
### Container Setup
**Resource Allocation**:
- Prometheus: 2GB memory allocation
- Grafana: 1GB memory allocation

**Persistence**:
- Prometheus data stored in persistent volume
- Grafana configurations and dashboards preserved

### Network Configuration
**Exposed Ports**:
- Grafana UI: Port 3000
- Prometheus UI: Port 9090 (internal only)

**Inter-service Communication**:
- All monitoring components on dedicated monitoring network
- Direct service names used for communication

## Benefits
- Proactive Issue Detection: Alerts before problems affect users
- Performance Optimization: Identify bottlenecks and resource constraints
- Capacity Planning: Track resource usage trends over time
- Troubleshooting: Correlate metrics with application issues
- Transparency: Clear visibility into system health and behavior
This comprehensive monitoring architecture provides robust observability across all components of the Transcendence application, from infrastructure to application performance.

