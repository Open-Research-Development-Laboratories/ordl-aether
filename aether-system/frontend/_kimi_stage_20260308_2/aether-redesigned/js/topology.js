/**
 * AETHER - Topology Visualization
 * Force-directed graph for swarm network
 */

class TopologyGraph {
  constructor() {
    this.canvas = document.getElementById('topology-canvas');
    this.ctx = this.canvas?.getContext('2d');
    this.nodePanel = document.getElementById('node-panel');
    this.nodePanelClose = document.getElementById('node-panel-close');
    
    // Graph data
    this.nodes = [];
    this.edges = [];
    this.selectedNode = null;
    this.hoveredNode = null;
    this.draggedNode = null;
    
    // Physics
    this.repulsion = 2000;
    this.springLength = 100;
    this.springStrength = 0.05;
    this.damping = 0.9;
    
    // Animation
    this.animationId = null;
    this.lastTime = 0;
    
    this.init();
  }
  
  init() {
    if (!this.canvas || !this.ctx) return;
    
    this.resize();
    window.addEventListener('resize', () => this.resize());
    
    // Generate sample data
    this.generateSampleData();
    
    // Event listeners
    this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
    this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
    this.canvas.addEventListener('mouseup', () => this.onMouseUp());
    this.canvas.addEventListener('wheel', (e) => this.onWheel(e));
    
    this.nodePanelClose?.addEventListener('click', () => this.closeNodePanel());
    
    // Start animation
    this.animate();
  }
  
  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
    this.centerX = rect.width / 2;
    this.centerY = rect.height / 2;
  }
  
  generateSampleData() {
    // Create nodes (agents)
    const nodeCount = 15;
    for (let i = 0; i < nodeCount; i++) {
      const angle = (i / nodeCount) * Math.PI * 2;
      const radius = 150 + Math.random() * 100;
      this.nodes.push({
        id: `agent-${String(i).padStart(2, '0')}`,
        x: this.centerX + Math.cos(angle) * radius,
        y: this.centerY + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        radius: 8 + Math.random() * 4,
        status: Math.random() > 0.8 ? 'dormant' : (Math.random() > 0.95 ? 'error' : 'active'),
        messages: Math.floor(Math.random() * 2000),
        cpu: Math.floor(Math.random() * 100),
        uptime: Math.floor(Math.random() * 100)
      });
    }
    
    // Create edges (connections)
    for (let i = 0; i < this.nodes.length; i++) {
      const connections = 1 + Math.floor(Math.random() * 3);
      for (let j = 0; j < connections; j++) {
        const target = Math.floor(Math.random() * this.nodes.length);
        if (target !== i && !this.edges.find(e => 
          (e.source === i && e.target === target) || 
          (e.source === target && e.target === i)
        )) {
          this.edges.push({
            source: i,
            target: target,
            strength: 0.5 + Math.random() * 0.5
          });
        }
      }
    }
  }
  
  updatePhysics() {
    // Repulsion between nodes
    for (let i = 0; i < this.nodes.length; i++) {
      for (let j = i + 1; j < this.nodes.length; j++) {
        const dx = this.nodes[j].x - this.nodes[i].x;
        const dy = this.nodes[j].y - this.nodes[i].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        
        const force = this.repulsion / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        
        this.nodes[i].vx -= fx;
        this.nodes[i].vy -= fy;
        this.nodes[j].vx += fx;
        this.nodes[j].vy += fy;
      }
    }
    
    // Spring forces along edges
    for (const edge of this.edges) {
      const n1 = this.nodes[edge.source];
      const n2 = this.nodes[edge.target];
      
      const dx = n2.x - n1.x;
      const dy = n2.y - n1.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      
      const force = (dist - this.springLength) * this.springStrength * edge.strength;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      
      n1.vx += fx;
      n1.vy += fy;
      n2.vx -= fx;
      n2.vy -= fy;
    }
    
    // Center gravity
    for (const node of this.nodes) {
      const dx = this.centerX - node.x;
      const dy = this.centerY - node.y;
      node.vx += dx * 0.001;
      node.vy += dy * 0.001;
    }
    
    // Apply velocity and damping
    for (const node of this.nodes) {
      if (node !== this.draggedNode) {
        node.vx *= this.damping;
        node.vy *= this.damping;
        node.x += node.vx;
        node.y += node.vy;
      }
    }
  }
  
  draw() {
    if (!this.ctx) return;
    
    // Clear canvas
    this.ctx.fillStyle = '#0a0a0a';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Draw grid
    this.drawGrid();
    
    // Draw edges
    for (const edge of this.edges) {
      const n1 = this.nodes[edge.source];
      const n2 = this.nodes[edge.target];
      
      this.ctx.beginPath();
      this.ctx.moveTo(n1.x, n1.y);
      this.ctx.lineTo(n2.x, n2.y);
      this.ctx.strokeStyle = `rgba(245, 242, 233, ${0.1 + edge.strength * 0.3})`;
      this.ctx.lineWidth = 1 + edge.strength * 2;
      this.ctx.stroke();
      
      // Draw message flow animation
      const time = Date.now() / 1000;
      const flowOffset = (time * 50) % 100 / 100;
      const fx = n1.x + (n2.x - n1.x) * flowOffset;
      const fy = n1.y + (n2.y - n1.y) * flowOffset;
      
      this.ctx.beginPath();
      this.ctx.arc(fx, fy, 2, 0, Math.PI * 2);
      this.ctx.fillStyle = 'rgba(245, 242, 233, 0.6)';
      this.ctx.fill();
    }
    
    // Draw nodes
    for (const node of this.nodes) {
      this.drawNode(node);
    }
  }
  
  drawGrid() {
    const gridSize = 40;
    this.ctx.strokeStyle = 'rgba(38, 38, 38, 0.5)';
    this.ctx.lineWidth = 1;
    
    for (let x = 0; x < this.canvas.width; x += gridSize) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, this.canvas.height);
      this.ctx.stroke();
    }
    
    for (let y = 0; y < this.canvas.height; y += gridSize) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.canvas.width, y);
      this.ctx.stroke();
    }
  }
  
  drawNode(node) {
    const isHovered = node === this.hoveredNode;
    const isSelected = node === this.selectedNode;
    
    // Glow effect
    if (isHovered || isSelected) {
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius + 8, 0, Math.PI * 2);
      this.ctx.fillStyle = 'rgba(245, 158, 11, 0.2)';
      this.ctx.fill();
    }
    
    // Node circle
    this.ctx.beginPath();
    this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
    
    // Color based on status
    let color = '#22c55e'; // active
    if (node.status === 'dormant') color = '#525252';
    if (node.status === 'error') color = '#ef4444';
    
    this.ctx.fillStyle = color;
    this.ctx.fill();
    
    // Border
    this.ctx.strokeStyle = isSelected ? '#f5f2e9' : '#0a0a0a';
    this.ctx.lineWidth = isSelected ? 2 : 1;
    this.ctx.stroke();
    
    // Inner highlight
    this.ctx.beginPath();
    this.ctx.arc(node.x - 2, node.y - 2, node.radius * 0.3, 0, Math.PI * 2);
    this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    this.ctx.fill();
    
    // Label
    if (isHovered || isSelected) {
      this.ctx.font = '11px "IBM Plex Mono"';
      this.ctx.fillStyle = '#f5f2e9';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(node.id, node.x, node.y + node.radius + 15);
    }
  }
  
  animate() {
    this.updatePhysics();
    this.draw();
    this.animationId = requestAnimationFrame(() => this.animate());
  }
  
  getMousePos(e) {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  }
  
  getNodeAt(pos) {
    for (const node of this.nodes) {
      const dx = pos.x - node.x;
      const dy = pos.y - node.y;
      if (Math.sqrt(dx * dx + dy * dy) < node.radius + 5) {
        return node;
      }
    }
    return null;
  }
  
  onMouseDown(e) {
    const pos = this.getMousePos(e);
    const node = this.getNodeAt(pos);
    
    if (node) {
      this.draggedNode = node;
      this.selectedNode = node;
      this.showNodePanel(node);
    } else {
      this.selectedNode = null;
      this.closeNodePanel();
    }
  }
  
  onMouseMove(e) {
    const pos = this.getMousePos(e);
    
    if (this.draggedNode) {
      this.draggedNode.x = pos.x;
      this.draggedNode.y = pos.y;
      this.draggedNode.vx = 0;
      this.draggedNode.vy = 0;
    } else {
      this.hoveredNode = this.getNodeAt(pos);
      this.canvas.style.cursor = this.hoveredNode ? 'pointer' : 'grab';
    }
  }
  
  onMouseUp() {
    this.draggedNode = null;
  }
  
  onWheel(e) {
    e.preventDefault();
    // Zoom functionality could be added here
  }
  
  showNodePanel(node) {
    if (!this.nodePanel) return;
    
    document.getElementById('node-name').textContent = node.id;
    this.nodePanel.classList.remove('hidden');
    
    // Update stats
    const statusEl = this.nodePanel.querySelector('.status-active');
    if (statusEl) {
      statusEl.textContent = node.status.toUpperCase();
      statusEl.className = 'node-stat-value status-' + node.status;
    }
  }
  
  closeNodePanel() {
    this.nodePanel?.classList.add('hidden');
  }
  
  reset() {
    this.nodes = [];
    this.edges = [];
    this.generateSampleData();
  }
}

// Initialize
window.topology = new TopologyGraph();