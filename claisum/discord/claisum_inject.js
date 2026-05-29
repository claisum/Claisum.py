// Claisum — Discord Injection v4
// Safe: typeof window check first, all DOM work deferred 2.5s, full try-catch
(function () {
  'use strict';
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  if (window.__claisumLoaded) return;
  window.__claisumLoaded = true;

  setTimeout(function () {
    try { init(); } catch (e) { console.error('[Claisum] init error:', e); }
  }, 2500);

  function init() {
    var ACCENT = '#7c6af7', BG = '#1e1e2e', BG2 = '#181825', BG3 = '#313244';
    var TEXT = '#cdd6f4', DIM = '#6c7086';

    var activeTheme    = null;
    var enabledPlugins = [];
    var customThemes   = [];
    var currentTab     = 'themes';

    try { activeTheme    = localStorage.getItem('cl_theme'); } catch(e){}
    try { enabledPlugins = JSON.parse(localStorage.getItem('cl_plugins') || '[]'); } catch(e){}
    try { customThemes   = JSON.parse(localStorage.getItem('cl_cthemes') || '[]'); } catch(e){}

    var THEMES = [
      { id:'midnight', name:'Midnight', preview:'#0d0f12', desc:'Deep dark with blue accents',
        css:':root{--background-primary:#0d0f12;--background-secondary:#101316;--background-tertiary:#08090b;--channeltextarea-background:#1a1d24;--text-normal:#dcddde;--text-muted:#72767d;--header-primary:#ffffff;}' },
      { id:'dracula', name:'Dracula', preview:'#282a36', desc:'Classic Dracula colors',
        css:':root{--background-primary:#282a36;--background-secondary:#21222c;--background-tertiary:#191a21;--channeltextarea-background:#44475a;--text-normal:#f8f8f2;--text-muted:#6272a4;--header-primary:#f8f8f2;}' },
      { id:'catppuccin', name:'Catppuccin Mocha', preview:'#1e1e2e', desc:'Soothing pastel theme',
        css:':root{--background-primary:#1e1e2e;--background-secondary:#181825;--background-tertiary:#11111b;--channeltextarea-background:#313244;--text-normal:#cdd6f4;--text-muted:#6c7086;--header-primary:#cdd6f4;}' },
      { id:'nord', name:'Nord', preview:'#2e3440', desc:'Arctic north-bluish theme',
        css:':root{--background-primary:#2e3440;--background-secondary:#272c36;--background-tertiary:#1e2229;--channeltextarea-background:#3b4252;--text-normal:#d8dee9;--text-muted:#4c566a;--header-primary:#eceff4;}' },
      { id:'rose-pine', name:'Rose Pine', preview:'#191724', desc:'Natural pine and soho vibes',
        css:':root{--background-primary:#191724;--background-secondary:#1f1d2e;--background-tertiary:#191724;--channeltextarea-background:#26233a;--text-normal:#e0def4;--text-muted:#6e6a86;--header-primary:#e0def4;}' },
    ];

    var PLUGINS = [
      { id:'compact', name:'Compact Mode', desc:'Reduces message spacing',
        css:'.message-2CShn3{padding:2px 16px !important;}.contents-2MsGLg{padding-top:0 !important;}' },
      { id:'noborder', name:'No Border Radius', desc:'Makes everything square',
        css:'*{border-radius:0 !important;}' },
      { id:'bigemoji', name:'Big Emoji', desc:'Makes solo emojis larger',
        css:'.emoji.jumboable{width:48px !important;height:48px !important;}' },
    ];

    function injectCSS(id, css) {
      try {
        var old = document.getElementById('cl-css-' + id);
        if (old) old.remove();
        var s = document.createElement('style');
        s.id = 'cl-css-' + id;
        s.textContent = css;
        document.head.appendChild(s);
      } catch(e) {}
    }
    function removeCSS(id) {
      try { var el = document.getElementById('cl-css-'+id); if (el) el.remove(); } catch(e){} }

    if (activeTheme) {
      var t = THEMES.find(function(x){return x.id===activeTheme;});
      if (t) injectCSS('theme', t.css);
    }
    enabledPlugins.forEach(function(pid) {
      var p = PLUGINS.find(function(x){return x.id===pid;});
      if (p && p.css) injectCSS(pid, p.css);
    });

    function el(tag, css, extra) {
      try {
        var e = document.createElement(tag);
        if (css) e.style.cssText = css;
        if (extra) Object.assign(e, extra);
        return e;
      } catch(e) { return document.createElement('div'); }
    }

    var panel = el('div',
      'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);' +
      'width:520px;max-height:580px;background:'+BG+';color:'+TEXT+';' +
      'border-radius:12px;box-shadow:0 8px 32px #0006;z-index:99999;' +
      'display:none;flex-direction:column;font-family:sans-serif;overflow:hidden;');

    var pHdr = el('div',
      'display:flex;align-items:center;padding:16px 20px;background:'+BG2+';' +
      'border-bottom:1px solid #ffffff18;flex-shrink:0;');
    var pTitle = el('span','font-size:16px;font-weight:700;flex:1;',{textContent:'\u26a1 Claisum'});
    var pClose = el('button',
      'background:none;border:none;color:'+DIM+';font-size:20px;cursor:pointer;padding:0 4px;',
      {textContent:'\u00d7'});
    pClose.onclick = function() { panel.style.display='none'; };
    pHdr.appendChild(pTitle); pHdr.appendChild(pClose);

    var tabBar = el('div',
      'display:flex;background:'+BG2+';border-bottom:1px solid #ffffff18;flex-shrink:0;');
    ['themes','plugins'].forEach(function(tab) {
      var btn = el('button',
        'flex:1;padding:10px;background:none;border:none;cursor:pointer;' +
        'font-size:13px;font-weight:600;transition:all .15s;',
        {textContent:tab==='themes'?'Themes':'Plugins'});
      btn.id = 'cl-tab-'+tab;
      btn.onclick = function() { showTab(tab); };
      tabBar.appendChild(btn);
    });

    var pBody = el('div','flex:1;overflow-y:auto;padding:16px;');
    var pFoot = el('div',
      'padding:10px 16px;background:'+BG2+';border-top:1px solid #ffffff18;' +
      'font-size:11px;color:'+DIM+';flex-shrink:0;',
      {textContent:'Claisum v4 \u2014 github.com/claisum/Claisum.py'});

    panel.appendChild(pHdr);
    panel.appendChild(tabBar);
    panel.appendChild(pBody);
    panel.appendChild(pFoot);

    function showTab(tab) {
      try {
        currentTab = tab;
        ['themes','plugins'].forEach(function(t) {
          var btn = document.getElementById('cl-tab-'+t);
          if (!btn) return;
          btn.style.color = t===tab ? ACCENT : DIM;
          btn.style.borderBottom = t===tab ? '2px solid '+ACCENT : '2px solid transparent';
        });
        pBody.innerHTML = '';
        if (tab==='themes') renderThemes();
        else renderPlugins();
      } catch(e) { console.error('[Claisum] showTab:', e); }
    }

    function card(label, sub, rightEl) {
      try {
        var c = el('div',
          'display:flex;align-items:center;padding:10px 12px;margin:4px 0;' +
          'background:'+BG3+';border-radius:8px;');
        var txt = el('div','flex:1;');
        txt.appendChild(el('div','font-size:13px;font-weight:600;color:'+TEXT+';',{textContent:label}));
        txt.appendChild(el('div','font-size:11px;color:'+DIM+';margin-top:2px;',{textContent:sub}));
        c.appendChild(txt);
        if (rightEl) c.appendChild(rightEl);
        return c;
      } catch(e) { return document.createElement('div'); }
    }

    function toggle(active, onChange) {
      try {
        var w = el('div',
          'width:36px;height:20px;border-radius:10px;cursor:pointer;' +
          'transition:background .2s;flex-shrink:0;position:relative;' +
          'background:'+(active?ACCENT:'#4a4a5a')+';');
        var k = el('div',
          'position:absolute;top:3px;width:14px;height:14px;border-radius:50%;' +
          'background:#fff;transition:left .2s;left:'+(active?'19px':'3px')+';');
        w.appendChild(k);
        w.onclick = function() {
          active = !active;
          w.style.background = active ? ACCENT : '#4a4a5a';
          k.style.left = active ? '19px' : '3px';
          try { onChange(active); } catch(e){}
        };
        return w;
      } catch(e) { return document.createElement('div'); }
    }

    function renderThemes() {
      try {
        var resetRow = el('div','margin-bottom:8px;text-align:right;');
        var resetBtn = el('button',
          'background:none;border:1px solid '+DIM+';color:'+DIM+';' +
          'border-radius:6px;padding:4px 10px;cursor:pointer;font-size:11px;',
          {textContent:'Reset to Default'});
        resetBtn.onclick = function() {
          activeTheme = null;
          try { localStorage.removeItem('cl_theme'); } catch(e){}
          removeCSS('theme');
          renderThemes();
        };
        resetRow.appendChild(resetBtn);
        pBody.appendChild(resetRow);

        THEMES.concat(customThemes).forEach(function(t) {
          var isOn = activeTheme===t.id;
          var tog = toggle(isOn, function(on) {
            if (on) {
              activeTheme = t.id;
              try { localStorage.setItem('cl_theme', t.id); } catch(e){}
              injectCSS('theme', t.css);
            } else if (activeTheme===t.id) {
              activeTheme = null;
              try { localStorage.removeItem('cl_theme'); } catch(e){}
              removeCSS('theme');
            }
            renderThemes();
          });
          var preview = el('div',
            'width:16px;height:16px;border-radius:50%;margin-right:8px;flex-shrink:0;' +
            'background:'+(t.preview||BG3)+';border:2px solid #ffffff20;');
          var c = card(t.name, t.desc||'', tog);
          c.insertBefore(preview, c.firstChild);
          pBody.appendChild(c);
        });
      } catch(e) { console.error('[Claisum] renderThemes:', e); }
    }

    function renderPlugins() {
      try {
        PLUGINS.forEach(function(p) {
          var isOn = enabledPlugins.indexOf(p.id)>=0;
          var tog = toggle(isOn, function(on) {
            if (on) {
              if (enabledPlugins.indexOf(p.id)<0) enabledPlugins.push(p.id);
              if (p.css) injectCSS(p.id, p.css);
            } else {
              enabledPlugins = enabledPlugins.filter(function(x){return x!==p.id;});
              if (p.css) removeCSS(p.id);
            }
            try { localStorage.setItem('cl_plugins', JSON.stringify(enabledPlugins)); } catch(e){}
          });
          pBody.appendChild(card(p.name, p.desc, tog));
        });
      } catch(e) { console.error('[Claisum] renderPlugins:', e); }
    }

    var fab = el('button',
      'position:fixed;bottom:20px;left:20px;width:44px;height:44px;' +
      'border-radius:50%;background:'+ACCENT+';border:none;cursor:pointer;' +
      'font-size:20px;z-index:99998;box-shadow:0 4px 12px #0004;' +
      'transition:transform .15s;',
      {textContent:'\u26a1', title:'Claisum Settings'});
    fab.onmouseenter = function() { fab.style.transform='scale(1.12)'; };
    fab.onmouseleave = function() { fab.style.transform='scale(1)'; };
    fab.onclick = function() {
      try {
        if (panel.style.display!=='flex') {
          panel.style.display='flex';
          showTab('themes');
        } else {
          panel.style.display='none';
        }
      } catch(e){}
    };

    document.addEventListener('mousedown', function(e) {
      try {
        if (panel.style.display==='flex' && !panel.contains(e.target) && e.target!==fab)
          panel.style.display='none';
      } catch(e){}
    });

    try {
      document.body.appendChild(fab);
      document.body.appendChild(panel);
    } catch(e) { console.error('[Claisum] body append:', e); }
  }
})();
