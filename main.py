import requests
from bs4 import BeautifulSoup
import mysql.connector
import smtplib
import sys
import os
import time
from dotenv import load_dotenv
import threading
from flask import Flask, request, render_template_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Web Watcher</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Clash+Display:wght@600;700&family=Outfit:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: black;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
            font-family: 'Outfit', sans-serif;
        }

        .card {
            width: 100%;
            max-width: 480px;
        }

        .badge {
            display: inline-block;
            border: 1px solid greenyellow;
            color: greenyellow;
            font-size: 11px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 18px;
            font-family: 'Outfit', sans-serif;
        }

        h1 {
            font-family: 'Clash Display', sans-serif;
            font-size: 44px;
            font-weight: 700;
            color: white;
            line-height: 1.05;
            margin-bottom: 10px;
        }

        h1 span {
            color: greenyellow;
        }

        .subtitle {
            color: gray;
            font-size: 14px;
            margin-bottom: 28px;
            line-height: 1.7;
        }

        .box {
            background: #111;
            border: 1px solid #222;
            border-radius: 16px;
            padding: 28px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .box-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .box-title {
            font-family: 'Clash Display', sans-serif;
            font-size: 14px;
            color: white;
            font-weight: 600;
            letter-spacing: 0.02em;
        }

        .stores {
            display: flex;
            gap: 6px;
        }

        .store-pill {
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            color: gray;
            font-size: 11px;
            padding: 3px 9px;
            border-radius: 20px;
        }

        .divider {
            height: 1px;
            background: #222;
        }

        input {
            background: #0d0d0d;
            border: 1px solid #2a2a2a;
            color: white;
            padding: 11px 14px;
            border-radius: 8px;
            font-size: 14px;
            font-family: 'Outfit', sans-serif;
            outline: none;
            transition: border-color 0.2s;
            width: 100%;
        }

        input:focus {
            border-color: greenyellow;
        }

        input::placeholder {
            color: #404040;
        }

        .row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        select {
            background: #0d0d0d;
            border: 1px solid #2a2a2a;
            color: #404040;
            padding: 11px 14px;
            border-radius: 8px;
            font-size: 14px;
            font-family: 'Outfit', sans-serif;
            outline: none;
            cursor: pointer;
            width: 100%;
            appearance: none;
        }

        select.selected {
            color: white;
        }

        button {
            background: greenyellow;
            color: black;
            border: none;
            padding: 13px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Clash Display', sans-serif;
            cursor: pointer;
            letter-spacing: 0.04em;
            transition: opacity 0.2s;
            width: 100%;
        }

        button:hover {
            opacity: 0.85;
        }

        .msg {
            font-size: 13px;
            color: gray;
            text-align: center;
            padding: 8px;
            border-radius: 8px;
            background: #0d0d0d;
            border: 1px solid #2a2a2a;
            display: none;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">Price Tracker</div>
        <h1>Web <span>Watcher.</span></h1>
        <p class="subtitle">Track prices across your favourite stores.<br>Get an email the moment prices drop.</p>
        <div class="box">
            <div class="box-header">
                <span class="box-title">Add to watchlist</span>
                <div class="stores">
                    <span class="store-pill">Flipkart</span>
                    <span class="store-pill">Amazon</span>
                    <span class="store-pill">Myntra</span>
                </div>
            </div>
            <div class="divider"></div>
            <input type="text" id="name" placeholder="Item name (e.g. Nike Air Max)" />
            <input type="text" id="url" placeholder="Product URL" />
            <div class="row">
                <input type="number" id="price" placeholder="Target price (₹)" />
                <select id="store" onchange="this.classList.add('selected')">
                    <option value="" disabled selected>Select store</option>
                    <option value="1">Flipkart</option>
                    <option value="2">Amazon</option>
                    <option value="3">Myntra</option>
                </select>
            </div>
            <input type="email" id="email" placeholder="Your email" />
            <button onclick="submitForm()">Add to Watchlist</button>
            <div class="msg" id="msg"></div>
        </div>
    </div>
    <script>
        async function submitForm() {
            const res = await fetch('/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: document.getElementById('name').value,
                    url: document.getElementById('url').value,
                    price: document.getElementById('price').value,
                    store: document.getElementById('store').value,
                    email: document.getElementById('email').value
                })
            });
            const data = await res.json();
            const msg = document.getElementById('msg');
            msg.style.display = 'block';
            msg.innerText = data.message;
        }
    </script>
