import pytest
from app.services.analytics import AnalyticsService

def test_get_roi_metrics():
    service = AnalyticsService()
    res = service.get_roi_metrics()
    assert "total_savings" in res
    assert "revenue_lift_percent" in res

def test_get_kpis():
    service = AnalyticsService()
    res = service.get_kpis()
    assert "revenue" in res
    assert "margin" in res

def test_get_trends():
    service = AnalyticsService()
    res = service.get_trends()
    assert isinstance(res, list)
    assert len(res) > 0
    assert "date" in res[0]
    assert "revenue" in res[0]

def test_get_cohort_analysis():
    service = AnalyticsService()
    res = service.get_cohort_analysis()
    assert "Electronics" in res
    assert "acceptance_rate" in res["Electronics"]
