from openai import OpenAI
from ..config import settings
import json
import pandas as pd

client = OpenAI(api_key=settings.openai_api_key)


def analyze_with_gpt(df: pd.DataFrame):
    # Przygotuj informacje o datasecie
    data_info = {
        'columns': df.columns.tolist(),
        'sample': df.head(5).to_dict('records'),
        'stats': df.describe().to_dict(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'row_count': len(df)
    }

    prompt = f"""
    Analyze this dataset and suggest exactly 4 different visualizations:
    {json.dumps(data_info, indent=2)}

    You MUST return exactly 4 charts in this order:
    1. A line chart showing trends or changes over time
    2. A bar chart comparing categories or groups
    3. A pie chart showing distribution or composition
    4. A bar chart showing another important comparison

    Return ONLY JSON with exactly this structure:
    {{
        "suggested_charts": [
            {{
                "type": "line",
                "title": "chart_title",
                "description": "why this visualization is useful",
                "data_columns": ["x_axis_column", "y_axis_column1", "y_axis_column2"],
                "data": []
            }},
            {{
                "type": "bar",
                "title": "chart_title",
                "description": "why this visualization is useful",
                "data_columns": ["category_column", "value_column"],
                "data": []
            }},
            {{
                "type": "pie",
                "title": "chart_title",
                "description": "why this visualization is useful",
                "data_columns": ["category_column"],
                "data": []
            }},
            {{
                "type": "bar",
                "title": "chart_title",
                "description": "why this visualization is useful",
                "data_columns": ["category_column", "value_column"],
                "data": []
            }}
        ],
        "key_insights": [
            "insight about trends",
            "insight about first comparison",
            "insight about distribution",
            "insight about second comparison"
        ],
        "additional_analysis_suggested": [
            "suggestion 1",
            "suggestion 2"
        ]
    }}

    Ensure that:
    1. Each chart uses appropriate columns from the dataset
    2. Line chart shows meaningful trends
    3. Bar charts compare different aspects of the data
    4. Pie chart shows a meaningful distribution
    """

    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system",
             "content": "You are a data analysis expert. Create meaningful visualizations that help understand the data."},
            {"role": "user", "content": prompt}
        ]
    )

    analysis = json.loads(response.choices[0].message.content)

    # Prepare data for each chart type
    for chart in analysis["suggested_charts"]:
        if chart["type"] == "line" or chart["type"] == "bar":
            chart["data"] = df[chart["data_columns"]].to_dict('records')
        elif chart["type"] == "pie":
            column = chart["data_columns"][0]
            value_counts = df[column].value_counts()
            chart["data"] = [{"name": str(name), "value": float(value)}
                             for name, value in value_counts.items()]

    return analysis