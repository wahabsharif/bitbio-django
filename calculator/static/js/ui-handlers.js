// ui-handlers.js

/**
 * Format number with comma separators if not already formatted
 * @param {string|number} value - The number to format
 * @returns {string} - Formatted number string
 */
function formatNumberWithCommas(value) {
    // Convert to string and trim
    const cleanValue = String(value).trim();

    // If empty, return as is
    if (cleanValue === "") {
        return cleanValue;
    }

    // If the value already contains commas, preserve the exact format
    if (cleanValue.includes(",")) {
        return cleanValue; // Preserve existing format
    }

    // Otherwise, format with commas
    // Parse as number (this will handle any conversion needed)
    const numValue = parseFloat(cleanValue.replace(/,/g, ""));

    // If not a valid number, return original input
    if (isNaN(numValue)) {
        return cleanValue;
    }

    // Format the number with commas as thousand separators
    const parts = numValue.toString().split(".");
    const integerPart = parts[0];
    const decimalPart = parts[1];

    // Add commas to integer part
    const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    // Return with decimal part if present
    return decimalPart
        ? `${formattedInteger}.${decimalPart}`
        : formattedInteger;
}

/**
 * Remove commas from formatted number for calculation purposes
 * @param {string} value - The formatted number string
 * @returns {string} - Clean number string without commas
 */
function removeCommasFromNumber(value) {
    return String(value).replace(/,/g, "");
}

/**
 * FIXED: Helper function to parse numeric inputs that may contain commas
 * @param {string} value - The input value to parse
 * @returns {number} The parsed decimal value
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

/**
 * Generic handler for manual input fields with common behaviors
 * @param {HTMLElement} inputElement - The input element
 * @param {jQuery} dropdownElement - The related dropdown (jQuery object)
 * @param {string} dropdownValue - Value to set in dropdown when manually changed
 */
function handleManualInput(inputElement, dropdownElement, dropdownValue) {
    if (!inputElement || !dropdownElement) return;

    let typingTimeout;

    // Input event handler
    inputElement.addEventListener("input", function (e) {
        if (this._programmaticSet) return;

        clearTimeout(typingTimeout);

        this.classList.remove("default-input");
        this.classList.add("active-input");

        // Set dropdown value after slight delay
        typingTimeout = setTimeout(() => {
            if (this.value.trim() !== "" && dropdownValue) {
                dropdownElement.dropdown("set selected", dropdownValue);
            }
        }, 500);
    });

    // Paste event handler
    inputElement.addEventListener("paste", function (e) {
        if (this._programmaticSet) return;

        setTimeout(() => {
            if (!this.value.includes(",")) {
                this.value = formatNumberWithCommas(this.value);
            }

            this.classList.remove("default-input");
            this.classList.add("active-input");

            if (this.value.trim() !== "" && dropdownValue) {
                dropdownElement.dropdown("set selected", dropdownValue);
            }
        }, 0);
    });

    // Focus event handler
    inputElement.addEventListener("focus", function () {
        if (!this._programmaticSet) {
            this.classList.remove("default-input");
            this.classList.add("active-input");
        }
    });

    // Keydown event handler for clearing behavior
    inputElement.addEventListener("keydown", function (e) {
        if (this._programmaticSet) return;

        if (
            ((e.key >= "0" && e.key <= "9") ||
                e.key === "." ||
                e.key === ",") &&
            (this.classList.contains("default-input") ||
                (this.selectionStart === 0 &&
                    this.selectionEnd === this.value.length))
        ) {
            this.value = "";
        }
    });

    // Blur event handler
    inputElement.addEventListener("blur", function () {
        if (!this._programmaticSet && this.value.trim() !== "") {
            if (!this.value.includes(",")) {
                this.value = formatNumberWithCommas(this.value);
            }
        }
    });
}

/**
 * Handles manual input in seeding density field with number formatting
 */
function handleSeedingDensityManualInput() {
    const seedingInput = document.getElementById("seeding_density");
    const cellTypeDropdown = $("#cell_type_dropdown");
    handleManualInput(seedingInput, cellTypeDropdown, "other");
}

