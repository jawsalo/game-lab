const statusDot = document.querySelector("#status-dot");
const statusText = document.querySelector("#status-text");
const apiVersion = document.querySelector("#api-version");
const copyrightYear = document.querySelector("#copyright-year");
copyrightYear.textContent = String(new Date().getFullYear());
const catalogMeta = document.querySelector("#catalog-meta");
const searchForm = document.querySelector("#catalog-search");
const searchQuery = document.querySelector("#search-query");
const searchGroup = document.querySelector("#search-group");
const searchRarity = document.querySelector("#search-rarity");
const searchEquipment = document.querySelector("#search-equipment");
const searchSlot = document.querySelector("#search-slot");
const highestLevelOnly = document.querySelector("#highest-level-only");
const searchReset = document.querySelector("#search-reset");
const searchStatus = document.querySelector("#search-status");
const searchResults = document.querySelector("#search-results");
const paginationControls = [
  {
    container: document.querySelector("#search-pagination"),
    previous: document.querySelector("#search-previous"),
    next: document.querySelector("#search-next"),
    label: document.querySelector("#search-page-label"),
  },
  {
    container: document.querySelector("#search-pagination-bottom"),
    previous: document.querySelector("#search-previous-bottom"),
    next: document.querySelector("#search-next-bottom"),
    label: document.querySelector("#search-page-label-bottom"),
  },
];
const PAGE_SIZE = 30;
let activeSearchParameters = null;
let currentOffset = 0;
let currentTotal = 0;
let searchPending = false;

const numberFormatter = new Intl.NumberFormat();
const DESCRIPTION_STYLES = {
  n: "default",
  w: "white",
  o: "accent",
};
const PROPERTY_LABELS = {
  characterAttackSpeedModifier: "Attack Speed",
  characterDefensiveAbility: "Defensive Ability",
  characterDexterity: "Cunning",
  characterLife: "Health",
  characterLifeModifier: "Health",
  characterManaRegen: "Energy Regeneration",
  characterOffensiveAbility: "Offensive Ability",
  characterPhysique: "Physique",
  characterSpellCastSpeedModifier: "Cast Speed",
  characterSpirit: "Spirit",
  defensiveAether: "Aether Resistance",
  defensiveBleeding: "Bleeding Resistance",
  defensiveChaos: "Chaos Resistance",
  defensiveCold: "Cold Resistance",
  defensiveElementalResistance: "Elemental Resistance",
  defensiveFire: "Fire Resistance",
  defensiveLife: "Vitality Resistance",
  defensiveLifeMaxResist: "Max Vitality Resistance",
  defensiveLightning: "Lightning Resistance",
  defensivePhysical: "Physical Resistance",
  defensivePierce: "Pierce Resistance",
  defensivePoison: "Poison & Acid Resistance",
  defensiveProtection: "Armor",
  defensiveVitality: "Vitality Resistance",
  offensiveLifeLeechMin: "Attack Damage converted to Health",
  offensivePhysicalMin: "Physical Damage (minimum)",
  offensivePhysicalMax: "Physical Damage (maximum)",
  offensivePhysicalModifier: "Physical Damage",
  offensivePoisonModifier: "Acid Damage",
  offensiveSlowPhysicalModifier: "Internal Trauma Damage",
  offensiveSlowPoisonModifier: "Poison Damage",
  retaliationPoisonMin: "Acid Retaliation",
  skillCooldownReduction: "Recharge Reduction",
};
const RESISTANCE_PROPERTY_KEYS = new Set([
  "defensiveAether",
  "defensiveBleeding",
  "defensiveChaos",
  "defensiveCold",
  "defensiveElementalResistance",
  "defensiveFire",
  "defensiveLife",
  "defensiveLightning",
  "defensivePhysical",
  "defensivePierce",
  "defensivePoison",
  "defensiveVitality",
]);
let nextDetailsId = 0;
let latestSearch = 0;
let equipmentGroupValue = "";

