const fs = require("fs");
const path = require("path");

const src = path.join(__dirname, "..", "..", "web", "out");
const dest = path.join(__dirname, "..", "ui");

function rmrf(dir) {
  if (!fs.existsSync(dir)) return;
  fs.rmSync(dir, { recursive: true, force: true });
}

function copyDir(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const entry of fs.readdirSync(from, { withFileTypes: true })) {
    const s = path.join(from, entry.name);
    const d = path.join(to, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

if (!fs.existsSync(path.join(src, "index.html"))) {
  console.error("Missing apps/web/out. Run Next export build first.");
  process.exit(1);
}

rmrf(dest);
copyDir(src, dest);
console.log(`Copied UI -> ${dest}`);
