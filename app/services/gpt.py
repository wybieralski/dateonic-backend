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
    Przeanalizuj ten zbiór danych i zaproponuj dokładnie 4 różne wizualizacje:
    {json.dumps(data_info, indent=2)}

    MUSISZ zwrócić dokładnie 4 wykresy w tej kolejności:
    1. Wykres liniowy pokazujący trendy lub zmiany w czasie
    2. Wykres słupkowy porównujący kategorie lub grupy  
    3. Wykres kołowy pokazujący rozkład lub kompozycję
    4. Wykres słupkowy pokazujący inne istotne porównanie

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

    Upewnij się, że:
    1. Każdy wykres używa odpowiednich kolumn ze zbioru danych
    2. Wykres liniowy pokazuje znaczące trendy
    3. Wykresy słupkowe porównują różne aspekty danych
    4. Wykres kołowy pokazuje znaczący rozkład
    5. Twoje odpowiedzi - insighty - są w jezyku polskim
    """

    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system",
             "content": "Jesteś doświadczonym data analitykiem + analitykiem biznesowym. Stwórz sensowne wizualizacje które pomogą zrozumiec te dane i wyciągnać z nich wnioski biznesowe"},
             # "content": "You are a data analysis expert. Create meaningful visualizations that help understand the data."},
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