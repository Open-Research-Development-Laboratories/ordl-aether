/**
 * AETHER - Timeline View
 * Temporal debugging with scrubber
 */

class Timeline {
  constructor() {
    this.track = document.querySelector('.timeline-track');
    this.handle = document.getElementById('timeline-handle');
    this.progress = document.getElementById('timeline-progress');
    this.playBtn = document.getElementById('timeline-play');
    this.saveBtn = document.getElementById('timeline-save');
    
    this.isPlaying = false;
    this.progressValue = 45;
    this.isDragging = false;
    
    this.init();
  }
  
  init() {
    // Drag handle
    this.handle?.addEventListener('mousedown', (e) => this.startDrag(e));
    document.addEventListener('mousemove', (e) => this.onDrag(e));
    document.addEventListener('mouseup', () => this.endDrag());
    
    // Click track
    this.track?.addEventListener('click', (e) => this.onTrackClick(e));
    
    // Play button
    this.playBtn?.addEventListener('click', () => this.togglePlay());
    
    // Save button
    this.saveBtn?.addEventListener('click', () => this.saveScenario());
    
    // Branch points
    document.querySelectorAll('.timeline-branch').forEach(branch => {
      branch.addEventListener('click', (e) => this.onBranchClick(e));
    });
  }
  
  startDrag(e) {
    this.isDragging = true;
    e.preventDefault();
  }
  
  onDrag(e) {
    if (!this.isDragging || !this.track) return;
    
    const rect = this.track.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
    
    this.setProgress(percent);
  }
  
  endDrag() {
    this.isDragging = false;
  }
  
  onTrackClick(e) {
    if (this.isDragging) return;
    
    const rect = this.track.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percent = (x / rect.width) * 100;
    
    this.setProgress(percent);
  }
  
  setProgress(percent) {
    this.progressValue = percent;
    
    if (this.handle) {
      this.handle.style.left = percent + '%';
    }
    if (this.progress) {
      this.progress.style.width = percent + '%';
    }
    
    // Update causal chain highlighting
    this.updateCausalChain(percent);
  }
  
  updateCausalChain(percent) {
    const events = document.querySelectorAll('.chain-event');
    const activeIndex = Math.floor((percent / 100) * events.length);
    
    events.forEach((event, i) => {
      event.classList.toggle('active', i === activeIndex);
    });
  }
  
  togglePlay() {
    this.isPlaying = !this.isPlaying;
    
    if (this.playBtn) {
      this.playBtn.innerHTML = this.isPlaying ? `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="6" y="4" width="4" height="16"/>
          <rect x="14" y="4" width="4" height="16"/>
        </svg>
      ` : `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
      `;
    }
    
    if (this.isPlaying) {
      this.play();
    }
  }
  
  play() {
    if (!this.isPlaying) return;
    
    this.progressValue += 0.2;
    if (this.progressValue > 100) {
      this.progressValue = 0;
    }
    
    this.setProgress(this.progressValue);
    requestAnimationFrame(() => this.play());
  }
  
  onBranchClick(e) {
    const branchNum = e.target.dataset.branch;
    alert(`Branch point ${branchNum} selected. This would show alternate timeline.`);
  }
  
  saveScenario() {
    const name = prompt('Enter scenario name:', `Scenario_${Date.now()}`);
    if (name) {
      alert(`Scenario "${name}" saved at T-${this.progressValue.toFixed(1)}%`);
    }
  }
}

// Initialize
const timeline = new Timeline();