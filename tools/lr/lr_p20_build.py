#!/usr/bin/env python3
"""Builds lr_thinking_skills_p20.json — 32 §5.2 critical-thinking questions.

who reasons correctly 12, conditional chains 10, necessary vs sufficient 10. §5.2 goes
135/396 to 167/396 — the legacy batch had already built across seven of its nine
subcategories, so this is a deepening rather than an opening. Only identify_flaw still
holds nothing.

§5.2 is judgement work in the main — weakening an argument, naming an unstated
assumption, telling correlation from causation. Those cannot be decided mechanically and
will be built with different care. But three of the nine subcategories are formal
reasoning in everyday clothes, and this batch takes all three, because for those the
checker in lr_logic settles the answer outright: every option is tested against every
world in which the premises hold, and the build fails unless exactly one survives.

That matters most for the traps. Most of these items exist to catch affirming the
consequent or denying the antecedent, so the tempting wrong answer sits one careless
step from the key — exactly the case where a writer checking their own work by reading
is least reliable.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import (  # noqa: E402
    ALL, BOTHo, EXACTLY_ONEo, IFo, ISo, NEITHERo, NO, NOTHING, NOTo, ORo, SOME,
    Scenario, syllogism,
)

B = Batch(nn=20)


def says(name, claim):
    """A named student's conclusion, as the option text reads."""
    return f"{name}: '{claim}'"


# ===================================================== who reasons correctly (12)

# Set logic, not if-then: "every novel is on the top shelf" is a claim about all the
# novels, which a fact-per-book encoding cannot express.
_c1 = syllogism(["topshelf", "novel", "atlas"],
                [ALL("topshelf", "novel"), NO("atlas", "novel")],
                [(says("Ana", "The atlas is not on the top shelf"), NO("atlas", "topshelf")),
                 (says("Ben", "The atlas is on the top shelf"), ALL("atlas", "topshelf")),
                 (says("Cara", "Every novel is on the top shelf"), ALL("novel", "topshelf")),
                 (says("Dev", "No novel is on the top shelf"), NO("novel", "topshelf"))])
B.Q("who_reasons_correctly",
    "Every book on the top shelf is a novel. The atlas is not a novel. Four students each "
    "draw a conclusion. Which one has reasoned correctly?",
    key=_c1, verify=says("Ana", "The atlas is not on the top shelf"),
    wrong=[says("Ben", "The atlas is on the top shelf"),
           says("Cara", "Every novel is on the top shelf"),
           says("Dev", "No novel is on the top shelf")],
    expl="If the atlas were on the top shelf it would have to be a novel, and it is not, so "
         "it cannot be up there. Cara turns the rule around, which it never allows — novels "
         "may sit on any shelf in the room.",
    difficulty="medium", confidence=0.92),

_S2 = Scenario(["cancelled", "calledoff", "refunds"],
               rules=[IFo("cancelled", "calledoff"), IFo("calledoff", "refunds")],
               given=[ISo("cancelled")])
_c2 = _S2.pick([(says("Eve", "Refunds are given"), _S2.here(ISo("refunds"))),
                (says("Finn", "No refunds are given"), _S2.here(NOTo("refunds"))),
                (says("Gia", "The tour went ahead"), _S2.here(NOTo("calledoff"))),
                (says("Hal", "Refunds are given only when the ferry is cancelled"),
                 _S2.always(IFo("refunds", "cancelled")))])
B.Q("who_reasons_correctly",
    "If the ferry is cancelled, the tour is called off. If the tour is called off, refunds "
    "are given. The ferry was cancelled. Which student has reasoned correctly?",
    key=_c2, verify=says("Eve", "Refunds are given"),
    wrong=[says("Finn", "No refunds are given"),
           says("Gia", "The tour went ahead"),
           says("Hal", "Refunds are given only when the ferry is cancelled")],
    expl="The two rules link into a chain: a cancelled ferry calls off the tour, and a "
         "called-off tour brings refunds. Hal reads the chain backwards — refunds might be "
         "given for other reasons entirely.",
    difficulty="medium", confidence=0.92),

# a second ferry stem scored 0.871 against the first, above phase 4's silent 0.85 drop,
# so the backwards-chain item moved to a different setting entirely
_S3 = Scenario(["ovenbroke", "boughtin", "pricerose"],
               rules=[IFo("ovenbroke", "boughtin"), IFo("boughtin", "pricerose")],
               given=[NOTo("pricerose")])