</body>
</html>
"""

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "web_watcher")
    )

def init_db():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("create table if not exists price_logs (id int auto_increment primary key, store_name varchar(100), price decimal(10, 2), timestamp datetime default current_timestamp)")
        cursor.execute("create table if not exists watchlist (id int auto_increment primary key, store_name varchar(100), url text, target_price decimal(10, 2), choice_code varchar(1), email varchar(100))")
        db.commit()
        db.close()
        print("✅ DB Init successful")
    except Exception as e:
        print(f"❌ DB Init failed: {e}")
        sys.exit(1)

def save_to_db(store_name, price):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("insert into price_logs (store_name, price) values (%s, %s)", (store_name, price))
        db.commit()
        db.close()
    except Exception as e:
        print(f"⚠️ Save to DB skipped: {e}")

def send_notification(store_name, price, link, email):
    msg = Mail(
        from_email=os.getenv("EMAIL_USER"),
        to_emails=email,
        subject=f"Price Drop Alert — {store_name}",
        plain_text_content=f"Price drop to ₹{price}!\nCheck it here: {link}"
    )
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(msg)
        print(f"✉️ Alert sent to {email}!")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def get_live_price(url, choice):
    api_key = os.getenv("SCRAPER_API_KEY")
    payload = {'api_key': api_key, 'url': url}
    try:
        res = requests.get('https://api.scraperapi.com', params=payload, timeout=60)
        soup = BeautifulSoup(res.content, 'html.parser')

        if choice == '1':
            boxes = soup.find_all("div", {"class": "v1zwn21l"})
            for box in boxes:
                try:
                    return float(box.get_text().replace("₹", "").replace(",", "").strip())
                except ValueError:
                    continue
            return None

        elif choice == '2':
            box = soup.find("span", {"class": "a-price-whole"})
            return float(box.get_text().replace(",", "").replace(".", "").strip()) if box else None

        elif choice == '3':
            box = soup.find("strong", {"class": "pdp-price"})
            return float("".join(filter(str.isdigit, box.get_text()))) if box else None

    except:
        return None

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/add', methods=['POST'])
def add_item():
    data = request.json
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("insert into watchlist (store_name, url, target_price, choice_code, email) values (%s, %s, %s, %s, %s)", (data['name'], data['url'], float(data['price']), data['store'], data['email']))
        db.commit()
        db.close()
        print(f"✅ Added: {data['name']}")
        return {"message": f"✅ {data['name']} added! You'll get an email at {data['email']} when price drops below ₹{data['price']}."}
    except Exception as e:
        return {"message": f"❌ Failed to add: {e}"}

def run_watcher():
    while True:
        print("⏰ Starting price check cycle...")
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("select * from watchlist")
            items = cursor.fetchall()
            db.close()

            for item in items:
                price = get_live_price(item['url'], item['choice_code'])
                print(f"🔍 Checked {item['store_name']}: Current Price = {price}, Target = {item['target_price']}")

                if price:
                    save_to_db(item['store_name'], price)
                    if price <= item['target_price']:
                        print(f"🎯 Target hit! Attempting email...")
                        sent = send_notification(item['store_name'], price, item['url'], item['email'])
                        if sent:
                            db2 = get_db_connection()
                            cursor2 = db2.cursor()
                            cursor2.execute("delete from watchlist where id = %s", (item['id'],))
                            db2.commit()
                            db2.close()
                            print(f"🗑️ Removed {item['store_name']} from watchlist")
                else:
                    print(f"⚠️ Could not fetch price for {item['store_name']}. Site might be blocking us.")

        except Exception as e:
            print(f"⚠️ Main cycle DB issue: {e}")

        print("😴 Sleeping for 1 hour...")
        time.sleep(3600)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_watcher, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Flask server starting on port {port}")
    app.run(host="0.0.0.0", port=port)