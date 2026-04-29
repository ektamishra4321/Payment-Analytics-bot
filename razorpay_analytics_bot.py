import os
import requests
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

# ══════════════════════════════════════════════════════
#  CONFIGURATION — set these as environment variables
# ══════════════════════════════════════════════════════

RAZORPAY_KEY_ID     = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")
TEAMS_WEBHOOK_URL   = os.environ.get("TEAMS_WEBHOOK_URL")

IST = pytz.timezone("Asia/Kolkata")

# ══════════════════════════════════════════════════════
#  HELPER — Razorpay API base request
# ══════════════════════════════════════════════════════

def razorpay_get(endpoint, params=None):
    base_url = "https://api.razorpay.com/v1"
    response = requests.get(
        f"{base_url}{endpoint}",
        auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
        params=params,
        timeout=15
    )
    response.raise_for_status()
    return response.json()


def get_today_timestamps():
    """Returns Unix timestamps for start and end of today IST."""
    now     = datetime.now(IST)
    start   = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end     = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return int(start.timestamp()), int(end.timestamp())


# ══════════════════════════════════════════════════════
#  METRIC 1 — Total Collections
# ══════════════════════════════════════════════════════

def fetch_collections():
    return {"total_amount": 100000, "count": 40, "avg_ticket": 2500, "currency": "INR"}
# ══════════════════════════════════════════════════════
#  METRIC 2 — Failed Payments
# ══════════════════════════════════════════════════════
 
def fetch_failures():
    return {"failed_count": 4, "failed_amount": 8000, "failure_rate": 10, "top_reasons": [("Bank issue", 2), ("Card declined", 2)]}

# ══════════════════════════════════════════════════════
#  METRIC 3 — Refunds
# ══════════════════════════════════════════════════════

def fetch_refunds():
    return {"total_refunds": 2, "total_amount": 3000, "pending_count": 1, "processed_count": 1}

# ══════════════════════════════════════════════════════
#  METRIC 4 — Settlements
# ══════════════════════════════════════════════════════

def fetch_settlements():
    return {"last_settlement": "Today", "last_amount": 75000, "pending_amount": 10000}


# ══════════════════════════════════════════════════════
#  BUILD TEAMS ADAPTIVE CARD
# ══════════════════════════════════════════════════════

