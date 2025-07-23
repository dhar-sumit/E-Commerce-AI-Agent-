import google.generativeai as genai

# Model for generating SQL queries
SQL_GEN_MODEL = genai.GenerativeModel('models/gemini-1.5-flash') 

# Model for humanizing the final answer
HUMANIZE_MODEL = genai.GenerativeModel('models/gemini-1.5-flash') 