/**
 * Handles manual input in surface area field
 */
function handleSurfaceAreaManualInput() {
    const surfaceAreaInput = document.getElementById("surface_area");
    const cultureVesselDropdown = $("#culture_vessel_dropdown");
    handleManualInput(surfaceAreaInput, cultureVesselDropdown, "other");
}

/**
 * Handles manual input in media volume field
 */
function handleMediaVolumeManualInput() {
    const mediaVolumeInput = document.getElementById("media_volume");
    const cultureVesselDropdown = $("#culture_vessel_dropdown");
    handleManualInput(mediaVolumeInput, cultureVesselDropdown, "other");
}

/**
 * FIXED: Handle input validation with proper comma support
 */
function addNumericInputValidation(input) {
    if (!input) return;

    // Handle input event to validate content
    input.addEventListener("input", function (e) {
        // Skip if this was a programmatic change
        if (this._programmaticSet) return;

        const value = this.value;
        const isViabilityField = [
            "viability1",
            "viability2",
            "viability3",
        ].includes(this.id);

        // For all numeric inputs, allow comma formatting
        // Only remove invalid characters, keep commas and periods
        const cleanedValue = value.replace(/[^0-9.,]/g, "");

        if (value !== cleanedValue) {
            this.value = cleanedValue;
        }

        // Check for negative values and enforce min/max constraints
        const numValue = parseDecimalInput(cleanedValue);
        if (!isNaN(numValue)) {
            // Check min constraint
            const minAttr = this.getAttribute("min");
            if (minAttr !== null && numValue < parseFloat(minAttr)) {
                this.value = minAttr;
            }

            // Check max constraint
            const maxAttr = this.getAttribute("max");
            if (maxAttr !== null && numValue > parseFloat(maxAttr)) {
                this.value = maxAttr;
            }

            // Immediately cap viability fields at 100 during typing
            if (isViabilityField && numValue > 100) {
                this.value = "100";
            }
        }
    });

    // FIXED: Handle blur event to preserve user's exact input format
    input.addEventListener("blur", function () {
        if (this._programmaticSet) return;

        // Don't reformat the input on blur - preserve exactly as entered
        // The only exception is if min/max constraints are violated
        const value = this.value;
        if (value && value.trim() !== "") {
            const numValue = parseDecimalInput(value);
            if (!isNaN(numValue)) {
                // Apply min/max constraints if needed
                const minAttr = this.getAttribute("min");
                const maxAttr = this.getAttribute("max");

                if (minAttr !== null && numValue < parseFloat(minAttr)) {
                    this.value = minAttr;
                } else if (maxAttr !== null && numValue > parseFloat(maxAttr)) {
                    this.value = maxAttr;
                }
                // Otherwise, preserve exactly as entered
            }
        }
    });

    // Add other event handlers (keydown, etc.) as in your original code...
}

/**
 * Populates cell types in the dropdown
 * @param {Array} types - Array of cell type objects
 */