_c3 = _S3.pick([(says("Ivy", "The oven did not break"), _S3.here(NOTo("ovenbroke"))),
                (says("Jed", "The oven broke"), _S3.here(ISo("ovenbroke"))),
                (says("Kim", "The bread was bought in"), _S3.here(ISo("boughtin"))),
                (says("Leo", "The price never rises"), _S3.always(NOTo("pricerose")))])
B.Q("who_reasons_correctly",
    "If the bakery's oven breaks down, the bread has to be bought in. If the bread is "
    "bought in, the price goes up. This week the price did not go up. Which student has "
    "reasoned correctly?",
    key=_c3, verify=says("Ivy", "The oven did not break"),
    wrong=[says("Jed", "The oven broke"),
           says("Kim", "The bread was bought in"),
           says("Leo", "The price never rises")],
    expl="Run the chain backwards from the end. A steady price means the bread was not "
         "bought in, and that means the oven did not break down. Kim goes forwards from a "
         "fact that was never given.",
    difficulty="hard", confidence=0.91),

_S4 = Scenario(["member", "borrowed"], rules=[IFo("borrowed", "member")],
               given=[ISo("borrowed")])
_c4 = _S4.pick([(says("Mia", "Tom is a member"), _S4.here(ISo("member"))),
                (says("Noor", "Tom is not a member"), _S4.here(NOTo("member"))),
                (says("Oli", "Every member has borrowed something"),
                 _S4.always(IFo("member", "borrowed"))),
                (says("Pia", "Tom will borrow again next term"), _S4.later(ISo("borrowed")))])
B.Q("who_reasons_correctly",
    "Only members may borrow equipment from the club. Tom borrowed a tent. Which student "
    "has reasoned correctly?",
    key=_c4, verify=says("Mia", "Tom is a member"),
    wrong=[says("Noor", "Tom is not a member"),
           says("Oli", "Every member has borrowed something"),
           says("Pia", "Tom will borrow again next term")],
    expl="'Only members may borrow' means anyone who borrows must be a member, so Tom is "
         "one. Oli reads it the other way round, as though membership required borrowing, "
         "which the rule does not say.",
    difficulty="medium", confidence=0.92),

# "tomorrow the shop will be open" was the first draft of Uma's option, and it is a
# second correct answer: if today is Sunday and the shop opens every other day, tomorrow
# is Monday and it opens. The model checker missed it only because its second occasion is
# an unrelated day rather than the next one. Uma now claims something the statement really
# does leave open, carried by a fact with no rule attached to it.
_S5 = Scenario(["sunday", "open", "busy"], rules=[EXACTLY_ONEo("open", "sunday")],
               given=[NOTo("open")])
_c5 = _S5.pick([(says("Ravi", "Today is Sunday"), _S5.here(ISo("sunday"))),
                (says("Sia", "Today is not Sunday"), _S5.here(NOTo("sunday"))),
                (says("Tam", "The shop never opens"), _S5.always(NOTo("open"))),
                (says("Uma", "The shop is busy on Saturdays"), _S5.here(ISo("busy")))])
B.Q("who_reasons_correctly",
    "The shop is open every day except Sunday, when it is closed. Today the shop is closed. "
    "Which student has reasoned correctly?",
    key=_c5, verify=says("Ravi", "Today is Sunday"),
    wrong=[says("Sia", "Today is not Sunday"),
           says("Tam", "The shop never opens"),
           says("Uma", "The shop is busy on Saturdays")],
    expl="Sunday is the only day the shop closes, so a closed shop means today is Sunday. "
         "Uma's claim may well be true, but nothing in the statement is about how busy the "
         "shop is, so it cannot be reasoned to.",
    difficulty="hard", confidence=0.91),

_S6 = Scenario(["red", "blue"], given=[ORo("red", "blue"), NOTo("red")])
_c6 = _S6.pick([(says("Vic", "The prize is in the blue box"), _S6.here(ISo("blue"))),
                (says("Wren", "The prize is in the red box"), _S6.here(ISo("red"))),
                (says("Xia", "The prize is in neither box"), _S6.here(NEITHERo("red", "blue"))),
                (says("Yan", "Both boxes hold a prize"), _S6.here(BOTHo("red", "blue")))])
B.Q("who_reasons_correctly",
    "The prize is in the red box or the blue box. It is not in the red box. Which student "
    "has reasoned correctly?",
    key=_c6, verify=says("Vic", "The prize is in the blue box"),
    wrong=[says("Wren", "The prize is in the red box"),
           says("Xia", "The prize is in neither box"),
           says("Yan", "Both boxes hold a prize")],
    expl="One of the two boxes holds the prize. Ruling out the red one leaves only the blue "
         "one. Xia's conclusion contradicts the first statement outright.",
    difficulty="medium", confidence=0.92),

