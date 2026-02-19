# 🏥 Healthcare AI Chatbot Integration - Complete Documentation

## 📋 Overview

The Healthcare AI Chatbot is a domain-specific AI assistant integrated into the Smart Healthcare Early Risk Prediction System. It provides:

- **Risk Explanation**: Understands patient risk scores and explains them clearly
- **Preventive Guidance**: Offers actionable prevention strategies
- **Health Education**: Answers disease awareness questions
- **Dashboard Navigation**: Supports command-based navigation
- **Safe Medical Boundaries**: Refuses dangerous medical prescriptions
- **OpenAI Fallback**: Uses GPT-4o-mini for general knowledge questions

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The following new packages are required:
- `openai>=1.0.0`

### 2. Configure OpenAI API

Create or update your `.env` file:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
FLASK_SECRET_KEY=your-flask-secret-key
DATABASE_URL=sqlite:///users.db
```

**Get your API Key:**
1. Visit https://platform.openai.com/account/api-keys
2. Create a new API key
3. Add it to your `.env` file

### 3. Run the Application

```bash
python run.py
```

The chatbot widget will appear in the bottom-right corner of your dashboard.

---

## 🧠 How the Chatbot Works

### Intent Detection Flow

```
User Message
    ↓
Intent Detection (Pattern Matching)
    ├── Medical Prescription → Block (Safety)
    ├── Risk Explanation → Fetch Database + Explain
    ├── Preventive Measures → Health Knowledge Base
    ├── Navigation → Route Redirection
    ├── Health Education → Knowledge Base
    └── General → OpenAI GPT-4o-mini
```

### Intent Types & Examples

#### 1. **Risk Explanation** (Healthcare Logic)
**User says:** "Explain my diabetes risk" / "Why is my score high?" / "Show my last result"

**Chatbot:**
- Fetches latest prediction from database
- Extracts contributing factors (glucose, BMI, age, etc.)
- Calculates risk level (Low/Moderate/High)
- Provides structured explanation with preventive suggestions
- Adds medical disclaimer

**Response Structure:**
```json
{
  "type": "health_response",
  "reply": "Your diabetes risk is 68%, categorized as moderate risk...",
  "risk_level": "Moderate",
  "probability": 68,
  "contributing_factors": [
    "Elevated glucose level (145 mg/dL)",
    "High BMI (28.5)"
  ],
  "preventive_actions": [
    "Exercise 150 mins per week",
    "Monitor weight and BMI",
    "Reduce sugar intake"
  ],
  "suggested_actions": [
    "Download Report",
    "Schedule Consultation"
  ]
}
```

#### 2. **Preventive Measures** (Healthcare Logic)
**User says:** "How can I improve my score?" / "Prevention tips for heart disease"

**Chatbot:**
- Identifies disease type from recent assessment or explicit mention
- Provides disease-specific prevention strategies
- Adapts guidance based on user's risk level
- Includes diet, exercise, lifestyle, and screening recommendations

**Example Response:**
```
## Prevention for Diabetes

**Definition:** Diabetes is a chronic condition...

**Key Risk Factors:**
• High glucose levels
• Elevated BMI
• Family history
...

**Normal Healthy Ranges:**
• Fasting Glucose: 70-100 mg/dL
• HbA1c: < 5.7%

**Prevention Tips:**
• Maintain healthy BMI (18.5-24.9)
• Exercise 150 minutes per week
• Eat balanced diet with whole grains
...
```

#### 3. **Navigation Commands** (Action Redirect)
**User says:** "Go to dashboard" / "Start new assessment" / "Download my report"

**Chatbot:**
Returns navigation action (not a text response):
```json
{
  "type": "navigation",
  "action": "redirect",
  "route": "/dashboard",
  "message": "Redirecting to dashboard..."
}
```

#### 4. **Health Education** (Knowledge Base)
**User says:** "What is diabetes?" / "What causes high cholesterol?" / "What's normal blood pressure?"

**Chatbot:**
- Uses built-in healthcare knowledge base
- Provides definitions, risk factors, normal ranges
- Falls back to OpenAI for advanced questions

#### 5. **Medical Prescription Block** (Safety Guardrail)
**User says:** "What medicine should I take?" / "Prescribe medication for diabetes"

**Chatbot:**
```json
{
  "type": "safety_block",
  "reply": "⚠️ Safety Notice: I cannot provide medication prescriptions...",
  "suggested_actions": ["Explain my risk", "Prevention tips", "Health information"]
}
```

#### 6. **General Knowledge** (OpenAI Fallback)
**User says:** "What is machine learning?" / "Who is the Prime Minister?" / "Explain quantum physics"

**Chatbot:**
- Routes to OpenAI GPT-4o-mini
- Uses healthcare-aware system prompt
- Refuses to provide medical prescriptions even for general questions
- Includes medical disclaimer

---

## 🔌 API Endpoints

### 1. Health Chat (Healthcare-Specific)
```http
POST /api/health-chat
Content-Type: application/json

