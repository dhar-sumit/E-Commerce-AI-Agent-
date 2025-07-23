from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
import os
from plotly.utils import PlotlyJSONEncoder
import google.generativeai as genai
from dotenv import load_dotenv

# --- UPDATED IMPORTS ---
from llm.gemini_agent import question_to_sql, humanize_answer 
from db.init_db import load_data as load_initial_data 
from utils.charts import generate_chart
# --- END UPDATED IMPORTS ---

# --- Flask app instance ---
# Renamed from app = Flask(__name__) for clarity as it's now inside an 'app' package
app = Flask(__name__) 

# --- CRITICAL FIX: Configure Flask to use Plotly's JSON encoder ---
app.json_encoder = PlotlyJSONEncoder
# --- END CRITICAL FIX ---


# --- Configuration ---
DB_FILE = "ecom.db" # This path is relative to where Flask is run, usually project root

# --- Initial Database Load on App Startup ---
with app.app_context():
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        print(f"--- Initializing database and loading data for web app ---")
        load_initial_data() 
        print(f"✅ Database '{DB_FILE}' initialized and loaded for web app.")
    else:
        print(f"✅ Database '{DB_FILE}' already exists and contains data. Skipping initial load for web app.")

# Load Gemini API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- ADD THESE DEBUG PRINTS ---
if GEMINI_API_KEY:
    print("DEBUG: GOOGLE_API_KEY loaded successfully (first few chars):", GEMINI_API_KEY[:5] + "...")
else:
    print("ERROR: GOOGLE_API_KEY not found in .env file or environment variables!")
# --- END DEBUG PRINTS ---

# Configure Gemini globally
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("DEBUG: Gemini API configured successfully.") # Add this
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to configure Gemini API: {e}") # Add this
        raise # Re-raise to stop execution if config fails


# Helper function to run SQL queries, returning DataFrame or error info
def run_sql_query_helper(query):
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(query, conn)
        return {"success": True, "data_frame": df}
    except pd.io.sql.DatabaseError as e:
        return {"error": f"Database query error: {str(e)}"}
    except sqlite3.Error as e:
        return {"error": f"SQLite error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
    finally:
        if conn:
            conn.close()

# --- Main Route: Serves the HTML page ---
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# ==============================================================================
# --- Sequential API Endpoints for Progressive Rendering ---
# ==============================================================================

@app.route("/api/generate_sql", methods=["POST"])
def api_generate_sql():
    user_question = request.json.get("question")
    if not user_question:
        return jsonify({"error": "Missing 'question' in request."}), 400
    
    try:
        sql_query = question_to_sql(user_question)
        if sql_query.startswith("-- ERROR:"):
            return jsonify({
                "question": user_question,
                "error": f"SQL generation failed: {sql_query.replace('-- ERROR: ', '')}"
            }), 500
        return jsonify({"success": True, "sql": sql_query}), 200
    except Exception as e:
        return jsonify({"error": f"SQL generation internal error: {str(e)}"}), 500

@app.route("/api/execute_query", methods=["POST"])
def api_execute_query():
    sql_query = request.json.get("sql")
    user_question = request.json.get("question") 
    if not sql_query:
        return jsonify({"error": "Missing 'sql' in request."}), 400
    
    query_execution_result = run_sql_query_helper(sql_query)
    
    if query_execution_result.get("error"):
        return jsonify({"error": query_execution_result["error"]}), 500
    
    result_df = query_execution_result['data_frame']
    
    raw_results_html = ""
    raw_results_records = []
    if not result_df.empty:
        raw_results_html = result_df.to_html(classes="table table-striped", index=False)
        raw_results_records = result_df.to_dict(orient="records") 
    else:
        raw_results_html = "<div class='text-danger'>❌ No matching data found in database.</div>"

    return jsonify({
        "success": True, 
        "raw_results_html": raw_results_html,
        "raw_results_records": raw_results_records, 
        "sql": sql_query, 
        "question": user_question 
    }), 200

@app.route("/api/generate_chart", methods=["POST"])
def api_generate_chart():
    raw_results_records = request.json.get("raw_results_records")
    sql_query = request.json.get("sql")
    user_question = request.json.get("question")
    
    if raw_results_records is None: 
        return jsonify({"error": "Missing 'raw_results_records' in request."}), 400
    
    result_df = pd.DataFrame(raw_results_records)

    chart_data_json = generate_chart(result_df, user_question) 
    
    return jsonify({"success": True, "chart_data_json": chart_data_json}), 200

@app.route("/api/humanize_answer", methods=["POST"])
def api_humanize_answer():
    raw_results_records = request.json.get("raw_results_records")
    sql_query = request.json.get("sql")
    user_question = request.json.get("question")

    if raw_results_records is None or not sql_query or not user_question:
        return jsonify({"error": "Missing data for humanization."}), 400
    
    result_df = pd.DataFrame(raw_results_records)

    final_answer = humanize_answer(user_question, sql_query, result_df)
    
    return jsonify({"success": True, "answer": final_answer}), 200

# ==============================================================================
# --- Original /api/ask Endpoint (for external usage - largely unchanged) ---
# This endpoint can remain as a single, combined response for external clients
# who don't need step-by-step updates.
# ==============================================================================
@app.route("/api/ask", methods=["POST"])
def ask_api():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' in request"}), 400

    question = data["question"]
    sql_query = None
    answer = None
    raw_results_records = [] 
    html_table = ""
    chart_data_json = None 
    
    try:
        sql_query = question_to_sql(question)

        if sql_query.startswith("-- ERROR:"):
            return jsonify({
                "question": question,
                "error": f"SQL generation failed: {sql_query.replace('-- ERROR: ', '')}"
            }), 500

        query_execution_result = run_sql_query_helper(sql_query) 
        if query_execution_result.get("error"):
            return jsonify({
                "question": question,
                "error": query_execution_result["error"]
            }), 500

        result_df = query_execution_result['data_frame']
        
        if not result_df.empty:
            raw_results_records = result_df.to_dict(orient="records")
            html_table = result_df.to_html(index=False, classes="table table-bordered")
            chart_data_json = generate_chart(result_df, question) 
        else:
            html_table = "<div style='color: #dc3545;'>No data found for this query.</div>"
            chart_data_json = None 

        answer = humanize_answer(question, sql_query, result_df)

        return jsonify({
            "question": question,
            "sql_query": sql_query,
            "answer": answer,
            "raw_results": raw_results_records, 
            "html_table": html_table,           
            "chart_data_json": chart_data_json, 
        })

    except Exception as e:
        return jsonify({
            "question": question,
            "error": f"An unexpected server error occurred: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)