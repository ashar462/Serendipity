// Receiver + static server for the one-click Figma exporter.
// Serves tools/exporter.html and accepts uploaded export files into figma-export/.
const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const PORT = 4173;
const SECRET = process.env.EXPORT_SECRET || crypto.randomBytes(12).toString("hex");
const ROOT = "/home/user/Serendipity";
const OUT = path.join(ROOT, "figma-export");
const PAGE = path.join(ROOT, "tools", "exporter.html");
fs.mkdirSync(OUT, { recursive: true });

let received = { files: 0, bytes: 0, recent: [] };

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://localhost");
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }

  if (req.method === "GET" && (url.pathname === "/" || url.pathname === "/exporter.html")) {
    let html = fs.readFileSync(PAGE, "utf8");
    try {
      const ft = Buffer.from(fs.readFileSync(path.join(ROOT, "tools", "ft.b64"), "utf8").trim(), "base64").toString("utf8");
      html = html.replace("__FT__", JSON.stringify(ft));
    } catch (e) { console.log("[warn] could not load ft.b64:", e.message); }
    html = html.replace("__SEC__", JSON.stringify(SECRET));
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store, max-age=0" });
    return res.end(html);
  }

  if (req.method === "GET" && url.pathname === "/manifest.json") {
    const p = path.join(ROOT, "figma-export", "manifest.json");
    if (!fs.existsSync(p)) { res.writeHead(404); return res.end("no manifest"); }
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(fs.readFileSync(p));
  }

  if (req.method === "GET" && url.pathname === "/have") {
    const dir = path.join(ROOT, "figma-export", "renders");
    const out = [];
    if (fs.existsSync(dir)) {
      (function walkDir(d) {
        for (const e of fs.readdirSync(d, { withFileTypes: true })) {
          if (e.isDirectory()) walkDir(path.join(d, e.name));
          else out.push("renders/" + path.relative(dir, path.join(d, e.name)).split(path.sep).join("/"));
        }
      })(dir);
    }
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify(out));
  }

  if (req.method === "GET" && url.pathname === "/stats") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify(received));
  }

  if (req.method === "POST" && url.pathname === "/upload") {
    if (url.searchParams.get("s") !== SECRET) { res.writeHead(403); return res.end("bad secret"); }
    let rel = url.searchParams.get("path") || "";
    if (!/^[A-Za-z0-9._\/-]+$/.test(rel) || rel.includes("..") || !rel.startsWith("figma-export/")) {
      res.writeHead(400); return res.end("bad path");
    }
    const chunks = []; let size = 0;
    req.on("data", c => { size += c.length; if (size > 110e6) { res.writeHead(413); res.end("too big"); req.destroy(); } chunks.push(c); });
    req.on("end", () => {
      try {
        const buf = Buffer.concat(chunks);
        const dec = url.searchParams.get("enc") === "b64" ? Buffer.from(buf.toString("utf8"), "base64") : buf;
        const dest = path.join(ROOT, rel);
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.writeFileSync(dest, dec);
        received.files++; received.bytes += dec.length;
        received.recent.unshift(rel + " (" + Math.round(dec.length / 1024) + " KB)");
        received.recent = received.recent.slice(0, 40);
        console.log(`[upload] ${rel} — ${Math.round(dec.length / 1024)} KB (total files: ${received.files})`);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: true, bytes: dec.length }));
      } catch (e) {
        console.log("[upload-error]", rel, e.message);
        res.writeHead(500); res.end(e.message);
      }
    });
    return;
  }

  res.writeHead(404); res.end("not found");
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`export receiver ready on :${PORT} (secret: ${SECRET})`);
});
