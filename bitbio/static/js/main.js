/**
 * Main JavaScript file for bit.bio calculator
 * This file initializes all functionality and ensures proper loading order
 */

// Global variables
let cellTypes = [];
let cultureVessels = [];

/**
 * Main initialization function
 */
async function initCalculator() {
    
    try {
        // Setup event listeners first
        setupEventListeners();
        
        // Fetch data in parallel
        await fetchInitialData();
        
        // Initialize other components
        initializeComponents();
        
        
    } catch (error) {
        console.error('Error during calculator initialization:', error);
    }
}

// Use global formatter from UI handlers if available
function applyThousandsFormatting(value) {
    try {
        if (typeof formatNumberWithCommas === 'function') {
            return formatNumberWithCommas(String(value));
        }
    } catch (e) {}
    return String(value);
}

/**
 * Fetch initial data from backend
 */
async function fetchInitialData() {
    try {
        const [typesResponse, vesselsResponse] = await Promise.all([
            fetch("products/"),
            fetch("culture-vessels/", {
                headers: {
                    Accept: "application/json",
                },
            }),
        ]);

        // Process responses
        if (typesResponse.ok) {
            cellTypes = await typesResponse.json();
            populateCellTypes(cellTypes);
        }

        if (vesselsResponse.ok) {
            cultureVessels = await vesselsResponse.json();
            populateCultureVessels(cultureVessels);
        }
    } catch (err) {
        console.error("Failed to fetch data:", err);
        // Use mock data for testing if fetch fails
        useMockData();
    }
    
    // Ensure dropdowns are populated even if fetch fails
    if (cellTypes.length === 0) {
        useMockData();
    }
}

/**
 * Use mock data for testing if backend is not available
 */
function useMockData() {
    
    // Mock cell types
    cellTypes = [
        { id: 1, name: 'iPSC', product_name: 'iPSC' },
        { id: 2, name: 'Neurons', product_name: 'Neurons' },
        { id: 3, name: 'Cardiomyocytes', product_name: 'Cardiomyocytes' }
    ];
    
    // Mock culture vessels
    cultureVessels = [
        { id: 1, name: '96-well plate', plate_format: '96-well plate', surface_area: 0.32, media_volume: 0.1 },
        { id: 2, name: '24-well plate', plate_format: '24-well plate', surface_area: 1.9, media_volume: 0.5 },
        { id: 3, name: '6-well plate', plate_format: '6-well plate', surface_area: 9.6, media_volume: 2.0 }
    ];
    
    // Try to populate dropdowns with retry mechanism
    populateDropdownsWithRetry();
}

/**
 * Populate dropdowns with retry mechanism
 */
function populateDropdownsWithRetry(maxRetries = 5) {
    let retryCount = 0;
    
    const tryPopulate = () => {
        
        const cellTypeDropdown = document.getElementById('cell_type_dropdown');
        const cultureVesselDropdown = document.getElementById('culture_vessel_dropdown');
        
        if (cellTypeDropdown && cultureVesselDropdown) {
            populateCellTypes(cellTypes);
            populateCultureVessels(cultureVessels);
            return true;
        } else {
            retryCount++;
            
            if (retryCount < maxRetries) {
                setTimeout(tryPopulate, 100 * retryCount); // Exponential backoff
                return false;
            } else {
                console.error('Failed to populate dropdowns after maximum retries');
                return false;
            }
        }
    };
    
    tryPopulate();
}

/**
 * Initialize all components
 */
function initializeComponents() {
    // Initialize tooltips if available
    if (typeof initializeTooltips === 'function') {
        initializeTooltips();
    }
    
    // Initialize cell validation if available
    if (typeof initializeCellValidation === 'function') {
        initializeCellValidation();
    }
    
    // Initialize field validation
    if (typeof initializeFieldValidation === 'function') {
        initializeFieldValidation();
    }
    
    // Initialize numeric input validation
    if (typeof initializeNumericInputValidation === 'function') {
        initializeNumericInputValidation();
    }

    // Color tracked defaults until changed
    if (typeof setupDefaultValueColoring === 'function') {
        setupDefaultValueColoring();
    }
}

/**
 * Setup event listeners for the calculator
 */
