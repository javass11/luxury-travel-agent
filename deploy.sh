#!/bin/bash
# Heroku Deployment Script for Bougee Bird
# Run this from your local machine after: heroku login

set -e

APP_NAME="bougee-bird"
SECRET_KEY="rhv2nerb_jJrGCf_rZbudsbtJRyAOHEnnv5awIkbZxk"

echo "🚀 Deploying Bougee Bird to Heroku..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Create app
echo "📦 Step 1: Creating Heroku app ($APP_NAME)..."
heroku create $APP_NAME 2>&1 || echo "ℹ️  App may already exist"

# Step 2: Add PostgreSQL
echo "🗄️  Step 2: Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:hobby-dev --app $APP_NAME 2>&1 || echo "ℹ️  Database may already exist"

# Step 3: Configure environment
echo "🔑 Step 3: Configuring environment variables..."
heroku config:set SECRET_KEY="$SECRET_KEY" --app $APP_NAME
heroku config:set DEBUG=false --app $APP_NAME
heroku config:set CORS_ORIGINS="https://bougee-bird.herokuapp.com" --app $APP_NAME

# Step 4: Deploy code
echo "📤 Step 4: Deploying code..."
git push heroku claude/hero-landing-page-pi6vV:main

# Step 5: Create tables
echo "🏗️  Step 5: Creating database tables..."
heroku run python -c "from src.app import app; from src.models import db; app.app_context().push(); db.create_all(); print('✓ Tables created')" --app $APP_NAME

# Step 6: Create admin user
echo "👤 Step 6: Creating admin user..."
heroku run python << 'EOF' --app $APP_NAME
from src.app import app
from src.models import db, User, LoyaltyProfile

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@luxurytravelagent.com').first()

    if not admin:
        admin = User(
            email='admin@luxurytravelagent.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('ChangeMe123!')

        loyalty = LoyaltyProfile(user=admin)

        db.session.add(admin)
        db.session.add(loyalty)
        db.session.commit()

        print('✓ Admin user created')
        print('  Email: admin@luxurytravelagent.com')
        print('  Password: ChangeMe123!')
    else:
        print('ℹ️  Admin already exists')
EOF

# Step 7: Test
echo "🧪 Step 7: Testing deployment..."
sleep 5
curl -X GET https://$APP_NAME.herokuapp.com/api/health

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment Complete!"
echo ""
echo "📍 App URL: https://$APP_NAME.herokuapp.com"
echo "📊 Dashboard: https://dashboard.heroku.com/apps/$APP_NAME"
echo ""
echo "🔐 Admin Credentials:"
echo "   Email: admin@luxurytravelagent.com"
echo "   Password: ChangeMe123!"
echo ""
echo "⚠️  IMPORTANT: Change admin password immediately!"
echo ""
echo "🎯 Next Steps:"
echo "   1. Login at: https://$APP_NAME.herokuapp.com/api/auth/login"
echo "   2. Change admin password"
echo "   3. Deploy frontend to Vercel/Netlify"
echo "   4. Update CORS_ORIGINS in Heroku config"
echo ""
