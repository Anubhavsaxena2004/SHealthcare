# 🏥 Healthcare Chatbot - System Architecture Guide

## System Overview Diagram

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    USER INTERFACE LAYER                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                             ┃
┃  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┃
┃  ┃        Healthcare Chatbot Widget                    ┃  ┃
┃  ┃  ┌──────────────────────────────────────────────┐  ┃  ┃
┃  ┃  │ 🏥 Health AI Assistant                       │  ┃  ┃
┃  ┃  │                                              │  ┃  ┃
┃  ┃  │ [Chat Messages Display Area]                │  ┃  ┃
┃  ┃  │                                              │  ┃  ┃
┃  ┃  │ ┌──────────────────────────────────────────┐│  ┃  ┃
┃  ┃  │ │ Bot: Your diabetes risk is 68%...      ││  ┃  ┃
┃  ┃  │ └──────────────────────────────────────────┘│  ┃  ┃
┃  ┃  │                                              │  ┃  ┃
┃  ┃  │ [Suggested Prompts] [Input Field] [Send]   │  ┃  ┃
┃  ┃  │                                              │  ┃  ┃
┃  ┃  └──────────────────────────────────────────────┘  ┃  ┃
┃  ┃                                                     ┃  ┃
┃  ┃  Plus: Toggle Button 💬 (bottom-right corner)    ┃  ┃
┃  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ┃
┃                                                             ┃
┃  File: app/templates/chatbot.html                          ┃
┃  + HTML structure                                          ┃
┃  + CSS styling (responsive, animations)                   ┃
┃  + JavaScript event handling                              ┃
┃                                                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                              │
                              │ JSON REST API
                              ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                     API ENDPOINT LAYER                      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                             ┃
┃  POST /api/health-chat                                     ┃
┃  ├─ Takes: { message, user_id }                           ┃
┃  └─ Returns: JSON response (health_response, etc.)        ┃
┃                                                             ┃
┃  POST /api/general-chat                                    ┃
┃  ├─ Takes: { message, user_id? }                          ┃
┃  └─ Returns: JSON response (ai_response, etc.)            ┃
┃                                                             ┃
┃  GET /api/chat-suggestions/{user_id}                       ┃
┃  └─ Returns: { suggestions[], context }                   ┃
┃                                                             ┃
┃  File: app/routes.py                                       ┃
┃                                                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                              │
                              │ Service Function Calls
                              ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                   CHATBOT SERVICE LAYER                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                             ┃
┃  ┌────────────────────────────────────────────────────┐   ┃
┃  │ Intent Detection Engine                            │   ┃
┃  │ • Pattern matching with regex                      │   ┃
┃  │ • 6 intent types identified                        │   ┃
┃  │ • Falls back to "general" if no match             │   ┃
┃  └────────────────────────────────────────────────────┘   ┃
┃           │ Detected Intent │                              ┃
┃           ▼                 ▼                              ┃
┃  ┌─────────────────────────────────────────────────────┐  ┃
┃  │ Intent Handlers                                     │  ┃
┃  │                                                    │  ┃
┃  │ 1️⃣ Risk Explanation Hander                        │  ┃
┃  │    └─ Queries DB → Analyzes factors → Explains   │  ┃
┃  │                                                    │  ┃
┃  │ 2️⃣ Preventive Measures Handler                    │  ┃
┃  │    └─ Knowledge Base → Risk-tailored plan        │  ┃
┃  │                                                    │  ┃
┃  │ 3️⃣ Navigation Handler                             │  ┃
┃  │    └─ Route mapping → Redirect response          │  ┃
┃  │                                                    │  ┃
┃  │ 4️⃣ Health Education Handler                       │  ┃
┃  │    └─ Knowledge Base → Educational content       │  ┃
┃  │                                                    │  ┃
┃  │ 5️⃣ Medical Prescription Handler (Safety Block!)  │  ┃
┃  │    └─ ⚠️ ALWAYS DECLINE with disclaimer          │  ┃
┃  │                                                    │  ┃
┃  │ 6️⃣ General Knowledge (Fallback)                   │  ┃
┃  │    └─ OpenAI GPT-4o-mini request                 │  ┃
┃  │                                                    │  ┃
┃  └─────────────────────────────────────────────────────┘  ┃
┃                                                             ┃
┃  File: app/chatbot_service.py                              ┃
┃                                                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                    │     │      │       │       │       │
        ┌───────────┘     │      │       │       │       └─────────┐
        │                 │      │       │       │                  │
        ▼                 ▼      ▼       ▼       ▼                  ▼
    ┌────────────┐   ┌─────────────────────────────────┐    ┌────────────┐
    │ DATABASE   │   │   KNOWLEDGE BASE                │    │   OpenAI   │
    │ (SQLAlch)  │   │  (Dictionary Data)             │    │   API      │
    │            │   │                                │    │            │
    │ • User     │   │ Diabetes:                      │    │ GPT-4o-mini│
    │ • Result   │   │ • Definition                   │    │ + system   │
    │   - disease│   │ • Risk factors                 │    │   prompt   │
    │   - prob   │   │ • Normal ranges                │    │ (Healthcare│
    │   - fields │   │ • Prevention tips              │    │  aware)    │
    │            │   │                                │    │            │
    │ Queries:   │   │ Heart Disease:                 │    │ Returns:   │
    │ • GET last │   │ • Definition                   │    │ • Response │
    │   result   │   │ • Risk factors                 │    │ • Metadata │
    │ • Analysis │   │ • Normal ranges                │    │            │
    │            │   │ • Prevention tips              │    │ Cost:      │
    │            │   │                                │    │ ~$0.01-0.1 │
    │            │   └─────────────────────────────────┘    │ per chat   │
    │            │                                          │            │
    └────────────┘                                          └────────────┘
