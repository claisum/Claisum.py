// [Claisum] Bootstrap — resources/app/index.js
// Do NOT remove manually; use Claisum_Setup.exe to uninstall.
"use strict";

const path = require("path");
const fs   = require("fs");
const os   = require("os");
const electron = require("electron");
const { app }  = electron;

const _asarPath = path.join(__dirname, "..", "app.asar");
const _preload  = path.join(__dirname, "claisum_inject.js");

// === DIAGNOSTIC: write Desktop log so we can verify bootstrap ran ===
try {
  const log =
    "[Claisum] Bootstrap ran: " + new Date().toISOString() + "\n" +
    "  asarPath   : " + _asarPath + "\n" +
    "  preload    : " + _preload  + "\n" +
    "  asar exists: " + fs.existsSync(_asarPath) + "\n" +
    "  our app dir: " + __dirname + "\n";
  fs.writeFileSync(path.join(os.homedir(), "Desktop", "claisum_MAIN.txt"), log);
} catch (_) {}

// 1. Fix app.getAppPath() so Discord finds its own files
app.setAppPath(_asarPath);

// 2. Patch BrowserWindow BEFORE Discord loads so our preload is in every window.
//    More reliable than session.setPreloads() — works for all sessions/partitions.
const _OrigBW = electron.BrowserWindow;

class _ClaisumBW extends _OrigBW {
  constructor(opts) {
    opts = Object.assign({}, opts || {});
    const wp = Object.assign({}, opts.webPreferences || {});
    // Store Discord's original preload so inject.js can chain it
    const origPreload = wp.preload || "";
    wp.additionalArguments = [
      ...(wp.additionalArguments || []),
      origPreload ? "--claisum-orig-preload=" + origPreload : ""
    ].filter(Boolean);
    wp.preload = _preload;
    opts.webPreferences = wp;
    super(opts);
  }
}

// Expose patched BrowserWindow to all subsequent require("electron") calls
require.cache[require.resolve("electron")].exports = Object.assign(
  {}, electron, { BrowserWindow: _ClaisumBW }
);

// 3. Load the real Discord (app.getAppPath() now returns asarPath)
require(path.join(_asarPath, "index.js"));
