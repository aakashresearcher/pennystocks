#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Penny Stock INR Price Prediction Bot
- Fetches Indian penny stocks in INR
- Predicts next-day price (5-day moving avg)
- Sends updates via Telegram
"""

import os, time, requests, schedule, pytz
import yfinance as yf
from datetime import datetime

# =========================
# CONFIG
# =========================
LOCAL_TZ = pytz.timezone("Asia/Kolkata")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # set in Railway/Render
CHAT_ID = os.getenv("CHAT_ID")

# Penny stocks (India)
INDIA_PENNY = [
    "SUZLON.NS","JPPOWER.NS","IDEA.NS","YESBANK.NS","RENUKA.NS",
    "PNB.NS","IRFC.NS","NHPC.NS","IOB.NS","UCOBANK.NS",
    "RPOWER.NS","SOUTHBANK.NS","UNIONBANK.NS","IDFCFIRSTB.NS",
    "CENTRALBK.NS","JISLJALEQS.NS","BANKINDIA.NS","GTLINFRA.NS",
    "NBCC.NS","RVNL.NS","HUDCO.NS","MMTC.NS","ITI.NS"
]

# =========================
# UTILITIES
# =========================

def now_str():
    return datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")

def send_telegram(msg: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[!] Telegram not configured. Msg:")
        print(msg)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def fetch_quotes(tickers):
    data = {}
    tk = yf.Tickers(" ".join(tickers))
    for t in tickers:
        try:
            fi = tk.tickers[t].fast_info
            price = fi.last_price
            hist = tk.tickers[t].history(period="5d")["Close"]
            pred = hist.mean() if not hist.empty else price
            data[t] = {"price": price, "pred": pred}
        except Exception:
            data[t] = {"price": None, "pred": None}
    return data

# =========================
# JOB
# =========================

def job_prices():
    data = fetch_quotes(INDIA_PENNY)
    lines = [f"📊 Stock Price Update ({now_str()})"]
    for t, v in data.items():
        if v["price"]:
            lines.append(f"- {t}: ₹{v['price']:.2f} → Tomorrow ~ ₹{v['pred']:.2f}")
        else:
            lines.append(f"- {t}: ❌ No data")
    send_telegram("\n".join(lines))

# =========================
# MAIN
# =========================

def main():
    job_prices()  # run immediately
    schedule.every(6).hours.do(job_prices)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
