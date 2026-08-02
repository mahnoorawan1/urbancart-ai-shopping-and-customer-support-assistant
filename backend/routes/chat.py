import re
from flask import Blueprint, request, jsonify

from services.gemini_service import (
    ask_gemini,
    recommend_with_ai,
    explain_order_status,
    explain_return
)

from services.intent_service import detect_intent
from services.order_service import get_order
from services.return_service import check_return
from services.crm_service import log_to_crm
from services.product_service import get_products

chat_bp = Blueprint("chat", __name__)

# ==========================================
# In-memory conversation state
# Keyed by session_id (sent by frontend).
# Holds what we're still waiting on the
# customer to provide — order_id/email for
# order_tracking & return, or
# category/budget/brand for recommendation.
# ==========================================

CONVERSATIONS = {}

EMAIL_PATTERN = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")

SKIP_WORDS = {
    "skip", "no", "none", "any", "n/a", "na",
    "no preference", "surprise me", "anything", "nothing"
}


def extract_email(text):
    match = EMAIL_PATTERN.search(text)
    return match.group() if match else None


def extract_order_id(text):
    # The bot has just asked the customer directly for their
    # Order ID, so whatever they type back IS the order ID
    # (e.g. "ORD1001") — no extraction needed, just clean it up.
    cleaned = text.strip().upper()
    return cleaned if cleaned else None


def is_skip(text):
    return text.strip().lower() in SKIP_WORDS


def normalize_category(text):
    # Match against real categories in products.json so a
    # typed answer like "gaming laptop" still resolves to the
    # actual "Laptop" category instead of returning zero results.
    if is_skip(text):
        return None

    known_categories = {p["category"].lower() for p in get_products()}
    lowered = text.strip().lower()

    for category in known_categories:
        if category in lowered or lowered in category:
            return category.title()

    return text.strip().title()


def extract_budget_number(text):
    if is_skip(text):
        return None
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def extract_brand(text):
    if is_skip(text):
        return None
    return text.strip().title()


def run_recommendation(session_id, state):
    """Ask the next missing recommendation slot, or — once
    category/budget/brand have all been asked about — call
    the AI and return the actual recommendation."""

    if not state.get("category_asked"):
        state["awaiting"] = "rec_category"
        state["category_asked"] = True
        CONVERSATIONS[session_id] = state
        return jsonify({
            "type": "recommendation",
            "reply": "Sure! What are you shopping for — Laptop, Headphones, Earbuds, or Mouse? (Or say 'surprise me' for anything.)",
            "data": {}
        })

    if not state.get("budget_asked"):
        state["awaiting"] = "rec_budget"
        state["budget_asked"] = True
        CONVERSATIONS[session_id] = state
        return jsonify({
            "type": "recommendation",
            "reply": "What's your budget? (Or say 'skip' if you don't have one.)",
            "data": {}
        })

    if not state.get("brand_asked"):
        state["awaiting"] = "rec_brand"
        state["brand_asked"] = True
        CONVERSATIONS[session_id] = state
        return jsonify({
            "type": "recommendation",
            "reply": "Any brand preference? (Or say 'skip'.)",
            "data": {}
        })

    # All slots collected (or skipped) — generate the recommendation.
    CONVERSATIONS.pop(session_id, None)

    reply = recommend_with_ai(
        user_message=state.get("original_message", ""),
        category=state.get("category"),
        max_price=state.get("budget"),
        brand=state.get("brand"),
        preferences=state.get("preferences") or []
    )

    log_to_crm(
        customer_name="Unknown",
        email=None,
        conversation_summary=state.get("original_message", ""),
        order_number="",
        support_category="Recommendation",
        ai_resolution_status="Resolved",
        escalation_status="No"
    )

    return jsonify({
        "type": "recommendation",
        "reply": reply,
        "data": {}
    })


