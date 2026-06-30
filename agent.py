from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from typing import TypedDict, Annotated
import operator
import os

# Import all four tools from tools.py
from tools import check_order_status, search_faq, escalate_to_human, check_product


# ─────────────────────────────────────────────
# STATE — the suitcase that travels everywhere
# ─────────────────────────────────────────────

class SupportState(TypedDict):
    messages: Annotated[list, operator.add]


# ─────────────────────────────────────────────
# TOOLS LIST — all tools the agent can use
# ─────────────────────────────────────────────

tools = [check_order_status, search_faq, escalate_to_human, check_product]


# ─────────────────────────────────────────────
# LLM — with tools bound to it
# ─────────────────────────────────────────────

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
    max_tokens=800
)
llm_with_tools = llm.bind_tools(tools)


# ─────────────────────────────────────────────
# SYSTEM PROMPT — the agent's identity and rules
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are Zara, a professional customer support agent for TechStore.pk — 
Pakistan's leading online electronics retailer.

Your personality:
- Warm, professional, and helpful
- Empathetic when customers are frustrated
- Concise — do not write long paragraphs unnecessarily

Your capabilities (always use tools, never guess):
- check_order_status: for any order tracking or delivery questions
- search_faq: for policy, shipping, payment, warranty questions  
- check_product: for product price, availability, stock questions
- escalate_to_human: when customer is upset or issue is unresolvable

Rules you must follow:
1. ALWAYS use a tool when the question matches a tool's purpose
2. NEVER make up order details, prices, or policies
3. If a customer seems very frustrated, use escalate_to_human immediately
4. If you cannot help, always offer to escalate
5. Address the customer by name if they mention it

You cannot process refunds directly or change orders yourself — 
always escalate these to a human agent."""


# ─────────────────────────────────────────────
# NODE 1 — agent_node (the thinking step)
# ─────────────────────────────────────────────

def agent_node(state: SupportState):
    # Always prepend system prompt to give agent its identity
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ─────────────────────────────────────────────
# NODE 2 — tool_node (the action step)
# ─────────────────────────────────────────────

def tool_node(state: SupportState):
    last_message = state["messages"][-1]

    # Build a lookup dictionary: tool name → tool object
    tool_map = {t.name: t for t in tools}
    results = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Run the actual Python function
        result = tool_map[tool_name].invoke(tool_args)

        # Wrap in ToolMessage with matching ID
        results.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
        )

    return {"messages": results}


# ─────────────────────────────────────────────
# CONDITIONAL EDGE — should we loop or stop?
# ─────────────────────────────────────────────

def should_continue(state: SupportState):
    last_message = state["messages"][-1]

    # If LLM requested tool calls → run tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "use_tool"

    # Otherwise LLM gave final text answer → stop
    return "end"


# ─────────────────────────────────────────────
# BUILD THE GRAPH
# ─────────────────────────────────────────────

def build_agent():
    graph = StateGraph(SupportState)

    # Register nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # Entry point — always start at agent
    graph.set_entry_point("agent")

    # After agent runs — check if tools needed
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "use_tool": "tools",
            "end": END
        }
    )

    # After tools run — always go back to agent
    graph.add_edge("tools", "agent")

    # Attach memory so conversations persist
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)