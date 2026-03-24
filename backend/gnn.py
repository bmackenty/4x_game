"""
backend/gnn.py — Galactic News Network (GNN) end-of-turn broadcast generator.

Produces a comedic, Alpha-Centauri-flavoured news summary at the end of each
turn, incorporating:
  * Game events returned by game.advance_turn()
  * Colony production / income figures from colony_manager.advance_turn()
  * Faction and research flavour
  * A structured income / expense ledger

All generation is pure-Python with no external dependencies.
The output is a dict returned inside the /api/game/turn/end response as
``gnn_summary``.
"""

import random
from datetime import datetime


# ---------------------------------------------------------------------------
# Headline templates
# ---------------------------------------------------------------------------

_HEADLINES = [
    "MARKETS IN CHAOS; ECONOMISTS BLAME EVERYTHING EXCEPT ECONOMISTS",
    "LOCAL FACTION DISPUTES BORDER: 'THAT HEX WAS ALWAYS OURS,' SAYS NOBODY CREDIBLE",
    "RESEARCH TEAM DISCOVERS SOMETHING; REFUSES TO EXPLAIN WHAT",
    "COLONY REPORTS RECORD HARVEST; COLONISTS COMPLAIN IT'S STILL NOT ENOUGH",
    "TRADE ROUTE DECLARED 'DEFINITELY NOT HAUNTED' AFTER THIRD INCIDENT",
    "GALACTIC SENATE PASSES RESOLUTION; NOBODY REMEMBERS WHAT IT SAID",
    "NPC SPOTTED DOING SOMETHING; WITNESSES DESCRIBE IT AS 'SUSPICIOUSLY PURPOSEFUL'",
    "MINERAL PRICES SURGE ON NEWS THAT MINERALS EXIST",
    "FACTION DIPLOMAT CALLS RIVAL 'UNDIPLOMATIC'; IRONY LOST ON ALL PARTIES",
    "SCIENTISTS WARN OF ETHER LEAK; IMMEDIATELY START ARGUING ABOUT METHODOLOGY",
    "DEEP SPACE ANOMALY DETECTED; PROBE SENT, PROBE LOST, NEW PROBE ORDERED",
    "POPULATION BOOM IN OUTER COLONIES; INFRASTRUCTURE BOOM NOTABLY ABSENT",
    "PIRATES DENY BEING PIRATES; FILE PAPERWORK AS 'AGGRESSIVE ENTREPRENEURS'",
    "STOCK EXCHANGE CRASHES AFTER TRADER SAYS 'I HAVE A GOOD FEELING ABOUT THIS'",
    "QUANTUM RELAY OUTAGE BLAMED ON 'TEMPORAL INTERFERENCE' AND ALSO BUDGET CUTS",
    "COLONY ADMINISTRATOR RESIGNS; CITES 'CREATIVE DIFFERENCES WITH REALITY'",
    "NEW SHIP CLASS UNVEILED; DESIGNER INSISTS COCKPIT IS 'INTENTIONALLY CRAMPED'",
    "FACTION SUMMIT ENDS EARLY AFTER SOMEONE ORDERS THE WRONG CATERING",
    "ETHER CONDUIT EXPLOSION BLAMED ON 'USER ERROR'; USER UNAVAILABLE FOR COMMENT",
    "GALACTIC CENSUS COMPLETE: MORE PEOPLE THAN LAST TIME, FEWER THAN EXPECTED",
]

_WEATHER = [
    "Stellar winds calm. Perfect day for ill-advised decisions.",
    "High radiation alert in sectors 7 through 12. As usual.",
    "Cosmic microwave background: still there, still mildly annoying.",
    "Void storm approaching from the galactic rim. Estimated arrival: whenever it feels like it.",
    "Clear skies over the core worlds. Suspicious.",
    "Solar flare activity elevated. Blame anything on it freely.",
    "Ether density: nominal. Nothing to see here. Probably.",
]

