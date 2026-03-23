"""
backstory.py — Procedural character origin story generator.

Assembles a single paragraph of narrative prose from template fragment banks
keyed to the player's character-creation choices: background (early life),
dominant stat (personal quality), profession category (career entry), and
faction (closing orientation).  Follows the same structural pattern as gnn.py:
module-level fragment banks + one public function.

Paragraph structure:
  [OPENING] [FORMATIVE_ENV] [PIVOT] [PROFESSIONAL_ENTRY] [FORWARD_LOOK]

The character is always framed as young — recently qualified, newly commissioned,
at the start of their independent career rather than its summit.
"""

import random


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _pick(bank: dict, key: str, **fmt) -> str:
    """
    Select a random fragment from bank[key], falling back to bank["default"].
    Returns an empty string if neither key nor "default" exists.
    Interpolates {name}, {profession}, and any other fmt kwargs.
    """
    options = bank.get(key) or bank.get("default") or [""]
    return random.choice(options).format(**fmt)


# ---------------------------------------------------------------------------
# OPENING — sets scene and character origin.  Keyed by background name.
# ---------------------------------------------------------------------------

_OPENING = {
    "Shipborn Integrative": [
        "{name} grew up in the corridors of a long-haul vessel, learning the ship's rhythms before they could walk a straight line in gravity.",
        "Born to a crew rotation aboard a deep-range transport, {name} never knew a childhood that wasn't measured in jump cycles and docking rotations.",
        "Before {name} had a room of their own, they had a bunk assignment and a duty roster — growing up shipboard meant growing up with purpose baked in from the start.",
    ],
    "Ecological Symbiosis": [
        "Raised in a living biosphere where forests tracked weather patterns and rivers encoded colony data, {name} learned to read the world before they learned to read text.",
        "{name} spent their youth among stewardship communities, where every child was assigned a patch of ecosystem to tend — and to listen to.",
        "The biosphere that raised {name} was not a passive environment: it responded, communicated, and occasionally demanded — a childhood curriculum that no formal academy could replicate.",
    ],
    "Cognitive Engineering": [
        "By the time most children were still learning to read, {name} had already been paired with an adaptive AI tutor in one of the galaxy's elite research enclaves.",
        "{name} was selected for advanced cognitive development early, raised alongside AI companions in an enclave designed to produce the next generation of systems thinkers.",
        "Recursive problem-solving and cognitive augmentation tools were part of daily life before {name}'s eighth year — not privileges, but curriculum.",
    ],
    "Ritual-Cultural Synthesis": [
        "Growing up at the crossroads of three different species' diplomatic traditions, {name} learned early that every ceremony is a negotiation and every gesture a vocabulary.",
        "{name} came of age in a cultural convergence hub, where rituals from a dozen worlds were performed side by side, and identity itself was a collaborative project.",
        "The diplomatic hubs where {name} was raised treated childhood as an extended exercise in cultural translation — a background that turned ambiguity into a tool rather than an obstacle.",
    ],
    "Frontier Autonomy": [
        "There were no authority structures where {name} grew up — just edge systems, jury-rigged equipment, and the expectation that you'd figure things out before they killed you.",
        "{name} was barely a teenager when they first repaired a failing life-support relay alone, somewhere on the frontier where the nearest repair depot was three jump points away.",
        "The outer systems that shaped {name}'s early years had one consistent lesson: solve the problem in front of you with the tools you have, because nothing else is coming.",
    ],
    "Economic Flow Immersion": [
        "Raised in an orbital marketplace where commodity prices were posted on the walls like art, {name} developed an instinct for trade flows before they developed an instinct for most other things.",
        "{name} spent their formative years in a logistics hub, tracking the movement of goods across six species and four currencies — first as a game, then as a vocation.",
        "The interstellar market systems that surrounded {name}'s childhood weren't abstract — they were infrastructure, weather, and social fabric all at once.",
    ],
    "Temporal Awareness": [
        "Growing up in a region afflicted by chrono-synthetic flux, {name} never took the linearity of time for granted — some days repeated, some afternoons arrived before their mornings.",
        "{name} was raised in a community that treated temporal perception as a trainable skill, where children were taught to hold multiple timelines in mind simultaneously.",
        "Time ran at variable rates in the region where {name} grew up, an environmental condition that required its inhabitants to treat causality as a discipline rather than an assumption.",
    ],
    "Embodied Craft": [
        "In the artisan guild world where {name} was raised, identity was inseparable from making — you were what you built, and childhood was measured in the complexity of your constructions.",
        "{name} grew up in a nano-fabrication community where the first lesson every child learned was the grain structure of metal, and the second was how to make it serve you.",
        "The guild world that formed {name} held a simple belief: that the surest path to understanding any system is to take it apart and build it again, better.",
    ],
    "default": [
        "{name} came from a corner of the settled galaxy where ambition and circumstance shaped early choices more than any formal curriculum.",
        "The circumstances of {name}'s early life were ordinary in outline and formative in detail — the kind of background that only becomes legible in retrospect.",
    ],
}


