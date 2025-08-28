// cell-checks.js

/**
 * Fallback parseDecimalInput function if the one from calculator.js is not available
 */
function parseDecimalInput(value) {
    // Fallback implementation
    if (!value || value === '') {
        return 0;
    }
    const result = parseFloat(String(value).replace(',', '.'));
    return result;
}

/**
 * Checks cell count variability and shows warning if necessary
 */
function checkCellCountVariability() {
    const count1El = document.getElementById("count1");
    const count2El = document.getElementById("count2");
    const count3El = document.getElementById("count3");
    const cellCountWarning = document.getElementById("cellCountWarning");

    if (!count1El || !cellCountWarning) {
        return;
    }

    const counts = [
        parseDecimalInput(count1El.value),
        count2El && count2El.value ? parseDecimalInput(count2El.value) : 0,
        count3El && count3El.value ? parseDecimalInput(count3El.value) : 0,
    ].filter((count) => count > 0); // Only consider non-zero values

    // Need at least 2 counts to compare
    if (counts.length < 2) {
        cellCountWarning.classList.add("hidden");
        cellCountWarning.classList.remove("show-warning");
        return;
    }

    let showWarning = false;

    // Check each pair of counts for ≥10% variability
    for (let i = 0; i < counts.length - 1; i++) {
        for (let j = i + 1; j < counts.length; j++) {
            const larger = Math.max(counts[i], counts[j]);
            const smaller = Math.min(counts[i], counts[j]);

            // Calculate percentage difference relative to the larger value
            const percentDiff = ((larger - smaller) / larger) * 100;

            if (percentDiff >= 10) {
                showWarning = true;
                break;
            }
        }
        if (showWarning) break;
    }

    if (showWarning) {
        // Remove hidden class and add show-warning class
        cellCountWarning.classList.remove("hidden");
        cellCountWarning.classList.add("show-warning");
    } else {
        // Remove show-warning class and add hidden class
        cellCountWarning.classList.remove("show-warning");
        cellCountWarning.classList.add("hidden");
    }
}

/**
 * Checks viability values and shows warning if necessary
 */
function checkViabilityValues() {
    const viabilityWarning = document.getElementById("viabilityWarning");
    if (!viabilityWarning) {
        return;
    }

    // Get all viability inputs
    const viability1 = document.getElementById("viability1");
    const viability2 = document.getElementById("viability2");
    const viability3 = document.getElementById("viability3");

    // Check if any input has been filled with a value that would trigger the warning
    let showWarning = false;

    // Check if any filled field has a value of 0 or below 80%
    if (viability1 && viability1.value !== "") {
        const val1 = parseFloat(viability1.value);
        if (val1 === 0 || (val1 > 0 && val1 < 80)) {
            showWarning = true;
        }
    }

    if (viability2 && viability2.value !== "") {
        const val2 = parseFloat(viability2.value);
        if (val2 === 0 || (val2 > 0 && val2 < 80)) {
            showWarning = true;
        }
    }

    if (viability3 && viability3.value !== "") {
        const val3 = parseFloat(viability3.value);
        if (val3 === 0 || (val3 > 0 && val3 < 80)) {
            showWarning = true;
        }
    }

    // Update warning visibility
    if (showWarning) {
        // Remove hidden class and add show-warning class
        viabilityWarning.classList.remove("hidden");
        viabilityWarning.classList.add("show-warning");
    } else {
        // Remove show-warning class and add hidden class
        viabilityWarning.classList.remove("show-warning");
        viabilityWarning.classList.add("hidden");
    }
}

// Make functions globally available
window.checkCellCountVariability = checkCellCountVariability;
window.checkViabilityValues = checkViabilityValues;
