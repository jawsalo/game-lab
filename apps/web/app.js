const statusDot = document.querySelector("#status-dot");
const statusText = document.querySelector("#status-text");
const apiVersion = document.querySelector("#api-version");
const catalogMeta = document.querySelector("#catalog-meta");
const searchForm = document.querySelector("#catalog-search");
const searchQuery = document.querySelector("#search-query");
const searchGroup = document.querySelector("#search-group");
const searchRarity = document.querySelector("#search-rarity");
const highestLevelOnly = document.querySelector("#highest-level-only");
const searchReset = document.querySelector("#search-reset");
const searchStatus = document.querySelector("#search-status");
const searchResults = document.querySelector("#search-results");

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
  characterSpellCastSpeedModifier: "Cast Speed",
  defensiveLife: "Health",
  defensiveProtection: "Armor",
  offensivePhysicalMin: "Physical Damage (minimum)",
  offensivePhysicalMax: "Physical Damage (maximum)",
  skillCooldownReduction: "Recharge Reduction",
};
let nextDetailsId = 0;
let latestSearch = 0;

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

function propertyLabel(property) {
  return PROPERTY_LABELS[property.key] || friendlyLabel(property.key);
}

function propertyValue(property) {
  const value = numberFormatter.format(property.value);
  const signedValue = property.value > 0 ? `+${value}` : value;
  const isPercent = property.key !== "defensiveProtection"
    && (property.key.startsWith("defensive") || property.key.endsWith("Modifier")
      || property.key === "skillCooldownReduction");
  return isPercent ? `${signedValue}%` : signedValue;
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

function renderResults(payload) {
  searchResults.replaceChildren();

  if (payload.items.length === 0) {
    searchStatus.textContent = "No matching catalog records.";
    return;
  }

  const shown = payload.items.length;
  searchStatus.textContent =
    `Showing ${numberFormatter.format(shown)} of ${numberFormatter.format(payload.total)} matching records.`;

  const fragment = document.createDocumentFragment();
  payload.items.forEach((item) => fragment.append(resultCard(item)));
  searchResults.append(fragment);
}

async function searchCatalog(event) {
  event.preventDefault();
  const searchId = ++latestSearch;
  const parameters = new URLSearchParams();
  const query = searchQuery.value.trim();

  if (query) parameters.set("q", query);
  if (searchGroup.value) parameters.set("group", searchGroup.value);
  if (searchRarity.value) parameters.set("rarity", searchRarity.value);
  if (highestLevelOnly.checked) parameters.set("highestLevelOnly", "true");
  parameters.set("limit", "30");

  searchStatus.textContent = "Searching catalog…";
  searchResults.replaceChildren();
  searchForm.setAttribute("aria-busy", "true");

  try {
    const response = await fetch(`/api/grim-dawn/items?${parameters}`, {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error(`Catalog search returned ${response.status}`);
    }
    const payload = await response.json();
    if (searchId === latestSearch) renderResults(payload);
  } catch (error) {
    if (searchId === latestSearch) {
      searchStatus.textContent = "Catalog search is temporarily unavailable.";
      console.error("Catalog search failed", error);
    }
  } finally {
    if (searchId === latestSearch) searchForm.removeAttribute("aria-busy");
  }
}

function resetSearch() {
  window.setTimeout(() => {
    latestSearch += 1;
    searchResults.replaceChildren();
    searchStatus.textContent = "Enter a name or choose a filter to begin.";
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

    Object.entries(catalog.groups).forEach(([group, count]) => {
      const option = document.createElement("option");
      option.value = group;
      option.textContent = `${friendlyLabel(group)} (${numberFormatter.format(count)})`;
      searchGroup.append(option);
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
checkPlatform();
