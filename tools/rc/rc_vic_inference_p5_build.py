#!/usr/bin/env python3
"""VIC informational inference top-up, batch p5 — 4 passages x 3 items, completing 84.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.rc.rc_vic_inference_p5_build

Passages and items only; the machinery, the admissibility rule and the confidence
rubric live in tools/rc/vic_inference_common.py.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.rc.vic_inference_common import build, write  # noqa: E402

PAGE = 5

PASSAGES = [
    ("harbour_bridge", "act_test8", 641, "The opening of the Sydney Harbour Bridge in 1932"),
    ("nullarbor_geo",  "act_test5", 391, "The vast expanse of the Nullarbor Plain, straddling the border"),
    ("trams",          "act_test4", 302, "Melbourne's iconic trams"),
    ("outback_flora",  "act_test4", 304, "The vast, sun-drenched expanses of the Australian Outback"),
]

ITEMS = {
"harbour_bridge": [
 ("structure",
  "The passage takes the bridge in which order?",
  ["a biography of Sir John Bradfield and his engineering career",
   "why it mattered, how it was built, and how it began its life",
   "an argument that the workers on it were treated unjustly",
   "a comparison of the bridge with other harbour crossings abroad"],
  "B",
  "It opens on the symbolic weight of the achievement, moves to the workers and the cost, and closes on the opening day and what followed. A biography of Sir John Bradfield and his engineering career rests on one sentence naming him as chief engineer.",
  {"A": "wrong_focus", "C": "overreach", "D": "unsupported"}, [], 0.90),
 ("inference",
  "The passage sets the bridge against a nation grappling with the Great Depression and notes Bradfield's hope of stimulating recovery. Together these suggest:",
  ["that the Depression held up the bridge's completion",
   "that the final cost came in below what had been forecast",
   "that Bradfield objected to the scale the design reached",
   "that the bridge was meant to do more than carry traffic"],
  "D",
  "A crossing intended to stimulate recovery is doing economic work as well as physical work, which is why the Depression is mentioned at all. That the Depression held up the bridge's completion is not stated; the dates given run without interruption from 1923 to 1932.",
  {"A": "unsupported", "B": "overreach", "C": "contradicts"}, [], 0.91),
 ("author_purpose",
  "The passage recounts Francis De Groot slashing the ribbon ahead of the official party. Including that episode works to:",
  ["explain why Premier Lang lost office not long afterwards",
   "suggest the opening of the bridge had to be postponed",
   "show that the occasion was not altogether a united one",
   "identify the person who first crossed the finished bridge"],
  "C",
  "A protest at the ceremony itself puts a dissenting voice inside an event the passage otherwise treats as triumphant. To identify the person who first crossed the finished bridge is true of De Groot in a narrow sense but mistakes an incidental detail for the reason the episode is told.",
  {"A": "unsupported", "B": "contradicts", "D": "half_right"}, [], 0.88),
],
"nullarbor_geo": [
 ("comparison",
  "How does the passage set what lies above the Nullarbor against what lies beneath it?",
  ["both the surface and the caves below are described as lifeless",
   "the cave systems are said to be larger than the plain above them",
   "the surface is bare while what lies below is full of life",
   "the caves are expected to be opened up to visiting tourists"],
  "C",
  "The plain is treeless and arid, while the passages beneath hold ancient ecosystems with specialised flora and fauna. That both the surface and the caves below are described as lifeless denies the very contrast the passage is built on.",
  {"A": "contradicts", "B": "unsupported", "D": "overreach"}, [], 0.90),
 ("author_purpose",
  "The passage explains that the name Nullarbor comes from the Latin for 'no trees'. Supplying that derivation works to:",
  ["establish which European explorers first named the plain",
   "argue the name gives a misleading impression of the terrain",
   "explain how Latin came to enter Australian place names",
   "have the term itself echo what has just been described"],
  "D",
  "The gloss arrives immediately after the plain is called treeless, so the name confirms the description rather than adding a fact. To argue the name gives a misleading impression of the terrain is the reverse of the passage, which calls it an apt description.",
  {"A": "unsupported", "B": "contradicts", "C": "wrong_focus"}, [], 0.89),
 ("inference",
  "The passage closes by saying the region demands a careful and informed approach from any visitor. This most strongly implies:",
  ["that visitors are being discouraged from entering the region",
   "that only trained geologists are equipped to explore there",
   "that the cave systems have been closed for safety reasons",
   "that the plain repays preparation rather than mere travel"],
  "D",
  "The sentence asks something of the visitor rather than turning them away, and it follows a paragraph calling the place scientifically rich. That visitors are being discouraged from entering the region misreads a condition of going as a reason not to.",
  {"A": "contradicts", "B": "overreach", "C": "unsupported"}, [], 0.90),
],
"trams": [
 ("structure",
  "The material in this passage is ordered as:",
  ["a case for extending the tram network further outward",
   "a comparison of Melbourne's trams with those overseas",
   "origins, then present scale, then what is being changed",
   "an account of how electric traction replaced the horses"],
  "C",
  "It starts in 1906 and the horse-drawn trams before it, gives the size of today's network, and ends on the low-floor fleet now being introduced. An account of how electric traction replaced the horses is one clause of the opening rather than the shape of the passage.",
  {"A": "overreach", "B": "unsupported", "D": "wrong_focus"}, [], 0.91),
 ("inference",
  "New trams are described as improving accessibility and carrying energy-efficient technologies. Mentioning both suggests:",
  ["that all of the older trams have now been withdrawn",
   "that accessibility was the network's original purpose",
   "that energy costs are the network's largest single expense",
   "that modernising serves aims beyond transport itself"],
  "D",
  "Disability access and environmental goals are both named as things the new fleet answers, neither of which is about moving people faster. That accessibility was the network's original purpose is contradicted by a network begun in the 1880s and only recently adapted.",
  {"A": "overreach", "B": "contradicts", "C": "unsupported"}, [], 0.89),
 ("author_purpose",
  "The passage supplies the network's track length, its number of stops and its annual passengers. Giving these figures works to:",
  ["show the network has grown faster than any other system",
   "explain the way the original tram routes were planned",
   "argue that the network has now become overcrowded",
   "back a claim about importance with something measurable"],
  "D",
  "The numbers arrive attached to the words largest and underscores its importance, so they exist to make an assertion checkable. To argue that the network has now become overcrowded reads a passenger total as a complaint the passage never makes.",
  {"A": "overreach", "B": "wrong_focus", "C": "unsupported"}, [], 0.90),
],
"outback_flora": [
 ("comparison",
  "The Mulga, the spinifex and the saltbush are each given a sentence. How does the passage relate them?",
  ["all three are described as storing water within their tissues",
   "each meets the same shortage by a different means",
   "the Mulga is presented as the most successful of the three",
   "the three are expected to vanish as the droughts lengthen"],
  "B",
  "One sheds its leaves, one sends down deep roots, and one stores water, so the shared problem of drought produces three unlike solutions. That all three are described as storing water within their tissues is true only of the saltbush.",
  {"A": "contradicts", "C": "unsupported", "D": "overreach"}, [], 0.91),
 ("structure",
  "The material here is laid out in which sequence?",
  ["a comparison of Outback soils with soils found elsewhere",
   "an argument for legally protecting the species it names",
   "adaptation, then human use, then a closing reflection",
   "a description of how Indigenous medicines are prepared"],
  "C",
  "Plant survival occupies the first half, Indigenous knowledge and use the second, and the final sentence steps back to nature's ingenuity. An argument for legally protecting the species it names imports a demand the passage never makes.",
  {"A": "unsupported", "B": "overreach", "D": "wrong_focus"}, [], 0.90),
 ("inference",
  "The passage says these plants are not merely survivalists but integral to culture, medicine and sustenance. This turn implies:",
  ["that the plants would not survive without human tending",
   "that Indigenous uses have displaced the plants' ecological role",
   "that scientists disagree about how the adaptations evolved",
   "that the plants are being given a second kind of value"],
  "D",
  "The word merely concedes the first account of the plants and then adds another on top of it. That Indigenous uses have displaced the plants' ecological role turns an addition into a substitution the sentence does not make.",
  {"A": "contradicts", "B": "overreach", "C": "unsupported"}, [], 0.90),
],
}


if __name__ == "__main__":
    write(build(PASSAGES, ITEMS, PAGE), PAGE)