```

---

## Intent Detection Flow

```
┌─ User Message: "Explain my diabetes risk"
│
├─ Pattern Matching Against Intents:
│  ├─ medical_prescription? ❌ No
│  ├─ risk_explanation? ✅ YES! (matches pattern)
│  ├─ preventive_measures? ❌ No
│  └─ ... (other intents)
│
└─ ROUTE: handle_risk_explanation()
   │
   ├─ Query Database
   │  └─ SELECT * FROM result WHERE user_id=1 ORDER BY timestamp DESC LIMIT 1
   │
   ├─ Analyze Result Data
   │  ├─ Probability: 68%
   │  ├─ Disease: Diabetes
   │  ├─ Glucose: 145 mg/dL (HIGH)
   │  ├─ BMI: 28.5 (ELEVATED)
   │  └─ Identify Contributing Factors
   │
   ├─ Generate Response
   │  └─ Create structured JSON with:
   │     ├─ type: "health_response"
   │     ├─ reply: "Your diabetes risk is 68%..."
   │     ├─ risk_level: "Moderate"
   │     ├─ contributing_factors: ["Glucose: 145", "BMI: 28.5", ...]
   │     ├─ preventive_actions: ["Exercise 150 mins/week", ...]
   │     ├─ suggested_actions: ["Download Report", ...]
   │     └─ disclaimer: "This is educational guidance..."
   │
   └─ Return to Frontend 🎉
```

---

## Safety Block Mechanism

```
┌─ User Message: "What medicine should I take?"
│
├─ Intent Detection Safety Check:
│  └─ Check against medical_prescription patterns
│     ├─ "prescribe" ✅ MATCH!
│     ├─ "medicine" ✅ MATCH!
│     ├─ "should take" ✅ MATCH!
│     └─ All 3 patterns match = PRESCRIPTION REQUEST
│
└─ BLOCK: handle_medical_prescription_block()
   │
   ├─ Never reaches OpenAI ✓
   ├─ Never reaches database ✓
   │
   └─ Return Safety Response:
      {
        "type": "safety_block",
        "reply": "⚠️ Safety Notice: I cannot provide medication...",
        "suggested_actions": [
          "Explain my risk",
          "Prevention tips",
          "Health information"
        ]
      }
```

---

## Response Type Decision Tree

```
                    User Message
                         │
                         ▼
                  Intent Detection
                    │    │    │    │    │    │
        ┌───────────┘    │    │    │    │    └────────────────┐
        │                │    │    │    │                     │
        ▼                ▼    ▼    ▼    ▼                     ▼
    medical_      risk_      prev_    nav_     health_      general
    prescription  expla      meas     cat      education
        │         nation           ion          │             │
        ▼         │                │            │             │
     BLOCK        ▼                ▼            ▼             ▼
        │       DB QUERY      KNOWLEDGE     KNOWLEDGE      OpenAI
        └──────►ANALYSIS        BASE         BASE           API
               │                │            │             │
               ├────────────────┼────────────┴─────────────┤
               │                │                          │
               ├────► safety_block ◄─────────────────────┘
               │      OR
               ├──────► health_response ◄────────────────┐
               │                                         │
               │      + contributing_factors             │
               │      + preventive_actions               │
               │      + suggested_actions                │
               │      + disclaimer                       │
               │
               ├──────► navigation ◄──────────────────────┤
               │        (route redirect)
               │
               └──────► ai_response
                        (from OpenAI)