_c7 = syllogism(["cake", "eggy", "sameats"],
                [ALL("cake", "eggy"), NO("sameats", "eggy")],
                [(says("Zed", "Sam cannot eat any of the cakes at the stall"),
                  NO("sameats", "cake")),
                 (says("Amy", "Sam can eat some of the cakes at the stall"),
                  SOME("sameats", "cake")),
                 (says("Bo", "Everything containing eggs is a cake from the stall"),
                  ALL("eggy", "cake")),
                 (says("Cy", "Everything Sam eats is a cake"), ALL("sameats", "cake"))])
B.Q("who_reasons_correctly",
    "Every cake at the stall contains eggs. Sam cannot eat anything containing eggs. Which "
    "student has reasoned correctly?",
    key=_c7, verify=says("Zed", "Sam cannot eat any of the cakes at the stall"),
    wrong=[says("Amy", "Sam can eat some of the cakes at the stall"),
           says("Bo", "Everything containing eggs is a cake from the stall"),
           says("Cy", "Everything Sam eats is a cake")],
    expl="Every cake there has eggs in it, and Sam eats nothing with eggs, so no cake at the "
         "stall is open to Sam. Bo reverses the first statement: eggs turn up in plenty of "
         "food that is not a cake from this stall.",
    difficulty="hard", confidence=0.91),

_c8 = syllogism(["year6", "excursion", "atschool"],
                [ALL("year6", "excursion"), NO("excursion", "atschool")],
                [(says("Dee", "Nobody in Year 6 was at school"), NO("year6", "atschool")),
                 (says("Eli", "Everybody at school was in Year 6"), ALL("atschool", "year6")),
                 (says("Fay", "Some of Year 6 were at school"), SOME("year6", "atschool")),
                 (says("Gus", "Only Year 6 went on the excursion"),
                  ALL("excursion", "year6"))])
B.Q("who_reasons_correctly",
    "Everyone in Year 6 went on the excursion. Nobody who went on the excursion was at "
    "school that day. Which student has reasoned correctly?",
    key=_c8, verify=says("Dee", "Nobody in Year 6 was at school"),
    wrong=[says("Eli", "Everybody at school was in Year 6"),
           says("Fay", "Some of Year 6 were at school"),
           says("Gus", "Only Year 6 went on the excursion")],
    expl="All of Year 6 was on the excursion, and nobody on the excursion was at school, so "
         "no Year 6 student was at school. Gus adds a restriction the statements never "
         "make: other year levels may have gone along too.",
    difficulty="hard", confidence=0.90),

_S9 = Scenario(["lowtide", "visible"], rules=[IFo("lowtide", "visible")],
               given=[NOTo("visible")])
_c9 = _S9.pick([(says("Hana", "The tide is not low"), _S9.here(NOTo("lowtide"))),
                (says("Ike", "The tide is low"), _S9.here(ISo("lowtide"))),
                (says("Jo", "The rock pools are never visible"), _S9.always(NOTo("visible"))),
                (says("Kai", "Only a low tide makes them visible"),
                 _S9.always(IFo("visible", "lowtide")))])
B.Q("who_reasons_correctly",
    "Whenever the tide is low, the rock pools are visible. Today the rock pools are not "
    "visible. Which student has reasoned correctly?",
    key=_c9, verify=says("Hana", "The tide is not low"),
    wrong=[says("Ike", "The tide is low"),
           says("Jo", "The rock pools are never visible"),
           says("Kai", "Only a low tide makes them visible")],
    expl="A low tide would guarantee visible rock pools. They are not visible, so the tide "
         "cannot be low. Kai turns a guarantee into the only possible cause, which is a "
         "stronger claim than was made.",
    difficulty="hard", confidence=0.91),

_S10 = Scenario(["kai", "lia"], given=[ORo("kai", "lia"), NOTo("lia")])
_c10 = _S10.pick([(says("Lena", "Kai has the key"), _S10.here(ISo("kai"))),
                  (says("Moss", "Nobody has the key"), _S10.here(NEITHERo("kai", "lia"))),
                  (says("Nina", "Lia has the key"), _S10.here(ISo("lia"))),
                  (says("Otto", "Kai and Lia each have a key"),
                   _S10.here(BOTHo("kai", "lia")))])
