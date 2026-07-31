from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
import csv

from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])
analytics_service = AnalyticsService()

@router.get("/roi")
async def get_roi():
    return analytics_service.get_roi_metrics()

@router.get("/kpis")
async def get_kpis(timeframe: str = "month"):
    return analytics_service.get_kpis(timeframe)

@router.get("/trends")
async def get_trends():
    return analytics_service.get_trends()

@router.get("/cohort")
async def get_cohorts():
    return analytics_service.get_cohort_analysis()

@router.get("/export")
async def export_report(format: str = "csv", report_type: str = "monthly"):
    # Generate mock CSV for export
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Revenue", "Margin", "Acceptance Rate"])
    
    trends = analytics_service.get_trends()
    for row in trends:
        writer.writerow([row["date"], row["revenue"], row["margin"], "88%"])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{report_type}.csv"}
    )
