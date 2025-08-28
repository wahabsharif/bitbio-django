// validation.js

/**
 * Validates required fields and returns array of missing field names
 * @returns {Array} Array of missing field objects with id and name properties
 */
function validateRequiredFields() {
    const requiredFields = [
        { id: 'seeding_density', name: 'Seeding Density' },
        { id: 'num_wells', name: 'Number of Wells' },
        { id: 'surface_area', name: 'Surface Area' },
        { id: 'media_volume', name: 'Media Volume' },
        { id: 'count1', name: 'Cell Count 1' },
        { id: 'viability1', name: 'Viability 1' },
        { id: 'buffer', name: 'Buffer Percentage' },
        { id: 'suspension_volume', name: 'Suspension Volume' }
    ];

    const missingFields = [];

    requiredFields.forEach(field => {
        const element = document.getElementById(field.id);
        if (!element || !element.value || element.value.trim() === '') {
            missingFields.push(field);
        }
    });

    return missingFields;
}

/**
 * Validates and clears field validation errors
 * @param {HTMLElement} field - The field to validate and clear
 */
function validateAndClearField(field) {
    if (!field) return;
    
    // Remove error styling
    field.classList.remove('error-field', 'border-red-500');
    field.style.border = '';
    
    // Clear any validation messages
    const errorText = field.parentElement?.querySelector('.error-text');
    if (errorText) {
        errorText.remove();
    }
}

/**
 * Shows a validation error message
 * @param {string} message - The error message to display
 */
function showValidationError(message) {
    const validationErrors = document.getElementById("validationErrors");
    if (!validationErrors) {
        console.error("Validation errors element not found");
        return;
    }

    const errorsList = validationErrors.querySelector("ul");
    if (!errorsList) {
        console.error("Errors list element not found");
        return;
    }

    // Clear existing errors
    errorsList.innerHTML = "";

    // Add the error message
    const errorItem = document.createElement("li");
    errorItem.textContent = message;
    errorsList.appendChild(errorItem);

    // Show the validation errors section
    validationErrors.classList.remove("hidden");

    // Auto-hide after 5 seconds
    setTimeout(() => {
        validationErrors.classList.add("hidden");
    }, 5000);
}
