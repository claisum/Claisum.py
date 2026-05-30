// Claisum — Renderer UI v11 — "always-on" visual identity
(function () {
  'use strict';
  if (window.__claisumLoaded) return;
  window.__claisumLoaded = true;

  var VERSION = '1.0.0.1';
  var REPO    = 'claisum/Claisum.py';

  // ── Storage ────────────────────────────────────────────────────────────
  function load(k, d) { try { var v = localStorage.getItem(k); return v !== null ? JSON.parse(v) : d; } catch(e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch(e) {} }

  // First-run defaults: apply Midnight theme + hide nitro + anon mode out of the box
  if (!localStorage.getItem('cl_init')) {
    localStorage.setItem('cl_init', '1');
    localStorage.setItem('cl_theme',   JSON.stringify('midnight'));
    localStorage.setItem('cl_plugins', JSON.stringify(['hide-nitro','anon-mode','hide-members-btn']));
  }

  var state = {
    theme:     load('cl_theme',     'midnight'),
    plugins:   load('cl_plugins',   ['hide-nitro','anon-mode','hide-members-btn']),
    customCss: load('cl_custom_css',''),
    accent:    load('cl_accent',    null),
    bgUrl:     load('cl_bg_url',    ''),
    msgCount:  load('cl_msg_count', 0),
    msgDate:   load('cl_msg_date',  ''),
    tab:       'themes'
  };

  var C = {
    get ACC()  { return state.accent || '#7c6af7'; },
    get ACC2() { return state.accent ? state.accent : '#6254d6'; },
    BG:'#1e1e2e', BG2:'#181825', BG3:'#313244', TXT:'#cdd6f4', DIM:'#6c7086'
  };
  var STATUS = { GREEN:'#43b581', RED:'#f04747', BLUE:'#5865F2' };

  // ── CSS helpers ─────────────────────────────────────────────────────────
  function applyCSS(id, css) {
    var el = document.getElementById('cl-' + id);
    if (!el) { el = document.createElement('style'); el.id = 'cl-' + id; document.head.appendChild(el); }
    el.textContent = css;
  }
  function removeCSS(id) { var el = document.getElementById('cl-' + id); if (el) el.remove(); }

  // ── ALWAYS-ON BASE CSS — makes Discord look modded immediately ──────────
  var BASE_CSS = [
    /* Thin accent scrollbar */
    '::-webkit-scrollbar{width:3px!important;height:3px!important;}',
    '::-webkit-scrollbar-track{background:transparent!important;}',
    '::-webkit-scrollbar-thumb{background:#7c6af7!important;border-radius:4px!important;}',
    '::-webkit-scrollbar-thumb:hover{background:#9d8eff!important;}',

    /* Message hover highlight */
    '[class*="message-"]:hover{background:rgba(124,106,247,0.06)!important;transition:background .15s;}',

    /* Mention = accent left border */
    '[class*="mentioned-"]{border-left:3px solid #7c6af7!important;background:rgba(124,106,247,0.08)!important;}',

    /* Code blocks — purple tint */
    '[class*="markup-"] code,[class*="inlineCode-"]{background:#2a2240!important;color:#cba6f7!important;border-radius:5px!important;}',
    '[class*="codeContainer-"],[class*="hljs"]{background:#1a1530!important;border:1px solid #7c6af750!important;border-radius:8px!important;}',

    /* Links — accent color */
    '[class*="markup-"] a{color:#a89df5!important;}[class*="markup-"] a:hover{color:#cba6f7!important;}',

    /* Rounded images */
    '[class*="imageWrapper"]{border-radius:10px!important;overflow:hidden!important;}',

    /* Reactions — accent on hover */
    '[class*="reaction-"]:hover{background:rgba(124,106,247,0.15)!important;border-color:#7c6af780!important;}',
    '[class*="reaction-"][class*="reactionMe-"]{background:rgba(124,106,247,0.25)!important;border-color:#7c6af7!important;}',

    /* User popout / modal corners */
    '[class*="userPopout-"],[class*="modal-"]{border-radius:14px!important;}',

    /* Server list icons — softer */
    '[class*="wrapper-"][class*="lowerBadge-"],[class*="childWrapper-"]{transition:border-radius .2s!important;}',

    /* Input box — left accent border */
    '[class*="channelTextArea-"]{border-left:2px solid #7c6af7!important;}',

    /* Subtle glow on own messages */
    '[class*="isCurrentUser-"] [class*="messageContent-"]{color:#e0def4!important;}',

    /* Titlebar accent strip */
    '[class*="titleBar-"]{border-bottom:1px solid #7c6af730!important;}',

    /* Claisum FAB tooltip */
    '#cl-fab::after{content:attr(title);position:absolute;left:54px;top:50%;transform:translateY(-50%);' +
      'background:#1e1e2e;color:#cdd6f4;border:1px solid #7c6af740;border-radius:6px;padding:4px 10px;' +
      'white-space:nowrap;font-size:11px;font-family:system-ui;pointer-events:none;opacity:0;transition:opacity .2s;}',
    '#cl-fab:hover::after{opacity:1;}',
  ].join('');

  var THEMES = [
    { id:'midnight',   name:'Midnight',        preview:'#0d0f12', desc:'Deep dark — blaue Akzente',   css:':root{--background-primary:#0d0f12;--background-secondary:#101316;--background-secondary-alt:#0d0f12;--background-tertiary:#08090b;--channeltextarea-background:#1a1d24;--text-normal:#dcddde;--text-muted:#72767d;--header-primary:#fff;--header-secondary:#b9bbbe;}' },
    { id:'dracula',    name:'Dracula',          preview:'#282a36', desc:'Klassische Dracula-Farben',   css:':root{--background-primary:#282a36;--background-secondary:#21222c;--background-secondary-alt:#1e1f29;--background-tertiary:#191a21;--channeltextarea-background:#44475a;--text-normal:#f8f8f2;--text-muted:#6272a4;--header-primary:#f8f8f2;--header-secondary:#bd93f9;}' },
    { id:'catppuccin', name:'Catppuccin Mocha', preview:'#1e1e2e', desc:'Sanftes Pastel-Theme',       css:':root{--background-primary:#1e1e2e;--background-secondary:#181825;--background-secondary-alt:#11111b;--background-tertiary:#181825;--channeltextarea-background:#313244;--text-normal:#cdd6f4;--text-muted:#6c7086;--header-primary:#cdd6f4;--header-secondary:#bac2de;}' },
    { id:'nord',       name:'Nord',             preview:'#2e3440', desc:'Arktische Blau-Palette',     css:':root{--background-primary:#2e3440;--background-secondary:#272c36;--background-secondary-alt:#21262e;--background-tertiary:#1e2229;--channeltextarea-background:#3b4252;--text-normal:#d8dee9;--text-muted:#4c566a;--header-primary:#eceff4;--header-secondary:#e5e9f0;}' },
    { id:'rose-pine',  name:'Rosé Pine',        preview:'#191724', desc:'Pine, Rose und Gold',        css:':root{--background-primary:#191724;--background-secondary:#1f1d2e;--background-secondary-alt:#191724;--background-tertiary:#191724;--channeltextarea-background:#26233a;--text-normal:#e0def4;--text-muted:#6e6a86;--header-primary:#e0def4;--header-secondary:#e0def4;}' },
    { id:'gruvbox',    name:'Gruvbox Dark',     preview:'#282828', desc:'Retro Groove-Schema',        css:':root{--background-primary:#282828;--background-secondary:#1d2021;--background-secondary-alt:#1a1a1a;--background-tertiary:#141617;--channeltextarea-background:#3c3836;--text-normal:#ebdbb2;--text-muted:#928374;--header-primary:#fbf1c7;--header-secondary:#ebdbb2;}' },
    { id:'solarized',  name:'Solarized Dark',   preview:'#002b36', desc:'Klassisches Solarized dark', css:':root{--background-primary:#002b36;--background-secondary:#073642;--background-secondary-alt:#001f27;--background-tertiary:#001f27;--channeltextarea-background:#073642;--text-normal:#839496;--text-muted:#586e75;--header-primary:#93a1a1;--header-secondary:#839496;}' },
  ];

  var PLUGINS = [
    { id:'compact',         name:'Compact Mode',      desc:'Engere Nachrichten — mehr Inhalt sichtbar', css:"[class*='message-']{padding:2px 16px!important;}[class*='contents-']{padding-top:0!important;}" },
    { id:'square',          name:'Square Corners',     desc:'Entfernt alle border-radius',               css:'*{border-radius:0!important;}' },
    { id:'bigemoji',        name:'Big Emoji',          desc:'Solo-Emoji auf 48px',                       css:"[class*='jumboable']{width:48px!important;height:48px!important;}" },
    { id:'nogame',          name:'Hide Game Activity', desc:'Spiel-Aktivitätsleiste ausblenden',         css:"[class*='activityStatus'],[class*='gameInfo']{display:none!important;}" },
    { id:'noavatar',        name:'Hide Avatars',       desc:'Alle Avatare ausblenden',                   css:"[class*='avatar-'],[class*='avatarWrapper']{display:none!important;}" },
    { id:'blur-media',      name:'Blur Media',         desc:'Bilder/Videos unscharf bis Hover',          css:"[class*='imageWrapper'],[class*='videoWrapper']{filter:blur(10px)!important;transition:filter .3s;}[class*='imageWrapper']:hover,[class*='videoWrapper']:hover{filter:none!important;}" },
    { id:'hide-nitro',      name:'Hide Nitro Banner',  desc:'Nitro-Werbung & Upsells weg',               css:"[class*='premiumPromo'],[class*='nitroUpsell'],[class*='upsellContainer'],[class*='premiumGuildSubscriptionSentMessage']{display:none!important;}" },
    { id:'anon-mode',       name:'Anonymous Mode',     desc:'"Schreibt..." ausblenden',                  css:"[class*='typing-'],[class*='typingDots']{display:none!important;}" },
    { id:'hide-members',    name:'Hide Member List',   desc:'Rechte Mitgliederliste ausblenden',         css:"[class*='membersWrap-'],[class*='membersList-']{display:none!important;}" },
    { id:'hide-members-btn',name:'Hide Members Button',desc:'Mitglieder-Button in Kopfleiste weg',       css:"[aria-label='Mitglieder anzeigen'],[aria-label='Show Member List']{display:none!important;}" },
    { id:'font-mono',       name:'Monospace Font',     desc:'Courier New für alle Texte',                css:":root{--font-primary:'Courier New',monospace;--font-display:'Courier New',monospace;}" },
    { id:'font-inter',      name:'Inter Font',         desc:'Saubere moderne Schrift',                   css:"@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');:root{--font-primary:'Inter',sans-serif;}" },
    { id:'anti-track',      name:'Anti-Track',         desc:'Discord Analytics blockieren',              css:'', jsInit: _initAntiTrack },
  ];

  // ── JS Plugin: Anti-Track ──────────────────────────────────────────────
  function _initAntiTrack() {
    var B = ['sentry.io','datadog','/api/v9/science','/api/v10/science','google-analytics','amplitude','bugsnag'];
    var _f = window.fetch;
    window.fetch = function(u) { if(typeof u==='string'&&B.some(function(b){return u.indexOf(b)>=0;})) return Promise.resolve(new Response('{}',{status:200})); return _f.apply(this,arguments); };
    var _o = XMLHttpRequest.prototype.open, _s = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.open = function(m,u) { if(typeof u==='string'&&B.some(function(b){return u.indexOf(b)>=0;}))this.__clB=true; return _o.apply(this,arguments); };
    XMLHttpRequest.prototype.send = function() { if(this.__clB)return; return _s.apply(this,arguments); };
  }

  // ── Message Counter ────────────────────────────────────────────────────
  function _initMsgCounter() {
    var today = new Date().toDateString();
    if (state.msgDate !== today) { state.msgCount = 0; state.msgDate = today; save('cl_msg_date',today); save('cl_msg_count',0); }
    document.addEventListener('keydown', function(e) {
      if (e.key==='Enter'&&!e.shiftKey) {
        var b=document.activeElement;
        if(b&&b.getAttribute('role')==='textbox') { state.msgCount++; save('cl_msg_count',state.msgCount); var c=document.getElementById('cl-ctr'); if(c)c.textContent=state.msgCount+' heute'; }
      }
    },{capture:true,passive:true});
  }

  // ── Ping ────────────────────────────────────────────────────────────────
  function _ping(cb) {
    try { var t=Date.now(),x=new XMLHttpRequest(); x.open('GET','https://discord.com/api/v10/gateway',true); x.onreadystatechange=function(){if(x.readyState===4)cb(Date.now()-t);}; x.timeout=5000; x.onerror=function(){cb(-1);}; x.send(); }
    catch(e){ cb(-1); }
  }

  // ── DOM helper ──────────────────────────────────────────────────────────
  function mk(tag,style,props) { var e=document.createElement(tag); if(style)e.style.cssText=style; if(props)Object.assign(e,props); return e; }

  function _applyBg(val) {
    if(!val){removeCSS('bg');return;}
    var css=val.match(/^#|^rgb|^hsl/)?'[class*="app-"],[class*="layers-"]{background:'+val+' !important;}':'[class*="app-"],[class*="layers-"]{background:url("'+val+'") center/cover no-repeat !important;}';
    applyCSS('bg',css);
  }

  // ── Build UI ────────────────────────────────────────────────────────────
  function buildUI() {
    // Always-on base visual identity
    applyCSS('base', BASE_CSS);

    // Apply saved theme
    if (state.theme) { var t=THEMES.find(function(x){return x.id===state.theme;}); if(t)applyCSS('theme',t.css); }

    // Apply saved plugins
    state.plugins.forEach(function(pid) {
      var p=PLUGINS.find(function(x){return x.id===pid;});
      if(!p) return;
      if(p.css) applyCSS(pid,p.css);
      if(p.jsInit) p.jsInit();
    });

    if(state.customCss) applyCSS('custom',state.customCss);
    if(state.bgUrl) _applyBg(state.bgUrl);
    _initMsgCounter();

    // ── Panel ──────────────────────────────────────────────────────────
    var panel = mk('div',
      'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);'+
      'width:540px;max-height:600px;background:'+C.BG+';color:'+C.TXT+';'+
      'border-radius:14px;box-shadow:0 16px 56px #000000bb,0 0 0 1px #7c6af720;'+
      'z-index:2147483646;display:none;flex-direction:column;'+
      'font-family:"Segoe UI",system-ui,sans-serif;overflow:hidden;');

    var ph=mk('div','display:flex;align-items:center;padding:14px 18px;background:'+C.BG2+';border-bottom:1px solid #ffffff12;flex-shrink:0;');
    var pt=mk('span','font-size:15px;font-weight:700;flex:1;background:linear-gradient(90deg,#7c6af7,#a89df5);-webkit-background-clip:text;-webkit-text-fill-color:transparent;',{textContent:'⚡ Claisum  v'+VERSION});
    var pc=mk('button','background:none;border:none;color:'+C.DIM+';font-size:22px;cursor:pointer;line-height:1;padding:0 4px;border-radius:4px;',{textContent:'×',title:'Schließen (F8)'});
    pc.onmouseenter=function(){pc.style.color=C.TXT;}; pc.onmouseleave=function(){pc.style.color=C.DIM;};
    pc.onclick=close_; ph.appendChild(pt); ph.appendChild(pc);

    var tb=mk('div','display:flex;background:'+C.BG2+';border-bottom:1px solid #ffffff12;flex-shrink:0;');
    var tBtns={};
    [{k:'themes',l:'🎨 Themes'},{k:'plugins',l:'🔌 Plugins'},{k:'tools',l:'🛠 Tools'}].forEach(function(t){
      var b=mk('button','flex:1;padding:10px 0;background:none;border:none;cursor:pointer;font-size:12px;font-weight:600;border-bottom:2px solid transparent;color:'+C.DIM+';',{textContent:t.l});
      b.onclick=function(){switchTab(t.k);}; tBtns[t.k]=b; tb.appendChild(b);
    });

    var pbody=mk('div','flex:1;overflow-y:auto;padding:12px 16px;'); pbody.style.scrollbarWidth='thin';
    var pfoot=mk('div','padding:8px 16px;background:'+C.BG2+';border-top:1px solid #ffffff12;font-size:11px;color:'+C.DIM+';flex-shrink:0;display:flex;align-items:center;gap:8px;');
    pfoot.appendChild(mk('span','flex:1;',{textContent:'F8 öffnen/schließen  •  github.com/'+REPO}));
    pfoot.appendChild(mk('span','color:'+C.DIM+';font-size:10px;',{id:'cl-ctr',textContent:state.msgCount+' heute'}));

    panel.appendChild(ph); panel.appendChild(tb); panel.appendChild(pbody); panel.appendChild(pfoot);

    // helpers
    function switchTab(tab){
      state.tab=tab;
      Object.keys(tBtns).forEach(function(t){
        tBtns[t].style.color=t===tab?C.ACC:C.DIM;
        tBtns[t].style.borderBottom=t===tab?'2px solid '+C.ACC:'2px solid transparent';
      });
      pbody.innerHTML='';
      if(tab==='themes')renderThemes();
      else if(tab==='plugins')renderPlugins();
      else renderTools();
    }
    function mkToggle(on){
      var tr=mk('div','width:38px;height:22px;border-radius:11px;cursor:pointer;position:relative;flex-shrink:0;background:'+(on?C.ACC:'#3a3a52')+';transition:background .2s;');
      var kn=mk('div','position:absolute;top:3px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 1px 4px #0004;transition:left .18s;left:'+(on?'19px':'3px')+';');
      tr.appendChild(kn); tr.__on=on; return tr;
    }
    function setToggle(tr,on){ tr.__on=on; tr.style.background=on?C.ACC:'#3a3a52'; var kn=tr.firstChild; if(kn)kn.style.left=on?'19px':'3px'; }
    function mkCard(children,extra){
      var c=mk('div','display:flex;align-items:center;padding:10px 12px;margin:4px 0;background:'+C.BG3+';border-radius:10px;gap:10px;border:1px solid transparent;transition:border-color .15s;'+(extra||''));
      c.onmouseenter=function(){c.style.borderColor='#7c6af730';}; c.onmouseleave=function(){c.style.borderColor='transparent';};
      children.forEach(function(x){c.appendChild(x);}); return c;
    }
    function mkInfo(name,desc,badge){
      var w=mk('div','flex:1;min-width:0;');
      var nameRow=mk('div','display:flex;align-items:center;gap:6px;');
      nameRow.appendChild(mk('div','font-size:13px;font-weight:600;color:'+C.TXT+';',{textContent:name}));
      if(badge) nameRow.appendChild(mk('span','font-size:9px;background:#7c6af730;color:#a89df5;border-radius:3px;padding:1px 5px;font-weight:700;',{textContent:badge}));
      w.appendChild(nameRow);
      w.appendChild(mk('div','font-size:11px;color:'+C.DIM+';margin-top:2px;',{textContent:desc}));
      return w;
    }
    function mkLabel(text){ return mk('div','font-size:10px;font-weight:700;letter-spacing:.08em;color:'+C.DIM+';text-transform:uppercase;margin:12px 0 4px;padding:0 2px;',{textContent:text}); }
    function mkBtn(label,bg,cb){ var b=mk('button','background:'+bg+';color:#fff;border:none;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:12px;font-weight:600;transition:opacity .15s;',{textContent:label}); b.onmouseenter=function(){b.style.opacity='.85';}; b.onmouseleave=function(){b.style.opacity='1';}; b.onclick=cb; return b; }

    // ── Themes ──────────────────────────────────────────────────────────
    function renderThemes(){
      var hint=mk('div','margin:0 0 10px;padding:10px 12px;background:rgba(124,106,247,0.08);border:1px solid #7c6af730;border-radius:8px;font-size:11px;color:#a89df5;');
      hint.textContent='✅ Base-CSS ist immer aktiv (Scrollbar, Hover-Effekte, Code-Blöcke). Themes ändern zusätzlich die Farben.';
      pbody.appendChild(hint);
      var row=mk('div','margin-bottom:8px;display:flex;justify-content:flex-end;');
      var rb=mk('button','background:none;border:1px solid '+C.DIM+';color:'+C.DIM+';border-radius:6px;padding:4px 12px;cursor:pointer;font-size:11px;',{textContent:'↺ Reset'});
      rb.onmouseenter=function(){rb.style.borderColor=C.TXT;rb.style.color=C.TXT;}; rb.onmouseleave=function(){rb.style.borderColor=C.DIM;rb.style.color=C.DIM;};
      rb.onclick=function(){ removeCSS('theme'); state.theme=null; save('cl_theme',null); document.querySelectorAll('[data-cl-t]').forEach(function(x){setToggle(x,false);}); };
      row.appendChild(rb); pbody.appendChild(row);
      THEMES.forEach(function(t){
        var dot=mk('div','width:18px;height:18px;border-radius:50%;flex-shrink:0;background:'+t.preview+';border:2px solid #ffffff20;box-shadow:0 0 0 1px #fff1;');
        var tr=mkToggle(state.theme===t.id); tr.setAttribute('data-cl-t',t.id);
        tr.onclick=function(){
          var on=!tr.__on;
          if(on){ if(state.theme&&state.theme!==t.id)removeCSS('theme'); state.theme=t.id; save('cl_theme',t.id); applyCSS('theme',t.css); document.querySelectorAll('[data-cl-t]').forEach(function(x){if(x!==tr)setToggle(x,false);}); }
          else{ if(state.theme===t.id){state.theme=null;save('cl_theme',null);removeCSS('theme');} }
          setToggle(tr,on);
        };
        pbody.appendChild(mkCard([dot,mkInfo(t.name,t.desc,t.id==='midnight'?'DEFAULT':''),tr]));
      });
    }

    // ── Plugins ─────────────────────────────────────────────────────────
    function renderPlugins(){
      pbody.appendChild(mkLabel('Hintergrundbild'));
      var bgRow=mk('div','display:flex;gap:6px;margin:4px 0 8px;');
      var bgInp=mk('input','flex:1;background:'+C.BG3+';border:1px solid #ffffff18;color:'+C.TXT+';border-radius:6px;padding:6px 10px;font-size:12px;outline:none;');
      bgInp.placeholder='URL oder CSS-Farbe (#1a1a2e)'; bgInp.value=state.bgUrl||'';
      bgRow.appendChild(bgInp);
      bgRow.appendChild(mkBtn('OK',C.ACC,function(){ state.bgUrl=bgInp.value.trim(); save('cl_bg_url',state.bgUrl); _applyBg(state.bgUrl); }));
      bgRow.appendChild(mkBtn('×','#f04747',function(){ state.bgUrl=''; save('cl_bg_url',''); removeCSS('bg'); bgInp.value=''; }));
      pbody.appendChild(bgRow);

      pbody.appendChild(mkLabel('Plugins'));
      PLUGINS.forEach(function(p){
        var on=state.plugins.indexOf(p.id)>=0;
        var tr=mkToggle(on);
        tr.onclick=function(){
          var nowOn=!tr.__on;
          if(nowOn){ if(state.plugins.indexOf(p.id)<0)state.plugins.push(p.id); if(p.css)applyCSS(p.id,p.css); if(p.jsInit)p.jsInit(); }
          else{ state.plugins=state.plugins.filter(function(x){return x!==p.id;}); if(p.css)removeCSS(p.id); }
          save('cl_plugins',state.plugins); setToggle(tr,nowOn);
        };
        pbody.appendChild(mkCard([mkInfo(p.name,p.desc,p.jsInit?'JS':''),tr]));
      });
    }

    // ── Tools ───────────────────────────────────────────────────────────
    function renderTools(){
      // Accent
      pbody.appendChild(mkLabel('Akzentfarbe'));
      var aRow=mk('div','display:flex;align-items:center;gap:10px;margin:4px 0 8px;');
      var aInp=mk('input','width:44px;height:36px;border:none;border-radius:6px;cursor:pointer;background:none;padding:0;');
      aInp.type='color'; aInp.value=state.accent||'#7c6af7';
      aInp.oninput=function(){ state.accent=aInp.value; save('cl_accent',state.accent); applyCSS('base',BASE_CSS.replace(/#7c6af7/g,state.accent).replace(/#9d8eff/g,state.accent).replace(/#a89df5/g,state.accent).replace(/#cba6f7/g,state.accent)); };
      aRow.appendChild(aInp); aRow.appendChild(mk('span','font-size:12px;color:'+C.DIM+';flex:1;',{textContent:'Akzentfarbe für Scrollbar, Hover, Mentions usw.'}));
      aRow.appendChild(mkBtn('Reset',C.BG3,function(){ state.accent=null; save('cl_accent',null); aInp.value='#7c6af7'; applyCSS('base',BASE_CSS); }));
      pbody.appendChild(aRow);

      // Ping
      pbody.appendChild(mkLabel('Server Ping'));
      var pRow=mk('div','display:flex;align-items:center;gap:10px;margin:4px 0 8px;');
      var pVal=mk('span','font-size:20px;font-weight:700;color:'+STATUS.GREEN+';',{textContent:'—'});
      pRow.appendChild(pVal); pRow.appendChild(mk('span','font-size:12px;color:'+C.DIM+';flex:1;',{textContent:'discord.com Gateway Latenz'}));
      pRow.appendChild(mkBtn('Messen',C.BG3,function(){ pVal.textContent='…'; pVal.style.color=C.DIM; _ping(function(ms){ pVal.textContent=ms<0?'Fehler':ms+'ms'; pVal.style.color=ms<0?STATUS.RED:ms<80?STATUS.GREEN:ms<200?'#f9e2af':STATUS.RED; }); }));
      pbody.appendChild(pRow);

      // Msg counter
      pbody.appendChild(mkLabel('Nachrichten heute'));
      var mRow=mk('div','display:flex;align-items:center;gap:10px;margin:4px 0 8px;');
      var mVal=mk('span','font-size:20px;font-weight:700;color:'+C.ACC+';',{textContent:String(state.msgCount)});
      mRow.appendChild(mVal); mRow.appendChild(mk('span','font-size:12px;color:'+C.DIM+';flex:1;',{textContent:'gesendete Nachrichten (täglich reset)'}));
      mRow.appendChild(mkBtn('Reset',C.BG3,function(){ state.msgCount=0; save('cl_msg_count',0); mVal.textContent='0'; var c=document.getElementById('cl-ctr'); if(c)c.textContent='0 heute'; }));
      pbody.appendChild(mRow);

      // Custom CSS
      pbody.appendChild(mkLabel('Eigenes CSS'));
      var ca=mk('textarea','width:100%;height:110px;background:'+C.BG3+';color:'+C.TXT+';border:1px solid #ffffff18;border-radius:8px;padding:8px 10px;font-family:"Courier New",monospace;font-size:11px;resize:vertical;outline:none;box-sizing:border-box;');
      ca.placeholder='/* Eigenes CSS */\n[class*="message-"] { font-size: 14px !important; }'; ca.value=state.customCss||'';
      pbody.appendChild(ca);
      var cRow=mk('div','display:flex;gap:6px;margin:4px 0 8px;');
      cRow.appendChild(mkBtn('Anwenden',C.ACC,function(){ state.customCss=ca.value; save('cl_custom_css',state.customCss); applyCSS('custom',state.customCss); }));
      cRow.appendChild(mkBtn('Entfernen','#f04747',function(){ state.customCss=''; save('cl_custom_css',''); removeCSS('custom'); ca.value=''; }));
      pbody.appendChild(cRow);

      // Export/Import
      pbody.appendChild(mkLabel('Einstellungen'));
      var sRow=mk('div','display:flex;gap:6px;margin:4px 0;');
      sRow.appendChild(mkBtn('⬇ Exportieren',C.ACC,function(){
        var data=JSON.stringify({theme:state.theme,plugins:state.plugins,customCss:state.customCss,accent:state.accent,bgUrl:state.bgUrl},null,2);
        var a=document.createElement('a'); a.href='data:text/json;charset=utf-8,'+encodeURIComponent(data); a.download='claisum-settings.json'; a.click();
      }));
      var fi=mk('input','display:none;'); fi.type='file'; fi.accept='.json';
      fi.onchange=function(){
        var f=fi.files[0]; if(!f)return;
        var r=new FileReader(); r.onload=function(e){ try{ var d=JSON.parse(e.target.result); if(d.theme!==undefined){state.theme=d.theme;save('cl_theme',d.theme);} if(d.plugins){state.plugins=d.plugins;save('cl_plugins',d.plugins);} if(d.customCss!==undefined){state.customCss=d.customCss;save('cl_custom_css',d.customCss);} if(d.accent!==undefined){state.accent=d.accent;save('cl_accent',d.accent);} if(d.bgUrl!==undefined){state.bgUrl=d.bgUrl;save('cl_bg_url',d.bgUrl);} switchTab('tools'); }catch(err){}};
        r.readAsText(f);
      };
      document.body.appendChild(fi);
      sRow.appendChild(mkBtn('⬆ Importieren',C.BG3,function(){ fi.click(); }));
      pbody.appendChild(sRow);
    }

    // ── FAB ─────────────────────────────────────────────────────────────
    var fab=mk('button',
      'position:fixed;bottom:22px;left:22px;width:46px;height:46px;border-radius:50%;'+
      'background:linear-gradient(135deg,#7c6af7,#a89df5);border:none;cursor:pointer;font-size:20px;'+
      'z-index:2147483647;box-shadow:0 4px 20px #7c6af760,0 0 0 2px #7c6af730;'+
      'transition:transform .15s,box-shadow .15s;',
      {id:'cl-fab',textContent:'⚡',title:'Claisum öffnen (F8)'});
    fab.onmouseenter=function(){fab.style.transform='scale(1.12)';fab.style.boxShadow='0 6px 28px #7c6af780,0 0 0 3px #7c6af750';};
    fab.onmouseleave=function(){fab.style.transform='scale(1)';fab.style.boxShadow='0 4px 20px #7c6af760,0 0 0 2px #7c6af730';};
    fab.onclick=toggle_;

    // ── Status dot ───────────────────────────────────────────────────────
    var dot=mk('div',
      'position:fixed;bottom:16px;right:16px;width:12px;height:12px;'+
      'border-radius:50%;background:'+STATUS.GREEN+';z-index:2147483647;'+
      'box-shadow:0 0 0 2px #ffffff22,0 0 8px '+STATUS.GREEN+'88;transition:background .4s;cursor:default;');
    dot.title='Claisum aktiv';
    function setStatus(col,title){ dot.style.background=col; dot.style.boxShadow='0 0 0 2px #ffffff22,0 0 8px '+col+'88'; if(title)dot.title=title; }

    function open_(){ panel.style.display='flex'; switchTab(state.tab||'themes'); }
    function close_(){ panel.style.display='none'; }
    function toggle_(){ if(panel.style.display==='flex')close_(); else open_(); }

    document.addEventListener('mousedown',function(e){ if(panel.style.display==='flex'&&!panel.contains(e.target)&&e.target!==fab)close_(); },{passive:true});
    function _f8(e){ if(e.key==='F8'){e.preventDefault();e.stopImmediatePropagation();toggle_();} }
    document.addEventListener('keydown',_f8,{capture:true});

    document.body.appendChild(fab);
    document.body.appendChild(dot);
    document.body.appendChild(panel);

    var _obs=new MutationObserver(function(){
      if(!document.body.contains(fab))document.body.appendChild(fab);
      if(!document.body.contains(dot))document.body.appendChild(dot);
      if(!document.body.contains(panel))document.body.appendChild(panel);
    });
    _obs.observe(document.body,{childList:true,subtree:false});

    // Discord version drift warning
    setTimeout(function(){
      try{
        var m=(document.location.href||'').match(/app-(\d+\.\d+\.\d+)/);
        var cur=m?m[1]:null, stored=load('cl_discord_ver',null);
        if(cur){ if(stored&&stored!==cur){ setStatus(STATUS.BLUE,'Discord updated — Claisum Installer → Repair'); fab.title='Discord updated! Repair ausführen.'; } save('cl_discord_ver',cur); }
      }catch(e){}
    },3000);

    // Update check
    setTimeout(function(){
      try{
        var x=new XMLHttpRequest(); x.open('GET','https://api.github.com/repos/'+REPO+'/releases/latest',true);
        x.setRequestHeader('Accept','application/vnd.github+json');
        x.onreadystatechange=function(){ if(x.readyState!==4||x.status!==200)return; try{ var tag=(JSON.parse(x.responseText).tag_name||'').replace(/^v/,''); if(tag&&tag!==VERSION){ setStatus(STATUS.BLUE,'Claisum Update: v'+tag+' verfügbar'); fab.title='Claisum v'+tag+' verfügbar!'; }}catch(e){}};
        x.timeout=8000; x.onerror=function(){setStatus(STATUS.RED,'Netzwerkfehler');}; x.send();
      }catch(e){}
    },6000);
  }

  // ── Init ────────────────────────────────────────────────────────────────
  if(document.body){ buildUI(); }
  else{
    var _done=false;
    function _try(){ if(_done||!document.body)return; _done=true; buildUI(); }
    document.addEventListener('DOMContentLoaded',_try);
    window.addEventListener('load',_try);
    var _p=setInterval(function(){ _try(); if(_done)clearInterval(_p); },80);
    setTimeout(function(){clearInterval(_p);},30000);
  }
})();
