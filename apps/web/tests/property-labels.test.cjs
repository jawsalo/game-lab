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
vm.runInContext(relevant + "\nthis.getLabel = propertyLabel; this.getValue = propertyValue; this.conversionDisplayName = conversionDisplayName; this.groupItemProperties = groupItemProperties;", context);

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

