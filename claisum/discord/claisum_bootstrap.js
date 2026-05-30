// [Claisum] Bootstrap — resources/app/index.js
// Do NOT remove manually; use the Claisum installer to uninstall.
//
// How this works:
//   Electron prefers resources/app/ over resources/app.asar when both exist.
//   We use this to run BEFORE Discord, register claisum_inject.js as a preload
//   for every renderer window, then hand control back to the real Discord asar.
'use strict';
const path = require('path');
const electron = require('electron');

const _claisumPreload = path.join(__dirname, 'claisum_inject.js');

function _installPreload() {
  try {
    const sess = electron.session.defaultSession;
    const list = sess.getPreloads ? sess.getPreloads() : [];
    if (list.indexOf(_claisumPreload) < 0) {
      if (sess.setPreloads) sess.setPreloads(list.concat([_claisumPreload]));
    }
  } catch (e) {
    console.error('[Claisum] preload registration failed:', e);
  }
}

// Register BEFORE Discord so our ready handler fires FIRST
if (electron.app.isReady()) {
  _installPreload();
} else {
  electron.app.once('ready', _installPreload);
}

// Load the real Discord (app.asar is one level up from resources/app/)
require(path.join(__dirname, '..', 'app.asar'));
