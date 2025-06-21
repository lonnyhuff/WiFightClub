# 🛰️ WiFightClub

**WiFightClub** is a lightweight, mildly sarcastic diagnostics logger that gathers Wi-Fi metrics and stores them in JSON logs and interactive dashboards.

---

## 🧩 What It Does

This tool periodically collects a snapshot of local Wi-Fi and network conditions and saves it to disk. Over time, it builds a time-series dataset that can be visualized to show:

- Wi-Fi signal strength (RSSI)
- Packet loss %
- Average latency to 8.8.8.8
- Transmit rate (Mbps)
- Noise level (dBm)
- Disconnect/system log events (macOS only, optional)

### Sample Architecture

```
                        +-------------------+
                        |   cron / loop     |
                        +--------+----------+
                                 |
                      +----------v-----------+
                      |   collect.py         |
                      |----------------------|
                      | - grabs WiFi stats   |
                      | - runs ping          |
                      | - saves JSON logs    |
                      +----------+-----------+
                                 |
                                 v
                   +-------------+-------------+
                   |      data/log_*.json      |
                   +-------------+-------------+
                                 |
                                 v
             +------------------+------------------+
             |     visualizer/plot.py             |
             |  - parses logs                     |
             |  - creates plotly HTML dashboards  |
             +------------------+------------------+
                                 |
                                 v
                     +-----------+-----------+
                     |       docs/*.html     |
                     |  (RSSI, Latency, etc) |
                     +-----------------------+
```

---

## 🛠️ What It Collects

### 📶 `wifi_stats`  
Gathered via `wdutil info` (on macOS), parsed using regex.

- `ssid` – network name
- `rssi` – signal strength in dBm (e.g. -60)
- `tx_rate` – theoretical max transmit rate (Mbps)
- `noise` – ambient Wi-Fi noise in dBm
- `channel` – the frequency and bandwidth used

### 🌐 `ping_stats`  
Runs `ping -c 100 -i 0.1 8.8.8.8` and parses summary.

- `packet_loss_percent` – % of dropped packets
- `avg_latency_ms` – average ping latency (ms)


---


## 🔁 Continuous Monitoring

To run this automatically every 5 minutes:

```bash
python3 monitor/run_monitor.py
```

This will:
- Collect fresh diagnostics
- Archive logs older than 7 days
- Re-generate all plots
- (Optionally) push updates to GitHub

Make sure `.env` is set up with:
```env
REPO_URL=git@github.com:your/repo.git
GITHUB_PAT=ghp_yourTokenHere
```

---

## 📦 Archiving Data

Logs are saved in `data/` and rotated to `archive/` based on retention rules. To archive manually:

```bash
zip archive/test_data_2025-06-21.zip data/log_*.json
rm data/log_*.json
```

You can copy that ZIP to a new host and let it continue collecting.

---

## 🧼 Resetting

Need to reset plots or start fresh?

```bash
rm data/*.json
rm docs/*.html
python3 visualizer/plot.py
```

---

## 👀 Sample Output (log)

```json
{
  "timestamp": "2025-06-21T19:18:52.711365",
  "wifi_stats": {
    "ssid": "SomeNetwork",
    "rssi": -57,
    "tx_rate": 286.0,
    "noise": -96,
    "channel": "5g36/20"
  },
  "ping_stats": {
    "packet_loss_percent": 0.0,
    "avg_latency_ms": 6.41
  }
}
```

