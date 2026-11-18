"""
Market Demand Forecasting Model (SB2/US38).
Projects labor market demand indices and trending career pathways using linear trend analysis.
NOTE: Historical demand series uses SAMPLE DATA per Issue #1 in analysis.
"""

from typing import Any, Dict, List
import numpy as np


class DemandForecastModel:
    """Labor market demand forecasting engine using trend extrapolation."""

    # Historical demand index across 5 consecutive years (2021-2025) (SAMPLE DATA)
    DEMAND_DATA = {
        "AI/ML Engineer": [100, 125, 160, 210, 275],
        "Data Scientist": [100, 115, 135, 155, 180],
        "Cybersecurity Analyst": [100, 118, 140, 165, 195],
        "DevOps Engineer": [100, 115, 132, 152, 175],
        "Software Engineer": [100, 110, 122, 136, 152],
        "Healthcare Informatics": [100, 112, 128, 145, 168],
        "Product Manager": [100, 108, 120, 132, 148],
        "UX Designer": [100, 106, 115, 125, 138],
        "Business Analyst": [100, 105, 112, 120, 130],
        "Financial Analyst": [100, 104, 110, 116, 124],
    }

    def __init__(self):
        self.history_years = np.array([0, 1, 2, 3, 4], dtype=np.float32)

    def forecast_demand(self, career: str, years_ahead: int = 2) -> Dict[str, Any]:
        """
        Extrapolate labor demand index for a career using linear trend analysis.
        Returns: {career, current_index, forecasted_index, cagr_growth_rate, trend_slope, outlook}
        """
        series = self.DEMAND_DATA.get(career, [100, 110, 120, 130, 140])
        y = np.array(series, dtype=np.float32)

        # Fit linear trend line: y = slope * x + intercept
        slope, intercept = np.polyfit(self.history_years, y, 1)

        current_val = float(series[-1])
        future_x = float(len(series) - 1 + years_ahead)
        forecast_val = float(max(10.0, slope * future_x + intercept))

        # Growth metrics
        annual_growth_rate = float(slope / current_val)
        cagr = float(((forecast_val / current_val) ** (1.0 / max(1, years_ahead))) - 1.0)

        if slope >= 30.0:
            outlook = "Hyper-Growth"
        elif slope >= 18.0:
            outlook = "Rapid Growth"
        elif slope >= 10.0:
            outlook = "Steady Growth"
        else:
            outlook = "Stable"

        return {
            "career": career,
            "years_ahead": years_ahead,
            "current_demand_index": round(current_val, 1),
            "forecasted_demand_index": round(forecast_val, 1),
            "projected_gain_percentage": round(((forecast_val - current_val) / current_val) * 100.0, 1),
            "cagr_growth_rate": round(cagr * 100.0, 2),
            "trend_slope": round(float(slope), 2),
            "market_outlook": outlook,
        }

    def get_trending_careers(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rank all careers by growth momentum and demand slope.
        """
        forecasts = [self.forecast_demand(c, years_ahead=2) for c in self.DEMAND_DATA]
        forecasts.sort(key=lambda x: x["trend_slope"], reverse=True)
        return forecasts[:top_k]

    def get_market_insights(self) -> Dict[str, Any]:
        """
        Produce macro hiring insights across all domains.
        """
        ranked = self.get_trending_careers(top_k=len(self.DEMAND_DATA))
        top_growth = ranked[0]
        most_stable = ranked[-1]

        return {
            "total_careers_tracked": len(self.DEMAND_DATA),
            "top_trending_career": top_growth["career"],
            "top_growth_cagr": top_growth["cagr_growth_rate"],
            "most_stable_career": most_stable["career"],
            "trending_rankings": ranked,
            "macro_narrative": (
                f"{top_growth['career']} is projected to lead market hiring with an estimated "
                f"{top_growth['projected_gain_percentage']}% demand surge over the next 24 months, "
                "driven by rapid industry adoption of automated cognitive workflows."
            ),
        }
