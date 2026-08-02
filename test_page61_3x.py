"""
One-off test: call generate_page for page 61 (science_reasoning) 3 times.
Check how many of the 30 questions are unique against each other.
"""
import json
import sys
import time
from pathlib import Path
from difflib import SequenceMatcher

sys.path.insert(0, str(Path(__file__).parent))

from pipeline.phase3_generate import generate_page, _get_gemini_model

PNG = "run_data/scratch/act_test1/images/science_reasoning/act_test1_220526_p61.png"
OUT_DIR = "run_data/output"
BRIEFING = {"target_year": "11-12", "difficulty": "hard"}
DEDUP_THRESHOLD = 0.85


def is_duplicate(new_stem, existing_stems):
    nl = new_stem.lower()
    for s in existing_stems:
        if SequenceMatcher(None, nl, s.lower()).ratio() >= DEDUP_THRESHOLD:
            return True
    return False


model = _get_gemini_model()
all_questions = []
passages = []

for run in range(1, 4):
    print(f"\n{'='*60}")
    print(f"RUN {run}/3 — calling Gemini for page 61...")

    # Use a unique output path per run so resumable logic doesn't skip
    out_path = Path(OUT_DIR) / "science_reasoning" / "generated" / f"act_test1_p61_run{run}.json"
    if out_path.exists():
        print(f"  Loading cached run {run} from {out_path}")
        batch = json.loads(out_path.read_text())
    else:
        batch = generate_page(
            page_n=61,
            image_path=PNG,
            subject="science_reasoning",
            book_id=f"act_test1_run{run}",
            output_dir=OUT_DIR + f"_run{run}",
            briefing_data=BRIEFING,
            model=model,
        )
        # Save under the named path for caching
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(batch, indent=2))

    passages.append(batch[0].get("passage", "")[:120] if batch else "")
    print(f"  Got {len(batch)} questions")
    if batch:
        print(f"  Passage preview: {passages[-1]!r}")
    all_questions.extend(batch)

    if run < 3:
        print("  Sleeping 3s before next call...")
        time.sleep(3)

# ── uniqueness check ─────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"UNIQUENESS CHECK across {len(all_questions)} questions (threshold={DEDUP_THRESHOLD})")
print("="*60)

seen_stems = []
unique = []
duplicates = []

for q in all_questions:
    stem = q["stem"]
    if is_duplicate(stem, seen_stems):
        duplicates.append(stem)
    else:
        seen_stems.append(stem)
        unique.append(q)

print(f"\nTotal questions : {len(all_questions)}")
print(f"Unique          : {len(unique)}")
print(f"Duplicates      : {len(duplicates)}")
print(f"Uniqueness rate : {len(unique)/len(all_questions)*100:.0f}%")

if duplicates:
    print("\nDuplicate stems:")
    for s in duplicates:
        print(f"  - {s[:90]}")

# ── passage diversity check ───────────────────────────────────────────────────
print(f"\n{'='*60}")
print("PASSAGE DIVERSITY (first 120 chars per run):")
for i, p in enumerate(passages, 1):
    print(f"  Run {i}: {p!r}")

# ── topic distribution ────────────────────────────────────────────────────────
from collections import Counter
topics = Counter(q["topic"] for q in all_questions)
print(f"\n{'='*60}")
print("TOPIC DISTRIBUTION:")
for topic, count in topics.most_common():
    print(f"  {topic}: {count}")
