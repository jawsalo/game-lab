// Run with: node --test apps/web/tests/property-labels.test.cjs
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "..", "app.js"), "utf8");
const labelsStart = source.indexOf("const PROPERTY_LABELS = {");
const labelsEnd = source.indexOf("\nfunction addSectionHeading(", labelsStart);
assert.ok(labelsStart >= 0 && labelsEnd > labelsStart, "Property formatter must exist");

// Evaluate the production label/value formatters without running the DOM app.
const relevant = source.slice(labelsStart, labelsEnd);
const context = vm.createContext({
  numberFormatter: new Intl.NumberFormat("en-US"),
});
vm.runInContext(relevant + "\nthis.getLabel = propertyLabel; this.getValue = propertyValue; this.conversionDisplayName = conversionDisplayName; this.groupItemProperties = groupItemProperties; this.groupedPropertySections = groupedPropertySections; this.classifyItemProperty = classifyItemProperty;", context);

test("damage-over-time modifiers use player-facing damage names", () => {
  for (const [key, expected] of [
    ["offensiveSlowBleedingModifier", "Bleeding Damage"],
    ["offensiveSlowFireModifier", "Burn Damage"],
    ["offensiveSlowColdModifier", "Frostburn Damage"],
    ["offensiveSlowLightningModifier", "Electrocute Damage"],
    ["offensiveSlowPoisonModifier", "Poison Damage"],
    ["offensiveSlowLifeModifier", "Vitality Decay Damage"],
    ["offensiveSlowPhysicalModifier", "Internal Trauma Damage"],
  ]) {
    assert.equal(context.getLabel({ key }), expected, key);
    assert.equal(context.getValue({ key, value: 100, minValue: 100, maxValue: 151 }), "+100/+151%", key);
  }
});

test("flat and percentage damage are distinct from damage over time", () => {
  assert.equal(context.getLabel({ key: "offensiveBaseAetherMin" }), "Flat Aether Damage");
  assert.equal(context.getLabel({ key: "offensiveAetherModifier" }), "Aether Damage");
  assert.equal(context.getLabel({ key: "offensiveSlowBleedingMin" }), "Offensive Slow Bleeding Min");
});

test("block chance is percent; blocked damage remains flat", () => {
  assert.equal(context.getLabel({ key: "defensiveBlockChance" }), "Block Chance");
  assert.equal(context.getValue({ key: "defensiveBlockChance", value: 34 }), "+34%");
  assert.equal(context.getLabel({ key: "defensiveBlock" }), "Blocked Damage");
  assert.equal(context.getValue({ key: "defensiveBlock", value: 930 }), "+930");
});

test("Dauntless conversion names include full damage types and rolled ranges", () => {
  assert.equal(
    context.conversionDisplayName({ from: "chaos", to: "physical", percentage: 45, minValue: 36, maxValue: 54 }),
    "36/54% Chaos Damage converted to Physical Damage"
  );
  assert.equal(
    context.conversionDisplayName({ from: "acid", to: "physical", percentage: 45, minValue: 36, maxValue: 54 }),
    "36/54% Acid Damage converted to Physical Damage"
  );
});

test("conversion formatting preserves fixed percentages and handles damage siblings", () => {
  assert.equal(
    context.conversionDisplayName({ from: "fire", to: "cold", percentage: 25 }),
    "25% Fire Damage converted to Cold Damage"
  );
  assert.equal(
    context.conversionDisplayName({ from: "poison", to: "vitality", percentage: 50 }),
    "50% Acid Damage converted to Vitality Damage"
  );
  assert.equal(
    context.conversionDisplayName({ from: "aether", to: "lightning", percentage: 12, minValue: 10, maxValue: 14 }),
    "10/14% Aether Damage converted to Lightning Damage"
  );
  assert.equal(
    context.conversionDisplayName({ from: "unknownType", to: "physical", percentage: 20 }),
    "20% Unknown Type converted to Physical Damage"
  );
});

