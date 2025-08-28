// calculator.js

/**
 * Helper function to parse decimal input that may use comma as decimal separator.
 * Returns a Number or 0 if parsing fails / empty.
 */
function parseDecimalInput(value) {
    if (!value) return 0;
    // Replace comma with dot for proper parsing
    const normalizedValue = value.toString().replace(",", ".");
    return parseFloat(normalizedValue) || 0;
}

/**
 * Helper function to format a volume value based on unit:
 * - If unit is 'uL', return an integer string (no decimal places).
 * - If unit is 'mL', return a string with two decimal places.
 * - Otherwise, just return the value as string.
 *
 * @param {number} value - numeric value to format
 * @param {string} unit  - either 'uL' or 'mL'
 * @returns {string}
 */
function formatVolume(value, unit) {
    if (unit === "uL") {
        // Round to nearest integer
        return Math.round(value).toString();
    } else if (unit === "mL") {
        // Always show two decimal places
        return value.toFixed(2);
    }
    // Fallback
    return value.toString();
}

/**
 * Formats a number in exponential notation with superscript exponent.
 * E.g. 1.23e+06 → "1.23 x 10⁶"
 *
 * @param {number} num
 * @returns {string}
 */
function formatExponential(num) {
    const exp = num.toExponential(2);
    const parts = exp.split("e+");

    // Map for converting digits to superscript Unicode characters
    const superscriptMap = {
        0: "⁰",
        1: "¹",
        2: "²",
        3: "³",
        4: "⁴",
        5: "⁵",
        6: "⁶",
        7: "⁷",
        8: "⁸",
        9: "⁹",
    };

    // Convert each digit in the exponent to superscript
    const superscriptExp = parts[1]
        .split("")
        .map((digit) => superscriptMap[digit] || "")
        .join("");

    return `${parts[0]} x 10${superscriptExp}`;
}

/**
 * Performs all calculations and updates the UI with results
 */