{
  "message": "Explain my diabetes risk",
  "user_id": 1
}
```

**Response:**
```json
{
  "type": "health_response",
  "reply": "Your diabetes risk is...",
  "risk_level": "Moderate",
  "probability": 68,
  "contributing_factors": [...],
  "preventive_actions": [...],
  "suggested_actions": [...],
  "disclaimer": "This is educational guidance, not medical advice.",
  "user_context": {
    "username": "john_doe",
    "last_assessment": "2026-02-19 10:30:00",
    "last_disease": "Diabetes",
    "last_probability": 68
  },
  "timestamp": "2026-02-19T10:35:00"
}
```

### 2. General Chat (OpenAI Fallback)
```http
POST /api/general-chat
Content-Type: application/json

{
  "message": "What is machine learning?",
  "user_id": 1  (optional)
}
```

**Response:**
```json
{
  "type": "ai_response",
  "reply": "Machine learning is...",
  "source": "OpenAI GPT-4o-mini",
  "disclaimer": "This is educational guidance, not medical advice.",
  "user_context": {...},
  "timestamp": "2026-02-19T10:35:00"
}
```

### 3. Chat Suggestions (Get Prompt Ideas)
```http
GET /api/chat-suggestions/{user_id}
```

**Response:**
```json
{
  "suggestions": [
    "Tell me about my Diabetes risk",
    "How to prevent Diabetes?",
    "Explain my last result",
    "What causes high diabetes risk?"
  ],
  "context": {
    "username": "john_doe",
    "last_assessment": "2026-02-19 10:30:00",
    "last_disease": "Diabetes",
    "last_probability": 68
  }
}
```

---

## 🛡️ Safety Guardrails

### What the Chatbot WILL DO:
✅ Explain risk scores with contributing factors  
✅ Provide prevention strategies  
✅ Educate about diseases  
✅ Navigate the application  
✅ Answer general knowledge questions  
✅ Direct users to healthcare professionals  

### What the Chatbot WILL NOT DO:
❌ Prescribe medications  
❌ Suggest dosages  
❌ Provide medical diagnoses  
❌ Replace doctor consultations  
❌ Make guarantees about outcomes  

### Safety Implementation:

1. **Intent Detection**: Detects prescription requests using regex patterns
```python
medical_prescription_patterns = [
    r"(prescribe|medicine|drug|medication)",
    r"(what|which).*(medicine|drug|medication).*(should|take)",
    r"(dosage|dose|how much)"
]
```

2. **System Prompt Control**: OpenAI requests include safety constraints
```python
system_prompt = """You are an AI healthcare assistant...
Do NOT provide diagnosis or medication advice.
Do NOT prescribe medications or suggest dosages.
Always add disclaimers: 'This is educational guidance, not medical advice'"""
```

3. **Disclaimers**: Every response includes appropriate disclaimers
```json
"disclaimer": "This is educational guidance, not medical advice. Consult a healthcare professional."
```

4. **Fallback Routing**: Medical questions route to healthcare logic, not general AI

---

## 🗂️ Project Structure

```
app/
├── chatbot_service.py          # ✨ NEW: Core chatbot logic
├── models.py                   # Database models (unchanged)
├── routes.py                   # Updated with /api/health-chat & /api/general-chat
├── services.py                 # (unchanged)
├── templates/
│   ├── base.html              # Updated with chatbot widget
│   └── chatbot.html           # ✨ NEW: Chatbot UI component
requirements.txt               # Updated with openai>=1.0.0
```

---

## 📊 Database Integration

The chatbot accesses:

### User Model
```python
class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True)
    email = Column(String(150), unique=True)
