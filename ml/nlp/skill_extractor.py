"""
Skill Extractor (SB2/US9).
Extracts technical and soft skills from resumes and plain text using spaCy NER and regex fallbacks.
Supports parsing PDF and DOCX resume documents.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Union


class SkillExtractor:
    """Extracts technical and soft skills from resume text with PDF/DOCX support."""

    TECH_SKILLS_KEYWORDS = [
        "python", "java", "c++", "c", "c#", "javascript", "typescript", "ruby", "php",
        "golang", "rust", "scala", "kotlin", "swift", "r", "matlab", "perl", "bash",
        "sql", "mysql", "postgresql", "sqlite", "oracle", "mongodb", "redis", "cassandra",
        "dynamodb", "neo4j", "mariadb", "firebase", "supabase", "elasticsearch",
        "html", "html5", "css", "css3", "sass", "bootstrap", "tailwind", "react", "react.js",
        "angular", "vue", "vue.js", "next.js", "nuxt.js", "svelte", "django", "fastapi",
        "flask", "spring", "spring boot", "express", "express.js", "node.js", "asp.net",
        "machine learning", "deep learning", "artificial intelligence", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "scipy",
        "opencv", "xgboost", "lightgbm", "llm", "transformers", "huggingface", "bert",
        "docker", "kubernetes", "aws", "amazon web services", "azure", "gcp", "google cloud",
        "terraform", "ansible", "jenkins", "gitlab ci", "github actions", "circleci",
        "git", "github", "gitlab", "bitbucket", "jira", "linux", "unix", "rest api", "graphql",
        "microservices", "kafka", "rabbitmq", "celery", "airflow", "spark", "hadoop",
        "cybersecurity", "penetration testing", "wireshark", "metasploit", "cryptography",
        "soc2", "iso 27001", "owasp", "network security", "firewall", "siem"
    ]

    SOFT_SKILLS_KEYWORDS = [
        "communication", "written communication", "verbal communication", "presentation skills",
        "public speaking", "active listening", "storytelling", "teamwork", "collaboration",
        "cross-functional collaboration", "leadership", "team leadership", "mentorship",
        "conflict resolution", "negotiation", "stakeholder management", "problem solving",
        "troubleshooting", "critical thinking", "analytical skills", "decision making",
        "creativity", "innovation", "design thinking", "time management", "prioritization",
        "multitasking", "adaptability", "flexibility", "resilience", "emotional intelligence",
        "empathy", "work ethic", "attention to detail", "strategic thinking"
    ]

    def __init__(self):
        self.nlp = None
        self._init_spacy()

    def _init_spacy(self):
        """Attempt to load spaCy model, fall back gracefully to regex."""
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = None
        except Exception:
            self.nlp = None

    def parse_docx(self, filepath: Union[str, Path]) -> str:
        """Extract text from DOCX file using python-docx."""
        path = Path(filepath)
        if not path.exists():
            return ""
        try:
            import docx
            doc = docx.Document(str(path))
            full_text = []
            for para in doc.paragraphs:
                if para.text:
                    full_text.append(para.text)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text:
                            full_text.append(cell.text)
            return "\n".join(full_text)
        except Exception as e:
            # Fallback text reading
            try:
                return path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                return ""

    def parse_pdf(self, filepath: Union[str, Path]) -> str:
        """Extract text from PDF file with multiple fallback strategies."""
        path = Path(filepath)
        if not path.exists():
            return ""

        # Strategy 1: pypdf / pypdf2 / pdfminer
        for mod_name in ["pypdf", "PyPDF2", "pdfminer.high_level"]:
            try:
                if mod_name == "pdfminer.high_level":
                    from pdfminer.high_level import extract_text
                    return extract_text(str(path))
                elif mod_name in ("pypdf", "PyPDF2"):
                    mod = __import__(mod_name)
                    reader = mod.PdfReader(str(path))
                    text_parts = [page.extract_text() or "" for page in reader.pages]
                    extracted = "\n".join(text_parts).strip()
                    if extracted:
                        return extracted
            except Exception:
                continue

        # Strategy 2: Stream extraction regex for PDF text objects
        try:
            raw_bytes = path.read_bytes()
            # Extract parenthesized strings inside BT ... ET text blocks
            text_chunks = re.findall(rb"\((.*?)\)\s*Tj", raw_bytes)
            if text_chunks:
                decoded = " ".join([c.decode("latin1", errors="ignore") for c in text_chunks])
                if len(decoded.strip()) > 20:
                    return decoded

            # Raw ascii text extraction fallback
            ascii_strings = re.findall(rb"[a-zA-Z0-9\s,\.\-_\+\#\:\(\)\/\@]{4,}", raw_bytes)
            if ascii_strings:
                return " ".join([s.decode("latin1", errors="ignore") for s in ascii_strings])
        except Exception:
            pass

        return ""

    def extract_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extract technical, soft, and combined skills from raw text.
        Returns: {technical: [...], soft: [...], all: [...]}
        """
        if not text:
            return {"technical": [], "soft": [], "all": []}

        lower_text = " " + text.lower() + " "
        found_tech: Set[str] = set()
        found_soft: Set[str] = set()

        # Regex matching against keyword taxonomies
        for skill in self.TECH_SKILLS_KEYWORDS:
            pattern = r"(?<![a-zA-Z0-9_\-\+\#])" + re.escape(skill) + r"(?![a-zA-Z0-9_\-\+\#])"
            if re.search(pattern, lower_text):
                found_tech.add(skill)

        for skill in self.SOFT_SKILLS_KEYWORDS:
            pattern = r"(?<![a-zA-Z0-9_])" + re.escape(skill) + r"(?![a-zA-Z0-9_])"
            if re.search(pattern, lower_text):
                found_soft.add(skill)

        # If spaCy NER is active, enrich with ORG/PRODUCT entities matching skills
        if self.nlp is not None:
            try:
                doc = self.nlp(text[:10000])  # limit length for speed
                for ent in doc.ents:
                    ent_clean = ent.text.strip().lower()
                    if ent_clean in self.TECH_SKILLS_KEYWORDS:
                        found_tech.add(ent_clean)
            except Exception:
                pass

        tech_list = sorted(list(found_tech))
        soft_list = sorted(list(found_soft))
        all_skills = sorted(list(found_tech.union(found_soft)))

        return {
            "technical": tech_list,
            "soft": soft_list,
            "all": all_skills,
        }

    def extract_from_resume_file(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract skill profile from a resume file (PDF, DOCX, TXT).
        """
        path = Path(filepath)
        suffix = path.suffix.lower()

        if suffix == ".docx":
            raw_text = self.parse_docx(path)
        elif suffix == ".pdf":
            raw_text = self.parse_pdf(path)
        else:
            try:
                raw_text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                raw_text = ""

        skills = self.extract_from_text(raw_text)
        return {
            "filename": path.name,
            "text_length": len(raw_text),
            "skills": skills,
            "extracted_text_snippet": raw_text[:300] if raw_text else "",
        }