function friendlyLabel(value) {
  return value
    .replaceAll("_", " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^./, (letter) => letter.toUpperCase());
}

function parseDescription(value) {
  if (typeof value !== "string" || value.length === 0) return [];

  const segments = [];
  const tokenPattern = /\^([nwo])/g;
  let style = "default";
  let cursor = 0;
  let match;

  while ((match = tokenPattern.exec(value)) !== null) {
    if (match.index > cursor) {
      segments.push({ text: value.slice(cursor, match.index), style });
    }
    style = DESCRIPTION_STYLES[match[1]];
    cursor = tokenPattern.lastIndex;
  }

  if (cursor < value.length) {
    segments.push({ text: value.slice(cursor), style });
  }
  return segments;
}

function renderDescription(element, segments) {
  segments.forEach((segment) => {
    const span = document.createElement("span");
    const style = ["default", "white", "accent"].includes(segment.style)
      ? segment.style
      : "default";
    span.className = `item-card__description--${style}`;
    span.textContent = segment.text;
    element.append(span);
  });
}

function resultCard(item) {
  const article = document.createElement("article");
  article.className = "result";

  const heading = document.createElement("h3");
  heading.textContent = item.name || `Unlocalized item (${item.id})`;

  const identity = document.createElement("p");
  identity.className = "result__identity";
  identity.textContent = item.id;

  const badges = document.createElement("div");
  badges.className = "result__badges";
  [item.group, item.slot || friendlyLabel(item.category), item.rarity]
    .filter(Boolean)
    .forEach((value) => {
      const badge = document.createElement("span");
      badge.textContent = value;
      badges.append(badge);
    });

  const descriptionSegments = parseDescription(item.description);
  if (descriptionSegments.length > 0) {
    const description = document.createElement("p");
    description.className = "result__description";
    renderDescription(description, descriptionSegments);
    article.append(heading, identity, badges, description);
  } else {
    article.append(heading, identity, badges);
  }

  const level = document.createElement("p");
  level.className = "result__level";
  level.textContent = item.levelRequirement === null
    ? `Item level ${item.itemLevel ?? "—"}`
    : `Requires level ${item.levelRequirement} · Item level ${item.itemLevel ?? "—"}`;
  article.append(level);

  const detailsButton = document.createElement("button");
  detailsButton.className = "result__details-toggle";
  detailsButton.type = "button";
  detailsButton.textContent = "View item details";

  const details = document.createElement("section");
  details.className = "result__details";
  details.id = `item-details-${++nextDetailsId}`;
  details.hidden = true;
  details.setAttribute("aria-label", `Details for ${heading.textContent}`);

  detailsButton.setAttribute("aria-controls", details.id);
  detailsButton.setAttribute("aria-expanded", "false");
  detailsButton.addEventListener("click", () => toggleItemDetails(detailsButton, details, item));

  article.append(detailsButton, details);
  return article;
}

function retaliationLabel(key) {
  // Flat retaliation damage has a different player-facing label from its
  // percentage-based Modifier counterpart. Keep all source values unchanged.
  const match = /^retaliation([A-Z][a-zA-Z]*)(Min|Max)$/.exec(key);
  if (!match) return null;
  const damageType = match[1] === "Poison" ? "Acid" : match[1];
  return `${friendlyLabel(damageType)} Retaliation`;
}

function propertyLabel(property) {
  const retaliation = retaliationLabel(property.key);
  if (retaliation) return retaliation;
  if (typeof property.label === "string" && property.label) return property.label;
  if (property.key === "offensiveSlowPoisonMin"
      && Number.isFinite(property.durationSeconds)) {
    return `Poison Damage over ${numberFormatter.format(property.durationSeconds)} Seconds`;
  }
  return PROPERTY_LABELS[property.key] || friendlyLabel(property.key);
}

function propertyValue(property) {
  const isPercent = property.key !== "defensiveProtection"
    && (property.key.startsWith("defensive") || property.key.endsWith("Modifier")
      || property.key === "skillCooldownReduction"
      || property.key === "offensiveLifeLeechMin");
  const hasRange = Number.isFinite(property.minValue)
    && Number.isFinite(property.maxValue)
    && property.minValue !== property.maxValue;
  const values = hasRange
    ? [property.minValue, property.maxValue]
    : [property.value];
  const includePlus = property.key !== "offensiveFireMin"
    && property.key !== "offensiveLifeLeechMin"
    && property.key !== "offensiveSlowPoisonMin"
    && !property.key.startsWith("retaliation")
    && !RESISTANCE_PROPERTY_KEYS.has(property.key);
  const formatted = values.map((value) => {
    const number = numberFormatter.format(value);
    return value > 0 && includePlus ? `+${number}` : number;
  }).join("/");
  return isPercent ? `${formatted}%` : formatted;
}

function addSectionHeading(parent, text) {
  const heading = document.createElement("h4");
  heading.className = "item-card__heading";
  heading.textContent = text;
  parent.append(heading);
}

function renderItemDetails(card, summaryDescription) {
  const fragment = document.createDocumentFragment();
  const detailDescription = Array.isArray(card.description)
    ? card.description.map((segment) => segment.text).join("")
    : "";

  // The summary already shows the item's flavor text; keep details focused on stats.
  if (Array.isArray(card.description) && card.description.length > 0
      && detailDescription !== summaryDescription) {
    const description = document.createElement("p");
    description.className = "item-card__description";
    renderDescription(description, card.description);
    fragment.append(description);
  }

  if (Array.isArray(card.properties) && card.properties.length > 0) {
    addSectionHeading(fragment, "Properties");
    const list = document.createElement("dl");
    list.className = "item-card__properties";
    card.properties.forEach((property) => {
      const term = document.createElement("dt");
      term.textContent = propertyLabel(property);
      const value = document.createElement("dd");
      value.textContent = propertyValue(property);
      list.append(term, value);
    });
    fragment.append(list);
  }

  if (Array.isArray(card.skillBonuses) && card.skillBonuses.length > 0) {
    addSectionHeading(fragment, "Skill Bonuses");
    const bonuses = document.createElement("ul");
    bonuses.className = "item-card__list";
    card.skillBonuses.forEach((bonus) => {
      const entry = document.createElement("li");
      entry.textContent = `+${numberFormatter.format(bonus.ranks)} to ${bonus.name}`;
      bonuses.append(entry);
    });
    fragment.append(bonuses);
  }

  if (Array.isArray(card.grantedSkills) && card.grantedSkills.length > 0) {
    addSectionHeading(fragment, "Granted Skills");
    const skills = document.createElement("div");
    skills.className = "item-card__skills";
    card.grantedSkills.forEach((skill) => {
      const block = document.createElement("section");
      block.className = "item-card__skill";

      const name = document.createElement("p");
      name.className = "item-card__skill-name";
      name.textContent = skill.trigger
        ? `${skill.name} ${skill.trigger}`
        : skill.name;
      block.append(name);

      if (skill.description) {
        const description = document.createElement("p");
        description.className = "item-card__skill-description";
        description.textContent = skill.description;
        block.append(description);
      }

      const lines = [];
      if (Number.isFinite(skill.rechargeSeconds)) {
        lines.push(`${numberFormatter.format(skill.rechargeSeconds)} Second Skill Recharge`);
      }
      if (Number.isFinite(skill.durationSeconds)) {
        lines.push(`${numberFormatter.format(skill.durationSeconds)} Second Duration`);
      }
      if (Array.isArray(skill.properties)) {
        skill.properties.forEach((property) => {
          lines.push(`${propertyValue(property)} ${propertyLabel(property)}`);
        });
      }
      if (lines.length > 0) {
        const effects = document.createElement("ul");
        effects.className = "item-card__list item-card__skill-effects";
        lines.forEach((line) => {
          const effect = document.createElement("li");
          effect.textContent = line;
          effects.append(effect);
        });
        block.append(effects);
      }
      skills.append(block);
    });
    fragment.append(skills);
  }

  if (Array.isArray(card.conversions) && card.conversions.length > 0) {
    addSectionHeading(fragment, "Conversions");
    const list = document.createElement("ul");
    list.className = "item-card__list";
    card.conversions.forEach((conversion) => {
      const entry = document.createElement("li");
      entry.textContent =
        `${numberFormatter.format(conversion.percentage)}% ${friendlyLabel(conversion.from)} to ${friendlyLabel(conversion.to)}`;
      list.append(entry);
    });
    fragment.append(list);
  }

  if (card.recipe) {
    addSectionHeading(fragment, "Recipe");
    const recipe = document.createElement("div");
    recipe.className = "item-card__recipe";

    const output = document.createElement("p");
    output.textContent =
      `Creates ${card.recipe.outputItemId} × ${numberFormatter.format(card.recipe.outputQuantity)}`;
    recipe.append(output);

    if (card.recipe.craftingCost !== null && card.recipe.craftingCost !== undefined) {
      const cost = document.createElement("p");
      cost.textContent = `Crafting cost: ${numberFormatter.format(card.recipe.craftingCost)} iron`;
      recipe.append(cost);
    }

    if (Array.isArray(card.recipe.ingredients) && card.recipe.ingredients.length > 0) {
      const ingredients = document.createElement("ul");
      card.recipe.ingredients.forEach((ingredient) => {
        const entry = document.createElement("li");
        const alternatives = ingredient.itemIds.join(" or ");
        entry.textContent =
          `${numberFormatter.format(ingredient.quantity)} × ${alternatives}`;
        ingredients.append(entry);
      });
      recipe.append(ingredients);
    }

    fragment.append(recipe);
  }

  if (Array.isArray(card.expansions) && card.expansions.length > 0) {
    const expansions = document.createElement("p");
    expansions.className = "item-card__expansions";
    expansions.textContent = `Expansion data: ${card.expansions.join(", ")}`;
    fragment.append(expansions);
  }

  if (fragment.childNodes.length === 0) {
    const empty = document.createElement("p");
    empty.className = "item-card__empty";
    empty.textContent = "No additional item details are available.";
    fragment.append(empty);
  }

  return fragment;
}

async function toggleItemDetails(button, panel, item) {
  if (panel.dataset.loaded === "true") {
    panel.hidden = !panel.hidden;
    button.setAttribute("aria-expanded", String(!panel.hidden));
    button.textContent = panel.hidden ? "View item details" : "Hide item details";
    return;
  }

  if (panel.dataset.loading === "true") return;

  panel.hidden = false;
  panel.dataset.loading = "true";
  panel.textContent = "Loading item details…";
  button.disabled = true;
  button.textContent = "Loading details…";
  button.setAttribute("aria-expanded", "true");

  try {
    const response = await fetch(
      `/api/grim-dawn/items/${encodeURIComponent(item.id)}/card`,
      { headers: { Accept: "application/json" } },
    );
    if (!response.ok) {
      throw new Error(`Item details returned ${response.status}`);
    }

    const card = await response.json();
    const summaryDescription = parseDescription(item.description)
      .map((segment) => segment.text)
      .join("");
    panel.replaceChildren(renderItemDetails(card, summaryDescription));
    panel.dataset.loaded = "true";
    button.textContent = "Hide item details";
  } catch (error) {
    panel.textContent = "Item details are temporarily unavailable. Try again.";
    button.textContent = "Retry item details";
    console.error("Item details failed", error);
  } finally {
    delete panel.dataset.loading;
    button.disabled = false;
  }
}

function updatePagination() {
  const hasResults = activeSearchParameters !== null && currentTotal > 0;
  const pageCount = Math.ceil(currentTotal / PAGE_SIZE);
  const currentPage = Math.floor(currentOffset / PAGE_SIZE) + 1;

  paginationControls.forEach(({ container, previous, next, label }) => {
    container.hidden = !hasResults || pageCount <= 1;
    previous.disabled = searchPending || !hasResults || currentOffset === 0;
    next.disabled = searchPending || !hasResults || currentOffset + PAGE_SIZE >= currentTotal;
    label.textContent = hasResults
      ? `Page ${numberFormatter.format(currentPage)} of ${numberFormatter.format(pageCount)}`
      : "";
  });
}

function renderResults(payload, offset) {
  searchResults.replaceChildren();
  currentOffset = offset;
  currentTotal = payload.total;

  if (payload.items.length === 0) {
    searchStatus.textContent = "No matching catalog records.";
    updatePagination();
    return;
  }

  const first = offset + 1;
  const last = offset + payload.items.length;
  searchStatus.textContent =
    `Showing ${numberFormatter.format(first)}–${numberFormatter.format(last)} of ${numberFormatter.format(payload.total)} matching records.`;

  const fragment = document.createDocumentFragment();
  payload.items.forEach((item) => fragment.append(resultCard(item)));
  searchResults.append(fragment);
  updatePagination();
}

async function fetchSearchPage(parameters, offset, navigate = false) {
  const searchId = ++latestSearch;
  const request = new URLSearchParams(parameters);
  request.set("limit", String(PAGE_SIZE));
  request.set("offset", String(offset));

  searchPending = true;
  updatePagination();
  searchStatus.textContent = "Searching catalog…";
  searchForm.setAttribute("aria-busy", "true");

  try {
    const response = await fetch(`/api/grim-dawn/items?${request}`, {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error(`Catalog search returned ${response.status}`);
    }
    const payload = await response.json();
    if (searchId !== latestSearch) return;
    renderResults(payload, offset);
    if (navigate) {
      document.querySelector("#search-status").scrollIntoView({ block: "start" });
    }
  } catch (error) {
    if (searchId === latestSearch) {
      searchStatus.textContent = "Catalog search is temporarily unavailable. Try again.";
      console.error("Catalog search failed", error);
    }
  } finally {
    if (searchId === latestSearch) {
      searchPending = false;
      searchForm.removeAttribute("aria-busy");
      updatePagination();
    }
  }
}

function searchCatalog(event) {
  event.preventDefault();
  const parameters = new URLSearchParams();
  const query = searchQuery.value.trim();

  if (query) parameters.set("q", query);
  if (searchGroup.value && !searchEquipment.value) parameters.set("group", searchGroup.value);
  if (searchRarity.value) parameters.set("rarity", searchRarity.value);
  if (searchEquipment.value) parameters.set("group", equipmentGroupValue || "equipment");
  if (searchSlot.value) parameters.set("slot", searchSlot.value);
  if (highestLevelOnly.checked) parameters.set("highestLevelOnly", "true");

  activeSearchParameters = parameters;
  currentOffset = 0;
  currentTotal = 0;
  searchResults.replaceChildren();
  updatePagination();
  fetchSearchPage(parameters, 0);
}

function navigateSearch(direction) {
  if (searchPending || activeSearchParameters === null) return;
  const offset = currentOffset + direction * PAGE_SIZE;
  if (offset < 0 || offset >= currentTotal) return;
  fetchSearchPage(activeSearchParameters, offset, true);
}

function resetSearch() {
  // Invalidate in-flight requests immediately, before the browser resets form fields.
  latestSearch += 1;
  activeSearchParameters = null;
  currentOffset = 0;
  currentTotal = 0;
  searchPending = false;
  searchForm.removeAttribute("aria-busy");
  updatePagination();
  searchResults.replaceChildren();
  searchStatus.textContent = "Enter a name or choose a filter to begin.";
  window.setTimeout(() => {
    searchGroup.disabled = false;
    searchQuery.focus();
  }, 0);
}

async function checkPlatform() {
  try {
    const [healthResponse, apiResponse, catalogResponse] = await Promise.all([
      fetch("/api/health/ready", { headers: { Accept: "application/json" } }),
      fetch("/api", { headers: { Accept: "application/json" } }),
      fetch("/api/grim-dawn/catalog", { headers: { Accept: "application/json" } }),
    ]);

    if (!healthResponse.ok || !catalogResponse.ok) {
      throw new Error("Platform readiness check failed");
    }

    const metadata = apiResponse.ok ? await apiResponse.json() : null;
    const catalog = await catalogResponse.json();

    statusDot.className = "status__dot status__dot--online";
    statusText.textContent = "Platform online";
    apiVersion.textContent = metadata?.version
      ? `API ${metadata.version}`
      : "API online";
    catalogMeta.textContent =
      `Grim Dawn ${catalog.gameVersion} · ${numberFormatter.format(catalog.recordCount)} searchable records`;

    searchSlot.replaceChildren(new Option("All slots", ""));
    Object.entries(catalog.slots || {}).forEach(([slot, count]) => {
      if (!slot) return;
      const option = document.createElement("option");
      option.value = slot;
      option.textContent = `${slot} (${numberFormatter.format(count)})`;
      searchSlot.append(option);
    });

    equipmentGroupValue = Object.keys(catalog.groups).find(
      (group) => group.toLowerCase() === "equipment",
    ) || "";
    searchEquipment.disabled = false;

    Object.entries(catalog.groups).forEach(([group, count]) => {
      const option = document.createElement("option");
      option.value = group;
      option.textContent = `${friendlyLabel(group)} (${numberFormatter.format(count)})`;
      searchGroup.append(option);
    });
    searchEquipment.addEventListener("change", () => {
      if (searchEquipment.value) searchGroup.value = "";
      searchGroup.disabled = Boolean(searchEquipment.value);
    });
  } catch (error) {
    statusDot.className = "status__dot status__dot--offline";
    statusText.textContent = "API not connected";
    apiVersion.textContent = "Web shell online";
    catalogMeta.textContent = "Catalog metadata unavailable.";
    searchStatus.textContent = "Catalog search is temporarily unavailable.";
    console.error("Platform status check failed", error);
  }
}

searchForm.addEventListener("submit", searchCatalog);
searchReset.addEventListener("click", resetSearch);
paginationControls.forEach(({ previous, next }) => {
  previous.addEventListener("click", () => navigateSearch(-1));
  next.addEventListener("click", () => navigateSearch(1));
});
checkPlatform();
