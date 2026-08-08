#!/usr/bin/env python3
"""Builds wr_nsw_selective_p1.json — the 11 NSW writing prompts §6.3 asks for.

Held before this batch: narrative 3, persuasive 3, article 1, diary 1, news report 1,
speech 1 = 10. Missing entirely: email and advice_sheet. Target 21 across all eight forms.

This batch adds email 3, advice sheet 3, article 2, diary 1, news report 1, speech 1,
taking every form to 2 or 3 and the set to 21.

CALIBRATION. These are written for the exam §1 describes: one prompt, 30 minutes, sat in
Year 6, no specialist knowledge required. That is deliberately different from the ten NSW
prompts already in the table, which carry target_year 9-10, a 25 minute limit and word
counts to 500 — Victorian calibration on an NSW row. Those ten are left alone; the
mismatch is reported rather than silently rewritten.

Every stimulus is self-contained: a Year 6 candidate needs nothing they have not been
given, which is what "no specialist knowledge is required" means in practice.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/writing/generated"
BOOK = "wr_nsw_selective"
NN = 1
NOW = datetime.datetime(2026, 8, 8, 9, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

PROMPTS = []


def P(prompt_type, stimulus_type, stimulus, task, topic, focus,
      lo=200, hi=320, difficulty="medium", image_desc=None):
    PROMPTS.append({
        "id": str(uuid.uuid4()),
        "prompt_type": prompt_type,
        "school_type": "nsw_selective",
        "stimulus_type": stimulus_type,
        "stimulus_content": stimulus,
        "stimulus_image_desc": image_desc,
        "task_instruction": task,
        "word_count_min": lo,
        "word_count_max": hi,
        "time_limit_minutes": 30,
        "target_year": "5-6",
        "difficulty": difficulty,
        "topic": topic,
        "marking_focus": json.dumps(focus),
        "source_book": BOOK,
        "review_status": "pending",
        "created_at": NOW,
    })


# ===================================================== email (3)

P("email", "scenario",
  "Your school canteen, in a country town in New South Wales, sells about 200 drinks a "
  "week in single-use plastic bottles. The "
  "student environment committee, which you belong to, has counted the bottles in the "
  "playground bins for a fortnight and found that fewer than half of them end up in the "
  "recycling — even though most of them carry the 10c Return and Earn refund mark. The "
  "committee thinks the canteen should sell drinks in cans, or fit a chilled water "
  "fountain and sell reusable bottles instead. The principal has asked the committee to "
  "put its case in writing before the next staff meeting.",
  "Write an email to your principal setting out what the committee found and what you "
  "want the school to do about it. Your email should have a clear subject line, explain "
  "the problem in a way that someone who has not counted the bins can follow, and make "
  "one practical suggestion. Keep the tone polite and businesslike.",
  "Environment and Sustainability",
  ["purpose and audience", "structure", "clarity", "tone"]),

P("email", "text",
  "NOTICE FROM THE SHIRE COUNCIL\n\n"
  "From Monday 3 March, the bus stop on Wattle Street outside the library will be "
  "removed. Buses will instead stop on Bridge Road, about 700 metres further on. The "
  "change will let the council widen the footpath on Wattle Street. Residents who wish to "
  "comment may write to the council before 20 February.",
  "You use the Wattle Street stop every school day, and so do a number of younger "
  "students. Write an email to the council responding to the notice. Your email should "
  "explain who is affected and why the extra 700 metres matters, and should ask for "
  "something specific. Remember that the person reading it has never met you.",
  "Community and Local Government",
  ["purpose and audience", "argument", "clarity", "tone"],
  difficulty="hard"),

P("email", "scenario",
  "Your class spent six weeks organising a fundraising picnic for the local WIRES "
  "wildlife rescue volunteers. Thirty families said they would come. On the morning of the picnic it "
  "rained so hard that the oval was closed, and the picnic was called off two hours "
  "before it was due to start. Several parents had already baked, and one had borrowed a "
  "gazebo. The class has decided to try again in four weeks.",
  "Write an email to the families who volunteered. Your email should thank them, explain "
  "honestly what happened without blaming anybody, and tell them clearly what will happen "
  "next. Think about how somebody feels when work they have done comes to nothing.",
  "Community and Resilience",
  ["purpose and audience", "tone", "structure", "clarity"]),

# ===================================================== advice sheet (3)

P("advice_sheet", "scenario",
  "Every year your school gives the incoming Year 6 students a page of advice written by "
  "the students who have just finished. Year 6 is the last year before high school in "
  "New South Wales, and the teacher has asked for advice that is actually "
  "useful rather than general encouragement: the things that were confusing in the first "
  "fortnight, the habits that turned out to matter, and the worries that came to nothing.",
  "Write the advice sheet for next year's Year 6 students. Use headings or numbered "
  "points so it can be read quickly, and make every piece of advice specific enough to "
  "act on. Write as somebody who has been there, not as a teacher.",
  "School Life and Transition",
  ["purpose and audience", "organisation", "usefulness", "voice"]),

P("advice_sheet", "scenario",
  "A wetland reserve near your town has just opened a boardwalk. It passes through "
  "bushland where wading birds nest between September and January. The rangers are "
  "worried: on the first weekend, visitors left the boardwalk to get closer to the birds, "
  "a dog was let off its lead, and several people fed bread to the ducks. The rangers "
  "want a single sheet handed to visitors at the gate.",
  "Write the advice sheet the rangers will hand out. It should tell visitors what to do "
  "and, just as importantly, why each thing matters — a rule with a reason behind it is "
  "far more likely to be followed. Set it out so somebody can read it while walking.",
  "Environment and Wildlife",
  ["purpose and audience", "organisation", "reasoning", "clarity"],
  difficulty="hard"),

P("advice_sheet", "data",
  "A survey of 120 students at an Australian primary school asked how long they spend on "
  "a screen after dinner on a school night.\n\n"
  "  Less than 30 minutes ....... 18 students\n"
  "  30 minutes to 1 hour ....... 34 students\n"
  "  1 to 2 hours ............... 45 students\n"
  "  More than 2 hours .......... 23 students\n\n"
  "The same survey asked how often students felt tired at school. Of the 23 who used a "
  "screen for more than two hours, 19 said they often felt tired.",
  "Using the survey, write an advice sheet for families about screens on school nights. "
  "Refer to the figures where they help your case, but write for parents and students "
  "rather than for a statistician. Give advice that a family could actually follow on a "
  "Tuesday evening.",
  "Health and Wellbeing",
  ["use of evidence", "purpose and audience", "organisation", "clarity"],
  difficulty="hard"),

# ===================================================== article (2)

P("article", "text",
  "For thirty years nobody had seen a platypus in Bilby Creek. The creek runs through "
  "the middle of a country town, and by the 1990s it carried more shopping trolleys than "
  "fish. In 2009 a group of residents began pulling rubbish out of it on the first "
  "Saturday of every month. They planted 4000 native seedlings along the banks. In "
  "March this year a Year 5 student on a school excursion filmed a platypus near the "
  "footbridge — the first confirmed sighting since 1994.",
  "Write an article for your school newspaper about the return of the platypus to Bilby "
  "Creek. An article informs before it persuades: your reader wants to know what "
  "happened, who made it happen and why it took so long. Give your article a headline.",
  "Environment and Community Action",
  ["information", "structure", "engagement", "language"]),

P("article", "image",
  "The photograph shows a school assembly area on a Friday afternoon. Around sixty "
  "students are sitting in rows on the concrete. At the front, an older student is "
  "speaking into a microphone while holding up a hand-drawn poster. The poster reads "
  "CLEAN UP: 214 BAGS. Behind her, six younger students are holding a long paper banner "
  "that has clearly been made in a hurry. It was taken on the Friday after Clean Up "
  "Australia Day.",
  "Write an article for your school newsletter about what is happening in the "
  "photograph. You will need to invent the details the picture does not give you — who "
  "the students are, where they spent the day, how the 214 bags were counted — but "
  "everything you "
  "invent must fit what can be seen. Give your article a headline.",
  "School Life and Community",
  ["information", "structure", "invention within limits", "language"],
  image_desc="School assembly on concrete; a student at a microphone holds a poster "
             "reading CLEAN UP: 214 BAGS; six younger students hold a hand-made banner.",
  difficulty="hard"),

# ===================================================== diary (1)

P("diary", "scenario",
  "A storm brought a tree down across the power lines on your street on Thursday "
  "afternoon. The power did not come back on until Saturday morning — thirty-eight hours "
  "later. The SES crew could not reach the street until Friday morning. There was no "
  "fridge, no hot water, no internet and no lights. Your family "
  "cooked on a camping stove in the carport. Neighbours you had never spoken to came out "
  "onto the footpath after dark because there was nothing else to do.",
  "Write a diary entry made on the Saturday, looking back on the thirty-eight hours. A "
  "diary is written for yourself, so it can admit things you would not say out loud. "
  "Write about what was genuinely difficult and about anything that turned out better "
  "than expected.",
  "Community and Resilience",
  ["voice", "reflection", "detail", "language"]),

# ===================================================== news report (1)

P("news_report", "scenario",
  "Last Friday every student at your school walked laps of the oval to raise money for a "
  "children's hospital in Sydney. The walk ran from 9.30 am to 12.30 pm. Students walked 2140 laps "
  "between them, which the maths teacher worked out as 856 kilometres. The school had "
  "hoped to raise $4000 and raised $6820. A Year 3 student walked 41 laps, more than "
  "anybody else in the school. Rain at 11 am stopped the walk for twenty minutes.",
  "Write a news report about the charity walk for a local paper. A news report puts the "
  "most important facts first and saves the colour for later, and it quotes people — you "
  "may invent quotes, as long as they sound like something a real person would say. Give "
  "your report a headline.",
  "School Life and Charity",
  ["information accuracy", "structure", "use of quotes", "language"]),

# ===================================================== speech (1)

P("speech", "quote",
  "\"The people who keep a place running are usually the ones nobody thanks.\"\n\n"
  "The crossing supervisor stands on the same corner in every kind of weather. The "
  "cleaner is in the building an hour before anybody else arrives. The canteen volunteer "
  "gives up a morning a week, year after year. None of them is ever mentioned at a school "
  "assembly in Australia, and none of them expects to be.",
  "Your school holds an assembly each term at which a student speaks for two minutes "
  "about somebody whose work goes unnoticed. Write the speech you would give. Choose one "
  "person or one job — a crossing supervisor, a cleaner, a bus driver, a canteen "
  "volunteer — and make your audience see why the work matters. A speech is written to "
  "be heard, so listen to your sentences as you write them.",
  "Community and Gratitude",
  ["voice", "argument", "audience awareness", "language"],
  difficulty="hard"),

if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(PROMPTS, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {len(PROMPTS)} prompts -> {path}")