# ---------------------------------------------------------------------------
# FORMATIVE_ENV — deepens the background context.  Keyed by background name.
# ---------------------------------------------------------------------------

_FORMATIVE_ENV = {
    "Shipborn Integrative": [
        "Learning was event-driven: navigation emergencies became physics lessons, crew disputes became diplomacy practice, and system failures were the most effective examinations imaginable.",
        "Multi-species crew bonds were formed early and lasted long — a childhood shaped by shared quarters and shared problems across cultural lines that most people never cross.",
        "Systems integration wasn't a specialty — it was the water {name} swam in, absorbed through proximity to people who kept a ship alive through coordination rather than heroism.",
    ],
    "Ecological Symbiosis": [
        "Control was never the lesson; participation was — ecological modeling and long-term stewardship were values instilled before formal schooling began.",
        "The biosphere communicated in distress signals, abundance cycles, and encoded datasets that required patience and attention to read — an education in listening at scale.",
        "Stewardship meant accepting that some things took longer than a childhood to understand, and that understanding them imperfectly was better than controlling them precisely.",
    ],
    "Cognitive Engineering": [
        "Simulation design, abstract reasoning, and recursive problem-solving were daily exercises — not preparation for something harder, but the thing itself.",
        "Abstract systems were treated as learnable languages, each one a lens that changed what problems were visible and which solutions became obvious.",
        "The enclave's methodology was simple: expose young minds to increasingly complex systems and trust that pattern recognition would do the rest.",
    ],
    "Ritual-Cultural Synthesis": [
        "Conflict resolution was mediated through shared ceremony, and emotional knowledge was encoded in performance — the body remembered what the mind couldn't always articulate.",
        "Identity formation was a collective process, shaped by participation in rituals from cultures not one's own — a self that was always partly borrowed and better for it.",
        "The convergence hubs taught that culture is a technology: a set of tools for managing the problems that arise when different kinds of people try to share a future.",
    ],
    "Frontier Autonomy": [
        "Self-reliance wasn't a philosophy — it was a survival prerequisite, and improvisation was valued over elegance every time the two came into conflict.",
        "The edge systems taught pragmatism at the cellular level: resources were finite, help was distant, and the only real lesson was to solve the problem in front of you.",
        "Growing up on the frontier meant that failure was instructive in ways that success rarely was — the feedback was immediate, specific, and occasionally dangerous.",
    ],
    "Economic Flow Immersion": [
        "Simulated and real trading decisions were made side by side from early adolescence, blurring the line between learning and practice in ways that proved useful later.",
        "The rhythms of interstellar commerce — price fluctuation, route optimization, negotiation cycles — became second nature long before formal training gave them names.",
        "Trade, as {name} absorbed it in childhood, was less about goods and more about information: who had it, who needed it, and what it was worth in the gap between.",
    ],
    "Temporal Awareness": [
        "Memory and anticipation were trained as dynamic, adjustable processes — what had happened and what might happen were both treated as variables, not fixed facts.",
        "Causality was a skill, not an assumption — the community believed that careful attention to causal chains could, with practice, be extended forward and backward in time.",
        "Non-linear planning became natural: holding multiple possible timelines simultaneously, weighting them by probability, adjusting as new information arrived.",
    ],
    "Embodied Craft": [
        "Precision and iteration were cultural values, not instructions — failing a construction wasn't a setback but data, and every rebuild was understood as refinement.",
        "The guild worlds taught that the hand and the mind are the same instrument, and that the quickest path to understanding a system is to take it apart and rebuild it yourself.",
        "Material intuition was the real curriculum: knowing what a substance wanted to do, and either working with that tendency or against it, deliberately.",
    ],
    "default": [
        "The lessons that mattered most were the ones that weren't scheduled — learned in margins, in failures, and in conversations that lasted past curfew.",
        "Not every valuable education has a credential attached to it, and {name}'s early years had more of the former kind than the latter.",
    ],
}


