"""
Sample Training Data Generator (SB2/US7).
NOTE: This module generates synthetic/sample labeled training data for career prediction,
documented as SAMPLE DATA per Issue #1 in analysis.
"""

from pathlib import Path
from typing import Union
import numpy as np
import pandas as pd

CAREER_LABELS = [
    "Software Engineer",
    "Data Scientist",
    "Product Manager",
    "UX Designer",
    "Business Analyst",
    "Cybersecurity Analyst",
    "DevOps Engineer",
    "AI/ML Engineer",
    "Financial Analyst",
    "Healthcare Informatics",
]

# Profiles for probabilistic generation of realistic correlated features
CAREER_PROFILES = {
    "Software Engineer": {
        "cgpa": (7.5, 1.0),
        "tech_skills": (10, 2),
        "soft_skills": (4, 2),
        "exp": (1.5, 1.2),
        "interests": [0.95, 0.3, 0.1, 0.4, 0.6],
        "personality": (7, 8, 5, 6, 4),  # O, C, E, A, N
    },
    "Data Scientist": {
        "cgpa": (8.2, 0.9),
        "tech_skills": (11, 2),
        "soft_skills": (5, 2),
        "exp": (1.8, 1.2),
        "interests": [0.9, 0.5, 0.3, 0.3, 0.95],
        "personality": (9, 8, 4, 6, 4),
    },
    "Product Manager": {
        "cgpa": (7.2, 1.1),
        "tech_skills": (6, 2),
        "soft_skills": (9, 1),
        "exp": (2.5, 1.2),
        "interests": [0.7, 0.95, 0.2, 0.7, 0.3],
        "personality": (8, 9, 9, 8, 3),
    },
    "UX Designer": {
        "cgpa": (6.8, 1.2),
        "tech_skills": (5, 2),
        "soft_skills": (8, 2),
        "exp": (1.5, 1.2),
        "interests": [0.6, 0.4, 0.2, 0.95, 0.2],
        "personality": (9, 7, 7, 8, 4),
    },
    "Business Analyst": {
        "cgpa": (7.3, 1.0),
        "tech_skills": (6, 2),
        "soft_skills": (8, 2),
        "exp": (2.0, 1.2),
        "interests": [0.6, 0.95, 0.3, 0.4, 0.5],
        "personality": (7, 9, 7, 7, 4),
    },
    "Cybersecurity Analyst": {
        "cgpa": (7.6, 1.0),
        "tech_skills": (10, 2),
        "soft_skills": (4, 2),
        "exp": (2.0, 1.2),
        "interests": [0.95, 0.4, 0.1, 0.2, 0.7],
        "personality": (7, 9, 4, 6, 6),
    },
    "DevOps Engineer": {
        "cgpa": (7.4, 1.1),
        "tech_skills": (11, 2),
        "soft_skills": (5, 2),
        "exp": (2.2, 1.2),
        "interests": [0.95, 0.3, 0.1, 0.2, 0.6],
        "personality": (7, 8, 5, 7, 4),
    },
    "AI/ML Engineer": {
        "cgpa": (8.5, 0.8),
        "tech_skills": (12, 2),
        "soft_skills": (5, 2),
        "exp": (2.0, 1.2),
        "interests": [0.95, 0.4, 0.3, 0.4, 0.95],
        "personality": (9, 9, 4, 6, 4),
    },
    "Financial Analyst": {
        "cgpa": (7.8, 1.0),
        "tech_skills": (5, 2),
        "soft_skills": (7, 2),
        "exp": (2.0, 1.2),
        "interests": [0.4, 0.95, 0.2, 0.2, 0.7],
        "personality": (6, 9, 6, 6, 5),
    },
    "Healthcare Informatics": {
        "cgpa": (7.5, 1.0),
        "tech_skills": (7, 2),
        "soft_skills": (6, 2),
        "exp": (1.8, 1.2),
        "interests": [0.7, 0.5, 0.95, 0.3, 0.8],
        "personality": (8, 9, 6, 8, 4),
    },
}


