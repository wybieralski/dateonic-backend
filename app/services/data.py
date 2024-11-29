import pandas as pd
from io import StringIO, BytesIO
from typing import Dict, Any, List

def prepare_chart_data(df: pd.DataFrame, chart_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Przygotowuje dane dla wykresu na podstawie jego konfiguracji"""
    if chart_config["type"] in ["line", "bar"]:
        # Dla wykresów liniowych i słupkowych używamy wszystkich wskazanych kolumn
        return df[chart_config["data_columns"]].to_dict('records')
    elif chart_config["type"] == "pie":
        # Dla wykresu kołowego przygotowujemy dane w formacie {name, value}
        column = chart_config["data_columns"][0]
        value_counts = df[column].value_counts()
        return [{"name": str(name), "value": int(value)}
                for name, value in value_counts.items()]
    return []

def process_file_content(content: bytes, filename: str) -> pd.DataFrame:
    """Przetwarza zawartość pliku do DataFrame"""
    try:
        if filename.endswith('.csv'):
            return pd.read_csv(StringIO(content.decode('utf-8')))
        elif filename.endswith(('.xls', '.xlsx')):
            return pd.read_excel(BytesIO(content))
        raise ValueError("Unsupported file format")
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise ValueError(f"Failed to process file: {str(e)}")