test("Dauntless shield stats are first, retain their values, and are not duplicated", () => {
  const properties = [
    { key: "characterDefensiveAbility", value: 75 },
    { key: "defensiveBlock", value: 930, minValue: 744, maxValue: 1116 },
    { key: "offensivePhysicalModifier", value: 110 },
    { key: "defensiveBlockChance", value: 34 },
  ];
  const grouped = context.groupItemProperties({
    id: "it14449", category: "ArmorProtective_Shield", slot: "Shield", properties,
  });
  assert.deepEqual(Array.from(grouped.shieldStats, (p) => p.key),
    ["defensiveBlockChance", "defensiveBlock"]);
  assert.deepEqual(Array.from(grouped.general, (p) => p.key),
    ["characterDefensiveAbility", "offensivePhysicalModifier"]);
  assert.equal(context.getValue(grouped.shieldStats[0]), "+34%");
  assert.equal(context.getValue(grouped.shieldStats[1]), "+744/+1,116");
  assert.equal(grouped.shieldStats.length + grouped.general.length, properties.length);
});

test("other shields, including Bramblevine, use the same shield-only grouping", () => {
  const properties = [
    { key: "defensiveBlock", value: 500 },
    { key: "defensiveBlockChance", value: 25 },
    { key: "defensivePhysical", value: 10 },
  ];
  const grouped = context.groupItemProperties({
    id: "it12725", slot: "Shield", category: "OtherShieldCategory", properties,
  });
  assert.deepEqual(Array.from(grouped.shieldStats, (p) => p.key),
    ["defensiveBlockChance", "defensiveBlock"]);
  assert.deepEqual(Array.from(grouped.general, (p) => p.key), ["defensivePhysical"]);
});

test("non-shields retain all original properties and their order", () => {
  const properties = [
    { key: "defensiveBlock", value: 500 },
    { key: "offensivePhysicalModifier", value: 50 },
    { key: "defensiveBlockChance", value: 20 },
  ];
  const grouped = context.groupItemProperties({
    id: "non-shield", slot: "Chest", category: "ArmorProtective_Chest", properties,
  });
  assert.equal(grouped.shieldStats.length, 0);
  assert.deepEqual(Array.from(grouped.general, (p) => p.key),
    ["defensiveBlock", "offensivePhysicalModifier", "defensiveBlockChance"]);
  assert.equal(context.groupItemProperties({ slot: "Shield", properties: [] }).shieldStats.length, 0);
});


test("movement speed and maximum movement speed retain distinct labels and rolls", () => {
  for (const [item, properties, expected] of [
    ["Mythical Bloodmist Boots", [
      { key: "characterRunSpeedModifier", value: 10, minValue: 8, maxValue: 12 },
    ], [["Movement Speed", "+8/+12%"]]],
    ["Mythical Boneshatter Treads", [
      { key: "characterRunSpeedModifier", value: 8, minValue: 7, maxValue: 9 },
      { key: "characterRunSpeedMaxModifier", value: 3, minValue: 2, maxValue: 4 },
    ], [["Movement Speed", "+7/+9%"], ["Maximum Movement Speed", "+2/+4%"]]],
    ["Non-boot equipment with movement speed", [
      { key: "characterRunSpeedModifier", value: 5 },
      { key: "characterRunSpeedMaxModifier", value: 2 },
    ], [["Movement Speed", "+5%"], ["Maximum Movement Speed", "+2%"]]],
  ]) {
    assert.deepEqual(properties.map((property) => [
      context.getLabel(property), context.getValue(property),
    ]), expected, item);
  }
});

test("movement speed labels do not change other speed or life-related properties", () => {
  assert.equal(context.getLabel({ key: "characterAttackSpeedModifier" }), "Attack Speed");
  assert.equal(context.getLabel({ key: "characterSpellCastSpeedModifier" }), "Cast Speed");
  assert.equal(context.getLabel({ key: "characterTotalSpeedModifier" }), "Character Total Speed Modifier");
  assert.equal(context.getLabel({ key: "characterRunSpeed" }), "Character Run Speed");
  assert.equal(context.getLabel({ key: "characterLifeModifier" }), "Health");
});

