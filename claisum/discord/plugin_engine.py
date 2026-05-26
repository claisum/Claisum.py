"""Built-in plugin implementations."""

# ── Better Notifications ─────────────────────────────────────────────────────

BETTER_NOTIFICATIONS = """
// Better Notifications Plugin v1.0.0
// Enhanced notification sounds and badges

class BetterNotifications {
    start() {
        console.log('[Claisum] Better Notifications enabled');
        this.initAudio();
    }
    
    stop() {
        console.log('[Claisum] Better Notifications disabled');
    }
    
    initAudio() {
        // Enhanced notification handling
        document.addEventListener('notificationReceived', (e) => {
            // Custom notification sound
            const audio = new Audio('data:audio/wav;base64,...');
            audio.play().catch(err => console.error('[Claisum] Sound error:', err));
        });
    }
}

module.exports = BetterNotifications;
"""

# ── Compact Mode ─────────────────────────────────────────────────────────────

COMPACT_MODE = """
// Compact Mode Plugin v1.0.0
// Reduces spacing for a denser message layout

class CompactMode {
    start() {
        console.log('[Claisum] Compact Mode enabled');
        this.injectCSS();
    }
    
    stop() {
        console.log('[Claisum] Compact Mode disabled');
        this.removeCSS();
    }
    
    injectCSS() {
        const style = document.createElement('style');
        style.id = 'compact-mode-style';
        style.textContent = `
            .message-G6aibn {
                margin-bottom: 2px !important;
                padding: 4px 0 !important;
            }
            .messageContent-2qWWxC {
                margin: 2px 0 !important;
            }
            .container-1D34oG {
                padding: 4px 0 !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    removeCSS() {
        const style = document.getElementById('compact-mode-style');
        if (style) style.remove();
    }
}

module.exports = CompactMode;
"""

# ── Message Logger ───────────────────────────────────────────────────────────

MESSAGE_LOGGER = """
// Message Logger Plugin v1.0.0
// Keep a local log of deleted/edited messages

class MessageLogger {
    start() {
        console.log('[Claisum] Message Logger enabled');
        this.initDB();
    }
    
    stop() {
        console.log('[Claisum] Message Logger disabled');
    }
    
    initDB() {
        this.db = indexedDB.open('claisum-message-logs');
        this.db.onupgradeneeded = (e) => {
            const db = e.target.result;
            if (!db.objectStoreNames.contains('messages')) {
                db.createObjectStore('messages', { keyPath: 'id' });
            }
        };
    }
    
    logMessage(msg) {
        if (!this.db) return;
        const store = this.db.transaction(['messages'], 'readwrite').objectStore('messages');
        store.add({
            id: Date.now(),
            content: msg.content,
            author: msg.author,
            timestamp: new Date().toISOString(),
            type: 'message'
        });
    }
}

module.exports = MessageLogger;
"""

BUILTIN_PLUGINS = {
    "better-notifications": {
        "name": "Better Notifications",
        "description": "Enhanced notification sounds and badges",
        "version": "1.0.0",
        "author": "Claisum",
        "code": BETTER_NOTIFICATIONS,
    },
    "compact-mode": {
        "name": "Compact Mode",
        "description": "Reduces spacing for a denser message layout",
        "version": "1.0.0",
        "author": "Claisum",
        "code": COMPACT_MODE,
    },
    "message-logger": {
        "name": "Message Logger",
        "description": "Keep a local log of deleted/edited messages",
        "version": "1.0.0",
        "author": "Claisum",
        "code": MESSAGE_LOGGER,
    },
}
