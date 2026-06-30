from langchain_core.tools import tool
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# REALISTIC ORDER DATABASE
# In a real company this would be a SQL database
# For portfolio demo this is identical in behavior
# ─────────────────────────────────────────────

ORDERS = {
    "ORD-78421": {
        "status": "shipped",
        "item": "Samsung Galaxy S24 Ultra 256GB Phantom Black",
        "customer": "Ahmed Raza",
        "city": "Lahore",
        "address": "House 14, Block C, Gulberg III",
        "phone": "0300-4521987",
        "price": "Rs. 289,999",
        "courier": "TCS Express",
        "tracking": "TCS-9921004872",
        "order_date": "June 22, 2026",
        "eta": "June 30, 2026"
    },
    "ORD-78422": {
        "status": "processing",
        "item": "Apple MacBook Air M3 8GB 256GB Space Grey",
        "customer": "Sara Malik",
        "city": "Islamabad",
        "address": "Street 5, F-7/2",
        "phone": "0321-9876543",
        "price": "Rs. 399,000",
        "courier": "Leopards Courier",
        "tracking": "Pending",
        "order_date": "June 27, 2026",
        "eta": "July 3, 2026"
    },
    "ORD-78423": {
        "status": "delivered",
        "item": "Sony WH-1000XM5 Wireless Headphones",
        "customer": "Usman Tariq",
        "city": "Karachi",
        "address": "Flat 8B, Clifton Block 4",
        "phone": "0333-1122334",
        "price": "Rs. 89,500",
        "courier": "TCS Express",
        "tracking": "TCS-9921003341",
        "order_date": "June 18, 2026",
        "eta": "Delivered on June 24, 2026"
    },
    "ORD-78424": {
        "status": "out_for_delivery",
        "item": "Dell XPS 15 Core i7 32GB 1TB SSD",
        "customer": "Fatima Noor",
        "city": "Rawalpindi",
        "address": "House 22, Satellite Town",
        "phone": "0311-5544332",
        "price": "Rs. 459,000",
        "courier": "Rider",
        "tracking": "RDR-20240629-5521",
        "order_date": "June 24, 2026",
        "eta": "Today — arriving between 2pm and 6pm"
    },
    "ORD-78425": {
        "status": "cancelled",
        "item": "iPad Pro 12.9 inch M4 WiFi 256GB",
        "customer": "Bilal Hassan",
        "city": "Faisalabad",
        "address": "Shop 3, Susan Road",
        "phone": "0301-7788990",
        "price": "Rs. 329,000",
        "courier": "N/A",
        "tracking": "N/A",
        "order_date": "June 20, 2026",
        "eta": "Cancelled — refund processing in 3-5 business days"
    },
    "ORD-78426": {
        "status": "shipped",
        "item": "Logitech MX Master 3S Wireless Mouse",
        "customer": "Hina Shahid",
        "city": "Multan",
        "address": "Block 7, New Multan Colony",
        "phone": "0345-6677889",
        "price": "Rs. 18,500",
        "courier": "Postex",
        "tracking": "PTX-884421009",
        "order_date": "June 25, 2026",
        "eta": "July 1, 2026"
    }
}

# ─────────────────────────────────────────────
# PRODUCT CATALOG — for product queries
# ─────────────────────────────────────────────

PRODUCTS = {
    "samsung galaxy s24": {
        "name": "Samsung Galaxy S24 Ultra",
        "price": "Rs. 289,999",
        "stock": "In Stock — 8 units",
        "warranty": "1 year Samsung Pakistan warranty",
        "colors": "Phantom Black, Titanium Gray, Titanium Violet"
    },
    "macbook air": {
        "name": "Apple MacBook Air M3",
        "price": "Rs. 399,000",
        "stock": "In Stock — 3 units",
        "warranty": "1 year Apple warranty + AppleCare available",
        "colors": "Space Grey, Silver, Midnight, Starlight"
    },
    "ipad pro": {
        "name": "iPad Pro 12.9 inch M4",
        "price": "Rs. 329,000",
        "stock": "In Stock — 5 units",
        "warranty": "1 year Apple warranty",
        "colors": "Space Black, Silver"
    }
}

# ─────────────────────────────────────────────
# FAQ DATABASE
# ─────────────────────────────────────────────

