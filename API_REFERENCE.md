# 🏥 Healthcare Chatbot API Reference

## API Overview

The Healthcare Chatbot provides 3 main endpoints for integrating conversational AI into your healthcare application.

---

## Endpoint 1: Health Chat (Healthcare-Specific)

### Route
```
POST /api/health-chat
```

### Purpose
Route healthcare-specific questions to domain logic. Handles risk explanations, preventive measures, navigation, and health education.

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "message": "Explain my diabetes risk",
  "user_id": 1
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | User's question/command |
| `user_id` | integer | Yes | Authenticated user ID |

### Response Formats

#### A. Health Response (Risk/Education)
```json
{
  "type": "health_response",
  "reply": "Your diabetes risk is 68%, categorized as moderate risk...",
  "risk_level": "Moderate",
  "probability": 68,
  "risk_percentage": "68%",
  "contributing_factors": [
    "Elevated glucose level (145 mg/dL)",
    "High BMI (28.5)"
  ],
  "preventive_actions": [
    "Exercise 150 mins per week",
    "Monitor weight and BMI",
    "Reduce sugar intake",
    "Schedule doctor visit"
  ],
  "suggested_actions": [
    "Download Report",
    "Schedule Consultation"
  ],
  "disclaimer": "This is educational guidance, not medical advice. Consult a healthcare professional.",
  "user_context": {
    "username": "john_doe",
    "last_assessment": "2026-02-19 10:30:00",
    "last_disease": "Diabetes",
    "last_probability": 68
  },
  "timestamp": "2026-02-19T10:35:00Z"
}
```

#### B. Navigation Response
```json
{
  "type": "navigation",
  "action": "redirect",
  "route": "/dashboard",
  "message": "Redirecting to dashboard..."
}
```

**Possible Routes:**
| Command | Route |
|---------|-------|
| "Go to dashboard" | `/dashboard` |
| "Open reports" | `/dashboard` |
| "Start new assessment" | `/select-disease` |
| "Download report" | `/dashboard` |

#### C. Safety Block (Prescription Request)
```json
{
  "type": "safety_block",
  "reply": "⚠️ Safety Notice: I cannot provide medication prescriptions, dosages, or drug recommendations.\n\nPlease consult a licensed healthcare professional or pharmacist for medication guidance.\n\nI can help with:\n• Explaining your risk scores\n• Prevention strategies\n• Health education\n• Navigation assistance",
  "suggested_actions": [
    "Explain my risk",
    "Prevention tips",
    "Health information"
  ]
}
```

#### D. Error Response
```json
{
  "type": "error",
  "reply": "I don't see any previous assessments. Please complete a health assessment first.",
  "suggested_actions": [
    "Start New Assessment"
  ]
}
```

### Status Codes
| Code | Meaning |
|------|---------|
| `200` | Success - Response returned |
| `400` | Bad Request - Missing/invalid parameters |
| `401` | Unauthorized - User not authenticated |
| `500` | Server Error - Internal error |

### Example Requests

#### Request 1: Risk Explanation
```bash
curl -X POST http://localhost:5000/api/health-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Why is my diabetes score high?",
    "user_id": 1
  }'
```

**Response:**
```json
{
  "type": "health_response",
  "reply": "Your elevated glucose level (145 mg/dL) and BMI (28.5) are contributing to your 68% diabetes risk score...",
  "risk_level": "Moderate",
  "probability": 68,
  ...
}
```

#### Request 2: Preventive Measures
```bash
curl -X POST http://localhost:5000/api/health-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How can I improve my heart health?",
    "user_id": 1
  }'
```

**Response:**
```json
{
  "type": "health_response",
  "reply": "## Prevention for Heart Disease\n\n**Key Risk Factors:**\n• High blood pressure\n• High cholesterol\n...",
  "preventive_actions": [
    "Reduce sodium intake",
    "Exercise regularly",
    "Manage stress",
    "Monitor cholesterol"
  ],
  ...
}
```

#### Request 3: Navigation
```bash
curl -X POST http://localhost:5000/api/health-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Open the dashboard",
    "user_id": 1
  }'
```

**Response:**
```json
{
  "type": "navigation",
  "action": "redirect",
  "route": "/dashboard",
  "message": "Redirecting to dashboard..."
}
```

