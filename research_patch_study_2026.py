"""First-party database study for /research/7600-vintage-synth-patches-database-study."""

STUDY_PAGE_URL = "https://bipluk.com/research/7600-vintage-synth-patches-database-study"
STUDY_DATA_URL = f"{STUDY_PAGE_URL}/data.json"

PATCH_STUDY_2026 = {
    "title": "What 7,600 Synthesizer Patches Taught Us About the Fragility of 1980s Memory",
    "slug": "7600-vintage-synth-patches-database-study",
    "period": "March to September 2026",
    "method": (
        "Empirical analysis of 7,600 synthesizer patches, 49 soundbanks, and 96 registered accounts "
        "stored in bipluk's production PostgreSQL vault (Half Radiation LLC). Analyzed patch nomenclature, "
        "SysEx binary payload sizes, hardware architecture share, user activation funnels, and Web MIDI pacing constraints."
    ),
    "metrics": {
        "total_patches_analyzed": 7600,
        "total_banks_uploaded": 49,
        "registered_synth_owners": 96,
        "generic_placeholder_patches": 5216,
        "generic_placeholder_pct": 68.6,
        "day_one_backup_success_pct": 29.1,
        "day_one_backup_success_users": 28,
        "second_session_retention_pct": 10.4,
        "paid_tier_conversion_pct": 6.25,
        "paid_tier_conversions": 6,
        "free_tier_avg_logins": 1.24,
        "max_single_user_logins": 14,
        "midi_baud_rate": 31250,
        "safe_packet_chunk_bytes": 64,
        "safe_packet_delay_ms": 25,
    },
    "patch_naming_breakdown": [
        {"category": "Generic / Factory Placeholders ('Preset X', '11 c')", "count": 5216, "pct": 68.6},
        {"category": "Bass", "count": 132, "pct": 1.7},
        {"category": "Ambient / Poly Pads", "count": 87, "pct": 1.1},
        {"category": "Pianos / Rhodes / FM EP", "count": 64, "pct": 0.8},
        {"category": "Synth Strings", "count": 37, "pct": 0.5},
        {"category": "Solo Leads", "count": 36, "pct": 0.5},
        {"category": "Other / Bespoke Titles", "count": 2028, "pct": 26.8},
    ],
    "synth_architecture_share": [
        {"model": "Yamaha DX7 (6-op FM)", "count": 5760, "pct": 75.8, "avg_bytes": 4104},
        {"model": "Auto-Detect / Multi-format", "count": 976, "pct": 12.8, "avg_bytes": 28637},
        {"model": "Sequential Prophet-5 / 600", "count": 328, "pct": 4.3, "avg_bytes": 6374},
        {"model": "Generic SysEx Dumps", "count": 192, "pct": 2.5, "avg_bytes": 1024},
        {"model": "Roland Juno-106 & D-50", "count": 144, "pct": 1.9, "avg_bytes": 3584},
        {"model": "Korg DW-6000 & DW-8000", "count": 128, "pct": 1.7, "avg_bytes": 2048},
        {"model": "Other Vintage Hardware", "count": 72, "pct": 0.9, "avg_bytes": 4096},
    ],
    "activation_funnel": [
        {"step": "Account Created & Email Verified", "users": 96, "pct": 100.0},
        {"step": "Completed First Web-MIDI SysEx Backup", "users": 28, "pct": 29.1},
        {"step": "Returned for Session 2+ (>1 Logins)", "users": 10, "pct": 10.4},
        {"step": "Converted to Paid Studio / Lifetime Tier", "users": 6, "pct": 6.25},
    ],
    "findings": [
        {
            "id": "nameless-bank-epidemic",
            "number": "01",
            "headline": "The Nameless Bank Epidemic",
            "summary": "68.6% of vintage synthesizer patches have generic placeholder names like 'Preset 1016'.",
            "body": (
                "When you inspect 7,600 patches pulled from vintage SRAM, the first thing that hits you is organizational entropy. "
                "Musicians do not label patches because 1980s user interfaces were hostile to human language. Naming a voice on a "
                "Yamaha DX7 requires toggling through 32 sub-menus with two membrane buttons and a data slider that skips characters "
                "if your finger twitches. If hardware makes naming a sound take longer than 8 seconds, musicians default to 'PRESET 01' "
                "and gamble their entire live set on muscle memory."
            ),
        },
        {
            "id": "dx7-javascript-of-hardware",
            "number": "02",
            "headline": "The DX7 is the JavaScript of Hardware Synths",
            "summary": "75.8% of all uploaded patches belong to Yamaha DX7 voice banks, driven by battery replacement dread.",
            "body": (
                "Every hardware era has one machine that dominates all traffic by brute force. In vintage MIDI, it is the Yamaha DX7. "
                "The DX7 owns three-quarters of our vault not just because Yamaha sold 200,000 units in the 1980s, but because the internal "
                "3V CR2032 battery is soldered directly to the motherboard with two solder tabs. When the cell drops below 2.2V, the RAM "
                "corrupts into gibberish and outputs ear-splitting digital static. Musicians back up because they dread soldering irons."
            ),
        },
        {
            "id": "activation-cliff",
            "number": "03",
            "headline": "The 29% Physical Activation Cliff",
            "summary": "Only 29.1% of signups complete a backup on day one due to physical MIDI interface and cable friction.",
            "body": (
                "Software onboarding stops at the keyboard; hardware onboarding requires debugging the physical universe between "
                "a browser and a diode manufactured in Osaka forty years ago. Between browser Web MIDI permission daemons, low-cost "
                "USB-MIDI dongles that drop SysEx buffers, and rear-panel physical MEMORY PROTECT toggle switches, 70.9% of users stall "
                "on their first attempt. The average login count for unactivated users is 1.24 before dropping off."
            ),
        },
        {
            "id": "baud-bottleneck",
            "number": "04",
            "headline": "The 31,250 Baud Bottleneck & Packet Pacing",
            "summary": "Modern 12 Mbps USB pipelines flood 1983 4-MHz microprocessors unless artificial pacing is injected.",
            "body": (
                "MIDI was standardized in 1983 at an asynchronous baud rate of 31,250 bps. When modern operating systems blast large "
                "SysEx dumps (such as a 300KB Sequential Prophet raw dump) at full USB 2.0 speed, vintage 8-bit chips like the Motorola 6809 "
                "or Intel 8051 experience catastrophic buffer overruns and freeze. Making 7,600 patches back up cleanly required pacing "
                "transmission in 64-byte chunks with an intentional 25ms delay."
            ),
        },
        {
            "id": "hardware-saas-insurance",
            "number": "05",
            "headline": "Hardware SaaS is an Insurance Game, Not a Feature Game",
            "summary": "Musicians don't want AI patch generation; they want zero-loss reliability before their vintage batteries die.",
            "body": (
                "The creator economy narrative insists that musicians demand AI voice generation and endless algorithmic variations. "
                "Our telemetry demonstrates the opposite: musicians want 100% certainty that when they power up their synth on stage in Berlin, "
                "the patches sculpted over twenty years are intact. The 6.25% of customers who converted to paid licenses bought peace of mind."
            ),
        },
    ],
}