FAQ = {
    "return policy": (
        "You can return any item within 14 days of delivery for a full refund. "
        "Items must be in original packaging and unused condition. "
        "To initiate a return, contact us at returns@techstore.pk or call 0800-00123."
    ),
    "shipping": (
        "Standard shipping: 3-5 business days — Free on orders above Rs. 5,000. "
        "Express shipping: 1-2 business days — Rs. 500 flat rate. "
        "Same day delivery available in Lahore, Karachi, Islamabad for orders placed before 12pm."
    ),
    "payment": (
        "We accept: Visa, Mastercard, JazzCash, EasyPaisa, HBL Pay, bank transfer, and Cash on Delivery. "
        "COD available for orders up to Rs. 50,000. "
        "0% installments available on selected credit cards."
    ),
    "warranty": (
        "All products carry original manufacturer warranty. "
        "Electronics: 1 year. Accessories: 6 months. "
        "Warranty claims can be filed at our service center or via email at warranty@techstore.pk."
    ),
    "contact": (
        "Phone: 0800-00123 (Mon-Sat, 9am-9pm). "
        "Email: support@techstore.pk. "
        "WhatsApp: 0300-1234567. "
        "Head office: 24 Main Boulevard, Gulberg, Lahore."
    )
}


# ─────────────────────────────────────────────
# TOOL 1 — Check Order Status
# ─────────────────────────────────────────────

@tool
def check_order_status(order_id: str) -> str:
    """
    Checks the current status of a customer order using order ID.
    Use this whenever a customer asks about their order, delivery date,
    tracking number, or shipment status.
    Order ID format is ORD-XXXXX (example: ORD-78421).
    """
    # Clean up the input — remove spaces, make uppercase
    order_id = order_id.upper().strip().replace(" ", "")

    if order_id in ORDERS:
        order = ORDERS[order_id]

        # Format a professional response with all relevant details
        status_display = order["status"].replace("_", " ").title()

        response = f"""
Order Found — {order_id}
━━━━━━━━━━━━━━━━━━━━━━━━
Product   : {order['item']}
Customer  : {order['customer']}
Status    : {status_display}
Courier   : {order['courier']}
Tracking  : {order['tracking']}
Order Date: {order['order_date']}
ETA       : {order['eta']}
━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return response.strip()

    # Order not found
    return (
        f"No order found with ID {order_id}. "
        f"Please double check your order ID — it should be in format ORD-XXXXX. "
        f"You can find your order ID in your confirmation email or SMS."
    )


# ─────────────────────────────────────────────
# TOOL 2 — Search FAQ
# ─────────────────────────────────────────────

@tool
def search_faq(topic: str) -> str:
    """
    Searches the knowledge base for answers to common customer questions.
    Use this for questions about return policy, shipping, payment methods,
    warranty, or contact information.
    Pass one or two keywords as the topic (example: 'return policy', 'shipping time').
    """
    topic_lower = topic.lower()

    # Check each FAQ key — does the topic match?
    for key, answer in FAQ.items():
        if key in topic_lower or topic_lower in key:
            return answer

    # Partial word match as fallback
    for key, answer in FAQ.items():
        topic_words = topic_lower.split()
        for word in topic_words:
            if word in key and len(word) > 3:
                return answer

    available = ", ".join(FAQ.keys())
    return (
        f"I could not find a specific answer for '{topic}'. "
        f"I can help with: {available}. "
        f"For other queries please call 0800-00123."
    )


# ─────────────────────────────────────────────
# TOOL 3 — Check Product Availability
# ─────────────────────────────────────────────

@tool
def check_product(product_name: str) -> str:
    """
    Checks product availability, price, and stock for items in our catalog.
    Use this when a customer asks about product price, availability, stock,
    colors, or warranty before making a purchase.
    """
    product_lower = product_name.lower()

    for key, product in PRODUCTS.items():
        if key in product_lower or any(word in product_lower for word in key.split()):
            return (
                f"Product: {product['name']}\n"
                f"Price: {product['price']}\n"
                f"Availability: {product['stock']}\n"
                f"Warranty: {product['warranty']}\n"
                f"Colors: {product['colors']}"
            )

    return (
        f"Product '{product_name}' not found in our current catalog. "
        f"Please visit techstore.pk or call 0800-00123 for our full product range."
    )


# ─────────────────────────────────────────────
# TOOL 4 — Escalate to Human Agent
# ─────────────────────────────────────────────

@tool
def escalate_to_human(reason: str) -> str:
    """
    Escalates the conversation to a human support agent.
    Use this when: the customer is very angry or frustrated,
    the issue cannot be resolved with available information,
    the customer explicitly asks to speak to a human,
    or the issue involves a refund, damage claim, or complaint.
    """
    # Generate a ticket number based on reason
    ticket_num = f"TKT-{abs(hash(reason + str(datetime.now()))) % 100000:05d}"

    return (
        f"Escalation successful. Ticket raised: {ticket_num}\n"
        f"Reason: {reason}\n"
        f"A senior support agent will contact you within 2 hours.\n"
        f"You can track your ticket at: techstore.pk/support/{ticket_num}\n"
        f"For urgent issues call: 0800-00123"
    )