function performCalculation() {
    // Validate required fields first
    const missingFields = validateRequiredFields();
    const warningsDiv = document.getElementById("warnings");
    const validationErrorsDiv = document.getElementById("validationErrors");
    const helpContent = document.getElementById("helpContent");
    const resultsContent = document.getElementById("resultsContent");

    // Add null checks for all critical elements
    if (!warningsDiv || !helpContent || !resultsContent) {
        console.error("Critical DOM elements not found");
        return;
    }

    // Silently validate - show popup if fields are missing
    if (missingFields.length > 0) {
        // Clear any previous validation error messages
        if (validationErrorsDiv) {
            validationErrorsDiv.classList.add("hidden");
            validationErrorsDiv.innerHTML = "";
        }

        // Show the missing fields popup
        showMissingFieldsPopup(missingFields);
        return; // Stop execution if validation fails
    } else {
        // Hide the popup if validation passes
        hideMissingFieldsPopup();
        if (validationErrorsDiv) {
            validationErrorsDiv.classList.add("hidden");
            validationErrorsDiv.innerHTML = "";
        }
    }

    // Hide help content and show results content
    helpContent.classList.add("hidden");
    resultsContent.classList.remove("hidden");

    // Get button elements with null checks
    const calculateBtn = document.getElementById("calculateBtn");
    const actionButtons = document.getElementById("actionButtons");
    const downloadOptions = document.getElementById("downloadOptions");
    const copyPasteInfo = document.getElementById("copyPasteInfo");

    // Only manipulate elements that exist
    if (calculateBtn) {
        calculateBtn.classList.add("hidden");
    }
    if (actionButtons) {
        actionButtons.classList.remove("hidden");
    }
    if (downloadOptions) {
        downloadOptions.classList.remove("hidden");
    }
    if (copyPasteInfo) {
        copyPasteInfo.classList.remove("hidden");
    }

    // Gather inputs with null checks
    const seedingEl = document.getElementById("seeding_density");
    const wellsEl = document.getElementById("num_wells");
    const areaEl = document.getElementById("surface_area");
    const mediaVolEl = document.getElementById("media_volume");
    const count1El = document.getElementById("count1");
    const count2El = document.getElementById("count2");
    const count3El = document.getElementById("count3");
    const viability1El = document.getElementById("viability1");
    const viability2El = document.getElementById("viability2");
    const viability3El = document.getElementById("viability3");
    const bufferEl = document.getElementById("buffer");
    const suspensionVolEl = document.getElementById("suspension_volume");

    // Check if required elements exist
    if (
        !seedingEl ||
        !wellsEl ||
        !areaEl ||
        !mediaVolEl ||
        !count1El ||
        !viability1El ||
        !bufferEl ||
        !suspensionVolEl
    ) {
        console.error("Required input elements not found");
        return;
    }

    // Parse input values
    const seeding = parseFloat(seedingEl.value) || 0;
    const wells = parseInt(wellsEl.value) || 0;
    const area = parseFloat(areaEl.value) || 0;
    const mediaVol = parseFloat(mediaVolEl.value) || 0;
    const counts = [
        parseDecimalInput(count1El.value),
        count2El ? parseDecimalInput(count2El.value) : 0,
        count3El ? parseDecimalInput(count3El.value) : 0,
    ];
    const viabilities = [
        parseFloat(viability1El.value) || 0,
        viability2El ? parseFloat(viability2El.value) || 0 : 0,
        viability3El ? parseFloat(viability3El.value) || 0 : 0,
    ];
    const bufferPerc = parseFloat(bufferEl.value) || 0;
    const suspensionVol = parseFloat(suspensionVolEl.value) || 1;

    // Compute averages
    const validCounts = counts.filter((n) => n > 0);
    const validViabilities = viabilities.filter((n) => n > 0);

    if (validCounts.length === 0 || validViabilities.length === 0) {
        console.error("No valid cell counts or viabilities found");
        return;
    }

    const avgCount =
        validCounts.reduce((a, b) => a + b, 0) / validCounts.length;
    const avgViab =
        validViabilities.reduce((a, b) => a + b, 0) / validViabilities.length;

    // FIXED CALCULATION 1: Cell density calculation
    // Input counts are in 10^6 cells/mL format, so multiply by 1,000,000 to get actual cells/mL
    // Then apply viability percentage and account for suspension volume
    const cellDensity = (avgCount * 1000000 * (avgViab / 100)) / suspensionVol;
    // This gives us viable cells/mL in the suspension

    // FIXED CALCULATION 2: Cells per well calculation
    const cellsPerWell = seeding * area;

    // FIXED CALCULATION 3: Total required cells calculation
    let requiredCells = cellsPerWell * wells;
    requiredCells *= 1 + bufferPerc / 100; // Apply buffer percentage correctly

    // FIXED CALCULATION 4: Volume calculations
    const volToSeed = requiredCells / cellDensity; // Volume of cell suspension needed (mL)
    const totalMediaPerWell = mediaVol; // Media volume per well (mL)
    const totalMediaNeeded = totalMediaPerWell * wells; // Total media for all wells (mL)
    const totalMediaWithBuffer = totalMediaNeeded * (1 + bufferPerc / 100); // Add buffer to media

    // FIXED CALCULATION 5: Final dilution volume calculation
    // Total final volume = cell suspension volume + additional media volume
    const volDilute = totalMediaWithBuffer - volToSeed; // Additional media needed for dilution (mL)

    // Ensure volDilute is not negative
    if (volDilute < 0) {
        console.warn(
            "Warning: Cell suspension volume exceeds total media volume"
        );
    }

    // FIXED CALCULATION 6: Volume per well for final step
    const volPlatePerWell = totalMediaWithBuffer / wells; // Final volume per well (mL)

    // Build calculation warnings (not validation errors)
    const warningsArr = [];

    // FIXED WARNING LOGIC: Compare total available cells vs required cells
    const totalAvailableCells = cellDensity * suspensionVol;
    if (requiredCells > totalAvailableCells) {
        warningsArr.push(
            "Please note that the number of live cells available is insufficient for your experimental design. Please review your setup and consider adjustments, such as reducing the number of wells used in the experiment."
        );
    }

    if (bufferPerc === 0) {
        warningsArr.push(
            "⚠️ It is highly recommended to include a buffer to ensure enough cells and media."
        );
    }

    // Check if cell suspension volume is too small for accurate pipetting
    if (volToSeed < 0.1) {
        warningsArr.push(
            "The required cell suspension volume is very small (" +
                formatVolume(volToSeed, "mL") +
                " mL). Consider using fewer wells or increasing the suspension volume for more accurate pipetting."
        );
    }

    if (warningsArr.length) {
        warningsDiv.innerHTML = warningsArr
            .map(
                (msg, index) => `
            <div id="warning-${index}" class="flex justify-between no-print items-start mb-2">
                <div class="flex justify-between text-orange-700">
                    <svg class="h-5 w-5 text-orange-500 mr-2 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                        <path fill-rule="evenodd" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 11c-.55 0-1-.45-1-1V8c0-.55.45-1 1-1s1 .45 1 1v4c0 .55-.45 1-1 1zm1 4h-2v-2h2v2z" />
                    </svg>
                </div>
                <p class="flex-grow mx-2">${msg}</p>
                <button type="button" class="ml-auto text-[#96a5b8]" onclick="document.getElementById('warning-${index}').remove(); checkRemainingWarnings();">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `
            )
            .join("");
        warningsDiv.classList.remove("hidden");
    } else {
        warningsDiv.classList.add("hidden");
    }

    // Display results in the side panel with null checks
    const wellCountEl = document.getElementById("wellCount");
    const volumeToDiluteEl = document.getElementById("volume_to_dilute");
    const volumeToSeedEl = document.getElementById("volume_to_seed");
    const volumePlatePerWellEl = document.getElementById(
        "volume_plate_perwell_simple"
    );
    const cellDensityFormattedEl = document.getElementById(
        "cell_density_formatted"
    );
    const requiredCellsFormattedEl = document.getElementById(
        "required_cells_total_formatted"
    );
    const cellsPerWellFormattedEl = document.getElementById(
        "cells_per_well_formatted"
    );

    if (wellCountEl) wellCountEl.textContent = wells;
    if (volumeToDiluteEl) {
        // volDilute is in mL → show 2 decimal places
        const val = Math.max(0, volDilute);
        volumeToDiluteEl.textContent = formatVolume(val, "mL");
    }
    if (volumeToSeedEl) {
        // volToSeed is in mL → show 2 decimal places
        volumeToSeedEl.textContent = formatVolume(volToSeed, "mL");
    }
    if (volumePlatePerWellEl) {
        // volPlatePerWell in mL, but display in µL without decimals
        const ulValue = volPlatePerWell * 1000;
        volumePlatePerWellEl.textContent = formatVolume(ulValue, "uL");
    }
    if (cellDensityFormattedEl)
        cellDensityFormattedEl.textContent = formatExponential(cellDensity);
    if (requiredCellsFormattedEl)
        requiredCellsFormattedEl.textContent = formatExponential(requiredCells);
    if (cellsPerWellFormattedEl) {
        cellsPerWellFormattedEl.textContent = cellsPerWell.toLocaleString(
            undefined,
            {
                maximumFractionDigits: 0,
            }
        );
    }

    // Update narrative elements
    const narrativeElements = {
        narrativeWellCount: wells,
        // narrativeVolumeSeed in mL → 2 decimal places
        narrativeVolumeSeed: formatVolume(volToSeed, "mL"),
        // narrativeVolumeDilute in mL → 2 decimal places, not negative
        narrativeVolumeDilute: formatVolume(Math.max(0, volDilute), "mL"),
        // narrativeVolumePerWell in µL → integer
        narrativeVolumePerWell: formatVolume(volPlatePerWell * 1000, "uL"),
        narrativeCellDensity: formatExponential(cellDensity),
        narrativeCellsPerWell: cellsPerWell.toLocaleString(undefined, {
            maximumFractionDigits: 0,
        }),
    };

    // Update each narrative element
    Object.entries(narrativeElements).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    });

    // Setup click-to-copy functionality
    const narrativeText = document.getElementById("narrativeText");
    if (narrativeText) {
        // To avoid multiple listeners, consider removing existing listener first in real code.
        narrativeText.addEventListener("click", function () {
            const copyIndicator = document.getElementById("copyIndicator");

            navigator.clipboard
                .writeText(this.textContent.trim().replace("Copied!", ""))
                .then(() => {
                    // Show the copy indicator
                    if (copyIndicator) {
                        copyIndicator.classList.remove("hidden");

                        // Hide the indicator after 2 seconds
                        setTimeout(() => {
                            copyIndicator.classList.add("hidden");
                        }, 2000);
                    }
                })
                .catch((err) => {
                    console.error("Failed to copy text: ", err);
                });
        });
    }

    // Mark all inputs used in calculations as active
    const inputsUsedInCalculation = [
        "seeding_density",
        "num_wells",
        "surface_area",
        "media_volume",
        "count1",
        "count2",
        "count3",
        "viability1",
        "viability2",
        "viability3",
        "buffer",
        "suspension_volume",
    ];

    inputsUsedInCalculation.forEach((id) => {
        const input = document.getElementById(id);
        if (input) {
            input.classList.remove("default-input");
            input.classList.add("active-input");
        }
    });

    // Note: Warning checks are now handled by event listeners in main.js
    // No need to call checkViabilityValues() and checkCellCountVariability() here
}

