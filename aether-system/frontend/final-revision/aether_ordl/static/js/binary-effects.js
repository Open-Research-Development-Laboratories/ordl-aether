/**
 * Binary Rain Effect - ORDL 零式 Aesthetic
 * Creates falling binary digits on canvas background
 * 
 * Philosophy: "黒い画面の中の白い影"
 * (A White Shadow in the Black Screen)
 */

(function() {
    'use strict';

    const canvas = document.getElementById('binary-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    
    // Configuration
    const config = {
        fontSize: 14,
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        color: 'rgba(255, 255, 255, 0.15)',
        highlightColor: 'rgba(255, 255, 255, 0.4)',
        fadeRate: 0.02,
        newColumnChance: 0.02,
        chars: '01'
    };

    let columns = [];
    let animationId = null;
    let isActive = true;

    /**
     * Resize canvas to fill window
     */
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initColumns();
    }

    /**
     * Initialize column data
     */
    function initColumns() {
        const colCount = Math.ceil(canvas.width / config.fontSize);
        columns = [];
        
        for (let i = 0; i < colCount; i++) {
            columns.push({
                x: i * config.fontSize,
                y: Math.random() * canvas.height,
                speed: Math.random() * 2 + 1,
                length: Math.floor(Math.random() * 15) + 5,
                chars: [],
                active: Math.random() < 0.3
            });
        }
    }

    /**
     * Get random binary character
     */
    function getRandomChar() {
        return config.chars[Math.floor(Math.random() * config.chars.length)];
    }

    /**
     * Draw a single frame
     */
    function draw() {
        if (!isActive) return;

        // Semi-transparent black for trail effect
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.font = `${config.fontSize}px ${config.fontFamily}`;
        ctx.textAlign = 'center';

        columns.forEach((col, idx) => {
            if (!col.active) {
                // Random chance to activate column
                if (Math.random() < config.newColumnChance) {
                    col.active = true;
                    col.y = -col.length * config.fontSize;
                }
                return;
            }

            // Generate new character at head
            if (col.chars.length < col.length) {
                col.chars.push(getRandomChar());
            }

            // Draw characters
            col.chars.forEach((char, charIdx) => {
                const y = col.y - (col.length - charIdx) * config.fontSize;
                
                if (y < -config.fontSize || y > canvas.height + config.fontSize) return;

                // Highlight the leading character
                if (charIdx === col.chars.length - 1) {
                    ctx.fillStyle = config.highlightColor;
                    ctx.shadowBlur = 4;
                    ctx.shadowColor = config.highlightColor;
                } else {
                    const opacity = (charIdx / col.length) * 0.15;
                    ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
                    ctx.shadowBlur = 0;
                }

                ctx.fillText(char, col.x + config.fontSize / 2, y);
            });

            // Move column
            col.y += col.speed;

            // Reset if off screen
            if (col.y - col.length * config.fontSize > canvas.height) {
                col.active = Math.random() < 0.5;
                col.y = -col.length * config.fontSize;
                col.chars = [];
                col.speed = Math.random() * 2 + 1;
            }
        });

        animationId = requestAnimationFrame(draw);
    }

    /**
     * Pause animation when tab is hidden
     */
    function handleVisibilityChange() {
        if (document.hidden) {
            isActive = false;
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
        } else {
            isActive = true;
            draw();
        }
    }

    /**
     * Initialize
     */
    function init() {
        resize();
        draw();

        window.addEventListener('resize', resize);
        document.addEventListener('visibilitychange', handleVisibilityChange);
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose API for external control
    window.BinaryRain = {
        pause: () => { isActive = false; },
        resume: () => { 
            isActive = true; 
            draw(); 
        },
        setOpacity: (opacity) => {
            canvas.style.opacity = opacity;
        }
    };
})();