function setupEventListeners() {
    
    // Apply default styling to all inputs with default values
    const numericInputs = document.querySelectorAll(
        'input[inputmode="decimal"], input[type="number"]'
    );

    numericInputs.forEach((input) => {
        // Ensure all numeric inputs have a step attribute
        if (!input.hasAttribute("step")) {
            input.setAttribute("step", "0.1");
        }

        // Apply default styling if value exists
        if (input.value) {
            input.classList.add("default-input");
        }

        // Handle wheel events for increment/decrement
        input.addEventListener("wheel", handleInputWheelEvent);

        // Handle special formatting for cell count inputs
        if (["count1", "count2", "count3"].includes(input.id)) {
            if (typeof handleCellCountInput === 'function') {
                handleCellCountInput(input);
            }
        }

        // Update styling on user interaction
        input.addEventListener("input", function () {
            this.classList.remove("default-input");
            this.classList.add("active-input");
        });

        input.addEventListener("focus", function () {
            this.classList.remove("default-input");
            this.classList.add("active-input");
            this.select();
        });
    });

    // Setup manual input handling for all relevant fields
    if (typeof handleSeedingDensityManualInput === 'function') {
        handleSeedingDensityManualInput();
    }
    if (typeof handleSurfaceAreaManualInput === 'function') {
        handleSurfaceAreaManualInput();
    }
    if (typeof handleMediaVolumeManualInput === 'function') {
        handleMediaVolumeManualInput();
    }

    // Setup sequential validation for count and viability fields
    if (typeof setupSequentialValidation === 'function') {
        setupSequentialValidation();
    }

    // Add calculate button event handler
    setupCalculateButton();

    // Setup other buttons
    setupActionButtons();

    // Setup validation warning indicators
    if (typeof setupValidationWarnings === 'function') {
        setupValidationWarnings();
    }

    // Prevent tooltip click propagation
    if (typeof preventTooltipPropagation === 'function') {
        preventTooltipPropagation();
    }

    // Hide validation errors on input focus
    if (typeof hideValidationErrorsOnFocus === 'function') {
        hideValidationErrorsOnFocus();
    }
}

/**
 * Setup calculate button and validation
 */
function setupCalculateButton() {
    const calculateBtn = document.getElementById("calculateBtn");
    if (calculateBtn) {
        calculateBtn.addEventListener("click", function () {
            // Validate for negative numbers or percentage over 100
            const allInputs = document.querySelectorAll(
                'input[type="number"], input[type="text"][inputmode="decimal"]'
            );
            let hasNegative = false;
            let hasPercentageOverLimit = false;
            const percentageFields = [
                "viability1",
                "viability2",
                "viability3",
                "buffer",
            ];

            allInputs.forEach((input) => {
                if (input.value.trim() === "") return;

                // For seeding density, remove commas before parsing
                let valueToCheck = input.value;
                if (input.id === "seeding_density") {
                    valueToCheck = removeCommasFromNumber(input.value);
                }

                const value = parseDecimalInput(valueToCheck);
                if (isNaN(value)) return;

                if (value < 0) {
                    hasNegative = true;
                    input.classList.add("border-red-500");
                } else if (percentageFields.includes(input.id) && value > 100) {
                    hasPercentageOverLimit = true;
                    input.classList.add("border-red-500");
                }
            });

            if (hasNegative) {
                showValidationError("Please do not include negative numbers");
                return;
            }

            if (hasPercentageOverLimit) {
                showValidationError(
                    "Your percentage value is higher than 100%, please confirm your values"
                );
                return;
            }

            // If no validation errors, proceed with calculation
            if (typeof performCalculation === 'function') {
                performCalculation();
            }
        });
    }
}

/**
 * Setup action buttons (reset, recalculate, download, etc.)
 */
function setupActionButtons() {
    const resetBtn = document.getElementById("resetBtn");
    const recalculateBtn = document.getElementById("recalculateBtn");
    const downloadExcelBtn = document.getElementById("downloadExcel");
    const downloadPdfBtn = document.getElementById("downloadPdf");

    if (resetBtn) {
        resetBtn.addEventListener("click", function() {
            if (typeof resetCalculator === 'function') {
                resetCalculator();
            }
        });
    }

    if (recalculateBtn) {
        recalculateBtn.addEventListener("click", function() {
            if (typeof performCalculation === 'function') {
                performCalculation();
            }
        });
    }

    if (downloadExcelBtn) {
        downloadExcelBtn.addEventListener("click", function (e) {
            e.preventDefault();
            if (typeof downloadAsExcel === 'function') {
                downloadAsExcel();
            }
        });
    }

    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener("click", function (e) {
            e.preventDefault();
            if (typeof downloadAsPdf === 'function') {
                downloadAsPdf();
            }
        });
    }
}

/**
 * Populate cell types dropdown
 */
