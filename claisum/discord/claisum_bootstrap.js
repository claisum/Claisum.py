// [Claisum] Bootstrap — resources/app/index.js
// Do NOT remove manually; use the Claisum installer to uninstall.
//
// How this works:
//   Electron loads resources/app/index.js before resources/app.asar.
//   Critical: we must call app.setAppPath() pointing at app.asar so Discord's
//   own code sees the right base path when it calls app.getAppPath().
//   Then we register claisum_inject.js as a preload via session.setPreloads()
//   and hand control to the real Discord asar.
'use strict';
const path   = require('path');
const Module = require('module');

// Grab electron without the cache entry pointing at our resources/app dir
const electron = require('electron');
const { app }  = electron;

const _asarPath     = path.join(__dirname, '..', 'app.asar');
const _claisumPreload = path.join(__dirname, 'claisum_inject.js');

// ── 1. Fix Discord's app path so app.getAppPath() returns app.asar, not us ──
app.setAppPath(_asarPath);

// ── 2. Register claisum_inject.js as a renderer preload ────────────────────
function _installPreload() {
  try {
    const sess = electron.session && electron.session.defaultSession;
    if (!sess) return;
    const existing = typeof sess.getPreloads === 'function' ? sess.getPreloads() : [];
    if (existing.indexOf(_claisumPreload) < 0) {
      if (typeof sess.setPreloads === 'function') {
        sess.setPreloads(existing.concat([_claisumPreload]));
      }
    }
  } catch (e) {
    console.error('[Claisum] preload registration failed:', e);
  }
}

if (app.isReady()) {
  _installPreload();
} else {
  app.once('ready', _installPreload);
}

// ── 3. Boot the real Discord ────────────────────────────────────────────────
// Make Module._resolveFilename resolve paths relative to app.asar, not our dir
const _realMain = require.resolve(path.join(_asarPath, 'index.js'));
Module._load(_realMain, null, true);
