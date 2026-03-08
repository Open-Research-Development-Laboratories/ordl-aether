/**
 * AETHER - Mentality Panel
 * Physical switches, dials, and compliance meters
 */

class MentalityPanel {
  constructor() {
    this.switches = document.querySelectorAll('.switch-input');
    this.dials = document.querySelectorAll('.dial-input');
    this.meters = document.querySelectorAll('.meter-fill');
    
    this.init();
  }
  
  init() {
    // Switches
    this.switches.forEach(sw => {
      sw.addEventListener('change', (e) => this.onSwitchChange(e));
    });
    
    // Dials
    this.dials.forEach(dial => {
      dial.addEventListener('input', (e) => this.onDialChange(e));
    });
    
    // Simulate compliance updates
    this.startComplianceSimulation();
  }
  
  onSwitchChange(e) {
    const switchItem = e.target.closest('.switch-item');
    const label = switchItem?.querySelector('.switch-label')?.textContent;
    const isChecked = e.target.checked;
    
    console.log(`Switch "${label}" ${isChecked ? 'enabled' : 'disabled'}`);
    
    // Update compliance meters
    this.updateCompliance();
    
    // Visual feedback
    this.showToast(`${label} ${isChecked ? 'enabled' : 'disabled'}`);
  }
  
  onDialChange(e) {
    const dialItem = e.target.closest('.dial-item');
    const valueEl = dialItem?.querySelector('.dial-value');
    
    if (valueEl) {
      valueEl.textContent = e.target.value;
    }
    
    // Update compliance meters
    this.updateCompliance();
  }
  
  updateCompliance() {
    // Calculate compliance based on switches
    const switches = Array.from(this.switches);
    const enabledCount = switches.filter(s => s.checked).length;
    const totalCount = switches.length;
    
    // Update meters
    const meters = document.querySelectorAll('.meter');
    meters.forEach((meter, i) => {
      const fill = meter.querySelector('.meter-fill');
      const value = meter.querySelector('.meter-value');
      
      if (fill && value) {
        let percent = 0;
        let count = 0;
        
        switch(i) {
          case 0: // Auto-recovery
            percent = switches[0]?.checked ? 100 : 0;
            count = switches[0]?.checked ? 12 : 0;
            break;
          case 1: // Consensus
            percent = switches[1]?.checked ? 92 : 0;
            count = switches[1]?.checked ? 11 : 0;
            break;
          case 2: // Logging
            percent = switches[2]?.checked ? 100 : 0;
            count = switches[2]?.checked ? 12 : 0;
            break;
        }
        
        fill.style.width = percent + '%';
        value.textContent = `${count}/12`;
        
        // Update color based on compliance
        fill.classList.remove('warning', 'error');
        if (percent < 50) {
          fill.classList.add('error');
        } else if (percent < 80) {
          fill.classList.add('warning');
        }
      }
    });
  }
  
  startComplianceSimulation() {
    // Simulate random fluctuations in compliance
    setInterval(() => {
      const meters = document.querySelectorAll('.meter');
      meters.forEach(meter => {
        const fill = meter.querySelector('.meter-fill');
        if (fill && Math.random() > 0.7) {
          const currentWidth = parseFloat(fill.style.width) || 0;
          const variation = (Math.random() - 0.5) * 5;
          const newWidth = Math.max(0, Math.min(100, currentWidth + variation));
          fill.style.width = newWidth + '%';
        }
      });
    }, 2000);
  }
  
  showToast(message) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      padding: 12px 20px;
      background: var(--charcoal-800);
      border: 1px solid var(--charcoal-600);
      border-radius: 4px;
      color: var(--cream-100);
      font-size: 14px;
      z-index: 1000;
      animation: slideIn 0.2s ease;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.2s ease';
      setTimeout(() => toast.remove(), 200);
    }, 2000);
  }
}

// Initialize
const mentalityPanel = new MentalityPanel();

// Add toast animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(style);