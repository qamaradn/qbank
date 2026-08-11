#!/usr/bin/env python3
"""Builds wr_vic_acer_p3.json — 11 persuasive-slot prompts for the VIC paper.

CALIBRATION. ~20 minutes, Year 8, 160-250 words. See tools/wr/wr_vic_p1_build.py.

WHAT 20 MINUTES DOES TO A PERSUASIVE PROMPT. It rules out the school-essay shape the ten
legacy VIC rows assume — "address both the environmental benefits and the economic
concerns", "use evidence, reasoning and at least one specific example, and refute the
opposing view". That is three or four deliverables. In 250 words a candidate can take a
position, support it, and deal with ONE objection. Every task here asks for exactly that
much and no more, and the prompts that were re-cut in
tools/repair_vic_writing_calibration.py were re-cut to the same shape.

THE HARDER DESIGN PROBLEM: A GOOD PERSUASIVE PROMPT MUST BE ARGUABLE BOTH WAYS. If a
thoughtful Year 8 can only see one side, the task stops testing argument and starts
testing agreement, and every script comes back the same. So each prompt below is checked
against a specific real counter-argument, named here in the topic or the stimulus. Where
the obvious answer is overwhelming ("should bullying be allowed"), the prompt is not used.

Held before this batch: 6 in the persuasive slot (persuasive 3, article 2, speech 1).
Target 27.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/writing/generated"
BOOK = "wr_vic_acer"
NN = 3
NOW = datetime.datetime(2026, 8, 12, 11, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

PROMPTS = []


def P(stimulus_type, stimulus, task, topic, focus, lo=160, hi=250, difficulty="medium"):
    PROMPTS.append({
        "id": str(uuid.uuid4()),
        "prompt_type": "persuasive",
        "school_type": "victorian_selective",
        "stimulus_type": stimulus_type,
        "stimulus_content": stimulus,
        "stimulus_image_desc": None,
        "task_instruction": task,
        "word_count_min": lo,
        "word_count_max": hi,
        "time_limit_minutes": 20,
        "target_year": "7-8",
        "difficulty": difficulty,
        "topic": topic,
        "marking_focus": json.dumps(focus),
        "source_book": BOOK,
        "review_status": "pending",
        "created_at": NOW,
    })


P("text",
  "A Victorian secondary school is considering replacing its end-of-year exams in Years 7 "
  "and 8 with a portfolio of work collected across the year. Supporters say exams reward "
  "the students who happen to be calm on one particular morning. Opponents say a portfolio "
  "rewards the students whose families have the time and the space to help at home.",
  "Write a persuasive piece arguing for one of these two systems. Take the strongest "
  "point on the other side and answer it. Do not try to answer them all.",
  "Assessment", ["position", "reasoning", "counter-argument", "language"]),

P("quote",
  "\"Every hour a teenager spends on a screen is an hour they are not spending outdoors.\"\n\n"
  "It is the kind of sentence that sounds true, gets repeated at school assemblies across "
  "Australia, and is almost never examined. It treats all screen hours as the same hour, "
  "and it assumes the alternative was always going to be a walk.",
  "Write a persuasive piece agreeing or disagreeing with the quote. Whichever side you "
  "take, deal with the objection raised underneath it.",
  "Technology and Adolescence", ["position", "analysis", "counter-argument", "language"],
  difficulty="hard"),

P("data",
  "Council survey — proposed 24-hour dog off-leash area, Brunswick\n\n"
  "  In favour ................. 61%\n"
  "  Opposed ................... 24%\n"
  "  No strong view ............ 15%\n\n"
  "Of those opposed, 78% live within 200 metres of the proposed area.\n"
  "Of those in favour, 12% do.",
  "The council has the numbers but not the neighbours. Write a persuasive piece arguing "
  "whether the proposal should go ahead. Your argument must engage with what the second "
  "half of the data shows.",
  "Local Democracy", ["position", "use of evidence", "counter-argument", "language"],
  difficulty="hard"),

P("scenario",
  "A country football league in western Victoria has proposed that every registered player "
  "get equal game time in Under-14s, regardless of ability. Clubs are split. One coach "
  "says the rule is the only reason half his squad still turns up. Another says it is "
  "unfair to the players who train hardest.",
  "Write a persuasive piece supporting or opposing the equal game time rule. Address the "
  "coach whose argument is against your position.",
  "Sport and Fairness", ["position", "reasoning", "counter-argument", "language"]),

P("text",
  "Some Australian libraries have removed fines for overdue books. Borrowing went up. "
  "Librarians report that the people who had stopped coming were mostly the people who "
  "could least afford the fines. Books are also now returned, on average, four days later "
  "than before.",
  "Write a persuasive piece arguing whether libraries should charge overdue fines. Use "
  "what the passage tells you, and take seriously the cost of the change as well as the "
  "benefit.",
  "Public Institutions", ["position", "use of evidence", "balance", "language"]),

P("scenario",
  "Your school in outer Melbourne is deciding what to do with a bequest of $40,000. The "
  "two shortlisted "
  "options are a full set of musical instruments that about thirty students would use "
  "every week, or shade structures over the yard that all nine hundred students would "
  "stand under every summer.",
  "Write a persuasive piece recommending one of the two. A good argument here has to say "
  "something about how a school should weigh depth against reach.",
  "Priorities", ["position", "reasoning", "counter-argument", "language"], difficulty="hard"),

P("quote",
  "\"Homework is practice, and nobody gets better at anything without practice.\"\n\n"
  "The comparison is with sport, and it is doing a lot of work. A netball training session "
  "is supervised, corrected on the spot, and finishes when the coach says so. Homework is "
  "none of those three things.",
  "Write a persuasive piece arguing whether homework should be set in Years 7 and 8. Test "
  "the comparison in the stimulus rather than ignoring it.",
  "Education", ["position", "analysis", "counter-argument", "language"]),

P("text",
  "A regional Victorian town has been offered a large solar farm on farmland just outside "
  "it. It would bring construction jobs for two years and about eleven permanent ones "
  "afterwards. The farmland is currently leased to three families. The town has lost a "
  "quarter of its population in fifteen years.",
  "Write a persuasive piece advising the town to accept or refuse the offer. Whichever you "
  "argue, do not pretend the other side has nothing to lose.",
  "Regional Australia", ["position", "reasoning", "empathy", "language"], difficulty="hard"),

P("scenario",
  "A Melbourne museum has been asked to return an object to the community it was taken "
  "from in the 1890s. The museum says it is seen by 200,000 people a year and is cared for "
  "in conditions no small community could match. The community says that is not the point.",
  "Write a persuasive piece arguing what the museum should do. The strongest version of "
  "this argument does not treat the other side as foolish.",
  "Culture and Ownership", ["position", "reasoning", "respect", "language"],
  difficulty="hard"),

P("data",
  "Two Australian schools, same suburb, same year level, same test:\n\n"
  "  School A — average mark 74, range 61 to 88\n"
  "  School B — average mark 74, range 22 to 99\n\n"
  "School B's principal describes the result as a success. School A's describes it the "
  "same way.",
  "Write a persuasive piece arguing which school has more to be pleased about. Your case "
  "depends on saying what a school is for, so say it.",
  "Measurement and Values", ["position", "use of evidence", "reasoning", "language"],
  difficulty="hard"),

P("text",
  "A proposal before a Victorian council would let residents vote directly, by phone app, "
  "on how part of the local budget is spent. Turnout in the trial suburb was 31%, which is "
  "far higher than attendance at council meetings and far lower than at an election. Most "
  "of the money went to sporting facilities.",
  "Write a persuasive piece arguing whether this should be extended to the whole council "
  "area. Deal with what a 31% turnout means for the result.",
  "Democracy and Participation", ["position", "analysis", "counter-argument", "language"]),


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(PROMPTS, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {len(PROMPTS)} prompts -> {path}")
