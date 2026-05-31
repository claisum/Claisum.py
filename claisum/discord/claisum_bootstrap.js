// [Claisum] Bootstrap — resources/app/index.js
// Do NOT remove manually; use Claisum_Setup.exe to uninstall.
"use strict";

const path     = require("path");
const electron = require("electron");
const { app }  = electron;

const _asarPath = path.join(__dirname, "..", "app.asar");
const _preload  = path.join(__dirname, "claisum_inject.js");

// 1. Redirect app.getAppPath() back to Discord's real asar BEFORE anything else
app.setAppPath(_asarPath);

// 2. Inject our preload into every renderer via defaultSession
app.once("ready", () => {
  const { session } = require("electron");
  const ds = session.defaultSession;
  ds.setPreloads([_preload, ...ds.getPreloads()]);
});

// 3. Load the real Discord (app.getAppPath() now points at app.asar)
require(path.join(_asarPath, "index.js"));
