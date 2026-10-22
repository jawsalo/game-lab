# GrimTools Item-Card Display Baseline

This is the reference baseline for matching the **wording, grouping, and ordering** of GrimTools item cards. It records four item cards from three user-provided GrimTools screenshots (Game 1.3.1.0). The screenshots are the visual source; this Markdown transcription makes the reference searchable and easy for an assistant to digest.

> This is a presentation baseline, not a statement that our current API already exposes every field. Values and labels should be checked against the pinned catalog record before implementation. Preserve the source data and add the missing mapping/display behavior deliberately.

## Baseline coverage

| Card | Screenshot | Important cases |
| --- | --- | --- |
| Serenity, Mythical Relic | `01-1000115463.jpg` | Item stats, variant ranges, granted skill, proc thresholds/recharge/duration, completion bonus, source/crafting relationship, expansion |
| Blueprint: Relic - Serenity | `01-1000115463.jpg` | Recipe ingredients and quantities, crafted output, drop source |
| Mythical Ring of the Black Matriarch | `02-1000115464.jpg` | Flavor text, damage-over-time, retaliation, skill bonuses, granted skill details, level/attribute requirements, expansion |
| Dauntless, Legendary Shield | `03-1000115465.jpg` | Block stats, conversions, retaliation, skill bonuses, embedded item skills and modifiers, faction/vendor/source information, expansion |

The three original screenshots were uploaded with these names:

- `1000115463.jpg`
- `1000115464.jpg`
- `1000115465.jpg`

The first screenshot contains two cards, so the reference set is four cards in total.

## Card 1 — Serenity

**Mythical Relic**  
“Peace within oneself.”

### Base item properties

- +240/+360 Health
- +4/+6% Movement Speed
- 20/30% Aether Resistance
- 20/30% Chaos Resistance
- 16/24% Reflected Damage Reduction
- +1 to all Skills

### Granted skill

**Serenity** (Granted by Item)  
“Serenity fills you in time of need, offering respite from grievous wounds.”

- Activates when Health drops below 35%
- 80 Second Skill Recharge
- 3 Second Duration
- 10% + 1000 Health Restored
- 35% Physical Resistance
- 35% Pierce Resistance
- 35% Poison & Acid Resistance
- 35% Vitality Resistance
- 35% Aether Resistance
- 35% Chaos Resistance
- 35% Elemental Resistance
- 35% Bleeding Resistance
- 35% Resistance to Life Reduction

### Completion bonus and provenance

- Completion Bonus
- Required Player Level: 90
- Item Level: 90
- Obtained from: Crafting — Blueprint: Relic - Serenity
- Expansion label: Forgotten Gods

## Card 2 — Blueprint: Relic - Serenity

**Blueprint: Relic - Serenity**  
“Ancient forging technique thought lost to the Grim Dawn.”

### Ingredients

- Wendigo Spirit (15)
- Citadel (1)
- Kilrian’s Shattered Soul (1)
- Blessed Whetstone (1)

### Output and provenance

- Crafts: Serenity (1)
- Obtained from: Random drop

This card demonstrates a blueprint as a separate searchable item, with ingredient quantities and an explicit crafted output linking back to an item.

## Card 3 — Mythical Ring of the Black Matriarch

“Signet of the Black Matriarch, a ruthless assassin who utilized spider venom to paralyze and execute her opponents.”

**Legendary Ring**

### Properties, in displayed order

- 1/3% of Attack Damage converted to Health
- 70/95 Poison Damage over 5 Seconds
- +85/+127% Physical Damage
- +85/+127% Acid Damage
- +85/+127% Internal Trauma Damage
- +85/+127% Poison Damage
- +23/+33 Cunning
- +4/+6% Attack Speed
- 27/39% Pierce Resistance
- 10/14% Vitality Resistance
- +3% Max Vitality Resistance
- 352/528 Acid Retaliation
- +2 to Cadence
- +2 to Curse of Frailty
- +2 to Nidalla’s Hidden Hand
- +2 to Righteous Fervor

### Granted skill

**Venom of the Black Matriarch** (15% Chance on Attack)  
“Inject your target with the deadly venom of the Black Matriarch.”

- 0.5 Second Skill Recharge
- 5 Second Duration
- 112 Poison Damage per Second
- -10% Physical Resistance

### Requirements and provenance

- Required Player Level: 94
- Required Spirit: 402
- Item Level: 94
- Obtained from: Random drop
- Expansion label: Ashes of Malmouth

This card demonstrates why a card cannot filter stats only by `character`, `defensive`, `offensive`, and `skill` prefixes: Acid Retaliation and granted-skill bonuses are important displayed data too.

## Card 4 — Dauntless

**Legendary Shield**

### Shield base stats

- 34% Chance to block 930 damage
- 0.6 Second Block Recovery
- 170 Physical Damage

### Item properties and conversions

- +89/+134% Physical Damage
- +89/+134% Internal Trauma Damage
- +100/+151% Burn Damage
- 36/54% Chaos Damage converted to Physical Damage
- 36/54% Acid Damage converted to Physical Damage
- +60/+90 Defensive Ability
- 12/16% Physical Resistance
- 32/48% Poison & Acid Resistance
- 1200/1800 Physical Damage Retaliation
- +108/+162% Physical Damage Retaliation
- +4 to Scars of Battle
- +3 to Menhir’s Bulwark
- +3 to Vindictive Flame
- +3 to Curse of Frailty
- +1 to all skills in Soldier
- +1 to all skills in Occultist

### Item skills and modifiers

**Counter Strike**

- 8% of Retaliation Damage added to Attack

**Vindictive Flame**

- -0.3 Second Skill Recharge
- 10% of Retaliation Damage added to Attack
- 180 Physical Damage
- 100% Fire Damage converted to Physical Damage

**Curse of Frailty**

- +25% Attack Speed
- -10% Physical Resistance

### Requirements and provenance

- Required Player Level: 94
- Required Physique: 777
- Item Level: 94
- Faction: Kurn
- Can be sold by: Atka of the Iron Clan (Kurnhold) [Map]
- Obtained from: Crafting — Blueprint: Dauntless
- Expansion label: Fangs of Asterkarn

This card demonstrates shield-specific values, multiple damage conversions, retaliation values, skill bonuses, and skills with item-specific modifiers. The display should group these clearly instead of flattening every numeric source field into one undifferentiated property list.

## Display-order pattern to test

Across the examples, use this as the initial ordering model:

1. Item name and flavor description
2. Item type/rarity and shield-specific base stats, when applicable
3. Core item properties, in source/card order
4. Granted skills and each skill’s description, trigger, recharge/duration, and effects
5. Completion bonus, if present
6. Requirements and item level
7. Faction, vendor, crafting, and drop provenance
8. Expansion label

Blueprint cards have their own compact structure: name, description, ingredients with quantities, crafted output, and source.

This is a baseline, not a final UI mandate. If source fields cannot yet be resolved, show an explicit unknown/unresolved state rather than inventing a skill name, stat label, or source.

## Implementation notes

- Keep the raw catalog record available for inspection; the display card is a projection, not the database itself.
- Add structured support for retaliation and granted skills before trying to solve them solely with frontend labels.
- Use translation/formatting maps for human-readable stat labels and units, while keeping original source keys alongside the rendered label.
- Skill/controller IDs need versioned lookup data before their names can be displayed reliably.
- Recipes should resolve ingredient and output item IDs to catalog names where possible, while retaining IDs for stable linking.
- Keep exact game wording, ordering, punctuation, percentages, and variant ranges as reference evidence. The screenshots are authoritative when this transcription is ambiguous.