function populateCellTypes(types) {
    // Sort types array by product_name, case-insensitive
    types.sort((a, b) => {
        const nameA = a.product_name || "";
        const nameB = b.product_name || "";
        return nameA.localeCompare(nameB, undefined, { sensitivity: "base" });
    });

    // Get Semantic UI dropdown
    const dropdown = $("#cell_type_dropdown");
    dropdown.dropdown("clear");

    // Add options to the menu
    const menu = dropdown.find(".menu");
    menu.empty();

    // Check if "Other" exists in API data
    const hasOtherInAPI = types.some(
        (type) =>
            type.product_name && type.product_name.toLowerCase() === "other"
    );

    // Add hardcoded "Other" option only if not available from API
    if (!hasOtherInAPI) {
        const otherOpt = document.createElement("div");
        otherOpt.className = "item";
        otherOpt.setAttribute("data-value", "other");
        otherOpt.setAttribute("data-seeding-density", "");
        otherOpt.textContent = "Other";
        menu.append(otherOpt);
    }

    types.forEach((type) => {
        const opt = document.createElement("div");
        opt.className = "item";
        opt.setAttribute("data-value", type.id);
        opt.setAttribute("data-seeding-density", type.seeding_density || "");
        opt.textContent = `${type.product_name} (${type.sku})`;
        menu.append(opt);
    });

    // Initialize dropdown with enhanced onChange handler
    dropdown.dropdown({
        fullTextSearch: true,
        match: "both",
        onChange: function (value, text, $selectedItem) {
            const seedingInput = document.getElementById("seeding_density");

            // Clear dropdown error immediately when selection is made
            const dd = document.querySelector("#cell_type_dropdown");
            if (dd && value && value.trim() !== "") {
                dd.classList.remove("error");
            }

            if (
                value &&
                value !== "other" &&
                $selectedItem &&
                $selectedItem.attr("data-seeding-density")
            ) {
                // Set flag to prevent manual input logic from triggering
                seedingInput._programmaticSet = true;
                const seedingValue = $selectedItem.attr("data-seeding-density");
                // Format the seeding density value with commas
                seedingInput.value = formatNumberWithCommas(seedingValue);
                seedingInput.classList.add("default-input");
                seedingInput.classList.remove("active-input");

                // IMPORTANT: Clear validation errors for seeding density
                validateAndClearField(seedingInput);

                // Reset flag after a short delay
                setTimeout(() => {
                    seedingInput._programmaticSet = false;
                }, 50);
            } else if (value === "other") {
                // Don't auto-fill seeding density for "Other"
                seedingInput.classList.remove("default-input");
                seedingInput.classList.add("active-input");
            } else {
                seedingInput._programmaticSet = true;
                seedingInput.value = "";
                setTimeout(() => {
                    seedingInput._programmaticSet = false;
                }, 50);
            }
        },
    });
}

/**
 * Populates culture vessels in the dropdown
 * @param {Array} vessels - Array of culture vessel objects
 */
