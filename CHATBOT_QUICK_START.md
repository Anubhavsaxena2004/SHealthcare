# 🚀 Healthcare Chatbot - Quick Setup Guide

## 1️⃣ Get OpenAI API Key (2 minutes)

### Step 1: Create OpenAI Account
- Go to https://platform.openai.com/signup
- Sign up with email or Google/Microsoft account
- Verify email

### Step 2: Generate API Key
- Visit https://platform.openai.com/account/api-keys
- Click "Create New Secret Key"
- Copy the key (you won't see it again!)
- **Keep it secure** - never commit to Git

### Step 3: Check API Pricing
- Visit https://platform.openai.com/account/billing/overview
- Add payment method if needed
- Models used: `gpt-4o-mini` (cheapest, fastest)
- Approximate cost: $0.15 per 1M input tokens

---

## 2️⃣ Configure Environment (2 minutes)

### Create or Update `.env` file:

```env
# REQUIRED - OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# OPTIONAL - Flask Configuration
FLASK_SECRET_KEY=your-super-secret-random-key-here
FLASK_ENV=development

# OPTIONAL - Database
DATABASE_URL=sqlite:///users.db

# OPTIONAL - Debug Mode
DEBUG=True
```

### Generate Secure Flask Key (Optional but Recommended):
```python
import secrets
print(secrets.token_hex(32))
```

---

## 3️⃣ Install Dependencies (1 minute)

```bash
# Navigate to project directory
cd diabetes-heart-prediction-main

# Install/Update packages
pip install -r requirements.txt

# Verify installation
python -c "from openai import OpenAI; print('✅ OpenAI installed')"
```

---

## 4️⃣ Test the Chatbot (2 minutes)

### Option A: Web Interface (Recommended)
```bash
# Start Flask application
python run.py

# Open browser
# http://localhost:5000

# Login/Signup
# You'll see chatbot button (💬) in bottom-right corner
```

### Option B: Test API Directly
```bash
# In terminal/PowerShell
curl -X POST http://localhost:5000/api/health-chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "Explain my diabetes risk"}'
```

### Option C: Python Test Script
```python
import requests
import json

# Health chat endpoint
response = requests.post(
    'http://localhost:5000/api/health-chat',
    json={
        'user_id': 1,
        'message': 'What causes high diabetes risk?'
    }
)

print(json.dumps(response.json(), indent=2))
```

---

## 5️⃣ Feature Checklist

After setup, test these features:

### ✅ Risk Explanation
```
User: "Explain my diabetes risk"
Expected: Bot fetches latest result and explains with factors
```

### ✅ Preventive Guidance
```
User: "How can I lower my score?"
Expected: Structured diet/exercise/lifestyle tips
```

### ✅ Health Education
```
User: "What is diabetes?"
Expected: Definition + risk factors + normal ranges
```

### ✅ Navigation
```
User: "Go to dashboard"
Expected: { "type": "navigation", "route": "/dashboard" }
```

### ✅ Safety Block
```
User: "What medicine should I take?"
Expected: ⚠️ Cannot prescribe. Suggest consulting doctor.
```

### ✅ General Knowledge
```
User: "What is machine learning?"
Expected: AI-generated response from OpenAI
```

---

## 🎯 Common Scenarios

### Scenario 1: User Asks About Their Risk
```
Input:
{
  "user_id": 1,
  "message": "Explain my last diabetes result"
}

Output:
{
  "type": "health_response",
  "reply": "Your diabetes risk is 68%, categorized as moderate risk...",
  "contributing_factors": ["Elevated glucose (145 mg/dL)", "High BMI (28.5)"],
  "preventive_actions": ["Exercise 150 mins/week", "Reduce sugar intake"],
  "suggested_actions": ["Download Report", "Schedule Consultation"]
}
```

### Scenario 2: User Asks for Prevention Tips
```
Input:
{
  "user_id": 1,
  "message": "How can I prevent heart disease?"
}

Output:
{
  "type": "health_response",
  "reply": "## Prevention for Heart Disease\n\n**Definition:** ...",
  "suggested_actions": ["Learn More", "Start New Assessment"]
}
```

### Scenario 3: User Tries to Get Prescription (Blocked)
```
Input:
{
  "user_id": 1,
  "message": "Prescribe medicine for diabetes"
}

Output:
{
  "type": "safety_block",
  "reply": "⚠️ Safety Notice: I cannot provide medication prescriptions...",
  "suggested_actions": ["Explain my risk", "Prevention tips"]
}
```

### Scenario 4: User Asks General Question
```
Input:
{
  "user_id": 1,
  "message": "What does machine learning mean?"
}

Output:
{
  "type": "ai_response",
  "reply": "Machine learning is...",
  "source": "OpenAI GPT-4o-mini",
  "disclaimer": "This is educational guidance, not medical advice."
}
```

---

## 🔍 Testing Endpoints

### Health Chat Endpoint
**URL:** `POST /api/health-chat`

```bash
curl -X POST http://localhost:5000/api/health-chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "What does high glucose mean?"
  }'
```

### General Chat Endpoint
**URL:** `POST /api/general-chat`

```bash
curl -X POST http://localhost:5000/api/general-chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "Explain quantum physics"
  }'
```

### Chat Suggestions Endpoint
**URL:** `GET /api/chat-suggestions/{user_id}`

```bash
curl http://localhost:5000/api/chat-suggestions/1
```

---

## ⚙️ Customization

### Change Risk Level Thresholds
Edit `app/chatbot_service.py`:
```python
def _calculate_risk_level(self, probability: float) -> str:
    if probability >= 70:      # High
        return "High"
    elif probability >= 40:    # Moderate
        return "Moderate"
    else:                      # Low
        return "Low"
```

### Modify OpenAI Temperature (Randomness)
```python
response = self.openai_client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.7,           # 0=Deterministic, 1=Random (0-2)
    max_tokens=500             # Response length limit
)
```

### Change OpenAI Model
```python
model="gpt-4o-mini"   # Default (fast, cheap)
model="gpt-4"         # More powerful, more expensive
model="gpt-3.5-turbo" # Older, similar quality to gpt-4o-mini
```

### Customize Chatbot Styling
Edit `app/templates/chatbot.html` CSS:
```css
.chatbot-container {
    width: 400px;           /* Change width */
    height: 600px;          /* Change height */
    bottom: 70px;           /* Distance from bottom */
    right: 20px;            /* Distance from right */
}

.chatbot-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Change gradient colors */
}
```

---

## 🐛 Debugging

### Enable Debug Logging
```python
# In routes.py or run.py
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.debug(f"Chatbot message: {message}")
```

### Test OpenAI Connection
```python
from openai import OpenAI
import os

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("❌ OPENAI_API_KEY not found in .env")
else:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "test"}]
    )
    print("✅ OpenAI connection successful")
```

### Check Database Data
```python
from app import db
from app.models import User, Result, flask

# Create app context
with flask.Flask(__name__).app_context():
    results = Result.query.all()
    for result in results:
        print(f"User: {result.user_id}, Disease: {result.disease_selected}, Risk: {result.probability}%")
```

---

## 📊 Monitor API Usage

### View OpenAI Usage
- Dashboard: https://platform.openai.com/account/billing/overview
- Usage tab: See tokens used per model
- Estimated cost: Based on token count

### Calculate Tokens
```python
# Rough estimate: 1 token ≈ 4 characters
# Exact count: use tiktoken library

pip install tiktoken
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o-mini")
tokens = len(enc.encode("your_text_here"))
```

---

## 🚨 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "Chatbot not appearing" | Check if logged in, refresh page, check console |
| "OpenAI API error" | Verify `OPENAI_API_KEY` in .env, check credits |
| "Intent detection wrong" | Check regex patterns in `chatbot_service.py` |
| "Database not found" | Run `python init_db.py` to initialize DB |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Port 5000 already in use" | Kill existing process or change port in `run.py` |

---

## 📱 Mobile Testing

The chatbot is mobile-responsive:
```css
@media (max-width: 600px) {
    .chatbot-container {
        width: calc(100vw - 40px);  /* Full width minus margins */
        height: calc(100vh - 200px); /* Full height minus nav/input */
    }
}
```

---

## 🔐 Environment Variable Checklist

```bash
# Check all required vars are set
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['OPENAI_API_KEY', 'FLASK_SECRET_KEY']
for var in required:
    value = os.getenv(var)
    status = '✅' if value else '❌'
    print(f'{status} {var}: {\"SET\" if value else \"MISSING\"}')"
```

---

## 🎓 Learning Resources

- **OpenAI API Docs:** https://platform.openai.com/docs/api-reference
- **Flask Documentation:** https://flask.palletsprojects.com/
- **SQLAlchemy Guide:** https://docs.sqlalchemy.org/
- **Regular Expressions:** https://regex101.com/

---

## 📋 Next Steps

1. ✅ Update `.env` with OpenAI API key
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Start app: `python run.py`
4. ✅ Test chatbot in browser (bottom-right corner)
5. ✅ Test API endpoints with curl/Postman
6. ✅ Review customization options
7. ✅ Deploy to production (see deployment guide)

---

**Version:** 1.0.0  
**Last Updated:** February 19, 2026  
**Status:** Ready to Use ✅
