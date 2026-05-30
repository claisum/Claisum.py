// [Claisum] Bootstrap — resources/app/index.js
// Do NOT remove manually; use the Claisum installer to uninstall.
//
// How this works:
//   Electron prefers resources/app/ over resources/app.asar when both exist.
//   We intercept Module._load to patch the electron module BEFORE Discord
//   ever sees it, then register claisum_inject.js as a preload on every
//   session (defaultSession + each partitioned session via browser-window-created).
//   Finally we hand control back to the real Discord app.asar.
'use strict';
const path   = require('path');
const Module = require('module');

const _claisumPreload = path.join(__dirname, 'claisum_inject.js');

// ── Intercept electron before Discord loads it ────────────────────────────
const _origLoad = Module._load;
Module._load = function(request, parent, isMain) {
  const result = _origLoad.apply(this, arguments);
  if (request !== 'electron' || result.__claisumPatched) return result;
  result.__claisumPatched = true;

  const { app } = result;

  // Add our preload to a session (idempotent)
  function _addToSession(ses) {
    try {
      if (!ses || !ses.setPreloads) return;
      const list = (ses.getPreloads ? ses.getPreloads() : [])
        .filter(function(p) { return p !== _claisumPreload; });
      ses.setPreloads([_claisumPreload].concat(list));
    } catch(e) {}
  }

  // Register on defaultSession once app is ready
  function _onReady() {
    try { _addToSession(result.session.defaultSession); } catch(e) {}
  }
  if (app.isReady()) { _onReady(); }
  else { app.once('ready', _onReady); }

  // Also patch every new window's session to cover partitioned sessions
  // (Discord uses partitioned sessions for some windows in newer versions)
  app.on('browser-window-created', function(_, win) {
    try { _addToSession(win.webContents.session); } catch(e) {}
    // Fallback: if setPreloads didn't work, try executeJavaScript after load
    win.webContents.on('did-finish-load', function() {
      try {
        win.webContents.executeJavaScript(
          'if(!window.__claisumLoaded){try{require("' +
          _claisumPreload.replace(/\\/g, '\\\\') +
          '")}catch(e){}}'
        ).catch(function(){});
      } catch(e) {}
    });
  });

  return result;
};

// ── Hand control to the real Discord ─────────────────────────────────────
require(path.join(__dirname, '..', 'app.asar'));