```

### Result Model
```python
class Result(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    disease = Column(String(50))
    prediction = Column(String(10))
    probability = Column(Float)          # Risk percentage
    disease_selected = Column(String(50)) # "Diabetes" or "Heart Disease"
    timestamp = Column(DateTime)
    
    # Diabetes fields
    glucose = Column(Float)
    bmi = Column(Float)
    # ... more fields
    
    # Heart fields
    trestbps = Column(Integer)           # Blood pressure
    chol = Column(Integer)               # Cholesterol
    # ... more fields
```

The chatbot extracts contributing factors from these fields to explain risk.

---

## 🎨 Frontend Integration

### Auto-Included Features:
1. **Chatbot Widget**: Appears in bottom-right corner (logged-in users only)
2. **Toggle Button**: Purple gradient button with chat icon
3. **Suggested Prompts**: Auto-loaded based on user's latest assessment
4. **Responsive Design**: Works on mobile and desktop
5. **Markdown Support**: Formats responses with bold, lists, headers

### Customization:

To modify styling, edit `app/templates/chatbot.html` CSS section:
```css
.chatbot-container {
    /* Position, size, colors */
}
```

---

## 🔧 Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=sk-your-key

# Optional (defaults provided)
FLASK_SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///users.db
FLASK_ENV=development
```

### Chatbot Behavior Customization

Edit `app/chatbot_service.py`:

1. **Adjust Risk Levels**:
```python
def _calculate_risk_level(self, probability: float) -> str:
    if probability >= 70:      # Change thresholds
        return "High"
    elif probability >= 40:
        return "Moderate"
```

2. **Add New Intent Patterns**:
```python
self.healthcare_intents = {
    "new_intent": [
        r"(pattern1|pattern2).*keywords",
    ]
}
```

3. **Update Health Knowledge Base**:
```python
self.health_knowledge = {
    "diabetes": {
        "definition": "...",
        "risk_factors": [...],
        "prevention_tips": [...]
    }
}
```

4. **Modify OpenAI Model**:
```python
response = self.openai_client.chat.completions.create(
    model="gpt-4o-mini",  # Change model here
    temperature=0.7       # Adjust randomness
)
```

---

## 📝 Usage Examples

### Example 1: User Gets Risk Explanation
```
User: "Explain my diabetes risk"
│
├─ Intent: risk_explanation
├─ Fetch: Latest diabetes result (probability: 68%)
├─ Extract: glucose=145, BMI=28.5
├─ Response: "Your diabetes risk is 68%, categorized as moderate..."
└─ Actions: ["Download Report", "Schedule Consultation"]
```

### Example 2: User Asks About Prevention
```
User: "How can I lower my diabetes risk?"
│
├─ Intent: preventive_measures
├─ Query: Latest assessment type (Diabetes)
├─ Risk Level: Moderate (68%)
├─ Response: Diet tips + Exercise + Lifestyle + Screening
└─ Actions: ["Download Prevention Guide", "Schedule Consultation"]
```

### Example 3: User Tries to Get Prescription
```
User: "What medicine should I take?"
│
├─ Intent: medical_prescription (DETECTED)
├─ Response: "⚠️ Safety Notice: I cannot provide prescriptions..."
└─ Actions: ["Explain my risk", "Prevention tips", "Health info"]
```

### Example 4: User Asks General Question
```
User: "What is machine learning?"
│
├─ Intent: general (no healthcare match)
├─ Route: OpenAI General Chat
├─ System Prompt: Healthcare-aware prompt added
├─ Response: "Machine learning is... (educational guidance)"
└─ Disclaimer: "This is educational guidance, not medical advice."
```

---

## 🐛 Troubleshooting

### Issue: Chatbot doesn't appear
**Solution:** 
- Ensure user is logged in (chatbot only shows for authenticated users)
- Check meta tag in base.html includes user-id
- Verify JavaScript in chatbot.html is loaded

### Issue: OpenAI responses fail
**Solution:**
- Verify OPENAI_API_KEY is set in .env
- Check API key is valid: https://platform.openai.com/account/api-keys
- Ensure account has sufficient credits
- Check network connectivity

### Issue: Risk explanation shows no factors
**Solution:**
- Database may lack detailed field values
- Chatbot shows "See detailed assessment for factors"
- This is expected for minimal data

### Issue: Chatbot routes wrong intent
**Solution:**
- Check intent patterns in `chatbot_service.py`
- Patterns use regex - may need adjustment for user language
- Manual pattern testing: `import re; re.search(pattern, message)`

---

## 📈 Performance Optimization

### Caching Suggestions
```python
# Cache user suggestions to reduce API calls
last_suggestions_cache = {}  # Add to chatbot_service.py
```

### Rate Limiting (Optional)
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: session.get('user_id'))
@main.route('/api/health-chat', methods=['POST'])
@limiter.limit("30 per minute")
def health_chat():
    # ...