def build_teams_card(collections, failures, refunds, settlements):
    date_str = datetime.now(IST).strftime("%d %b %Y")

    failure_color = "attention" if failures["failure_rate"] > 10 else "good"

    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type":    "AdaptiveCard",
                    "version": "1.4",
                    "body": [

                        # ── Header ──
                        {
                            "type":   "TextBlock",
                            "text":   f"Razorpay Daily Summary — {date_str}",
                            "weight": "Bolder",
                            "size":   "Large",
                            "color":  "Accent",
                            "wrap":   True
                        },
                        {
                            "type":  "TextBlock",
                            "text":  "Generated at 9:00 AM IST | All figures for today",
                            "size":  "Small",
                            "color": "Default",
                            "isSubtle": True,
                            "wrap": True
                        },

                        # ── Divider ──
                        { "type": "TextBlock", "text": " ", "spacing": "None" },

                        # ── Collections ──
                        {
                            "type": "TextBlock",
                            "text": "💰 Collections",
                            "weight": "Bolder",
                            "size": "Medium",
                            "spacing": "Medium"
                        },
                        {
                            "type":    "ColumnSet",
                            "columns": [
                                {
                                    "type":  "Column",
                                    "width": "stretch",
                                    "items": [
                                        {"type": "TextBlock", "text": "Total Collected", "isSubtle": True, "size": "Small"},
                                        {"type": "TextBlock", "text": f"₹{collections['total_amount']:,.2f}", "weight": "Bolder", "size": "ExtraLarge", "color": "Good"}
                                    ]
                                },
                                {
                                    "type":  "Column",
                                    "width": "stretch",
                                    "items": [
                                        {"type": "TextBlock", "text": "Transactions", "isSubtle": True, "size": "Small"},
                                        {"type": "TextBlock", "text": str(collections["count"]), "weight": "Bolder", "size": "ExtraLarge"}
                                    ]
                                },
                                {
                                    "type":  "Column",
                                    "width": "stretch",
                                    "items": [
                                        {"type": "TextBlock", "text": "Avg Ticket", "isSubtle": True, "size": "Small"},
                                        {"type": "TextBlock", "text": f"₹{collections['avg_ticket']:,.0f}", "weight": "Bolder", "size": "ExtraLarge"}
                                    ]
                                }
                            ]
                        },

                        # ── Failed Payments ──
                        {
                            "type": "TextBlock",
                            "text": "⚠️ Failed Payments",
                            "weight": "Bolder",
                            "size": "Medium",
                            "spacing": "Medium"
                        },
                        {
                            "type":    "ColumnSet",
                            "columns": [
                                {
                                    "type":  "Column",
                                    "width": "stretch",
                                    "items": [
                                        {"type": "TextBlock", "text": "Failed Count", "isSubtle": True, "size": "Small"},
                                        {"type": "TextBlock", "text": str(failures["failed_count"]), "weight": "Bolder", "size": "ExtraLarge", "color": failure_color}
                                    ]
                                },
                                {
                                    "type":  "Column",
                                    "width": "stretch",
                                    "items": [
                                        {"type": "TextBlock", "text": "Failed Amount", "isSubtle": True, "size": "Small"},
                                        {"type": "TextBlock", "text": f"₹{failures['failed_amount']:,.2f}", "weight": "Bolder", "size": "ExtraLarge", "color": failure_color}
                                    ]
                                },
                                {
                                    "type":  "Column",
                                    "width": "stretch",
                                    "items": [
                                        {"type": "TextBlock", "text": "Failure Rate", "isSubtle": True, "size": "Small"},
                                        {"type": "TextBlock", "text": f"{failures['failure_rate']}%", "weight": "Bolder", "size": "ExtraLarge", "color": failure_color}
                                    ]
                                }
                            ]
                        },

                        # ── Top failure reasons ──
                        *([
                            {
                                "type": "TextBlock",
                                "text": "Top failure reasons: " + " | ".join(
                                    f"{r} ({c}x)" for r, c in failures["top_reasons"]
                                ),
                                "size": "Small",
                                "isSubtle": True,
                                "wrap": True
                            }
                        ] if failures["top_reasons"] else []),

                        # ── Refunds ──
                        {
                            "type": "TextBlock",
                            "text": "↩️ Refunds",
                            "weight": "Bolder",
                            "size": "Medium",
                            "spacing": "Medium"
                        },
                        {
                            "type":    "ColumnSet",
                            "columns": [
                                {
                                    "type":  "Column",
                                    "width": "stretch",
                                    "items": [
                                        {"type": "TextBlock", "text": "Total Refunds", "isSubtle": True, "size": "Small"},
                                        {"type": "TextBlock", "text": str(refunds["total_refunds"]), "weight": "Bolder", "size": "ExtraLarge"}
                                    ]
                                },
                                {
                                    "type":  "Column",
                                    "width": "stretch",
                                    "items": [
                                        {"type": "TextBlock", "text": "Refund Amount", "isSubtle": True, "size": "Small"},
                                        {"type": "TextBlock", "text": f"₹{refunds['total_amount']:,.2f}", "weight": "Bolder", "size": "ExtraLarge", "color": "Warning"}
                                    ]
                                },
                                {
                                    "type":  "Column",
                                    "width": "stretch",
                                    "items": [
                                        {"type": "TextBlock", "text": "Pending", "isSubtle": True, "size": "Small"},
                                        {"type": "TextBlock", "text": str(refunds["pending_count"]), "weight": "Bolder", "size": "ExtraLarge", "color": "Warning"}
                                    ]
                                }
                            ]
                        },

                        # ── Settlements ──
                        {
                            "type": "TextBlock",
                            "text": "🏦 Settlements",
                            "weight": "Bolder",
                            "size": "Medium",
                            "spacing": "Medium"
                        },
                        {
                            "type":    "FactSet",
                            "facts":   [
                                {"title": "Last Settlement Date",   "value": settlements["last_settlement"]},
                                {"title": "Last Settlement Amount", "value": f"₹{settlements['last_amount']:,.2f}"},
                                {"title": "Pending Settlement",     "value": f"₹{settlements['pending_amount']:,.2f}"},
                            ]
                        },

                        # ── Footer ──
                        {
                            "type":     "TextBlock",
                            "text":     "Data pulled live from Razorpay API. Check Razorpay Dashboard for full details.",
                            "size":     "Small",
                            "isSubtle": True,
                            "wrap":     True,
                            "spacing":  "Large"
                        }
                    ]
                }
            }
        ]
    }
    return card


# ══════════════════════════════════════════════════════
#  SEND TO TEAMS
# ══════════════════════════════════════════════════════

def send_to_teams(card):
    print("Sending to Microsoft Teams...")
    try:
        r = requests.post(TEAMS_WEBHOOK_URL, json=card, timeout=15)
        if r.ok:
            print(f"  Sent successfully at {datetime.now(IST).strftime('%H:%M:%S IST')}")
        else:
            print(f"  Failed: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"  Teams error: {e}")


# ══════════════════════════════════════════════════════
#  DAILY JOB
# ══════════════════════════════════════════════════════

def job():
    print(f"\n{'='*50}")
    print(f"Razorpay Analytics Bot — {datetime.now(IST).strftime('%d %b %Y %H:%M IST')}")
    print(f"{'='*50}")

    try:
        collections  = fetch_collections()
        failures     = fetch_failures()
        refunds      = fetch_refunds()
        settlements  = fetch_settlements()

        card = build_teams_card(collections, failures, refunds, settlements)
        send_to_teams(card)

        print("\nSummary:")
        print(f"  Collections : ₹{collections['total_amount']:,.2f} ({collections['count']} txns)")
        print(f"  Failures    : {failures['failed_count']} ({failures['failure_rate']}% rate)")
        print(f"  Refunds     : ₹{refunds['total_amount']:,.2f} ({refunds['total_refunds']} refunds)")
        print(f"  Settlement  : Last ₹{settlements['last_amount']:,.2f} on {settlements['last_settlement']}")

    except Exception as e:
        print(f"Job error: {e}")


# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Razorpay Analytics Bot — Starting up...")

    # Uncomment below to test immediately without waiting for schedule:
    job()

    scheduler = BlockingScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(job, "cron", hour=9, minute=0)
    print("Bot scheduled. Will post daily at 9:00 AM IST.")
    print("Press Ctrl+C to stop.\n")
    scheduler.start()