def generate_career_training_data(n_samples: int = 1000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic labeled training data for career prediction (SAMPLE DATA).
    
    Returns a DataFrame with columns:
    - cgpa (2.0-10.0)
    - num_skills (1-20)
    - technical_skills_count (0-15)
    - soft_skills_count (0-10)
    - years_experience (0-5)
    - interest_technology (0-1)
    - interest_business (0-1)
    - interest_healthcare (0-1)
    - interest_design (0-1)
    - interest_science (0-1)
    - personality_openness (1-10)
    - personality_conscientiousness (1-10)
    - personality_extraversion (1-10)
    - personality_agreeableness (1-10)
    - personality_neuroticism (1-10)
    - career_label (string)
    """
    np.random.seed(random_state)
    records = []
    samples_per_class = max(1, n_samples // len(CAREER_LABELS))

    for career in CAREER_LABELS:
        profile = CAREER_PROFILES[career]
        for _ in range(samples_per_class):
            cgpa = float(np.clip(np.random.normal(profile["cgpa"][0], profile["cgpa"][1]), 2.0, 10.0))
            tech = int(np.clip(np.random.normal(profile["tech_skills"][0], profile["tech_skills"][1]), 0, 15))
            soft = int(np.clip(np.random.normal(profile["soft_skills"][0], profile["soft_skills"][1]), 0, 10))
            num_skills = int(np.clip(tech + soft + np.random.randint(-1, 2), 1, 20))
            years_exp = float(np.clip(np.random.normal(profile["exp"][0], profile["exp"][1]), 0.0, 5.0))

            interest_probs = profile["interests"]
            interests = [
                int(np.random.binomial(1, np.clip(p + np.random.uniform(-0.15, 0.15), 0.0, 1.0)))
                for p in interest_probs
            ]

            p_means = profile["personality"]
            personality = [
                int(np.clip(np.round(np.random.normal(m, 1.2)), 1, 10))
                for m in p_means
            ]

            records.append({
                "cgpa": round(cgpa, 2),
                "num_skills": num_skills,
                "technical_skills_count": tech,
                "soft_skills_count": soft,
                "years_experience": round(years_exp, 1),
                "interest_technology": interests[0],
                "interest_business": interests[1],
                "interest_healthcare": interests[2],
                "interest_design": interests[3],
                "interest_science": interests[4],
                "personality_openness": personality[0],
                "personality_conscientiousness": personality[1],
                "personality_extraversion": personality[2],
                "personality_agreeableness": personality[3],
                "personality_neuroticism": personality[4],
                "career_label": career,
            })

    # If any remaining samples needed to reach n_samples
    remaining = n_samples - len(records)
    for _ in range(remaining):
        chosen_career = np.random.choice(CAREER_LABELS)
        profile = CAREER_PROFILES[chosen_career]
        cgpa = float(np.clip(np.random.normal(profile["cgpa"][0], profile["cgpa"][1]), 2.0, 10.0))
        tech = int(np.clip(np.random.normal(profile["tech_skills"][0], profile["tech_skills"][1]), 0, 15))
        soft = int(np.clip(np.random.normal(profile["soft_skills"][0], profile["soft_skills"][1]), 0, 10))
        num_skills = int(np.clip(tech + soft, 1, 20))
        years_exp = float(np.clip(np.random.normal(profile["exp"][0], profile["exp"][1]), 0.0, 5.0))
        interests = [int(np.random.binomial(1, np.clip(p, 0.0, 1.0))) for p in profile["interests"]]
        personality = [int(np.clip(np.round(np.random.normal(m, 1.2)), 1, 10)) for m in profile["personality"]]

        records.append({
            "cgpa": round(cgpa, 2),
            "num_skills": num_skills,
            "technical_skills_count": tech,
            "soft_skills_count": soft,
            "years_experience": round(years_exp, 1),
            "interest_technology": interests[0],
            "interest_business": interests[1],
            "interest_healthcare": interests[2],
            "interest_design": interests[3],
            "interest_science": interests[4],
            "personality_openness": personality[0],
            "personality_conscientiousness": personality[1],
            "personality_extraversion": personality[2],
            "personality_agreeableness": personality[3],
            "personality_neuroticism": personality[4],
            "career_label": chosen_career,
        })

    df = pd.DataFrame(records)
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df


def save_sample_data(filepath: Union[str, Path], n_samples: int = 1200) -> Path:
    """Save synthetic career training data to a CSV file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_career_training_data(n_samples=n_samples)
    df.to_csv(path, index=False)
    return path


def load_training_data(filepath: Union[str, Path]) -> pd.DataFrame:
    """Load career training data from CSV file, generating it if not found."""
    path = Path(filepath)
    if not path.exists():
        return generate_career_training_data()
    return pd.read_csv(path)


if __name__ == "__main__":
    df = generate_career_training_data(100)
    print("Sample data generated successfully, shape:", df.shape)
    print(df.head(2))
