from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union

class ChartData(BaseModel):
    """
    Reprezentacja danych pojedynczego wykresu.
    """
    type: str = Field(..., description="Typ wykresu (line, bar, pie)")
    title: str = Field(..., description="Tytuł wykresu")
    description: str = Field(..., description="Opis wykresu i jego znaczenia")
    data_columns: List[str] = Field(..., description="Lista kolumn użytych w wykresie")
    data: List[Dict[str, Union[str, float, int]]] = Field(
        default=[],
        description="Dane wykresu w formacie zależnym od typu wykresu"
    )

class AnalysisResponse(BaseModel):
    """
    Pełna odpowiedź z analizą danych.
    """
    suggested_charts: List[ChartData] = Field(
        ...,
        description="Lista sugerowanych wykresów"
    )
    key_insights: List[str] = Field(
        ...,
        description="Lista głównych wniosków z analizy"
    )
    additional_analysis_suggested: List[str] = Field(
        ...,
        description="Lista sugestii dodatkowych analiz"
    )

class AnalysisRequest(BaseModel):
    """
    Request model dla analizy danych.
    """
    file_content: str = Field(..., description="Zawartość pliku do analizy")
    user_question: Optional[str] = Field(
        None,
        description="Opcjonalne pytanie użytkownika dotyczące analizy"
    )