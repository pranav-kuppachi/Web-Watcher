import requests
from bs4 import BeautifulSoup
import mysql.connector
import smtplib
from email.mime.text import MIMEText
import sys
import os
import time
from dotenv import load_dotenv
import threading
from flask import Flask, request, render_template_string

load_dotenv()

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Web Watcher</title>
    <style>
        body { 
            font-family: sans-serif; 
            max-width: 500px; 
            margin: 60px auto; 
            padding: 0 20px; 
            background: #0f0f0f; 
            color: #fff; 
        }

        h1 { 
            color: #adff2f;
        }

        input, select { 
            width: 100%; 
            padding: 10px; 
            margin: 8px 0; 
            border-radius: 6px; 
            border: 1px solid #333; 
            background: #1a1a1a; 
            color: #fff; 
            box-sizing: border-box;
        }

        button { 
            width: 100%; 
            padding: 12px; 
            background: #adff2f; 
            color: #000; 
            font-weight: bold; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            margin-top: 10px;
        }

        .msg { 
            margin-top: 16px; 
            padding: 10px; 
            border-radius: 6px; 
            background: #1a1a1a;
        }

    </style>
</head>
<body>
    <h1>🔍 Web Watcher</h1>
    <p>Track prices on Flipkart, Amazon and Myntra. Get email alerts when prices drop.</p>
    <input type="text" id="name" placeholder="Item Name (e.g. Nike Air Max)" />
    <input type="text" id="url" placeholder="Product URL" />
    <input type="number" id="price" placeholder="Target Price (₹)" />
    <select id="store">
        <option value="1">Flipkart</option>
        <option value="2">Amazon</option>
        <option value="3">Myntra</option>
    </select>
    <input type="email" id="email" placeholder="Your Email" />
    <button onclick="submit()">Add to Watchlist</button>
    <div class="msg" id="msg" style="display:none"></div>
    <script>
        async function submit() {
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
    # ADDED: .replace(" ", "") ensures the 16-digit App Password works even if pasted with spaces
    app_pass = os.getenv("EMAIL_PASS").replace(" ", "")
    sender = os.getenv("EMAIL_USER")
    msg = MIMEText(f"Price drop to ₹{price}!\nCheck it here: {link}", 'plain', 'utf-8')
    msg['Subject'] = f"Price Drop Alert — {store_name}"
    msg['From'] = sender
    msg['To'] = email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, app_pass)
            server.send_message(msg)
            print(f"✉️ Alert sent to {email}!")
            return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def get_live_price(url, choice):
    api_key = os.getenv("SCRAPER_API_KEY")
    scraper_url = f"http://api.scraperapi.com?api_key={api_key}&url={url}"
    try:
        res = requests.get(scraper_url, timeout=60)
        soup = BeautifulSoup(res.content, 'html.parser')

        if choice == '1':
            boxes = soup.find_all("div", {"class": "v1zwn21l"})
            for box in boxes:
                try:
                    return float(box.get_text().replace("₹", "").replace(",", "").strip())
                except ValueError: continue
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
                # ADDED: Debug print to show current price in Render logs
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
                    # ADDED: Error print for blocked scrapers
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