```

### Batch Processing
```python
# For multiple users' suggestions
def batch_load_suggestions(user_ids):
    contexts = [get_conversation_context(uid) for uid in user_ids]
    return [generate_suggestions(ctx) for ctx in contexts]
```

---

## 🚀 Deployment

### Production Checklist:
- [ ] OPENAI_API_KEY set in production environment
- [ ] FLASK_SECRET_KEY changed to strong random key
- [ ] DATABASE_URL points to production database
- [ ] Error logging configured
- [ ] Rate limiting enabled
- [ ] HTTPS enabled
- [ ] Chatbot disclaimer visible to all users

### Docker Deployment:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
CMD ["python", "run.py"]
```

---

## 📚 Healthcare Knowledge Base

The chatbot includes built-in knowledge for:

### Diabetes
- Definition and pathophysiology
- Risk factors (glucose, BMI, family history, age, lifestyle)
- Normal ranges (fasting glucose, random glucose, HbA1c)
- Prevention tips (diet, exercise, monitoring, stress management)

### Heart Disease
- Definition and conditions covered
- Risk factors (BP, cholesterol, smoking, diabetes, obesity, stress)
- Normal ranges (blood pressure, cholesterol, heart rate)
- Prevention tips (exercise, diet, stress management, screening)

**Extending Knowledge:**
```python
self.health_knowledge["new_disease"] = {
    "definition": "...",
    "risk_factors": [...],
    "normal_ranges": {...},
    "prevention_tips": [...]
}
```

---

## 🔐 Security Considerations

1. **API Authentication**: All endpoints require user session or user_id
2. **SQL Injection**: Uses SQLAlchemy ORM (parameterized queries)
3. **XSS Protection**: Flask auto-escapes template variables
4. **Input Validation**: Message length limited by frontend
5. **Rate Limiting**: Optional - recommended for production
6. **API Key Security**: Never expose OPENAI_API_KEY in code/logs

---

## 🎓 Medical Compliance

### HIPAA-Like Considerations:
- ✅ User data accessed only by authenticated user
- ✅ Responses include medical disclaimers
- ✅ No diagnostic claims made
- ✅ No medication prescriptions provided
- ⚠️ Logging may contain health data (secure logs)
- ⚠️ OpenAI processes messages (review OpenAI privacy)

### For Production HIPAA Compliance:
1. Use private deployment of language model
2. Implement audit logging
3. Add data encryption at rest
4. Use dedicated secure database
5. Obtain legal review from healthcare attorney

---

## 🤝 Integration with Existing System

The chatbot integrates seamlessly with:
- **Prediction Models**: Uses latest Result from database
- **User Sessions**: Accesses via Flask session
- **Frontend**: Embedded widget in base template
- **Database**: Queries User and Result models
- **API**: New endpoints without breaking existing ones

**No changes required to:**
- Prediction logic
- User authentication
- Database schema
- Existing routes

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review chatbot logs: `app.logger.debug(message)`
3. Test endpoints with curl/Postman
4. Verify OpenAI API access
5. Check browser console for JavaScript errors

---

## 📄 License & Attribution

- Healthcare AI Chatbot: Integrated System (2026)
- OpenAI API: https://openai.com/
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://sqlalchemy.org/

---

**Last Updated:** February 19, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅
