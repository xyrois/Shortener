# URL Shortener

A full-stack URL shortener built with FastAPI that allows users to create short links, set expiration dates, and view analytics with charts.

---

## Features

- Generate short URLs from long links
- Automatic expiration (default: 7 days)
- Custom expiration within 7-day window
- Redirect handling for shortened links
- Analytics dashboard:
  - Total clicks
  - Visits over time (chart)
  - Country-based tracking
- Clean modern frontend UI
- Automatic deletion of expired links

---

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** HTML, CSS, JavaScript
- **Charts:** Chart.js
- **Geolocation:** IP → Country lookup API

---

## How It Works

1. User enters a long URL
2. App generates a unique short key
3. Optional expiration is validated (max 7 days)
4. Short link is created and stored
5. When visited:
   - Redirects to target URL
   - Logs visit data (timestamp, country, user agent)
6. Analytics endpoint aggregates visit data and renders charts

---

## Local Setup

Clone the repo:

```bash
git clone https://github.com/YOUR_USERNAME/url-shortener.git
cd url-shortener
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn shortener_app.main:app --reload
```

Open in your browser:

```
http://127.0.0.1:8000
```

---

## Deployment

This application can be deployed using [Render](https://render.com).

**Steps:**

1. Push your project to GitHub
2. Go to [https://render.com](https://render.com)
3. Click **New → Web Service**
4. Connect your repository

**Configuration:**

| Setting | Value |
|---|---|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn shortener_app.main:app --host 0.0.0.0 --port $PORT` |

**Environment Variables**

After deployment, set:

```
BASE_URL=https://your-app-name.onrender.com
```

This ensures generated short links work across devices.

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/url` | POST | Create a short URL |
| `/{url_key}` | GET | Redirect to original URL |
| `/admin/{secret_key}` | GET | Retrieve analytics data |

**Example Request:**

```json
{
  "target_url": "https://example.com",
  "expires_at": "2026-05-01T00:00:00"
}
```

---

## Notes

- Links expire automatically after 7 days if no expiration is provided
- Expired links are deleted from the database when accessed
- Analytics include click count, visit timestamps, and country-based tracking
- IP addresses are not displayed in the UI for privacy

---

## Future Improvements

- Custom short URLs
- User authentication and dashboards
- Persistent database (PostgreSQL)
- Advanced analytics (charts by country, device type)
- Rate limiting and security improvements

---

## License

MIT License

---

## Author

Brinta Kundu