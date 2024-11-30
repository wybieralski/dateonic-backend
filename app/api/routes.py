# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.gpt import analyze_with_gpt
from ..services.data import process_file_content, prepare_chart_data
from ..models.schemas import AnalysisResponse
from .auth_routes import auth_router  # Dodajemy import routera autoryzacji

router = APIRouter()

# Istniejący endpoint analizy
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = process_file_content(content, file.filename)

        # Get analysis from GPT
        analysis = analyze_with_gpt(df)

        # Prepare data for each chart
        for chart in analysis["suggested_charts"]:
            chart["data"] = prepare_chart_data(df, chart)

        return analysis

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Dodajemy router autoryzacji jako sub-router
router.include_router(auth_router, prefix="/auth", tags=["auth"])