import requests

N8N_WEBHOOK = "https://mahnoor-1.app.n8n.cloud/webhook/urbancart-escalation"


def log_to_crm(
    customer_name,
    email,
    conversation_summary,
    order_number,
    support_category,
    ai_resolution_status,
    escalation_status
):

    payload = {
        "customer_name": customer_name,
        "email": email,
        "conversation_summary": conversation_summary,
        "order_number": order_number,
        "support_category": support_category,
        "ai_resolution_status": ai_resolution_status,
        "escalation_status": escalation_status
    }

    try:

        response = requests.post(
            N8N_WEBHOOK,
            json=payload,
            timeout=10
        )

        return response.status_code

    except Exception as e:

        print("CRM Error:", e)

        return None