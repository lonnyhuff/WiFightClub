# WiFightClub

> Diagnose and document sketchy WeWork WiFi like a pro.

This tool collects local WiFi and network telemetry, performs basic diagnostics (e.g. signal strength, ping tests, disconnect logs), and pushes structured data to a central GitHub repo for visualization.

## Features
- WiFi metadata: SSID, BSSID, RSSI, channel, noise
- Ping tests to external servers
- Disconnect event logging
- JSON-based telemetry log
- GitHub sync with PAT
- Visualizations (basic CLI + web-based)

## Getting Started

```bash
pip install -r requirements.txt
python collector/collect.py