/**
 * Shows the missing fields popup with a list of missing fields
 * @param {Array} missingFields - Array of missing field objects with id and name properties
 */
function showMissingFieldsPopup(missingFields) {
    const popup = document.getElementById("missingFieldsPopup");
    const fieldsList = document.getElementById("missingFieldsList");

    if (!popup || !fieldsList) {
        console.error("Missing fields popup elements not found");
        return;
    }

    // Clear existing list
    fieldsList.innerHTML = "";

    // Populate the list with missing fields
    missingFields.forEach((field) => {
        const listItem = document.createElement("li");
        listItem.textContent = field.name || field.id;
        fieldsList.appendChild(listItem);
    });

    // Show the popup
    popup.classList.remove("hidden");

    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideMissingFieldsPopup();
    }, 5000);
}

/**
 * Hides the missing fields popup
 */
function hideMissingFieldsPopup() {
    const popup = document.getElementById("missingFieldsPopup");
    if (popup) {
        popup.classList.add("hidden");
    }
}

// Add event listener for the close button when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
    const closeButton = document.getElementById("closeMissingFieldsPopup");
    if (closeButton) {
        closeButton.addEventListener("click", hideMissingFieldsPopup);
    }
});

/**
 * Checks if there are any remaining warnings and hides the container if empty
 */
function checkRemainingWarnings() {
    const warningsDiv = document.getElementById("warnings");
    if (!warningsDiv) return;

    // Get all warning elements inside the warnings div
    const remainingWarnings = warningsDiv.querySelectorAll('[id^="warning-"]');

    // If no warnings remain, hide the container
    if (remainingWarnings.length === 0) {
        warningsDiv.classList.add("hidden");
    }
}

// These functions are now defined in cell-checks.js

