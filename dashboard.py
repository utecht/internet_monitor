from flask import Flask, render_template
import sqlite3
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

DB_PATH = "/data/internet_status.db"


def get_outage_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM outages", conn)
    conn.close()
    return df


@app.route("/")
def index():
    df = get_outage_data()
    outages = df.tail(10).to_dict(orient="records")  # Get the last 10 outages
    total_outages = len(df)
    total_downtime = df["duration"].sum()
    # Generate the chart
    img = io.BytesIO()
    plt.figure(figsize=(10, 5))
    if not df.empty:
        df["start_time"] = pd.to_datetime(df["start_time"])
        df.set_index("start_time", inplace=True)
        df["duration"].plot(kind="bar")
        plt.ylabel("Duration (seconds)")
        plt.title("Internet Outage Durations Over Time")
        plt.tight_layout()
    else:
        plt.text(
            0.5,
            0.5,
            "No Data Available",
            horizontalalignment="center",
            verticalalignment="center",
        )
    plt.savefig(img, format="png")
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render_template(
        "dashboard.html",
        outages=outages,
        total_outages=total_outages,
        total_downtime=total_downtime,
        chart_url=chart_url,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
