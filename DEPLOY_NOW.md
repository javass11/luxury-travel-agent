# 🚀 Deploy to Heroku - Ready Now!

**Your app is ready to deploy to Heroku with app name: `bougee-bird`**

---

## ⚡ Quick Deploy (3 minutes)

### Step 1: Install Heroku CLI (if not already installed)

**macOS:**
```bash
brew tap heroku/brew && brew install heroku
```

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

**Windows:**
Download from: https://cli-assets.heroku.com/heroku-x64.exe

---

### Step 2: Login to Heroku

```bash
heroku login
```

This opens a browser window. Sign in with your Heroku account, then return to terminal.

---

### Step 3: Run the Deployment Script

From the project root directory, run:

```bash
bash deploy.sh
```

This will:
- ✅ Create Heroku app (bougee-bird)
- ✅ Add PostgreSQL database
- ✅ Set environment variables
- ✅ Deploy your code
- ✅ Create database tables
- ✅ Set up admin user
- ✅ Test the deployment

**Total time:** 3-5 minutes

---

## 🔐 Admin Credentials

After deployment:
- Email: `admin@luxurytravelagent.com`
- Password: `ChangeMe123!`

**⚠️ Change this immediately after login!**

---

## ✅ After Deployment

Test the API:
```bash
curl https://bougee-bird.herokuapp.com/api/health
```

View logs:
```bash
heroku logs --tail --app bougee-bird
```

---

## 🌐 Deployment Flow

1. ✅ Run `bash deploy.sh`
2. ✅ Heroku CLI creates app + database
3. ✅ Code is deployed
4. ✅ Backend is LIVE at: https://bougee-bird.herokuapp.com
5. Next: Deploy React frontend to Vercel/Netlify

---

## 📊 Cost: FREE (for testing)
- Dyno: $0/month
- PostgreSQL: $0/month

---

## 📚 More Info

- `HEROKU_DEPLOYMENT.md` - Full detailed guide
- `deploy.sh` - Automated deployment script
- `.env.production.example` - Environment template

---

**Ready? Run:** `bash deploy.sh` 🚀
