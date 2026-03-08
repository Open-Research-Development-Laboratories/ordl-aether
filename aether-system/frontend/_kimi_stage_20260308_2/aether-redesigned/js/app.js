/**
 * AETHER - Main Application
 * Swarm Intelligence Platform
 */

// Application state
const App = {
  version: '2.0.0',
  initialized: false,
  
  init() {
    console.log(`🚀 AETHER v${this.version} initializing...`);
    
    // Initialize all modules
    this.initKeyboardShortcuts();
    this.initTooltips();
    this.initStatusUpdates();
    
    this.initialized = true;
    console.log('✅ AETHER initialized');
  },
  
  initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // ⌘/Ctrl + number for views
      if ((e.metaKey || e.ctrlKey) && !e.shiftKey) {
        const viewMap = {
          '1': 'topology',
          '2': 'agents', 
          '3': 'timeline',
          '4': 'mentality',
          '5': 'ghosts',
          '6': 'logs'
        };
        
        if (viewMap[e.key]) {
          e.preventDefault();
          sidebar?.navigate(viewMap[e.key]);
        }
        
        // Settings
        if (e.key === ',') {
          e.preventDefault();
          sidebar?.navigate('settings');
        }
      }
    });
  },
  
  initTooltips() {
    // Initialize all tooltips
    document.querySelectorAll('[data-tooltip]').forEach(el => {
      el.addEventListener('mouseenter', () => {
        // Tooltip is handled by CSS
      });
    });
  },
  
  initStatusUpdates() {
    // Simulate live status updates
    setInterval(() => {
      this.updateStats();
    }, 3000);
  },
  
  updateStats() {
    // Update topology stats with random variations
    const throughput = document.getElementById('msg-throughput');
    const latency = document.getElementById('latency');
    
    if (throughput) {
      const base = 14.2;
      const variation = (Math.random() - 0.5) * 0.5;
      throughput.textContent = (base + variation).toFixed(1) + 'K/s';
    }
    
    if (latency) {
      const base = 23;
      const variation = Math.floor((Math.random() - 0.5) * 4);
      latency.textContent = (base + variation) + 'ms';
    }
  },
  
  // Deploy fleet configuration
  deploy() {
    console.log('🚀 Deploying fleet configuration...');
    
    // Show loading state
    const btn = document.getElementById('topology-deploy');
    if (btn) {
      const originalText = btn.innerHTML;
      btn.innerHTML = `
        <svg class="btn-icon spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
        </svg>
        Deploying...
      `;
      btn.disabled = true;
      
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
        this.showNotification('Fleet deployed successfully', 'success');
      }, 2000);
    }
  },
  
  // Show notification
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
      position: fixed;
      top: 64px;
      right: 24px;
      padding: 12px 20px;
      background: var(--charcoal-800);
      border: 1px solid var(--charcoal-600);
      border-left: 3px solid ${type === 'success' ? 'var(--status-active)' : 'var(--amber-400)'};
      border-radius: 4px;
      color: var(--cream-100);
      font-size: 14px;
      z-index: 1000;
      animation: slideInRight 0.2s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.2s ease';
      setTimeout(() => notification.remove(), 200);
    }, 3000);
  }
};

// Add notification animations
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
  @keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(notificationStyles);

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});

// Expose to global scope for debugging
window.AETHER = App;