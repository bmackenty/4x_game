equipment = {
    "Void_Comms_Mesh": {
        "slot": "utility",
        "category": "communications",
        "factions": ["Stellar Nexus Guild", "Stellar Cartographers Alliance"],
        "classes": ["Data Weaver", "Quantum Ranger", "Star Skald"],
        "backgrounds": ["Deep-Space Navigator", "Outer Rim Courier", "Signal Diver"],
        "rarity": "uncommon",
        "lore": "A self-configuring micro-drone mesh that maintains encrypted comms across shifting grav-wells and ether storms.",
        "mechanics": {
            "network_range_km": 500000,
            "signal_penetration": 85,
            "jamming_resistance": 70,
            "slots_used": 1
        }
    },
    "Etheric_Harmonics_Band": {
        "slot": "wrist",
        "category": "support",
        "factions": ["Harmonic Resonance Collective", "Harmonic Vitality Consortium"],
        "classes": ["Etheric Adept", "Bio-Arcanist", "Star Skald"],
        "backgrounds": ["Choir of Resonance", "Temple Resonant", "Frontier Mediarch"],
        "rarity": "rare",
        "lore": "A band of phase-linked crystals that tunes the wearer’s biofield to stabilise nearby allies.",
        "mechanics": {
            "ally_stability_bonus": 12,
            "etheric_control_bonus": 8,
            "area_radius_m": 25,
            "slots_used": 1
        }
    },
    "Grav_Anchor_Greaves": {
        "slot": "legs",
        "category": "mobility",
        "factions": ["Ironclad Collective", "Gaian Enclave"],
        "classes": ["Grav-Commando", "Mechwright", "Void Corsair"],
        "backgrounds": ["Siege Veteran", "Orbital Dockworker", "Asteroid Miner"],
        "rarity": "uncommon",
        "lore": "Boots lined with localized gravity wells, allowing stable footing on hulls, rubble, or rotating habitats.",
        "mechanics": {
            "fall_resistance": 80,
            "recoil_stability": 15,
            "movement_penalty": -5,
            "slots_used": 2
        }
    },
    "Phase_Coil_Carapace": {
        "slot": "armor",
        "category": "defense",
        "factions": ["Technomancers", "Quantum Artificers Guild"],
        "classes": ["Etheric Adept", "Chrononaut", "Cipher Operative"],
        "backgrounds": ["Research Diver", "Quantum Academy Graduate", "Temporal Exile"],
        "rarity": "epic",
        "lore": "An exoshell woven from phase-coils that briefly slip the wearer half a heartbeat out of local spacetime.",
        "mechanics": {
            "damage_reduction": 30,
            "phase_dodge_chance": 18,
            "chrono_instability": 7,
            "slots_used": 4
        }
    },
    "Mnemonic_Shunt_Rig": {
        "slot": "head",
        "category": "cerebral",
        "factions": ["Veritas Covenant", "Scholara Nexus"],
        "classes": ["Data Weaver", "Star Skald", "Bio-Arcanist"],
        "backgrounds": ["Archivist of Lost Wars", "University Savant", "Truth-Seeker"],
        "rarity": "rare",
        "lore": "A cranial harness that offloads short-term memory into a local quantum buffer for rapid recall.",
        "mechanics": {
            "analysis_speed_bonus": 15,
            "memory_slots_virtual": 6,
            "corruption_risk": 5,
            "slots_used": 1
        }
    },
    "Abyssal_Thrower_Array": {
        "slot": "weapon_main",
        "category": "ranged",
        "factions": ["Voidbound Monks", "Icaron Collective"],
        "classes": ["Void Corsair", "Quantum Ranger", "Grav-Commando"],
        "backgrounds": ["Derelict Scavenger", "Station Enforcer", "Counter-Pirate Marine"],
        "rarity": "rare",
        "lore": "A shoulder-mounted projector that hurls compressed void-pockets which rupture into hungry darkness.",
        "mechanics": {
            "damage": 65,
            "range_m": 900,
            "void_scatter": 12,
            "ethic_risk_index": 20,
            "slots_used": 3
        }
    },
    "Bioforge_Field_Kit": {
        "slot": "pack",
        "category": "medical",
        "factions": ["Harmonic Vitality Consortium", "Gaian Enclave"],
        "classes": ["Bio-Arcanist", "Etheric Adept", "Grav-Commando"],
        "backgrounds": ["Frontier Medic", "Gene-Craft Apprentice", "Plague Zone Survivor"],
        "rarity": "uncommon",
        "lore": "A portable bioforge capable of printing temporary organs, dermal patches, and stabilizing symbiotes.",
        "mechanics": {
            "healing_per_cycle": 25,
            "cycles_per_mission": 5,
            "infection_mitigation": 30,
            "slots_used": 2
        }
    },
    "Chrono_Slipband": {
        "slot": "wrist",
        "category": "chrono",
        "factions": ["Technomancers", "Quantum Artificers Guild"],
        "classes": ["Chrononaut", "Etheric Adept", "Cipher Operative"],
        "backgrounds": ["Temporal Exile", "Black-Box Investigator", "Timefront Courier"],
        "rarity": "legendary",
        "lore": "A ring of syncopated chronocrystals that grants micro-skips in time at the cost of long-term coherence.",
        "mechanics": {
            "initiative_bonus": 20,
            "chrono_adaptability": 25,
            "temporal_stress_gain": 10,
            "slots_used": 1
        }
    },
    "Riot_of_Stars_Cloak": {
        "slot": "back",
        "category": "stealth",
        "factions": ["Galactic Circus", "Provocateurs' Guild"],
        "classes": ["Void Corsair", "Star Skald", "Cipher Operative"],
        "backgrounds": ["Street Performer", "Political Agitator", "Smuggler Prince"],
        "rarity": "epic",
        "lore": "A cloak that diffracts light into fractal starfields, masking the wearer in spectacle and misdirection.",
        "mechanics": {
            "visual_stealth": 30,
            "social_distraction": 18,
            "sensor_ghosting": 12,
            "slots_used": 1
        }
    },
    "Grav_Nail_Cluster": {
        "slot": "throwable",
        "category": "tactical",
        "factions": ["Ironclad Collective", "Gearwrights Guild"],
        "classes": ["Grav-Commando", "Mechwright", "Quantum Ranger"],
        "backgrounds": ["Siege Veteran", "Shipwright Scion", "Urban Breacher"],
        "rarity": "common",
        "lore": "Micro-spikes that burrow into structures and briefly spike local gravity, pinning targets in place.",
        "mechanics": {
            "immobilize_chance": 40,
            "radius_m": 4,
            "structure_stress": 20,
            "slots_used": 1
        }
    },
    "Etheric_Scribe_Gauntlet": {
        "slot": "hand",
        "category": "interface",
        "factions": ["Veritas Covenant", "Scholara Nexus"],
        "classes": ["Data Weaver", "Etheric Adept", "Star Skald"],
        "backgrounds": ["Court Scribe", "Treaty Cartographer", "Relic Translator"],
        "rarity": "uncommon",
        "lore": "A gauntlet that records etheric imprints as visible glyphs, making unseen flows legible and editable.",
        "mechanics": {
            "etheric_visualization": 90,
            "field_editing_precision": 10,
            "data_storage_slots": 12,
            "slots_used": 1
        }
    },
    "Singularity_Wedge_Charge": {
        "slot": "explosive",
        "category": "breach",
        "factions": ["Ironclad Collective", "Voidbound Monks"],
        "classes": ["Grav-Commando", "Void Corsair", "Mechwright"],
        "backgrounds": ["Siege Veteran", "Derelict Scavenger", "Salvage Engineer"],
        "rarity": "rare",
        "lore": "A shaped charge that creates a momentary micro-singularity, cutting clean corridors through bulkheads.",
        "mechanics": {
            "hull_breach_power": 95,
            "collateral_risk": 25,
            "uses_per_mission": 2,
            "slots_used": 2
        }
    },
    "Polymorph_Tool_Spine": {
        "slot": "belt",
        "category": "engineering",
        "factions": ["Gearwrights Guild", "Scholara Nexus"],
        "classes": ["Mechwright", "Data Weaver", "Bio-Arcanist"],
        "backgrounds": ["Station Mechanic", "Ruins Tinkerer", "Colony Founder"],
        "rarity": "uncommon",
        "lore": "A segmented spine of nano-tools that can become almost any mundane tool or fine manipulator.",
        "mechanics": {
            "fabrication_speed_bonus": 20,
            "repair_efficiency": 15,
            "precision_rating": 18,
            "slots_used": 1
        }
    },
    "Neurolattice_Overcloak": {
        "slot": "back",
        "category": "defense",
        "factions": ["Technotheos", "Technomancers"],
        "classes": ["Etheric Adept", "Chrononaut", "Cipher Operative"],
        "backgrounds": ["Cult of Circuits", "Machine Pilgrim", "AI Negotiator"],
        "rarity": "epic",
        "lore": "An overcloak threaded with neurolattice fibers that negotiates incoming attacks with machine spirits.",
        "mechanics": {
            "ai_convergence": 22,
            "projectile_deflection": 18,
            "cyber_resilience": 25,
            "slots_used": 2
        }
    },
    "Psychoacoustic_Shard_Kit": {
        "slot": "utility",
        "category": "social/field",
        "factions": ["Galactic Circus", "Harmonic Resonance Collective"],
        "classes": ["Star Skald", "Cipher Operative", "Void Corsair"],
        "backgrounds": ["Street Performer", "Propaganda Architect", "Subculture Producer"],
        "rarity": "rare",
        "lore": "A set of floating shards that emit carefully sculpted sounds to manipulate moods and crowd behavior.",
        "mechanics": {
            "crowd_control_bonus": 20,
            "fear_induction": 10,
            "calm_aura": 10,
            "slots_used": 1
        }
    },
    "Gaian_Symbiote_Weave": {
        "slot": "armor",
        "category": "bio-armor",
        "factions": ["Gaian Enclave", "Harmonic Vitality Consortium"],
        "classes": ["Bio-Arcanist", "Grav-Commando", "Etheric Adept"],
        "backgrounds": ["Forest World Ranger", "Bio-Refugee", "Terraformer"],
        "rarity": "rare",
        "lore": "A living weave that fuses to the wearer, hardening on impact and self-healing between engagements.",
        "mechanics": {
            "armor_rating": 25,
            "self_heal_rate": 5,
            "toxicity_resistance": 20,
            "slots_used": 3
        }
    },
    "Echo_of_Lost_Maps": {
        "slot": "head",
        "category": "navigation",
        "factions": ["Stellar Cartographers Alliance", "Scholara Nexus"],
        "classes": ["Quantum Ranger", "Star Skald", "Data Weaver"],
        "backgrounds": ["Deep-Space Navigator", "Astrometric Clerk", "Expedition Scholar"],
        "rarity": "epic",
        "lore": "A cranial halo that overlays phantom star-charts from lost eras onto present-day navigation.",
        "mechanics": {
            "navigation_precision": 25,
            "jump_risk_reduction": 15,
            "archaic_route_access": 3,
            "slots_used": 1
        }
    },
    "Liminal_Threshold_Beacon": {
        "slot": "deployable",
        "category": "tactical",
        "factions": ["Voidbound Monks", "Etheric Preservationists"],
        "classes": ["Chrononaut", "Etheric Adept", "Quantum Ranger"],
        "backgrounds": ["Wreck Diver", "Rift Scout", "Boundary Guard"],
        "rarity": "rare",
        "lore": "A beacon that stabilizes or destabilizes local dimensional seams, marking safe or forbidden thresholds.",
        "mechanics": {
            "rift_stability_control": 30,
            "danger_sense_bonus": 15,
            "deployment_time_s": 6,
            "slots_used": 2
        }
    },
    "Shard_of_Common_Cause": {
        "slot": "trinket",
        "category": "social",
        "factions": ["Collective of Commonality", "Veritas Covenant"],
        "classes": ["Star Skald", "Data Weaver", "Bio-Arcanist"],
        "backgrounds": ["Union Organizer", "Border Mediator", "Community Anchor"],
        "rarity": "uncommon",
        "lore": "A multifaceted shard that amplifies shared intentions, making collaboration feel physically easier.",
        "mechanics": {
            "teamwork_bonus": 20,
            "morale_resilience": 15,
            "conflict_diffusion": 10,
            "slots_used": 1
        }
    },
    "Ghostwalk_Induction_Hood": {
        "slot": "head",
        "category": "stealth",
        "factions": ["Provocateurs' Guild", "Technomancers"],
        "classes": ["Cipher Operative", "Void Corsair", "Chrononaut"],
        "backgrounds": ["Black-Box Investigator", "Insurgency Liaison", "Counter-Intel Defector"],
        "rarity": "epic",
        "lore": "A neural hood that induces predictable blind spots in both humans and common sensor suites.",
        "mechanics": {
            "sensor_stealth": 28,
            "memory_smudge_strength": 15,
            "traceability_penalty": -10,
            "slots_used": 1
        }
    },
    "Relic_Anchor_Talisman": {
        "slot": "neck",
        "category": "protection",
        "factions": ["Keepers of the Spire", "Etheric Preservationists"],
        "classes": ["Etheric Adept", "Bio-Arcanist", "Star Skald"],
        "backgrounds": ["Relic Guardian", "Vault Custodian", "Pilgrim Guide"],
        "rarity": "rare",
        "lore": "A talisman that pins dangerous artifacts to the current reality, preventing uncontrolled bleed-through.",
        "mechanics": {
            "artifact_stability": 30,
            "corruption_resistance": 20,
            "ritual_control_bonus": 10,
            "slots_used": 1
        }
    },
    "Kinetic_Reflection_Bracers": {
        "slot": "arm",
        "category": "defense",
        "factions": ["Ironclad Collective", "Gearwrights Guild"],
        "classes": ["Grav-Commando", "Mechwright", "Void Corsair"],
        "backgrounds": ["Arena Brawler", "Boarding Specialist", "Urban Sentinel"],
        "rarity": "rare",
        "lore": "Bracers that capture part of incoming kinetic force and redirect it in a controlled backlash.",
        "mechanics": {
            "block_power": 20,
            "counterstrike_chance": 15,
            "user_strain": 8,
            "slots_used": 2
        }
    },
    "Quantum_Prism_Analyser": {
        "slot": "hand",
        "category": "scientific",
        "factions": ["Scholara Nexus", "Quantum Artificers Guild"],
        "classes": ["Data Weaver", "Bio-Arcanist", "Chrononaut"],
        "backgrounds": ["Research Diver", "Laboratory Analyst", "Ruins Tinkerer"],
        "rarity": "uncommon",
        "lore": "A palm-sized prism that reveals layered probabilities and hidden structures in matter and code.",
        "mechanics": {
            "scan_resolution": 90,
            "anomaly_detection": 20,
            "analysis_time_reduction": 15,
            "slots_used": 1
        }
    },
    "Tide_of_Sparks_Pistol": {
        "slot": "weapon_sidearm",
        "category": "ranged",
        "factions": ["Galactic Circus", "Technotheos"],
        "classes": ["Void Corsair", "Star Skald", "Cipher Operative"],
        "backgrounds": ["Street Performer", "Dockside Duellist", "Faith Enforcer"],
        "rarity": "uncommon",
        "lore": "A sidearm that fires cascades of guided micro-sparks, dazzling and scorching in equal measure.",
        "mechanics": {
            "damage": 35,
            "stun_chance": 20,
            "ammo_capacity": 18,
            "slots_used": 1
        }
    },
    "Helioform_Enviro_Shard": {
        "slot": "utility",
        "category": "environment",
        "factions": ["Gaian Enclave", "Stellar Cartographers Alliance"],
        "classes": ["Quantum Ranger", "Bio-Arcanist", "Grav-Commando"],
        "backgrounds": ["Terraformer", "Survey Scout", "Wasteland Nomad"],
        "rarity": "uncommon",
        "lore": "A floating shard that generates a tunable microclimate bubble around its bearer.",
        "mechanics": {
            "temperature_control": 95,
            "toxin_filtering": 20,
            "radiation_shielding": 15,
            "slots_used": 1
        }
    },
    "Cortical_Duet_Implant": {
        "slot": "implant",
        "category": "neural",
        "factions": ["Technotheos", "Collective of Commonality"],
        "classes": ["Data Weaver", "Star Skald", "Cipher Operative"],
        "backgrounds": ["Union Organizer", "Fleet Coordinator", "Choir of Resonance"],
        "rarity": "rare",
        "lore": "Paired implants allowing synchronized thought between two trusted users across short distances.",
        "mechanics": {
            "shared_reaction_bonus": 15,
            "empathy_link_strength": 20,
            "desync_risk": 10,
            "slots_used": 1
        }
    },
    "Grav_Moire_Shield": {
        "slot": "offhand",
        "category": "defense",
        "factions": ["Ironclad Collective", "Voidbound Monks"],
        "classes": ["Grav-Commando", "Void Corsair", "Mechwright"],
        "backgrounds": ["Siege Veteran", "Hull Guardian", "Station Enforcer"],
        "rarity": "epic",
        "lore": "A shield that projects overlapping gravity patterns, bending trajectories and warping impacts.",
        "mechanics": {
            "projectile_bend": 30,
            "area_defense_radius_m": 6,
            "massive_hit_leak": 10,
            "slots_used": 2
        }
    },
    "Echo_Trace_Recorder": {
        "slot": "utility",
        "category": "investigation",
        "factions": ["Veritas Covenant", "Provocateurs' Guild"],
        "classes": ["Cipher Operative", "Data Weaver", "Chrononaut"],
        "backgrounds": ["Black-Box Investigator", "News-Stream Editor", "Court Scribe"],
        "rarity": "uncommon",
        "lore": "A recorder that captures etheric and sensory echoes, reconstructing past scenes as layered projections.",
        "mechanics": {
            "replay_duration_min": 30,
            "detail_resolution": 80,
            "tamper_detection": 25,
            "slots_used": 1
        }
    },
    "Phase_Thread_Rappeller": {
        "slot": "utility",
        "category": "mobility",
        "factions": ["Voidbound Monks", "Stellar Nexus Guild"],
        "classes": ["Quantum Ranger", "Void Corsair", "Grav-Commando"],
        "backgrounds": ["Rift Scout", "Hull Runner", "Derelict Scavenger"],
        "rarity": "uncommon",
        "lore": "A phase-linked line that threads through solid matter along least-resistance paths for exfiltration.",
        "mechanics": {
            "max_length_m": 200,
            "phase_penetration": 70,
            "misroute_risk": 12,
            "slots_used": 1
        }
    },
    "Bio_Cantor_Vials": {
        "slot": "belt",
        "category": "medical/offense",
        "factions": ["Harmonic Vitality Consortium", "Gaian Enclave"],
        "classes": ["Bio-Arcanist", "Etheric Adept", "Star Skald"],
        "backgrounds": ["Plague Zone Survivor", "Frontier Medic", "Cultivated Singer"],
        "rarity": "rare",
        "lore": "Living vials that respond to sung commands, switching from healing serums to aggressive spores.",
        "mechanics": {
            "healing_mode_power": 25,
            "offensive_mode_power": 25,
            "switch_time_s": 2,
            "slots_used": 1
        }
    },
    "Flux_Rider_Gauntlets": {
        "slot": "hand",
        "category": "piloting",
        "factions": ["Stellar Nexus Guild", "Technomancers"],
        "classes": ["Quantum Ranger", "Etheric Adept", "Mechwright"],
        "backgrounds": ["Test Pilot", "Shipwright Scion", "Drift Racer"],
        "rarity": "rare",
        "lore": "Gauntlets that let the pilot feel the flux of drives and ether currents as if they were muscle and wind.",
        "mechanics": {
            "piloting_bonus": 25,
            "crash_avoidance": 15,
            "fatigue_accumulation": 10,
            "slots_used": 1
        }
    },
    "Icon_of_Many_Faiths": {
        "slot": "trinket",
        "category": "social/ethic",
        "factions": ["Technotheos", "Collective of Commonality"],
        "classes": ["Star Skald", "Bio-Arcanist", "Etheric Adept"],
        "backgrounds": ["Machine Pilgrim", "Border Mediator", "Community Anchor"],
        "rarity": "uncommon",
        "lore": "A small rotating poly-icon that adapts its symbolism to comfort nearby belief systems.",
        "mechanics": {
            "conflict_deescalation": 20,
            "faith_trust_bonus": 15,
            "fanatic_trigger_risk": 5,
            "slots_used": 1
        }
    },
    "Spectral_Forge_Shard": {
        "slot": "implant",
        "category": "crafting",
        "factions": ["Gearwrights Guild", "Quantum Artificers Guild"],
        "classes": ["Mechwright", "Data Weaver", "Bio-Arcanist"],
        "backgrounds": ["Ruins Tinkerer", "Shipwright Scion", "Expedition Scholar"],
        "rarity": "epic",
        "lore": "An embedded shard that projects ghost-blueprints of devices before matter is ever shaped.",
        "mechanics": {
            "design_speed_bonus": 30,
            "fabrication_success_rate": 20,
            "overdesign_risk": 10,
            "slots_used": 1
        }
    },
    "Rift_Sense_Pendant": {
        "slot": "neck",
        "category": "navigation/defense",
        "factions": ["Etheric Preservationists", "Voidbound Monks"],
        "classes": ["Chrononaut", "Etheric Adept", "Quantum Ranger"],
        "backgrounds": ["Rift Scout", "Boundary Guard", "Wreck Diver"],
        "rarity": "uncommon",
        "lore": "A pendant that warms near thin places in reality, and burns near truly dangerous ones.",
        "mechanics": {
            "rift_detection_radius_m": 500,
            "danger_prediction": 20,
            "false_positive_rate": 8,
            "slots_used": 1
        }
    },
    "Circuit_Chant_Tome": {
        "slot": "hand",
        "category": "ritual/tech",
        "factions": ["Technotheos", "Technomancers"],
        "classes": ["Etheric Adept", "Star Skald", "Data Weaver"],
        "backgrounds": ["Machine Pilgrim", "Temple Resonant", "Laboratory Analyst"],
        "rarity": "rare",
        "lore": "A hybrid codex of chants and code snippets that invoke cooperative machine-ether behavior.",
        "mechanics": {
            "ai_harmony_bonus": 20,
            "system_uptime_bonus": 10,
            "ritual_cast_time_reduction": 15,
            "slots_used": 1
        }
    },
    "Pulse_Lattice_Lance": {
        "slot": "weapon_main",
        "category": "melee/ranged hybrid",
        "factions": ["Ironclad Collective", "Icaron Collective"],
        "classes": ["Grav-Commando", "Void Corsair", "Mechwright"],
        "backgrounds": ["Arena Brawler", "Counter-Pirate Marine", "Urban Breacher"],
        "rarity": "epic",
        "lore": "A collapsible lance that discharges staged grav-pulses along its length or as a focused bolt.",
        "mechanics": {
            "melee_damage": 55,
            "ranged_damage": 45,
            "stagger_chance": 20,
            "slots_used": 3
        }
    },
    "Whisperline_Entangler": {
        "slot": "utility",
        "category": "counter-intel",
        "factions": ["Provocateurs' Guild", "Veritas Covenant"],
        "classes": ["Cipher Operative", "Data Weaver", "Chrononaut"],
        "backgrounds": ["Insurgency Liaison", "News-Stream Editor", "Black-Box Investigator"],
        "rarity": "rare",
        "lore": "A device that latches onto enemy comms and braids their messages into misleading duplicates.",
        "mechanics": {
            "intercept_rate": 25,
            "confusion_index": 20,
            "trace_back_risk": 15,
            "slots_used": 1
        }
    },
    "Soulprint_Flare": {
        "slot": "deployable",
        "category": "recon",
        "factions": ["Harmonic Resonance Collective", "Scholara Nexus"],
        "classes": ["Etheric Adept", "Star Skald", "Quantum Ranger"],
        "backgrounds": ["Choir of Resonance", "Expedition Scholar", "Signal Diver"],
        "rarity": "rare",
        "lore": "A flare that records the emotional and etheric signatures present when it ignites.",
        "mechanics": {
            "signature_capture_quality": 90,
            "duration_s": 120,
            "area_radius_m": 30,
            "slots_used": 1
        }
    },
    "Collective_Link_Rig": {
        "slot": "implant",
        "category": "coordination",
        "factions": ["Collective of Commonality", "Stellar Nexus Guild"],
        "classes": ["Data Weaver", "Grav-Commando", "Star Skald"],
        "backgrounds": ["Union Organizer", "Fleet Coordinator", "Community Anchor"],
        "rarity": "epic",
        "lore": "An implant that aggregates team intent into a shared tactical overlay with negotiated priorities.",
        "mechanics": {
            "squad_efficiency_bonus": 25,
            "decision_latency_reduction": 20,
            "overwhelm_risk": 10,
            "slots_used": 1
        }
    },
    "Null_Script_Injector": {
        "slot": "weapon_sidearm",
        "category": "cyber",
        "factions": ["Technomancers", "Quantum Artificers Guild"],
        "classes": ["Cipher Operative", "Data Weaver", "Mechwright"],
        "backgrounds": ["Counter-Intel Defector", "Laboratory Analyst", "Station Mechanic"],
        "rarity": "rare",
        "lore": "A pistol that fires data-tipped flechettes, injecting null scripts into hostile systems on impact.",
        "mechanics": {
            "damage": 20,
            "system_crash_chance": 30,
            "countermeasure_risk": 15,
            "slots_used": 1
        }
    },
    "Resonant_Pilgrim_Staff": {
        "slot": "weapon_main",
        "category": "melee/support",
        "factions": ["Technotheos", "Harmonic Vitality Consortium"],
        "classes": ["Etheric Adept", "Star Skald", "Bio-Arcanist"],
        "backgrounds": ["Machine Pilgrim", "Temple Resonant", "Frontier Mediarch"],
        "rarity": "rare",
        "lore": "A staff that carries and amplifies hymns, turning ritual songs into shield or scourge.",
        "mechanics": {
            "melee_damage": 35,
            "support_aura_power": 20,
            "corruption_cleanse": 10,
            "slots_used": 2
        }
    },
    "Mirage_Spine_Armor": {
        "slot": "armor",
        "category": "stealth/defense",
        "factions": ["Provocateurs' Guild", "Voidbound Monks"],
        "classes": ["Cipher Operative", "Void Corsair", "Chrononaut"],
        "backgrounds": ["Insurgency Liaison", "Wreck Diver", "Dockside Duellist"],
        "rarity": "epic",
        "lore": "Armor that projects multiple afterimages of the wearer with slight physical substance.",
        "mechanics": {
            "decoy_count": 3,
            "hit_redirection_chance": 25,
            "maintain_focus_cost": 15,
            "slots_used": 3
        }
    },
    "Axial_Ring_of_Return": {
        "slot": "finger",
        "category": "chrono/utility",
        "factions": ["Technomancers", "Etheric Preservationists"],
        "classes": ["Chrononaut", "Etheric Adept", "Quantum Ranger"],
        "backgrounds": ["Temporal Exile", "Boundary Guard", "Test Pilot"],
        "rarity": "legendary",
        "lore": "A ring that bookmarks a previous state of the wearer’s position for a single emergency recall.",
        "mechanics": {
            "max_distance_m": 2000,
            "time_window_s": 20,
            "cooldown_missions": 1,
            "slots_used": 1
        }
    }
}
