"""Claisum Discord injector — patches discord_desktop_core/index.js"""
import os, glob, shutil, subprocess, sys

VERSION  = "1.0.0.1"
REPO     = "claisum/Claisum.py"
PRELOAD  = "// [Claisum Injected]"

def find_discord_indices():
    bases = []
    if sys.platform == "win32":
        lappdata = os.environ.get("LOCALAPPDATA", "")
        for name in ("Discord", "DiscordPTB", "DiscordCanary"):
            bases.append(os.path.join(lappdata, name))
    else:
        for candidate in [
            os.path.expanduser("~/.config/discord"),
            os.path.expanduser("~/.config/discordptb"),
            "/opt/discord",
            "/usr/lib/discord",
        ]:
            bases.append(candidate)

    indices = []
    for base in bases:
        for pattern in [
            os.path.join(base, "app-*", "modules", "discord_desktop_core-*",
                         "discord_desktop_core", "index.js"),
            os.path.join(base, "modules", "discord_desktop_core-*",
                         "discord_desktop_core", "index.js"),
            os.path.join(base, "resources", "app.asar.unpacked",
                         "node_modules", "discord_desktop_core", "index.js"),
        ]:
            indices.extend(glob.glob(pattern))
    return list(set(indices))

def _build_loader(version=VERSION, repo=REPO):
    return f"""{PRELOAD}
;(function(){{
  const _fs=require('fs'),_path=require('path'),_https=require('https');
  const CL_VER='{version}',REPO='{repo}';
  const jsFile=_path.join(__dirname,'claisum_inject.js');
  function run(code){{
    const go=()=>{{try{{eval(code);}}catch(e){{console.error('[Claisum]',e);}}}};
    if(document.readyState==='loading')window.addEventListener('DOMContentLoaded',()=>setTimeout(go,1500));
    else setTimeout(go,1500);
  }}
  let base='';
  try{{base=_fs.readFileSync(jsFile,'utf8');}}catch(e){{}}
  if(base)run(base);
  try{{
    const req=_https.get({{hostname:'api.github.com',
      path:'/repos/'+REPO+'/releases/latest',
      headers:{{'User-Agent':'Claisum-'+CL_VER,'Accept':'application/vnd.github+json'}}}},res=>{{
      let d='';res.on('data',c=>d+=c);
      res.on('end',()=>{{
        try{{
          const t=(JSON.parse(d).tag_name||'').replace(/^v/,'');
          if(t&&t!==CL_VER){{
            _https.get({{hostname:'raw.githubusercontent.com',
              path:'/'+REPO+'/main/claisum/discord/claisum_inject.js',
              headers:{{'User-Agent':'Claisum-'+CL_VER}}}},r=>{{
              let js='';r.on('data',c=>js+=c);
              r.on('end',()=>{{try{{_fs.writeFileSync(jsFile,js,'utf8');}}catch(e){{}}}});
            }}).on('error',()=>{{}});
          }}
        }}catch(e){{}}
      }});
    }});
    req.setTimeout(8000,()=>req.destroy());
    req.on('error',()=>{{}});
  }}catch(e){{}}
}})();
"""

def inject_into_discord(inject_js_src: str | None = None) -> list[str]:
    """Inject Claisum into all found Discord installations. Returns list of patched paths."""
    indices = find_discord_indices()
    if not indices:
        raise FileNotFoundError("No Discord installation found.")

    patched = []
    for index_path in indices:
        core_dir    = os.path.dirname(index_path)
        inject_dest = os.path.join(core_dir, "claisum_inject.js")

        # Copy inject.js
        if inject_js_src and os.path.exists(inject_js_src):
            shutil.copy2(inject_js_src, inject_dest)

        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()

        if PRELOAD in content:
            # Re-patch (repair mode)
            remove_injection(index_path)
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()

        loader = _build_loader()
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(loader + "\n" + content)
        patched.append(index_path)

    return patched

def remove_injection(index_path: str) -> bool:
    """Remove Claisum injection from index.js. Returns True if removed."""
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    if PRELOAD not in content:
        return False
    lines = content.split("\n")
    start = next((i for i, l in enumerate(lines) if PRELOAD in l), None)
    if start is None:
        return False
    end = start + 1
    while end < len(lines) and lines[end].strip():
        end += 1
    cleaned = "\n".join(lines[end:]).lstrip("\n")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(cleaned)
    return True

def uninstall_from_discord() -> list[str]:
    """Remove injection from all Discord installations."""
    indices = find_discord_indices()
    removed = []
    for index_path in indices:
        core_dir = os.path.dirname(index_path)
        inject_dest = os.path.join(core_dir, "claisum_inject.js")
        if remove_injection(index_path):
            removed.append(index_path)
        try:
            os.remove(inject_dest)
        except FileNotFoundError:
            pass
    return removed

def get_status() -> dict:
    indices = find_discord_indices()
    status = {}
    for p in indices:
        try:
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            status[p] = PRELOAD in content
        except Exception:
            status[p] = None
    return status
