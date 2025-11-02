from flask import Flask, request
import csv
from datetime import datetime
import os

app = Flask(__name__)

CSV_FILE = "conversations.csv"
WEBHOOK_VERIFY_TOKEN = "PranCartFacebookConversation2025"

# Create CSV if doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as f:
        f.write("timestamp,facebook_user_id,message\n")

@app.route("/", methods=["GET"])
def verify_root():
    """Handle webhook verification at root"""
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    print(f"Verification request: token={token}, challenge={challenge}")
    
    if token == WEBHOOK_VERIFY_TOKEN:
        print("✅ Webhook verified!")
        return challenge
    
    print("❌ Invalid token!")
    return "Invalid token", 403

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Handle webhook verification at /webhook"""
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    print(f"Verification request: token={token}, challenge={challenge}")
    
    if token == WEBHOOK_VERIFY_TOKEN:
        print("✅ Webhook verified!")
        return challenge
    
    print("❌ Invalid token!")
    return "Invalid token", 403

@app.route("/webhook", methods=["POST"])
def receive_messages():
    """Receive messages from Facebook"""
    data = request.json
    print(f"📨 Received webhook: {data}")
    
    try:
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                if "message" in event:
                    user_id = event["sender"]["id"]
                    message = event["message"].get("text", "")
                    timestamp = datetime.now().isoformat()
                    
                    print(f"💬 Message from {user_id}: {message}")
                    
                    # Save to CSV
                    with open(CSV_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, user_id, message])
                    
                    print(f"✅ Saved to conversations.csv")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return {"status": "ok"}, 200

@app.route("/", methods=["GET", "POST"])
def health():
    """Health check"""
    try:
        with open(CSV_FILE, "r") as f:
            count = len(f.readlines()) - 1
        return {"status": "running", "messages": count}, 200
    except:
        return {"status": "running", "messages": 0}, 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
