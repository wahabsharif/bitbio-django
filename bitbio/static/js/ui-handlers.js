/**
 * UI handlers for bit.bio calculator
 */

/**
 * Format numbers with thousands separators while preserving decimal precision from the input string
 */
function formatNumberWithCommas(value) {
	if (value === null || value === undefined) return '';
	var str = String(value);
	if (!str) return '';

	// If user used a comma as the decimal separator (and no dot), preserve that precision
	if (str.indexOf('.') === -1 && str.indexOf(',') !== -1) {
		var partsComma = str.split(',');
		var fractionDigitsComma = partsComma[1] ? partsComma[1].length : 0;
		var numericFromComma = (typeof parseDecimalInput === 'function')
			? parseDecimalInput(str)
			: Number(str.replace(',', '.'));
		if (isNaN(numericFromComma)) return str;
		return numericFromComma.toLocaleString('en-US', {
			minimumFractionDigits: fractionDigitsComma,
			maximumFractionDigits: fractionDigitsComma
		});
	}

	// Default: treat commas as thousand separators and dot as decimal
	var numeric = Number(str.replace(/,/g, ''));
	if (isNaN(numeric)) return str;
	var decimalPart = str.indexOf('.') >= 0 ? str.split('.')[1] : '';
	var fractionDigits = decimalPart.length;
	return numeric.toLocaleString('en-US', {
		minimumFractionDigits: fractionDigits,
		maximumFractionDigits: fractionDigits
	});
}

/**
 * Initialize numeric input formatting: strip commas on focus; add thousands separators on blur
 */
function initializeNumericInputValidation() {
	var inputs = document.querySelectorAll('input[inputmode="decimal"], input[inputmode="numeric"], input[type="number"]');
	inputs.forEach(function(input){
		// Remove thousands separators for easy editing
		if (!input._formatFocusBound) {
			input.addEventListener('focus', function(){
				if (typeof this.value === 'string') {
					this.value = this.value.replace(/,/g, '');
				}
			});
			input._formatFocusBound = true;
		}

		// Apply formatting on blur (skip HTML number inputs which cannot display commas)
		if (!input._formatBlurBound) {
			input.addEventListener('blur', function(){
				if (this.type === 'number') return;
				var raw = this.value;
				if (!raw || String(raw).trim() === '') return;
				var numeric = (typeof parseDecimalInput === 'function') ? parseDecimalInput(raw) : Number(String(raw).replace(',', '.'));
				if (isNaN(numeric)) return;
				this.value = formatNumberWithCommas(raw);
			});
			input._formatBlurBound = true;
		}
	});
}

/**
 * Resets the calculator form to its initial state
 */
function resetCalculator() {
    // Reset all input fields
    const inputs = document.querySelectorAll('input[type="number"], input[type="text"]');
    inputs.forEach(input => {
        input.value = '';
        input.classList.remove('active-input', 'border-red-500', 'error-field');
        input.classList.add('default-input');
    });

    // Restore default values for specific fields that have explicit defaults
    const defaultFieldIds = ['suspension_volume', 'num_wells', 'buffer'];
    defaultFieldIds.forEach(function(id){
        const el = document.getElementById(id);
        if (!el) return;
        const defaultValue = (el.dataset && typeof el.dataset.defaultValue !== 'undefined')
            ? el.dataset.defaultValue
            : (el.getAttribute('value') || '');
        if (defaultValue !== '') {
            el.value = defaultValue;
        }
        // Trigger change to refresh any styling linked to default values
        try { el.dispatchEvent(new Event('change')); } catch (e) {}
    });

    // Reset dropdowns to default state
    const cellTypeDropdown = document.getElementById('cell_type_dropdown');
    const cultureVesselDropdown = document.getElementById('culture_vessel_dropdown');
    
    // If Semantic UI is available, use its API to clear selections
    if (window.jQuery && window.jQuery.fn && typeof window.jQuery.fn.dropdown === 'function') {
        if (cellTypeDropdown) {
            window.jQuery(cellTypeDropdown).dropdown('clear');
        }
        if (cultureVesselDropdown) {
            window.jQuery(cultureVesselDropdown).dropdown('clear');
        }
    } else {
        // Fallback: manually reset labels
        if (cellTypeDropdown) {
            const defaultText = cellTypeDropdown.querySelector('.text, .default.text');
            if (defaultText) {
                defaultText.textContent = '- - Select your cell type - -';
            }
        }
        
        if (cultureVesselDropdown) {
            const defaultText = cultureVesselDropdown.querySelector('.text, .default.text');
            if (defaultText) {
                defaultText.textContent = '- - Select your culture vessel - -';
            }
        }
    }

    // Also clear hidden inputs that hold the values
    const hiddenCellType = document.getElementById('cell_type');
    if (hiddenCellType) hiddenCellType.value = '';
    const hiddenCultureVessel = document.getElementById('culture_vessel');
    if (hiddenCultureVessel) hiddenCultureVessel.value = '';

    // Hide results and show help content
    const helpContent = document.getElementById('helpContent');
    const resultsContent = document.getElementById('resultsContent');
    const calculateBtn = document.getElementById('calculateBtn');
    const actionButtons = document.getElementById('actionButtons');
    const downloadOptions = document.getElementById('downloadOptions');
    const warningsDiv = document.getElementById('warnings');

    if (helpContent) helpContent.style.display = 'block';
    if (resultsContent) resultsContent.style.display = 'none';
    if (calculateBtn) calculateBtn.style.display = 'block';
    if (actionButtons) actionButtons.classList.remove('visible');
    if (downloadOptions) downloadOptions.style.display = 'none';
    if (warningsDiv) warningsDiv.classList.add('hidden');

    // Clear any validation errors
    if (typeof hideValidationError === 'function') {
        hideValidationError();
    }
    if (typeof hideWarnings === 'function') {
        hideWarnings();
    }

    // Clear field errors
    const errorFields = document.querySelectorAll('.error-field');
    errorFields.forEach(field => {
        if (typeof clearFieldError === 'function') {
            clearFieldError(field);
        }
    });

    // Re-apply sequential locks immediately
    try {
        if (typeof setupSequentialValidation === 'function') {
            setupSequentialValidation();
        }
    } catch (e) {}

}

