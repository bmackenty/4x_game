"""
professions.py — Unified profession system for Chronicles of the Ether (Year 7019).

All profession data is stored in lore/professions.json.
This module loads that file and exposes the same public API as before,
so all existing callers (game.py, backend/main.py, etc.) are unaffected.

All professions share a common schema:
  category              : str        — one of the CATEGORY_* constants below
  description           : str        — lore-rich career description
  skills                : list[str]  — five defining professional skills
  base_benefits         : list[str]  — what the profession provides at levels 1–2
  intermediate_benefits : list[str]  — benefits unlocked at levels 3–5
  advanced_benefits     : list[str]  — benefits unlocked at levels 6–8
  master_benefits       : list[str]  — benefits unlocked at levels 9–10

ProfessionSystem class wraps PROFESSIONS and tracks per-character XP and level.
"""

import json
import pathlib
import random

# ── Category constants ─────────────────────────────────────────────────────────
CATEGORY_ETHERIC     = "Etheric"       # consciousness, ether, mystical tech
CATEGORY_ENGINEERING = "Engineering"   # hardware, systems, construction
CATEGORY_SCIENTIFIC  = "Scientific"    # research, analysis, exploration
CATEGORY_DIPLOMATIC  = "Diplomatic"    # relations, negotiation, culture, education
CATEGORY_OPERATIONS  = "Operations"    # logistics, security, management
CATEGORY_MEDICAL     = "Medical"       # healing, biology, enhancement
CATEGORY_ARTISTIC    = "Artistic"      # creative expression, culture, ritual

# ── Load raw data from lore/professions.json ───────────────────────────────────
_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "professions.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    _data = json.load(_f)

# ── Public data ────────────────────────────────────────────────────────────────

PROFESSIONS: dict = _data["professions"]

# All valid category labels in display order
PROFESSION_CATEGORIES_ORDERED: list = _data["categories_ordered"]

# Pre-built lookup: category name → sorted list of profession names
PROFESSIONS_BY_CATEGORY: dict[str, list[str]] = {}
for _name, _entry in PROFESSIONS.items():
    _cat = _entry["category"]
    PROFESSIONS_BY_CATEGORY.setdefault(_cat, []).append(_name)
for _cat in PROFESSIONS_BY_CATEGORY:
    PROFESSIONS_BY_CATEGORY[_cat].sort()

# Legacy aliases used by older callers in game.py
professions = PROFESSIONS
profession_categories = PROFESSIONS_BY_CATEGORY


# ── ProfessionSystem class ─────────────────────────────────────────────────────

