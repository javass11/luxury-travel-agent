# Luxury Travel Agent

A premium web application for discovering exceptional flight and hotel deals using miles and points, with intelligent CPP (cents-per-point) analysis.

## Features

- **Premium Search Interface** - Elegant hero landing page with flight and hotel search
- **Flight Search** - Browse business and first-class premium redemptions
- **Hotel Search** - Luxury property availability with cash vs. points comparison
- **CPP Engine** - Intelligent cents-per-point calculator highlighting value deals
- **Loyalty Profiles** - Track miles balances and elite status across programs
- **Deal Saving** - Bookmark and track favorite redemptions
- **AI Assistant** - Context-aware LLM assistant for personalized recommendations
- **Responsive Design** - Optimized for desktop and mobile with luxury aesthetics

## Project Structure

```
luxury-travel-agent/
├── src/
│   ├── app.py              # Flask application and API routes
│   ├── database.py         # SQLite database layer
│   ├── models.py           # Data models and dataclasses
│   ├── config.py           # Configuration and environment variables
│   ├── flights.py          # Flight search engine
│   ├── hotels.py           # Hotel search engine
│   ├── agent.py            # LLM-powered travel assistant
│   └── __init__.py
├── static/
│   └── index.html          # Premium UI interface
├── tests/
│   ├── test_database.py    # Database tests
│   ├── test_flights.py     # Flight engine tests
│   ├── test_hotels.py      # Hotel engine tests
│   └── test_agent.py       # Assistant tests
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── test_db.py             # Quick database validation script
```

## Installation

1. **Clone and setup:**
```bash
git clone https://github.com/javass11/luxury-travel-agent.git
cd luxury-travel-agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and add your API credentials
```

## Configuration

Required environment variables in `.env`:

```
# Anthropic API for LLM Assistant
ANTHROPIC_API_KEY=sk-...

# External Travel APIs (optional for advanced features)
AMADEUS_CLIENT_ID=your-amadeus-id
AMADEUS_CLIENT_SECRET=your-amadeus-secret
DUFFEL_ACCESS_TOKEN=your-duffel-token
SEATS_AERO_API_KEY=your-seats-aero-key

# Flask Configuration
DEBUG=False
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///luxury_travel.db
```

## Running the Application

**Start the Flask server:**
```bash
python -m src.app
```

The application will be available at `http://localhost:5000`

## Testing

**Run all tests:**
```bash
python -m pytest tests/ -v
```

**Run specific test suite:**
```bash
python -m pytest tests/test_flights.py -v
python -m pytest tests/test_hotels.py -v
```

**Quick database validation:**
```bash
python test_db.py
```

## API Endpoints

### Search & Analysis
- `POST /api/deals/analyze` - Search flights and hotels, analyze CPP
- `GET /api/flights/search` - Search flights by route and date
- `GET /api/hotels/search` - Search hotels by destination and dates

### Assistant
- `POST /api/chat` - Chat with AI travel assistant

### Deal Management
- `POST /api/deals/save` - Save a deal for later
- `GET /api/health` - Check API health and credentials

## Data Models

### FlightDeal
- Origin/destination airport codes
- Departure date and cabin class
- Cash price and miles cost
- Calculated CPP value
- Seat map and amenities info

### HotelDeal
- Property name and location
- Check-in/check-out dates
- Cash rate and points cost
- Calculated CPP value
- Elite night credits and suite upgrade availability

### LoyaltyProfile
- User miles balances by airline
- Hotel points balances by program
- Elite status by program
- Profile timestamps

## Security Considerations

- ✅ API credentials securely loaded from environment variables
- ✅ Database uses SQLite with parameterized queries
- ✅ LLM requests processed server-side only
- ✅ User profile data not exposed to frontend
- ✅ CORS headers properly configured
- ✅ Input validation on all API endpoints

## Known Limitations

- Sample data provided for demo purposes
- Real-time flight/hotel data requires external API credentials
- LLM features require Anthropic API key configuration

## Future Enhancements

- Integration with live flight APIs (Amadeus, Duffel)
- Real-time seat map visualization (SeatsAero)
- User authentication and saved deals dashboard
- Mobile app with push notifications
- Advanced filters and sorting options
- Historical pricing analysis

## Contributing

Contributions welcome! Please ensure tests pass before submitting PRs.

## License

MIT License - See LICENSE file for details
