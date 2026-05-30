// Claisum — Discord Injection v7
// Dual-context: auto-detects main vs renderer process and hooks accordingly.
(function () {
  'use strict';

  var VERSION = '1.0.0.1';
  var REPO    = 'claisum/Claisum.py';

  // ── Context detection ────────────────────────────────────────────────────
  // discord_desktop_core/index.js may be required from the MAIN process (no DOM)
  // OR from a preload/renderer (has DOM). Handle both.
  var inRenderer = (
    typeof window !== 'undefined' &&
    typeof document !== 'undefined' &&
    typeof window.document !== 'undefined'
  );

  if (!inRenderer) {
    // ══ MAIN PROCESS PATH ═════════════════════════════════════════════════
    // Register this very file as an extra preload for every Discord renderer
    // window so that the renderer path below runs in full DOM context.
    try {
      var electron = require('electron');
      var thisFile = __filename;           // absolute path to claisum_inject.js

      function _setupPreload() {
        try {
          // session.setPreloads adds our script to every BrowserWindow preload
          var sess = electron.session.defaultSession;
          var list = sess.getPreloads();
          if (list.indexOf(thisFile) === -1) {
            sess.setPreloads(list.concat([thisFile]));
          }
        } catch (_) {
          // Fallback: executeJavaScript after each window finishes loading
          _hookWindows(electron, thisFile);
        }
      }

      var app = electron.app;
      if (app.isReady()) {
        _setupPreload();
      } else {
        app.once('ready', _setupPreload);
      }
    } catch (e) {
      console.error('[Claisum] main-process hook failed:', e);
    }
    return;   // renderer code below is not for main process
  }

  // ══ RENDERER / PRELOAD PATH ═══════════════════════════════════════════════
  if (window.__claisumLoaded) return;
  window.__claisumLoaded = true;

  // ── Storage ──────────────────────────────────────────────────────────────
  function load(k, d) { try { var v = localStorage.getItem(k); return v !== null ? JSON.parse(v) : d; } catch(e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch(e) {} }

  var state = { theme: load('cl_theme', null), plugins: load('cl_plugins', []), tab: 'themes' };

  // ── Palette ───────────────────────────────────────────────────────────────
  var C = { ACC:'#7c6af7', ACC2:'#6254d6', BG:'#1e1e2e', BG2:'#181825', BG3:'#313244', BG4:'#45475a', TXT:'#cdd6f4', DIM:'#6c7086' };

  // ── Data ─────────────────────────────────────────────────────────────────
  var THEMES = [
    { id:'midnight',   name:'Midnight',        preview:'#0d0f12', desc:'Deep dark — blue accents',    css:':root{--background-primary:#0d0f12;--background-secondary:#101316;--background-secondary-alt:#0d0f12;--background-tertiary:#08090b;--channeltextarea-background:#1a1d24;--text-normal:#dcddde;--text-muted:#72767d;--header-primary:#fff;--header-secondary:#b9bbbe;}' },
    { id:'dracula',    name:'Dracula',          preview:'#282a36', desc:'Classic Dracula colors',      css:':root{--background-primary:#282a36;--background-secondary:#21222c;--background-secondary-alt:#1e1f29;--background-tertiary:#191a21;--channeltextarea-background:#44475a;--text-normal:#f8f8f2;--text-muted:#6272a4;--header-primary:#f8f8f2;--header-secondary:#bd93f9;}' },
    { id:'catppuccin', name:'Catppuccin Mocha', preview:'#1e1e2e', desc:'Soothing pastel theme',      css:':root{--background-primary:#1e1e2e;--background-secondary:#181825;--background-secondary-alt:#11111b;--background-tertiary:#181825;--channeltextarea-background:#313244;--text-normal:#cdd6f4;--text-muted:#6c7086;--header-primary:#cdd6f4;--header-secondary:#bac2de;}' },
    { id:'nord',       name:'Nord',             preview:'#2e3440', desc:'Arctic blue palette',         css:':root{--background-primary:#2e3440;--background-secondary:#272c36;--background-secondary-alt:#21262e;--background-tertiary:#1e2229;--channeltextarea-background:#3b4252;--text-normal:#d8dee9;--text-muted:#4c566a;--header-primary:#eceff4;--header-secondary:#e5e9f0;}' },
    { id:'rose-pine',  name:'Rosé Pine',        preview:'#191724', desc:'Pine, rose and gold tones',   css:':root{--background-primary:#191724;--background-secondary:#1f1d2e;--background-secondary-alt:#191724;--background-tertiary:#191724;--channeltextarea-background:#26233a;--text-normal:#e0def4;--text-muted:#6e6a86;--header-primary:#e0def4;--header-secondary:#e0def4;}' },
    { id:'gruvbox',    name:'Gruvbox Dark',     preview:'#282828', desc:'Retro groove scheme',         css:':root{--background-primary:#282828;--background-secondary:#1d2021;--background-secondary-alt:#1a1a1a;--background-tertiary:#141617;--channeltextarea-background:#3c3836;--text-normal:#ebdbb2;--text-muted:#928374;--header-primary:#fbf1c7;--header-secondary:#ebdbb2;}' },
    { id:'solarized',  name:'Solarized Dark',   preview:'#002b36', desc:'Classic Solarized dark',     css:':root{--background-primary:#002b36;--background-secondary:#073642;--background-secondary-alt:#001f27;--background-tertiary:#001f27;--channeltextarea-background:#073642;--text-normal:#839496;--text-muted:#586e75;--header-primary:#93a1a1;--header-secondary:#839496;}' },
  ];

  var PLUGINS = [
    { id:'compact',   name:'Compact Mode',        desc:'Tighter messages — more content visible', css:"[class*='message-']{padding:2px 16px!important;}[class*='contents-']{padding-top:0!important;}" },
    { id:'square',    name:'Square Corners',       desc:'Removes all border-radius',              css:'*{border-radius:0!important;}' },
    { id:'bigemoji',  name:'Big Emoji',            desc:'Enlarges solo emoji to 48px',            css:"[class*='jumboable']{width:48px!important;height:48px!important;}" },
    { id:'nogame',    name:'Hide Game Activity',   desc:'Hides the "playing a game" bar',         css:"[class*='activityStatus'],[class*='gameInfo']{display:none!important;}" },
    { id:'noavatar',  name:'Hide Avatars',         desc:'Removes user avatars',                   css:"[class*='avatar-'],[class*='avatarWrapper']{display:none!important;}" },
  ];

  // ── CSS helpers ──────────────────────────────────────────────────────────
  function applyCSS(id, css) {
    var el = document.getElementById('cl-' + id);
    if (!el) { el = document.createElement('style'); el.id = 'cl-' + id; document.head.appendChild(el); }
    el.textContent = css;
  }
  function removeCSS(id) { var el = document.getElementById('cl-' + id); if (el) el.remove(); }

  // ── DOM helper ───────────────────────────────────────────────────────────
  function mk(tag, style, props) {
    var e = document.createElement(tag);
    if (style) e.style.cssText = style;
    if (props) Object.assign(e, props);
    return e;
  }

  // ── Build UI ─────────────────────────────────────────────────────────────
  var _built = false;
  function buildUI() {
    if (_built) return;
    _built = true;

    // Apply saved theme/plugins immediately
    if (state.theme) { var t = THEMES.find(function(x){return x.id===state.theme;}); if(t) applyCSS('theme', t.css); }
    state.plugins.forEach(function(pid){ var p=PLUGINS.find(function(x){return x.id===pid;}); if(p) applyCSS(pid,p.css); });

    // ── Panel ─────────────────────────────────────────────────────────────
    var panel = mk('div',
      'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);' +
      'width:520px;max-height:580px;background:'+C.BG+';color:'+C.TXT+';' +
      'border-radius:14px;box-shadow:0 16px 56px #000000aa;z-index:2147483646;' +
      'display:none;flex-direction:column;font-family:"Segoe UI",system-ui,sans-serif;overflow:hidden;');

    var ph = mk('div','display:flex;align-items:center;padding:14px 18px;background:'+C.BG2+';border-bottom:1px solid #ffffff12;flex-shrink:0;');
    var pt = mk('span','font-size:15px;font-weight:700;flex:1;',{textContent:'\u26a1 Claisum  v'+VERSION});
    var pc = mk('button','background:none;border:none;color:'+C.DIM+';font-size:22px;cursor:pointer;line-height:1;padding:0 4px;',{textContent:'\u00d7',title:'Close (F8)'});
    pc.onmouseenter=function(){pc.style.color=C.TXT;}; pc.onmouseleave=function(){pc.style.color=C.DIM;};
    pc.onclick=close_; ph.appendChild(pt); ph.appendChild(pc);

    var tb = mk('div','display:flex;background:'+C.BG2+';border-bottom:1px solid #ffffff12;flex-shrink:0;');
    var tabBtns = {};
    ['themes','plugins'].forEach(function(t){
      var b = mk('button','flex:1;padding:10px 0;background:none;border:none;cursor:pointer;font-size:13px;font-weight:600;border-bottom:2px solid transparent;',
        {textContent:t==='themes'?'Themes ('+THEMES.length+')':'Plugins ('+PLUGINS.length+')'});
      b.onclick=function(){switchTab(t);}; tabBtns[t]=b; tb.appendChild(b);
    });

    var pb = mk('div','flex:1;overflow-y:auto;padding:12px 16px;'); pb.style.scrollbarWidth='thin';

    var pf = mk('div','padding:8px 16px;background:'+C.BG2+';border-top:1px solid #ffffff12;font-size:11px;color:'+C.DIM+';display:flex;align-items:center;flex-shrink:0;');
    pf.appendChild(mk('span',null,{textContent:'F8 to toggle \u2022 github.com/'+REPO}));

    panel.appendChild(ph); panel.appendChild(tb); panel.appendChild(pb); panel.appendChild(pf);

    // ── Tab rendering ─────────────────────────────────────────────────────
    function switchTab(tab) {
      state.tab=tab;
      Object.keys(tabBtns).forEach(function(t){
        var on=t===tab;
        tabBtns[t].style.color=on?C.ACC:C.DIM;
        tabBtns[t].style.borderBottom=on?'2px solid '+C.ACC:'2px solid transparent';
      });
      pb.innerHTML='';
      if(tab==='themes') renderThemes(); else renderPlugins();
    }

    function toggle_(on) {
      var tr=mk('div','width:38px;height:22px;border-radius:11px;cursor:pointer;position:relative;flex-shrink:0;background:'+(on?C.ACC:'#3a3a52')+';transition:background .2s;');
      var kn=mk('div','position:absolute;top:3px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 1px 4px #0004;transition:left .18s;left:'+(on?'19px':'3px')+';');
      tr.appendChild(kn); tr.__on=on;
      return tr;
    }
    function setToggle(tr,on,cb){
      tr.__on=on; tr.style.background=on?C.ACC:'#3a3a52';
      var kn=tr.firstChild; if(kn) kn.style.left=on?'19px':'3px';
      if(cb) try{cb(on);}catch(e){}
    }

    function card(children) {
      var c=mk('div','display:flex;align-items:center;padding:10px 12px;margin:4px 0;background:'+C.BG3+';border-radius:10px;gap:10px;border:1px solid transparent;');
      c.onmouseenter=function(){c.style.borderColor='#ffffff18';}; c.onmouseleave=function(){c.style.borderColor='transparent';};
      children.forEach(function(x){c.appendChild(x);}); return c;
    }
    function info_(name, desc) {
      var w=mk('div','flex:1;min-width:0;');
      w.appendChild(mk('div','font-size:13px;font-weight:600;color:'+C.TXT+';',{textContent:name}));
      w.appendChild(mk('div','font-size:11px;color:'+C.DIM+';margin-top:2px;',{textContent:desc}));
      return w;
    }

    function renderThemes() {
      var row=mk('div','margin-bottom:8px;display:flex;justify-content:flex-end;');
      var rb=mk('button','background:none;border:1px solid '+C.DIM+';color:'+C.DIM+';border-radius:6px;padding:4px 12px;cursor:pointer;font-size:11px;',{textContent:'\u21ba Reset theme'});
      rb.onmouseenter=function(){rb.style.borderColor=C.TXT;rb.style.color=C.TXT;}; rb.onmouseleave=function(){rb.style.borderColor=C.DIM;rb.style.color=C.DIM;};
      rb.onclick=function(){
        if(state.theme) removeCSS('theme');
        state.theme=null; save('cl_theme',null);
        document.querySelectorAll('[data-cl-t]').forEach(function(tr){setToggle(tr,false);});
      };
      row.appendChild(rb); pb.appendChild(row);
      THEMES.forEach(function(t){
        var dot=mk('div','width:18px;height:18px;border-radius:50%;flex-shrink:0;background:'+t.preview+';border:2px solid #ffffff20;');
        var tr=toggle_(state.theme===t.id); tr.setAttribute('data-cl-t',t.id);
        tr.onclick=function(){
          var on=!tr.__on;
          if(on){
            if(state.theme&&state.theme!==t.id)removeCSS('theme');
            state.theme=t.id; save('cl_theme',t.id); applyCSS('theme',t.css);
            document.querySelectorAll('[data-cl-t]').forEach(function(x){if(x!==tr)setToggle(x,false);});
          } else { if(state.theme===t.id){state.theme=null;save('cl_theme',null);removeCSS('theme');} }
          setToggle(tr,on);
        };
        pb.appendChild(card([dot,info_(t.name,t.desc),tr]));
      });
    }

    function renderPlugins() {
      PLUGINS.forEach(function(p){
        var isOn=state.plugins.indexOf(p.id)>=0;
        var tr=toggle_(isOn);
        tr.onclick=function(){
          var on=!tr.__on;
          if(on){if(state.plugins.indexOf(p.id)<0)state.plugins.push(p.id);applyCSS(p.id,p.css);}
          else{state.plugins=state.plugins.filter(function(x){return x!==p.id;});removeCSS(p.id);}
          save('cl_plugins',state.plugins); setToggle(tr,on);
        };
        pb.appendChild(card([info_(p.name,p.desc),tr]));
      });
    }

    // ── FAB ──────────────────────────────────────────────────────────────────
    var fab = mk('button',
      'position:fixed;bottom:22px;left:22px;width:46px;height:46px;border-radius:50%;' +
      'background:'+C.ACC+';border:none;cursor:pointer;font-size:20px;' +
      'z-index:2147483647;box-shadow:0 4px 16px #0006,0 0 0 2px #ffffff18;' +
      'transition:transform .15s,box-shadow .15s;user-select:none;',
      {textContent:'\u26a1',title:'Claisum (F8)'});
    fab.onmouseenter=function(){fab.style.transform='scale(1.14)';};
    fab.onmouseleave=function(){fab.style.transform='scale(1)';};
    fab.onclick=toggle_;

    // open / close
    function open_() { panel.style.display='flex'; switchTab(state.tab||'themes'); fab.style.background=C.ACC2; }
    function close_() { panel.style.display='none'; fab.style.background=C.ACC; }
    function toggle_() { if(panel.style.display==='flex') close_(); else open_(); }

    // Close on outside click
    document.addEventListener('mousedown',function(e){ if(panel.style.display==='flex'&&!panel.contains(e.target)&&e.target!==fab) close_(); },{passive:true});

    // F8 — capture phase on both window and document
    function _f8(e){ if(e.key==='F8'){e.preventDefault();e.stopImmediatePropagation();toggle_();} }
    document.addEventListener('keydown',_f8,{capture:true});
    window.addEventListener('keydown',_f8,{capture:true});

    // Mount
    document.body.appendChild(fab);
    document.body.appendChild(panel);

    // ── Discord update detector ────────────────────────────────────────────
    setTimeout(function(){
      try {
        var m=(document.location.href||'').match(/app-(\d+\.\d+\.\d+)/);
        var cur=m?m[1]:null, stored=load('cl_discord_ver',null);
        if(cur){
          if(stored&&stored!==cur){
            var b=mk('span','position:absolute;top:-5px;right:-5px;background:#f9e2af;color:#1e1e2e;border-radius:50%;width:18px;height:18px;font-size:12px;font-weight:900;display:flex;align-items:center;justify-content:center;pointer-events:none;',{textContent:'\u26a0'});
            fab.style.position='fixed'; fab.appendChild(b);
            fab.title='Discord updated ('+stored+' \u2192 '+cur+') \u2014 re-run Claisum installer \u2192 Repair';
          }
          save('cl_discord_ver',cur);
        }
      }catch(e){}
    },3000);

    // ── Claisum update check ───────────────────────────────────────────────
    setTimeout(function(){
      try {
        var xhr=new XMLHttpRequest();
        xhr.open('GET','https://api.github.com/repos/'+REPO+'/releases/latest',true);
        xhr.setRequestHeader('Accept','application/vnd.github+json');
        xhr.onreadystatechange=function(){
          if(xhr.readyState!==4||xhr.status!==200)return;
          try{
            var tag=(JSON.parse(xhr.responseText).tag_name||'').replace(/^v/,'');
            if(tag&&tag!==VERSION){
              var b=mk('span','position:absolute;top:-4px;right:-4px;background:#f04747;color:#fff;border-radius:50%;width:16px;height:16px;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;pointer-events:none;',{textContent:'!'});
              fab.appendChild(b); fab.title='Claisum v'+tag+' available!';
            }
          }catch(e){}
        };
        xhr.timeout=8000; xhr.send();
      }catch(e){}
    },6000);

    // ── MutationObserver: re-inject FAB if Discord removes it ─────────────
    var _obs = new MutationObserver(function(){
      if (!document.body.contains(fab)) document.body.appendChild(fab);
      if (!document.body.contains(panel)) document.body.appendChild(panel);
    });
    _obs.observe(document.body, {childList:true, subtree:false});
  }

  // ══ Multi-strategy init ════════════════════════════════════════════════════
  if (document.body) {
    buildUI();
  } else {
    var _done = false;
    function _tryBuild(){ if(_done||!document.body)return; _done=true; buildUI(); }
    document.addEventListener('DOMContentLoaded', _tryBuild);
    window.addEventListener('load', _tryBuild);
    var _poll = setInterval(function(){ _tryBuild(); if(_done) clearInterval(_poll); }, 100);
    setTimeout(function(){ clearInterval(_poll); }, 30000);
  }

})();

// ── fallback BrowserWindow hook (used when session.setPreloads fails) ────────
function _hookWindows(electron, thisFile) {
  try {
    var fs = require('fs');
    var code = fs.readFileSync(thisFile, 'utf8');
    function _inject(win) {
      win.webContents.on('did-finish-load', function(){
        try { win.webContents.executeJavaScript(code).catch(function(){}); } catch(e){}
      });
    }
    electron.BrowserWindow.getAllWindows().forEach(_inject);
    electron.app.on('browser-window-created', function(e,w){ _inject(w); });
  } catch(e) { console.error('[Claisum] BrowserWindow hook failed:', e); }
}