function populateCellTypes(types) {
    
    const dropdown = document.getElementById('cell_type_dropdown');
    if (!dropdown) {
        console.error('Cell type dropdown not found');
        return;
    }

    const menu = dropdown.querySelector('.menu');
    if (!menu) {
        console.error('Cell type menu not found');
        return;
    }

    // Clear existing items
    menu.innerHTML = '';

    // Add default option
    const defaultItem = document.createElement('div');
    defaultItem.className = 'item';
    defaultItem.setAttribute('data-value', '');
    defaultItem.textContent = '- - Select your cell type - -';
    menu.appendChild(defaultItem);

    // Add cell types
    types.forEach(type => {
        const item = document.createElement('div');
        item.className = 'item';
        item.setAttribute('data-value', type.id);
        item.textContent = type.name || type.product_name || 'Unknown';
        menu.appendChild(item);
    });

    // Setup dropdown behavior (prefer Semantic UI if available)
    if (window.jQuery && window.jQuery.fn && typeof window.jQuery.fn.dropdown === 'function') {
        window.jQuery('#cell_type_dropdown')
            .dropdown({
                fullTextSearch: true,
                selectOnKeydown: true,
                onChange: function(value) {
                    var hidden = document.getElementById('cell_type');
                    if (hidden) hidden.value = value || '';
                    if (value && typeof updateCellTypeDefaults === 'function') {
                        updateCellTypeDefaults(value);
                    }
                }
            })
            .dropdown('clear')
            .dropdown('refresh');
    } else {
        setupDropdownBehavior(dropdown, 'cell_type');
    }
}

/**
 * Populate culture vessels dropdown
 */
function populateCultureVessels(vessels) {
    
    const dropdown = document.getElementById('culture_vessel_dropdown');
    if (!dropdown) {
        console.error('Culture vessel dropdown not found');
        return;
    }

    const menu = dropdown.querySelector('.menu');
    if (!menu) {
        console.error('Culture vessel menu not found');
        return;
    }

    // Clear existing items
    menu.innerHTML = '';

    // Add default option
    const defaultItem = document.createElement('div');
    defaultItem.className = 'item';
    defaultItem.setAttribute('data-value', '');
    defaultItem.textContent = '- - Select your culture vessel - -';
    menu.appendChild(defaultItem);

    // Add culture vessels
    vessels.forEach(vessel => {
        const item = document.createElement('div');
        item.className = 'item';
        item.setAttribute('data-value', vessel.id);
        item.textContent = vessel.name || vessel.plate_format || 'Unknown';
        menu.appendChild(item);
    });

    // Setup dropdown behavior (prefer Semantic UI if available)
    if (window.jQuery && window.jQuery.fn && typeof window.jQuery.fn.dropdown === 'function') {
        window.jQuery('#culture_vessel_dropdown')
            .dropdown({
                fullTextSearch: true,
                selectOnKeydown: true,
                onChange: function(value) {
                    var hidden = document.getElementById('culture_vessel');
                    if (hidden) hidden.value = value || '';
                    if (value && typeof updateVesselDefaults === 'function') {
                        updateVesselDefaults(value);
                    }
                }
            })
            .dropdown('clear')
            .dropdown('refresh');
    } else {
        setupDropdownBehavior(dropdown, 'culture_vessel');
    }
}

/**
 * Setup dropdown behavior
 */
function setupDropdownBehavior(dropdown, fieldType) {
    
    const text = dropdown.querySelector('.text, .default.text');
    const menu = dropdown.querySelector('.menu');
    const items = menu.querySelectorAll('.item');

    if (!text || !menu) {
        console.error('Dropdown elements not found for:', fieldType);
        return;
    }

    // Toggle dropdown
    dropdown.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Toggle menu visibility
        const isVisible = menu.classList.contains('visible');
        if (isVisible) {
            menu.classList.remove('visible');
        } else {
            // Close any other open dropdowns first
            document.querySelectorAll('.ui.dropdown .menu.visible').forEach(openMenu => {
                if (openMenu !== menu) {
                    openMenu.classList.remove('visible');
                }
            });
            menu.classList.add('visible');
        }
        
    });

    // Handle item selection
    items.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const value = this.getAttribute('data-value');
            const displayText = this.textContent;
            
            // Update the text display
            if (text) {
                text.textContent = displayText;
                text.classList.remove('default');
                text.classList.add('text');
            }
            
            // Update hidden input if it exists
            const hiddenInput = document.getElementById(fieldType);
            if (hiddenInput) {
                hiddenInput.value = value;
            }
            
            // Update related fields based on selection
            if (value) {
                if (fieldType === 'culture_vessel') {
                    updateVesselDefaults(value);
                } else if (fieldType === 'cell_type') {
                    if (typeof updateCellTypeDefaults === 'function') {
                        updateCellTypeDefaults(value);
                    }
                }
            }
            
            // Close the menu
            menu.classList.remove('visible');
        });
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!dropdown.contains(e.target)) {
            menu.classList.remove('visible');
        }
    });

    // Add keyboard navigation
    dropdown.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            const isVisible = menu.classList.contains('visible');
            if (isVisible) {
                menu.classList.remove('visible');
            } else {
                menu.classList.add('visible');
            }
        } else if (e.key === 'Escape') {
            menu.classList.remove('visible');
        }
    });

    // Add hover effect for better UX
    dropdown.addEventListener('mouseenter', function() {
        if (!menu.classList.contains('visible')) {
            dropdown.style.borderColor = '#9ca3af';
        }
    });

    dropdown.addEventListener('mouseleave', function() {
        if (!menu.classList.contains('visible')) {
            dropdown.style.borderColor = '#d1d5db';
        }
    });

}

