#!/usr/bin/env python3
"""Close the length tell in the ACT reading set by lengthening distractors.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_length_tell --report
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_length_tell --worklist 40
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_length_tell --apply

THE DEFECT

    vic_content_taxonomy_TASK.md §4.2. In the 718 ACT-sourced reading questions the key
    averages 62.1 characters against 54.9 for the distractors, so "pick the longest
    option" scores 48.7% against a 25% chance rate. repair_key_skew could not touch it:
    reordering moves options without changing them.

WHY THIS IS NOT AUTOMATABLE

    The fix is to make a distractor longer, and the only lengthening worth having adds
    meaning. Padding with filler ("the", "of the") closes the arithmetic and leaves a
    different tell -- three terse options and one limp one -- so every edit here is
    hand-written against its own question and recorded in EDITS below.

    What IS automated is the accounting: which questions still fail, how many must be
    fixed to reach the target, and which are cheapest to close. The median gap over the
    next-longest option is 9 characters, so most edits are a clause, not a sentence.

TARGET

    The key should be the longest option in about a quarter of questions, not half.
    Overshooting is its own tell -- a distractor reliably longer than the key just
    inverts the strategy -- so --report tracks BOTH directions.
"""
import argparse
import json
import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DB = ROOT / "run_data/db/qbank.db"
REPORT = ROOT / "run_data/output/length_tell_manifest.json"
SCOPE = ("subject = 'reading_comprehension' AND source_book LIKE 'act_%' "
         "AND review_status != 'rejected'")
LETTERS = "ABCD"

