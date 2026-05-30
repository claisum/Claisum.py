// Claisum — Renderer UI v10
// Loaded as an Electron preload via resources/app/index.js (claisum_bootstrap.js).
(function () {
  'use strict';
  if (window.__claisumLoaded) return;
  window.__claisumLoaded = true;

  var VERSION = '1.0.0.1';
  var REPO    = 'claisum/Claisum.py';

  // ── Storage ──────────────────────────────────────────────────────────────
  function load(k, d) { try { var v = localStorage.getItem(k); return v !== null ? JSON.parse(v) : d; } catch(e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch(e) {} }
  var state = {
    theme:       load('cl_theme',      null),
    plugins:     load('cl_plugins',    []),
    customCss:   load('cl_custom_css', ''),
    accent:      load('cl_accent',     null),
    bgUrl:       load('cl_bg_url',     ''),
    msgCount:    load('cl_msg_count',  0),
    msgDate:     load('cl_msg_date',   ''),
    tab:         'themes'
  };

  // ── Palette (accent is user-configurable) ─────────────────────────────
  var C = {
    get ACC()  { return state.accent || '#7c6af7'; },
    get ACC2() { var a=state.accent||'#7c6af7'; return a==='#7c6af7'?'#6254d6':a; },
    BG:'#1e1e2e', BG2:'#181825', BG3:'#313244', TXT:'#cdd6f4', DIM:'#6c7086'
  };
  var STATUS = { GREEN:'#43b581', RED:'#f04747', BLUE:'#5865F2' };

  // ── Data ──────────────────────────────────────────────────────────────
  var THEMES = [
    { id:'midnight',   name:'Midnight',        preview:'#0d0f12', desc:'Deep dark — blue accents',   css:':root{--background-primary:#0d0f12;--background-secondary:#101316;--background-secondary-alt:#0d0f12;--background-tertiary:#08090b;--channeltextarea-background:#1a1d24;--text-normal:#dcddde;--text-muted:#72767d;--header-primary:#fff;--header-secondary:#b9bbbe;}' },
    { id:'dracula',    name:'Dracula',          preview:'#282a36', desc:'Classic Dracula colors',     css:':root{--background-primary:#282a36;--background-secondary:#21222c;--background-secondary-alt:#1e1f29;--background-tertiary:#191a21;--channeltextarea-background:#44475a;--text-normal:#f8f8f2;--text-muted:#6272a4;--header-primary:#f8f8f2;--header-secondary:#bd93f9;}' },
    { id:'catppuccin', name:'Catppuccin Mocha', preview:'#1e1e2e', desc:'Soothing pastel theme',     css:':root{--background-primary:#1e1e2e;--background-secondary:#181825;--background-secondary-alt:#11111b;--background-tertiary:#181825;--channeltextarea-background:#313244;--text-normal:#cdd6f4;--text-muted:#6c7086;--header-primary:#cdd6f4;--header-secondary:#bac2de;}' },
    { id:'nord',       name:'Nord',             preview:'#2e3440', desc:'Arctic blue palette',        css:':root{--background-primary:#2e3440;--background-secondary:#272c36;--background-secondary-alt:#21262e;--background-tertiary:#1e2229;--channeltextarea-background:#3b4252;--text-normal:#d8dee9;--text-muted:#4c566a;--header-primary:#eceff4;--header-secondary:#e5e9f0;}' },
    { id:'rose-pine',  name:'Rosé Pine',        preview:'#191724', desc:'Pine, rose and gold tones',  css:':root{--background-primary:#191724;--background-secondary:#1f1d2e;--background-secondary-alt:#191724;--background-tertiary:#191724;--channeltextarea-background:#26233a;--text-normal:#e0def4;--text-muted:#6e6a86;--header-primary:#e0def4;--header-secondary:#e0def4;}' },
    { id:'gruvbox',    name:'Gruvbox Dark',     preview:'#282828', desc:'Retro groove scheme',        css:':root{--background-primary:#282828;--background-secondary:#1d2021;--background-secondary-alt:#1a1a1a;--background-tertiary:#141617;--channeltextarea-background:#3c3836;--text-normal:#ebdbb2;--text-muted:#928374;--header-primary:#fbf1c7;--header-secondary:#ebdbb2;}' },
    { id:'solarized',  name:'Solarized Dark',   preview:'#002b36', desc:'Classic Solarized dark',    css:':root{--background-primary:#002b36;--background-secondary:#073642;--background-secondary-alt:#001f27;--background-tertiary:#001f27;--channeltextarea-background:#073642;--text-normal:#839496;--text-muted:#586e75;--header-primary:#93a1a1;--header-secondary:#839496;}' },
  ];

  var PLUGINS = [
    { id:'compact',      name:'Compact Mode',       desc:'Engere Nachrichten — mehr Inhalt sichtbar', css:"[class*='message-']{padding:2px 16px!important;}[class*='contents-']{padding-top:0!important;}" },
    { id:'square',       name:'Square Corners',      desc:'Entfernt alle border-radius',               css:'*{border-radius:0!important;}' },
    { id:'bigemoji',     name:'Big Emoji',           desc:'Solo-Emoji auf 48px vergrößern',            css:"[class*='jumboable']{width:48px!important;height:48px!important;}" },
    { id:'nogame',       name:'Hide Game Activity',  desc:'Spiel-Aktivitätsleiste ausblenden',         css:"[class*='activityStatus'],[class*='gameInfo']{display:none!important;}" },
    { id:'noavatar',     name:'Hide Avatars',        desc:'Alle Benutzer-Avatare ausblenden',          css:"[class*='avatar-'],[class*='avatarWrapper']{display:none!important;}" },
    { id:'blur-media',   name:'Blur Media',          desc:'Bilder/Videos unscharf bis Hover',          css:"[class*='imageWrapper'],[class*='videoWrapper']{filter:blur(10px)!important;transition:filter .3s;}[class*='imageWrapper']:hover,[class*='videoWrapper']:hover{filter:none!important;}" },
    { id:'hide-nitro',   name:'Hide Nitro Banner',   desc:'Nitro-Werbung & Upsells ausblenden',        css:"[class*='premiumPromo'],[class*='nitroUpsell'],[class*='upsellContainer'],[class*='premiumGuildSubscriptionSentMessage']{display:none!important;}" },
    { id:'anon-mode',    name:'Anonymous Mode',      desc:'"Schreibt..." Indikator ausblenden',        css:"[class*='typing-'],[class*='typingDots']{display:none!important;}" },
    { id:'hide-members', name:'Hide Member List',    desc:'Rechte Mitgliederliste ausblenden',         css:"[class*='membersWrap-'],[class*='membersList-']{display:none!important;}" },
    { id:'font-mono',    name:'Monospace Font',      desc:'Monospace-Schrift für alle Texte',          css:":root{--font-primary:'Courier New',monospace;--font-display:'Courier New',monospace;}" },
    { id:'font-inter',   name:'Inter Font',          desc:'Saubere moderne Schrift (Inter)',           css:"@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');:root{--font-primary:'Inter',sans-serif;--font-display:'Inter',sans-serif;}" },
    { id:'anti-track',   name:'Anti-Track',          desc:'Discord Analytics & Tracking blockieren',  css:'', jsInit: _initAntiTrack },
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

  // ── JS Plugin: Anti-Track ────────────────────────────────────────────────
  function _initAntiTrack() {
    var BLOCKED = ['sentry.io', 'datadog', '/api/v9/science', '/api/v10/science', 'google-analytics', 'amplitude', 'bugsnag'];
    var _origFetch = window.fetch;
    window.fetch = function(url) {
      if (typeof url === 'string' && BLOCKED.some(function(b){ return url.indexOf(b) >= 0; })) {
        return Promise.resolve(new Response('{}', {status:200}));
      }
      return _origFetch.apply(this, arguments);
    };
    var _origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(m, url) {
      if (typeof url === 'string' && BLOCKED.some(function(b){ return url.indexOf(b) >= 0; })) {
        this.__clBlocked = true;
      }
      return _origOpen.apply(this, arguments);
    };
    var _origSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function() {
      if (this.__clBlocked) return;
      return _origSend.apply(this, arguments);
    };
  }

  // ── Message Counter ───────────────────────────────────────────────────────
  function _initMsgCounter() {
    var today = new Date().toDateString();
    if (state.msgDate !== today) { state.msgCount = 0; state.msgDate = today; save('cl_msg_date', today); save('cl_msg_count', 0); }
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        var box = document.activeElement;
        if (box && box.getAttribute('role') === 'textbox') {
          state.msgCount++;
          save('cl_msg_count', state.msgCount);
          var ctr = document.getElementById('cl-msg-counter');
          if (ctr) ctr.textContent = state.msgCount + ' heute';
        }
      }
    }, {capture: true, passive: true});
  }

  // ── Ping helper ──────────────────────────────────────────────────────────
  function _measurePing(cb) {
    try {
      var t = Date.now();
      var x = new XMLHttpRequest();
      x.open('GET', 'https://discord.com/api/v10/gateway', true);
      x.onreadystatechange = function() {
        if (x.readyState === 4) cb(Date.now() - t);
      };
      x.timeout = 5000;
      x.onerror = function() { cb(-1); };
      x.send();
    } catch(e) { cb(-1); }
  }

  // ── Build UI ─────────────────────────────────────────────────────────────
  function buildUI() {
    // Apply saved settings
    if (state.theme) { var t = THEMES.find(function(x){return x.id===state.theme;}); if(t) applyCSS('theme', t.css); }
    state.plugins.forEach(function(pid) {
      var p = PLUGINS.find(function(x){return x.id===pid;});
      if (!p) return;
      if (p.css) applyCSS(pid, p.css);
      if (p.jsInit) p.jsInit();
    });
    if (state.customCss) applyCSS('custom', state.customCss);
    if (state.bgUrl) _applyBg(state.bgUrl);
    _initMsgCounter();

    // ── Panel ────────────────────────────────────────────────────────────
    var panel = mk('div',
      'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);' +
      'width:540px;max-height:600px;background:'+C.BG+';color:'+C.TXT+';' +
      'border-radius:14px;box-shadow:0 16px 56px #000000bb;z-index:2147483646;' +
      'display:none;flex-direction:column;font-family:"Segoe UI",system-ui,sans-serif;overflow:hidden;');

    // Header
    var ph = mk('div','display:flex;align-items:center;padding:14px 18px;background:'+C.BG2+';border-bottom:1px solid #ffffff12;flex-shrink:0;');
    var pt = mk('span','font-size:15px;font-weight:700;flex:1;',{textContent:'\u26a1 Claisum  v'+VERSION});
    var pc = mk('button','background:none;border:none;color:'+C.DIM+';font-size:22px;cursor:pointer;line-height:1;padding:0 4px;border-radius:4px;',{textContent:'\u00d7',title:'Schließen (F8)'});
    pc.onmouseenter=function(){pc.style.color=C.TXT;}; pc.onmouseleave=function(){pc.style.color=C.DIM;};
    pc.onclick=close_; ph.appendChild(pt); ph.appendChild(pc);

    // Tabs
    var tb = mk('div','display:flex;background:'+C.BG2+';border-bottom:1px solid #ffffff12;flex-shrink:0;');
    var tBtns = {};
    ['themes','plugins','tools'].forEach(function(t){
      var label = {themes:'Themes ('+THEMES.length+')', plugins:'Plugins ('+PLUGINS.length+')', tools:'Tools'}[t];
      var b = mk('button','flex:1;padding:10px 0;background:none;border:none;cursor:pointer;font-size:12px;font-weight:600;border-bottom:2px solid transparent;color:'+C.DIM+';', {textContent:label});
      b.onclick=function(){switchTab(t);}; tBtns[t]=b; tb.appendChild(b);
    });

    var pbody = mk('div','flex:1;overflow-y:auto;padding:12px 16px;'); pbody.style.scrollbarWidth='thin';
    var pfoot = mk('div','padding:8px 16px;background:'+C.BG2+';border-top:1px solid #ffffff12;font-size:11px;color:'+C.DIM+';flex-shrink:0;display:flex;align-items:center;gap:8px;');
    pfoot.appendChild(mk('span','flex:1;',{textContent:'F8 öffnen/schließen  \u2022  github.com/'+REPO}));
    var ctrEl = mk('span','color:'+C.DIM+';font-size:10px;',{id:'cl-msg-counter',textContent:state.msgCount+' heute'});
    pfoot.appendChild(ctrEl);

    panel.appendChild(ph); panel.appendChild(tb); panel.appendChild(pbody); panel.appendChild(pfoot);

    // ── Helpers ──────────────────────────────────────────────────────────
    function switchTab(tab) {
      state.tab=tab;
      Object.keys(tBtns).forEach(function(t){
        tBtns[t].style.color=t===tab?C.ACC:C.DIM;
        tBtns[t].style.borderBottom=t===tab?'2px solid '+C.ACC:'2px solid transparent';
      });
      pbody.innerHTML='';
      if(tab==='themes') renderThemes();
      else if(tab==='plugins') renderPlugins();
      else renderTools();
    }

    function mkToggle(on) {
      var tr=mk('div','width:38px;height:22px;border-radius:11px;cursor:pointer;position:relative;flex-shrink:0;background:'+(on?C.ACC:'#3a3a52')+';transition:background .2s;');
      var kn=mk('div','position:absolute;top:3px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 1px 4px #0004;transition:left .18s;left:'+(on?'19px':'3px')+';');
      tr.appendChild(kn); tr.__on=on; return tr;
    }
    function setToggle(tr,on){ tr.__on=on; tr.style.background=on?C.ACC:'#3a3a52'; var kn=tr.firstChild; if(kn)kn.style.left=on?'19px':'3px'; }
    function mkCard(children,extra){
      var c=mk('div','display:flex;align-items:center;padding:10px 12px;margin:4px 0;background:'+C.BG3+';border-radius:10px;gap:10px;border:1px solid transparent;'+(extra||''));
      c.onmouseenter=function(){c.style.borderColor='#ffffff18';}; c.onmouseleave=function(){c.style.borderColor='transparent';};
      children.forEach(function(x){c.appendChild(x);}); return c;
    }
    function mkInfo(name,desc){
      var w=mk('div','flex:1;min-width:0;');
      w.appendChild(mk('div','font-size:13px;font-weight:600;color:'+C.TXT+';',{textContent:name}));
      w.appendChild(mk('div','font-size:11px;color:'+C.DIM+';margin-top:2px;',{textContent:desc}));
      return w;
    }
    function mkSectionLabel(text){
      return mk('div','font-size:10px;font-weight:700;letter-spacing:.08em;color:'+C.DIM+';text-transform:uppercase;margin:12px 0 4px;padding:0 2px;',{textContent:text});
    }
    function mkBtn(label, bg, cb) {
      var b=mk('button','background:'+bg+';color:#fff;border:none;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:12px;font-weight:600;',{textContent:label});
      b.onclick=cb; return b;
    }

    // ── Themes tab ───────────────────────────────────────────────────────
    function renderThemes(){
      var row=mk('div','margin-bottom:8px;display:flex;justify-content:flex-end;');
      var rb=mk('button','background:none;border:1px solid '+C.DIM+';color:'+C.DIM+';border-radius:6px;padding:4px 12px;cursor:pointer;font-size:11px;',{textContent:'\u21ba Reset'});
      rb.onmouseenter=function(){rb.style.borderColor=C.TXT;rb.style.color=C.TXT;}; rb.onmouseleave=function(){rb.style.borderColor=C.DIM;rb.style.color=C.DIM;};
      rb.onclick=function(){ if(state.theme) removeCSS('theme'); state.theme=null; save('cl_theme',null); document.querySelectorAll('[data-cl-t]').forEach(function(x){setToggle(x,false);}); };
      row.appendChild(rb); pbody.appendChild(row);
      THEMES.forEach(function(t){
        var dot=mk('div','width:18px;height:18px;border-radius:50%;flex-shrink:0;background:'+t.preview+';border:2px solid #ffffff20;');
        var tr=mkToggle(state.theme===t.id); tr.setAttribute('data-cl-t',t.id);
        tr.onclick=function(){
          var on=!tr.__on;
          if(on){ if(state.theme&&state.theme!==t.id)removeCSS('theme'); state.theme=t.id; save('cl_theme',t.id); applyCSS('theme',t.css); document.querySelectorAll('[data-cl-t]').forEach(function(x){if(x!==tr)setToggle(x,false);}); }
          else{ if(state.theme===t.id){state.theme=null;save('cl_theme',null);removeCSS('theme');} }
          setToggle(tr,on);
        };
        pbody.appendChild(mkCard([dot,mkInfo(t.name,t.desc),tr]));
      });
    }

    // ── Plugins tab ──────────────────────────────────────────────────────
    function renderPlugins(){
      // Background URL input section
      pbody.appendChild(mkSectionLabel('Hintergrundbild'));
      var bgRow = mk('div','display:flex;gap:6px;margin:4px 0 8px;');
      var bgInp = mk('input','flex:1;background:'+C.BG3+';border:1px solid #ffffff18;color:'+C.TXT+';border-radius:6px;padding:6px 10px;font-size:12px;outline:none;');
      bgInp.placeholder='URL oder CSS-Wert (z.B. #1a1a2e)';
      bgInp.value = state.bgUrl || '';
      var bgApply = mkBtn('Anwenden', C.ACC, function(){
        state.bgUrl = bgInp.value.trim();
        save('cl_bg_url', state.bgUrl);
        _applyBg(state.bgUrl);
      });
      var bgClear = mkBtn('X', '#f04747', function(){
        state.bgUrl=''; save('cl_bg_url',''); removeCSS('bg'); bgInp.value='';
      });
      bgRow.appendChild(bgInp); bgRow.appendChild(bgApply); bgRow.appendChild(bgClear);
      pbody.appendChild(bgRow);

      pbody.appendChild(mkSectionLabel('Plugins'));
      PLUGINS.forEach(function(p){
        var on = state.plugins.indexOf(p.id) >= 0;
        var tr=mkToggle(on);
        tr.onclick=function(){
          var nowOn=!tr.__on;
          if(nowOn){
            if(state.plugins.indexOf(p.id)<0) state.plugins.push(p.id);
            if(p.css) applyCSS(p.id,p.css);
            if(p.jsInit) p.jsInit();
          } else {
            state.plugins=state.plugins.filter(function(x){return x!==p.id;});
            if(p.css) removeCSS(p.id);
          }
          save('cl_plugins',state.plugins); setToggle(tr,nowOn);
        };
        pbody.appendChild(mkCard([mkInfo(p.name,p.desc),tr]));
      });
    }

    // ── Tools tab ────────────────────────────────────────────────────────
    function renderTools(){
      // Accent color
      pbody.appendChild(mkSectionLabel('Akzentfarbe'));
      var accRow=mk('div','display:flex;align-items:center;gap:10px;margin:4px 0 8px;');
      var accInp=mk('input','width:44px;height:36px;border:none;border-radius:6px;cursor:pointer;background:none;padding:0;');
      accInp.type='color'; accInp.value=state.accent||'#7c6af7';
      accInp.oninput=function(){ state.accent=accInp.value; save('cl_accent',state.accent); _refreshAccent(); };
      var accReset=mkBtn('Reset', C.BG3, function(){ state.accent=null; save('cl_accent',null); accInp.value='#7c6af7'; _refreshAccent(); });
      accReset.style.color=C.TXT;
      accRow.appendChild(accInp);
      accRow.appendChild(mk('span','font-size:12px;color:'+C.DIM+';',{textContent:'Claisum-Akzentfarbe anpassen'}));
      accRow.appendChild(accReset);
      pbody.appendChild(accRow);

      // Ping
      pbody.appendChild(mkSectionLabel('Server Ping'));
      var pingRow=mk('div','display:flex;align-items:center;gap:10px;margin:4px 0 8px;');
      var pingVal=mk('span','font-size:20px;font-weight:700;color:'+STATUS.GREEN+';',{textContent:'—'});
      var pingBtn=mkBtn('Messen', C.BG3, function(){
        pingVal.textContent='…'; pingVal.style.color=C.DIM;
        _measurePing(function(ms){
          pingVal.textContent=ms<0?'Fehler':ms+'ms';
          pingVal.style.color=ms<0?STATUS.RED:ms<80?STATUS.GREEN:ms<200?'#f9e2af':STATUS.RED;
        });
      });
      pingBtn.style.color=C.TXT;
      pingRow.appendChild(pingVal);
      pingRow.appendChild(mk('span','font-size:12px;color:'+C.DIM+';',{textContent:'discord.com/api Gateway'}));
      pingRow.appendChild(pingBtn);
      pbody.appendChild(pingRow);

      // Message counter
      pbody.appendChild(mkSectionLabel('Nachrichten heute'));
      var mcRow=mk('div','display:flex;align-items:center;gap:10px;margin:4px 0 8px;');
      var mcVal=mk('span','font-size:20px;font-weight:700;color:'+C.ACC+';',{textContent:String(state.msgCount)});
      var mcReset=mkBtn('Reset', C.BG3, function(){ state.msgCount=0; save('cl_msg_count',0); mcVal.textContent='0'; var c=document.getElementById('cl-msg-counter'); if(c)c.textContent='0 heute'; });
      mcReset.style.color=C.TXT;
      mcRow.appendChild(mcVal);
      mcRow.appendChild(mk('span','font-size:12px;color:'+C.DIM+';',{textContent:'gesendete Nachrichten (reset täglich)'}));
      mcRow.appendChild(mcReset);
      pbody.appendChild(mcRow);

      // Custom CSS
      pbody.appendChild(mkSectionLabel('Eigenes CSS'));
      var cssArea=mk('textarea','width:100%;height:110px;background:'+C.BG3+';color:'+C.TXT+';border:1px solid #ffffff18;border-radius:8px;padding:8px 10px;font-family:"Courier New",monospace;font-size:11px;resize:vertical;outline:none;box-sizing:border-box;');
      cssArea.placeholder='/* Eigenes CSS hier eingeben */\n[class*="message-"] { font-size: 14px !important; }';
      cssArea.value=state.customCss||'';
      pbody.appendChild(cssArea);
      var cssRow=mk('div','display:flex;gap:6px;margin:4px 0 8px;');
      cssRow.appendChild(mkBtn('Anwenden', C.ACC, function(){ state.customCss=cssArea.value; save('cl_custom_css',state.customCss); applyCSS('custom',state.customCss); }));
      cssRow.appendChild(mkBtn('Entfernen', '#f04747', function(){ state.customCss=''; save('cl_custom_css',''); removeCSS('custom'); cssArea.value=''; }));
      pbody.appendChild(cssRow);

      // Backup / Restore
      pbody.appendChild(mkSectionLabel('Einstellungen'));
      var settRow=mk('div','display:flex;gap:6px;margin:4px 0;');
      settRow.appendChild(mkBtn('\u2193 Exportieren', C.ACC, function(){
        var data=JSON.stringify({theme:state.theme,plugins:state.plugins,customCss:state.customCss,accent:state.accent,bgUrl:state.bgUrl},null,2);
        var a=document.createElement('a'); a.href='data:text/json;charset=utf-8,'+encodeURIComponent(data);
        a.download='claisum-settings.json'; a.click();
      }));
      var fileInp=mk('input','display:none;'); fileInp.type='file'; fileInp.accept='.json';
      fileInp.onchange=function(){
        var f=fileInp.files[0]; if(!f) return;
        var r=new FileReader();
        r.onload=function(e){
          try {
            var d=JSON.parse(e.target.result);
            if(d.theme!==undefined){state.theme=d.theme;save('cl_theme',d.theme);}
            if(d.plugins){state.plugins=d.plugins;save('cl_plugins',d.plugins);}
            if(d.customCss!==undefined){state.customCss=d.customCss;save('cl_custom_css',d.customCss);}
            if(d.accent!==undefined){state.accent=d.accent;save('cl_accent',d.accent);}
            if(d.bgUrl!==undefined){state.bgUrl=d.bgUrl;save('cl_bg_url',d.bgUrl);}
            switchTab('tools');
          } catch(err){}
        };
        r.readAsText(f);
      };
      document.body.appendChild(fileInp);
      settRow.appendChild(mkBtn('\u2191 Importieren', C.BG3, function(){ fileInp.style.color=C.TXT; fileInp.click(); }));
      pbody.appendChild(settRow);
    }

    // ── FAB ──────────────────────────────────────────────────────────────
    var fab = mk('button',
      'position:fixed;bottom:22px;left:22px;width:46px;height:46px;border-radius:50%;' +
      'background:'+C.ACC+';border:none;cursor:pointer;font-size:20px;' +
      'z-index:2147483647;box-shadow:0 4px 16px #0006,0 0 0 2px #ffffff18;' +
      'transition:transform .15s,box-shadow .15s;',
      {textContent:'\u26a1',title:'Claisum öffnen (F8)'});
    fab.onmouseenter=function(){fab.style.transform='scale(1.14)';}; fab.onmouseleave=function(){fab.style.transform='scale(1)';};
    fab.onclick=toggle_;

    // ── Status dot (bottom-right) ─────────────────────────────────────
    var statusDot = mk('div',
      'position:fixed;bottom:16px;right:16px;width:12px;height:12px;' +
      'border-radius:50%;background:'+STATUS.GREEN+';z-index:2147483647;' +
      'box-shadow:0 0 0 2px #ffffff22,0 0 8px '+STATUS.GREEN+'88;' +
      'pointer-events:auto;cursor:default;transition:background .4s,box-shadow .4s;');
    statusDot.title='Claisum aktiv';
    function setStatus(color, title){
      var col=STATUS[color.toUpperCase()]||color;
      statusDot.style.background=col;
      statusDot.style.boxShadow='0 0 0 2px #ffffff22,0 0 8px '+col+'88';
      if(title) statusDot.title=title;
    }

    function open_(){ panel.style.display='flex'; switchTab(state.tab||'themes'); fab.style.background=C.ACC2; }
    function close_(){ panel.style.display='none'; fab.style.background=C.ACC; }
    function toggle_(){ if(panel.style.display==='flex') close_(); else open_(); }

    document.addEventListener('mousedown',function(e){ if(panel.style.display==='flex'&&!panel.contains(e.target)&&e.target!==fab) close_(); },{passive:true});
    function _f8(e){ if(e.key==='F8'){e.preventDefault();e.stopImmediatePropagation();toggle_();} }
    document.addEventListener('keydown',_f8,{capture:true});
    window.addEventListener('keydown',_f8,{capture:true});

    document.body.appendChild(fab);
    document.body.appendChild(statusDot);
    document.body.appendChild(panel);

    var _obs=new MutationObserver(function(){
      if(!document.body.contains(fab)) document.body.appendChild(fab);
      if(!document.body.contains(statusDot)) document.body.appendChild(statusDot);
      if(!document.body.contains(panel)) document.body.appendChild(panel);
    });
    _obs.observe(document.body,{childList:true,subtree:false});

    // ── Discord version drift ─────────────────────────────────────────
    setTimeout(function(){
      try {
        var m=(document.location.href||'').match(/app-(\d+\.\d+\.\d+)/);
        var cur=m?m[1]:null, stored=load('cl_discord_ver',null);
        if(cur){
          if(stored&&stored!==cur){
            fab.appendChild(mk('span','position:absolute;top:-5px;right:-5px;background:#f9e2af;color:#1e1e2e;border-radius:50%;width:18px;height:18px;font-size:12px;display:flex;align-items:center;justify-content:center;pointer-events:none;',{textContent:'\u26a0'}));
            fab.title='Discord updated \u2014 Claisum Installer \u2192 Repair';
            setStatus('blue','Discord updated \u2014 Claisum Installer \u2192 Repair ausführen');
          }
          save('cl_discord_ver',cur);
        }
      }catch(e){ setStatus('red','Claisum: Fehler'); }
    },3000);

    // ── Claisum version check ─────────────────────────────────────────
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
              fab.appendChild(mk('span','position:absolute;top:-4px;right:-4px;background:#f04747;color:#fff;border-radius:50%;width:16px;height:16px;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;pointer-events:none;',{textContent:'!'}));
              fab.title='Claisum v'+tag+' verfügbar!';
              setStatus('blue','Claisum Update: v'+tag+' verfügbar');
            }
          }catch(e){}
        };
        xhr.onerror=function(){ setStatus('red','Claisum: Netzwerkfehler'); };
        xhr.timeout=8000; xhr.send();
      }catch(e){}
    },6000);

    // ── Accent color refresh ───────────────────────────────────────────
    function _refreshAccent(){
      fab.style.background=C.ACC;
      statusDot.style.background=STATUS.GREEN;
      if(panel.style.display==='flex') switchTab(state.tab||'themes');
    }
  }

  // ── Background helper ────────────────────────────────────────────────
  function _applyBg(val){
    if(!val){ removeCSS('bg'); return; }
    var css;
    if(val.match(/^#|^rgb|^hsl/)){
      css='[class*="app-"],[class*="layers-"]{background:'+val+' !important;}';
    } else {
      css='[class*="app-"],[class*="layers-"]{background:url("'+val+'") center/cover no-repeat !important;}';
    }
    applyCSS('bg',css);
  }

  // ── Multi-strategy init ──────────────────────────────────────────────
  if (document.body) {
    buildUI();
  } else {
    var _done=false;
    function _tryBuild(){ if(_done||!document.body)return; _done=true; buildUI(); }
    document.addEventListener('DOMContentLoaded',_tryBuild);
    window.addEventListener('load',_tryBuild);
    var _poll=setInterval(function(){ _tryBuild(); if(_done) clearInterval(_poll); },100);
    setTimeout(function(){ clearInterval(_poll); },30000);
  }
})();
