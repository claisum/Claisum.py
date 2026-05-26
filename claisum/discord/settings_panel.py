"""Discord settings panel — injected into Discord UI."""

DISCORD_SETTINGS_PANEL = """
// Claisum Settings Panel - Injected into Discord
// This creates a custom settings tab for themes and plugins

class ClaisumSettingsPanel {
    constructor() {
        this.settings_html = `
<div id="claisum-settings-panel" style="display: none; padding: 20px;">
    <h2 style="color: #ffffff; margin-bottom: 20px;">⚙️ Claisum Settings</h2>
    
    <!-- Themes Section -->
    <div style="margin-bottom: 30px; border: 1px solid #313244; padding: 15px; border-radius: 8px;">
        <h3 style="color: #cdd6f4; margin-bottom: 15px;">🎨 Themes</h3>
        <div id="claisum-themes-list" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">
            <!-- Themes will be inserted here -->
        </div>
    </div>
    
    <!-- Plugins Section -->
    <div style="margin-bottom: 30px; border: 1px solid #313244; padding: 15px; border-radius: 8px;">
        <h3 style="color: #cdd6f4; margin-bottom: 15px;">🔌 Plugins</h3>
        <div id="claisum-plugins-list" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">
            <!-- Plugins will be inserted here -->
        </div>
    </div>
    
    <!-- Status Section -->
    <div style="border: 1px solid #313244; padding: 15px; border-radius: 8px; background: #181825;">
        <h3 style="color: #cdd6f4; margin-bottom: 10px;">📊 Status</h3>
        <p id="claisum-status" style="color: #6c7086; font-size: 14px;">
            Initializing...
        </p>
    </div>
</div>
`;
    }
    
    start() {
        console.log('[Claisum] Settings Panel starting...');
        this.injectSettings();
        this.loadThemes();
        this.loadPlugins();
        this.setupObserver();
    }
    
    stop() {
        console.log('[Claisum] Settings Panel stopping...');
        const panel = document.getElementById('claisum-settings-panel');
        if (panel) panel.remove();
    }
    
    injectSettings() {
        // Wait for Discord to load, then inject our panel
        const interval = setInterval(() => {
            const settingsBtn = document.querySelector('[aria-label="User Settings"]');
            if (settingsBtn) {
                clearInterval(interval);
                this.createSettingsTab();
            }
        }, 500);
    }
    
    createSettingsTab() {
        // Insert settings HTML into Discord
        const container = document.body;
        const panel = document.createElement('div');
        panel.innerHTML = this.settings_html;
        container.appendChild(panel);
        
        // Add click listener to show/hide
        this.addTabButton();
    }
    
    addTabButton() {
        // Add Claisum button to settings sidebar
        const settingsList = document.querySelector('[class*="side-8zPYf6"]');
        if (settingsList) {
            const btn = document.createElement('div');
            btn.innerHTML = '🎨 Claisum';
            btn.style.cssText = 'padding: 10px; cursor: pointer; color: #7c6af7; margin: 10px 0;';
            btn.onclick = () => {
                const panel = document.getElementById('claisum-settings-panel');
                panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            };
            settingsList.appendChild(btn);
        }
    }
    
    loadThemes() {
        const themesList = document.getElementById('claisum-themes-list');
        if (!themesList) return;
        
        // Fetch available themes
        fetch('http://localhost:7777/api/themes')
            .then(r => r.json())
            .then(themes => {
                themesList.innerHTML = themes.map(t => `
                    <div style="padding: 12px; background: #313244; border-radius: 6px; cursor: pointer; transition: all 0.2s;"
                         onmouseover="this.style.background='#45475a'"
                         onmouseout="this.style.background='#313244'"
                         onclick="fetch('http://localhost:7777/api/themes/apply/${t.id}')">
                        <div style="color: #ffffff; font-weight: bold;">${t.name}</div>
                        <div style="color: #6c7086; font-size: 12px;">${t.description}</div>
                    </div>
                `).join('');
            });
    }
    
    loadPlugins() {
        const pluginsList = document.getElementById('claisum-plugins-list');
        if (!pluginsList) return;
        
        // Fetch available plugins
        fetch('http://localhost:7777/api/plugins')
            .then(r => r.json())
            .then(plugins => {
                pluginsList.innerHTML = plugins.map(p => `
                    <div style="padding: 12px; background: #313244; border-radius: 6px; cursor: pointer; transition: all 0.2s;"
                         onmouseover="this.style.background='#45475a'"
                         onmouseout="this.style.background='#313244'">
                        <input type="checkbox" id="plugin-${p.id}" 
                               onchange="fetch('http://localhost:7777/api/plugins/${this.checked ? 'enable' : 'disable'}/${p.id}')">
                        <label for="plugin-${p.id}" style="color: #ffffff; margin-left: 8px;">${p.name}</label>
                        <div style="color: #6c7086; font-size: 12px; margin-top: 4px;">${p.description}</div>
                    </div>
                `).join('');
            });
    }
    
    setupObserver() {
        // Watch for Discord UI changes
        const observer = new MutationObserver(() => {
            if (!document.getElementById('claisum-settings-panel')) {
                this.createSettingsTab();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }
}

module.exports = ClaisumSettingsPanel;
"""