```

---

## Request/Response Lifecycle

```
FRONTEND                 API ENDPOINT              CHATBOT SERVICE          EXTERNAL
(Browser)               (Flask Route)              (Chatbot Class)           SERVICES
   │                        │                          │                       │
   │─ User types ────────────►                         │                       │
   │   message              │                          │                       │
   │                        │               ┌──────────┴──────────┐            │
   │                        └──────────────►│ Detect Intent       │            │
   │                                        │ Pattern Matching    │            │
   │                                        └──────────┬──────────┘            │
   │                                                   │                       │
   │                                                   ├──────────────┐        │
   │                        ┌─────────────────────────┘              │        │
   │                        │ Is it prescription request?            │        │
   │                        │ YES ──────► BLOCK IMMEDIATELY ✓        │        │
   │                        │ NO  ──────► Continue Processing        │        │
   │                        │                                        │        │
   │                        │         ┌──────────────────────────────┘        │
   │                        │         │ Based on intent type:                 │
   │                        │         │                                       │
   │                  ┌─────┤ risk? ──┴──────► Query DB ──────────────────►database
   │                  │     │ prevent?       Analyze Result                  query
   │                  │     │ navigate? ─────► Route Mapping                 │
   │                  │     │ educate? ──────► Knowledge Base                │
   │                  │     │ general? ──────► OpenAI Request ──────────────►OpenAI
   │                  │     │                                     │          API
   │                  │     │                                     │          │
   │                  ├─────┴─────────────────────────────────────┼──────────┐
   │                  │ Response received                         │
   │                  │                                           │
   │  ◄──────────────┴─────────────────────────────────────────┘
   │ JSON Response with:
   │ - type (health_response, navigation, etc.)
   │ - reply (text content)
   │ - suggested_actions
   │ - user_context
   │ - timestamp
   │
   ├─ JavaScript processes response
   │  ├─ Format markdown
   │  ├─ Add to message history
   │  ├─ Show suggested action buttons
   │  └─ Handle navigation if needed
   │
   └─ Display in Chat Widget ✨
```

---

## Data Models

```
┌────────────────────────┐
│       User (DB)        │
├────────────────────────┤
│ • id (PK)              │
│ • username (UNIQUE)    │
│ • email (UNIQUE)       │
│ • password (hashed)    │
└───────────┬────────────┘
            │ 1:N
            ▼
┌────────────────────────────────────────┐
│        Result (DB)                     │
├────────────────────────────────────────┤
│ • id (PK)                              │
│ • user_id (FK → User)                  │
│ • disease (Diabetes/Heart Disease)     │
│ • prediction (Yes/No)                  │
│ • probability (0-100, %)               │
│ • timestamp                            │
│                                        │
│ Diabetes Fields:                       │
│ • glucose (mg/dL) ◄──────┐            │
│ • bmi                    │ Used by     │
│ • pregnancies            │ chatbot to  │
│ • age                    │ extract     │
│ • ... (7 total)          │ contributing
│                          │ factors     │
│ Heart Disease Fields:                  │
│ • trestbps (BP)          │            │
│ • chol (Cholesterol)  ◄──┘            │
│ • age                                  │
│ • ... (11 total)                       │
└────────────────────────────────────────┘

