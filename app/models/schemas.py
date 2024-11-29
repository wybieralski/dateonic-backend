from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChartConfig(BaseModel):
    type: str
    title: str
    description: str
    data_columns: List[str]
    data: List[Dict[str, Any]]  # Zawsze lista słowników
    config: Dict[str, Any] = {}

class AnalysisResponse(BaseModel):
    suggested_charts: List[ChartConfig]
    key_insights: List[str]
    additional_analysis_suggested: List[str]