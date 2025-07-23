# cli_ask.py

import sqlite3
import pandas as pd
import os
from app.llm.gemini_agent import question_to_sql, humanize_answer # Import the humanization function from llm/gemini_agent.py
from app.db.init_db import load_data as load_initial_data # Import your data loading function

# --- Configuration ---
DB_FILE = "ecom.db"
SCHEMA_FILE = "db/schema.sql" # Assuming schema.sql is in a 'db' folder relative to project root
DATA_DIR = "data"             # Assuming CSVs are in a 'data' folder relative to project root

if __name__ == "__main__":
    print("🚀 Starting E-commerce Data Assistant...")

    # Ensure database and data are loaded/initialized first
    # This prevents errors on the first run or if ecom.db is deleted
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        print("\n--- Initializing database and loading data ---")
        # Ensure init_db.py's load_data function can handle relative paths correctly
        # The load_data function in init_db.py implicitly assumes it's run from the root
        # If your init_db.py load_data needs specific paths, pass them here.
        # As per your latest init_db.py, it uses "db/schema.sql" and "data/", which is fine
        # if cli_ask.py is run from the project root.
        load_initial_data() # This call will create/populate ecom.db
        print(f"✅ Database '{DB_FILE}' initialized and loaded.")
    else:
        print(f"✅ Database '{DB_FILE}' already exists and contains data. Skipping initial load.")

    print("\n--- Ready to answer your questions ---")
    
    while True: # Keep the loop for continuous questions
        question = input("❓ Ask your analytics question (type 'exit' or 'quit' to end): ")
        if question.lower() in ['exit', 'quit']:
            print("👋 Goodbye!")
            break

        print("\n🧠 Generating SQL Query...")
        generated_sql = question_to_sql(question)
        print(f"📝 Generated SQL Query:\n{generated_sql}\n")

        # Handle LLM error response for SQL generation
        if generated_sql.startswith("-- ERROR:"): # Match the exact error prefix from gemini_agent.py
            print(f"❌ SQL Generation Error: {generated_sql.replace('-- ERROR: ', '')}")
            print("-" * 50)
            continue

        print("📊 Executing Query...")
        # Open connection within this block for each query
        conn = None 
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute(generated_sql)
            results = cursor.fetchall()

            # Fetch column names
            column_names = [desc[0] for desc in cursor.description]

            if results:
                result_df = pd.DataFrame(results, columns=column_names)

                print("\n📊 Raw Query Results:")
                print(result_df)

                print("\n✨ Humanizing Answer...")
                # Use the imported humanize_answer_llm from gemini_agent.py
                final_answer = humanize_answer(question, generated_sql, result_df)
                
                print("\n💬 Final Answer:")
                print(final_answer)

            else:
                print("⚠️ No data found for this query.")
                # Also use humanize_answer_llm for a natural "no data" response
                final_answer = humanize_answer(question, generated_sql, pd.DataFrame()) # Pass empty DataFrame
                print(f"\n💬 Final Answer:\n{final_answer}")


        except sqlite3.Error as e: # Catch specific SQLite errors
            print(f"\n🚨 Database Query Error: {e}")
        except Exception as e: # Catch any other unexpected errors
            print(f"\n🚨 An unexpected error occurred during query execution: {e}")
        finally:
            if conn:
                conn.close() # Ensure connection is always closed

        print("-" * 50) # Separator for next question


# ----------------------------------------------------------


# # cli_ask.py

# import sqlite3
# import pandas as pd
# from llm.gemini_agent import question_to_sql, humanize_answer

# # Connect to SQLite database
# conn = sqlite3.connect("ecom.db")
# cursor = conn.cursor()

# # Get user question from CLI
# question = input("❓ Ask your analytics question: ")

# # Use LLM to get SQL
# sql_query = question_to_sql(question) 
# # sql_query = "SELECT item_id FROM ad_sales_metrics WHERE date = '2025-06-01' ORDER BY ad_spend DESC LIMIT 1"
# print("\n🧠 Generated SQL Query:")
# print(sql_query)

# # Handle Gemini fallback
# if sql_query.startswith("ERROR"):
#     print("\n❌ Sorry, I cannot answer this based on available data.")
# else:
#     try:
#         # Run SQL query
#         cursor.execute(sql_query)
#         results = cursor.fetchall()

#         # Fetch column names
#         column_names = [desc[0] for desc in cursor.description]

#         if results:
#             # Convert to DataFrame
#             result_df = pd.DataFrame(results, columns=column_names)

#             print("\n📊 Query Results:")
#             print(result_df)

#             # Get humanized answer
#             final_answer = humanize_answer(question, sql_query, result_df)
#             # Get humanized answer
#             # final_answer = "Correct answer"
#             print("\n💬 Final Answer:")
#             print(final_answer)

#         else:
#             print("⚠️ No data found for this query.")

#     except Exception as e:
#         print(f"\n🚨 Error running query: {e}")

# # Close DB connection
# conn.close()






# # -------------------------------------------------------



# # # cli_ask.py

# # import sqlite3
# # from llm.gemini_agent import question_to_sql

# # # Connect to SQLite database
# # conn = sqlite3.connect("ecom.db")
# # cursor = conn.cursor()

# # # Get user question from CLI
# # question = input("❓ Ask your analytics question: ")

# # # Use LLM to get SQL
# # # sql_query = question_to_sql(question)
# # sql_query = "SELECT item_id FROM ad_sales_metrics WHERE date = '2025-06-01' ORDER BY ad_spend DESC LIMIT 1"
# # print("\n🧠 Generated SQL Query:")
# # print(sql_query)

# # # Handle Gemini fallback
# # if sql_query.startswith("ERROR"):
# #     print("\n❌ Sorry, I cannot answer this based on available data.")
# # else:
# #     try:
# #         # Run SQL query
# #         cursor.execute(sql_query)
# #         results = cursor.fetchall()

# #         # Fetch column names
# #         column_names = [desc[0] for desc in cursor.description]

# #         # Display results
# #         print("\n📊 Query Results:")
# #         if results:
# #             print("\t".join(column_names))
# #             for row in results:
# #                 print("\t".join(str(x) for x in row))
# #         else:
# #             print("⚠️ No data found for this query.")
# #     except Exception as e:
# #         print(f"\n🚨 Error running query: {e}")

# # # Close DB connection
# # conn.close()