#### Request 4: Prescription Block
```bash
curl -X POST http://localhost:5000/api/health-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What medicine should I take?",
    "user_id": 1
  }'
```

**Response:**
```json
{
  "type": "safety_block",
  "reply": "⚠️ Safety Notice: I cannot provide medication prescriptions...",
  "suggested_actions": [
    "Explain my risk",
    "Prevention tips",
    "Health information"
  ]
}
```

---

## Endpoint 2: General Chat (OpenAI Fallback)

### Route
```
POST /api/general-chat
```

### Purpose
Route non-healthcare questions to OpenAI GPT-4o-mini with healthcare-aware system prompt.

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "message": "What is machine learning?",
  "user_id": 1
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | User's question |
| `user_id` | integer | No | Optional user ID (for context) |

### Response

```json
{
  "type": "ai_response",
  "reply": "Machine learning is a subset of artificial intelligence that...",
  "source": "OpenAI GPT-4o-mini",
  "disclaimer": "This is educational guidance, not medical advice.",
  "user_context": {
    "username": "john_doe",
    "last_assessment": "2026-02-19 10:30:00",
    "last_disease": "Diabetes",
    "last_probability": 68
  },
  "timestamp": "2026-02-19T10:35:00Z"
}
```

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"ai_response"` or `"error"` |
| `reply` | string | AI-generated response |
| `source` | string | Always `"OpenAI GPT-4o-mini"` |
| `disclaimer` | string | Medical disclaimer |
| `user_context` | object | User context (if user_id provided) |
| `timestamp` | string | ISO 8601 timestamp |

### Status Codes
| Code | Meaning |
|------|---------|
| `200` | Success |
| `400` | Bad Request |
| `500` | Server Error |

### Example Request

```bash
curl -X POST http://localhost:5000/api/general-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum physics",
    "user_id": 1
  }'
```

**Response:**
```json
{
  "type": "ai_response",
  "reply": "Quantum physics is the branch of physics that studies particles at the atomic and subatomic level...",
  "source": "OpenAI GPT-4o-mini",
  "disclaimer": "This is educational guidance, not medical advice.",
  "timestamp": "2026-02-19T10:35:00Z"
}
```

### Error Response (No API Key)

```json
{
  "type": "error",
  "reply": "OpenAI API is not configured. Please set OPENAI_API_KEY environment variable.",
  "suggested_actions": [
    "Try healthcare question",
    "Contact Support"
  ]
}
```

---

## Endpoint 3: Chat Suggestions

### Route
```
GET /api/chat-suggestions/{user_id}
```

### Purpose
Get suggested chat prompts based on user's latest assessment.

### Request

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | Path | User ID |

**Example:**
```bash
curl http://localhost:5000/api/chat-suggestions/1
```

### Response

```json
{
  "suggestions": [
    "Tell me about my Diabetes risk",
    "How to prevent Diabetes?",
    "Explain my last result",
    "What causes high diabetes risk?",
    "Prevention tips for diabetes"
  ],
  "context": {
    "username": "john_doe",
    "last_assessment": "2026-02-19 10:30:00",
    "last_disease": "Diabetes",
    "last_probability": 68
  }
}
```

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `suggestions` | array | List of suggested prompts |
| `context` | object | User's assessment context |
| `context.username` | string | User's username |
| `context.last_assessment` | string | Timestamp of last assessment |
| `context.last_disease` | string | Type of last assessment |
| `context.last_probability` | number | Risk percentage of last assessment |

### Status Codes
| Code | Meaning |
|------|---------|
| `200` | Success |
| `403` | Forbidden - Wrong user |
| `500` | Server Error |

### Error Response

```json
{
  "error": "Unauthorized"
}
```

---

## Intent Detection

The health chat endpoint automatically detects user intent and routes appropriately:

### Intent Types

#### 1. Risk Explanation
**Triggers:**
- "Explain my diabetes risk"
- "Why is my score high?"
- "Tell me my last result"
- "Show my heart disease probability"

**Response Type:** `health_response` with risk details

#### 2. Preventive Measures
**Triggers:**
- "How can I reduce my risk?"
- "How to prevent heart disease?"
- "What can I do to improve my score?"
- "Diet tips for diabetes"

**Response Type:** `health_response` with prevention strategies

#### 3. Navigation
**Triggers:**
- "Go to dashboard"
- "Open reports"
- "Start new assessment"
- "Download my report"

**Response Type:** `navigation` with route redirect

#### 4. Health Education
**Triggers:**
- "What is diabetes?"
- "Define heart disease"
- "What's normal blood pressure?"
- "What causes high cholesterol?"

**Response Type:** `health_response` with educational content

#### 5. Medical Prescription (Blocked)
**Triggers:**
- "What medicine should I take?"
- "Prescribe medication"
- "Dosage for diabetes"
- "What drug should I use?"

**Response Type:** `safety_block` (ALWAYS DECLINED)

#### 6. General Knowledge
**Triggers:**
- "What is machine learning?"
- "Who is the President?"
- "Explain quantum physics"
- Any non-healthcare question

**Response Type:** `ai_response` (OpenAI)

---

## Example Integration (Frontend)

### JavaScript/TypeScript

```typescript
// Health chat function
async function askHealthQuestion(message: string, userId: number) {
  const response = await fetch('/api/health-chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      user_id: userId
    })
  });

  const data = await response.json();

  // Handle different response types
  if (data.type === 'health_response') {
    displayHealthResponse(data);
  } else if (data.type === 'navigation') {
    window.location.href = data.route;
  } else if (data.type === 'safety_block') {
    displaySafetyNotice(data);
  } else if (data.type === 'error') {
    displayError(data);
  }
}

