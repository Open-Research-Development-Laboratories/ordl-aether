/**
 * AETHER - Sidebar Navigation
 * Collapsible navigation with view switching
 */

class Sidebar {
  constructor() {
    this.sidebar = document.getElementById('sidebar');
    this.toggle = document.getElementById('sidebar-toggle');
    this.links = document.querySelectorAll('.sidebar-link');
    
    this.init();
  }
  
  init() {
    // Toggle collapse
    this.toggle?.addEventListener('click', () => this.toggleCollapse());
    
    // Navigation links
    this.links.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = link.getAttribute('href')?.substring(1);
        if (target) this.navigate(target);
      });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.metaKey || e.ctrlKey) {
        const key = e.key;
        const map = {
          '1': 'topology',
          '2': 'agents',
          '3': 'timeline',
          '4': 'mentality',
          '5': 'ghosts',
          '6': 'logs'
        };
        if (map[key]) {
          e.preventDefault();
          this.navigate(map[key]);
        }
      }
    });
  }
  
  toggleCollapse() {
    const isCollapsed = this.sidebar?.getAttribute('data-collapsed') === 'true';
    this.sidebar?.setAttribute('data-collapsed', !isCollapsed);
    localStorage.setItem('sidebar-collapsed', !isCollapsed);
  }
  
  navigate(viewName) {
    // Hide all views
    document.querySelectorAll('.view').forEach(view => {
      view.classList.add('hidden');
    });
    
    // Show target view
    const targetView = document.getElementById(viewName + '-view');
    if (targetView) {
      targetView.classList.remove('hidden');
    }
    
    // Update active link
    this.links.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + viewName) {
        link.classList.add('active');
      }
    });
    
    // Update breadcrumbs
    this.updateBreadcrumbs(viewName);
    
    // Trigger view-specific initialization
    if (viewName === 'topology' && window.topology) {
      window.topology.resize();
    }
  }
  
  updateBreadcrumbs(viewName) {
    const breadcrumbActive = document.querySelector('.breadcrumb-item.active span');
    if (breadcrumbActive) {
      const names = {
        'topology': 'Topology View',
        'agents': 'Agent Registry',
        'timeline': 'Temporal Debug',
        'mentality': 'Mentality Panel',
        'ghosts': 'Ghost Fleets',
        'logs': 'System Logs',
        'settings': 'Settings'
      };
      breadcrumbActive.textContent = names[viewName] || viewName;
    }
  }
}

// Context Panel
class ContextPanel {
  constructor() {
    this.panel = document.getElementById('context-panel');
    this.toggle = document.getElementById('context-panel-toggle');
    
    this.init();
  }
  
  init() {
    this.toggle?.addEventListener('click', () => this.toggle());
  }
  
  toggle() {
    const isExpanded = this.panel?.getAttribute('data-expanded') === 'true';
    this.panel?.setAttribute('data-expanded', !isExpanded);
  }
}

// Initialize
const sidebar = new Sidebar();
const contextPanel = new ContextPanel();