╔════════════════════════════════════════╗
║ Knowledge Base (In Memory Dictionary)  ║
╠════════════════════════════════════════╣
║                                        ║
║ {                                      ║
║   "diabetes": {                        ║
║     "definition": "...",               ║
║     "risk_factors": [                  ║
║       "High glucose levels",           ║
║       "Elevated BMI",                  ║
║       ...                              ║
║     ],                                 ║
║     "normal_ranges": {                 ║
║       "fasting_glucose": "70-100",     ║
║       ...                              ║
║     },                                 ║
║     "prevention_tips": [               ║
║       "Maintain healthy BMI",          ║
║       ...                              ║
║     ]                                  ║
║   },                                   ║
║   "heart_disease": { ... }             ║
║ }                                      ║
║                                        ║
╚════════════════════════════════════════╝
```

---

## Frontend Widget Architecture

```
┌─────────────────────┐
│  base.html (Main)   │
│                     │
│  Contains meta tag: │
│  <meta name="user-id"
│   content="{{ session['user_id'] }}">
│                     │
│  Includes:          │
│  {% include         │
│   'chatbot.html' %}│
└────────┬────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│       chatbot.html (Widget)          │
│                                      │
│ Structure:                           │
│ ├─ Container <div>                  │
│ ├─ Header (title + close button)    │
│ ├─ Messages area (scrollable)       │
│ ├─ Suggestions area                 │
│ ├─ Input area (text + send button)  │
│ ├─ Disclaimer footer                │
│ └─ Toggle button                    │
│                                      │
│ Styling:                             │
│ ├─ CSS Grid layout                  │
│ ├─ Flexbox positioning              │
│ ├─ Responsive breakpoints           │
│ ├─ Animations (slide-in, bounce)    │
│ └─ Gradient backgrounds             │
│                                      │
│ Interactivity:                       │
│ ├─ toggleChatbot()                  │
│ ├─ sendChatbotMessage()             │
│ ├─ loadChatbotSuggestions()         │
│ ├─ formatChatbotResponse()          │
│ └─ Event listeners (Enter key, etc) │
│                                      │
└──────────────────────────────────────┘
```

---

## Configuration Flow

```
┌─────────────────────────────┐
│      .env File (Secret)     │
│  (Never commit to Git!)     │
├─────────────────────────────┤
│ OPENAI_API_KEY=sk-...       │
│ FLASK_SECRET_KEY=...        │
│ DATABASE_URL=sqlite://...   │
│ OPENAI_MODEL=gpt-4o-mini   │
│ OPENAI_TEMPERATURE=0.7      │
│ LOG_LEVEL=INFO              │
└──────────┬──────────────────┘
           │
           ▼ (python-dotenv)
┌──────────────────────────────────┐
│   Python Environment Variables   │
│   (os.getenv('OPENAI_API_KEY'))  │
└──────────┬───────────────────────┘
           │
           ├─► chatbot_service.py
           │   • Sets OpenAI client
           │   • Configures model
           │   • Sets temperature
           │
           ├─► app/__init__.py
           │   • Sets SECRET_KEY
           │   • Sets DATABASE_URL
           │
           └─► routes.py
               • Uses for logging config
               • Uses for environment checks
