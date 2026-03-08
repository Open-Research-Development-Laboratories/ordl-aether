/**
 * AETHER - Command Palette
 * ⌘K fuzzy search interface
 */

class CommandPalette {
  constructor() {
    this.element = document.getElementById('command-palette');
    this.input = document.getElementById('command-input');
    this.results = document.getElementById('command-results');
    this.trigger = document.getElementById('search-trigger');
    
    this.commands = [
      { id: 'topology', title: 'Open Topology View', description: 'View swarm network visualization', shortcut: '⌘1' },
      { id: 'agents', title: 'Open Agent Registry', description: 'Manage fleet agents', shortcut: '⌘2' },
      { id: 'timeline', title: 'Open Timeline', description: 'Temporal debugging interface', shortcut: '⌘3' },
      { id: 'mentality', title: 'Open Mentality Panel', description: 'Configure fleet behavior', shortcut: '⌘4' },
      { id: 'ghosts', title: 'Open Ghost Fleets', description: 'Test shadow deployments', shortcut: '⌘5' },
      { id: 'logs', title: 'Open System Logs', description: 'View fleet activity logs', shortcut: '⌘6' },
      { id: 'settings', title: 'Open Settings', description: 'Configure system preferences', shortcut: '⌘,' },
      { id: 'deploy', title: 'Deploy Fleet', description: 'Push configuration to all agents', shortcut: '⌘D' },
      { id: 'reset', title: 'Reset Topology', description: 'Reset swarm visualization', shortcut: '⌘R' },
      { id: 'save', title: 'Save Scenario', description: 'Save current state as test case', shortcut: '⌘S' },
    ];
    
    this.selectedIndex = -1;
    this.filteredCommands = [];
    
    this.init();
  }
  
  init() {
    // Keyboard shortcut ⌘K or Ctrl+K
    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        this.open();
      }
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });
    
    // Click trigger
    this.trigger?.addEventListener('click', () => this.open());
    
    // Close on overlay click
    this.element?.querySelector('[data-close-palette]')?.addEventListener('click', () => this.close());
    
    // Input handling
    this.input?.addEventListener('input', (e) => this.filter(e.target.value));
    this.input?.addEventListener('keydown', (e) => this.handleKeydown(e));
  }
  
  open() {
    this.element?.classList.remove('hidden');
    this.input?.focus();
    this.input.value = '';
    this.filter('');
  }
  
  close() {
    this.element?.classList.add('hidden');
    this.selectedIndex = -1;
  }
  
  isOpen() {
    return !this.element?.classList.contains('hidden');
  }
  
  filter(query) {
    const q = query.toLowerCase().trim();
    
    if (!q) {
      this.filteredCommands = this.commands;
    } else {
      this.filteredCommands = this.commands.filter(cmd => 
        cmd.title.toLowerCase().includes(q) ||
        cmd.description.toLowerCase().includes(q)
      );
    }
    
    this.selectedIndex = this.filteredCommands.length > 0 ? 0 : -1;
    this.render();
  }
  
  handleKeydown(e) {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredCommands.length - 1);
      this.render();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
      this.render();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (this.selectedIndex >= 0) {
        this.execute(this.filteredCommands[this.selectedIndex]);
      }
    }
  }
  
  execute(command) {
    this.close();
    
    // Navigate to view
    const viewId = command.id + '-view';
    const view = document.getElementById(viewId);
    if (view) {
      document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
      view.classList.remove('hidden');
      
      // Update sidebar
      document.querySelectorAll('.sidebar-link').forEach(link => link.classList.remove('active'));
      const sidebarLink = document.querySelector(`.sidebar-link[href="#${command.id}"]`);
      if (sidebarLink) sidebarLink.classList.add('active');
    }
    
    // Execute action
    if (command.id === 'deploy') {
      alert('Deploying fleet configuration...');
    } else if (command.id === 'reset') {
      window.topology?.reset();
    } else if (command.id === 'save') {
      alert('Scenario saved!');
    }
  }
  
  render() {
    if (!this.results) return;
    
    this.results.innerHTML = this.filteredCommands.map((cmd, i) => `
      <div class="command-item ${i === this.selectedIndex ? 'selected' : ''}" data-index="${i}">
        <svg class="command-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>
        </svg>
        <div class="command-item-content">
          <div class="command-item-title">${this.highlightMatch(cmd.title)}</div>
          <div class="command-item-description">${cmd.description}</div>
        </div>
        <kbd class="command-item-shortcut">${cmd.shortcut}</kbd>
      </div>
    `).join('');
    
    // Click handlers
    this.results.querySelectorAll('.command-item').forEach(item => {
      item.addEventListener('click', () => {
        const index = parseInt(item.dataset.index);
        this.execute(this.filteredCommands[index]);
      });
    });
  }
  
  highlightMatch(text) {
    const query = this.input?.value.toLowerCase().trim();
    if (!query) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark style="background: var(--amber-400); color: var(--charcoal-950); padding: 0 2px; border-radius: 2px;">$1</mark>');
  }
}

// Initialize
const commandPalette = new CommandPalette();