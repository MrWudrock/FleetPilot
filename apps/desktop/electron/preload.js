const { contextBridge, ipcRenderer } = require("electron");

const initial = ipcRenderer.sendSync("fleetpilot:get-config-sync");

contextBridge.exposeInMainWorld("__FLEETPILOT__", {
  apiUrl: initial.apiUrl,
  isDesktop: true,
  version: initial.version || "0.1.0",
});

contextBridge.exposeInMainWorld("fleetpilotDesktop", {
  isDesktop: true,
  getConfig: () => ipcRenderer.invoke("fleetpilot:get-config"),
  setApiUrl: (apiUrl) => ipcRenderer.invoke("fleetpilot:set-api-url", apiUrl),
  getDefaults: () => ipcRenderer.invoke("fleetpilot:get-defaults"),
});