B.Q("who_reasons_correctly",
    "Either Kai or Lia has the key to the store room. Lia does not have it. Which student "
    "has reasoned correctly?",
    key=_c10, verify=says("Lena", "Kai has the key"),
    wrong=[says("Moss", "Nobody has the key"),
           says("Nina", "Lia has the key"),
           says("Otto", "Kai and Lia each have a key")],
    expl="One of the two has the key, and it is not Lia, so it is Kai. Moss's conclusion "
         "denies the first statement instead of using it.",
    difficulty="medium", confidence=0.92),

_c11 = syllogism(["winner", "medalled", "jo"],
                 [ALL("winner", "medalled"), NO("jo", "medalled")],
                 [(says("Pearl", "Jo did not win"), NO("jo", "winner")),
                  (says("Quill", "Jo won"), ALL("jo", "winner")),
                  (says("Rhys", "Everyone with a medal won"), ALL("medalled", "winner")),
                  (says("Sasha", "Nobody with a medal won"), NO("medalled", "winner"))])
B.Q("who_reasons_correctly",
    "All the winners received a medal. Jo did not receive a medal. Which student has "
    "reasoned correctly?",
    key=_c11, verify=says("Pearl", "Jo did not win"),
    wrong=[says("Quill", "Jo won"),
           says("Rhys", "Everyone with a medal won"),
           says("Sasha", "Nobody with a medal won")],
    expl="Winning brings a medal with it, and Jo has no medal, so Jo did not win. Rhys "
         "reverses that: medals might also go to helpers or to everyone who took part.",
    difficulty="medium", confidence=0.92),

_S12 = Scenario(["raining", "indoors", "hallbooked"],
                rules=[IFo("raining", "indoors"), IFo("indoors", "hallbooked")],
                given=[NOTo("hallbooked")])
_c12 = _S12.pick([(says("Tao", "It is not raining"), _S12.here(NOTo("raining"))),
                  (says("Umi", "It is raining"), _S12.here(ISo("raining"))),
                  (says("Vale", "Sport is indoors"), _S12.here(ISo("indoors"))),
                  (says("Wynn", "The hall is booked only when it rains"),
                   _S12.always(IFo("hallbooked", "raining")))])
B.Q("who_reasons_correctly",
    "If it is raining, sport is held indoors. If sport is held indoors, the hall is booked. "
    "The hall has not been booked. Which student has reasoned correctly?",
    key=_c12, verify=says("Tao", "It is not raining"),
    wrong=[says("Umi", "It is raining"),
           says("Vale", "Sport is indoors"),
           says("Wynn", "The hall is booked only when it rains")],
    expl="No booking means sport is not indoors, and that means it is not raining. Wynn "
         "reverses the chain: the hall could equally be booked for a concert.",
    difficulty="hard", confidence=0.90),

# ===================================================== conditional chains (10)

_D1 = Scenario(["frost", "cover", "survive"],
               rules=[IFo("frost", "cover"), IFo("cover", "survive")], given=[ISo("frost")])
_d1 = _D1.pick([("The seedlings survive", _D1.here(ISo("survive"))),
                ("The seedlings do not survive", _D1.here(NOTo("survive"))),
                ("The covers were not needed", _D1.here(NOTo("cover"))),
                ("Only a frost brings the covers out", _D1.always(IFo("cover", "frost")))])
B.Q("conditional_chains",
    "If there is a frost, the covers go on. If the covers go on, the seedlings survive. "
    "There was a frost last night. Which one of these must be true?",
    key=_d1, verify="The seedlings survive",
    wrong=["The seedlings do not survive", "The covers were not needed",
           "Only a frost brings the covers out"],
    expl="Frost leads to covers, and covers lead to survival, so a frost leads to survival "
         "in two steps. The covers might also go on before hail or a heatwave, so the last "
         "option claims more than the rules give.",
    difficulty="medium", confidence=0.92),

_D2 = Scenario(["rain", "muddy", "cancelled"],
               rules=[IFo("rain", "muddy"), IFo("muddy", "cancelled")],
               given=[NOTo("cancelled")])
_d2 = _D2.pick([("It did not rain", _D2.here(NOTo("rain"))),
                ("It rained", _D2.here(ISo("rain"))),
                ("The ground is muddy", _D2.here(ISo("muddy"))),
                ("Only rain cancels the match", _D2.always(IFo("cancelled", "rain")))])
