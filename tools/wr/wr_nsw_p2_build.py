#!/usr/bin/env python3
"""Builds wr_nsw_selective_p2.json — 21 more NSW writing prompts, taking the set to 42.

21 felt thin for launch, and on the numbers it was thinner than it looked: ten of those
21 carry Victorian calibration (target_year 9-10, 25 minutes, up to 500 words), so the
pool actually usable for a Year 6 sitting was 11. Worse, all three narrative and all
three persuasive prompts are among those ten — the two forms most likely to be set had
no correctly calibrated prompt at all.

This batch adds narrative 3, persuasive 3, diary 3, speech 3, news report 3, email 2,
article 2, advice sheet 2 = 21, all at Year 6 / 30 minutes. After it:

  every form           5 or 6 prompts, 42 in total
  correctly calibrated 32, covering all eight forms
  still mis-calibrated 10, unchanged and still flagged

So the pool stands up whether or not the ten are eventually retired.

Stimulus types are spread deliberately: no form is all-scenario, and the set as a whole
carries text, quote, data and image alongside the scenarios.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/writing/generated"
BOOK = "wr_nsw_selective"
NN = 2
NOW = datetime.datetime(2026, 8, 8, 11, 0, 0, tzinfo=datetime.timezone.utc) \
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


# ===================================================== narrative (3)

P("narrative", "quote",
  "\"The last thing I expected was for the door to be unlocked.\"\n\n"
  "The shed had stood at the bottom of the paddock, on a property in the Riverina, for "
  "as long as anyone in the family "
  "could remember. Nobody had a key. Every summer somebody said they would get around to "
  "cutting the padlock off, and every summer nobody did.",
  "Write a narrative that begins with the sentence above. Your story can go anywhere the "
  "opening allows, but it must earn its ending — a reader should be able to look back and "
  "see the ending coming. Give at least one character something they want.",
  "Narrative - Discovery",
  ["ideas", "structure", "characterisation", "language"]),

P("narrative", "scenario",
  "You borrow a battered library book about the Snowy Mountains and find a note folded "
  "inside the back cover. It is written in careful handwriting and dated forty years ago. "
  "It says: 'If you are reading this, the book is still on the shelf, and that is worth "
  "knowing. Write back and tell me one thing that has changed.' Underneath is an address "
  "in a town two hours away, in southern New South Wales.",
  "Write a narrative about what happens next. You may take the story in any direction — "
  "the address may be a house, a paddock or a post office that closed years ago — but the "
  "note has to matter to your main character by the end.",
  "Narrative - Connection Across Time",
  ["ideas", "structure", "characterisation", "language"],
  difficulty="hard"),

P("narrative", "image",
  "The photograph shows a corrugated iron shed at the edge of a dry paddock in inland "
  "Australia. A child's bicycle is leaning against the wall, and the front wheel is "
  "missing. The shed door is open a hand's width. Long afternoon shadows run away from "
  "the shed towards the camera. There are no people in the picture.",
  "Write a narrative set in the place shown in the photograph. Everything in the picture "
  "should have a reason for being there by the time your story ends — including the "
  "missing wheel. Do not simply describe the scene; something has to happen in it.",
  "Narrative - Place and Absence",
  ["ideas", "setting", "structure", "language"],
  image_desc="A corrugated iron shed at the edge of a dry inland paddock; a child's "
             "bicycle with no front wheel leans against it; the door is ajar; long "
             "afternoon shadows; nobody in shot.",
  difficulty="hard"),

# ===================================================== persuasive (3)

P("persuasive", "text",
  "FROM THE LOCAL PAPER\n\n"
  "The shire council will vote next month on whether to close the skate park beside the "
  "river and use the land for extra parking. The council says the car park is needed for "
  "the Saturday markets. The skate park was built in 2011 and is used by about forty young "
  "people on a weekday afternoon. There is no other skate park within thirty kilometres.",
  "Write a persuasive piece arguing for or against the closure, to be sent to the council "
  "before the vote. Choose one side and hold it. Deal with the strongest point on the "
  "other side rather than pretending it is not there — an argument that ignores the car "
  "park is easy to dismiss.",
  "Community and Public Space",
  ["argument", "use of evidence", "structure", "language"],
  difficulty="hard"),

P("persuasive", "scenario",
  "Your school, in western Sydney, has run a vegetable garden for eight years. Every class has a bed, and the "
  "produce goes to the canteen. The school now needs somewhere to put twelve extra staff "
  "car spaces, and the garden is the only flat ground left. The principal has invited "
  "written views from students before deciding.",
  "Write a persuasive piece putting your view to the principal. You may argue to keep the "
  "garden, to give it up, or to do something else with the space — but whatever you argue, "
  "you have to explain what happens to the problem your view does not solve.",
  "School Life and Decision Making",
  ["argument", "structure", "audience awareness", "language"]),

P("persuasive", "quote",
  "\"In a country like this one, learning to swim is not a hobby. It is a safety skill.\"\n\n"
  "Some Australian schools run swimming lessons for every student in Years 3 to 6, paid "
  "for out of the school budget. Others offer nothing, and families arrange lessons "
  "themselves. Pool hire and buses are expensive, and time spent at the pool is time not "
  "spent in class.",
  "Write a persuasive piece arguing whether swimming lessons should be compulsory in all "
  "Australian primary schools. Use the quote if it helps you, or argue against it. Be "
  "specific about who pays and what is given up, because that is where the real "
  "disagreement lies.",
  "Health and Public Policy",
  ["argument", "use of evidence", "structure", "language"],
  difficulty="hard"),

# ===================================================== diary (3)

P("diary", "scenario",
  "Your family has moved from a farm outside Dubbo to a third-floor flat in Sydney. It is "
  "the end of your first day. The flat has no yard. You can hear a neighbour's television "
  "through the wall. From the balcony you can see the tops of trees in a park two streets "
  "away, and further off, a train. Your dog stayed behind with your grandparents.",
  "Write a diary entry for the end of that first day. A diary can hold two things at once "
  "— write about what you have lost and about anything, however small, that you did not "
  "expect to like.",
  "Change and Belonging",
  ["voice", "reflection", "detail", "language"]),

P("diary", "scenario",
  "You finished last in the 800 metres at the interschool athletics carnival in "
  "Tamworth. You had "
  "trained for it since February. What you did not expect was that when you came round "
  "the final bend, well behind everybody, your whole school stood up along the fence and "
  "made more noise than they had for the winner.",
  "Write a diary entry made that evening. Be honest about both parts of the day — the "
  "result and the noise — and about the fact that they do not cancel each other out.",
  "Sport and Self-Knowledge",
  ["voice", "reflection", "honesty", "language"],
  difficulty="hard"),

P("diary", "scenario",
  "Today was your first morning volunteering at an RSPCA animal shelter in Wollongong. You "
  "expected puppies. What you got was three hours of hosing out concrete runs, a dog that "
  "would not come out of the back of its pen no matter what you did, and a staff member "
  "who has worked there eleven years and did not once sound tired of it.",
  "Write a diary entry about the morning. Diaries record what actually happened rather "
  "than what should have happened, so write about the gap between what you expected and "
  "what you found.",
  "Community and Responsibility",
  ["voice", "reflection", "detail", "language"]),

# ===================================================== speech (3)

P("speech", "scenario",
  "Each year your school, like many across Australia, gives an award to the student who "
  "has done most for other "
  "students — not the best at anything, but the one the school would miss. Any student may "
  "nominate somebody by speaking for two minutes at assembly. You have decided to nominate "
  "a classmate whose contribution is easy to overlook.",
  "Write the speech nominating your classmate. You will need to invent the person and what "
  "they have done. Give the assembly at least one specific moment they can picture, "
  "because a list of qualities convinces nobody.",
  "School Life and Recognition",
  ["voice", "argument", "audience awareness", "language"]),

P("speech", "quote",
  "\"You can tell a lot about a town by what it decides to keep.\"\n\n"
  "The old railway goods shed on the edge of your town, in the New South Wales wheat "
  "belt, has been empty for twenty years. "
  "The council will decide next month whether to demolish it or spend the money to make it "
  "safe and open it as a community hall. Both options cost money the council says it does "
  "not really have.",
  "Write a speech to be given at the council meeting arguing for one option. You are "
  "speaking to adults who will vote straight afterwards, so be clear about what you want "
  "them to do and why the cost is worth it.",
  "Community and Heritage",
  ["argument", "audience awareness", "structure", "language"],
  difficulty="hard"),

P("speech", "scenario",
  "It is the last week of Year 6. One student is asked to speak at the final assembly, in "
  "front of the whole school, the teachers and a hall full of families. The Year 6 group "
  "has been together since Kindergarten and most of them are going to different high "
  "schools across Sydney next year.",
  "Write the speech you would give. It has to work for three audiences at once — the "
  "friends who were there, the younger students who were not, and the families at the back "
  "of the hall. Avoid the phrases everybody expects; find something true instead.",
  "School Life and Endings",
  ["voice", "audience awareness", "structure", "language"],
  difficulty="hard"),

# ===================================================== news report (3)

P("news_report", "data",
  "Figures released by a wildlife group about a forest in northern New South Wales that "
  "burnt in the 2019 bushfires:\n\n"
  "  Koalas counted before the fires (2019) ....... 240\n"
  "  Koalas counted after the fires (2020) ........  61\n"
  "  Koalas counted this year ..................... 148\n"
  "  Hectares of habitat replanted since 2020 ..... 310\n"
  "  Volunteers involved .......................... 1200\n\n"
  "The group says numbers are unlikely to return to 2019 levels before 2040.",
  "Write a news report about the koala figures for a state newspaper. Lead with what "
  "matters most, use the numbers rather than listing them, and include a quote from "
  "somebody involved. You may invent the quote and the speaker's name and role.",
  "Environment and Recovery",
  ["information accuracy", "structure", "use of quotes", "language"],
  difficulty="hard"),

P("news_report", "scenario",
  "At about 6 am yesterday a humpback whale was found tangled in netting about 400 metres "
  "off a beach on the New South Wales coast. A crew from the marine rescue service worked "
  "for five hours in a small boat to cut the netting away. The whale swam off just after "
  "11 am. Around 200 people watched from the headland. Nobody was hurt.",
  "Write a news report of the rescue for the following morning's paper. Readers were not "
  "there, so they need the facts in an order that makes sense, and they need to be told "
  "what is still unknown as well as what is settled.",
  "Environment and Rescue",
  ["information accuracy", "structure", "clarity", "language"]),

P("news_report", "text",
  "COUNCIL MEDIA RELEASE\n\n"
  "The Wattle Creek shared path opens on Saturday. The 4.2 kilometre path connects the "
  "primary school, the swimming pool and the shopping centre, and replaces a route along "
  "the highway that had no footpath for 800 metres. Construction took fourteen months and "
  "cost $2.6 million. Three hundred trees were planted along the route.",
  "Write a news report about the opening of the Wattle Creek path for a local paper. A media release is "
  "written by the council to make the council look good; a news report is not. Use the "
  "facts, but ask the questions a reader would ask.",
  "Community and Infrastructure",
  ["information accuracy", "structure", "independence", "language"],
  difficulty="hard"),

# ===================================================== email (2)

P("email", "scenario",
  "Your school library has almost nothing written by Aboriginal and Torres Strait "
  "Islander authors, and what it has is twenty years old. You and two friends have made a "
  "list of eight titles you would like the library to buy, with reasons. The teacher "
  "librarian has a small budget each term and has asked students to make their case in "
  "writing rather than at the desk.",
  "Write an email to the teacher librarian making the case. You will not have room to "
  "argue for all eight titles, so choose: it is better to make one or two convincing than "
  "eight in a list. Say clearly what you are asking for.",
  "Library and Representation",
  ["purpose and audience", "argument", "clarity", "tone"],
  difficulty="hard"),

P("email", "text",
  "AN EMAIL YOUR CLASS HAS RECEIVED\n\n"
  "Hello from Year 6 at Alice Springs. Our teacher set up this exchange so we can each "
  "find out what school is like somewhere very different. We would like to know three "
  "things: what you can see from your classroom window, what everybody at your school is "
  "talking about this week, and one thing about where you live that we would get wrong if "
  "we only read about it. Please write back.",
  "Write the email your class sends in reply. Answer all three questions, and answer the "
  "third one properly — the interesting part is the gap between how a place looks from "
  "outside and how it actually is.",
  "Community and Perspective",
  ["purpose and audience", "content", "voice", "clarity"]),

# ===================================================== article (2)

P("article", "text",
  "The passenger line to your town in central New South Wales closed in 1975. The rails "
  "stayed where they were, rusting through the wheat country, and the station became a "
  "storage shed. In 2019 a "
  "group of volunteers began clearing the platform. Last month, after seven years of work "
  "and a state government grant, a tourist train ran the 46 kilometres from the junction "
  "into town. Four hundred people came to the station to watch it arrive. The oldest was "
  "94 and had travelled on the last service in 1975.",
  "Write an article about the return of the train for a regional newspaper. An article "
  "gives the reader the story and the background together — they need to know what "
  "happened last month and why it took fifty years. Give your article a headline.",
  "History and Community",
  ["information", "structure", "engagement", "language"]),

P("article", "data",
  "A survey of how 200 students at one Australian primary school get to school:\n\n"
  "  Driven by a family member .... 96 students\n"
  "  Walk ......................... 54 students\n"
  "  Bus .......................... 32 students\n"
  "  Ride a bike .................. 18 students\n\n"
  "Students were also asked how far they live from school. Of the 96 who are driven, 41 "
  "live less than one kilometre away.",
  "Write an article for the school newsletter about how students get to school. Explain "
  "what the figures show, including the part that is most likely to surprise a reader, and "
  "be careful not to claim more than the survey can support. Give your article a headline.",
  "Transport and Community Habits",
  ["information", "use of evidence", "structure", "language"],
  difficulty="hard"),

# ===================================================== advice sheet (2)

P("advice_sheet", "scenario",
  "Year 6 goes on a three-day camp in the Blue Mountains each year. The teachers hand out "
  "a sheet about what to pack and when the bus leaves. They have asked this year's group "
  "to write a second sheet — the one about everything else. Last year several students "
  "were homesick on the second night, two brought no warm clothes because the forecast "
  "said 24 degrees, and nobody had told them how cold a valley gets after dark.",
  "Write the advice sheet for next year's campers. Cover the things the teachers' sheet "
  "does not, use headings so it can be skimmed on the bus, and be honest about the "
  "difficult parts rather than promising everybody a wonderful time.",
  "School Camps and Preparation",
  ["purpose and audience", "organisation", "usefulness", "voice"]),

P("advice_sheet", "scenario",
  "Between August and November, magpies nesting near your school swoop people who walk "
  "past. Two students have been hit this month. The school has had complaints from "
  "families wanting the birds removed, and a letter from a local naturalist pointing out "
  "that the same pair has nested in that tree for six years, that swooping stops when the "
  "chicks fledge, and that magpies remember individual faces.",
  "Write an advice sheet for students about walking past the nesting tree. It has to be "
  "practical enough to follow on the way to school and fair to the birds at the same time. "
  "Explain why each piece of advice works, not just what to do.",
  "Wildlife and Coexistence",
  ["purpose and audience", "organisation", "reasoning", "clarity"],
  difficulty="hard"),

if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(PROMPTS, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {len(PROMPTS)} prompts -> {path}")