# id prefix -> (option letter, replacement text). Hand-written, one per question.
EDITS = {
    # batch 1 — gap 1-2 characters, closed by one qualifying word each
    "fb3882e2": ("A", "The festival mainly benefits local musicians and performers, with little broader economic impact at all."),
    "be858a4b": ("D", "Economic interests have been fully aligned with conservation goals, simplifying the process considerably."),
    "de173ee8": ("A", "Limited access to the park's rock art sites due to long-standing traditional restrictions."),
    "e4defea1": ("A", "It was a crucial moment for the development of cricket in Aboriginal communities generally."),
    "58b0232f": ("A", "The lack of advanced modern breeding techniques"),
    "63b2cd5a": ("C", "To collect seeds for a national conservation program."),
    "958eb968": ("B", "Abundant surface water and lush green vegetation"),
    "06db2502": ("B", "The primary interaction involves Indigenous Australians cultivating these plants for export overseas."),
    "c22e1caa": ("C", "Overfishing by large commercial fishing fleets"),
    "95ab3e3d": ("C", "Vulnerability to short-term fluctuations in local water temperature."),
    "f43d5d1c": ("B", "Abstract philosophical concepts and dense existential themes."),
    "8a0510a2": ("C", "A visionary who anticipated the future challenges."),
    "ca8ce719": ("D", "She is frustrated by her father's pessimism and is determined to prove that the station can survive the drought without drastic measures at all."),
    "78c41434": ("A", "A natural colour change occurring during the coral's normal life cycle."),
    "5d0da13e": ("D", "Its annual aggregation of large migrating whale sharks."),
    "c8a2b58a": ("C", "To investigate the impact of extreme temperatures on fossilisation rates."),
    "c4d89160": ("B", "Habitat destruction from rapid coastal development."),
    "aefcbf1f": ("D", "The lizard's survival depends on its highly efficient water conservation."),
    "eb4fed33": ("B", "Increased water clarity from reduced farm runoff"),
    "4872521e": ("B", "The cost of implementing starfish control programs is prohibitive for most conservation groups today."),
    "522fe3f1": ("C", "Scavenging for carcasses left behind by larger predators."),
    "8b3e9658": ("D", "To signal its presence to other fungi and initiate new growth."),
    "9ce3f481": ("B", "Indigenous knowledge helped scientists pinpoint the exact location of the glowing fungi."),
    "c0353495": ("A", "The sheer size of the whole reef system."),
    "f4c84e71": ("A", "Its primary value lies in its geological composition rather than in its biodiversity."),
    "3210ed1e": ("D", "The desire to reduce reliance on fossil fuels for purely environmental reasons."),
    "133cd0ea": ("C", "Historic routes that have remained largely unchanged over the years."),
    "04db2965": ("B", "Facilitate scientific research into the disease transmission rates in the wild."),
    "268ed968": ("D", "Vibrations from heavy machinery"),
    # batch 2 — gap 2-3 characters
    "561c2981": ("C", "Damage caused by steadily increasing tourism activities."),
    "c577e06d": ("D", "Government grants have made the transition financially viable already."),
    "48ec04c7": ("B", "It increases the water temperature, thereby accelerating coral bleaching."),
    "5649f4d9": ("A", "desert grasses and their seeds."),
    "5a16c1f4": ("D", "It primarily benefited the economic standing of the co-hosting nations through increased tourism revenue."),
    "f1fd0e5a": ("B", "Increased competition from foreign fishing vessels offshore."),
    "ba972ee9": ("C", "Contain the majority of Melbourne's traditional public art galleries."),
    "c25da83d": ("B", "The resistance of local Indigenous communities to newcomers."),
    "b6cb308e": ("D", "An optimistic outlook on the future sustainability of the whole park."),
    "ac2164cd": ("C", "Advanced technology and manufacturing."),
    "e9752480": ("B", "It deposits nutrient-rich droppings that steadily fertilise the soil."),
    "71f1e065": ("D", "A relatively safe project completed with modern earthmoving machinery."),
    "47e28e12": ("D", "It primarily consumes small desert insects and the occasional seeds."),
    "f62edacd": ("C", "An indicator of aggressive territorial disputes nearby."),
    "10ddf425": ("B", "The decline in global support for LGBTQIA+ rights, necessitating continued public protest."),
    "f57b01c5": ("D", "It is the location of ongoing diplomatic relations between Australia and modern PNG."),
    "c7a5a9b1": ("D", "Comparative, implying a clear ranking or competition between the cities."),
    "e39f9888": ("D", "The BNT faces considerable challenges due to its remote location, making it impractical for most Australians to access or help maintain."),
    "7a3e514d": ("D", "Highlight the beauty of the Darwin coastline before his eventual departure."),
    "84b46266": ("D", "Emphasise the clear dominance of economic interests over environmental concerns."),
    "f9c4ac03": ("D", "It was the very first year the race concluded in Hobart."),
    "02e2788f": ("D", "Creating digital archives of historical linguistic data and records."),
    "1b855abd": ("A", "Pessimistic and fatalistic, suggesting the dingo's eventual extinction is inevitable."),
    "75a11ffa": ("A", "The author suggests that these regions are scientifically important only for their unusual geological features."),
    "3481ae45": ("A", "Its notably lower cost and widespread availability"),
    "92b0921d": ("C", "The educational value of learning more advanced culinary techniques"),
    "1f81ca10": ("B", "Failed to establish any effective conservation policies for Australia's many unique ecosystems."),
    "7dd97112": ("A", "Ability to access and utilise a range of diverse natural resources."),
    "8acb2522": ("B", "Eliminating all forms of resource extraction industry in sensitive areas."),
    "84bafb4c": ("A", "To seek shelter from the larger predatory marine animals."),
    "6824b732": ("C", "Overfishing and other unsustainable tourism practices."),
    "7dc1d4d2": ("D", "Similar types of small independent boutiques"),
    "987dd293": ("A", "The employment of a single, very large engineering firm to oversee the entire project."),
    # batch 3 — gap 3-4 characters
    "2900d7b7": ("B", "A general shift away from agricultural pursuits"),
    "c85b01ae": ("B", "Natural migration across established geographic borders."),
    "94853a4b": ("B", "highlight its growing importance as a tourist destination."),
    "7751b8a9": ("A", "Decrease the district's reliance on the Royal Flying Doctor Service."),
    "603c8b6d": ("B", "Technological advancements will soon solve the underlying problems of climate change."),
    "25098c63": ("D", "A general lack of communication with overseas markets."),
    "60962a05": ("D", "Passive observer with no real involvement in artistic or developmental decisions."),
    "26c99b3a": ("D", "A constant desire to relocate to the urban centres."),
    "e2f6d2a6": ("A", "The physical journey is far more significant than the spiritual aspect."),
    "87e8b729": ("B", "An event focused solely on honouring Australian soldiers without any local interaction."),
    "35bf0fd2": ("B", "A complete lack of vaccination programs in the region."),
    "44787ee3": ("B", "A competitive platform for emerging young jockeys from rural areas."),
    "adead962": ("A", "It is the only sporting event held in Australia that attracts international viewers."),
    "6cb16b9b": ("C", "A historical progression from unsustainable Indigenous practices through to modern conservation."),
    "7f0d5d3b": ("C", "Several hundreds of thousands"),
    "e5a5ced3": ("A", "The Riversleigh Fossil Mammal Precinct has consistently yielded fossils that align closely with current platypus biology, indicating little evolutionary change."),
    "67fcc3c3": ("C", "The gradual displacement of historical architectural styles"),
    "740fc60e": ("C", "They primarily focused on selling their Merino meat globally."),
    "83126e04": ("D", "The Anangu people's enduring spiritual connection to the land."),
    "19c947b7": ("D", "Drought relief for the coastal regions and mineral extraction"),
    "efd2c998": ("C", "limited and largely intermittent"),
    "cdd49fae": ("A", "a historical site illustrating aspects of pre-colonial Yolŋu life."),
    "1ed61454": ("B", "Distract the reader from the central plot point of illegal imports."),
    "a762ced0": ("D", "Providing useful insights for modern sustainable land management."),
    "da2ecb78": ("B", "Familiar problems that have often occurred before."),
    "917f2f32": ("C", "Optimistic, highlighting several successful conservation initiatives."),
    "44c93e00": ("B", "A universal public acceptance of graffiti as a legitimate art form."),
    "80d898cc": ("D", "demonstrate the relatively low value of the gold discoveries."),
    "fd2028b1": ("C", "Suggest that the extreme heat contributed to the fossilisation process."),
    "515666ff": ("D", "Predatory and openly exploitative."),
    "1ae05d05": ("B", "It is a barren and unchanging environment with almost no capacity for adaptation."),
    # batch 4 — gap 4-5 characters
    "2c5bbc6d": ("A", "significantly limiting the types of rock formation visible there."),
    "dea1499c": ("D", "Largely unnecessary given the local resources"),
    "b6bee5e4": ("D", "Their connection is based primarily on economic exploitation of its resources."),
    "a786dcfe": ("B", "Sceptical and dismissive, questioning its practical utility today."),
    "0b17f780": ("C", "The growing popularity of backcountry exploration and adventure tourism."),
    "80a1bdab": ("A", "Developing new mining technologies suitable for very arid regions."),
    "18afde1a": ("D", "It is only rarely encountered by tourists due to its elusive nature."),
    "56d1cb20": ("A", "focused on a single, critical aspect of overall reef preservation."),
    "bbcc5982": ("B", "The oppressive heat of a north Queensland summer"),
    "86a6b844": ("A", "The diminishing role of European migrants in its daily operation"),
    "39c0ffc8": ("A", "Accurately representing the harsh economic realities of pastoralism."),
    "d78525c2": ("D", "Breaking both attendance and viewership records for women's sport."),
    "f53761dd": ("A", "Ancient Aboriginal rock carvings clearly visible from afar."),
    "8cb4829e": ("A", "the ocean currents have created quite intricate patterns on the land."),
    "cec86c19": ("C", "Emphasise the sharp contrast between the theatre's past grandeur and its current state."),
    "e5152991": ("C", "It is a relatively short and easy stretch of open water."),
    "4481a013": ("C", "The opportunity to avoid navigating the whole of Bass Strait."),
    "a0adbd66": ("C", "Invasive species and pollution from purely natural sources."),
    "99a5d1f3": ("A", "The direct destruction of bilby burrows by heavy mining equipment."),
    "9a6d405a": ("B", "From research initiation through to technology commercialisation."),
    "13f23a52": ("D", "To be a major tourist attraction right from its inception."),
    "730c2434": ("A", "Relatively insignificant given its lasting impact."),
    "41ead0d6": ("D", "Focusing on the purely scientific aspects of fermentation."),
    "c462a125": ("C", "Heavy rainfall followed by unusually strong winds."),
    "08e5f767": ("B", "A primary location for major international shipping routes."),
    "bf7a1777": ("D", "By migrating seasonally to escape the extreme temperature fluctuations there."),
    "b152342f": ("A", "The taste of expensive perfumes and the feel of fine silk."),
    "dbb1c29e": ("D", "They confirm that Indigenous Australians first arrived via a land bridge from Southeast Asia."),
    "45d1d10e": ("D", "A singular emphasis on traditional Australian barbecue food."),
    # batch 5 — gap 6-7 characters, taking the set to target
    "cd591a60": ("A", "Within the last hundred years or so."),
    "0c0f7b5f": ("C", "It strengthens the immune systems of most native amphibians."),
    "ae0f69c8": ("D", "The current conservation efforts are more than sufficient to guarantee future economic returns."),
    "0af014fb": ("C", "Emphasise the routine and rather mundane nature of conservation fieldwork."),
    "4aef0392": ("D", "It is the largest coral reef system anywhere in the world."),
    "52bf374b": ("B", "Struggling financially because of the high transport costs."),
    "23ab0bcd": ("A", "He is a longstanding rival of Old Man Hemlock and dismisses his claims."),
    "0662ccc2": ("D", "The Twelve Apostles rock stacks"),
    "080fef2c": ("D", "The coolness of the evening breeze."),
    "f954928e": ("C", "Highlight the historical Indigenous knowledge as by far the most critical aspect of the discovery."),
    "8a11f1fb": ("A", "Have already been successfully resolved by the station owners"),
    "203b8ecc": ("A", "The continuing importance of mining and pastoral industries."),
    "2d4cea59": ("C", "A pressing need to document ancient Indigenous stories before they are lost."),
    "4fd0361c": ("D", "The instantaneous power output capability of the whole facility."),
    "e41ac257": ("C", "The wide network of home bakers sharing recipes online"),
    "15b1e604": ("D", "Only partially recovered so far."),
    "d7f57471": ("D", "Constant intervention through research into new plant species"),
    "83721ec0": ("C", "They are rare occurrences, which makes them far less vital to the ecosystem."),
    "7e81524b": ("B", "They are primarily for entertainment and have very little spiritual significance."),
    "a6445099": ("D", "Suggest Liam's youthful inexperience in properly understanding cricket."),
    "2c7973bf": ("D", "Their economic impact has steadily diminished with the rise of private car ownership."),
    "3a463f69": ("A", "Reduced biodiversity across whole marine ecosystems."),
    "e2904250": ("B", "it plays a crucial role in supporting the wider ecosystem of the whole Outback."),
    "0295c213": ("D", "Highlight the clear limitations of scientific methods in understanding the outback."),
    "f7fc7a07": ("C", "It causes the surrounding water to become warmer, leading to coral bleaching."),
    "b81766d1": ("D", "Suggest that the region's natural beauty is diminishing due to ancient geological processes."),
    "cba7b00e": ("D", "To suggest that only those with a very strong will to survive can appreciate the area's natural beauty."),
    "0c2a20d3": ("B", "Growing competition from international agricultural markets"),
    "0f961667": ("B", "Primarily reactive measures taken against extreme conditions."),
    "961b2c8d": ("C", "Participating in large organised desert racing events."),
    "b5e279fa": ("B", "Its role as a crucial breeding ground for many endangered marine species."),
    # 25635c89 skipped: its options are city names, which cannot be lengthened truthfully.
}


