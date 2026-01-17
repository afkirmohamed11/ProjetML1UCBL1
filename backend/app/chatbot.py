"""
Chatbot module with RAG and Text-to-SQL using OpenAI function calling.
The LLM decides which tool to use based on the question.
"""
import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-nano")

# Documents directory for RAG
DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

# Database schema for Text-to-SQL context
DB_SCHEMA = """
Tables in the database:

1. customers - Main customer information table
   Columns:
   - customer_id (TEXT, PRIMARY KEY): Unique customer identifier
   - gender (TEXT): Customer gender
   - senior_citizen (BOOLEAN): Is senior citizen
   - partner (BOOLEAN): Has partner
   - dependents (BOOLEAN): Has dependents
   - tenure (INTEGER): Months with company
   - phone_service (BOOLEAN): Has phone service
   - multiple_lines (TEXT): Multiple lines status
   - internet_service (TEXT): Type of internet (DSL, Fiber optic, No)
   - online_security (TEXT): Online security status
   - online_backup (TEXT): Online backup status
   - device_protection (TEXT): Device protection status
   - tech_support (TEXT): Tech support status
   - streaming_tv (TEXT): Streaming TV status
   - streaming_movies (TEXT): Streaming movies status
   - contract (TEXT): Contract type (Month-to-month, One year, Two year)
   - paperless_billing (BOOLEAN): Uses paperless billing
   - payment_method (TEXT): Payment method
   - monthly_charges (NUMERIC): Monthly charges amount
   - total_charges (NUMERIC): Total charges amount
   - churn (BOOLEAN): Has churned
   - status (VARCHAR): Customer status
   - first_name (VARCHAR): First name
   - last_name (VARCHAR): Last name
   - email (VARCHAR): Email address

2. predictions - Churn predictions table
   Columns:
   - prediction_id (SERIAL, PRIMARY KEY): Prediction ID
   - customer_id (TEXT): Customer ID
   - churn_score (FLOAT): Churn probability score
   - churn_label (INTEGER): Predicted label (0 or 1)
   - features_json (JSONB): Features used for prediction
   - model_version (TEXT): Model version used
   - token (UUID): Unique token for feedback
   - created_at (TIMESTAMP): Prediction timestamp

3. feedback - User feedback on predictions
   Columns:
   - feedback_id (SERIAL, PRIMARY KEY): Feedback ID
   - prediction_id (INTEGER): Related prediction
   - feedback_label (INTEGER): Actual outcome (0 or 1)
   - source (TEXT): Feedback source
   - created_at (TIMESTAMP): Feedback timestamp
"""