def public_json() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": PATCH_STUDY_2026["title"],
        "description": (
            "Empirical database study analyzing 7,600 synthesizer patches, 49 soundbanks, and 96 synth owners "
            "archived in bipluk's cloud SysEx vault. Details preset nomenclature entropy, Yamaha DX7 dominance, "
            "hardware onboarding friction, and Web MIDI 31,250 baud packet pacing."
        ),
        "url": STUDY_PAGE_URL,
        "creator": {
            "@type": "Organization",
            "name": "Half Radiation LLC",
            "url": "https://bipluk.com",
        },
        "datePublished": "2026-09-16",
        "temporalCoverage": "2026-03-01/2026-09-16",
        "variableMeasured": [
            "Synthesizer patch naming distribution",
            "SysEx binary payload byte sizes",
            "Hardware synth architecture market share",
            "Web MIDI physical activation funnel",
            "Baud rate packet transmission pacing",
        ],
        "size": (
            f"{PATCH_STUDY_2026['metrics']['total_patches_analyzed']} patches across "
            f"{PATCH_STUDY_2026['metrics']['total_banks_uploaded']} soundbanks and "
            f"{PATCH_STUDY_2026['metrics']['registered_synth_owners']} registered synth owners"
        ),
        "citation": (
            f"Half Radiation LLC, {PATCH_STUDY_2026['title']}, bipluk research, "
            f"{PATCH_STUDY_2026['period']}."
        ),
        "data": PATCH_STUDY_2026,
    }
