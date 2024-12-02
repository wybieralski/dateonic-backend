# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.param_functions import Form
from ..services.gpt import analyze_with_gpt
from ..services.data import process_file_content, prepare_chart_data
from ..models.schemas import AnalysisResponse
from .auth_routes import auth_router
from ..utils.logger import logger, handle_errors
from typing import Optional

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
@handle_errors
async def analyze_file(
    file: UploadFile = File(...),
    user_question: Optional[str] = Form(None)
):
    logger.info(f"Starting analysis for file: {file.filename}")
    if user_question:
        logger.info(f"User question: {user_question}")

    try:
        # Read file content
        logger.debug("Reading file content")
        content = await file.read()

        # Process file
        logger.debug("Processing file content")
        df = process_file_content(content, file.filename)
        logger.info(f"Successfully processed file. DataFrame shape: {df.shape}")

        # Get analysis from GPT
        logger.info("Starting GPT analysis")
        analysis = analyze_with_gpt(df, user_question=user_question)
        logger.info("GPT analysis completed successfully")

        # Prepare chart data
        logger.debug("Preparing chart data")
        for chart in analysis["suggested_charts"]:
            logger.debug(f"Preparing data for chart: {chart['title']}")
            chart["data"] = prepare_chart_data(df, chart)

        logger.info("Analysis completed successfully")
        return analysis

    except Exception as e:
        logger.error(f"Error during file analysis: {str(e)}", exc_info=True)
        if "quota exceeded" in str(e).lower():
            raise HTTPException(
                status_code=402,
                detail="OpenAI API quota exceeded. Please check your API credits."
            )
        raise HTTPException(status_code=400, detail=str(e))


# Include auth router
router.include_router(auth_router, prefix="/auth", tags=["auth"])