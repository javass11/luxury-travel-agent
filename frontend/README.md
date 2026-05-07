# Luxury Travel Agent - React Frontend

Modern React frontend for the Luxury Travel Agent platform.

## Features

- ✈️ Flight search with CPP comparison
- 🏨 Hotel search integration
- 🏆 Award availability search
- 💰 Redemption value calculator
- 🔐 User authentication (JWT)
- 📱 Responsive design
- ⚡ Real-time search results

## Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Backend Setup

Make sure the Flask backend is running:
```bash
cd ..
python -m src.app
```

The frontend will proxy API calls to `http://localhost:5000/api`

## Development

### File Structure

```
frontend/
├── src/
│   ├── components/      # Reusable React components
│   ├── pages/          # Page components
│   ├── hooks/          # Custom hooks (auth, etc)
│   ├── services/       # API service layer
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # React entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML entry point
├── vite.config.js      # Vite configuration
├── tailwind.config.js  # Tailwind CSS config
└── package.json
```

### Build

```bash
npm run build
```

Creates optimized production build in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Technology Stack

- **Framework:** React 18
- **Build Tool:** Vite
- **Routing:** React Router v6
- **State Management:** Zustand
- **HTTP Client:** Axios
- **Styling:** Tailwind CSS
- **Icons:** Lucide React

## API Integration

API calls are made through `src/services/api.js` which includes:
- Automatic JWT token handling
- Request/response interceptors
- Error handling with automatic logout on 401

## Authentication

The app uses JWT tokens stored in localStorage:
- `access_token` - Used for API requests
- `refresh_token` - For token refresh (future)

### Demo Account

```
Email: demo@example.com
Password: DemoPass123
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| VITE_API_URL | http://localhost:5000/api | Backend API URL |

For production, update this to your deployed backend URL.

## Production Deployment

### Build for Production

```bash
npm run build
```

### Serve with Static Host

The `dist/` folder is production-ready and can be served by:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Any static hosting

### Environment Variables for Production

Create `.env.production.local`:
```
VITE_API_URL=https://your-backend-url/api
```

## Troubleshooting

### API Connection Failed

1. Ensure backend is running on `http://localhost:5000`
2. Check VITE_API_URL environment variable
3. Check browser console for CORS errors
4. Verify backend CORS configuration

### Styling Issues

Clear cache and rebuild:
```bash
rm -rf node_modules dist
npm install
npm run build
```

### Development Server Port Already in Use

Use a different port:
```bash
npm run dev -- --port 3001
```

## Next Steps

- [ ] Implement hotel search component
- [ ] Implement award search component
- [ ] Add redemption calculator page
- [ ] Add saved deals page
- [ ] Add user profile settings
- [ ] Add deal comparison tools
- [ ] Add price alerts
- [ ] Mobile app version

## Support

For issues or questions, check the main README.md in the project root.