# ---------------------------------------------------------------------------
# PIVOT — one mechanical sentence grounded in the character's dominant stat.
# Keyed by stat abbreviation.
# ---------------------------------------------------------------------------

_PIVOT = {
    "VIT": [
        "What set {name} apart was a physical endurance that refused to distinguish between inconvenience and emergency — both received the same stubborn response.",
        "{name} had a constitutional tolerance for difficult conditions that their instructors noted early and couldn't fully explain: not invulnerability, but a refusal to register damage as a reason to stop.",
    ],
    "KIN": [
        "There was a quality of physical intelligence to {name}'s approach to problems — a preference for doing over deliberating, and a body that consistently delivered on the preference.",
        "Those who trained alongside {name} noted the same thing: a kinetic fluency that made complex physical tasks look like practiced instinct, and a tendency to think best while in motion.",
    ],
    "INT": [
        "Where others saw obstacles, {name} saw systems — a habit of mind that sought the underlying structure of any problem before proposing a solution.",
        "{name} had a reputation, even in youth, for asking the second question: not 'what happened?' but 'what structure produced this outcome, and what would have to change to produce a different one?'",
    ],
    "AEF": [
        "Early on, evaluators noted a sensitivity in {name} that didn't map cleanly to any instrument — an awareness of ambient fields and resonant frequencies most people never noticed at all.",
        "{name} came of age already half-tuned to etheric currents that others required years of training to perceive, a facility that distinguished them from their earliest cohort.",
    ],
    "COH": [
        "Under pressure, {name} became more coherent rather than less — a clarity that colleagues found either reassuring or unsettling, depending on how close they stood to the source of the pressure.",
        "What distinguished {name}'s early record wasn't brilliance but composure: a stable operational baseline that held its shape when everything else became uncertain.",
    ],
    "INF": [
        "Even before formal training, {name} had a facility for social calibration — an instinctive reading of group dynamics and an ability to shift the temperature of a room without appearing to try.",
        "The people around {name} tended to find themselves in agreement without quite knowing when the shift had occurred — a quality that instructors noticed and began shaping almost immediately.",
    ],
    "SYN": [
        "The interface between {name} and any system — biological, mechanical, or digital — was unusually frictionless, a quality that showed up consistently across every domain they touched.",
        "{name} had a rare facility for coordination: the ability to hold multiple interdependent systems in mind simultaneously and optimize across all of them without losing coherence in any.",
    ],
    "default": [
        "Those who trained alongside {name} noted a consistency of approach that suggested not just aptitude but something harder to name — a quality of sustained, deliberate attention.",
    ],
}


# ---------------------------------------------------------------------------
# PROFESSIONAL_ENTRY — career entry framing.  Keyed by profession category.
# ---------------------------------------------------------------------------

_PROFESSION_ENTRY = {
    "Etheric": [
        "After completing assessments that placed them in the upper cohort for etheric sensitivity, {name} qualified as a {profession} and entered a field where the instruments are often less reliable than the practitioner.",
        "{name}'s early evaluations confirmed what childhood had suggested: a measurable affinity for etheric phenomena that led directly into formal training as a {profession}, younger than most.",
    ],
    "Engineering": [
        "Technical certification as a {profession} followed naturally from years of informal practice — {name} entered the field with fewer theoretical gaps and more practical hours than most of their peers.",
        "{name} completed their engineering track and qualified as a {profession} at an age that raised eyebrows at the certification board — not for irregularity, but for the quality of the work.",
    ],
    "Scientific": [
        "{name} was awarded a research designation as a {profession} after assessments that described their approach as 'methodologically unconventional and empirically rigorous' — a combination that opened doors.",
        "A natural aptitude for systematic inquiry led {name} into formal scientific training as a {profession}, where the habit of asking structural questions finally found an institutional home.",
    ],
    "Medical": [
        "Medical qualification as a {profession} came after a training period that {name} later described as 'learning to pay attention at the cellular level' — a discipline that turned out to have broad applications.",
        "{name} entered practice as a {profession} after training that combined formal curriculum with field experience: the kind of preparation that no examination fully measures.",
    ],
    "Diplomatic": [
        "Formal posting as a {profession} was a credential {name} had been working toward deliberately, each prior placement chosen to build fluency in the language of institutional leverage.",
        "{name} was cleared for independent service as a {profession} younger than the median — a function less of exceptional talent than of an unusually complete set of applicable preparation.",
    ],
    "Operations": [
        "Operational certification as a {profession} gave structure to skills {name} had been developing informally for years, providing a framework without fundamentally changing the approach.",
        "{name} qualified as a {profession} through a track that weighted applied experience as heavily as formal examination — a policy that worked strongly in their favor.",
    ],
    "Artistic": [
        "Recognition as a {profession} came when {name}'s work began circulating beyond the cohort that first encountered it — a progression from local reputation to something wider and less controllable.",
        "{name} completed formal designation as a {profession} and immediately began working at a scale that made the designation feel slightly inadequate.",
    ],
    "default": [
        "Formal qualification as a {profession} followed a path that, in retrospect, had been laid since early childhood — each choice pointing toward the same destination from a different angle.",
        "{name} entered their professional track as a {profession} with the kind of preparation that looks inevitable after the fact and feels like improvisation while it's happening.",
    ],
}