_MARKET_TIDBITS = [
    "Analysts predict the market will go up, down, or sideways.",
    "Commodities trader arrested for 'aggressive optimism.'",
    "The credit reaches a new high; economists celebrate; everyone else checks their bills.",
    "Fuel prices remain 'criminally stupid,' says no official report.",
    "Trade guilds announce merger; combined bureaucracy achieves sentience.",
    "Supply chains described as 'functioning' in the loosest sense of the word.",
    "Demand for minerals at all-time high; supply mysteriously in a cave.",
]

# ---------------------------------------------------------------------------
# Economy event narrative templates
# Keys match the 'name' field in economy.py's create_economic_event().
# Each list entry is a GNN-style sentence.  {commodities} is replaced by the
# affected goods names.  A fallback generic template handles unknown events.
# ---------------------------------------------------------------------------

_ECON_EVENT_TEMPLATES = {
    "Mining Boom": [
        "BREAKING MARKETS: Rich ore deposits discovered across multiple systems. "
        "{commodities} flooding the exchange — traders are loading up.",
        "ECONOMY DESK: A mining boom is underway. {commodities} prices have collapsed "
        "as supply surges. Industrial worlds are celebrating; investors are not.",
    ],
    "Crop Failure": [
        "BREAKING MARKETS: Agricultural blight has devastated harvests across the "
        "sector. {commodities} prices spiking hard — anyone with food cargo is "
        "sitting on a fortune.",
        "ECONOMY DESK: Crop failures reported on three systems. {commodities} "
        "shortfalls are severe. Humanitarian fleets en route; price gougers reportedly "
        "en route faster.",
    ],
    "Trade War": [
        "BREAKING MARKETS: Political tensions between factions have disrupted trade "
        "lanes. Prices across all commodities up — {commodities} hit hardest. "
        "Diplomats are talking; traders are not waiting.",
        "ECONOMY DESK: A trade war has broken out. Commerce is complicated, prices "
        "are elevated, and everyone is calling it someone else's fault. "
        "Affected: {commodities}.",
    ],
    "Technology Breakthrough": [
        "BREAKING MARKETS: New manufacturing techniques are revolutionising production "
        "of {commodities}. Expect prices to fall as supply expands. "
        "Early buyers will feel this one.",
        "ECONOMY DESK: A technology breakthrough has been announced. {commodities} "
        "supply is surging as factories retool. Analysts advise selling before the "
        "market realises what's happening.",
    ],
    "Pirate Raids": [
        "BREAKING MARKETS: Pirate activity along core trade lanes has disrupted "
        "luxury shipments. {commodities} supplies cut — prices elevated. "
        "The pirates, predictably, are unavailable for comment.",
        "ECONOMY DESK: Pirate raids have targeted convoys carrying {commodities}. "
        "Supply is down, prices are up, and insurance rates are becoming "
        "philosophically interesting.",
    ],
}

_ECON_EVENT_FALLBACK = (
    "ECONOMY DESK: An economic event ({name}) has rippled through the markets. "
    "Traders are advised to check prices before assuming anything."
)

_FACTION_SNIPPETS = {
    "The Veritas Covenant": [
        "Veritas Covenant releases 40-volume research compendium; nobody has time to read it.",
        "Covenant scholars debate whether knowledge is power or just a coping mechanism.",
        "New Covenant policy: all secrets must be filed in triplicate.",
    ],
    "Stellar Nexus Guild": [
        "Nexus Guild announces 'record profits'; refuses to show the records.",
        "Guild trade envoy describes rival system as 'economically sub-optimal.'",
        "Nexus trading post opens in seventeen new systems; still no seating.",
    ],
    "Ironclad Collective": [
        "Ironclad fleet conducts 'routine exercises' near contested border. Very routine.",
        "Collective military budget classified; so is the budget for classifying it.",
        "New Ironclad warship named after something suitably ominous.",
    ],
    "Scholara Nexus": [
        "Scholara lab produces breakthrough; entire team immediately argues about credit.",
        "Research grant applications outnumber actual researchers seven to one.",
        "Nexus academic paper rejected for 'excessive use of the word quantum.'",
    ],
    "Harmonic Vitality Consortium": [
        "Consortium announces new agricultural initiative; plants remain unaware.",
        "HVC wellness report: galaxy is stressed but hydrated.",
        "Organic food standards updated; definition of 'organic' now seventeen pages long.",
    ],
    "Gearwrights Guild": [
        "Gearwrights Guild releases new drill model; previous model still technically 'supported.'",
        "Mining output up 12%. Mining workers' pay up 0%. Coincidence suspected.",
        "New automated ore processor malfunctions; replaced by slightly different automated ore processor.",
    ],
    "Keepers of the Spire": [
        "Ancient relic discovered; immediately argued over by three factions.",
        "Keepers refuse to reveal what the Spire does. Again.",
        "Archaeological team uncovers evidence that someone was here before. Disturbing.",
    ],
}