# Define tools for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Query the PostgreSQL database to get specific data about customers, predictions, or feedback. Use this for questions asking about counts, lists, averages, specific records, or any data retrieval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": f"A valid PostgreSQL SELECT query. Available schema: {DB_SCHEMA}"
                    }
                },
                "required": ["sql_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_documentation",
            "description": "Search the system documentation to answer questions about how the system works, features, concepts, or general information about churn prediction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant documentation"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def get_openai_client():
    """Get OpenAI client."""
    try:
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")


# ============== TOOL IMPLEMENTATIONS ==============

def load_documents() -> list[dict]:
    """Load documents from the docs directory."""
    documents = []
    
    if not DOCS_DIR.exists():
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        sample_doc = DOCS_DIR / "about.md"
        sample_doc.write_text("""# Telco Churn Prediction System

## Overview
This system predicts customer churn for a telecommunications company using machine learning.

## Features
- **Churn Prediction**: Predict whether a customer will churn based on their profile
- **Customer Management**: View and manage customer information
- **Model Retraining**: Retrain the model with new feedback data

## How it works
1. Customer data is collected including tenure, services, and billing information
2. The ML model analyzes patterns to predict churn probability
3. Predictions are stored and can be reviewed
4. User feedback improves the model over time

## Key Factors for Churn
- Contract type (month-to-month contracts have higher churn)
- Tenure (newer customers are more likely to churn)
- Monthly charges (higher charges correlate with churn)
- Internet service type (Fiber optic users show different patterns)
- Payment method (Electronic check users churn more)
""")
    
    for file_path in DOCS_DIR.glob("**/*"):
        if file_path.is_file() and file_path.suffix in [".txt", ".md", ".pdf"]:
            try:
                content = file_path.read_text(encoding="utf-8")
                documents.append({
                    "filename": file_path.name,
                    "content": content
                })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return documents


def execute_search_documentation(query: str) -> str:
    """Search documentation and return relevant content."""
    documents = load_documents()
    
    if not documents:
        return "No documentation found."
    
    # Simple keyword matching (could be enhanced with embeddings)
    query_lower = query.lower()
    relevant_docs = []
    
    for doc in documents:
        if any(word in doc['content'].lower() for word in query_lower.split()):
            relevant_docs.append(doc)
    
    if not relevant_docs:
        relevant_docs = documents  # Return all if no match
    
    return "\n\n---\n\n".join([
        f"Document: {doc['filename']}\n{doc['content']}" 
        for doc in relevant_docs[:3]
    ])


def execute_query_database(sql_query: str) -> dict:
    """Execute SQL query and return results."""
    # Clean up the SQL
    sql_query = sql_query.strip()
    if sql_query.startswith("```"):
        sql_query = sql_query.split("\n", 1)[1] if "\n" in sql_query else sql_query[3:]
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]
    sql_query = sql_query.strip()
    
    # Security check - only allow SELECT
    if not sql_query.upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed.", "results": None}
    
    from app.db_connection import get_db_connection
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(sql_query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
        conn.close()
        
        results = [dict(zip(columns, row)) for row in rows]
        return {
            "error": None,
            "results": results[:50],
            "total_rows": len(results),
            "sql": sql_query
        }
        
    except Exception as e:
        return {"error": str(e), "results": None, "sql": sql_query}


# ============== MAIN CHAT FUNCTION ==============

def chat(question: str) -> dict:
    """
    Process a chat question using OpenAI function calling.
    The LLM decides whether to query the database or search docs.
    """
    if not OPENAI_API_KEY:
        return {
            "question": question,
            "answer": "Error: OPENAI_API_KEY not configured. Please set it in .env file.",
            "tools_used": [],
            "error": True
        }
    
    client = get_openai_client()
    
    system_prompt = """You are a helpful assistant for a Telco Customer Churn Prediction system.
You have access to two tools:
1. query_database - Use this to get specific data (counts, lists, customer info, statistics)
2. search_documentation - Use this to answer questions about how the system works

Choose the appropriate tool based on the user's question. You can use multiple tools if needed.
After getting tool results, provide a clear, helpful answer to the user."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    
    tools_used = []
    
    # First call - LLM decides which tool(s) to use
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.3
    )
    
    assistant_message = response.choices[0].message
    
    # If no tool calls, return direct answer
    if not assistant_message.tool_calls:
        return {
            "question": question,
            "answer": assistant_message.content,
            "tools_used": [],
            "error": False
        }
    
    # Process tool calls
    messages.append(assistant_message)
    
    for tool_call in assistant_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "query_database":
            result = execute_query_database(function_args["sql_query"])
            tools_used.append({
                "tool": "query_database",
                "sql": result.get("sql"),
                "row_count": result.get("total_rows"),
                "error": result.get("error")
            })
            tool_response = json.dumps(result, default=str)
            
        elif function_name == "search_documentation":
            result = execute_search_documentation(function_args["query"])
            tools_used.append({
                "tool": "search_documentation",
                "query": function_args["query"]
            })
            tool_response = result
        else:
            tool_response = "Unknown tool"
        
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_response
        })
    
    # Final call - LLM generates answer based on tool results
    final_response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=500
    )
    
    return {
        "question": question,
        "answer": final_response.choices[0].message.content,
        "tools_used": tools_used,
        "error": False
    }


# ============== LEGACY FUNCTIONS (for /chat/rag and /chat/sql endpoints) ==============

def rag_query(question: str) -> str:
    """Answer question using RAG with loaded documents."""
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY not configured."
    
    documents = load_documents()
    if not documents:
        return "No documents found."
    
    context = "\n\n---\n\n".join([
        f"Document: {doc['filename']}\n{doc['content']}" 
        for doc in documents
    ])
    
    client = get_openai_client()
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer based on the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content


def text_to_sql(question: str) -> dict:
    """Convert natural language to SQL and execute."""
    if not OPENAI_API_KEY:
        return {"sql": None, "result": None, "answer": "Error: OPENAI_API_KEY not configured.", "error": True}
    
    client = get_openai_client()
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"Convert to PostgreSQL SELECT query only. Schema: {DB_SCHEMA}"},
            {"role": "user", "content": question}
        ],
        temperature=0,
        max_tokens=300
    )
    
    sql_query = response.choices[0].message.content.strip()
    result = execute_query_database(sql_query)
    
    if result["error"]:
        return {"sql": result.get("sql"), "result": None, "answer": result["error"], "error": True}
    
    # Generate answer
    answer_response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "Provide a concise answer based on the query results."},
            {"role": "user", "content": f"Question: {question}\nResults: {result['results'][:10]}\nTotal: {result['total_rows']}"}
        ],
        temperature=0.3,
        max_tokens=300
    )
    
    return {
        "sql": result["sql"],
        "result": result["results"],
        "answer": answer_response.choices[0].message.content,
        "error": False
    }
