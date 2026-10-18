const statusDot = document.querySelector("#status-dot");
const statusText = document.querySelector("#status-text");
const apiVersion = document.querySelector("#api-version");

async function checkPlatform() {
  try {
    const healthResponse = await fetch("/api/health/ready", {
      headers: { Accept: "application/json" },
    });

    if (!healthResponse.ok) {
      throw new Error(`Health check returned ${healthResponse.status}`);
    }

    const apiResponse = await fetch("/api", {
      headers: { Accept: "application/json" },
    });
    const metadata = apiResponse.ok ? await apiResponse.json() : null;

    statusDot.className = "status__dot status__dot--online";
    statusText.textContent = "Platform online";
    apiVersion.textContent = metadata?.version
      ? `API ${metadata.version}`
      : "API online";
  } catch (error) {
    statusDot.className = "status__dot status__dot--offline";
    statusText.textContent = "API not connected";
    apiVersion.textContent = "Web shell online";
    console.error("Platform status check failed", error);
  }
}

checkPlatform();
