# 🧠 E-commerce AI Data Agent – Intelligent Analytics Assistant

> **Transforming raw data into actionable insights through natural language.**
>
> Built with **Flask** | **Google Gemini** | **Plotly** | **SQLite**
> 💡 By **Sumit Dhar**

---

## 🚀 Overview

The **E-commerce AI Data Agent** is a cutting-edge, AI-powered analytics tool designed to democratize data access. It enables users to ask complex e-commerce data questions in plain English, receiving instant, human-friendly answers and interactive visualizations. This agent bridges the gap between raw data and actionable insights, making data analysis accessible to everyone.

-   **🧠 LLM (Google Gemini)**: Powers intelligent understanding, SQL query generation, and humanized responses.
-   **🧮 Local Data Processing**: Efficiently queries structured e-commerce datasets stored in a local SQLite database.
-   **📊 Dynamic Visualizations**: Automatically displays interactive Plotly charts for suitable query results.
-   **🖥️ Modern Web UI (Flask)**: Provides a sleek, animated, and responsive interface for seamless user interaction.
-   **💻 CLI & API Access**: Offers both a command-line interface for direct interaction and comprehensive API endpoints for external integration.

---

## 🌟 Key Features

-   **🔍 Natural Language Querying**: Ask questions like "What is my total sales?" or "Calculate RoAS".
-   **🤖 Intelligent SQL Generation**: Leverages Google Gemini to automatically translate natural language into optimized SQL.
-   **📈 Contextual Data Visualization**: Automatically generates interactive **Plotly charts** (bar, line, scatter, histograms) based on query results, providing visual insights.
-   **💬 Progressive UI & Animations**: Engaging user experience with dynamic loading messages, text-by-text answer generation, floating titles, and interactive button/label effects.
-   **💡 Dark/Light Mode Toggle**: Personalize the interface with a seamless theme switch.
-   **🌐 Comprehensive API Endpoints**: Exposes dedicated API routes for both frontend communication and robust external application integration.
-   **🛠️ Modular & Maintainable**: Built with a clean, professional folder structure for easy understanding and future expansion.

---

## 📚 Technologies Used

-   **🧠 Google Gemini API: Powers natural language understanding, SQL generation, and humanized responses.".
-   **🐍 Python 3.10+: Core programming language.
-   **🌐 Flask: Lightweight web framework for the backend API and UI.
-   **📊 Plotly: For creating rich, interactive data visualizations.
-   **🧮 SQLite3: Efficient local relational database for data storage.
-   **🎨 HTML, CSS, JavaScript: Building the dynamic and engaging frontend interface.
-   **🐼 Pandas: For robust data manipulation and integration with SQL/CSVs.
-   **✨ python-dotenv: For secure management of environment variables.
  
---

## 🗂️ Project Architecture

```text
ecom_ai_assistant/                     # Main project root directory
├── .env                               # Environment variables (e.g., GOOGLE_API_KEY)
├── .gitignore                         # Files/folders ignored by Git (e.g., .env, __pycache__, ecom.db)
├── Procfile                           # Web server configuration for deployment (e.g., gunicorn)
├── README.md                          # This file
├── requirements.txt                   # All Python dependencies

├── app/                               # Main application source code (Python package)
│   ├── __init__.py                    # Marks 'app' as a Python package
│   ├── main.py                        # Flask application instance & API endpoints
│   │
│   ├── data/                          # Raw CSV datasets
│   │   ├── ad_sales.csv
│   │   ├── total_sales.csv
│   │   └── eligibility.csv
│   │
│   ├── db/                            # Database interaction layer
│   │   ├── __init__.py                # Marks 'db' as a Python subpackage
│   │   ├── schema.sql                 # SQL DDL for database creation
│   │   └── init_db.py                 # Script to initialize SQLite DB and load data
│   │
│   ├── models/                            
│   │   ├── __init__.py                
│   │   └── gemini_models.py                               
│   │
│   ├── llm/                           # Large Language Model integration
│   │   ├── __init__.py                # Marks 'llm' as a Python subpackage
│   │   ├── gemini_agent.py            # Handles Gemini API calls (SQL generation, humanization)
│   │   └── prompts/                   # Dedicated folder for LLM prompt templates
│   │       ├── __init__.py
│   │       ├── humanization_prompts.py
│   │       └── sql_generation_prompts.py
│   │
│   ├── static/                        # Static assets served by Flask
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── main.js
│   │
│   └── templates/                     # Jinja2 HTML templates
│       └── index.html
│   │
│   └── utils/                         # General utility functions
│       ├── __init__.py                # Marks 'utils' as a Python subpackage
│       └── charts.py                  # Plotly chart generation logic
│
├── scripts/                           # Standalone utility scripts
│   ├── cli_ask.py                     # CLI tool for direct questions
│   └── testings.py                    # Script for basic functionality tests
│
└── ecom.db                            # SQLite database file (auto-created on first run, explicitly ignored by Git)
```

---

## 📄 License

This project is licensed under the MIT License – feel free to use, modify, and distribute it with proper credit.

-   **Google & the Gemini team for their powerful LLM APIs.
-   **Plotly for their exceptional charting libraries.
-   **The Flask and Pandas communities for their robust frameworks.
-   **All open-source contributors who inspire modern development practices.

---

## 🤝 Connect with Me

-   **🔗 LinkedIn: linkedin.com/in/sumit-dhar/
-   **💻 GitHub: github.com/dhar-sumit
-   **📧 Email: sumiths.0015@gmail.com

---
