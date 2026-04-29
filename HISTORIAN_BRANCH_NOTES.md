# Historian Branch Notes

Branch: `feature-influx-grafana-historian`

This branch develops one critical missing assignment area: the application-layer historian stack.

Implemented in this branch:

- Added `InfluxDB 2.7` to Docker Compose
- Added `Grafana 11` to Docker Compose
- Provisioned a default Grafana datasource pointing to InfluxDB
- Extended the backend to persist:
  - `temperature`
  - `humidity`
  - `anomaly`
  - `timestamp`
- Added backend endpoints:
  - `GET /health`
  - `GET /api/latest`

Current limitations:

- No prebuilt Grafana dashboard JSON yet
- No Node-RED integration yet
- No query API for historical trends yet
- No RUL calculation yet

Default local URLs:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:5000`
- InfluxDB: `http://localhost:8086`
- Grafana: `http://localhost:3000`

Default credentials:

- Grafana: `admin / admin12345`
- InfluxDB: `admin / admin12345`
