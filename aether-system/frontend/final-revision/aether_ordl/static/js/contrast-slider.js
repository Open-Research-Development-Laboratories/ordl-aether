/**
 * Contrast Slider - ORDL 零式 Aesthetic
 * Controls brightness/contrast of the interface
 * 
 * Label: 明度 / BRIGHT
 */

(function() {
    'use strict';

    const slider = document.getElementById('contrast-slider');
    if (!slider) return;

    const root = document.documentElement;
    
    // Default values
    const defaults = {
        brightness: 100,
        contrast: 100
    };

    /**
     * Update CSS variables based on slider value
     * @param {number} value - 0 to 100
     */
    function updateContrast(value) {
        // Map 0-100 to appropriate CSS values
        // 50 = normal, 0 = dim, 100 = bright
        const brightness = 50 + (value / 2); // 50% to 100%
        const contrast = 50 + value; // 50% to 150%
        
        root.style.setProperty('--ordl-brightness', `${brightness}%`);
        root.style.setProperty('--ordl-contrast', contrast / 100);
        
        // Apply filter to main container
        const container = document.querySelector('.ordl-container');
        if (container) {
            container.style.filter = `brightness(${brightness}%) contrast(${contrast}%)`;
        }

        // Store preference
        localStorage.setItem('ordl-brightness', value);
    }

    /**
     * Initialize from stored preference
     */
    function init() {
        const stored = localStorage.getItem('ordl-brightness');
        const initialValue = stored !== null ? parseInt(stored, 10) : 50;
        
        slider.value = initialValue;
        slider.min = 0;
        slider.max = 100;
        slider.step = 1;
        
        updateContrast(initialValue);

        // Event listeners
        slider.addEventListener('input', (e) => {
            updateContrast(parseInt(e.target.value, 10));
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + Up/Down to adjust brightness
            if ((e.ctrlKey || e.metaKey) && e.shiftKey) {
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    const newValue = Math.min(100, parseInt(slider.value, 10) + 5);
                    slider.value = newValue;
                    updateContrast(newValue);
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const newValue = Math.max(0, parseInt(slider.value, 10) - 5);
                    slider.value = newValue;
                    updateContrast(newValue);
                }
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose API
    window.OrdlContrast = {
        set: (value) => {
            if (slider) {
                slider.value = value;
                updateContrast(value);
            }
        },
        get: () => parseInt(slider?.value || 50, 10),
        reset: () => {
            if (slider) {
                slider.value = 50;
                updateContrast(50);
            }
        }
    };
})();
