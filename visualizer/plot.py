#!/usr/bin/env python3
import json
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
DOCS_DIR = Path("docs")

def load_all_diagnostics():
    records = []

    for file in DATA_DIR.glob("*.json"):
        try:
            with open(file) as f:
                entry = json.load(f)
                timestamp = entry.get("timestamp")
                wifi = entry.get("wifi_info", {})
                ping = entry.get("ping_summary", "")
                record = {
                    "timestamp": timestamp,
                    "RSSI": int(wifi.get("agrCtlRSSI", -999)),
                    "Noise": int(wifi.get("agrCtlNoise", -999)),
                    "Channel": wifi.get("channel"),
                    "SSID": wifi.get("SSID"),
                    "ping_summary": ping
                }

                # Extract packet loss
                loss_line = [l for l in ping.split("\n") if "packet loss" in l]
                if loss_line:
                    try:
                        percent = loss_line[0].split(",")[2].strip().split("%")[0]
                        record["packet_loss_percent"] = float(percent)
                    except:
                        record["packet_loss_percent"] = None
                else:
                    record["packet_loss_percent"] = None

                records.append(record)
        except Exception as e:
            print(f"⚠️ Failed to parse {file.name}: {e}")
            continue

    return pd.DataFrame(records)

def plot_metric(df, y_col, title, out_file):
    if df.empty or y_col not in df.columns:
        print(f"⚠️ No data to plot for {y_col}")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    fig = px.line(df, x="timestamp", y=y_col, title=title, markers=True)
    fig.update_layout(xaxis_title="Time", yaxis_title=y_col)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    fig.write_html(DOCS_DIR / out_file)
    print(f"✅ Wrote {out_file}")

def main():
    df = load_all_diagnostics()

    plot_metric(df, "RSSI", "WiFi Signal Strength Over Time", "rssi_plot.html")
    plot_metric(df, "packet_loss_percent", "Packet Loss % Over Time", "packet_loss_plot.html")

if __name__ == "__main__":
    main()