_COLONY_NEWS = [
    "Colony on {planet} reports {pop:,} residents and zero complaints, which is itself suspicious.",
    "Infrastructure investment in {planet} described as 'ambitious' by officials, 'adequate' by nobody.",
    "Population of {planet} grows; available housing does not. Classic.",
    "{planet} colonists petition for better coffee. Petition denied. Morale declines predictably.",
    "New trade nexus on {planet} expected to boost income; boosts paperwork first.",
    "{planet} colony administrator declares situation 'under control.' Situation files complaint.",
]

_RESEARCH_SNIPPETS = [
    "Research progress continues at the speed of 'we're working on it.'",
    "Scientists confirm: the more you research, the more there is to research.",
    "Lab intern accidentally solves minor mystery. Credit given to lab director.",
    "Research funding request approved; actual research funding: pending.",
    "Breakthrough imminent according to researcher who has been saying that for six turns.",
]

_CLOSING_REMARKS = [
    "This has been the Galactic News Network. Stay informed. Stay suspicious.",
    "GNN: All the news that's fit to broadcast and several items that arguably aren't.",
    "Remember: the galaxy is vast, indifferent, and somehow still generating paperwork.",
    "GNN signing off. May your jump drives be reliable and your diplomats be caffeinated.",
    "That's the news. We apologise for any accuracy that may have inadvertently occurred.",
    "GNN: Brought to you by the Stellar Nexus Guild. (We did not ask for this.)",
    "Stay safe out there. Or don't. The galaxy has insurance for that.",
]


# ---------------------------------------------------------------------------
# Income / expense formatter
# ---------------------------------------------------------------------------

