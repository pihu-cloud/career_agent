"""
Career Growth Trajectory and Job-Readiness Model (SB2/US33, US48).
Forecasts career progression levels, salary growth trajectories (in INR),
and time-to-readiness timelines for students.
"""

from typing import Any, Dict, List, Optional, Union
from ml.models.content_filter import ContentBasedFilter


class GrowthTrajectoryModel:
    """Predicts career milestones, salary progression, and job-readiness velocity."""

    # Industry baseline salary bands in INR (SAMPLE DATA per Issue #1)
    SALARY_DATA = {
        "Software Engineer": {"entry": 450000, "mid": 950000, "senior": 1800000, "lead": 2800000},
        "Data Scientist": {"entry": 550000, "mid": 1100000, "senior": 2100000, "lead": 3200000},
        "Product Manager": {"entry": 600000, "mid": 1300000, "senior": 2400000, "lead": 3600000},
        "UX Designer": {"entry": 400000, "mid": 850000, "senior": 1600000, "lead": 2400000},
        "Business Analyst": {"entry": 420000, "mid": 850000, "senior": 1550000, "lead": 2300000},
        "Cybersecurity Analyst": {"entry": 480000, "mid": 1050000, "senior": 1950000, "lead": 2900000},
        "DevOps Engineer": {"entry": 500000, "mid": 1050000, "senior": 2000000, "lead": 3000000},
        "AI/ML Engineer": {"entry": 650000, "mid": 1350000, "senior": 2500000, "lead": 3800000},
        "Financial Analyst": {"entry": 450000, "mid": 900000, "senior": 1700000, "lead": 2600000},
        "Healthcare Informatics": {"entry": 420000, "mid": 880000, "senior": 1650000, "lead": 2500000},
    }

    MILESTONES = [
        {"level": "Entry Level", "min_skills": 3, "min_cgpa": 6.0, "years_exp": 0.0},
        {"level": "Mid Level", "min_skills": 6, "min_cgpa": 6.5, "years_exp": 2.0},
        {"level": "Senior Level", "min_skills": 10, "min_cgpa": 7.0, "years_exp": 4.5},
        {"level": "Lead / Principal", "min_skills": 14, "min_cgpa": 7.5, "years_exp": 7.0},
    ]

    def __init__(self):
        self.content_filter = ContentBasedFilter()

    def predict_trajectory(
        self,
        career: str,
        current_skills: List[Union[str, Dict[str, Any]]],
        cgpa: float = 7.0,
    ) -> Dict[str, Any]:
        """
        Predict student's current placement stage, salary bracket, and next milestone.
        Returns: {current_level, next_milestone, estimated_salary, years_to_next, growth_path}
        """
        salaries = self.SALARY_DATA.get(career, {
            "entry": 400000,
            "mid": 800000,
            "senior": 1500000,
            "lead": 2400000,
        })

        gap_info = self.content_filter.compute_skill_gap(current_skills, career)
        matched_count = len(gap_info.get("present_skills", []))

        # Determine current level
        if matched_count >= 8 and cgpa >= 7.5:
            current_level = "Mid Level"
            next_milestone = "Senior Level"
            estimated_salary = salaries["mid"]
            years_to_next = 2.0
        elif matched_count >= 4 and cgpa >= 6.5:
            current_level = "Entry Level"
            next_milestone = "Mid Level"
            estimated_salary = salaries["entry"]
            years_to_next = 1.5
        else:
            current_level = "Aspiring Intern / Pre-Entry"
            next_milestone = "Entry Level"
            estimated_salary = int(salaries["entry"] * 0.75)
            years_to_next = 0.8

        growth_path = [
            {"milestone": "Pre-Entry / Intern", "target_salary": int(salaries["entry"] * 0.75), "duration_months": 6},
            {"milestone": "Entry Level Engineer", "target_salary": salaries["entry"], "duration_months": 18},
            {"milestone": "Mid-Level Specialist", "target_salary": salaries["mid"], "duration_months": 36},
            {"milestone": "Senior / Tech Lead", "target_salary": salaries["senior"], "duration_months": 60},
        ]

        return {
            "career": career,
            "current_level": current_level,
            "next_milestone": next_milestone,
            "estimated_salary_inr": estimated_salary,
            "years_to_next": years_to_next,
            "growth_path": growth_path,
            "matching_skills_count": matched_count,
        }

    def predict_skill_progression(self, user_profile: Dict[str, Any], target_career: Optional[str] = None) -> Dict[str, Any]:
        """
        SB2/US48: Predicts when a student will be "job-ready" for their target or top career.
        Returns readiness percentage, estimated weeks to readiness, and recommended learning plan.
        """
        career = target_career or "Software Engineer"
        user_skills = user_profile.get("skills", [])
        gap_info = self.content_filter.compute_skill_gap(user_skills, career)

        missing_skills = gap_info.get("missing_skills", [])
        present_skills = gap_info.get("present_skills", [])
        total_req = len(missing_skills) + len(present_skills) or 1

        readiness_pct = round((len(present_skills) / total_req) * 100.0, 1)

        # Assuming an average of 4 weeks per core skill module
        weeks_per_skill = 3.5
        est_weeks = int(round(len(missing_skills) * weeks_per_skill))
        est_months = round(est_weeks / 4.3, 1)

        is_job_ready = readiness_pct >= 75.0

        roadmap = []
        for idx, skill in enumerate(missing_skills):
            roadmap.append({
                "step": idx + 1,
                "skill": skill,
                "target_duration_weeks": 3,
                "priority": "High" if idx < 2 else "Medium",
            })

        return {
            "target_career": career,
            "is_job_ready": is_job_ready,
            "readiness_percentage": readiness_pct,
            "estimated_weeks_to_ready": est_weeks,
            "estimated_months_to_ready": est_months,
            "missing_skills_count": len(missing_skills),
            "acquired_skills_count": len(present_skills),
            "learning_roadmap": roadmap,
            "readiness_status": "Job-Ready" if is_job_ready else f"Job-Ready in ~{est_months} months",
        }