B.Q("conditional_chains",
    "If it rains, the ground becomes muddy. If the ground is muddy, the match is cancelled. "
    "The match was not cancelled. Which one of these must be true?",
    key=_d2, verify="It did not rain",
    wrong=["It rained", "The ground is muddy", "Only rain cancels the match"],
    expl="Working backwards: no cancellation means the ground was not muddy, and dry ground "
         "means it did not rain. Each step undoes one rule.",
    difficulty="hard", confidence=0.91),

_D3 = Scenario(["study", "pass", "certificate"],
               rules=[IFo("study", "pass"), IFo("pass", "certificate")],
               given=[NOTo("study")])
_d3 = _D3.pick([("The certificate may or may not be awarded", NOTHING),
                ("The certificate is awarded", _D3.here(ISo("certificate"))),
                ("The certificate is not awarded", _D3.here(NOTo("certificate"))),
                ("The test was failed", _D3.here(NOTo("pass")))])
B.Q("conditional_chains",
    "If Ada studies, she passes. If she passes, she gets a certificate. Ada did not study. "
    "Which one of these must be true?",
    key=_d3, verify="The certificate may or may not be awarded",
    wrong=["The certificate is awarded", "The certificate is not awarded",
           "The test was failed"],
    expl="The rules say what happens when Ada studies, not what happens when she does not. "
         "She might pass anyway and collect the certificate, or she might not, so neither "
         "outcome can be relied on. Concluding she failed is the common slip.",
    difficulty="hard", confidence=0.90),

_D4 = Scenario(["signup", "trained", "compete"],
               rules=[IFo("signup", "trained"), IFo("trained", "compete")],
               given=[ISo("compete")])
_d4 = _D4.pick([("Nothing follows about signing up", NOTHING),
                ("Ben signed up", _D4.here(ISo("signup"))),
                ("Ben did not sign up", _D4.here(NOTo("signup"))),
                ("Ben was trained", _D4.here(ISo("trained")))])
B.Q("conditional_chains",
    "If Ben signs up, he is trained. If he is trained, he may compete. Ben competed. Which "
    "one of these must be true?",
    key=_d4, verify="Nothing follows about signing up",
    wrong=["Ben signed up", "Ben did not sign up", "Ben was trained"],
    expl="The rules run from signing up towards competing, not back the other way. Ben may "
         "have reached the competition by a route the rules never mention, so the fact that "
         "he competed settles nothing about signing up.",
    difficulty="hard", confidence=0.90),

_D5 = Scenario(["late", "walk", "tired"],
               rules=[IFo("late", "walk"), IFo("walk", "tired")], given=[NOTo("tired")])
_d5 = _D5.pick([("The bus was not late", _D5.here(NOTo("late"))),
                ("The bus was late", _D5.here(ISo("late"))),
                ("Priya walked", _D5.here(ISo("walk"))),
                ("Priya is never tired", _D5.always(NOTo("tired")))])
B.Q("conditional_chains",
    "If the bus is late, Priya walks. If Priya walks, she arrives tired. Today Priya did not "
    "arrive tired. Which one of these must be true?",
    key=_d5, verify="The bus was not late",
    wrong=["The bus was late", "Priya walked", "Priya is never tired"],
    expl="Not tired means she did not walk, and not walking means the bus was not late. "
         "Today's fact says nothing about any other day, so the last option overreaches.",
    difficulty="hard", confidence=0.91),

_D6 = Scenario(["fullmoon", "hightide", "flooded", "closed"],
               rules=[IFo("fullmoon", "hightide"), IFo("hightide", "flooded"),
                      IFo("flooded", "closed")],
               given=[ISo("fullmoon")])
_d6 = _D6.pick([("The path is closed", _D6.here(ISo("closed"))),
                ("The path is open", _D6.here(NOTo("closed"))),
                ("The tide is low", _D6.here(NOTo("hightide"))),
                ("Only a full moon closes the path",
                 _D6.always(IFo("closed", "fullmoon")))])
B.Q("conditional_chains",
    "A full moon brings a high tide. A high tide floods the path. A flooded path is closed. "
    "Tonight there is a full moon. Which one of these must be true?",
    key=_d6, verify="The path is closed",
    wrong=["The path is open", "The tide is low", "Only a full moon closes the path"],
    expl="Three rules link into one chain: full moon, high tide, flooded path, closed path. "
         "The last option reverses the chain, and storms or repairs could close the path "
         "with no moon involved.",
    difficulty="medium", confidence=0.92),

_D7 = Scenario(["power", "lights", "alarm"],
               rules=[IFo("power", "lights"), IFo("lights", "alarm")], given=[NOTo("alarm")])
