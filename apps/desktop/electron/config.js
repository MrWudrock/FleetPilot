const fs = require("fs");
const path = require("path");
const { app } = require("electron");

/** Pilot default — cloud API host is not deployed yet. */
const PILOT_API_URL = "http://localhost:8800";
const LEGACY_CLOUD_HOSTS = new Set([
  "https://api.fleetpilot.ru",
  "http://api.fleetpilot.ru",
]);

const DEFAULT_API_URL = process.env.FLEETPILOT_API_URL || PILOT_API_URL;

function getConfigPath() {
  return path.join(app.getPath("userData"), "config.json");
}

function normalizeApiUrl(url) {
  const cleaned = String(url || DEFAULT_API_URL).trim().replace(/\/$/, "");
  if (!cleaned || LEGACY_CLOUD_HOSTS.has(cleaned)) {
    return PILOT_API_URL;
  }
  let parsed;
  try {
    parsed = new URL(cleaned);
  } catch {
    return PILOT_API_URL;
  }
  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
    return PILOT_API_URL;
  }
  return cleaned;
}

function defaultConfig() {
  return {
    apiUrl: normalizeApiUrl(DEFAULT_API_URL),
  };
}

function writeConfig(cfg) {
  const file = getConfigPath();
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(cfg, null, 2), "utf8");
}

function getConfig() {
  const file = getConfigPath();
  try {
    if (fs.existsSync(file)) {
      const raw = JSON.parse(fs.readFileSync(file, "utf8"));
      const apiUrl = normalizeApiUrl(raw.apiUrl);
      const cfg = {
        ...defaultConfig(),
        ...raw,
        apiUrl,
      };
      // Persist migration away from dead cloud URL
      if (apiUrl !== raw.apiUrl) {
        writeConfig(cfg);
      }
      return cfg;
    }
  } catch {
    // fall through
  }
  const cfg = defaultConfig();
  try {
    writeConfig(cfg);
  } catch {
    // ignore
  }
  return cfg;
}

function setApiUrl(apiUrl) {
  const next = { ...getConfig(), apiUrl: normalizeApiUrl(apiUrl) };
  writeConfig(next);
  return next;
}

module.exports = {
  DEFAULT_API_URL: PILOT_API_URL,
  getConfigPath,
  getConfig,
  setApiUrl,
};
