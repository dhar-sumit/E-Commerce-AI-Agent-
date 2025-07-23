# llm/gemini_agent.py

import re
from models.gemini_models import SQL_GEN_MODEL, HUMANIZE_MODEL
from llm.prompts.sql_generation_prompts import SQL_GEN_PROMPT 
from llm.prompts.humanization_prompts import HUMANIZE_PROMPT


def question_to_sql(question):
    
    prompt = SQL_GEN_PROMPT.format(question=question)

    try:
        response = SQL_GEN_MODEL.generate_content(prompt)
        raw_sql_text = response.text.strip()

        # --- REVISED AGGRESSIVE POST-PROCESSING ---
        sql_query = raw_sql_text
        # print(response)

        # 1. Remove common leading markdown code block syntax (e.g., ```sql, ```sqlite)
        sql_query = re.sub(r"^\s*`{3,}\s*(sql|sqlite)?\s*\n?", "", sql_query, flags=re.IGNORECASE).strip()
        
        # 2. Remove common trailing markdown code block syntax
        sql_query = re.sub(r"\s*\n?`{3,}\s*$", "", sql_query, flags=re.IGNORECASE).strip()

        # 3. Remove common prefixes that LLMs sometimes add (e.g., 'SQL:', 'SQLite', 'query')
        #    and common suffixes (like 'lite' that appeared)
        sql_query = re.sub(r"^\s*(sql|sqlite|query|sql:|sqlite:|query:)\s*", "", sql_query, flags=re.IGNORECASE).strip()
        sql_query = re.sub(r"\s*(sql|sqlite|query|lite)\s*$", "", sql_query, flags=re.IGNORECASE).strip()

        # 4. Crucial: Ensure the query ends with a semicolon.
        #    If there's multiple semicolons (e.g., from an error), only keep the first statement.
        if ';' in sql_query:
            # Find the first semicolon and take everything before and including it.
            sql_query = sql_query.split(';')[0].strip() + ';'
        else:
            # If for some reason no semicolon is generated, just ensure it's stripped well
            sql_query = sql_query.strip()
            # As a last resort, add a semicolon if it's missing (helps with cursor.execute)
            if not sql_query.endswith(';'):
                sql_query += ';'

        return sql_query

    except Exception as e:
        return f"-- ERROR: Gemini API failed: {e}"

# Function to humanize the answer using Gemini
# Renamed from 'humanize_answer' to 'humanize_answer_llm' for clarity and to avoid conflicts
def humanize_answer(question, sql, result_df):
    # Convert DataFrame to readable string

    if result_df.empty:
        result_text = "No results found."
    
    else:
        # Use to_markdown() for better structured input to the LLM
        result_text = result_df.to_markdown(index=False, numalign="left", stralign="left")

    prompt = HUMANIZE_PROMPT.format(question=question, sql=sql, result_text=result_text)

    response = HUMANIZE_MODEL.generate_content(prompt) # Using HUMANIZE_MODEL
    print(response)
    return response.text.strip()
    # response = "Working the best way we can .... SELECT item_id, SUM(ad_sales) AS total_ad_sales FROM ad_sales_metrics WHERE date = '2025-06-01' GROUP BY item_id ORDER BY total_ad_sales DESC LIMIT 10;SELECT item_id, SUM(ad_sales) AS total_ad_sales FROM ad_sales_metrics WHERE date = '2025-06-01' GROUP BY item_id ORDER BY total_ad_sales DESC LIMIT 10;"
    # return response.strip()







# barchart
#         raw_sql_text = '''SELECT asm.ad_sales, tsm.total_sales, asm.ad_spend
# FROM ad_sales_metrics AS asm
# INNER JOIN total_sales_metrics AS tsm
#     ON asm.item_id = tsm.item_id AND asm.date = tsm.date
# WHERE asm.item_id = 4 AND asm.date = '2025-06-01';'''
        # line chart
#         raw_sql_text = '''SELECT 
#     asm.date, 
#     SUM(asm.ad_sales) AS total_ad_sales, 
#     SUM(asm.units_sold) AS total_units_sold_from_ads,
#     SUM(tsm.total_units_ordered) AS total_units_ordered
# FROM ad_sales_metrics AS asm
# INNER JOIN total_sales_metrics AS tsm
#     ON asm.item_id = tsm.item_id AND asm.date = tsm.date
# WHERE asm.date BETWEEN '2025-06-01' AND '2025-06-30'
# GROUP BY asm.date
# ORDER BY asm.date;'''
        # scatter plot
#         raw_sql_text = '''SELECT impressions, clicks
# FROM ad_sales_metrics
# WHERE date = '2025-06-01';'''
        # histogram
#         raw_sql_text = '''SELECT item_id, SUM(ad_spend) * 1.0 / SUM(clicks) AS cpc
# FROM ad_sales_metrics
# WHERE clicks > 0
# GROUP BY item_id
# ORDER BY cpc DESC
# LIMIT 1;'''
        # raw_sql_text = '''SELECT ad_spend FROM ad_sales_metrics WHERE item_id = 0 AND date = '2025-06-01';'''