_d7 = _D7.pick([("The power is off", _D7.here(NOTo("power"))),
                ("The power is on", _D7.here(ISo("power"))),
                ("The lights are on", _D7.here(ISo("lights"))),
                ("The alarm is armed every night", _D7.always(ISo("alarm")))])
B.Q("conditional_chains",
    "If the power is on, the lights work. If the lights work, the alarm is armed. Tonight "
    "the alarm is not armed. Which one of these must be true?",
    key=_d7, verify="The power is off",
    wrong=["The power is on", "The lights are on", "The alarm is armed every night"],
    expl="No armed alarm means the lights are not working, and that means the power is off. "
         "The last option is contradicted by tonight itself.",
    difficulty="hard", confidence=0.91),

_D8 = Scenario(["earlybird", "discount", "member"],
               rules=[IFo("earlybird", "discount"), IFo("discount", "member")],
               given=[NOTo("member")])
_d8 = _D8.pick([("The ticket was not an early-bird ticket", _D8.here(NOTo("earlybird"))),
                ("The ticket was an early-bird ticket", _D8.here(ISo("earlybird"))),
                ("A discount was given", _D8.here(ISo("discount"))),
                ("Members always book early", _D8.always(IFo("member", "earlybird")))])
B.Q("conditional_chains",
    "An early-bird ticket always carries a discount. A discount is only given to members. "
    "The buyer is not a member. Which one of these must be true?",
    key=_d8, verify="The ticket was not an early-bird ticket",
    wrong=["The ticket was an early-bird ticket", "A discount was given",
           "Members always book early"],
    expl="A non-member gets no discount, and no discount means the ticket cannot have been "
         "an early-bird one. The last option swaps the rule around: being a member says "
         "nothing about when somebody books.",
    difficulty="hard", confidence=0.90),

_D9 = Scenario(["snow", "roadclosed", "schoolshut"],
               rules=[IFo("snow", "roadclosed"), IFo("roadclosed", "schoolshut")],
               given=[ISo("schoolshut")])
_d9 = _D9.pick([("Nothing follows about the snow", NOTHING),
                ("It snowed", _D9.here(ISo("snow"))),
                ("It did not snow", _D9.here(NOTo("snow"))),
                ("The road is closed", _D9.here(ISo("roadclosed")))])
B.Q("conditional_chains",
    "If it snows, the mountain road closes. If the road closes, the school shuts. Today the "
    "school is shut. Which one of these must be true?",
    key=_d9, verify="Nothing follows about the snow",
    wrong=["It snowed", "It did not snow", "The road is closed"],
    expl="A shut school is where the chain ends, not where it starts. The school might be "
         "shut for a public holiday or a burst pipe, so neither the road nor the snow can "
         "be worked out from it.",
    difficulty="hard", confidence=0.90),

_D10 = Scenario(["practise", "improve", "selected"],
                rules=[IFo("practise", "improve"), IFo("improve", "selected")],
                given=[ISo("practise")])
_d10 = _D10.pick([("Cleo is selected", _D10.here(ISo("selected"))),
                  ("Cleo is not selected", _D10.here(NOTo("selected"))),
                  ("Cleo did not improve", _D10.here(NOTo("improve"))),
                  ("Only those who practise are selected",
                   _D10.always(IFo("selected", "practise")))])
B.Q("conditional_chains",
    "If Cleo practises daily, she improves. If she improves, she is selected. Cleo practised "
    "daily all term. Which one of these must be true?",
    key=_d10, verify="Cleo is selected",
    wrong=["Cleo is not selected", "Cleo did not improve",
           "Only those who practise are selected"],
    expl="Practice leads to improvement, and improvement leads to selection, so Cleo is "
         "selected. The last option is a different claim: somebody else might be selected "
         "for a talent they never had to practise.",
    difficulty="medium", confidence=0.92),

# ===================================================== necessary vs sufficient (10)

_e1 = syllogism(["team", "swimmer", "kim"],
                [ALL("team", "swimmer"), ALL("kim", "swimmer")],
                [("Everyone in the team can swim 200 m", ALL("team", "swimmer")),
                 ("Kim is in the team", ALL("kim", "team")),
                 ("Kim is not in the team", NO("kim", "team")),
                 ("Everyone who can swim 200 m is in the team", ALL("swimmer", "team"))])
