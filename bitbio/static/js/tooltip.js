/**
 * Tooltip functionality for bit.bio calculator
 * Handles showing/hiding tooltips on click with close buttons
 */

document.addEventListener("DOMContentLoaded", function () {
    // Get all tooltip triggers
    const tooltipTriggers = document.querySelectorAll(".tooltip-container");

    // Track currently open tooltip
    let openTooltip = null;

    // Function to handle tooltip toggle
    function toggleTooltip(trigger) {
        const tooltip = trigger.querySelector(".custom-tooltip");
        if (!tooltip) {
            return;
        }

        // If there's an open tooltip and it's not the current one, close it
        if (openTooltip && openTooltip !== tooltip) {
            openTooltip.classList.remove("active");
        }

        // Toggle the current tooltip
        if (tooltip.classList.contains("active")) {
            tooltip.classList.remove("active");
            openTooltip = null;
        } else {
            tooltip.classList.add("active");
            openTooltip = tooltip;
        }
    }

    // Prevent form labels from interfering with tooltips
    tooltipTriggers.forEach((trigger) => {
        const label = trigger.closest('.form-label');
        if (label) {
            // Prevent the label from focusing inputs when tooltip is clicked
            label.addEventListener('click', function(e) {
                if (e.target.closest('.tooltip-container')) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    
                    // Now manually trigger the tooltip
                    const tooltipContainer = e.target.closest('.tooltip-container');
                    if (tooltipContainer) {
                        toggleTooltip(tooltipContainer);
                    }
                    
                    return false;
                }
            }, true); // Use capture phase
        }
    });

    // Add click event to each tooltip trigger
    tooltipTriggers.forEach((trigger, index) => {
        // Make the entire tooltip container clickable
        trigger.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            toggleTooltip(this);
            return false;
        });
        
        // Also add click to the SVG icon specifically
        const svgIcon = trigger.querySelector('svg');
        if (svgIcon) {
            svgIcon.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                
                toggleTooltip(trigger);
                return false;
            });
        }
    });

    // Close tooltip when clicking close button
    document.querySelectorAll(".tooltip-close").forEach((closeBtn) => {
        closeBtn.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            const tooltip = this.closest(".custom-tooltip");
            if (tooltip) {
                tooltip.classList.remove("active");
                if (openTooltip === tooltip) {
                    openTooltip = null;
                }
            }
        });
    });

    // Close tooltip when clicking outside
    document.addEventListener("click", function (event) {
        if (openTooltip && !openTooltip.contains(event.target) && !event.target.closest('.tooltip-container')) {
            openTooltip.classList.remove("active");
            openTooltip = null;
        }
    });

    // Close tooltip when pressing ESC key
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && openTooltip) {
            openTooltip.classList.remove("active");
            openTooltip = null;
        }
    });
    
    // Test tooltip functionality
    setTimeout(() => {
        const testTrigger = tooltipTriggers[0];
        if (testTrigger) {
            // This will help verify the tooltip is working
        }
    }, 1000);
});