// General question function
async function askGeneralQuestion(message: string, userId?: number) {
  const response = await fetch('/api/general-chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      user_id: userId
    })
  });

  const data = await response.json();
  displayAIResponse(data);
}

// Load suggestions
async function loadSuggestions(userId: number) {
  const response = await fetch(`/api/chat-suggestions/${userId}`);
  const data = await response.json();
  displaySuggestions(data.suggestions);
}
```

### Python

```python
import requests

BASE_URL = "http://localhost:5000"

def ask_health_question(message, user_id):
    response = requests.post(
        f"{BASE_URL}/api/health-chat",
        json={
            "message": message,
            "user_id": user_id
        }
    )
    return response.json()

def ask_general_question(message, user_id=None):
    response = requests.post(
        f"{BASE_URL}/api/general-chat",
        json={
            "message": message,
            "user_id": user_id
        }
    )
    return response.json()

def get_suggestions(user_id):
    response = requests.get(
        f"{BASE_URL}/api/chat-suggestions/{user_id}"
    )
    return response.json()

# Usage
result = ask_health_question("Explain my diabetes risk", user_id=1)
print(result['reply'])
```

---

## Error Handling

All endpoints return standard error responses:

```json
{
  "type": "error",
  "reply": "Error message explaining what went wrong",
  "suggested_actions": [
    "Alternative action 1",
    "Alternative action 2"
  ]
}
```

### Common Errors

| Scenario | Status | Response |
|----------|--------|----------|
| Missing message | 400 | "Please provide a message" |
| Invalid user_id | 401 | "User not authenticated" |
| No assessment data | 200 | "No previous assessments found" |
| OpenAI API down | 200 | "AI service temporarily unavailable" |
| Server error | 500 | "An error occurred: ..." |

---

## Rate Limiting

Current: No rate limiting (optional - add for production)

Recommended limits:
- Health chat: 30 requests/minute per user
- General chat: 20 requests/minute per user
- Suggestions: 60 requests/minute per user

---

## Performance Metrics

**Response Times (Average):**
- Health chat (database hit): 200ms-500ms
- Health chat (knowledge base): 100ms-300ms
- General chat (OpenAI): 2-5 seconds
- Suggestions: 100ms-300ms

**Timeout Recommendations:**
- Health chat: 5 seconds
- General chat: 15 seconds
- Suggestions: 5 seconds

---

## Authentication

- All endpoints require authenticated user (session or user_id)
- User_id must be valid in database
- Session-based auth via Flask session cookie

---

## Next Steps

1. ✅ Review API reference
2. ✅ Test endpoints with curl/Postman
3. ✅ Integrate into frontend
4. ✅ Handle different response types
5. ✅ Add error handling
6. ✅ Monitor performance
7. ✅ Deploy to production

---

**API Version:** 1.0.0  
**Last Updated:** February 19, 2026  
**Status:** Production Ready ✅