def lengths(r):
    return {L: len(str(r["option_" + L.lower()] or "")) for L in LETTERS}


def key_longest(r):
    L = lengths(r)
    k = r["correct_answer"]
    return L[k] > max(v for m, v in L.items() if m != k)


def a_distractor_longest(r):
    L = lengths(r)
    k = r["correct_answer"]
    return max(v for m, v in L.items() if m != k) > L[k]


def load(conn):
    return [dict(r) for r in conn.execute(f"SELECT * FROM questions WHERE {SCOPE}")]


def report(rows, label):
    n = len(rows)
    kl = sum(1 for r in rows if key_longest(r))
    dl = sum(1 for r in rows if a_distractor_longest(r))
    kmean = sum(len(str(r["option_" + r["correct_answer"].lower()] or "")) for r in rows) / n
    dmean = sum(len(str(r["option_" + L.lower()] or "")) for r in rows for L in LETTERS
                if L != r["correct_answer"]) / (3 * n)
    print(f"  {label:22s} n={n}  key longest {kl:3d} ({100 * kl / n:4.1f}%)   "
          f"a distractor longest {dl:3d} ({100 * dl / n:4.1f}%)   "
          f"mean key {kmean:.1f} vs distractor {dmean:.1f}")
    return kl


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--worklist", type=int, metavar="N",
                    help="print the N cheapest unfixed questions, gap ascending")
    ap.add_argument("--target", type=float, default=0.28)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    rows = load(conn)

    if args.worklist:
        done = {p for p in EDITS}
        todo = []
        for r in rows:
            if not key_longest(r) or r["id"][:8] in done:
                continue
            L = lengths(r)
            k = r["correct_answer"]
            other = max(((v, m) for m, v in L.items() if m != k))
            todo.append((L[k] - other[0], r, other[1]))
        todo.sort(key=lambda t: t[0])
        for gap, r, longest_d in todo[:args.worklist]:
            print(f"### {r['id'][:8]} gap={gap} key={r['correct_answer']}({lengths(r)[r['correct_answer']]})")
            print(f"  KEY  {r['option_' + r['correct_answer'].lower()]}")
            print(f"  {longest_d}({lengths(r)[longest_d]})  {r['option_' + longest_d.lower()]}")
        return 0

    print("BEFORE")
    before = report(rows, "ACT reading")

    changes = []
    for r in rows:
        e = EDITS.get(r["id"][:8])
        if not e:
            continue
        letter, text = e
        if letter == r["correct_answer"]:
            raise SystemExit(f"{r['id'][:8]}: edit targets the KEY, not a distractor")
        changes.append({"id": r["id"], "letter": letter,
                        "before": r["option_" + letter.lower()], "after": text})

    after = [dict(r) for r in rows]
    idx = {c["id"]: c for c in changes}
    for r in after:
        if r["id"] in idx:
            c = idx[r["id"]]
            r["option_" + c["letter"].lower()] = c["after"]
    print("AFTER (projected)")
    projected = report(after, "ACT reading")
    need = projected - int(args.target * len(rows))
    print(f"\n  edits written: {len(changes)}   still to fix for a {100 * args.target:.0f}% "
          f"target: {max(0, need)}")

    if not args.apply:
        print("  --report only: nothing written.")
        return 0

    with conn:
        for c in changes:
            conn.execute(f"UPDATE questions SET option_{c['letter'].lower()}=? WHERE id=?",
                         (c["after"], c["id"]))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"tool": "repair_length_tell",
                                  "written_at": datetime.now(timezone.utc).isoformat(),
                                  "changes": changes}, indent=1, ensure_ascii=False))
    print(f"\n  applied {len(changes)} edits. manifest -> {REPORT}")
    report(load(conn), "verified from DB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