function populateCultureVessels(vessels) {
    // Sort vessels array by plate_format, case-insensitive
    vessels.sort((a, b) => {
        const pfA = a.plate_format || "";
        const pfB = b.plate_format || "";
        return pfA.localeCompare(pfB, undefined, { sensitivity: "base" });
    });

    // Get Semantic UI dropdown
    const dropdown = $("#culture_vessel_dropdown");
    dropdown.dropdown("clear");

    // Add options to the menu
    const menu = dropdown.find(".menu");
    menu.empty();

    // Check if "Other" exists in API data
    const hasOtherInAPI = vessels.some(
        (vessel) =>
            vessel.plate_format && vessel.plate_format.toLowerCase() === "other"
    );

    // Add hardcoded "Other" option only if not available from API
    if (!hasOtherInAPI) {
        const otherOpt = document.createElement("div");
        otherOpt.className = "item";
        otherOpt.setAttribute("data-value", "other");
        otherOpt.setAttribute("data-surface-area", "");
        otherOpt.setAttribute("data-media-volume", "");
        otherOpt.textContent = "Other";
        menu.append(otherOpt);
    }

    // Track if we've added any option with "other" as the value attribute
    let hasOtherValue = false;

    vessels.forEach((v) => {
        const opt = document.createElement("div");
        opt.className = "item";

        // Special handling for "Other" option from API
        if (v.plate_format && v.plate_format.toLowerCase() === "other") {
            opt.setAttribute("data-value", "other");
            hasOtherValue = true;
        } else {
            opt.setAttribute("data-value", v.id);
        }

        opt.setAttribute("data-surface-area", v.surface_area_cm2);
        opt.setAttribute("data-media-volume", v.media_volume_per_well_ml);
        opt.textContent = v.plate_format;
        menu.append(opt);
    });

    // Handle duplicate "Other" options
    if (!hasOtherValue && !hasOtherInAPI) {
        const otherOpt = document.createElement("div");
        otherOpt.className = "item";
        otherOpt.setAttribute("data-value", "other");
        otherOpt.setAttribute("data-surface-area", "");
        otherOpt.setAttribute("data-media-volume", "");
        otherOpt.textContent = "Other";
        menu.append(otherOpt);
    }

    // Remove any duplicate "Other" options
    const otherOptions = menu.find('.item[data-value="other"]');
    if (otherOptions.length > 1) {
        otherOptions.slice(1).remove();
    }

    const surfaceAreaInput = document.getElementById("surface_area");
    const mediaVolumeInput = document.getElementById("media_volume");

    // Initialize dropdown with enhanced onChange handler
    dropdown.dropdown({
        fullTextSearch: true,
        match: "both",
        onChange: function (value, text, $selectedItem) {
            // Clear dropdown error immediately when selection is made
            const dd = document.querySelector("#culture_vessel_dropdown");
            if (dd && value && value.trim() !== "") {
                dd.classList.remove("error");
            }

            if (value && value !== "other" && $selectedItem) {
                const surfaceArea = $selectedItem.attr("data-surface-area");
                const mediaVolume = $selectedItem.attr("data-media-volume");

                if (surfaceArea && surfaceArea !== "null") {
                    surfaceAreaInput._programmaticSet = true;
                    surfaceAreaInput.value = surfaceArea;
                    surfaceAreaInput.classList.add("default-input");
                    surfaceAreaInput.classList.remove("active-input");

                    // IMPORTANT: Clear validation errors for surface area
                    validateAndClearField(surfaceAreaInput);

                    setTimeout(() => {
                        surfaceAreaInput._programmaticSet = false;
                    }, 50);
                } else {
                    surfaceAreaInput._programmaticSet = true;
                    surfaceAreaInput.value = "";
                    setTimeout(() => {
                        surfaceAreaInput._programmaticSet = false;
                    }, 50);
                }

                if (mediaVolume && mediaVolume !== "null") {
                    mediaVolumeInput._programmaticSet = true;
                    mediaVolumeInput.value = mediaVolume;
                    mediaVolumeInput.classList.add("default-input");
                    mediaVolumeInput.classList.remove("active-input");

                    // IMPORTANT: Clear validation errors for media volume
                    validateAndClearField(mediaVolumeInput);

                    setTimeout(() => {
                        mediaVolumeInput._programmaticSet = false;
                    }, 50);
                } else {
                    mediaVolumeInput._programmaticSet = true;
                    mediaVolumeInput.value = "";
                    setTimeout(() => {
                        mediaVolumeInput._programmaticSet = false;
                    }, 50);
                }
            } else if (value === "other") {
                // Don't auto-fill surface area and media volume for "Other"
                surfaceAreaInput.classList.remove("default-input");
                surfaceAreaInput.classList.add("active-input");
                mediaVolumeInput.classList.remove("default-input");
                mediaVolumeInput.classList.add("active-input");
            } else {
                surfaceAreaInput._programmaticSet = true;
                surfaceAreaInput.value = "";
                mediaVolumeInput._programmaticSet = true;
                mediaVolumeInput.value = "";
                setTimeout(() => {
                    surfaceAreaInput._programmaticSet = false;
                    mediaVolumeInput._programmaticSet = false;
                }, 50);
            }
        },
    });
}

/**
 * Resets the calculator form to its initial state
 */
