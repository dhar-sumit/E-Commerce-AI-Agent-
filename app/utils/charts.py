# utils/chart_utils.py

import plotly.express as px
import pandas as pd
import json

def generate_chart(df: pd.DataFrame, question: str):
    """
    Generates a plotly chart based on the data and attempts to infer the best type.
    Prioritizes meaningful visualizations.
    """
    if df.empty:
        print("[Chart Info]: DataFrame is empty, cannot generate chart.")
        return None  # No data, no chart

    try:
        fig = None

        # Identify column types
        numeric_cols = df.select_dtypes(include=['int', 'float']).columns.tolist()
        text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        
        # Heuristic for potential date columns (often stored as text)
        date_cols = [col for col in text_cols if 'date' in col.lower() or 'datetime' in col.lower()]
        other_categorical_cols = [col for col in text_cols if col not in date_cols]

        # --- Charting Logic based on Data Shape and Types ---

        # Scenario 1: Single value result (e.g., SUM, COUNT of a single total) - cannot plot meaningfully
        if df.shape == (1, 1):
            print("[Chart Info]: Single value result, cannot generate chart.")
            return None 
        
        # Scenario 2: Single row with multiple numeric values (e.g., ad_sales, total_sales for one item)
        # This will melt the data into a bar chart
        if df.shape[0] == 1 and len(numeric_cols) >= 2:
            temp_df = df.copy() 
            for col in numeric_cols:
                temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce') 
            
            df_melted = temp_df[numeric_cols].melt(var_name='Metric', value_name='Value')
            df_melted.dropna(subset=['Value'], inplace=True) 

            if df_melted.empty: 
                print("[Chart Info]: Melted DataFrame is empty after numeric coercion, cannot generate chart.")
                return None

            fig = px.bar(df_melted, x='Metric', y='Value', 
                         title="Metrics Comparison for Single Entry",
                         labels={'Metric': 'Metric', 'Value': 'Value'},
                         color_discrete_sequence=[px.colors.qualitative.Plotly[0], px.colors.qualitative.Plotly[1]]) 

        # Scenario 3: Time Series Data (Date + 1 or more numeric columns, multiple rows)
        # This is now an 'elif' to ensure it only runs if the single-row case above was not met
        elif len(date_cols) >= 1 and len(numeric_cols) >= 1 and df.shape[0] > 1: # Must have numeric cols to plot
            x_col_date = date_cols[0]
            # y_cols_for_plot = [col for col in numeric_cols if col != x_col_date] # Original line. This might be stripping out a numeric column if named similar to date.
            
            # --- CRITICAL FIX FOR TIME SERIES ---
            # Ensure we only pick numeric columns that are NOT the date column
            # And also ensure they are actually numeric types in the DataFrame right now
            y_cols_for_plot = []
            for col in numeric_cols:
                if col.lower() not in [dc.lower() for dc in date_cols]: # Check against all date_cols, not just x_col_date
                    if pd.api.types.is_numeric_dtype(df[col]): # Verify dtype for robustness
                        y_cols_for_plot.append(col)
            # --- END CRITICAL FIX ---

            # If no suitable numeric columns found to plot against date, pass to next condition
            if not y_cols_for_plot:
                print(f"[Chart Info]: No suitable Y-axis numeric columns found for time series plot against '{x_col_date}'.")
                pass # Continue to next conditions
            else:
                temp_df = df.copy() # Work on a copy
                try:
                    temp_df[x_col_date] = pd.to_datetime(temp_df[x_col_date])
                    # Ensure all Y-axis columns are numeric and drop NaNs
                    for y_col in y_cols_for_plot:
                        temp_df[y_col] = pd.to_numeric(temp_df[y_col], errors='coerce')
                    temp_df.dropna(subset=[x_col_date] + y_cols_for_plot, inplace=True) 

                    if temp_df.empty:
                        print("[Chart Info]: DataFrame empty after date/numeric coercion for time series.")
                        pass # Continue if data becomes empty
                    else:
                        if len(y_cols_for_plot) > 1:
                            fig = px.line(temp_df, x=x_col_date, y=y_cols_for_plot, 
                                          title=f"Trends Over Time",
                                          labels={x_col_date: 'Date'},
                                          line_shape="spline") # Added spline for smoother lines
                        else: 
                            fig = px.line(temp_df, x=x_col_date, y=y_cols_for_plot[0], 
                                          title=f"{y_cols_for_plot[0].replace('_', ' ').title()} Over Time",
                                          labels={x_col_date: 'Date'},
                                          line_shape="spline") # Added spline
                except Exception as date_error:
                    print(f"[Chart Info]: Date conversion/plotting failed for time series ({date_error}), attempting other chart types.")
                    pass 
        
        # Scenario 4: One "ID-like" numeric column and one other numeric column (Bar Chart)
        elif not fig and len(numeric_cols) >= 2 and df.shape[0] > 1: # Added 'elif not fig'
            id_like_numeric_cols = [col for col in numeric_cols if 'item_id' in col.lower() or col.lower() == 'id']
            
            if len(id_like_numeric_cols) >= 1: # Check if an ID column is present
                x_col_id = id_like_numeric_cols[0]
                y_cols_for_bar = [col for col in numeric_cols if col != x_col_id] 

                if not y_cols_for_bar:
                    print(f"[Chart Info]: No suitable Y-column found for ID-based bar chart with X='{x_col_id}'.")
                    pass
                else:
                    y_col_value = y_cols_for_bar[0] 
                    temp_df = df.copy()
                    temp_df[y_col_value] = pd.to_numeric(temp_df[y_col_value], errors='coerce')
                    temp_df.dropna(subset=[y_col_value], inplace=True)
                    if temp_df.empty: 
                        print("[Chart Info]: DataFrame empty after numeric coercion for ID-based bar chart.")
                        pass
                    else:
                        fig = px.bar(temp_df, x=x_col_id, y=y_col_value,
                                     title=f"{y_col_value.replace('_', ' ').title()} by {x_col_id.replace('_', ' ').title()}",
                                     labels={x_col_id: x_col_id.replace('_', ' ').title(), y_col_value: y_col_value.replace('_', ' ').title()})

            # Scenario 5: Two or more Numeric Columns (Scatter Plot) - General case if not ID-based
            if not fig and len(numeric_cols) >= 2 and df.shape[0] > 1: 
                temp_df = df.copy()
                for col in numeric_cols:
                    temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce')
                temp_df.dropna(subset=numeric_cols, inplace=True)
                if temp_df.empty: 
                    print("[Chart Info]: DataFrame empty after numeric coercion for scatter plot.")
                    pass
                else:
                    fig = px.scatter(temp_df, x=numeric_cols[0], y=numeric_cols[1], 
                                     title=f"Relationship: {numeric_cols[0].replace('_', ' ').title()} vs. {numeric_cols[1].replace('_', ' ').title()}",
                                     labels={numeric_cols[0]: numeric_cols[0].replace('_', ' ').title(), numeric_cols[1]: numeric_cols[1].replace('_', ' ').title()},
                                     hover_data=temp_df.columns)

        # Scenario 6: One Numeric Column & One Categorical Column (Bar Chart)
        elif not fig and len(numeric_cols) >= 1 and len(other_categorical_cols) >= 1 and df.shape[0] > 1:
            temp_df = df.copy()
            for col in numeric_cols: temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce')
            temp_df.dropna(subset=[numeric_cols[0]], inplace=True)
            if temp_df.empty: 
                print("[Chart Info]: DataFrame empty after numeric coercion for categorical bar chart.")
                pass
            else:
                fig = px.bar(temp_df, x=other_categorical_cols[0], y=numeric_cols[0], 
                             title=f"{numeric_cols[0].replace('_', ' ').title()} by {other_categorical_cols[0].replace('_', ' ').title()}",
                             labels={other_categorical_cols[0]: other_categorical_cols[0].replace('_', ' ').title(), numeric_cols[0]: numeric_cols[0].replace('_', ' ').title()})
                
                if len(numeric_cols) == 1 and ('sum' in numeric_cols[0].lower() or 'count' in numeric_cols[0].lower()):
                    try:
                        if (temp_df[numeric_cols[0]] >= 0).all():
                            fig_pie = px.pie(temp_df, names=other_categorical_cols[0], values=numeric_cols[0], 
                                             title=f"Distribution of {other_categorical_cols[0].replace('_', ' ').title()} by {numeric_cols[0].replace('_', ' ').title()}")
                        pass
                    except Exception:
                        pass

        # Scenario 7: Only one numeric column (Histogram)
        elif not fig and len(numeric_cols) == 1 and df.shape[0] > 1: 
            temp_df = df.copy()
            temp_df[numeric_cols[0]] = pd.to_numeric(temp_df[numeric_cols[0]], errors='coerce')
            temp_df.dropna(subset=[numeric_cols[0]], inplace=True)
            if temp_df.empty: 
                print("[Chart Info]: DataFrame empty after numeric coercion for histogram.")
                pass
            else:
                fig = px.histogram(temp_df, x=numeric_cols[0], 
                                   title=f"Distribution of {numeric_cols[0].replace('_', ' ').title()}",
                                   labels={numeric_cols[0]: numeric_cols[0].replace('_', ' ').title()})

        else:
            print("[Chart Info]: No suitable chart type found for the given data structure.")
            return None 

        if fig:
            fig.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                title_font_size=18,
                title_x=0.5,
                height=400,
                hovermode="x unified" if len(date_cols) >=1 else "closest"
            )
            return json.loads(fig.to_json()) 
        else:
            print("[Chart Info]: Figure object not created after charting logic - Fallback.")
            return None 
            
    except Exception as e:
        print(f"[Chart Error]: An unhandled error occurred during chart generation for question: '{question}' - Error: {e}")
        return None