import pytest
from app.services.experimentation import ExperimentationService

def test_assign_group_deterministic():
    service = ExperimentationService()
    user_id = "user-123"
    exp_id = "exp-456"
    
    # Should be deterministic
    group1 = service.assign_group(user_id, exp_id)
    group2 = service.assign_group(user_id, exp_id)
    
    assert group1 == group2

def test_calculate_results_significant():
    service = ExperimentationService()
    # Control: 100/1000 (10%)
    # Treatment: 150/1000 (15%)
    res = service.calculate_results(100, 1000, 150, 1000)
    
    assert res["significant"] is True
    assert res["p_value"] < 0.05
    assert res["confidence"] > 0.95

def test_calculate_results_insignificant():
    service = ExperimentationService()
    # Control: 100/1000 (10%)
    # Treatment: 102/1000 (10.2%)
    res = service.calculate_results(100, 1000, 102, 1000)
    
    assert res["significant"] is False
    assert res["p_value"] > 0.05

def test_power_analysis():
    service = ExperimentationService()
    # Small effect size requires larger sample
    res_small = service.power_analysis(0.05)
    # Large effect size requires smaller sample
    res_large = service.power_analysis(0.20)
    
    assert res_small["required_sample_size"] > res_large["required_sample_size"]