B.Q("necessary_vs_sufficient",
    "To join the swimming team you must be able to swim 200 metres. Kim can swim 200 "
    "metres. Which one of these must be true?",
    key=_e1, verify="Everyone in the team can swim 200 m",
    wrong=["Kim is in the team", "Kim is not in the team",
           "Everyone who can swim 200 m is in the team"],
    expl="Swimming 200 metres is something the team requires, not something that gets you "
         "in. Kim meets the requirement, but there may be trials, fees or a full squad, so "
         "membership does not follow.",
    difficulty="hard", confidence=0.91),

_E2 = Scenario(["passed", "certificate"], rules=[IFo("passed", "certificate")],
               given=[NOTo("passed")])
_e2 = _E2.pick([("Nothing follows about the certificate", NOTHING),
                ("Ali received the certificate", _E2.here(ISo("certificate"))),
                ("Ali did not receive the certificate", _E2.here(NOTo("certificate"))),
                ("Only those who pass receive one", _E2.always(IFo("certificate", "passed")))])
B.Q("necessary_vs_sufficient",
    "Passing the test is enough on its own to earn the certificate. Ali did not pass. Which "
    "one of these must be true?",
    key=_e2, verify="Nothing follows about the certificate",
    wrong=["Ali received the certificate", "Ali did not receive the certificate",
           "Only those who pass receive one"],
    expl="Passing is enough, but the statement never says it is the only way. Ali may have "
         "earned the certificate by attendance or by a second attempt, so failing the test "
         "settles nothing.",
    difficulty="hard", confidence=0.90),

_e3 = syllogism(["entrant", "under13", "sam"],
                [ALL("entrant", "under13"), ALL("sam", "under13")],
                [("Everyone in the competition is under 13", ALL("entrant", "under13")),
                 ("Sam is in the competition", ALL("sam", "entrant")),
                 ("Sam is not in the competition", NO("sam", "entrant")),
                 ("Everyone under 13 is in the competition", ALL("under13", "entrant"))])
B.Q("necessary_vs_sufficient",
    "You may enter the competition only if you are under 13. Sam is 11. Which one of these "
    "must be true?",
    key=_e3, verify="Everyone in the competition is under 13",
    wrong=["Sam is in the competition", "Sam is not in the competition",
           "Everyone under 13 is in the competition"],
    expl="'Only if' sets a condition entrants must meet; it does not enter anybody. Sam "
         "qualifies on age but may simply not have entered.",
    difficulty="hard", confidence=0.91),

_E4 = Scenario(["ticket", "entry"], rules=[IFo("entry", "ticket")], given=[ISo("ticket")])
_e4 = _E4.pick([("Nothing follows about whether she went in", NOTHING),
                ("She went in", _E4.here(ISo("entry"))),
                ("She did not go in", _E4.here(NOTo("entry"))),
                ("A ticket guarantees entry", _E4.always(IFo("ticket", "entry")))])
B.Q("necessary_vs_sufficient",
    "Nobody is let into the concert without a ticket. Nadia has a ticket. Which one of these "
    "must be true?",
    key=_e4, verify="Nothing follows about whether she went in",
    wrong=["She went in", "She did not go in", "A ticket guarantees entry"],
    expl="A ticket is needed to get in, which is not the same as a ticket being enough. "
         "Nadia might have arrived late, changed her mind, or been turned away for some "
         "other reason.",
    difficulty="hard", confidence=0.90),

_E5 = Scenario(["watered", "grows"], rules=[IFo("grows", "watered")], given=[NOTo("watered")])
_e5 = _E5.pick([("The plant did not grow", _E5.here(NOTo("grows"))),
                ("The plant grew", _E5.here(ISo("grows"))),
                ("Every watered plant grows", _E5.always(IFo("watered", "grows"))),
                ("Nothing follows about whether it grew", NOTHING)])
B.Q("necessary_vs_sufficient",
    "A plant cannot grow unless it is watered. This plant was never watered. Which one of "
    "these must be true?",
    key=_e5, verify="The plant did not grow",
    wrong=["The plant grew", "Every watered plant grows",
           "Nothing follows about whether it grew"],
    expl="Water is a requirement for growth, so no water means no growth. That does not run "
         "the other way: watering alone will not make a plant grow, since it also needs "
         "light and warmth.",
    difficulty="medium", confidence=0.92),

_E6 = Scenario(["licence", "drive"], rules=[IFo("drive", "licence")], given=[NOTo("licence")])
_e6 = _E6.pick([("Jules did not drive", _E6.here(NOTo("drive"))),
                ("Jules drove", _E6.here(ISo("drive"))),
                ("Everybody with a licence drives", _E6.always(IFo("licence", "drive"))),
                ("Nothing follows about whether Jules drove", NOTHING)])