def _build_ledger(financial_summary: dict, game_credits_before: int,
                  game_credits_after: int) -> dict:
    """
    Build a structured income/expense ledger for display in the GNN modal.

    financial_summary comes from colony_manager.advance_turn() return value.
    """
    colony_credits  = financial_summary.get("colony_credits", 0)
    pop_income      = financial_summary.get("population_income", 0)
    research_pts    = financial_summary.get("research_pts", 0)
    colonies        = financial_summary.get("colonies", [])

    total_income = colony_credits + pop_income
    net_change   = game_credits_after - game_credits_before

    income_lines = []
    if pop_income:
        income_lines.append({"label": "Population tax", "value": pop_income})
    if colony_credits:
        income_lines.append({"label": "Colony building output", "value": colony_credits})

    # Per-colony breakdown
    colony_lines = [
        {"name": c["name"], "income": c["income"], "pop": c["pop"]}
        for c in colonies
    ]

    return {
        "income_lines":   income_lines,
        "colony_lines":   colony_lines,
        "total_income":   total_income,
        "research_pts":   research_pts,
        "net_change":     net_change,
        "credits_after":  game_credits_after,
    }


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_gnn_summary(game, colony_manager, events: list,
                         financial_summary: dict,
                         credits_before: int, credits_after: int) -> dict:
    """
    Generate the full GNN end-of-turn broadcast.

    Parameters
    ----------
    game              : Game instance
    colony_manager    : ColonyManager instance
    events            : list of {"channel": str, "message": str} from advance_turn
    financial_summary : dict returned by colony_manager.advance_turn()
    credits_before    : player credits before this turn's income was applied
    credits_after     : player credits after all income applied

    Returns a dict suitable for JSON serialisation:
    {
        "turn":        int,
        "headline":    str,
        "news_items":  [ str, ... ],
        "weather":     str,
        "ledger":      { ... },
        "closing":     str,
    }
    """
    rng = random.Random()   # unseeded — different every call

    turn = game.current_turn
    news_items = []

    # ── Headline ─────────────────────────────────────────────────────────────
    headline = rng.choice(_HEADLINES)

    # ── Weather ──────────────────────────────────────────────────────────────
    weather = rng.choice(_WEATHER)

    # ── Events from the turn ─────────────────────────────────────────────────
    for evt in events:
        channel = evt.get("channel", "")
        msg     = evt.get("message", "")
        if not msg:
            continue
        if channel == "ECON":
            news_items.append(f"ECONOMY DESK: {msg}")
        elif channel == "RESEARCH":
            news_items.append(f"SCIENCE DESK: {msg}")
        elif channel == "FACTION":
            news_items.append(f"DIPLOMATIC DESK: {msg}")
        elif channel == "EVENT":
            news_items.append(f"BREAKING: {msg}")
        else:
            news_items.append(msg)

    # ── Colony colour ────────────────────────────────────────────────────────
    colonies = financial_summary.get("colonies", [])
    for col in rng.sample(colonies, min(2, len(colonies))):
        template = rng.choice(_COLONY_NEWS)
        news_items.append(
            "COLONIAL AFFAIRS: " + template.format(
                planet=col["name"], pop=col["pop"]
            )
        )

    # ── Faction snippet ──────────────────────────────────────────────────────
    galaxy = game.navigation.galaxy
    factions_present = set()
    for sys_data in galaxy.systems.values():
        f = sys_data.get("controlling_faction")
        if f:
            factions_present.add(f)

    for faction in rng.sample(sorted(factions_present), min(2, len(factions_present))):
        snippets = _FACTION_SNIPPETS.get(faction)
        if snippets:
            news_items.append(f"FACTION WATCH: {rng.choice(snippets)}")

    # ── Research colour ──────────────────────────────────────────────────────
    if game.active_research:
        news_items.append(
            f"SCIENCE DESK: Research continues on '{game.active_research}'. "
            + rng.choice(_RESEARCH_SNIPPETS)
        )
    else:
        news_items.append("SCIENCE DESK: " + rng.choice(_RESEARCH_SNIPPETS))

    # ── Market tidbit ────────────────────────────────────────────────────────
    news_items.append("MARKETS: " + rng.choice(_MARKET_TIDBITS))

    # ── Economy events from the engine ───────────────────────────────────────
    # economy.global_events stores the last 5 macro events triggered by
    # tick_global_state (Mining Boom, Crop Failure, Trade War, etc.).
    # We surface the most recent one with a tailored narrative template so the
    # GNN feels connected to what is actually happening in the economy.
    try:
        economy = getattr(game, "economy", None)
        recent_econ_events = list(getattr(economy, "global_events", [])) if economy else []
        if recent_econ_events:
            evt       = recent_econ_events[-1]  # most recent event
            evt_name  = evt.get("name", "Unknown")
            effects   = evt.get("effects", {})
            raw_comms = effects.get("commodities", [])
            # Resolve the commodity list (may be a list, the string "all", or "luxury")
            if isinstance(raw_comms, list):
                comm_str = ", ".join(raw_comms[:3]) if raw_comms else "various commodities"
            elif raw_comms == "all":
                comm_str = "all major commodities"
            else:
                comm_str = str(raw_comms)

            templates = _ECON_EVENT_TEMPLATES.get(evt_name)
            if templates:
                snippet = rng.choice(templates).format(commodities=comm_str)
            else:
                snippet = _ECON_EVENT_FALLBACK.format(name=evt_name)
            news_items.append(snippet)
    except Exception:
        pass  # economy event flavour is cosmetic; never crash GNN

    # Shuffle so the order feels organic
    rng.shuffle(news_items)

    # ── Ledger ───────────────────────────────────────────────────────────────
    ledger = _build_ledger(financial_summary, credits_before, credits_after)

    # ── Closing ──────────────────────────────────────────────────────────────
    closing = rng.choice(_CLOSING_REMARKS)

    return {
        "turn":       turn,
        "headline":   headline,
        "news_items": news_items,
        "weather":    weather,
        "ledger":     ledger,
        "closing":    closing,
    }
