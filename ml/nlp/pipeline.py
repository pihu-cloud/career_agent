"""
NLP Pipeline (SB2/US14).
Orchestrates SkillExtractor and SkillClassifier to analyze resumes, raw text, and student profiles.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ml.models.skill_classifier import SkillClassifier
from ml.nlp.skill_extractor import SkillExtractor


class NLPPipeline:
    """End-to-end NLP processing pipeline for resumes and skill analysis."""

    def __init__(
        self,
        extractor: Optional[SkillExtractor] = None,
        classifier: Optional[SkillClassifier] = None,
    ):
        self.extractor = extractor or SkillExtractor()
        self.classifier = classifier or SkillClassifier()

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Extract skills from text and classify them.
        Returns: {extracted_skills: {...}, classified_skills: [...], summary: {...}}
        """
        extracted = self.extractor.extract_from_text(text)
        classified = self.classifier.classify_bulk(extracted["all"])

        tech_classified = [c for c in classified if c["category"] == "Technical"]
        soft_classified = [c for c in classified if c["category"] == "Soft"]
        domain_classified = [c for c in classified if c["category"] == "Domain"]

        return {
            "raw_text_length": len(text) if text else 0,
            "extracted_skills": extracted,
            "classified_skills": classified,
            "summary": {
                "total_skills": len(extracted["all"]),
                "technical_count": len(tech_classified),
                "soft_count": len(soft_classified),
                "domain_count": len(domain_classified),
            },
        }

    def process_resume(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Analyze a complete resume file (PDF, DOCX, TXT).
        """
        file_result = self.extractor.extract_from_resume_file(filepath)
        all_skills = file_result["skills"]["all"]
        classified = self.classifier.classify_bulk(all_skills)

        return {
            "filename": file_result["filename"],
            "text_length": file_result["text_length"],
            "snippet": file_result["extracted_text_snippet"],
            "extracted_skills": file_result["skills"],
            "classified_skills": classified,
            "summary": {
                "total_skills": len(all_skills),
                "technical_count": len(file_result["skills"]["technical"]),
                "soft_count": len(file_result["skills"]["soft"]),
            },
        }

    def process_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a full student profile (skills, interests, academics, resume text).
        """
        raw_skills = profile.get("skills", [])
        skill_names = []
        for s in raw_skills:
            if isinstance(s, dict):
                skill_names.append(s.get("skill_name", ""))
            elif isinstance(s, str):
                skill_names.append(s)

        classified = self.classifier.classify_bulk(skill_names)

        # Resume text analysis if present
        resume_analysis = None
        if "resume_text" in profile and profile["resume_text"]:
            resume_analysis = self.process_text(profile["resume_text"])

        return {
            "profile_skills_count": len(skill_names),
            "classified_profile_skills": classified,
            "resume_analysis": resume_analysis,
        }