# ---------------------------------------------------------------------------
# FORWARD_LOOK — closing hook positioning the character at game start.
# Keyed by faction name; empty string "" for no faction (neutral).
# ---------------------------------------------------------------------------

_FORWARD_LOOK = {
    "": [  # neutral / no faction
        "Now commanding their own vessel, {name} answers to no banner — a freedom that is also, occasionally, a liability.",
        "{name} steps onto the command deck without faction allegiance, which means without guaranteed support and without constraints on what the next chapter becomes.",
    ],
    "The Veritas Covenant": [
        "Aligned with the Veritas Covenant's commitment to unfiltered truth, {name} begins this command with the conviction that the galaxy's deepest problems are problems of incomplete information.",
        "{name} carries a Veritas Covenant charter — not as a restriction, but as a shared orientation toward questions that can only be answered by going further than anyone has gone before.",
    ],
    "Stellar Nexus Guild": [
        "With Stellar Nexus Guild backing, {name} enters independent command with trade routes already plotted and the understanding that commerce, properly applied, is a form of diplomacy.",
        "{name}'s Guild affiliation means the first port of call is never truly unfamiliar — the Stellar Nexus network extends to corners of the galaxy where no other institution has a foothold.",
    ],
    "Harmonic Vitality Consortium": [
        "Backed by the Harmonic Vitality Consortium's philosophy of balance, {name} begins this mission with the conviction that the health of a civilization and the health of an individual are the same problem at different scales.",
        "{name} carries Consortium credentials that open doors across the quadrant's medical and biological communities — a head start that comes with an implicit obligation to the philosophy behind it.",
    ],
    "The Icaron Collective": [
        "Operating under the Icaron Collective's model of integrated intelligence, {name} begins their command with access to distributed processing networks that make most problems soluble given sufficient framing.",
        "{name}'s Collective affiliation offers a form of extended cognition — the ability to query a shared knowledge substrate that has no analog in independent operation.",
    ],
    "The Gaian Enclave": [
        "Chartered by the Gaian Enclave's ecological mandate, {name} begins their mission with a particular attention to planetary systems — and a set of obligations that extend beyond profit or power.",
        "{name} carries a Gaian designation that complicates certain contracts and opens others: not every faction shares the Enclave's view that preserving a biosphere outweighs exploiting it.",
    ],
    "The Gearwrights Guild": [
        "With Guild credentials from the Gearwrights, {name} enters command knowing their ship will be maintained to a standard most commanders can only approximate — and that perfection, in the Guild tradition, is a process rather than a destination.",
        "{name}'s Gearwright affiliation provides a deep network of fabrication and repair contacts across the settled systems, and a professional obligation to the craft that precedes any particular mission.",
    ],
    "The Scholara Nexus": [
        "Affiliated with the Scholara Nexus, {name} begins this command with an implicit brief to learn and to teach — every system encountered a curriculum, every crew member both student and instructor.",
        "{name} carries a Scholara designation that grants unusual access to educational and archival institutions across the quadrant, and an expectation that knowledge encountered will be shared.",
    ],
    "The Harmonic Resonance Collective": [
        "Operating under the Collective's framework of vibrational unity, {name} enters command with perceptual tools that most commanders regard as metaphor — and a growing conviction that the metaphor may be literally accurate.",
        "{name}'s Collective affiliation opens access to resonance research networks that have no parallel in conventional science, and a worldview that treats frequency as a foundational category.",
    ],
    "The Provocateurs' Guild": [
        "With a Guild charter that treats disruption as a methodology rather than a failure mode, {name} begins their command outside the normal categories — a position that is uncomfortable, productive, and occasionally dangerous.",
        "{name} carries Provocateurs' Guild credentials that are treated with wariness by established institutions and considerable interest by everyone else.",
    ],
    "The Quantum Artificers Guild": [
        "Operating under a Quantum Artificers mandate, {name} enters independent command with a research brief that most institutions consider either visionary or irresponsible, depending on their comfort with probability as a working material.",
        "{name}'s Artificers Guild affiliation means access to quantum fabrication resources that have no analog in conventional technology — and experimental obligations that are difficult to explain to cargo inspectors.",
    ],
    "The Stellar Cartographers Alliance": [
        "With a Cartographers Alliance charter, {name} begins this mission with a brief that explicitly prioritizes discovery over destination — every route provisional until something better is found.",
        "{name} carries Alliance credentials that guarantee a welcome in surveying communities across the settled systems, and an obligation to submit any navigation data gathered during independent operation.",
    ],
    "The Galactic Circus": [
        "Operating under a Circus affiliation that baffles and delights in equal measure, {name} enters command with a brief that combines spectacle, logistics, and a genuine commitment to bringing wonder to places that have forgotten what it feels like.",
        "{name}'s Circus designation is the kind of credential that opens unexpected doors — most gatekeepers aren't sure what category it belongs to, and that uncertainty is, by design, exploitable.",
    ],
    "The Technotheos": [
        "Aligned with the Technotheos doctrine that advanced technology is a form of divinity, {name} begins this command with a sense of purpose that exceeds the merely professional and a set of engineering tools that most factions regard with either reverence or apprehension.",
        "{name} carries a Technotheos designation that grants access to sacred engineering archives and transcendence protocols — a foundation for command that is equal parts technical and theological.",
    ],
    "default": [
        "Whatever comes next, {name} faces it with the kind of preparation that only a particular combination of origin, training, and temperament can produce — and a ship that, for now, is entirely their own.",
    ],
}


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def generate_backstory(
    character_data: dict,
    lore_backgrounds: dict,
    lore_professions: dict,
) -> str:
    """
    Generate a single-paragraph origin story for the new commander.

    Args:
        character_data:  Dict with keys name, background, profession, faction, stats.
        lore_backgrounds: The lore/backgrounds.json dict (for fallback profession lookups).
        lore_professions: The PROFESSIONS dict from professions.py (for category lookup).

    Returns:
        A single paragraph string.  Deterministic for the same input values.
    """
    name       = character_data.get("name") or "The Commander"
    background = character_data.get("background") or ""
    profession = character_data.get("profession") or ""
    faction    = character_data.get("faction") or ""
    stats      = character_data.get("stats") or {}

    # Seed the RNG so the same character choices always produce the same story,
    # but different names (or other choices) produce different fragment selections.
    seed_str = name + background + profession + faction
    random.seed(hash(seed_str) & 0xFFFFFFFF)

    # Determine the dominant stat (highest value; defaults to INT if stats absent).
    dominant_stat = max(stats, key=lambda k: stats[k]) if stats else "INT"

    # Resolve profession category for the profession-entry slot.
    prof_info     = lore_professions.get(profession, {})
    prof_category = prof_info.get("category", "")

    # Assemble the five narrative slots.
    opening    = _pick(_OPENING,            background,    name=name, profession=profession)
    formative  = _pick(_FORMATIVE_ENV,      background,    name=name, profession=profession)
    pivot      = _pick(_PIVOT,              dominant_stat, name=name, profession=profession)
    prof_entry = _pick(_PROFESSION_ENTRY,   prof_category, name=name, profession=profession)
    hook       = _pick(_FORWARD_LOOK,       faction,       name=name, profession=profession)

    # Join the five fragments into a single paragraph.
    return " ".join(filter(None, [opening, formative, pivot, prof_entry, hook]))
