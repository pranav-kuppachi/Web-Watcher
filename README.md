# Web-Watcher

Web-Watcher is an automated price monitoring system that tracks products on websites, stores their price information and sends email when target price is reached.

The project combines web scraping, database storage, scheduled monitoring and email notifications into a single application.

## What It Does

Instead of manually checking a product page over and over, Web-Watcher handles the monitoring automatically.

The basic workflow is:

```text
Product URL
     ↓
Web Scraper
     ↓
Extract Product Information
     ↓
Store Price Data
     ↓
Compare With Previous Price
     ↓
Price Changed?
   ↙       ↘
 Yes        No
 ↓           ↓
Send Email   Continue Monitoring
```

## Features

* **Automated Web Scraping** - Extract product information from monitored websites.
* **Price Tracking** - Store and compare previous and current prices.
* **Change Detection** - Identify when a product's price changes.
* **Email Notifications** - Send alerts when tracked prices meet the target conditions.
* **Database Storage** - Store product and price information using MySQL.
* **Scheduled Monitoring** - Automatically check tracked products without requiring manual input.
* **Web Interface** - Flask based interface for interacting with the application.
* **Environment Variables** - Keep configuration and sensitive credentials outside the source code.
* **Concurrent Monitoring** - Use threading to handle multiple monitoring tasks.

## Tech Stack

### Backend

* Python
* Flask

### Web Scraping

* BeautifulSoup
* Requests

### Database

* MySQL

### Notifications

* SMTP / email service

### Other

* Threading
* Environment variables
* Git
* CI/CD

## How It Works

### 1. Add a Product

A product URL is added to the system along with the information required to identify its price.

### 2. Scrape the Website

The application sends a request to the target page and uses BeautifulSoup to extract the required product information.

### 3. Store the Price

The current price is stored in the database so that it can be compared with future checks.

### 4. Monitor Changes

The system periodically checks the product again and compares the newly extracted price with the stored value.

### 5. Send a Notification

When a relevant price change is detected, Web-Watcher sends an email notification.

## Database

MySQL is used to persist information instead of keeping the tracked data only in memory.

This allows price information to survive application restarts and provides a history that can be used for comparison and tracking.

## Running Locally

### Prerequisites

* Python 3
* MySQL
* pip

Clone the repository:

```bash
git clone https://github.com/pranav-kuppachi/Web-Watcher.git
cd Web-Watcher
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file for the required configuration and credentials.

Example:

```env
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=web_watcher

EMAIL_HOST=your_smtp_host
EMAIL_PORT=your_smtp_port
EMAIL_USER=your_email
EMAIL_PASSWORD=your_password
```

Set up the required MySQL database and then start the Flask application.

```bash
python app.py
```

> The exact entry point and environment variable names should match the files currently present in the repository.

## Project Structure

```text
Web-Watcher/
├── ...
├── requirements.txt
└── ...
```

The application is separated into the scraping, application, database, and notification components.


## License

This project is for educational and portfolio purposes.