@chat_bp.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    message = data.get("message", "").strip()
    session_id = data.get("session_id", "anonymous")

    state = CONVERSATIONS.get(session_id)

    # ==========================================
    # Guard: if we're mid-flow but the new message
    # looks like a full sentence (not a short direct
    # answer), the customer likely restarted or asked
    # something new — e.g. re-clicking a quick-action
    # button. Drop the pending state and re-classify
    # from scratch instead of swallowing the sentence
    # as the order ID / email / recommendation slot.
    # ==========================================

    if state and state.get("awaiting") and len(message.split()) > 4:
        CONVERSATIONS.pop(session_id, None)
        state = None

    # ==========================================
    # Recommendation multi-step flow — handled
    # entirely separately since its slots
    # (category/budget/brand) are each individually
    # skippable, unlike order_id/email.
    # ==========================================

    if state and state.get("awaiting") in ("rec_category", "rec_budget", "rec_brand"):

        awaiting = state["awaiting"]

        if awaiting == "rec_category":
            state["category"] = normalize_category(message)
        elif awaiting == "rec_budget":
            state["budget"] = extract_budget_number(message)
        elif awaiting == "rec_brand":
            state["brand"] = extract_brand(message)

        return run_recommendation(session_id, state)

    # ==========================================
    # If we're mid-flow on order_id/email (order
    # tracking or return), treat this message as
    # filling that slot instead of re-running
    # intent detection.
    # ==========================================

    if state and state.get("awaiting"):

        awaiting = state["awaiting"]

        if awaiting == "order_id":
            candidate = extract_order_id(message)

            if not candidate or not re.search(r"\d", candidate):
                return jsonify({
                    "type": state["intent"],
                    "reply": "That doesn't look like a valid Order ID — it should include numbers (e.g. ORD1001). Please re-enter it.",
                    "data": {}
                })

            state["order_id"] = candidate
        elif awaiting == "email":
            candidate = extract_email(message)

            if not candidate:
                return jsonify({
                    "type": state["intent"],
                    "reply": "That doesn't look like a valid email address. Please re-enter the email used to place this order.",
                    "data": {}
                })

            state["email"] = candidate

        intent = state["intent"]
        entities = {
            "order_id": state.get("order_id"),
            "email": state.get("email")
        }

    else:

        result = detect_intent(message)
        intent = result["intent"]
        entities = result["entities"]

    # ==========================================
    # Recommendation Module (fresh start)
    # ==========================================

    if intent == "recommendation":

        new_state = {
            "intent": "recommendation",
            "category": entities.get("category"),
            "budget": entities.get("budget"),
            "brand": entities.get("brand"),
            "preferences": entities.get("preferences") or [],
            "original_message": message,
            "category_asked": bool(entities.get("category")),
            "budget_asked": entities.get("budget") is not None,
            "brand_asked": bool(entities.get("brand")),
        }

        return run_recommendation(session_id, new_state)

    # ==========================================
    # Order Tracking Module
    # ==========================================

    elif intent == "order_tracking":

        order_id = entities.get("order_id")
        email = entities.get("email")

        if not order_id:
            CONVERSATIONS[session_id] = {
                "intent": "order_tracking",
                "awaiting": "order_id",
                "order_id": None,
                "email": None
            }
            return jsonify({
                "type": intent,
                "reply": "Sure! Please provide your Order ID.",
                "data": {}
            })

        if not email:
            CONVERSATIONS[session_id] = {
                "intent": "order_tracking",
                "awaiting": "email",
                "order_id": order_id,
                "email": None
            }
            return jsonify({
                "type": intent,
                "reply": "For security, please provide the email address used to place this order.",
                "data": {}
            })

        CONVERSATIONS.pop(session_id, None)

        order = get_order(order_id, email)

        if not order:
            return jsonify({
                "type": intent,
                "reply": "Sorry, I couldn't find any order matching that Order ID and email.",
                "data": {}
            })

        reply = explain_order_status(order)

        log_to_crm(
            customer_name=order["customer_name"],
            email=order["email"],
            conversation_summary=message,
            order_number=order["order_id"],
            support_category="Order Tracking",
            ai_resolution_status="Resolved",
            escalation_status="No"
        )

    # ==========================================
    # Return Module
    # ==========================================

    elif intent == "return":

        order_id = entities.get("order_id")
        email = entities.get("email")

        if not order_id:
            CONVERSATIONS[session_id] = {
                "intent": "return",
                "awaiting": "order_id",
                "order_id": None,
                "email": None
            }
            return jsonify({
                "type": intent,
                "reply": "Please provide your Order ID.",
                "data": {}
            })

        if not email:
            CONVERSATIONS[session_id] = {
                "intent": "return",
                "awaiting": "email",
                "order_id": order_id,
                "email": None
            }
            return jsonify({
                "type": intent,
                "reply": "For security, please provide the email used to place this order.",
                "data": {}
            })

        CONVERSATIONS.pop(session_id, None)

        order = check_return(order_id, email)

        if not order:
            return jsonify({
                "type": intent,
                "reply": "Sorry, I couldn't find any order matching that Order ID and email.",
                "data": {}
            })

        reply = explain_return(order)

        log_to_crm(
            customer_name=order["customer_name"],
            email=order["email"],
            conversation_summary=message,
            order_number=order["order_id"],
            support_category="Return Request",
            ai_resolution_status="Resolved",
            escalation_status="No"
        )

    # ==========================================
    # Human Handoff
    # ==========================================

    elif intent == "human_handoff":

        CONVERSATIONS.pop(session_id, None)

        log_to_crm(
            customer_name="Unknown",
            email=entities.get("email"),
            conversation_summary=message,
            order_number=entities.get("order_id"),
            support_category="Human Handoff",
            ai_resolution_status="Escalated",
            escalation_status="Yes"
        )

        reply = (
            "I understand you'd like to speak with a human support representative.\n\n"
            "✅ Your request has been escalated.\n"
            "Our support team will contact you shortly."
        )

    # ==========================================
    # FAQ / General
    # ==========================================

    else:

        CONVERSATIONS.pop(session_id, None)

        reply = ask_gemini(message)

        log_to_crm(
            customer_name="Unknown",
            email=entities.get("email"),
            conversation_summary=message,
            order_number="",
            support_category="FAQ",
            ai_resolution_status="Resolved",
            escalation_status="No"
        )

    return jsonify({
        "type": intent,
        "reply": reply,
        "data": {}
    })