// Claisum — Discord Injection v6
// Robust multi-strategy init: DOMContentLoaded + poll + load event
(function () {
  'use strict';

  // ── Guard: only run once ─────────────────────────────────────────────────
  if (window.__claisumLoaded) return;
  window.__claisumLoaded = true;

  var VERSION = '1.0.0.1';
  var REPO    = 'claisum/Claisum.py';

  // ── State ─────────────────────────────────────────────────────────────────
  function load(key, def) {
    try { var v = localStorage.getItem(key); return v !== null ? JSON.parse(v) : def; }
    catch(e) { return def; }
  }
  function save(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch(e){} }

  var state = {
    theme   : load('cl_theme',   null),
    plugins : load('cl_plugins', []),
    tab     : 'themes',
  };

  // ── Constants ─────────────────────────────────────────────────────────────
  var C = {
    ACCENT : '#7c6af7', ACC2 : '#6254d6',
    BG : '#1e1e2e', BG2 : '#181825', BG3 : '#313244', BG4 : '#45475a',
    TEXT : '#cdd6f4', DIM : '#6c7086', OK : '#a6e3a1', ERR : '#f38ba8', WARN : '#f9e2af',
  };

  // ── Themes / Plugins ──────────────────────────────────────────────────────
  var THEMES = [
    { id:'midnight',   name:'Midnight',        preview:'#0d0f12', desc:'Deep dark with blue accents',
      css:':root{--background-primary:#0d0f12;--background-secondary:#101316;--background-secondary-alt:#0d0f12;--background-tertiary:#08090b;--channeltextarea-background:#1a1d24;--text-normal:#dcddde;--text-muted:#72767d;--text-link:#5865f2;--header-primary:#ffffff;--header-secondary:#b9bbbe;}' },
    { id:'dracula',    name:'Dracula',          preview:'#282a36', desc:'Classic Dracula color scheme',
      css:':root{--background-primary:#282a36;--background-secondary:#21222c;--background-secondary-alt:#1e1f29;--background-tertiary:#191a21;--channeltextarea-background:#44475a;--text-normal:#f8f8f2;--text-muted:#6272a4;--text-link:#8be9fd;--header-primary:#f8f8f2;--header-secondary:#bd93f9;}' },
    { id:'catppuccin', name:'Catppuccin Mocha', preview:'#1e1e2e', desc:'Soothing pastel theme',
      css:':root{--background-primary:#1e1e2e;--background-secondary:#181825;--background-secondary-alt:#11111b;--background-tertiary:#181825;--channeltextarea-background:#313244;--text-normal:#cdd6f4;--text-muted:#6c7086;--text-link:#89b4fa;--header-primary:#cdd6f4;--header-secondary:#bac2de;}' },
    { id:'nord',       name:'Nord',             preview:'#2e3440', desc:'Arctic north-bluish color palette',
      css:':root{--background-primary:#2e3440;--background-secondary:#272c36;--background-secondary-alt:#21262e;--background-tertiary:#1e2229;--channeltextarea-background:#3b4252;--text-normal:#d8dee9;--text-muted:#4c566a;--text-link:#88c0d0;--header-primary:#eceff4;--header-secondary:#e5e9f0;}' },
    { id:'rose-pine',  name:'Rosé Pine',        preview:'#191724', desc:'Natural pine, rose and gold tones',
      css:':root{--background-primary:#191724;--background-secondary:#1f1d2e;--background-secondary-alt:#191724;--background-tertiary:#191724;--channeltextarea-background:#26233a;--text-normal:#e0def4;--text-muted:#6e6a86;--text-link:#9ccfd8;--header-primary:#e0def4;--header-secondary:#e0def4;}' },
    { id:'gruvbox',    name:'Gruvbox Dark',     preview:'#282828', desc:'Retro groove color scheme',
      css:':root{--background-primary:#282828;--background-secondary:#1d2021;--background-secondary-alt:#1a1a1a;--background-tertiary:#141617;--channeltextarea-background:#3c3836;--text-normal:#ebdbb2;--text-muted:#928374;--text-link:#83a598;--header-primary:#fbf1c7;--header-secondary:#ebdbb2;}' },
    { id:'solarized',  name:'Solarized Dark',   preview:'#002b36', desc:'Classic Solarized dark palette',
      css:':root{--background-primary:#002b36;--background-secondary:#073642;--background-secondary-alt:#001f27;--background-tertiary:#001f27;--channeltextarea-background:#073642;--text-normal:#839496;--text-muted:#586e75;--text-link:#268bd2;--header-primary:#93a1a1;--header-secondary:#839496;}' },
  ];

  var PLUGINS = [
    { id:'compact-mode',       name:'Compact Mode',        desc:'Tighter message layout — more content visible at once',
      css:"[class*='message-']{padding:2px 16px!important;}[class*='contents-']{padding-top:0!important;}[class*='cozyMessage']{min-height:0!important;}" },
    { id:'square-corners',     name:'Square Corners',       desc:'Removes all border-radius — sharp modern look',
      css:'*{border-radius:0!important;}' },
    { id:'big-emoji',          name:'Big Emoji',            desc:'Enlarges solo emoji to 48 px',
      css:"[class*='emoji'][class*='jumboable'],[class*='emojiContainer']{width:48px!important;height:48px!important;}" },
    { id:'hide-game-activity', name:'Hide Game Activity',   desc:'Hides the "playing a game" status bar',
      css:"[class*='activityStatus'],[class*='gameInfo'],[class*='nowPlayingColumn']{display:none!important;}" },
    { id:'hide-avatars',       name:'Hide Avatars',         desc:'Removes all user avatars to reduce visual noise',
      css:"[class*='avatar-'],[class*='avatarWrapper']{display:none!important;}" },
  ];

  // ── CSS helpers ───────────────────────────────────────────────────────────
  function applyCSS(id, css) {
    var el = document.getElementById('cl-' + id);
    if (!el) { el = document.createElement('style'); el.id = 'cl-' + id; document.head.appendChild(el); }
    el.textContent = css;
  }
  function removeCSS(id) { var el = document.getElementById('cl-' + id); if (el) el.remove(); }

  // Apply saved state immediately
  function applyState() {
    if (state.theme) {
      var t = THEMES.find(function(x){ return x.id===state.theme; });
      if (t) applyCSS('theme', t.css);
    }
    state.plugins.forEach(function(pid) {
      var p = PLUGINS.find(function(x){ return x.id===pid; });
      if (p) applyCSS(pid, p.css);
    });
  }

  // ── DOM factory ───────────────────────────────────────────────────────────
  function mk(tag, style, props) {
    var e = document.createElement(tag);
    if (style) e.style.cssText = style;
    if (props) Object.assign(e, props);
    return e;
  }

  // ── Panel ─────────────────────────────────────────────────────────────────
  var panel, fab, _panelBuilt = false;

  function buildUI() {
    if (_panelBuilt) return;
    _panelBuilt = true;

    applyState();

    panel = mk('div',
      'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);' +
      'width:540px;max-height:600px;background:'+C.BG+';color:'+C.TEXT+';' +
      'border-radius:14px;box-shadow:0 12px 48px #00000099;z-index:2147483646;' +
      'display:none;flex-direction:column;font-family:"Segoe UI",system-ui,sans-serif;' +
      'overflow:hidden;user-select:none;');

    // Header
    var ph = mk('div','display:flex;align-items:center;padding:14px 18px;background:'+C.BG2+';border-bottom:1px solid #ffffff14;flex-shrink:0;');
    var pt = mk('span','font-size:15px;font-weight:700;flex:1;letter-spacing:.02em;',{textContent:'\u26a1 Claisum'});
    var pc = mk('button','background:none;border:none;color:'+C.DIM+';font-size:22px;cursor:pointer;line-height:1;padding:2px 4px;border-radius:4px;',{textContent:'\u00d7',title:'Close  (F8)'});
    pc.addEventListener('mouseenter',function(){pc.style.color=C.TEXT;});
    pc.addEventListener('mouseleave',function(){pc.style.color=C.DIM;});
    pc.addEventListener('click',closePanel);
    ph.appendChild(pt); ph.appendChild(pc);

    // Tabs
    var tb = mk('div','display:flex;background:'+C.BG2+';border-bottom:1px solid #ffffff14;flex-shrink:0;');
    var tabBtns = {};
    ['themes','plugins'].forEach(function(tab) {
      var btn = mk('button','flex:1;padding:10px 0;background:none;border:none;cursor:pointer;font-size:13px;font-weight:600;transition:color .15s,border-bottom .15s;border-bottom:2px solid transparent;',
        {textContent:tab==='themes'?'Themes ('+THEMES.length+')':'Plugins ('+PLUGINS.length+')'});
      btn.addEventListener('click',function(){switchTab(tab);});
      tabBtns[tab]=btn; tb.appendChild(btn);
    });

    var pb = mk('div','flex:1;overflow-y:auto;padding:12px 16px;');
    pb.style.scrollbarWidth='thin';

    var pf = mk('div','padding:8px 16px;background:'+C.BG2+';border-top:1px solid #ffffff14;font-size:11px;color:'+C.DIM+';flex-shrink:0;display:flex;align-items:center;');
    var pfL = mk('span',null,{textContent:'Claisum v'+VERSION+'  \u2014  F8 to toggle'});
    var pfR = mk('a','margin-left:auto;color:'+C.DIM+';text-decoration:none;cursor:pointer;',
      {textContent:'github.com/claisum/Claisum.py',href:'https://github.com/'+REPO,target:'_blank'});
    pfR.addEventListener('mouseenter',function(){pfR.style.color=C.TEXT;});
    pfR.addEventListener('mouseleave',function(){pfR.style.color=C.DIM;});
    pf.appendChild(pfL); pf.appendChild(pfR);

    panel.appendChild(ph); panel.appendChild(tb); panel.appendChild(pb); panel.appendChild(pf);

    // ── Tab rendering ──────────────────────────────────────────────────────
    function switchTab(tab) {
      state.tab = tab;
      Object.keys(tabBtns).forEach(function(t) {
        var on = (t===tab);
        tabBtns[t].style.color = on ? C.ACCENT : C.DIM;
        tabBtns[t].style.borderBottom = on ? '2px solid '+C.ACCENT : '2px solid transparent';
      });
      pb.innerHTML = '';
      (tab==='themes' ? renderThemes : renderPlugins)();
    }

    function renderThemes() {
      var resetRow = mk('div','margin-bottom:10px;display:flex;justify-content:flex-end;');
      var resetBtn = mk('button','background:none;border:1px solid '+C.DIM+';color:'+C.DIM+';border-radius:6px;padding:4px 12px;cursor:pointer;font-size:11px;');
      resetBtn.textContent = '\u21ba Reset theme';
      resetBtn.addEventListener('mouseenter',function(){resetBtn.style.borderColor=C.TEXT;resetBtn.style.color=C.TEXT;});
      resetBtn.addEventListener('mouseleave',function(){resetBtn.style.borderColor=C.DIM;resetBtn.style.color=C.DIM;});
      resetBtn.addEventListener('click',function(){
        if(state.theme) removeCSS('theme');
        state.theme=null; save('cl_theme',null);
        document.querySelectorAll('[data-cl-theme]').forEach(function(tog){_setToggle(tog,false);});
      });
      resetRow.appendChild(resetBtn); pb.appendChild(resetRow);
      THEMES.forEach(function(t){ pb.appendChild(themeCard(t)); });
    }

    function themeCard(t) {
      var isOn = (state.theme===t.id);
      var card = mk('div','display:flex;align-items:center;padding:10px 12px;margin:4px 0;background:'+C.BG3+';border-radius:10px;gap:10px;border:1px solid transparent;transition:border-color .15s;');
      card.addEventListener('mouseenter',function(){card.style.borderColor='#ffffff18';});
      card.addEventListener('mouseleave',function(){card.style.borderColor='transparent';});
      var dot = mk('div','width:18px;height:18px;border-radius:50%;flex-shrink:0;background:'+t.preview+';border:2px solid #ffffff20;');
      var info = mk('div','flex:1;min-width:0;');
      info.appendChild(mk('div','font-size:13px;font-weight:600;color:'+C.TEXT+';',{textContent:t.name}));
      info.appendChild(mk('div','font-size:11px;color:'+C.DIM+';margin-top:2px;',{textContent:t.desc}));
      var tog = _makeToggle(isOn,function(on){
        if(on){
          if(state.theme&&state.theme!==t.id) removeCSS('theme');
          state.theme=t.id; save('cl_theme',t.id); applyCSS('theme',t.css);
          document.querySelectorAll('[data-cl-theme]').forEach(function(el){if(el!==tog)_setToggle(el,false);});
        } else {
          if(state.theme===t.id){state.theme=null;save('cl_theme',null);removeCSS('theme');}
        }
      });
      tog.setAttribute('data-cl-theme',t.id);
      card.appendChild(dot); card.appendChild(info); card.appendChild(tog);
      return card;
    }

    function renderPlugins() {
      PLUGINS.forEach(function(p){ pb.appendChild(pluginCard(p)); });
    }

    function pluginCard(p) {
      var isOn = (state.plugins.indexOf(p.id)>=0);
      var card = mk('div','display:flex;align-items:center;padding:10px 12px;margin:4px 0;background:'+C.BG3+';border-radius:10px;gap:10px;border:1px solid transparent;transition:border-color .15s;');
      card.addEventListener('mouseenter',function(){card.style.borderColor='#ffffff18';});
      card.addEventListener('mouseleave',function(){card.style.borderColor='transparent';});
      var info = mk('div','flex:1;min-width:0;');
      info.appendChild(mk('div','font-size:13px;font-weight:600;color:'+C.TEXT+';',{textContent:p.name}));
      info.appendChild(mk('div','font-size:11px;color:'+C.DIM+';margin-top:2px;',{textContent:p.desc}));
      var tog = _makeToggle(isOn,function(on){
        if(on){if(state.plugins.indexOf(p.id)<0)state.plugins.push(p.id);applyCSS(p.id,p.css);}
        else{state.plugins=state.plugins.filter(function(x){return x!==p.id;});removeCSS(p.id);}
        save('cl_plugins',state.plugins);
      });
      card.appendChild(info); card.appendChild(tog);
      return card;
    }

    function _makeToggle(active, onChange) {
      var track = mk('div','width:38px;height:22px;border-radius:11px;cursor:pointer;transition:background .2s;flex-shrink:0;position:relative;background:'+(active?C.ACCENT:'#3a3a52')+';');
      var knob  = mk('div','position:absolute;top:3px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 1px 4px #0004;transition:left .18s;left:'+(active?'19px':'3px')+';');
      track.appendChild(knob); track.__clActive = active;
      track.addEventListener('click',function(){
        track.__clActive = !track.__clActive;
        _setToggle(track, track.__clActive);
        try{onChange(track.__clActive);}catch(e){}
      });
      return track;
    }
    function _setToggle(track, on) {
      track.__clActive = on;
      track.style.background = on ? C.ACCENT : '#3a3a52';
      var knob = track.firstChild;
      if (knob) knob.style.left = on ? '19px' : '3px';
    }

    // ── FAB ──────────────────────────────────────────────────────────────────
    fab = mk('button',
      'position:fixed;bottom:22px;left:22px;width:46px;height:46px;' +
      'border-radius:50%;background:'+C.ACCENT+';border:none;cursor:pointer;' +
      'font-size:20px;z-index:2147483647;' +
      'box-shadow:0 4px 16px #0005,0 0 0 2px #ffffff18;' +
      'transition:transform .15s,box-shadow .15s;',
      {textContent:'\u26a1',title:'Claisum Settings  (F8)'});
    fab.addEventListener('mouseenter',function(){fab.style.transform='scale(1.14)';fab.style.boxShadow='0 6px 24px #0007,0 0 0 2px '+C.ACCENT+'66';});
    fab.addEventListener('mouseleave',function(){fab.style.transform='scale(1)';fab.style.boxShadow='0 4px 16px #0005,0 0 0 2px #ffffff18';});
    fab.addEventListener('click',togglePanel);

    // ── Open/close ────────────────────────────────────────────────────────────
    function openPanel() {
      panel.style.display='flex'; switchTab(state.tab||'themes'); fab.style.background=C.ACC2;
    }
    function closePanel() {
      panel.style.display='none'; fab.style.background=C.ACCENT;
    }
    function togglePanel() {
      if(panel.style.display==='flex') closePanel(); else openPanel();
    }

    document.addEventListener('mousedown',function(e){
      if(panel.style.display==='flex'&&!panel.contains(e.target)&&e.target!==fab) closePanel();
    },{passive:true});

    // F8 — capture phase so Discord can't block it
    function _f8(e) {
      if (e.key==='F8') { e.preventDefault(); e.stopPropagation(); togglePanel(); }
    }
    document.addEventListener('keydown', _f8, true);
    window.addEventListener('keydown', _f8, true);

    // Mount
    document.body.appendChild(fab);
    document.body.appendChild(panel);

    // ── Discord update detector ────────────────────────────────────────────
    setTimeout(function(){
      try {
        var href = (document.location&&document.location.href)||'';
        var match = href.match(/app-(\d+\.\d+\.\d+)/);
        var discordVer = match ? match[1] : null;
        var storedVer = load('cl_discord_ver', null);
        if (discordVer) {
          if (storedVer && storedVer!==discordVer) {
            var badge = mk('span',
              'position:absolute;top:-5px;right:-5px;background:#f9e2af;color:#1e1e2e;' +
              'border-radius:50%;width:18px;height:18px;font-size:12px;font-weight:900;' +
              'display:flex;align-items:center;justify-content:center;pointer-events:none;',
              {id:'cl-repair-badge',textContent:'\u26a0'});
            if (!document.getElementById('cl-repair-badge')) fab.appendChild(badge);
            fab.title='Discord updated! Re-run Claisum installer → Repair.';
            var toast = mk('div',
              'position:fixed;bottom:80px;left:16px;background:#313244;color:#f9e2af;' +
              'border-radius:10px;padding:10px 16px;font-size:12px;font-weight:600;' +
              'box-shadow:0 4px 16px #0007;z-index:2147483645;max-width:280px;line-height:1.5;');
            toast.textContent = '\u26a0\ufe0f Discord updated to '+discordVer+'. Re-run Claisum installer \u2192 Repair.';
            document.body.appendChild(toast);
            setTimeout(function(){try{toast.remove();}catch(e){}},9000);
          }
          save('cl_discord_ver', discordVer);
        }
      } catch(e){}
    }, 2500);

    // ── Claisum version check ──────────────────────────────────────────────
    setTimeout(function(){
      try {
        var xhr = new XMLHttpRequest();
        xhr.open('GET','https://api.github.com/repos/'+REPO+'/releases/latest',true);
        xhr.setRequestHeader('Accept','application/vnd.github+json');
        xhr.onreadystatechange = function(){
          if(xhr.readyState!==4||xhr.status!==200) return;
          try {
            var tag = (JSON.parse(xhr.responseText).tag_name||'').replace(/^v/,'');
            if(tag&&tag!==VERSION&&!document.getElementById('cl-repair-badge')){
              var b=mk('span','position:absolute;top:-4px;right:-4px;background:#f04747;color:#fff;border-radius:50%;width:16px;height:16px;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;pointer-events:none;',{textContent:'!'});
              fab.appendChild(b);
              fab.title='Claisum v'+tag+' available — github.com/'+REPO+'/releases';
            }
          }catch(e){}
        };
        xhr.timeout=8000; xhr.send();
      }catch(e){}
    }, 5000);
  }

  // ══ Multi-strategy init ═══════════════════════════════════════════════════
  // Strategy 1: body already exists (renderer context where page is loaded)
  if (document.body) {
    buildUI();
    return;
  }

  // Strategy 2: DOMContentLoaded (preload context, page hasn't loaded yet)
  var _done = false;
  function _tryBuild() {
    if (_done || !document.body) return;
    _done = true;
    buildUI();
  }

  document.addEventListener('DOMContentLoaded', _tryBuild);
  window.addEventListener('load', _tryBuild);

  // Strategy 3: poll every 100 ms for up to 30 s (belt-and-suspenders)
  var _poll = setInterval(function(){
    _tryBuild();
    if (_done) clearInterval(_poll);
  }, 100);
  setTimeout(function(){ clearInterval(_poll); }, 30000);

})();
