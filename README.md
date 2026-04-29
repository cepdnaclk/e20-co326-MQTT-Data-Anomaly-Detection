# CO326-Computer-Systems-Engineering-Industrial-Networks-Project

## Group Members

- `E/20/259` Munasinghe S
- `E/20/328` Rathnaweera R.V.C.
- `E/20/455` Dilshan W.M.N
- `E/20/456` Dulaj U.P.S.D.

## Project Overview

This project is an Industrial IoT and Digital Twin prototype for the CO326 course project. It simulates sensor data, performs lightweight anomaly detection, stores telemetry in a historian, and visualizes the system through a dashboard stack.

Current main services in the project:

- `publisher`: simulated sensor data generator
- `mqtt`: message broker
- `ai-brain`: lightweight ESP32-style anomaly detection simulation
- `backend`: real-time processing and API layer
- `influxdb`: historian
- `grafana`: visualization platform
- `frontend`: dashboard UI

## Documentation

- Architecture document: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Historian notes: [HISTORIAN_BRANCH_NOTES.md](HISTORIAN_BRANCH_NOTES.md)

## Main Ports

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:5000`
- AI Brain: `http://localhost:5001`
- InfluxDB: `http://localhost:8086`
- Grafana: `http://localhost:3000`
