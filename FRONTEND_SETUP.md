# Frontend Setup Guide

Your React frontend is ready to run! This guide walks you through setting it up locally and deploying it.

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Node.js 18+ installed
- Backend running on `http://localhost:5000`

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

This installs React, Vite, Tailwind CSS, and all dependencies.

### Step 2: Start Development Server

```bash
npm run dev
```

You'll see:
```
  VITE v5.0.0  ready in 123 ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

### Step 3: Open in Browser

Visit: **http://localhost:3000**

You should see the Luxury Travel Agent home page.

## 🔐 Test Login

Use the demo account on the login page:
```
Email: demo@example.com
Password: DemoPass123
```

Or create a new account with your own email.

## 📁 Frontend Structure

```
frontend/
├── src/
│   ├── components/           # Reusable React components
│   │   ├── Navigation.jsx    # Header/nav bar
│   │   ├── SearchFlights.jsx # Flight search form & results
│   │   └── ...
│   ├── pages/               # Full page components
│   │   ├── Home.jsx         # Landing page
│   │   ├── Login.jsx        # Login page
│   │   ├── Register.jsx     # Registration page
│   │   ├── Search.jsx       # Search hub (flights/hotels/awards)
│   │   └── ...
│   ├── hooks/               # Custom React hooks
│   │   └── useAuth.js       # Authentication state management
│   ├── services/            # API integration
│   │   └── api.js           # Axios client + API methods
│   ├── App.jsx              # Main app with routing
│   ├── main.jsx             # React entry point
│   └── index.css            # Tailwind + global styles
├── index.html               # HTML entry point
├── vite.config.js           # Vite bundler config
├── tailwind.config.js       # Tailwind CSS config
├── postcss.config.js        # PostCSS config
└── package.json             # Dependencies
```

## 🎯 Running Backend + Frontend Together

### Terminal 1: Start Backend
```bash
# From project root
python -m src.app
```

Backend runs on `http://localhost:5000`

### Terminal 2: Start Frontend
```bash
# From project root
cd frontend
npm run dev
```

Frontend runs on `http://localhost:3000`

### Frontend Configuration

The frontend automatically proxies API calls to the backend via `vite.config.js`:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  }
}
```

So requests to `/api/flights/search` are proxied to `http://localhost:5000/api/flights/search`

## 🛠 Development

### Edit Components

All components are in `src/components/` and `src/pages/`

The dev server has **hot module reload** - changes appear instantly without page refresh.

### Add New API Endpoint

1. Add method to `src/services/api.js`:
```javascript
export const myService = {
  myEndpoint: (param) =>
    apiClient.post('/my-endpoint', { param }),
}
```

2. Use in component:
```javascript
const { data } = await myService.myEndpoint(value)
```

### Authentication

Handled by `useAuth()` hook from `src/hooks/useAuth.js`:
```javascript
import { useAuth } from '../hooks/useAuth'

export default function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth()
  
  // Use in component...
}
```

## 🏗 Production Build

### Build for Production

```bash
npm run build
```

Creates optimized bundle in `frontend/dist/` folder.

### Deploy to Vercel (Easiest)

1. Push code to GitHub
2. Go to https://vercel.com
3. Click "Import Project"
4. Select your repository
5. Set environment variable:
   ```
   VITE_API_URL=https://your-backend-url/api
   ```
6. Click "Deploy"

Your site is now live! Vercel auto-deploys on every push.

### Deploy to Netlify

1. Push code to GitHub
2. Go to https://netlify.com
3. Click "New site from Git"
4. Select repository
5. Build command: `cd frontend && npm run build`
6. Publish directory: `frontend/dist`
7. Set environment variable: `VITE_API_URL`
8. Click "Deploy"

### Deploy to GitHub Pages

1. Update `vite.config.js`:
```javascript
export default {
  base: '/luxury-travel-agent/',
  // ... rest of config
}
```

2. Build and push to `gh-pages` branch:
```bash
npm run build
git add frontend/dist
git commit -m "Deploy frontend"
git push -u origin main
git subtree push --prefix frontend/dist origin gh-pages
```

## 📝 Environment Variables

Create `frontend/.env.local` (for development):
```
VITE_API_URL=http://localhost:5000/api
```

For production, Vercel/Netlify will use `.env.production`:
```
VITE_API_URL=https://your-backend-url/api
```

## 🐛 Troubleshooting

### "Port 3000 already in use"

Use a different port:
```bash
npm run dev -- --port 3001
```

### API calls returning 404/CORS errors

1. Verify backend is running: `http://localhost:5000/api/health`
2. Check browser console for error details
3. Update `VITE_API_URL` environment variable

### Styling looks broken

Clear cache and rebuild:
```bash
rm -rf node_modules .next
npm install
npm run dev
```

### Login/Registration not working

1. Verify backend `/api/auth/register` and `/api/auth/login` endpoints work:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

2. Check browser Network tab for exact error

### Blank page or "Cannot find module" error

1. Install dependencies: `npm install`
2. Clear cache: `rm -rf node_modules dist && npm install`
3. Restart dev server

## 📊 Performance Tips

- Vite bundles only used code
- Tailwind CSS purges unused styles
- Images should be optimized before deploying
- Use React.lazy() for code splitting (in production build)

## 🚀 Next Steps

### Frontend Features to Add

- [ ] Hotel search component
- [ ] Award availability search
- [ ] Redemption calculator
- [ ] Saved deals page
- [ ] Deal comparison tools
- [ ] User profile page
- [ ] Price alert notifications
- [ ] Mobile app version (React Native)

### Backend Features to Integrate

- [ ] Implement hotel search
- [ ] Implement award search
- [ ] Add price tracking
- [ ] Add push notifications
- [ ] Add ML-based recommendations

## 📚 Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- [Axios Documentation](https://axios-http.com)

## 🎉 You're All Set!

Your full-stack application is now ready:

✅ **Backend** (Flask) → http://localhost:5000  
✅ **Frontend** (React) → http://localhost:3000  
✅ **Real APIs** (Amadeus, Seats.aero)  
✅ **Authentication** (JWT)  
✅ **Database** (PostgreSQL or SQLite)  

**Next:** Run both servers and start building features!

---

**Need help?** Check `frontend/README.md` for more details.