function resetCalculator() {
    // Define default values for inputs that should have them
    const defaultValues = {
        suspension_volume: "1",
        buffer: "10",
        num_wells: "0",
        // Add any other inputs that should have default values here
    };

    // Reset all form inputs (including all input types)
    document.querySelectorAll("input").forEach((input) => {
        // Set default values for inputs that have defined defaults
        if (defaultValues.hasOwnProperty(input.id)) {
            input.value = defaultValues[input.id];
        } else {
            // Clear all other inputs
            input.value = "";
        }

        // Reset styling classes
        input.classList.remove("active-input", "border-red-500");
        if (input.value) {
            input.classList.add("default-input");
        } else {
            input.classList.remove("default-input");
        }
    });

    // Reset text inputs with inputmode="decimal" (like count1, count2, count3)
    document.querySelectorAll('input[inputmode="decimal"]').forEach((input) => {
        // Only clear if it doesn't have a default value
        if (!defaultValues.hasOwnProperty(input.id)) {
            input.value = "";
        }
        input.classList.remove("active-input", "border-red-500");
        if (input.value) {
            input.classList.add("default-input");
        } else {
            input.classList.remove("default-input");
        }
    });

    // Reset select elements and Semantic UI dropdowns
    const cellTypeElement = document.getElementById("cell_type");
    const cultureVesselElement = document.getElementById("culture_vessel");

    if (cellTypeElement) cellTypeElement.value = "";
    if (cultureVesselElement) cultureVesselElement.value = "";

    // Reset Semantic UI dropdowns
    $("#cell_type_dropdown").dropdown("clear");
    $("#culture_vessel_dropdown").dropdown("clear");

    // Hide results and show help content
    const resultsContent = document.getElementById("resultsContent");
    const helpContent = document.getElementById("helpContent");
    const validationErrors = document.getElementById("validationErrors");
    const warnings = document.getElementById("warnings");

    if (resultsContent) resultsContent.classList.add("hidden");
    if (helpContent) helpContent.classList.remove("hidden");
    if (validationErrors) validationErrors.classList.add("hidden");
    if (warnings) warnings.classList.add("hidden");

    // Hide download options and copy/paste info
    const downloadOptions = document.getElementById("downloadOptions");
    if (downloadOptions) downloadOptions.classList.add("hidden");

    const copyPasteInfo = document.getElementById("copyPasteInfo");
    if (copyPasteInfo) copyPasteInfo.classList.add("hidden");

    // Show calculate button, hide action buttons
    const calculateBtn = document.getElementById("calculateBtn");
    const actionButtons = document.getElementById("actionButtons");

    if (calculateBtn) calculateBtn.classList.remove("hidden");
    if (actionButtons) actionButtons.classList.add("hidden");

    // Reset any warning messages
    const cellCountWarning = document.getElementById("cellCountWarning");
    const viabilityWarning = document.getElementById("viabilityWarning");

    if (cellCountWarning) cellCountWarning.classList.add("hidden");
    if (viabilityWarning) viabilityWarning.classList.add("hidden");

    // Reset sequential validation states
    updateCellCountFieldStates();
    updateViabilityFieldStates();
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
            handleCellCountInput(input);
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
    handleSeedingDensityManualInput();
    handleSurfaceAreaManualInput();
    handleMediaVolumeManualInput();

    // Setup sequential validation for count and viability fields
    setupSequentialValidation();

    // Add calculate button event handler
    setupCalculateButton();

    // Setup other buttons
    setupActionButtons();

    // Setup validation warning indicators
    setupValidationWarnings();

    // Prevent tooltip click propagation
    preventTooltipPropagation();

    // Hide validation errors on input focus
    hideValidationErrorsOnFocus();
}

/**
 * Handle wheel events for numeric inputs
 * @param {Event} e - The wheel event
 */
function handleInputWheelEvent(e) {
    if (document.activeElement !== this) return;

    e.preventDefault();

    // Check if user is using comma as decimal separator
    const useCommaAsDecimal =
        this.value.includes(",") &&
        !this.value.includes(".") &&
        (this.value.match(/,/g) || []).length === 1;

    const step = parseFloat(this.getAttribute("step") || "0.1");
    const currentValue = parseDecimalInput(this.value) || 0;

    let newValue;
    if (e.deltaY < 0) {
        // Scroll up - increment
        newValue = currentValue + step;
    } else {
        // Scroll down - decrement
        newValue = Math.max(0, currentValue - step);
    }

    // Apply min/max constraints
    const minAttr = this.getAttribute("min");
    const maxAttr = this.getAttribute("max");

    if (minAttr !== null && newValue < parseFloat(minAttr)) {
        newValue = parseFloat(minAttr);
    }

    if (maxAttr !== null && newValue > parseFloat(maxAttr)) {
        newValue = parseFloat(maxAttr);
    }

    // Ensure viability fields never exceed 100
    const isViabilityField = [
        "viability1",
        "viability2",
        "viability3",
    ].includes(this.id);
    if (isViabilityField && newValue > 100) {
        newValue = 100;
    }

    // Format the value appropriately
    const isCountField = ["count1", "count2", "count3"].includes(this.id);

    if (isCountField) {
        // For count fields, check if it's a whole number
        if (Number.isInteger(newValue)) {
            this.value = newValue.toString();
        } else {
            // Preserve comma as decimal separator if that's what user entered
            if (useCommaAsDecimal) {
                this.value = newValue.toFixed(1).replace(".", ",");
            } else {
                this.value = newValue.toFixed(1);
            }
        }
    } else if (Number.isInteger(newValue) && step >= 1) {
        // For whole numbers with step >= 1
        this.value = newValue.toString();
    } else {
        // For decimal values, use appropriate precision
        const decimals = step.toString().includes(".")
            ? step.toString().split(".")[1].length
            : 1;

        // Preserve comma as decimal separator if that's what user entered
        if (useCommaAsDecimal) {
            this.value = newValue.toFixed(decimals).replace(".", ",");
        } else {
            this.value = newValue.toFixed(decimals);
        }
    }

    // Trigger change events
    this.dispatchEvent(new Event("change", { bubbles: true }));
    this.dispatchEvent(new Event("input", { bubbles: true }));
}