/**
 * Setup validation warnings
 */
function setupValidationWarnings() {
    // This function is called from setupEventListeners
    // It's a placeholder for future validation warning setup
}

/**
 * Hide the global warnings container (used by results section)
 */
function hideWarnings() {
	var container = document.getElementById('warnings');
	if (!container) return;
	container.classList.add('hidden');
	container.style.display = 'none';
	try { container.innerHTML = ''; } catch (e) {}
}

/**
 * Check remaining warnings; if none, hide the container to avoid showing borders
 */
function checkRemainingWarnings() {
	var container = document.getElementById('warnings');
	if (!container) return;
	var hasRow = container.querySelector('.warning-row');
	if (!hasRow) {
		hideWarnings();
	}
}

/**
 * Hide validation errors on input focus
 */
function hideValidationErrorsOnFocus() {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            if (typeof clearFieldError === 'function')  {
                clearFieldError(this);
            }
        });
    });
}

/**
 * Handle cell count input formatting and validation
 */
function handleCellCountInput(input) {
    // Add input event listener for real-time formatting
    input.addEventListener('input', function(e) {
        let value = e.target.value;
        
        // Allow only digits, dot or comma
        value = value.replace(/[^\d\.,]/g, '');

        const hasDot = value.indexOf('.') !== -1;
        const hasComma = value.indexOf(',') !== -1;

        // If both separators present, keep the first typed as decimal separator and remove the other
        if (hasDot && hasComma) {
            const firstDot = value.indexOf('.');
            const firstComma = value.indexOf(',');
            if (firstDot < firstComma) {
                // Dot is decimal; remove all commas
                value = value.replace(/,/g, '');
            } else {
                // Comma is decimal; remove all dots
                value = value.replace(/\./g, '');
            }
        }

        // Ensure at most one decimal separator and limit decimals to 2
        let sep = null;
        if (value.indexOf(',') !== -1) sep = ',';
        else if (value.indexOf('.') !== -1) sep = '.';

        if (sep) {
            const parts = value.split(sep);
            const integerPart = parts[0].replace(/[.,]/g, '');
            let fractionalPart = parts.slice(1).join('').replace(/[.,]/g, '');
            if (fractionalPart.length > 2) fractionalPart = fractionalPart.substring(0, 2);
            value = integerPart + sep + fractionalPart;
        }
        
        // Update input value
        e.target.value = value;
        
        // Trigger validation
        if (typeof validateCellCountField === 'function') {
            validateCellCountField(input);
        }
    });
    
    // Add blur event listener for final formatting
    input.addEventListener('blur', function(e) {
        var raw = e.target.value;
        var num = (typeof parseDecimalInput === 'function') ? parseDecimalInput(raw) : Number(String(raw).replace(',', '.'));
        if (!isNaN(num)) {
            e.target.value = formatNumberWithCommas(raw);
        }
    });
}

/**
 * Validate cell count field
 */