test("offensive Life damage family uses Vitality Damage labels and preserves rolls", () => {
  for (const item of ["Mythical Boneshatter Treads (it9093)", "Mythical Bilethread Greaves (it14641)"]) {
    const property = { key: "offensiveLifeModifier", value: 83, minValue: 67, maxValue: 100 };
    assert.equal(context.getLabel(property), "Vitality Damage", item);
    assert.equal(context.getValue(property), "+67/+100%", item);
  }
  assert.equal(context.getLabel({ key: "offensiveBaseLifeMin" }), "Flat Vitality Damage");
  assert.equal(context.getLabel({ key: "offensiveLifeMin" }), "Offensive Life Min");
  assert.equal(context.getLabel({ key: "offensiveSlowLifeModifier" }), "Vitality Decay Damage");
});

test("Vitality damage labeling does not affect health, resistance, or life leech", () => {
  for (const [key, expected] of [
    ["characterLife", "Health"],
    ["characterLifeModifier", "Health"],
    ["defensiveLife", "Vitality Resistance"],
    ["offensiveLifeLeechMin", "Attack Damage converted to Health"],
    ["defensiveSlowLifeLeech", "Defensive Slow Life Leech"],
  ]) {
    assert.equal(context.getLabel({ key }), expected, key);
  }
});

test("base armor appears in its own section on boots without duplication", () => {
  for (const item of ["it9093", "it14641", "it14640"]) {
    const properties = [
      { key: "characterDefensiveAbility", value: 75 },
      { key: "defensiveProtection", value: 1454 },
      { key: "offensiveLifeModifier", value: 100 },
    ];
    const grouped = context.groupItemProperties({
      id: item, group: "equipment", slot: "Feet", properties,
    });
    assert.deepEqual(Array.from(grouped.baseStats, (p) => p.key), ["defensiveProtection"]);
    assert.deepEqual(Array.from(grouped.general, (p) => p.key),
      ["characterDefensiveAbility", "offensiveLifeModifier"]);
    assert.equal(context.getLabel(grouped.baseStats[0]), "Armor");
    assert.equal(context.getValue(grouped.baseStats[0]), "+1,454");
    assert.equal(grouped.baseStats.length + grouped.general.length, properties.length);
  }
});

test("shields retain shield stats first and armor separately when present", () => {
  const properties = [
    { key: "defensiveProtection", value: 1000 },
    { key: "defensiveBlock", value: 900 },
    { key: "defensiveBlockChance", value: 34 },
    { key: "defensivePhysical", value: 10 },
  ];
  const grouped = context.groupItemProperties({
    id: "shield", group: "equipment", slot: "Shield", properties,
  });
  assert.deepEqual(Array.from(grouped.shieldStats, (p) => p.key),
    ["defensiveBlockChance", "defensiveBlock"]);
  assert.deepEqual(Array.from(grouped.baseStats, (p) => p.key), ["defensiveProtection"]);
  assert.deepEqual(Array.from(grouped.general, (p) => p.key), ["defensivePhysical"]);
  assert.equal(grouped.shieldStats.length + grouped.baseStats.length + grouped.general.length,
    properties.length);
});

test("items without base armor and non-equipment records remain unchanged", () => {
  const properties = [
    { key: "defensiveProtection", value: 50 },
    { key: "characterLife", value: 100 },
  ];
  const nonEquipment = context.groupItemProperties({ group: "component", properties });
  assert.equal(nonEquipment.baseStats.length, 0);
  assert.deepEqual(Array.from(nonEquipment.general, (p) => p.key),
    ["defensiveProtection", "characterLife"]);
  const noArmor = context.groupItemProperties({
    group: "equipment", slot: "Finger", properties: [properties[1]],
  });
  assert.equal(noArmor.baseStats.length, 0);
  assert.deepEqual(Array.from(noArmor.general, (p) => p.key), ["characterLife"]);
});