/**
 * Handle cell count input fields
 * @param {HTMLElement} input - The cell count input element
 */
function handleCellCountInput(input) {
    input.addEventListener("input", function (e) {
        if (this._programmaticSet) return;

        this.classList.remove("default-input");
        this.classList.add("active-input");

        // Minimal validation during typing
        const value = this.value;
        const cleanedValue = value.replace(/[^0-9.,]/g, "");

        if (value !== cleanedValue) {
            this.value = cleanedValue;
        }
    });

    input.addEventListener("change", function () {
        if (this._programmaticSet) return;

        if (this.value !== "") {
            const numValue = parseDecimalInput(this.value);
            if (!isNaN(numValue)) {
                if (this.value.includes(",") && !this.value.includes(".")) {
                    const parts = this.value.split(",");
                    const intPart = parts[0];
                    let decPart = parts[1] || "0";
                    decPart = decPart.substring(0, 1).padEnd(1, "0");

                    this.value = intPart + "," + decPart;
                } else {
                    // Check if it's a whole number
                    if (Number.isInteger(numValue)) {
                        this.value = numValue.toString();
                    } else {
                        this.value = numValue.toFixed(1);
                    }
                }
            }
        }

        if (parseDecimalInput(this.value) < 0) {
            this.value = "0";
        }
    });

    input.addEventListener("blur", function () {
        if (this._programmaticSet) return;

        if (this.value !== "") {
            const numValue = parseDecimalInput(this.value);
            if (!isNaN(numValue)) {
                if (this.value.includes(",") && !this.value.includes(".")) {
                    const parts = this.value.split(",");
                    const intPart = parts[0];
                    let decPart = parts[1] || "0";
                    decPart = decPart.substring(0, 1).padEnd(1, "0");

                    this.value = intPart + "," + decPart;
                } else {
                    // Check if it's a whole number
                    if (Number.isInteger(numValue)) {
                        this.value = numValue.toString();
                    } else {
                        this.value = numValue.toFixed(1);
                    }
                }
            }
        }
    });
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
            performCalculation();
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
        resetBtn.addEventListener("click", resetCalculator);
    }

    if (recalculateBtn) {
        recalculateBtn.addEventListener("click", performCalculation);
    }

    if (downloadExcelBtn) {
        downloadExcelBtn.addEventListener("click", function (e) {
            e.preventDefault();
            downloadAsExcel();
        });
    }

    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener("click", function (e) {
            e.preventDefault();
            downloadAsPdf();
        });
    }
}

/**
 * Setup validation warnings for cell count and viability
 */
function setupValidationWarnings() {

}

/**
 * Prevent tooltip clicks from selecting inputs
 */
function preventTooltipPropagation() {
    document.querySelectorAll(".tooltip-container").forEach((tooltip) => {
        tooltip.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
        });
    });
}

/**
 * Hide validation errors when focusing on any input
 */
