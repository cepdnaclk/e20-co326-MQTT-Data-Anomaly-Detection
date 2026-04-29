---
layout: home
permalink: index.html
repository-name: CO326-Computer-Systems-Engineering-Industrial-Networks-Project
title: Industrial Digital Twin and Cyber-Physical Security
---

# Industrial Digital Twin and Cyber-Physical Security

Software-only edge-to-cloud Industrial IoT integration project for **CO326 Computer Systems Engineering - Industrial Networks**.

---

## Team

- `E/20/259` Munasinghe S
- `E/20/328` Rathnaweera R.V.C.
- `E/20/455` Dilshan W.M.N
- `E/20/456` Dulaj U.P.S.D.

## Table of Contents

1. [Introduction](#introduction)
2. [Project Scope](#project-scope)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [How the Pipeline Works](#how-the-pipeline-works)
6. [Main Topics and Services](#main-topics-and-services)
7. [Project Links](#project-links)

---

## Introduction

This project implements a **simulated industrial digital twin** for **Motor-01 overheating monitoring with relay trip simulation**. The system models one main process variable, `Motor/WindingTemperature`, and one actuator, a protective relay that can be controlled in `AUTO`, `TRIP`, and `RESET` modes.

The objective is to demonstrate a realistic Industrial IoT pipeline using a software-only setup that still follows the required edge-to-cloud architecture:

- simulated sensor and actuator behavior
- MQTT-based industrial messaging
- Sparkplug-style edge topic structure
- Unified Namespace telemetry flow
- lightweight edge-style anomaly scoring
- historian storage
- Grafana visualization
- dashboard-to-actuator control loop

## Project Scope

The project is centered on a single industrial use case:

- **Asset**: `Motor-01`
- **Sensor**: simulated winding temperature
- **Actuator**: simulated protective relay
- **Main problem**: detect abnormal motor overheating and respond through protection logic and operator control

This is a **software simulation**, not a hardware deployment. The edge device behavior and lightweight ML runtime are designed to represent an ESP32-class constrained environment using container resource limits and simple inference logic.

## System Architecture

The pipeline consists of these major components:

1. `publisher`
   Generates simulated motor temperature data and relay feedback state.
2. `mqtt`
   Carries Sparkplug-style telemetry and relay command messages.
3. `node-red`
   Bridges Sparkplug device data into a Unified Namespace and applies orchestration logic.
4. `ai-brain`
   Runs a lightweight anomaly-scoring model using statistical thresholding.
5. `backend`
   Consumes telemetry, calls the ML service, estimates Remaining Useful Life (RUL), writes historian records, and exposes APIs for the dashboard.
6. `influxdb`
   Stores time-series telemetry and derived analytics.
7. `grafana`
   Visualizes temperature, anomaly score, RUL, and other historian data.
8. `frontend`
   Shows live digital twin state and allows relay commands.

For the detailed architecture diagrams and data-flow sequence, see [docs/ARCHITECTURE.md](../ARCHITECTURE.md).

## Technology Stack

- **Messaging**: MQTT
- **Flow orchestration**: Node-RED
- **Historian**: InfluxDB
- **Visualization**: Grafana
- **Live dashboard**: React frontend
- **Backend**: Node.js + Express + Socket.IO
- **Edge ML simulation**: Flask + lightweight statistical model
- **Deployment**: Docker Compose

## How the Pipeline Works

1. The simulated publisher generates Motor-01 temperature and relay-state telemetry.
2. Telemetry is published on a Sparkplug-style MQTT topic.
3. Node-RED transforms and republishes the data into a Unified Namespace topic.
4. The backend subscribes to the UNS telemetry stream.
5. The backend sends `motorTemperatureC` to the lightweight ML service for anomaly scoring.
6. The backend estimates RUL from temperature trend, anomaly score, and relay state.
7. Processed records are stored in InfluxDB.
8. Grafana reads historian data for trend visualization.
9. The frontend shows live state and sends operator relay commands back through the backend and MQTT.

## Main Topics and Services

### MQTT Topics

- Sparkplug telemetry: `spBv1.0/CO326/DDATA/Plant1.Line1.MotorCell/Motor01`
- Sparkplug relay command: `spBv1.0/CO326/DCMD/Plant1.Line1.MotorCell/Motor01`
- UNS telemetry: `uns/CO326/Plant1/Line1/MotorCell/Motor01/telemetry`

### Local Service Ports

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:5000`
- AI Brain: `http://localhost:5001`
- Node-RED: `http://localhost:1880`
- InfluxDB: `http://localhost:8086`
- Grafana: `http://localhost:3000`

## Project Links

- [Project Repository](https://github.com/cepdnaclk/{{ page.repository-name }}){:target="_blank"}
- [Project Page](https://cepdnaclk.github.io/{{ page.repository-name }}){:target="_blank"}
- [Architecture Document](../ARCHITECTURE.md)
- [Department of Computer Engineering](http://www.ce.pdn.ac.lk/)
- [University of Peradeniya](https://eng.pdn.ac.lk/)