function validateCellCountField(input) {
    const valueNum = (typeof parseDecimalInput === 'function') ? parseDecimalInput(input.value) : Number(String(input.value || '').replace(',', '.'));
    
    if (isNaN(valueNum)) {
        if (typeof clearFieldError === 'function') {
            clearFieldError(input);
        }
        return;
    }
    
    if (valueNum < 0) {
        if (typeof showFieldError === 'function') {
            showFieldError(input.id, 'Cell count cannot be negative');
        }
        return;
    }
    
    if (valueNum > 1e12) {
        if (typeof showFieldError === 'function') {
            showFieldError(input.id, 'Cell count seems unusually high. Please verify.');
        }
        return;
    }
    
    // Clear any existing errors
    if (typeof clearFieldError === 'function') {
        clearFieldError(input);
    }
}

/**
 * Validate and clear field
 */
function validateAndClearField(input) {
    if (!input) return false;

    let rawValue = input.value;
    if (typeof parseDecimalInput === 'function') {
        const numValue = parseDecimalInput(rawValue);

        // Field is valid if it's not empty, not NaN, and not zero
        const isValid = rawValue.trim() !== "" && !isNaN(numValue) && numValue !== 0;

        if (isValid) {
            if (typeof clearFieldError === 'function') {
                clearFieldError(input);
            }
        }

        return isValid;
    }
    return false;
}

/**
 * Prevent tooltip click propagation
 */
function preventTooltipPropagation() {
    // This function prevents tooltip clicks from interfering with other functionality
    // Implementation can be added here if needed
}

/**
 * Track default values for key fields and switch text color to black when changed
 */
function setupDefaultValueColoring() {
    const trackedIds = ['suspension_volume', 'num_wells', 'buffer'];

    trackedIds.forEach(function(id){
        const element = document.getElementById(id);
        if (!element) return;

        // Persist the default value from initial DOM state
        if (typeof element.dataset.defaultValue === 'undefined') {
            element.dataset.defaultValue = String(element.value || '');
        }

        const applyColorFromValue = function() {
            const defaultValue = element.dataset.defaultValue || '';
            const currentValue = String(element.value || '');
            if (currentValue === defaultValue) {
                element.style.color = '#9da3c1';
            } else {
                element.style.color = '#000000';
            }
        };

        // Initialize
        applyColorFromValue();

        // React to user edits
        element.addEventListener('input', applyColorFromValue);
        element.addEventListener('change', applyColorFromValue);
    });
}

/**
 * Enforce sequential entry for count and viability fields
 * - Disables Count 2 until Count 1 has a value
 * - Disables Count 3 until Count 2 has a value
 * - Same for Viability 2/3 with respect to the previous field
 */
function setupSequentialValidation() {
    // Helper to enable/disable input and tidy state
    function setInputEnabled(input, enabled, message) {
        if (!input) return;
        if (enabled) {
            input.removeAttribute('disabled');
            input.removeAttribute('readonly');
            input.classList.remove('disabled-input');
            if (input._originalTabIndex !== undefined) {
                input.tabIndex = input._originalTabIndex;
            }
            input.title = '';
        } else {
            // Store tabindex once to restore later
            if (input._originalTabIndex === undefined) {
                input._originalTabIndex = input.tabIndex || 0;
            }
            input.value = '';
            input.setAttribute('disabled', 'disabled');
            input.setAttribute('readonly', 'readonly');
            input.tabIndex = -1;
            input.classList.add('disabled-input');
            input.title = message || 'Please complete the previous field first.';
            if (typeof clearFieldError === 'function') {
                clearFieldError(input);
            }
        }
    }

    // Apply sequential rule within a group of inputs by id
    function applySequentialRule(ids, message) {
        const inputs = ids.map(id => document.getElementById(id)).filter(Boolean);
        if (!inputs.length) return;

        function updateLocks() {
            inputs.forEach((input, index) => {
                if (index === 0) {
                    setInputEnabled(input, true);
                } else {
                    const prev = inputs[index - 1];
                    const prevHasValue = !!(prev && String(prev.value).trim() !== '');
                    setInputEnabled(input, prevHasValue, message);
                }
            });
        }

        // Update locks on any input/change in the group
        inputs.forEach(input => {
            input.addEventListener('input', updateLocks);
            input.addEventListener('change', updateLocks);
        });

        // Initial state
        updateLocks();
    }

    // Enforce for Counts and Viabilities
    applySequentialRule(['count1', 'count2', 'count3'], 'Fill the previous count before continuing.');
    applySequentialRule(['viability1', 'viability2', 'viability3'], 'Fill the previous viability before continuing.');
}