function hideValidationErrorsOnFocus() {
    document.querySelectorAll("input, select").forEach((el) => {
        el.addEventListener("focus", function () {
            const validationErrors =
                document.getElementById("validationErrors");
            if (validationErrors) {
                validationErrors.classList.add("hidden");
            }
        });
    });
}

/**
 * Validates that cell count fields are filled sequentially
 * @param {string} currentFieldId - The current field being typed in
 * @returns {boolean} - Whether the field should be enabled
 */
function validateCellCountSequence(currentFieldId) {
    const count1 = document.getElementById("count1");
    const count2 = document.getElementById("count2");
    const count3 = document.getElementById("count3");

    const count1Value = count1 ? parseDecimalInput(count1.value) : 0;
    const count2Value = count2 ? parseDecimalInput(count2.value) : 0;

    switch (currentFieldId) {
        case "count1":
            return true; // Count1 is always allowed
        case "count2":
            return !isNaN(count1Value) && count1Value > 0;
        case "count3":
            return (
                !isNaN(count1Value) &&
                count1Value > 0 &&
                !isNaN(count2Value) &&
                count2Value > 0
            );
        default:
            return true;
    }
}

/**
 * Validates that viability fields are filled sequentially
 * @param {string} currentFieldId - The current field being typed in
 * @returns {boolean} - Whether the field should be enabled
 */
function validateViabilitySequence(currentFieldId) {
    const viability1 = document.getElementById("viability1");
    const viability2 = document.getElementById("viability2");
    const viability3 = document.getElementById("viability3");

    const viability1Value = viability1
        ? parseDecimalInput(viability1.value)
        : 0;
    const viability2Value = viability2
        ? parseDecimalInput(viability2.value)
        : 0;

    switch (currentFieldId) {
        case "viability1":
            return true; // Viability1 is always allowed
        case "viability2":
            return !isNaN(viability1Value) && viability1Value > 0;
        case "viability3":
            return (
                !isNaN(viability1Value) &&
                viability1Value > 0 &&
                !isNaN(viability2Value) &&
                viability2Value > 0
            );
        default:
            return true;
    }
}

/**
 * Disables a field and shows visual feedback
 * @param {HTMLElement} field - The field to disable
 * @param {string} reason - The reason for disabling
 */
function disableFieldWithFeedback(field, reason) {
    if (!field) return;

    field.disabled = true;
    field.style.backgroundColor = "#f5f5f5";
    field.style.cursor = "not-allowed";
    field.placeholder = reason;
    field.title = reason;
}

/**
 * Enables a field and removes visual feedback
 * @param {HTMLElement} field - The field to enable
 */
function enableField(field) {
    if (!field) return;

    field.disabled = false;
    field.style.backgroundColor = "";
    field.style.cursor = "";
    field.placeholder = "";
    field.title = "";
}

/**
 * Updates the state of cell count fields based on sequential validation
 */
function updateCellCountFieldStates() {
    const count1 = document.getElementById("count1");
    const count2 = document.getElementById("count2");
    const count3 = document.getElementById("count3");

    // Count1 is always enabled
    if (count1) enableField(count1);

    // Count2 depends on count1
    if (count2) {
        if (validateCellCountSequence("count2")) {
            enableField(count2);
        } else {
            disableFieldWithFeedback(count2, "");
            count2.value = ""; // Clear invalid value
        }
    }

    // Count3 depends on count1 and count2
    if (count3) {
        if (validateCellCountSequence("count3")) {
            enableField(count3);
        } else {
            disableFieldWithFeedback(count3, "");
            count3.value = ""; // Clear invalid value
        }
    }
}

/**
 * Updates the state of viability fields based on sequential validation
 */