```

---

## Error Handling Flow

```
┌─ Request arrives
│
├─ Validation Check
│  ├─ Message empty? ❌ Return 400 "Provide a message"
│  ├─ User not auth? ❌ Return 401 "Not authenticated"
│  └─ All valid? ✓ Continue
│
├─ Intent Detection
│  └─ Successfully identifies intent
│
├─ Handler Execution
│  ├─ Try {
│  │   └─ Execute handler logic
│  │
│  └─ Catch Exception {
│      └─ Return 500 "An error occurred"
│     }
│
├─ Response Formatting
│  ├─ Add metadata (user_context, timestamp)
│  ├─ Include disclaimers
│  └─ Add suggested_actions
│
└─ Return to Frontend
   ├─ Status 200 + JSON
   └─ Frontend displays/handles
```

---

## Deployment Architecture

```
DEVELOPMENT                STAGING              PRODUCTION
(localhost:5000)          (staging server)     (aws/azure/gcp)
     │                         │                    │
     ├─ .env.example           │                    │
     │ (copy locally)           │                    │
     │                          │                    │
     ├─ python run.py           │                    │
     │ (Flask dev server)       │                    │
     │                          │                    │
     └─ SQLite DB               ├─ Environment      ├─ Environment
        (local)                 │   variables       │   variables
                                │   (secure)        │   (secure - sealed)
                                │                   │
                                ├─ PostgreSQL       ├─ Managed DB
                                │   or MySQL        │   (AWS RDS, etc.)
                                │                   │
                                ├─ Gunicorn         ├─ Loadbalancer
                                │   + Nginx         │   Gunicorn workers
                                │                   │
                                ├─ Rate limiting    ├─ CDN
                                │   (basic)         │   SSL/TLS
                                │                   │   Rate limiting
                                ├─ Monitoring       │   Monitoring
                                │   (logs)          │   (full stack)
                                │                   │
                                ├─ Secrets          ├─ Secrets
                                │   (env vars)      │   (Vault/Key Mgr)
                                │                   │
                                └─ Testing          └─ Alerts
                                   (CI/CD)             Logging
                                                       Backups
```

---

## Cost Estimation

```
OpenAI API Usage (per month):

┌─ Input Tokens (0.075 ¢ per 1M)
│  ├─ Average message: 50-100 tokens
│  ├─ System prompt: ~200 tokens
│  └─ Context: ~500 tokens per request
│     = ~800 tokens per general chat call
│
└─ Output Tokens (0.30 ¢ per 1M)
   ├─ Average response: 200-500 tokens
   └─ = ~300 tokens per general chat call

Total per call: ~1,100 tokens = ~0.0001 per call

Scenario: 100 users × 10 calls/month
= 1,000 calls/month
= 1,100,000 tokens
= ~$0.33/month ✓ Very cheap!

Healthcare chats (DB lookups): FREE ✓
Navigation: FREE ✓
Health education (knowledge base): FREE ✓
Only general chat costs money.
```

---

## Security Model

```
┌─────────────────────────────────────────────────────┐
│ Authentication Layer                                │
│ ├─ Flask session (cookie-based)                    │
│ ├─ User login required                             │
│ └─ Session ID in request validation                │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ Authorization Layer                                 │
│ ├─ User only accesses own data                     │
│ ├─ Chat suggestions checks user_id match           │
│ └─ Database queries filtered by user_id            │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ Input Validation Layer                              │
│ ├─ Message length limits                           │
│ ├─ User ID format validation                       │
│ ├─ Regex sanitization                              │
│ └─ Exception handling everywhere                   │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ Data Protection Layer                               │
│ ├─ SQLAlchemy ORM (prevents SQL injection)         │
│ ├─ Flask auto-escapes templates (prevents XSS)    │
│ ├─ HTTPS (recommended for production)              │
│ ├─ Environment variables for secrets               │
│ └─ No sensitive data in logs                       │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ AI Safety Layer                                     │
│ ├─ Intent detection blocks prescriptions           │
│ ├─ System prompt constrains OpenAI behavior        │
│ ├─ Disclaimers added to all responses              │
│ └─ Healthcare logic never provides diagnoses       │
└─────────────────────────────────────────────────────┘
```

---

## Key Files Reference

```
Core Chatbot Service:
└─ app/chatbot_service.py (NEW, 600+ lines)
   ├─ HealthcareChatbot class
   ├─ Intent detection (6 types)
   ├─ Risk explanation handler
   ├─ Preventive measures handler
   ├─ Health education handler
   ├─ Navigation handler
   ├─ Safety block (prescription blocking)
   ├─ OpenAI fallback integration
   ├─ Health knowledge base (Diabetes + Heart)
   └─ Context awareness utilities

API Endpoints:
└─ app/routes.py (UPDATED)
   ├─ POST /api/health-chat (NEW)
   ├─ POST /api/general-chat (NEW)
   └─ GET /api/chat-suggestions/{user_id} (NEW)

Frontend Widget:
├─ app/templates/chatbot.html (NEW)
│  ├─ HTML structure
│  ├─ CSS styling
│  └─ JavaScript interactivity
│
└─ app/templates/base.html (UPDATED)
   ├─ Meta tag for user-id
   └─ Chatbot widget inclusion

Documentation:
├─ CHATBOT_INTEGRATION_GUIDE.md (500+ lines)
├─ CHATBOT_QUICK_START.md (300+ lines)
├─ API_REFERENCE.md (400+ lines)
├─ INTEGRATION_SUMMARY.md (comprehensive)
└─ SYSTEM_ARCHITECTURE.md (this file)

Testing:
├─ test_chatbot.py (500+ lines, 12 tests)
└─ .env.example (configuration template)
```

---

## Quick Integration Checklist

- [ ] Install openai>=1.0.0
- [ ] Set OPENAI_API_KEY in .env
- [ ] Run app
- [ ] See 💬 button in bottom-right
- [ ] Test "Explain my risk" prompt
- [ ] Test "What is diabetes?" prompt
- [ ] Test "Go to dashboard" command
- [ ] Try "Prescribe medicine" (should block)
- [ ] Run test_chatbot.py
- [ ] Review provided documentation
- [ ] Deploy to production with environment secrets

---

**Architecture Documentation Complete ✅**

For more details, see:
- CHATBOT_INTEGRATION_GUIDE.md (full system guide)
- API_REFERENCE.md (endpoint documentation)
- CHATBOT_QUICK_START.md (setup instructions)
