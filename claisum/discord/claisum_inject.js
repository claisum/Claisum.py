// Claisum — Discord Settings Injection
// Adds "Plugins" and "Themes" tabs to Discord Settings
// Automatically injected by Claisum Setup

(function() {
  'use strict';

  const ACCENT   = '#7c6af7';
  const BG       = '#1e1e2e';
  const BG2      = '#181825';
  const BG3      = '#313244';
  const TEXT     = '#cdd6f4';
  const DIM      = '#6c7086';
  const OK       = '#a6e3a1';
  const ERR      = '#f38ba8';

  const STORAGE_THEMES  = 'claisum_enabled_theme';
  const STORAGE_PLUGINS = 'claisum_enabled_plugins';

  const BUILTIN_THEMES = [
    { id:'midnight', name:'Midnight', author:'Claisum',
      description:'Deep dark theme with blue accents', preview:'#0d0f12',
      css:`:root{--background-primary:#0d0f12;--background-secondary:#101316;
      --background-tertiary:#08090b;--background-accent:#1a1d24;
      --channeltextarea-background:#1a1d24;--text-normal:#dcddde;
      --text-muted:#72767d;--header-primary:#ffffff;}` },
    { id:'dracula', name:'Dracula', author:'Claisum',
      description:'The classic Dracula color scheme', preview:'#282a36',
      css:`:root{--background-primary:#282a36;--background-secondary:#21222c;
      --background-tertiary:#191a21;--background-accent:#44475a;
      --channeltextarea-background:#44475a;--text-normal:#f8f8f2;
      --text-muted:#6272a4;--header-primary:#f8f8f2;--header-secondary:#bd93f9;}` },
    { id:'catppuccin', name:'Catppuccin Mocha', author:'Claisum',
      description:'Soothing pastel theme (Mocha variant)', preview:'#1e1e2e',
      css:`:root{--background-primary:#1e1e2e;--background-secondary:#181825;
      --background-tertiary:#181825;--background-accent:#313244;
      --channeltextarea-background:#313244;--text-normal:#cdd6f4;
      --text-muted:#6c7086;--header-primary:#cdd6f4;}` },
    { id:'nord', name:'Nord', author:'Claisum',
      description:'Arctic, north-bluish clean and elegant', preview:'#2e3440',
      css:`:root{--background-primary:#2e3440;--background-secondary:#272c36;
      --background-tertiary:#1e2229;--background-accent:#3b4252;
      --channeltextarea-background:#3b4252;--text-normal:#d8dee9;
      --text-muted:#4c566a;--header-primary:#eceff4;}` },
    { id:'rose-pine', name:'Rose Pine', author:'Claisum',
      description:'All natural pine, faux fur and soho vibes', preview:'#191724',
      css:`:root{--background-primary:#191724;--background-secondary:#1f1d2e;
      --background-tertiary:#191724;--background-accent:#26233a;
      --channeltextarea-background:#26233a;--text-normal:#e0def4;
      --text-muted:#6e6a86;--header-primary:#e0def4;}` },
  ];

  const BUILTIN_PLUGINS = [
    { id:'compact-mode', name:'Compact Mode', author:'Claisum',
      description:'Reduces message spacing for a denser layout',
      apply:()=>{ const s=document.createElement('style');s.id='clp-compact';
        s.textContent='[class*="message-"]{margin-bottom:2px!important;padding:2px 0!important;}';
        document.head.appendChild(s); },
      remove:()=>document.getElementById('clp-compact')?.remove() },
    { id:'hide-nitro', name:'Hide Nitro Upsells', author:'Claisum',
      description:'Removes Nitro ads and upsell banners from Discord',
      apply:()=>{ const s=document.createElement('style');s.id='clp-nitro';
        s.textContent='[class*="upsell"],[class*="nitroUpsell"],[class*="premiumBanner"]{display:none!important;}';
        document.head.appendChild(s); },
      remove:()=>document.getElementById('clp-nitro')?.remove() },
    { id:'bigger-emojis', name:'Bigger Emojis', author:'Claisum',
      description:'Makes emojis in messages larger and easier to see',
      apply:()=>{ const s=document.createElement('style');s.id='clp-emoji';
        s.textContent='[class*="emoji"]{width:2em!important;height:2em!important;}';
        document.head.appendChild(s); },
      remove:()=>document.getElementById('clp-emoji')?.remove() },
    { id:'timestamps', name:'Always Show Timestamps', author:'Claisum',
      description:'Shows full timestamps on every message at all times',
      apply:()=>{ const s=document.createElement('style');s.id='clp-ts';
        s.textContent='[class*="timestamp-"]{display:inline!important;opacity:1!important;}';
        document.head.appendChild(s); },
      remove:()=>document.getElementById('clp-ts')?.remove() },
    { id:'hide-activities', name:'Hide Activities Tab', author:'Claisum',
      description:'Hides the activity tab from the left sidebar',
      apply:()=>{ const s=document.createElement('style');s.id='clp-act';
        s.textContent='[aria-label="Activity"]{display:none!important;}';
        document.head.appendChild(s); },
      remove:()=>document.getElementById('clp-act')?.remove() },
  ];

  let activeThemeId  = localStorage.getItem(STORAGE_THEMES) || null;
  let enabledPlugins = JSON.parse(localStorage.getItem(STORAGE_PLUGINS) || '[]');
  let customThemes   = JSON.parse(localStorage.getItem('claisum_custom_themes') || '[]');
  let customPluginsRaw = JSON.parse(localStorage.getItem('claisum_custom_plugins_raw') || '[]');
  let currentTab     = 'themes';
  let tabsInjected   = false;

  function applyTheme(id) {
    document.getElementById('claisum-theme-style')?.remove();
    const all = [...BUILTIN_THEMES, ...customThemes];
    const t = all.find(x => x.id === id); if(!t) return;
    const el = document.createElement('style');
    el.id = 'claisum-theme-style'; el.textContent = t.css;
    document.head.appendChild(el);
    activeThemeId = id; localStorage.setItem(STORAGE_THEMES, id);
  }
  function removeTheme() {
    document.getElementById('claisum-theme-style')?.remove();
    activeThemeId = null; localStorage.removeItem(STORAGE_THEMES);
  }
  function getPlugin(id) {
    return [...BUILTIN_PLUGINS, ...customPluginsRaw.map(p => ({
      ...p,
      apply: () => { try { new Function(p.code)(); } catch(e) { console.error('[Claisum plugin]',e); } },
      remove: () => { document.getElementById('clp-'+p.id)?.remove(); }
    }))].find(x => x.id === id);
  }
  function applyPlugin(id) {
    if (enabledPlugins.includes(id)) return;
    const p = getPlugin(id); if(!p) return;
    try { p.apply(); } catch(e) {}
    enabledPlugins.push(id); localStorage.setItem(STORAGE_PLUGINS, JSON.stringify(enabledPlugins));
  }
  function removePlugin(id) {
    const p = getPlugin(id); if(p) { try { p.remove(); } catch(e){} }
    enabledPlugins = enabledPlugins.filter(x=>x!==id);
    localStorage.setItem(STORAGE_PLUGINS, JSON.stringify(enabledPlugins));
  }

  function restoreState() {
    if (activeThemeId) applyTheme(activeThemeId);
    enabledPlugins.slice().forEach(id => applyPlugin(id));
  }

  // ── UI ───────────────────────────────────────────────────────────────────
  const CSS = `
    #cl-panel *{box-sizing:border-box;font-family:"gg sans","Noto Sans",sans-serif;}
    #cl-panel{padding:0;color:${TEXT};}
    .cl-h1{font-size:20px;font-weight:700;color:${TEXT};margin-bottom:4px;}
    .cl-sub{font-size:13px;color:${DIM};margin-bottom:20px;}
    .cl-tabs{display:flex;gap:2px;border-bottom:2px solid ${BG3};margin-bottom:20px;}
    .cl-tab{padding:10px 20px;cursor:pointer;color:${DIM};font-weight:600;font-size:14px;
            border-bottom:2px solid transparent;margin-bottom:-2px;transition:color .15s;}
    .cl-tab:hover{color:${TEXT};}
    .cl-tab.on{color:${ACCENT};border-bottom-color:${ACCENT};}
    .cl-sec{font-size:11px;font-weight:700;text-transform:uppercase;color:${DIM};
            letter-spacing:.06em;margin:16px 0 10px;}
    .cl-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
             gap:10px;margin-bottom:20px;}
    .cl-card{background:${BG2};border-radius:8px;padding:14px;cursor:pointer;
             border:2px solid transparent;transition:all .15s;position:relative;}
    .cl-card:hover{border-color:${BG3};}
    .cl-card.on{border-color:${ACCENT};}
    .cl-prev{width:100%;height:36px;border-radius:4px;margin-bottom:10px;}
    .cl-name{font-weight:700;font-size:14px;color:${TEXT};margin-bottom:2px;}
    .cl-auth{font-size:11px;color:${DIM};margin-bottom:4px;}
    .cl-desc{font-size:12px;color:${DIM};line-height:1.4;}
    .cl-badge{position:absolute;top:8px;right:8px;background:${ACCENT};color:#fff;
              font-size:10px;font-weight:700;padding:2px 7px;border-radius:10px;}
    .cl-row{display:flex;align-items:flex-start;justify-content:space-between;
            background:${BG2};border-radius:8px;padding:12px 14px;margin-bottom:8px;gap:14px;}
    .cl-toggle{position:relative;width:40px;height:22px;flex-shrink:0;margin-top:2px;}
    .cl-toggle input{opacity:0;width:0;height:0;}
    .cl-slider{position:absolute;inset:0;background:${BG3};border-radius:22px;
               cursor:pointer;transition:.2s;}
    .cl-slider:before{content:"";position:absolute;height:16px;width:16px;left:3px;bottom:3px;
                      background:white;border-radius:50%;transition:.2s;}
    .cl-toggle input:checked+.cl-slider{background:${ACCENT};}
    .cl-toggle input:checked+.cl-slider:before{transform:translateX(18px);}
    .cl-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:4px;
            font-size:14px;font-weight:600;cursor:pointer;border:none;transition:all .15s;}
    .cl-prim{background:${ACCENT};color:#fff;}.cl-prim:hover{background:#6c5ce7;}
    .cl-ghost{background:${BG3};color:${TEXT};}.cl-ghost:hover{background:#45475a;}
    .cl-acts{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;}
    .cl-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:100000;
                display:flex;align-items:center;justify-content:center;}
    .cl-modal{background:${BG};border-radius:12px;padding:26px;width:540px;
              max-width:90vw;max-height:80vh;overflow-y:auto;border:1px solid ${BG3};}
    .cl-modal h2{font-size:17px;font-weight:700;color:${TEXT};margin-bottom:4px;}
    .cl-modal p{font-size:13px;color:${DIM};margin-bottom:16px;}
    .cl-lbl{font-size:11px;font-weight:700;text-transform:uppercase;color:${DIM};
            letter-spacing:.06em;margin-bottom:5px;display:block;}
    .cl-inp,.cl-ta{width:100%;background:${BG2};border:1px solid ${BG3};color:${TEXT};
                   border-radius:4px;padding:8px 12px;font-size:14px;outline:none;
                   margin-bottom:14px;font-family:inherit;}
    .cl-inp:focus,.cl-ta:focus{border-color:${ACCENT};}
    .cl-ta{min-height:130px;resize:vertical;font-family:monospace;font-size:12px;}
    .cl-mfoot{display:flex;justify-content:flex-end;gap:8px;margin-top:6px;}
    .cl-note{background:${BG2};border:1px solid ${BG3};border-radius:6px;padding:12px;
             font-size:12px;color:${DIM};line-height:1.6;margin-top:8px;}
    .cl-own{background:${BG3};font-size:10px;color:${DIM};padding:2px 6px;border-radius:4px;}
  `.replace(/${ACCENT}/g,ACCENT).replace(/${BG}/g,BG).replace(/${BG2}/g,BG2)
   .replace(/${BG3}/g,BG3).replace(/${TEXT}/g,TEXT).replace(/${DIM}/g,DIM)
   .replace(/${OK}/g,OK).replace(/${ERR}/g,ERR);

  function ensureStyles() {
    if (!document.getElementById('cl-styles')) {
      const s = document.createElement('style'); s.id='cl-styles';
      s.textContent=CSS; document.head.appendChild(s);
    }
  }

  function buildPanel() {
    ensureStyles();
    const allThemes  = [...BUILTIN_THEMES,  ...customThemes];
    const allPlugins = [...BUILTIN_PLUGINS, ...customPluginsRaw.map(p=>({...p,author:'You',isCustom:true}))];
    const themes = allThemes.map(t=>`
      <div class="cl-card ${activeThemeId===t.id?'on':''}" onclick="claisumApplyTheme('${t.id}')">
        ${activeThemeId===t.id?'<span class="cl-badge">Active</span>':''}
        <div class="cl-prev" style="background:${t.preview||BG2}"></div>
        <div class="cl-name">${t.name}${t.isCustom?' <span class="cl-own">yours</span>':''}</div>
        <div class="cl-auth">by ${t.author||'Claisum'}</div>
        <div class="cl-desc">${t.description}</div>
      </div>`).join('');
    const plugins = allPlugins.map(p=>`
      <div class="cl-row">
        <div>
          <div class="cl-name">${p.name}${p.isCustom?' <span class="cl-own">yours</span>':''}</div>
          <div class="cl-auth">by ${p.author||'Claisum'}</div>
          <div class="cl-desc">${p.description}</div>
        </div>
        <label class="cl-toggle">
          <input type="checkbox" ${enabledPlugins.includes(p.id)?'checked':''}
                 onchange="claisumToggle('${p.id}',this.checked)">
          <span class="cl-slider"></span>
        </label>
      </div>`).join('');
    return `<div id="cl-panel">
      <div class="cl-h1">Claisum</div>
      <div class="cl-sub">Customize Discord your way — themes, plugins &amp; more</div>
      <div class="cl-tabs">
        <div class="cl-tab ${currentTab==='themes'?'on':''}" onclick="claisumTab('themes')">🎨 Themes</div>
        <div class="cl-tab ${currentTab==='plugins'?'on':''}" onclick="claisumTab('plugins')">🔌 Plugins</div>
      </div>
      ${currentTab==='themes'?`
        <div class="cl-acts">
          <button class="cl-btn cl-prim" onclick="claisumNewTheme()">+ Create Theme</button>
          ${activeThemeId?`<button class="cl-btn cl-ghost" onclick="claisumRemoveTheme()">✕ Remove Theme</button>`:''}
        </div>
        <div class="cl-sec">Themes (${allThemes.length})</div>
        <div class="cl-grid">${themes}</div>
      `:`
        <div class="cl-acts">
          <button class="cl-btn cl-prim" onclick="claisumNewPlugin()">+ Create Plugin</button>
        </div>
        <div class="cl-sec">Plugins (${allPlugins.length})</div>
        ${plugins}
      `}
    </div>`;
  }

  function renderPanel() {
    const el = document.getElementById('cl-content');
    if (el) el.innerHTML = buildPanel();
  }

  // ── Global actions ───────────────────────────────────────────────────────
  window.claisumTab = t => { currentTab=t; renderPanel(); };
  window.claisumApplyTheme = id => { applyTheme(id); renderPanel(); };
  window.claisumRemoveTheme = () => { removeTheme(); renderPanel(); };
  window.claisumToggle = (id, on) => { on ? applyPlugin(id) : removePlugin(id); };

  window.claisumNewTheme = () => showModal(`
    <h2>🎨 Create Theme</h2>
    <p>Write CSS variables to change Discord's look. Click "Save &amp; Publish" to share with others!</p>
    <label class="cl-lbl">Name</label>
    <input class="cl-inp" id="cl-tn" placeholder="My Awesome Theme"/>
    <label class="cl-lbl">Description</label>
    <input class="cl-inp" id="cl-td" placeholder="A short description"/>
    <label class="cl-lbl">CSS</label>
    <textarea class="cl-ta" id="cl-tc" placeholder=":root {
  --background-primary: #1a1b2e;
  --background-secondary: #16213e;
  --text-normal: #e2e8f0;
}"></textarea>
    <div class="cl-mfoot">
      <button class="cl-btn cl-ghost" onclick="claisumCloseModal()">Cancel</button>
      <button class="cl-btn cl-ghost" onclick="claisumSaveTheme(false)">Save</button>
      <button class="cl-btn cl-prim" onclick="claisumSaveTheme(true)">📤 Save &amp; Publish</button>
    </div>`);

  window.claisumSaveTheme = pub => {
    const name=document.getElementById('cl-tn').value.trim();
    const desc=document.getElementById('cl-td').value.trim();
    const css=document.getElementById('cl-tc').value.trim();
    if (!name||!css) { alert('Please fill in name and CSS.'); return; }
    const id=name.toLowerCase().replace(/[^a-z0-9]+/g,'-');
    const t={id,name,description:desc||'Custom theme',author:'You',preview:'#1e1e2e',css,isCustom:true};
    customThemes=customThemes.filter(x=>x.id!==id); customThemes.push(t);
    localStorage.setItem('claisum_custom_themes',JSON.stringify(customThemes));
    claisumCloseModal(); if(pub) claisumPublishInfo(name,'theme'); renderPanel();
  };

  window.claisumNewPlugin = () => showModal(`
    <h2>🔌 Create Plugin</h2>
    <p>Write JavaScript to modify Discord. Your code runs when the plugin is toggled on. Click "Save &amp; Publish" to share!</p>
    <label class="cl-lbl">Name</label>
    <input class="cl-inp" id="cl-pn" placeholder="My Cool Plugin"/>
    <label class="cl-lbl">Description</label>
    <input class="cl-inp" id="cl-pd" placeholder="What does it do?"/>
    <label class="cl-lbl">JavaScript</label>
    <textarea class="cl-ta" id="cl-pc" placeholder="// Inject CSS example:
const style = document.createElement('style');
style.id = 'my-plugin';
style.textContent = 'body { font-size: 16px; }';
document.head.appendChild(style);"></textarea>
    <div class="cl-mfoot">
      <button class="cl-btn cl-ghost" onclick="claisumCloseModal()">Cancel</button>
      <button class="cl-btn cl-ghost" onclick="claisumSavePlugin(false)">Save</button>
      <button class="cl-btn cl-prim" onclick="claisumSavePlugin(true)">📤 Save &amp; Publish</button>
    </div>`);

  window.claisumSavePlugin = pub => {
    const name=document.getElementById('cl-pn').value.trim();
    const desc=document.getElementById('cl-pd').value.trim();
    const code=document.getElementById('cl-pc').value.trim();
    if (!name||!code) { alert('Please fill in name and code.'); return; }
    const id=name.toLowerCase().replace(/[^a-z0-9]+/g,'-');
    const p={id,name,description:desc||'Custom plugin',author:'You',isCustom:true,code};
    customPluginsRaw=customPluginsRaw.filter(x=>x.id!==id); customPluginsRaw.push(p);
    localStorage.setItem('claisum_custom_plugins_raw',JSON.stringify(customPluginsRaw));
    claisumCloseModal(); if(pub) claisumPublishInfo(name,'plugin'); renderPanel();
  };

  window.claisumPublishInfo = (name,type) => showModal(`
    <h2>📤 Publish "${name}"</h2>
    <p>Share your ${type} with the Claisum community for free!</p>
    <div class="cl-note">
      <strong>How to publish:</strong><br><br>
      1. Go to <strong>github.com/claisum/Claisum.py</strong><br>
      2. Click <strong>Issues → New Issue</strong><br>
      3. Title it: <strong>[${type.toUpperCase()}] ${name}</strong><br>
      4. Paste your ${type==='theme'?'CSS':'JavaScript'} code in the description<br>
      5. Submit — the Claisum team will review and add it to the marketplace!
    </div>
    <div class="cl-mfoot">
      <button class="cl-btn cl-ghost" onclick="claisumCloseModal()">Close</button>
      <button class="cl-btn cl-prim"
        onclick="window.open('https://github.com/claisum/Claisum.py/issues/new','_blank');claisumCloseModal()">
        Open GitHub →
      </button>
    </div>`);

  window.claisumCloseModal = () => document.getElementById('cl-overlay')?.remove();

  function showModal(html) {
    document.getElementById('cl-overlay')?.remove();
    const ov=document.createElement('div');
    ov.id='cl-overlay'; ov.className='cl-overlay';
    ov.innerHTML=`<div class="cl-modal">${html}</div>`;
    ov.onclick=e=>{ if(e.target===ov) claisumCloseModal(); };
    document.body.appendChild(ov);
  }

  // ── Settings tab injection ───────────────────────────────────────────────
  function showClaisumPanel() {
    ensureStyles();
    let region = document.querySelector('[class*="contentRegion-"]');
    if (!region) return;
    let panel = document.getElementById('cl-content');
    if (!panel) {
      panel = document.createElement('div'); panel.id='cl-content';
      panel.style.cssText='position:absolute;inset:0;overflow-y:auto;padding:60px 40px 40px;z-index:10;background:var(--background-primary,'+BG+')';
      region.style.position='relative'; region.appendChild(panel);
    }
    panel.style.display='block'; panel.innerHTML=buildPanel();
  }

  function hideClaisumPanel() {
    const p = document.getElementById('cl-content');
    if (p) p.style.display='none';
  }

  function injectTabs() {
    if (tabsInjected) return;
    const sidebar = document.querySelector('[class*="sidebarRegion-"]');
    if (!sidebar) return;
    if (document.getElementById('cl-themes-btn')) return;

    const makeBtn = (id, icon, label, tab) => {
      const btn = document.createElement('div');
      btn.id=id;
      btn.style.cssText='padding:10px 12px;cursor:pointer;color:'+DIM+';font-size:14px;font-weight:500;border-radius:4px;margin:1px 8px;display:flex;align-items:center;gap:8px;transition:all .1s;';
      btn.innerHTML=`<span>${icon}</span><span>${label}</span>`;
      btn.onmouseenter=()=>{ btn.style.background=BG3; btn.style.color=TEXT; };
      btn.onmouseleave=()=>{ btn.style.background=''; btn.style.color=DIM; };
      btn.onclick=()=>{ currentTab=tab; showClaisumPanel(); };
      return btn;
    };

    sidebar.appendChild(makeBtn('cl-themes-btn','🎨','Themes','themes'));
    sidebar.appendChild(makeBtn('cl-plugins-btn','🔌','Plugins','plugins'));
    tabsInjected = true;
    console.log('[Claisum] Tabs injected into Discord Settings');
  }

  const obs = new MutationObserver(() => {
    const inSettings = !!document.querySelector('[class*="standardSidebarView-"]') ||
                       !!document.querySelector('[class*="sidebarRegion-"]');
    if (!inSettings) { tabsInjected=false; hideClaisumPanel(); return; }
    injectTabs();
  });
  obs.observe(document.body,{childList:true,subtree:true});

  restoreState();
  console.log('[Claisum] Ready — open Discord Settings to see Themes & Plugins tabs');
})();
