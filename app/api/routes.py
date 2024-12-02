# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.gpt import analyze_with_gpt
from ..services.data import process_file_content, prepare_chart_data
from ..models.schemas import AnalysisResponse
from .auth_routes import auth_router
from ..utils.logger import logger, handle_errors

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
@handle_errors
async def analyze_file(file: UploadFile = File(...)):
    logger.info(f"Starting analysis for file: {file.filename}")

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
        analysis = analyze_with_gpt(df)
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