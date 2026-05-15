"""Central config — all values from environment. No magic numbers anywhere else."""
import os
from dotenv import load_dotenv

load_dotenv()

# API keys
ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]
SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "figures")

# Data paths
DATA_DIR: str = os.getenv("DATA_DIR", "/data")
PDF_DIR: str = os.getenv("PDF_DIR", "/data/pdfs")
SCRATCH_DIR: str = os.getenv("SCRATCH_DIR", "/data/scratch")
OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "/data/output")
DB_PATH: str = os.getenv("DB_PATH", "/data/db/qbank.db")
FIGURES_DIR: str = os.getenv("FIGURES_DIR", "/data/db/figures")

# Pipeline tuning
FIGURE_PROXIMITY_PX: int = int(os.getenv("FIGURE_PROXIMITY_PX", "150"))
CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.90"))
BRIEFING_OVERRIDE_THRESHOLD: float = float(os.getenv("BRIEFING_OVERRIDE_THRESHOLD", "0.85"))
QUESTIONS_PER_PAGE: int = int(os.getenv("QUESTIONS_PER_PAGE", "8"))
FIGURE_QUESTIONS_PER_FIGURE: int = int(os.getenv("FIGURE_QUESTIONS_PER_FIGURE", "4"))
API_DELAY_SECONDS: int = int(os.getenv("API_DELAY_SECONDS", "2"))
CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
GEMINI_KEY: str = os.getenv("GEMINI_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Review server
REVIEW_HOST: str = os.getenv("REVIEW_HOST", "0.0.0.0")
REVIEW_PORT: int = int(os.getenv("REVIEW_PORT", "8000"))

# Valid subjects — never change these
VALID_SUBJECTS: tuple[str, ...] = (
    "quantitative_reasoning",
    "logical_reasoning",
    "science_reasoning",
    "reading_comprehension",
    "writing",
)

# Valid classifier return values (subjects + special tokens)
VALID_CLASSIFIER_RETURNS: tuple[str, ...] = VALID_SUBJECTS + ("answer_key", "skip")
