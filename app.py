from flask import Flask, request
import csv
import os
from datetime import datetime

app = Flask(__name__)

WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "test123")
CSV_FILE = "conversations.csv"

# Create CSV if doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as f:
        f.write("timestamp,facebook_user_id,message\n")

@app.route("/webhook", methods=["GET"])
def verify():
    """Facebook webhook verification"""
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if token == WEBHOOK_VERIFY_TOKEN:
        print(f"✅ Webhook verified!")
        return challenge
    
    print(f"❌ Token mismatch: {token}")
    return "Invalid token", 403

@app.route("/webhook", methods=["POST"])
def receive_messages():
    """Receive messages from Facebook"""
    data = request.json
    
    try:
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                if "message" in event:
                    facebook_user_id = event["sender"]["id"]
                    message_text = event["message"].get("text", "")
                    timestamp = datetime.now().isoformat()
                    
                    # Save to CSV
                    with open(CSV_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, facebook_user_id, message_text])
                    
                    print(f"✅ Saved: {facebook_user_id} - {message_text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return {"status": "ok"}, 200

@app.route("/", methods=["GET"])
def health():
    """Health check"""
    return {"status": "running", "messages": count_messages()}, 200

def count_messages():
    """Count total messages"""
    try:
        with open(CSV_FILE, "r") as f:
            return len(f.readlines()) - 1  # Exclude header
    except:
        return 0

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
