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
  RESISTANCE_PROPERTY_KEYS: new Set(),
});
vm.runInContext(relevant + "\nthis.getLabel = propertyLabel; this.getValue = propertyValue;", context);

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
