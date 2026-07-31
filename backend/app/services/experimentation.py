import hashlib
from scipy import stats
import math

class ExperimentationService:
    def assign_group(self, user_id: str, experiment_id: str) -> str:
        """Deterministically assigns a user to control or treatment."""
        hash_input = f"{user_id}-{experiment_id}".encode('utf-8')
        hash_val = int(hashlib.md5(hash_input).hexdigest(), 16)
        return "treatment" if hash_val % 2 == 0 else "control"

    def calculate_results(self, control_conversions: int, control_visitors: int,
                          treatment_conversions: int, treatment_visitors: int) -> dict:
        """Calculates statistical significance using Chi-squared test for conversion rates."""
        if control_visitors == 0 or treatment_visitors == 0:
            return {"p_value": None, "confidence": 0.0, "significant": False}

        control_failures = control_visitors - control_conversions
        treatment_failures = treatment_visitors - treatment_conversions
        
        # Contingency table
        observed = [
            [control_conversions, control_failures],
            [treatment_conversions, treatment_failures]
        ]
        
        try:
            chi2, p_value, dof, expected = stats.chi2_contingency(observed)
            confidence = 1 - p_value
            significant = bool(p_value < 0.05)
            return {
                "p_value": round(p_value, 4),
                "confidence": round(confidence, 4),
                "significant": significant
            }
        except ValueError:
            return {"p_value": None, "confidence": 0.0, "significant": False}

    def power_analysis(self, expected_effect_size: float, confidence: float = 0.95, power: float = 0.80) -> dict:
        """Estimates required sample size using standard normal distributions."""
        # Z-scores for alpha and power
        alpha = 1 - confidence
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        # Simplified sample size calculation for proportions
        # Assuming baseline conversion of 5% (0.05) for demonstration
        p1 = 0.05
        p2 = p1 * (1 + expected_effect_size)
        p_pool = (p1 + p2) / 2
        
        numerator = (z_alpha * math.sqrt(2 * p_pool * (1 - p_pool)) + z_beta * math.sqrt(p1*(1-p1) + p2*(1-p2))) ** 2
        denominator = (p1 - p2) ** 2
        
        if denominator == 0:
            sample_size = 0
        else:
            sample_size = int(math.ceil(numerator / denominator))
        
        # Estimate duration assuming 100 visitors per day
        visitors_per_day = 100
        duration = math.ceil((sample_size * 2) / visitors_per_day)
        
        return {
            "required_sample_size": sample_size * 2, # Total for both groups
            "estimated_duration_days": duration
        }
