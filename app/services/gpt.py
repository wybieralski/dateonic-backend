from openai import OpenAI
from ..config import settings
import json
import pandas as pd
from ..utils.logger import logger
from fastapi import HTTPException
from typing import Optional

client = OpenAI(api_key=settings.openai_api_key)


def analyze_with_gpt(df: pd.DataFrame, user_question: Optional[str] = None):
    try:
        logger.info("Preparing data for GPT analysis")
        if user_question:
            logger.info(f"User question: {user_question}")

        # Prepare dataset information
        data_info = {
            'columns': df.columns.tolist(),
            'sample': df.head(5).to_dict('records'),
            'stats': df.describe().to_dict(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'row_count': len(df)
        }

        logger.debug(f"Dataset info prepared. Columns: {', '.join(data_info['columns'])}")

        # Base prompt
        prompt = f"""
        Przeanalizuj ten zbiór danych:
        {json.dumps(data_info, indent=2)}
        """

        # Add user question if provided
        if user_question:
            prompt += f"""

        Dodatkowe pytanie od uzytkownika: {user_question}

        Dostosuj swoją analizę, aby odpowiedzieć na to pytanie, ale także pokaż inne ważne aspekty danych. 
        Jesli w pytaniu nie ma nic zwiazanego z danymi to je ignoruj.
        """

        prompt += """
        MUSISZ zwrócić dokładnie 4 wykresy w tej kolejności:
        1. Wykres liniowy pokazujący trendy lub zmiany w czasie
        2. Wykres słupkowy porównujący kategorie lub grupy  
        3. Wykres kołowy pokazujący rozkład lub kompozycję
        4. Wykres słupkowy pokazujący inne istotne porównanie

        Return ONLY JSON with exactly this structure:
        {
            "suggested_charts": [
                {
                    "type": "line",
                    "title": "chart_title",
                    "description": "why this visualization is useful",
                    "data_columns": ["x_axis_column", "y_axis_column1", "y_axis_column2"],
                    "data": []
                },
                {
                    "type": "bar",
                    "title": "chart_title",
                    "description": "why this visualization is useful",
                    "data_columns": ["category_column", "value_column"],
                    "data": []
                },
                {
                    "type": "pie",
                    "title": "chart_title",
                    "description": "why this visualization is useful",
                    "data_columns": ["category_column"],
                    "data": []
                },
                {
                    "type": "bar",
                    "title": "chart_title",
                    "description": "why this visualization is useful",
                    "data_columns": ["category_column", "value_column"],
                    "data": []
                }
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
        }

        Upewnij się, że:
        1. Każdy wykres używa odpowiednich kolumn ze zbioru danych
        2. Wykres liniowy pokazuje znaczące trendy
        3. Wykresy słupkowe porównują różne aspekty danych
        4. Wykres kołowy pokazuje znaczący rozkład
        5. Twoje odpowiedzi - insighty - są w jezyku polskim
        """

        logger.info("Sending request to OpenAI API")
        try:
            system_prompt = "Jesteś doświadczonym data analitykiem + analitykiem biznesowym. "
            if user_question:
                system_prompt += "Skup się na odpowiedzi na pytanie użytkownika, pokazując odpowiednie wizualizacje i wnioski. "
            system_prompt += "Stwórz sensowne wizualizacje które pomogą zrozumiec te dane i wyciągnać z nich wnioski biznesowe"

            response = client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            logger.info("Successfully received response from OpenAI API")

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            if "insufficient_quota" in str(e).lower():
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI API quota exceeded. Please check your API credits."
                )
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI API error: {str(e)}"
            )

        try:
            analysis = json.loads(response.choices[0].message.content)
            logger.debug("Successfully parsed GPT response")
        except json.JSONDecodeError as e:
            logger.error("Failed to parse GPT response as JSON", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Failed to parse analysis results"
            )

        # Prepare data for each chart type
        logger.info("Preparing chart data")
        for chart in analysis["suggested_charts"]:
            logger.debug(f"Processing chart type: {chart['type']}")
            if chart["type"] in ["line", "bar"]:
                try:
                    chart["data"] = df[chart["data_columns"]].to_dict('records')
                except KeyError as e:
                    logger.error(f"Missing column in DataFrame: {str(e)}", exc_info=True)
                    raise HTTPException(
                        status_code=500,
                        detail=f"Column not found in data: {str(e)}"
                    )
            elif chart["type"] == "pie":
                try:
                    column = chart["data_columns"][0]
                    value_counts = df[column].value_counts()
                    chart["data"] = [{"name": str(name), "value": float(value)}
                                     for name, value in value_counts.items()]
                except Exception as e:
                    logger.error(f"Error preparing pie chart data: {str(e)}", exc_info=True)
                    raise HTTPException(
                        status_code=500,
                        detail="Error preparing chart data"
                    )

        logger.info("Analysis completed successfully")
        return analysis

    except Exception as e:
        logger.error(f"Unexpected error in analyze_with_gpt: {str(e)}", exc_info=True)
        raise