/**
 * Update vessel defaults when culture vessel is selected
 */
function updateVesselDefaults(vesselId) {
    
    const vessel = cultureVessels.find(v => v.id == vesselId);
    if (vessel) {
        
        // Update surface area
        const surfaceAreaInput = document.getElementById('surface_area');
        const surfaceArea = (vessel.surface_area !== undefined ? vessel.surface_area : vessel.surface_area_cm2);
        if (surfaceAreaInput && surfaceArea !== undefined && surfaceArea !== null) {
            surfaceAreaInput.value = applyThousandsFormatting(surfaceArea);
            surfaceAreaInput.classList.add('active-input');
        }
        
        // Update media volume
        const mediaVolumeInput = document.getElementById('media_volume');
        const mediaVolume = (vessel.media_volume !== undefined ? vessel.media_volume : vessel.media_volume_per_well_ml);
        if (mediaVolumeInput && mediaVolume !== undefined && mediaVolume !== null) {
            mediaVolumeInput.value = applyThousandsFormatting(mediaVolume);
            mediaVolumeInput.classList.add('active-input');
        }
    } else {
        console.warn('Vessel not found:', vesselId);
    }
}

/**
 * Update defaults when a cell type is selected (e.g., seeding density)
 */
function updateCellTypeDefaults(cellTypeId) {

    const cellType = cellTypes.find(c => c.id == cellTypeId);
    if (!cellType) {
        console.warn('Cell type not found:', cellTypeId);
        return;
    }

    const seedingDensityInput = document.getElementById('seeding_density');
    const seedingDensity = (cellType.seeding_density !== undefined && cellType.seeding_density !== null)
        ? cellType.seeding_density
        : '';
    if (seedingDensityInput && seedingDensity !== '') {
        seedingDensityInput.value = applyThousandsFormatting(seedingDensity);
        seedingDensityInput.classList.add('active-input');
    }
}

/**
 * Handle input wheel event for increment/decrement
 */
function handleInputWheelEvent(e) {
    e.preventDefault();
    
    const input = e.target;
    const currentValue = parseFloat(input.value) || 0;
    const step = parseFloat(input.step) || 1;
    
    if (e.deltaY < 0) {
        // Scroll up - increment
        input.value = (currentValue + step).toFixed(4);
    } else {
        // Scroll down - decrement
        input.value = Math.max(0, (currentValue - step)).toFixed(4);
    }
    
    // Trigger input event to update styling
    input.dispatchEvent(new Event('input'));
}

/**
 * Remove commas from number string
 */
function removeCommasFromNumber(str) {
    return str.replace(/,/g, '');
}

/**
 * Parse decimal input
 */
function parseDecimalInput(value) {
    if (!value || value.trim() === "") return NaN;

    // First handle the case where comma is used as decimal separator (e.g., "1,1")
    if (value.includes(",") && !value.includes(".")) {
        // If there's only one comma and it's used as decimal separator
        const commaCount = (value.match(/,/g) || []).length;
        if (commaCount === 1) {
            // Replace the comma with a period for parsing
            return parseFloat(value.replace(",", "."));
        }
    }

    // For values with proper thousand separators (e.g., "1,000.5" or "1,000")
    const normalized = String(value).replace(/,/g, "");
    const result = parseFloat(normalized);
    return isNaN(result) ? NaN : result;
}

// Initialize calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCalculator();
});

// Global error handler
window.addEventListener('error', function(e) {
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);

});
