# UrbanCart AI — Intelligent Shopping Assistant

UrbanCart AI is a web-based AI shopping assistant chatbot built for the UrbanCart e-commerce store. It uses Google's Gemini AI to understand customer intent and handle product recommendations, order tracking, returns, FAQs, and human support escalation — with every conversation automatically logged to a CRM (Google Sheets) and escalations triggering a real-time email alert.

## Features

- **AI Intent Detection** — Understands customer messages and routes them to the correct workflow (recommendation, order tracking, return, human handoff, or general FAQ) using Gemini.
- **Product Recommendations** — Suggests products based on category, budget, brand, and stated preferences.
- **Order Tracking** — Verifies the customer via Order ID + email, then returns live order status, tracking number, and estimated delivery.
- **Returns Handling** — Checks return eligibility and explains the return process for a given order.
- **Human Handoff** — Lets a customer escalate to a human support agent at any point in the conversation.
- **CRM Logging** — Every conversation (regardless of intent) is automatically logged to a connected Google Sheet via an n8n webhook, capturing customer name, email, summary, order number, support category, AI resolution status, and escalation status.
- **Automated Escalation Emails** — When a conversation is flagged as escalated, an n8n workflow automatically sends a Gmail notification to the support team in real time.
- **Analytics Dashboard** — A standalone dashboard page (`frontend/analytics.html`) presenting a UI concept for conversation volume, support category breakdown, AI resolution rate, and recent activity.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, vanilla JavaScript |
| Backend | Python, Flask |
| AI | Google Gemini API |
| Automation / CRM | n8n (webhook → Google Sheets → Gmail) |
| Data storage | Google Sheets (CRM log), local JSON (product/order/FAQ data) |

## Project Structure

```
BranDive-AI/
├── backend/
│   ├── app.py                  # Flask app entry point
│   ├── routes/
│   │   └── chat.py             # Main /chat endpoint — intent routing + CRM logging
│   ├── services/
│   │   ├── gemini_service.py   # Gemini AI calls (chat, recommend, explain order/return)
│   │   ├── intent_service.py   # Intent detection
│   │   ├── entity_service.py   # Entity extraction (order ID, email, budget, etc.)
│   │   ├── order_service.py    # Order lookup
│   │   ├── return_service.py   # Return eligibility checks
│   │   ├── recommendation_service.py
│   │   ├── crm_service.py      # Sends conversation data to n8n webhook
│   │   ├── escalation_service.py
│   │   ├── faq_service.py
│   │   ├── knowledge_service.py
│   │   ├── preference_service.py
│   │   └── product_service.py
│   ├── data/                   # Sample product, order, customer, FAQ, return data (JSON)
│   ├── prompts/                # System + intent prompts for Gemini
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Chatbot UI
│   ├── analytics.html          # Analytics dashboard (UI concept, static sample data)
│   ├── css/
│   │   ├── style.css
│   │   └── analytics.css
│   └── js/
│       └── app.js
└── README.md
```

## How It Works

1. Customer sends a message through the chat widget on `frontend/index.html`.
2. The Flask backend (`/chat` route) detects the intent using Gemini.
3. Based on intent, the relevant service handles the request (order lookup, return check, recommendation, or handoff) and Gemini generates a natural-language reply.
4. Every conversation outcome is sent to an **n8n webhook**, which appends a row to a Google Sheet acting as the CRM log.
5. If the conversation is flagged as an escalation (`escalation_status = Yes`), an n8n IF node routes that event to a Gmail node, which sends an instant email alert to the support team.

## Running Locally

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python app.py
```

**Frontend:**
Open `frontend/index.html` directly in a browser (or serve it with any static server).

> Note: `crm_service.py` points to an n8n webhook URL configured for this project's test environment. CRM logging and escalation emails will only work while that n8n workflow is active.

## Analytics Dashboard

Accessible via the **"📊 Analytics Dashboard"** button on the chatbot page. This is a UI concept built to demonstrate what a support/analytics view would look like on top of the CRM data — figures shown are static sample data for demonstration purposes, not a live data connection.

## 🚀 Future Scope & Production Readiness

UrbanCart AI has been built with a modular architecture, making it easy to extend into a production-ready customer support solution.

Planned Enhancements
🛒 Shopify Integration: Replace local JSON files with Shopify APIs for live products, inventory, customers, and orders.
💬 Persistent Conversation Memory: Store conversation history using Redis or a database for multi-turn interactions and personalized support.
📊 Live Analytics: Connect the dashboard to CRM data for real-time support metrics and insights.
☁ Cloud Deployment: Deploy the application on platforms such as Render, Railway, AWS, or Google Cloud.
📧 Multi-channel Support: Extend human handoff beyond Gmail by integrating WhatsApp Business, Slack, or Zendesk.
🏢 Enterprise CRM: Replace Google Sheets with platforms like HubSpot, Salesforce, or Zoho CRM while keeping the existing chatbot workflow.

This architecture separates AI, business logic, and data services, allowing the current prototype to evolve into a scalable production system with minimal structural changes.

## 📖 Business Problems Solved

UrbanCart AI addresses key customer support challenges commonly faced by e-commerce businesses.

| Business Challenge         | UrbanCart AI Solution                                           |
| -------------------------- | --------------------------------------------------------------- |
| Product discovery          | AI-powered personalized recommendations                         |
| Order status inquiries     | Secure order tracking using Order ID and email                  |
| Return & refund requests   | Automated return eligibility and policy guidance                |
| Frequently asked questions | Instant AI-powered knowledge base responses                     |
| Human support requests     | Intelligent escalation with email notification                  |
| Manual CRM updates         | Automatic conversation logging through n8n                      |
| Lack of support insights   | Analytics dashboard prototype for monitoring support activities |


## Author

Built by Mahnoor Awan.