test("six-group presentation classifies representative source keys without losing properties", () => {
  const properties = [
    { key: "characterOffensiveAbility", value: 75 },
    { key: "offensiveLifeModifier", value: 100 },
    { key: "defensivePhysical", value: 5 },
    { key: "characterRunSpeedModifier", value: 8 },
    { key: "retaliationPoisonMin", value: 368 },
    { key: "defensiveSlowLifeLeech", value: 40 },
    { key: "unrecognizedSourceStat", value: 123 },
    { key: "defensiveProtection", value: 1454 },
    { key: "characterLife", value: 500 },
    { key: "defensiveTotalSpeed", value: 24 },
  ];
  const sections = context.groupedPropertySections({ group: "equipment", slot: "Feet", properties });
  assert.deepEqual(Array.from(sections, (section) => section.heading), [
    "Base Stats", "Attributes & Combat", "Damage & Retaliation",
    "Resistances & Defense", "Utility", "Other Properties",
  ]);
  const keys = Array.from(sections, (section) =>
    Array.from(section.properties, (property) => property.key)).flat();
  assert.equal(keys.length, properties.length);
  assert.equal(new Set(keys).size, keys.length);
  assert.deepEqual(keys.slice(-1), ["unrecognizedSourceStat"]);
  assert.deepEqual(Array.from(sections[2].properties, (property) => property.key),
    ["offensiveLifeModifier", "retaliationPoisonMin"]);
  assert.deepEqual(Array.from(sections[3].properties, (property) => property.key),
    ["defensivePhysical", "defensiveSlowLifeLeech", "defensiveTotalSpeed"]);
});

test("shields put block chance, blocked damage, and armor in one base section", () => {
  const properties = [
    { key: "defensiveProtection", value: 1200 },
    { key: "defensiveBlock", value: 900 },
    { key: "defensiveBlockChance", value: 34 },
    { key: "defensivePhysical", value: 10 },
  ];
  const sections = context.groupedPropertySections({
    group: "equipment", slot: "Shield", properties,
  });
  assert.equal(sections[0].heading, "Base Stats");
  assert.deepEqual(Array.from(sections[0].properties, (property) => property.key),
    ["defensiveBlockChance", "defensiveBlock", "defensiveProtection"]);
  assert.equal(sections[1].heading, "Resistances & Defense");
});

test("unknown and ambiguous properties stay visible and are not guessed into a group", () => {
  const properties = [
    { key: "offensiveLifeLeechMin", value: 5 },
    { key: "offensiveSlowLifeLeechMin", value: 8 },
    { key: "retaliationUnknownModifier", value: 10 },
    { key: "defensiveBlock", value: 200 },
    { key: "defensiveProtection", value: 20 },
    { key: "characterRunSpeedModifier", value: 7 },
  ];
  const sections = context.groupedPropertySections({ group: "component", properties });
  const other = sections.find((section) => section.key === "other");
  assert.deepEqual(Array.from(other.properties, (property) => property.key),
    ["offensiveLifeLeechMin", "offensiveSlowLifeLeechMin",
      "retaliationUnknownModifier", "defensiveBlock", "defensiveProtection"]);
  assert.equal(sections.some((section) => section.key === "base"), false);
  assert.equal(sections.some((section) => section.key === "utility"), true);
});

test("empty sections are omitted and source order is stable within a group", () => {
  const properties = [
    { key: "offensiveFireModifier", value: 10 },
    { key: "offensivePhysicalModifier", value: 20 },
    { key: "offensiveSlowLifeModifier", value: 30 },
  ];
  const sections = context.groupedPropertySections({ group: "equipment", properties });
  assert.deepEqual(Array.from(sections, (section) => section.heading), ["Damage & Retaliation"]);
  assert.deepEqual(Array.from(sections[0].properties, (property) => property.key),
    properties.map((property) => property.key));
  assert.equal(context.groupedPropertySections({ group: "equipment", properties: [] }).length, 0);
});
