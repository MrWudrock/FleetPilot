const fs = require("fs");
const http = require("http");
const path = require("path");
const { app, BrowserWindow, ipcMain, shell, Menu } = require("electron");

const {
  DEFAULT_API_URL,
  getConfig,
  setApiUrl,
  getConfigPath,
} = require("./config");

/** @type {import('http').Server | null} */
let uiServer = null;
/** @type {BrowserWindow | null} */
let mainWindow = null;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".txt": "text/plain; charset=utf-8",
  ".map": "application/json",
};

function uiRoot() {
  if (app.isPackaged) {
    return path.join(__dirname, "..", "ui");
  }
  const packagedUi = path.join(__dirname, "..", "ui");
  if (fs.existsSync(path.join(packagedUi, "index.html"))) {
    return packagedUi;
  }
  return path.join(__dirname, "..", "..", "web", "out");
}

function isPathInside(rootDir, candidate) {
  const root = path.resolve(rootDir);
  const resolved = path.resolve(candidate);
  const rel = path.relative(root, resolved);
  return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
}

function startUiServer(rootDir) {
  return new Promise((resolve, reject) => {
    const root = path.resolve(rootDir);
    const server = http.createServer((req, res) => {
      try {
        const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
        let rel = urlPath === "/" ? "index.html" : urlPath.replace(/^\/+/, "");
        let filePath = path.resolve(root, rel);
        if (!isPathInside(root, filePath)) {
          res.writeHead(403);
          res.end("Forbidden");
          return;
        }
        if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
          // SPA / Next static export fallback
          filePath = path.join(root, "index.html");
          // Prefer path/index.html for Next export routes
          const candidate = path.join(root, rel, "index.html");
          if (fs.existsSync(candidate) && isPathInside(root, candidate)) {
            filePath = candidate;
          } else {
            const htmlCandidate = path.join(root, `${rel.replace(/\/$/, "")}.html`);
            if (fs.existsSync(htmlCandidate) && isPathInside(root, htmlCandidate)) {
              filePath = htmlCandidate;
            }
          }
        }
        if (!isPathInside(root, filePath)) {
          res.writeHead(403);
          res.end("Forbidden");
          return;
        }
        const ext = path.extname(filePath).toLowerCase();
        const data = fs.readFileSync(filePath);
        res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
        res.end(data);
      } catch (err) {
        res.writeHead(404);
        res.end("Not found");
      }
    });

    server.listen(0, "127.0.0.1", () => {
      const addr = server.address();
      if (!addr || typeof addr === "string") {
        reject(new Error("Failed to bind UI server"));
        return;
      }
      resolve({ server, port: addr.port });
    });
    server.on("error", reject);
  });
}

function createMenu() {
  const template = [
    {
      label: "Файл",
      submenu: [
        {
          label: "Открыть конфиг",
          click: () => shell.showItemInFolder(getConfigPath()),
        },
        { type: "separator" },
        { role: "quit", label: "Выход" },
      ],
    },
    {
      label: "Вид",
      submenu: [
        { role: "reload", label: "Обновить" },
        { role: "toggleDevTools", label: "DevTools" },
        { type: "separator" },
        { role: "resetZoom", label: "Сброс масштаба" },
        { role: "zoomIn", label: "Крупнее" },
        { role: "zoomOut", label: "Мельче" },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

async function createWindow() {
  const root = uiRoot();
  if (!fs.existsSync(path.join(root, "index.html"))) {
    console.error("UI not found at", root);
    console.error("Run: npm run build:web");
  }

  const { server, port } = await startUiServer(root);
  uiServer = server;

  mainWindow = new BrowserWindow({
    width: 1360,
    height: 860,
    minWidth: 1024,
    minHeight: 680,
    title: "FleetPilot",
    backgroundColor: "#09090b",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  await mainWindow.loadURL(`http://127.0.0.1:${port}/login`);

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function registerIpc() {
  ipcMain.on("fleetpilot:get-config-sync", (event) => {
    const cfg = getConfig();
    event.returnValue = { ...cfg, version: app.getVersion() };
  });
  ipcMain.handle("fleetpilot:get-config", () => getConfig());
  ipcMain.handle("fleetpilot:set-api-url", (_event, apiUrl) => {
    const next = setApiUrl(String(apiUrl || ""));
    if (mainWindow && !mainWindow.isDestroyed()) {
      const safe = {
        apiUrl: next.apiUrl,
        isDesktop: true,
      };
      mainWindow.webContents.executeJavaScript(
        `window.__FLEETPILOT__ = Object.assign({}, window.__FLEETPILOT__ || {}, ${JSON.stringify(safe)});`,
      );
    }
    return next;
  });
  ipcMain.handle("fleetpilot:get-defaults", () => ({
    defaultApiUrl: DEFAULT_API_URL,
    configPath: getConfigPath(),
  }));
}

app.whenReady().then(async () => {
  createMenu();
  registerIpc();
  await createWindow();

  app.on("activate", async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (uiServer) {
    uiServer.close();
    uiServer = null;
  }
  if (process.platform !== "darwin") {
    app.quit();
  }
});
