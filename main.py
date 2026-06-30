from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template
from langchain_core.messages import HumanMessage
from agent import build_agent
import os

app = Flask(__name__)

# Build the agent once when server starts
# Not inside the route — you do not want to rebuild the graph on every request
agent = build_agent()


# ─────────────────────────────────────────────
# ROUTE 1 — Serve the chat page
# ─────────────────────────────────────────────

@app.route("/")
def index():
    # Flask looks for index.html inside the templates/ folder automatically
    return render_template("index.html")


# ─────────────────────────────────────────────
# ROUTE 2 — Handle chat messages from browser
# ─────────────────────────────────────────────

@app.route("/chat", methods=["POST"])
def chat():
    # Read the JSON data sent from the browser
    data = request.json
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default_session")

    # Basic validation
    if not user_message:
        return jsonify({"error": "Please type a message"}), 400

    # thread_id connects this call to the right memory
    config = {"configurable": {"thread_id": session_id}}

    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config
        )

        # Last message in state is always the final agent response
        response_text = result["messages"][-1].content

        return jsonify({
            "response": response_text,
            "session_id": session_id
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Agent error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
    