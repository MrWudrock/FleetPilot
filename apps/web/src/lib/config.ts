export type FleetPilotRuntime = {
  apiUrl?: string;
  isDesktop?: boolean;
  version?: string;
};

export type FleetPilotDesktopBridge = {
  isDesktop: boolean;
  getConfig: () => Promise<{ apiUrl: string }>;
  setApiUrl: (apiUrl: string) => Promise<{ apiUrl: string }>;
  getDefaults: () => Promise<{ defaultApiUrl: string; configPath: string }>;
};

declare global {
  interface Window {
    __FLEETPILOT__?: FleetPilotRuntime;
    __FLEETPILOT_API_OVERRIDE__?: string;
    fleetpilotDesktop?: FleetPilotDesktopBridge;
  }
}

const FALLBACK_API = "http://localhost:8800";

/** Resolve API base at call-time (Electron injects window.__FLEETPILOT__). */
export function getApiBase(): string {
  if (typeof window !== "undefined") {
    const override = window.__FLEETPILOT_API_OVERRIDE__?.trim();
    if (override) return override.replace(/\/$/, "");
    const fromRuntime = window.__FLEETPILOT__?.apiUrl?.trim();
    if (fromRuntime) return fromRuntime.replace(/\/$/, "");
  }
  const fromEnv = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  return FALLBACK_API;
}

export function isDesktopApp(): boolean {
  if (typeof window === "undefined") return false;
  return Boolean(window.fleetpilotDesktop?.isDesktop || window.__FLEETPILOT__?.isDesktop);
}