B.Q("necessary_vs_sufficient",
    "It is illegal to drive without a licence, and nobody in this family breaks the law. "
    "Jules has no licence. Which one of these must be true?",
    key=_e6, verify="Jules did not drive",
    wrong=["Jules drove", "Everybody with a licence drives",
           "Nothing follows about whether Jules drove"],
    expl="A licence is required before anyone in this family will drive, so without one "
         "Jules did not drive. Holding a licence would not have forced Jules to drive "
         "either — it only permits it.",
    difficulty="medium", confidence=0.92),

_e7 = syllogism(["scholar", "essay", "rin"],
                [ALL("scholar", "essay"), ALL("rin", "essay")],
                [("Every scholarship winner wrote an essay", ALL("scholar", "essay")),
                 ("Rin won a scholarship", ALL("rin", "scholar")),
                 ("Rin did not win a scholarship", NO("rin", "scholar")),
                 ("Everyone who wrote an essay won a scholarship", ALL("essay", "scholar"))])
B.Q("necessary_vs_sufficient",
    "Every scholarship winner had to write an essay. Rin wrote an essay. Which one of these "
    "must be true?",
    key=_e7, verify="Every scholarship winner wrote an essay",
    wrong=["Rin won a scholarship", "Rin did not win a scholarship",
           "Everyone who wrote an essay won a scholarship"],
    expl="Writing an essay was required of the winners, so all of them wrote one. Many "
         "others will have written essays and won nothing, so Rin's essay decides it "
         "neither way.",
    difficulty="hard", confidence=0.91),

_E8 = Scenario(["sunny", "picnic"], rules=[IFo("sunny", "picnic")], given=[NOTo("sunny")])
_e8 = _E8.pick([("Nothing follows about the picnic", NOTHING),
                ("The picnic went ahead", _E8.here(ISo("picnic"))),
                ("The picnic was cancelled", _E8.here(NOTo("picnic"))),
                ("Sunshine is needed for the picnic", _E8.always(IFo("picnic", "sunny")))])
B.Q("necessary_vs_sufficient",
    "Sunshine is enough for the picnic to go ahead. Saturday was not sunny. Which one of "
    "these must be true?",
    key=_e8, verify="Nothing follows about the picnic",
    wrong=["The picnic went ahead", "The picnic was cancelled",
           "Sunshine is needed for the picnic"],
    expl="Sunshine guarantees the picnic, but a cloudy dry day might do just as well — the "
         "statement never made sunshine a requirement. So the lack of it decides nothing.",
    difficulty="hard", confidence=0.90),

_E9 = Scenario(["key", "opened"], rules=[IFo("opened", "key")], given=[ISo("opened")])
_e9 = _E9.pick([("Somebody had the key", _E9.here(ISo("key"))),
                ("Nobody had the key", _E9.here(NOTo("key"))),
                ("Having the key means the door is open", _E9.always(IFo("key", "opened"))),
                ("Nothing follows about the key", NOTHING)])
B.Q("necessary_vs_sufficient",
    "The store room door cannot be opened without the key. This morning the door was open. "
    "Which one of these must be true?",
    key=_e9, verify="Somebody had the key",
    wrong=["Nobody had the key", "Having the key means the door is open",
           "Nothing follows about the key"],
    expl="The key is required to open the door, so an open door means somebody had it. The "
         "reverse does not hold: plenty of people hold keys to doors they leave shut.",
    difficulty="medium", confidence=0.92),

_E10 = Scenario(["topmark", "prize"], rules=[IFo("topmark", "prize")], given=[ISo("prize")])
_e10 = _E10.pick([("Nothing follows about the top mark", NOTHING),
                  ("Ola had the top mark", _E10.here(ISo("topmark"))),
                  ("Ola did not have the top mark", _E10.here(NOTo("topmark"))),
                  ("Only the top mark wins the prize",
                   _E10.always(IFo("prize", "topmark")))])
B.Q("necessary_vs_sufficient",
    "The top mark in the class is enough to win the prize. Ola won the prize. Which one of "
    "these must be true?",
    key=_e10, verify="Nothing follows about the top mark",
    wrong=["Ola had the top mark", "Ola did not have the top mark",
           "Only the top mark wins the prize"],
    expl="The top mark wins the prize, but the statement does not say it is the only way to "
         "win one. Ola may have taken the prize for effort or for improvement instead.",
    difficulty="hard", confidence=0.90),

B.write()
