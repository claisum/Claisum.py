// Claisum — Discord Injection v2
// Robust: floating button always visible + Settings sidebar tabs

(function() {
  'use strict';
  if (window.__claisumLoaded) return;
  window.__claisumLoaded = true;

  const ACCENT = '#7c6af7', BG = '#1e1e2e', BG2 = '#181825', BG3 = '#313244';
  const TEXT = '#cdd6f4', DIM = '#6c7086', OK = '#a6e3a1', ERR = '#f38ba8';

  // ── Persist state ─────────────────────────────────────────────────────────
  let activeTheme    = localStorage.getItem('cl_theme') || null;
  let enabledPlugins = JSON.parse(localStorage.getItem('cl_plugins') || '[]');
  let customThemes   = JSON.parse(localStorage.getItem('cl_cthemes') || '[]');
  let customPluginsRaw = JSON.parse(localStorage.getItem('cl_cplugins') || '[]');
  let currentTab     = 'themes';

  // ── Built-in themes ───────────────────────────────────────────────────────
  const THEMES = [
    { id:'midnight', name:'Midnight', author:'Claisum', preview:'#0d0f12',
      desc:'Deep dark with blue accents',
      css:':root{--background-primary:#0d0f12;--background-secondary:#101316;--background-tertiary:#08090b;--background-accent:#1a1d24;--channeltextarea-background:#1a1d24;--text-normal:#dcddde;--text-muted:#72767d;--header-primary:#ffffff;--interactive-normal:#b9bbbe;}' },
    { id:'dracula', name:'Dracula', author:'Claisum', preview:'#282a36',
      desc:'Classic Dracula color scheme',
      css:':root{--background-primary:#282a36;--background-secondary:#21222c;--background-tertiary:#191a21;--background-accent:#44475a;--channeltextarea-background:#44475a;--text-normal:#f8f8f2;--text-muted:#6272a4;--header-primary:#f8f8f2;--header-secondary:#bd93f9;}' },
    { id:'catppuccin', name:'Catppuccin Mocha', author:'Claisum', preview:'#1e1e2e',
      desc:'Soothing pastel Mocha theme',
      css:':root{--background-primary:#1e1e2e;--background-secondary:#181825;--background-tertiary:#11111b;--background-accent:#313244;--channeltextarea-background:#313244;--text-normal:#cdd6f4;--text-muted:#6c7086;--header-primary:#cdd6f4;--interactive-hover:#b4befe;}' },
    { id:'nord', name:'Nord', author:'Claisum', preview:'#2e3440',
      desc:'Arctic north-bluish theme',
      css:':root{--background-primary:#2e3440;--background-secondary:#272c36;--background-tertiary:#1e2229;--background-accent:#3b4252;--channeltextarea-background:#3b4252;--text-normal:#d8dee9;--text-muted:#4c566a;--header-primary:#eceff4;}' },
    { id:'rose-pine', name:'Rose Pine', author:'Claisum', preview:'#191724',
      desc:'Natural pine and soho vibes',
      css:':root{--background-primary:#191724;--background-secondary:#1f1d2e;--background-tertiary:#191724;--background-accent:#26233a;--channeltextarea-background:#26233a;--text-normal:#e0def4;--text-muted:#6e6a86;--header-primary:#e0def4;}' },
  ];

  // ── Built-in plugins ──────────────────────────────────────────────────────
  const PLUGINS = [
    { id:'compact', name:'Compact Mode', author:'Claisum', desc:'Reduces message spacing',
      on:()=>injectCSS('cl-compact','[class*="message-"]{margin-bottom:2px!important;padding:2px 0!important;}'),
      off:()=>removeCSS('cl-compact') },
    { id:'no-nitro', name:'Hide Nitro Upsells', author:'Claisum', desc:'Removes Nitro ads and banners',
      on:()=>injectCSS('cl-nonitro','[class*="upsell"],[class*="nitroUpsell"],[class*="premiumBanner"],[class*="upsellContainer"]{display:none!important;}'),
      off:()=>removeCSS('cl-nonitro') },
    { id:'big-emoji', name:'Bigger Emojis', author:'Claisum', desc:'Makes emojis larger',
      on:()=>injectCSS('cl-emoji','[class*="emoji"]{width:2em!important;height:2em!important;}'),
      off:()=>removeCSS('cl-emoji') },
    { id:'timestamps', name:'Always Show Timestamps', author:'Claisum', desc:'Full timestamps on every message',
      on:()=>injectCSS('cl-ts','[class*="timestamp-"],[class*="timestampVisibleOnHover-"]{opacity:1!important;display:inline!important;}'),
      off:()=>removeCSS('cl-ts') },
    { id:'no-activities', name:'Hide Activities Tab', author:'Claisum', desc:'Hides the activity tab',
      on:()=>injectCSS('cl-act','[aria-label="Activity"]{display:none!important;}'),
      off:()=>removeCSS('cl-act') },
  ];

  function injectCSS(id, css) {
    removeCSS(id);
    const s = document.createElement('style'); s.id = id; s.textContent = css;
    document.head.appendChild(s);
  }
  function removeCSS(id) { document.getElementById(id)?.remove(); }

  function applyTheme(id) {
    removeCSS('cl-theme');
    const all = [...THEMES, ...customThemes];
    const t = all.find(x => x.id === id); if (!t) return;
    injectCSS('cl-theme', t.css);
    activeTheme = id; localStorage.setItem('cl_theme', id);
  }
  function removeTheme() { removeCSS('cl-theme'); activeTheme = null; localStorage.removeItem('cl_theme'); }

  function getPlugin(id) {
    const builtIn = PLUGINS.find(p => p.id === id);
    if (builtIn) return builtIn;
    const custom = customPluginsRaw.find(p => p.id === id);
    if (custom) return { ...custom,
      on: () => { try { new Function(custom.code)(); } catch(e) { console.error('[Claisum]', e); } },
      off: () => removeCSS('cl-cp-' + custom.id)
    };
    return null;
  }
  function enablePlugin(id) {
    if (enabledPlugins.includes(id)) return;
    const p = getPlugin(id); if (!p) return;
    p.on(); enabledPlugins.push(id); localStorage.setItem('cl_plugins', JSON.stringify(enabledPlugins));
  }
  function disablePlugin(id) {
    const p = getPlugin(id); if (p) p.off();
    enabledPlugins = enabledPlugins.filter(x => x !== id);
    localStorage.setItem('cl_plugins', JSON.stringify(enabledPlugins));
  }

  // ── Restore on load ───────────────────────────────────────────────────────
  if (activeTheme) applyTheme(activeTheme);
  enabledPlugins.slice().forEach(id => enablePlugin(id));

  // ── Global styles ─────────────────────────────────────────────────────────
  injectCSS('cl-ui', `
    #cl-fab{position:fixed;bottom:20px;left:72px;width:40px;height:40px;background:${ACCENT};
      border-radius:50%;cursor:pointer;z-index:9999;display:flex;align-items:center;
      justify-content:center;font-size:18px;box-shadow:0 2px 10px rgba(0,0,0,.4);
      transition:transform .15s,opacity .15s;user-select:none;}
    #cl-fab:hover{transform:scale(1.1);}
    #cl-overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:10000;
      display:flex;align-items:center;justify-content:center;}
    #cl-win{background:${BG};border-radius:12px;width:700px;max-width:95vw;
      height:560px;max-height:90vh;display:flex;overflow:hidden;
      box-shadow:0 8px 32px rgba(0,0,0,.6);}
    #cl-sidebar{width:200px;background:${BG2};padding:20px 0;flex-shrink:0;}
    #cl-sidebar .cl-logo{padding:0 16px 16px;color:${ACCENT};font-weight:800;font-size:16px;}
    #cl-sidebar .cl-ver{padding:0 16px 16px;color:${DIM};font-size:11px;margin-top:-12px;}
    #cl-sidebar hr{border:none;border-top:1px solid ${BG3};margin:8px 16px 16px;}
    .cl-stab{padding:9px 16px;cursor:pointer;color:${DIM};font-size:14px;font-weight:500;
      display:flex;align-items:center;gap:8px;border-radius:4px;margin:1px 8px;transition:all .1s;}
    .cl-stab:hover{background:${BG3};color:${TEXT};}
    .cl-stab.on{background:${BG3};color:${ACCENT};font-weight:600;}
    #cl-main{flex:1;overflow-y:auto;padding:28px 28px 20px;}
    #cl-main *{box-sizing:border-box;font-family:"gg sans","Noto Sans",sans-serif;}
    .cl-h{font-size:18px;font-weight:700;color:${TEXT};margin-bottom:4px;}
    .cl-sub{font-size:12px;color:${DIM};margin-bottom:20px;}
    .cl-sec{font-size:11px;font-weight:700;text-transform:uppercase;color:${DIM};
      letter-spacing:.06em;margin:16px 0 10px;}
    .cl-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin-bottom:16px;}
    .cl-card{background:${BG2};border-radius:8px;padding:12px;cursor:pointer;
      border:2px solid transparent;transition:all .15s;position:relative;}
    .cl-card:hover{border-color:${BG3};}
    .cl-card.on{border-color:${ACCENT};}
    .cl-prev{width:100%;height:32px;border-radius:4px;margin-bottom:8px;}
    .cl-cname{font-weight:700;font-size:13px;color:${TEXT};margin-bottom:1px;}
    .cl-auth{font-size:10px;color:${DIM};margin-bottom:4px;}
    .cl-cdesc{font-size:11px;color:${DIM};line-height:1.4;}
    .cl-badge{position:absolute;top:6px;right:6px;background:${ACCENT};color:#fff;
      font-size:9px;font-weight:700;padding:2px 6px;border-radius:8px;}
    .cl-row{display:flex;align-items:center;justify-content:space-between;
      background:${BG2};border-radius:8px;padding:10px 14px;margin-bottom:6px;gap:12px;}
    .cl-row .info .rname{font-weight:700;font-size:13px;color:${TEXT};}
    .cl-row .info .rauth{font-size:10px;color:${DIM};}
    .cl-row .info .rdesc{font-size:11px;color:${DIM};margin-top:2px;}
    .cl-toggle{position:relative;width:36px;height:20px;flex-shrink:0;}
    .cl-toggle input{opacity:0;width:0;height:0;}
    .cl-slider{position:absolute;inset:0;background:${BG3};border-radius:20px;cursor:pointer;transition:.2s;}
    .cl-slider:before{content:"";position:absolute;height:14px;width:14px;left:3px;bottom:3px;
      background:white;border-radius:50%;transition:.2s;}
    .cl-toggle input:checked+.cl-slider{background:${ACCENT};}
    .cl-toggle input:checked+.cl-slider:before{transform:translateX(16px);}
    .cl-acts{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;}
    .cl-btn{display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:4px;
      font-size:13px;font-weight:600;cursor:pointer;border:none;transition:all .15s;}
    .cl-prim{background:${ACCENT};color:#fff;}.cl-prim:hover{background:#6c5ce7;}
    .cl-ghost{background:${BG3};color:${TEXT};}.cl-ghost:hover{background:#45475a;}
    .cl-close{position:absolute;top:16px;right:16px;background:transparent;border:none;
      color:${DIM};font-size:18px;cursor:pointer;padding:4px 8px;border-radius:4px;}
    .cl-close:hover{background:${BG3};color:${TEXT};}
    .cl-modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:10001;
      display:flex;align-items:center;justify-content:center;}
    .cl-modal{background:${BG};border-radius:10px;padding:24px;width:500px;
      max-width:90vw;max-height:80vh;overflow-y:auto;border:1px solid ${BG3};}
    .cl-modal h2{font-size:16px;font-weight:700;color:${TEXT};margin-bottom:4px;}
    .cl-modal p{font-size:12px;color:${DIM};margin-bottom:14px;}
    .cl-lbl{font-size:11px;font-weight:700;text-transform:uppercase;color:${DIM};
      letter-spacing:.06em;margin-bottom:4px;display:block;}
    .cl-inp,.cl-ta{width:100%;background:${BG2};border:1px solid ${BG3};color:${TEXT};
      border-radius:4px;padding:8px 10px;font-size:13px;outline:none;margin-bottom:12px;font-family:inherit;}
    .cl-inp:focus,.cl-ta:focus{border-color:${ACCENT};}
    .cl-ta{min-height:120px;resize:vertical;font-family:monospace;font-size:12px;}
    .cl-mfoot{display:flex;justify-content:flex-end;gap:8px;margin-top:4px;}
    .cl-note{background:${BG2};border:1px solid ${BG3};border-radius:6px;
      padding:12px;font-size:12px;color:${DIM};line-height:1.6;margin-top:8px;}
    .cl-own{background:${BG3};font-size:9px;color:${DIM};padding:1px 5px;border-radius:4px;margin-left:4px;}
    #cl-sidebar .cl-close-side{position:absolute;display:none;}
  `);

  // ── Build panel HTML ──────────────────────────────────────────────────────
  function buildContent() {
    const allThemes  = [...THEMES,  ...customThemes];
    const allPlugins = [...PLUGINS, ...customPluginsRaw.map(p => ({...p, id:p.id, desc:p.description||'Custom plugin'}))];

    if (currentTab === 'themes') {
      const cards = allThemes.map(t => `
        <div class="cl-card ${activeTheme===t.id?'on':''}" onclick="claisumApplyTheme('${t.id}')">
          ${activeTheme===t.id?'<span class="cl-badge">Active</span>':''}
          <div class="cl-prev" style="background:${t.preview||BG2}"></div>
          <div class="cl-cname">${t.name}${t.isCustom?'<span class="cl-own">yours</span>':''}</div>
          <div class="cl-auth">by ${t.author||'Claisum'}</div>
          <div class="cl-cdesc">${t.desc||t.description||''}</div>
        </div>`).join('');
      return `
        <div class="cl-h">🎨 Themes</div>
        <div class="cl-sub">Choose a theme or create your own</div>
        <div class="cl-acts">
          <button class="cl-btn cl-prim" onclick="claisumNewTheme()">+ Create Theme</button>
          ${activeTheme?'<button class="cl-btn cl-ghost" onclick="claisumRemoveTheme()">✕ Remove</button>':''}
        </div>
        <div class="cl-sec">Themes (${allThemes.length})</div>
        <div class="cl-grid">${cards}</div>`;
    } else {
      const rows = allPlugins.map(p => `
        <div class="cl-row">
          <div class="info">
            <div class="rname">${p.name}${p.isCustom?'<span class="cl-own">yours</span>':''}</div>
            <div class="rauth">by ${p.author||'Claisum'}</div>
            <div class="rdesc">${p.desc||p.description||''}</div>
          </div>
          <label class="cl-toggle">
            <input type="checkbox" ${enabledPlugins.includes(p.id)?'checked':''}
              onchange="claisumToggle('${p.id}',this.checked)">
            <span class="cl-slider"></span>
          </label>
        </div>`).join('');
      return `
        <div class="cl-h">🔌 Plugins</div>
        <div class="cl-sub">Enable, disable or create your own plugins</div>
        <div class="cl-acts">
          <button class="cl-btn cl-prim" onclick="claisumNewPlugin()">+ Create Plugin</button>
        </div>
        <div class="cl-sec">Plugins (${allPlugins.length})</div>
        ${rows}`;
    }
  }

  function renderContent() {
    const el = document.getElementById('cl-main');
    if (el) el.innerHTML = buildContent();
  }

  // ── Panel open/close ──────────────────────────────────────────────────────
  window.claisumOpen = function(tab) {
    if (tab) currentTab = tab;
    let ov = document.getElementById('cl-overlay');
    if (ov) { renderContent(); return; }
    ov = document.createElement('div'); ov.id = 'cl-overlay';
    ov.onclick = e => { if (e.target === ov) claisumClose(); };
    ov.innerHTML = `
      <div id="cl-win">
        <div id="cl-sidebar">
          <div class="cl-logo">⚡ Claisum</div>
          <div class="cl-ver">v1.0.0.1</div>
          <hr>
          <div class="cl-stab ${currentTab==='themes'?'on':''}" onclick="claisumTab('themes')">🎨 Themes</div>
          <div class="cl-stab ${currentTab==='plugins'?'on':''}" onclick="claisumTab('plugins')">🔌 Plugins</div>
        </div>
        <div id="cl-main" style="position:relative;">
          <button class="cl-close" onclick="claisumClose()">✕</button>
          ${buildContent()}
        </div>
      </div>`;
    document.body.appendChild(ov);
  };

  window.claisumClose = function() { document.getElementById('cl-overlay')?.remove(); };
  window.claisumTab   = function(t) { currentTab=t; document.querySelectorAll('.cl-stab').forEach(b=>b.classList.remove('on')); document.querySelectorAll('.cl-stab')[t==='themes'?0:1]?.classList.add('on'); renderContent(); };
  window.claisumApplyTheme = function(id) { applyTheme(id); renderContent(); };
  window.claisumRemoveTheme = function() { removeTheme(); renderContent(); };
  window.claisumToggle = function(id, on) { on ? enablePlugin(id) : disablePlugin(id); };

  window.claisumNewTheme = function() { showModal(`
    <h2>🎨 Create Theme</h2>
    <p>Write CSS to change Discord's look. Hit "Save & Publish" to share with others!</p>
    <label class="cl-lbl">Name</label><input class="cl-inp" id="cl-tn" placeholder="My Theme"/>
    <label class="cl-lbl">Description</label><input class="cl-inp" id="cl-td" placeholder="Short description"/>
    <label class="cl-lbl">CSS</label>
    <textarea class="cl-ta" id="cl-tc" placeholder=":root {\n  --background-primary: #1a1b2e;\n  --text-normal: #e2e8f0;\n}"></textarea>
    <div class="cl-mfoot">
      <button class="cl-btn cl-ghost" onclick="claisumCloseModal()">Cancel</button>
      <button class="cl-btn cl-ghost" onclick="claisumSaveTheme(false)">Save</button>
      <button class="cl-btn cl-prim" onclick="claisumSaveTheme(true)">📤 Save & Publish</button>
    </div>`);
  };

  window.claisumSaveTheme = function(pub) {
    const name=document.getElementById('cl-tn')?.value.trim();
    const desc=document.getElementById('cl-td')?.value.trim();
    const css=document.getElementById('cl-tc')?.value.trim();
    if(!name||!css){alert('Please fill in name and CSS.');return;}
    const id=name.toLowerCase().replace(/[^a-z0-9]+/g,'-');
    customThemes=customThemes.filter(t=>t.id!==id);
    customThemes.push({id,name,desc:desc||'Custom theme',author:'You',preview:'#1e1e2e',css,isCustom:true});
    localStorage.setItem('cl_cthemes',JSON.stringify(customThemes));
    claisumCloseModal(); if(pub) claisumPublishInfo(name,'theme'); renderContent();
  };

  window.claisumNewPlugin = function() { showModal(`
    <h2>🔌 Create Plugin</h2>
    <p>Write JavaScript that runs in Discord. Hit "Save & Publish" to share with others!</p>
    <label class="cl-lbl">Name</label><input class="cl-inp" id="cl-pn" placeholder="My Plugin"/>
    <label class="cl-lbl">Description</label><input class="cl-inp" id="cl-pd" placeholder="What does it do?"/>
    <label class="cl-lbl">JavaScript</label>
    <textarea class="cl-ta" id="cl-pc" placeholder="// Example: inject CSS\nconst s=document.createElement('style');\ns.textContent='/* your CSS */';\ndocument.head.appendChild(s);"></textarea>
    <div class="cl-mfoot">
      <button class="cl-btn cl-ghost" onclick="claisumCloseModal()">Cancel</button>
      <button class="cl-btn cl-ghost" onclick="claisumSavePlugin(false)">Save</button>
      <button class="cl-btn cl-prim" onclick="claisumSavePlugin(true)">📤 Save & Publish</button>
    </div>`);
  };

  window.claisumSavePlugin = function(pub) {
    const name=document.getElementById('cl-pn')?.value.trim();
    const desc=document.getElementById('cl-pd')?.value.trim();
    const code=document.getElementById('cl-pc')?.value.trim();
    if(!name||!code){alert('Please fill in name and code.');return;}
    const id=name.toLowerCase().replace(/[^a-z0-9]+/g,'-');
    customPluginsRaw=customPluginsRaw.filter(p=>p.id!==id);
    customPluginsRaw.push({id,name,description:desc||'Custom plugin',author:'You',isCustom:true,code});
    localStorage.setItem('cl_cplugins',JSON.stringify(customPluginsRaw));
    claisumCloseModal(); if(pub) claisumPublishInfo(name,'plugin'); renderContent();
  };

  window.claisumPublishInfo = function(name, type) { showModal(`
    <h2>📤 Publish "${name}"</h2>
    <p>Share your ${type} with the Claisum community for free!</p>
    <div class="cl-note">
      <strong>How to publish:</strong><br><br>
      1. Go to <strong>github.com/claisum/Claisum.py</strong><br>
      2. Click Issues → New Issue<br>
      3. Title: <strong>[${type.toUpperCase()}] ${name}</strong><br>
      4. Paste your ${type==='theme'?'CSS':'JavaScript'} code in the description<br>
      5. Submit — the team will review and add it to the marketplace!
    </div>
    <div class="cl-mfoot">
      <button class="cl-btn cl-ghost" onclick="claisumCloseModal()">Close</button>
      <button class="cl-btn cl-prim" onclick="window.open('https://github.com/claisum/Claisum.py/issues/new','_blank');claisumCloseModal()">Open GitHub →</button>
    </div>`);
  };

  window.claisumCloseModal = function() { document.getElementById('cl-modal-bg')?.remove(); };
  function showModal(html) {
    document.getElementById('cl-modal-bg')?.remove();
    const bg=document.createElement('div'); bg.id='cl-modal-bg'; bg.className='cl-modal-bg';
    bg.innerHTML=`<div class="cl-modal">${html}</div>`;
    bg.onclick=e=>{if(e.target===bg)claisumCloseModal();};
    document.body.appendChild(bg);
  }

  // ── Floating action button ────────────────────────────────────────────────
  function createFAB() {
    if (document.getElementById('cl-fab')) return;
    const fab = document.createElement('div');
    fab.id = 'cl-fab'; fab.title = 'Claisum — Themes & Plugins';
    fab.textContent = '⚡';
    fab.onclick = () => claisumOpen();
    document.body.appendChild(fab);
  }

  // ── Also try to add settings sidebar tabs ─────────────────────────────────
  let sidebarInjected = false;
  function tryInjectSidebar() {
    if (sidebarInjected) return;
    // Try many possible sidebar selectors
    const sidebar =
      document.querySelector('[class*="sidebarRegion-"]') ||
      document.querySelector('[class*="sidebar-"] [role="tablist"]')?.parentElement ||
      document.querySelector('[class*="sidebar-"]');
    if (!sidebar) return;
    if (document.getElementById('cl-stab-themes')) return;

    const makeBtn = (id, icon, label, tab) => {
      const b = document.createElement('div');
      b.id = id; b.className = 'cl-stab';
      b.innerHTML = icon + ' ' + label;
      b.onclick = () => claisumOpen(tab);
      return b;
    };
    sidebar.appendChild(makeBtn('cl-stab-themes', '🎨', 'Themes', 'themes'));
    sidebar.appendChild(makeBtn('cl-stab-plugins', '🔌', 'Plugins', 'plugins'));
    sidebarInjected = true;
  }

  const obs = new MutationObserver(() => {
    createFAB();
    const inSettings = document.querySelector('[class*="sidebarRegion-"]') ||
                       document.querySelector('[class*="standardSidebarView-"]');
    if (!inSettings) sidebarInjected = false;
    else tryInjectSidebar();
  });
  obs.observe(document.body, { childList: true, subtree: true });

  // Initial setup
  setTimeout(createFAB, 1000);
  console.log('[Claisum] Loaded ✓ — click the ⚡ button in Discord to open Themes & Plugins');
})();
