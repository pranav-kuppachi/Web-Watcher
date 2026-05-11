Web Watcher 🔍 : An Automated 24/7 Price Tracking & Alert Engine

Web Watcher is a robust data extraction tool designed to monitor price volatility across major e-commerce platforms (Amazon, Flipkart, Myntra). It automates the tedious process of manual tracking by utilizing multi-threaded scraping and real-time email notifications.

Key Feature ⏰ :
1. 24/7 Automated Monitoring: Runs continuously to capture price drops the moment they happen.
2. Multi-Platform Support: Specialized scrapers for Amazon, Flipkart, and Myntra.
3. Real-Time Alerts: Integrated with SendGrid SMTP to deliver instant email notifications.
4. Data Persistence: Uses MySQL to store historical price data for trend analysis.
5. Web Dashboard: A Flask-based interface to view tracked items and status at a glance.

Tech Stack 🛠️:
1. Language: Python
2. Scraping: BeautifulSoup4, Requests
3. Backend: Flask (Web Server)
4. Database: MySQL
5. Notification: SendGrid API / SMTP
6. Deployment: Render / GitHub Actions (CI/CD)

Architecture 🏗️:
1. Extraction Layer: Python scripts utilize BeautifulSoup to parse HTML and extract specific price/availability selectors.
2. Logic Layer: Compares current scraped price against the "Target Price" or "Last Known Price" stored in the database.
3. Persistence Layer: All logs and price histories are committed to a relational MySQL schema.
4. Notification Layer: If a price drop criteria is met, an asynchronous trigger sends an email via SendGrid.

Installation & Setup 📦
1. Clone the repository:  git clone https://github.com/pranavkuppachi/web-watcher.git, cd web-watcher
2. Install dependencies: pip install -r requirements.txt
3. Create a .env file and add your credentials:
   DB_HOST=your_host
   DB_USER=your_user
   DB_PASS=your_password
   SENDGRID_API_KEY=your_key
4. Run the application: python app.py