class ProfessionSystem:
    """
    Tracks a single character's profession choice, XP, and mastery level.

    Levels 1–10 unlock progressively more powerful benefits:
      Levels 1–2  → base_benefits
      Levels 3–5  → + intermediate_benefits
      Levels 6–8  → + advanced_benefits
      Levels 9–10 → + master_benefits

    XP thresholds: 100 XP per level (level = XP // 100 + 1, capped at 10).
    """

    def __init__(self):
        # The character's chosen primary profession
        self.character_profession: str | None = None
        # XP accumulated per profession name
        self.profession_experience: dict[str, int] = {}
        # Current level per profession name
        self.profession_levels: dict[str, int] = {}

    # ── Assignment ────────────────────────────────────────────────────────────

    def assign_profession(self, profession_name: str) -> bool:
        """Assign a profession to the character. Returns True if valid."""
        if profession_name not in PROFESSIONS:
            return False
        self.character_profession = profession_name
        self.profession_experience.setdefault(profession_name, 0)
        self.profession_levels.setdefault(profession_name, 1)
        return True

    # ── XP and levelling ──────────────────────────────────────────────────────

    def gain_experience(self, profession_name: str, xp: int, activity: str = "") -> str:
        """
        Add XP to a profession, auto-levelling if the threshold is crossed.
        Returns a human-readable status string.
        """
        if profession_name not in PROFESSIONS:
            return f"Unknown profession: {profession_name}"

        self.profession_experience.setdefault(profession_name, 0)
        self.profession_levels.setdefault(profession_name, 1)

        old_level = self.profession_levels[profession_name]
        self.profession_experience[profession_name] += xp
        new_level = min(10, self.profession_experience[profession_name] // 100 + 1)

        if new_level > old_level:
            self.profession_levels[profession_name] = new_level
            return f"Level up! {profession_name}: Level {old_level} → {new_level}"

        label = f" ({activity})" if activity else ""
        return f"Gained {xp} XP in {profession_name}{label}"

    # ── Info retrieval ────────────────────────────────────────────────────────

    def get_profession_info(self, profession_name: str) -> dict | None:
        """Return full profession data merged with this character's progress."""
        if profession_name not in PROFESSIONS:
            return None
        info = PROFESSIONS[profession_name].copy()
        info["player_experience"] = self.profession_experience.get(profession_name, 0)
        info["player_level"]      = self.profession_levels.get(profession_name, 0)
        info["is_player_profession"] = (profession_name == self.character_profession)
        return info

    def get_profession_bonuses(self, profession_name: str) -> list[str]:
        """Return all benefits currently unlocked for this profession at its current level."""
        level = self.profession_levels.get(profession_name, 0)
        if level == 0:
            return []
        data = PROFESSIONS.get(profession_name, {})
        bonuses: list[str] = list(data.get("base_benefits", []))
        if level >= 3:
            bonuses += data.get("intermediate_benefits", [])
        if level >= 6:
            bonuses += data.get("advanced_benefits", [])
        if level >= 9:
            bonuses += data.get("master_benefits", [])
        return bonuses

    # ── Job opportunities ─────────────────────────────────────────────────────

    def generate_job_opportunities(self, system_type: str | None = None) -> list[dict]:
        """
        Generate a short list of available job opportunities for the current system.
        Returns a list of job dicts; also caches them on self.available_jobs.
        """
        # Base pay by category
        pay_ranges = {
            CATEGORY_ENGINEERING: (4000, 12000),
            CATEGORY_SCIENTIFIC:  (5000, 15000),
            CATEGORY_ETHERIC:     (4000, 16000),
            CATEGORY_MEDICAL:     (6000, 18000),
            CATEGORY_DIPLOMATIC:  (5000, 14000),
            CATEGORY_OPERATIONS:  (3000, 10000),
            CATEGORY_ARTISTIC:    (2000,  8000),
        }

        # System-type affinity groups (profession names must exist in PROFESSIONS)
        system_affinity: dict[str, list[str]] = {
            "Research":    ["Astrobiologist", "Xenoanthropologist", "Etheric Historian",
                            "Consciousness Engineer", "Quantum Navigator"],
            "Industrial":  ["Nano-Fabrication Artisan", "Bio-Integrated Manufacturing Director",
                            "Atmospheric Harvest Technician", "Gravitic Systems Engineer"],
            "Trading Hub": ["Exotic Commodities Broker", "Trade Route Adjudicator",
                            "Universal Translation Mediator", "Interstellar Quartermaster"],
            "Core World":  ["Interstellar Diplomatic Attaché", "Sentient Systems Ethicist",
                            "Etheric Legal Advocate", "Etheric Historian"],
            "Frontier":    ["Deep Space Reconnaissance Operative", "Salvage Systems Diver",
                            "Resource Vein Prospector", "Void Cartographer"],
        }

        candidates: list[str] = []
        if system_type and system_type in system_affinity:
            candidates = [p for p in system_affinity[system_type] if p in PROFESSIONS]

        # Pad with random professions so we always have at least 5 options
        all_names = list(PROFESSIONS.keys())
        while len(candidates) < 5:
            pick = random.choice(all_names)
            if pick not in candidates:
                candidates.append(pick)

        jobs = []
        for name in candidates[:5]:
            data = PROFESSIONS[name]
            cat  = data.get("category", CATEGORY_SCIENTIFIC)
            low, high = pay_ranges.get(cat, (3000, 10000))
            jobs.append({
                "profession":        name,
                "title":             f"{name} Position",
                "description":       data["description"],
                "pay":               random.randint(low, high),
                "experience_reward": random.randint(10, 50),
                "duration":          random.randint(1, 5),
                "skills_required":   data.get("skills", [])[:2],
                "category":          cat,
                "context":           system_type or "General",
            })

        self.available_jobs = jobs
        return jobs
