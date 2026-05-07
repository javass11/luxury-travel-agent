# 🖥️ Windows Local Setup Guide

Get Bougee Bird running on your laptop in 5 minutes!

---

## ⚡ Quick Start

### Step 1: Download Python

Go to: https://www.python.org/downloads/

Click the big yellow **"Download Python 3.11"** button.

When you run the installer:
- ✅ Check the box: **"Add Python to PATH"** (IMPORTANT!)
- ✅ Click "Install Now"

Wait for it to finish.

---

### Step 2: Get the Project

**Option A: If you have Git**
```bash
git clone https://github.com/javass11/luxury-travel-agent.git
cd luxury-travel-agent
```

**Option B: If you don't have Git**
1. Go to: https://github.com/javass11/luxury-travel-agent
2. Click green "Code" button → "Download ZIP"
3. Unzip the folder
4. Rename to `luxury-travel-agent`

---

### Step 3: Run Setup Script

1. Open Command Prompt (Press `Windows Key + R`, type `cmd`, press Enter)
2. Navigate to the project folder:
   ```bash
   cd C:\Users\YourName\Downloads\luxury-travel-agent
   ```
   (Replace `YourName` with your Windows username)

3. Run the setup script:
   ```bash
   setup-windows.bat
   ```

Wait 2-3 minutes while it installs everything.

---

## ✅ When Setup is Done

You'll see:
```
============================================================
 SETUP COMPLETE!
============================================================

Your development environment is ready!

To start the app, run:
   python -m src.app

Then open your browser to:
   http://localhost:5000
```

---

## 🚀 Start the App

In Command Prompt (in the `luxury-travel-agent` folder):

```bash
python -m src.app
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

## 🌐 Open in Browser

Click this link or copy it to your browser:

**http://localhost:5000**

You should see the Luxury Travel Agent homepage!

---

## 🧪 Test It Works

### Login with Demo Account:
- Email: `demo@example.com`
- Password: `DemoPass123`

### Or Create New Account:
Click "Register" and create a new account with a password containing:
- At least 8 characters
- 1 uppercase letter
- 1 number

---

## 🛑 Stop the App

Press `Ctrl + C` in Command Prompt.

---

## 📁 What You Now Have

```
luxury-travel-agent/
├── venv/                 (Virtual environment)
├── src/                  (All the code)
├── requirements.txt      (Dependencies)
├── .env                  (Configuration)
└── setup-windows.bat     (Setup script)
```

---

## ✨ What's Running Locally

✅ Backend API at http://localhost:5000
✅ PostgreSQL-style database (SQLite for local testing)
✅ All features: flights, hotels, alerts, analytics, etc.
✅ Authentication (register/login)
✅ Security: encryption, rate limiting, etc.

---

## 🆘 Troubleshooting

### "python: command not found"
**Solution:** Python not installed correctly. Reinstall from:
https://www.python.org/downloads/
Make sure to check "Add Python to PATH"

### "ModuleNotFoundError"
**Solution:** Run setup script again:
```bash
setup-windows.bat
```

### "Port 5000 already in use"
**Solution:** Close other apps using port 5000, or change port:
```bash
python -c "from src.app import app; app.run(port=5001)"
```

### "Database error"
**Solution:** Delete the database and restart:
```bash
del luxury_travel.db
python -m src.app
```

---

## 🎯 Next Steps

Once it's working locally:

1. **Test the API:**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Create test data:**
   - Register new account
   - Search flights
   - Create alerts
   - Save deals

3. **Deploy to Heroku:**
   When ready, run:
   ```bash
   bash deploy.sh
   ```

---

## 💡 Tips

- Keep Command Prompt window open while app is running
- Don't close the window or the app stops
- Changes to Python files take effect immediately (auto-reload)
- Database file: `luxury_travel.db` (auto-created)
- Environment: `.env` (auto-created)

---

**You're all set! Start the app and explore! 🚀**
