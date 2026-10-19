const statusDot = document.querySelector("#status-dot");
const statusText = document.querySelector("#status-text");
const apiVersion = document.querySelector("#api-version");
const catalogMeta = document.querySelector("#catalog-meta");
const searchForm = document.querySelector("#catalog-search");
const searchQuery = document.querySelector("#search-query");
const searchGroup = document.querySelector("#search-group");
const searchRarity = document.querySelector("#search-rarity");
const searchReset = document.querySelector("#search-reset");
const searchStatus = document.querySelector("#search-status");
const searchResults = document.querySelector("#search-results");

const numberFormatter = new Intl.NumberFormat();

function friendlyLabel(value) {
  return value
    .replaceAll("_", " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^./, (letter) => letter.toUpperCase());
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

  const description = document.createElement("p");
  description.className = "result__description";
  description.textContent = item.description || "No localized description.";

  const level = document.createElement("p");
  level.className = "result__level";
  level.textContent = item.levelRequirement === null
    ? `Item level ${item.itemLevel ?? "—"}`
    : `Requires level ${item.levelRequirement} · Item level ${item.itemLevel ?? "—"}`;

  article.append(heading, identity, badges, description, level);
  return article;
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
  const parameters = new URLSearchParams();
  const query = searchQuery.value.trim();

  if (query) parameters.set("q", query);
  if (searchGroup.value) parameters.set("group", searchGroup.value);
  if (searchRarity.value) parameters.set("rarity", searchRarity.value);
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
    renderResults(await response.json());
  } catch (error) {
    searchStatus.textContent = "Catalog search is temporarily unavailable.";
    console.error("Catalog search failed", error);
  } finally {
    searchForm.removeAttribute("aria-busy");
  }
}

function resetSearch() {
  window.setTimeout(() => {
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
