#!/bin/bash

echo "🚀 Deploying Luxury Travel Agent to Heroku"
echo "=========================================="
echo ""

# Check if heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not installed"
    echo "Install from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Heroku CLI found"
echo ""

# Login to Heroku
echo "Step 1: Login to Heroku (browser will open)"
heroku login

echo ""
echo "Step 2: Creating Heroku app..."
APP_NAME="luxury-travel-agent-$(date +%s)"
heroku create $APP_NAME

echo ""
echo "Step 3: Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:hobby-dev --app $APP_NAME

echo ""
echo "Step 4: Setting environment variables..."
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') --app $APP_NAME
heroku config:set JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') --app $APP_NAME

echo ""
echo "Step 5: Deploying code..."
git push heroku main

echo ""
echo "Step 6: Running migrations..."
heroku run alembic upgrade head --app $APP_NAME

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo ""
echo "Your app is live at:"
echo "https://$APP_NAME.herokuapp.com"
echo ""
echo "Test it:"
echo "curl https://$APP_NAME.herokuapp.com/api/health"
echo ""