function updateViabilityFieldStates() {
    const viability1 = document.getElementById("viability1");
    const viability2 = document.getElementById("viability2");
    const viability3 = document.getElementById("viability3");

    // Viability1 is always enabled
    if (viability1) enableField(viability1);

    // Viability2 depends on viability1
    if (viability2) {
        if (validateViabilitySequence("viability2")) {
            enableField(viability2);
        } else {
            disableFieldWithFeedback(viability2, "");
            viability2.value = ""; // Clear invalid value
        }
    }

    // Viability3 depends on viability1 and viability2
    if (viability3) {
        if (validateViabilitySequence("viability3")) {
            enableField(viability3);
        } else {
            disableFieldWithFeedback(viability3, "");
            viability3.value = ""; // Clear invalid value
        }
    }
}

/**
 * Sets up sequential validation for cell count and viability fields
 */
function setupSequentialValidation() {
    // Cell count field validation
    const cellCountFields = ["count1", "count2", "count3"];
    cellCountFields.forEach((fieldId) => {
        const field = document.getElementById(fieldId);
        if (field) {
            // Add input event listener
            field.addEventListener("input", function () {
                updateCellCountFieldStates();
            });

            // Add change event listener
            field.addEventListener("change", function () {
                updateCellCountFieldStates();
            });

            // Add focus event listener to prevent typing in disabled fields
            field.addEventListener("focus", function (e) {
                if (!validateCellCountSequence(fieldId)) {
                    e.target.blur();
                    showValidationMessage(
                        fieldId,
                        "Please fill the previous cell count field first"
                    );
                }
            });

            // Add keydown event listener to prevent typing in disabled fields
            field.addEventListener("keydown", function (e) {
                if (!validateCellCountSequence(fieldId)) {
                    e.preventDefault();
                }
            });
        }
    });

    // Viability field validation
    const viabilityFields = ["viability1", "viability2", "viability3"];
    viabilityFields.forEach((fieldId) => {
        const field = document.getElementById(fieldId);
        if (field) {
            // Add input event listener
            field.addEventListener("input", function () {
                updateViabilityFieldStates();
            });

            // Add change event listener
            field.addEventListener("change", function () {
                updateViabilityFieldStates();
            });

            // Add focus event listener to prevent typing in disabled fields
            field.addEventListener("focus", function (e) {
                if (!validateViabilitySequence(fieldId)) {
                    e.target.blur();
                    showValidationMessage(
                        fieldId,
                        "Please fill the previous viability field first"
                    );
                }
            });

            // Add keydown event listener to prevent typing in disabled fields
            field.addEventListener("keydown", function (e) {
                if (!validateViabilitySequence(fieldId)) {
                    e.preventDefault();
                }
            });
        }
    });

    // Initialize field states
    updateCellCountFieldStates();
    updateViabilityFieldStates();
}

/**
 * Shows a temporary validation message for a field
 * @param {string} fieldId - The field ID
 * @param {string} message - The message to show
 */
function showValidationMessage(fieldId, message) {
    // Remove any existing validation message
    const existingMessage = document.querySelector(".validation-message");
    if (existingMessage) {
        existingMessage.remove();
    }

    const field = document.getElementById(fieldId);
    if (!field) return;

    // Create validation message element
    const messageDiv = document.createElement("div");
    messageDiv.className = "validation-message";
    messageDiv.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        background: #fee;
        border: 1px solid #fcc;
        color: #c33;
        padding: 4px 8px;
        font-size: 12px;
        border-radius: 4px;
        z-index: 1000;
        white-space: nowrap;
        margin-top: 2px;
    `;
    messageDiv.textContent = message;

    // Position the message relative to the field
    field.parentElement.style.position = "relative";
    field.parentElement.appendChild(messageDiv);

    // Remove message after 3 seconds
    setTimeout(() => {
        if (messageDiv.parentElement) {
            messageDiv.remove();
        }
    }, 3000);
}

/**
 * Initialize the calculator app
 */
async function initCalculator() {
    // Setup event listeners
    setupEventListeners();

    let cellTypes = [];
    let cultureVessels = [];

    // Fetch data in parallel
    try {
        const [typesResponse, vesselsResponse] = await Promise.all([
            fetch("products"),
            fetch("culture-vessels", {
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
    }
}

// Initialize calculator when document is ready
// Note: This is now handled by main.js to avoid duplicate event listeners
// document.addEventListener("DOMContentLoaded", initCalculator);
