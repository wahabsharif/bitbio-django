/**
 * Export helpers: download Excel and PDF via Django endpoints
 */

(function(){
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function parseDecimalInput(value) {
        if (!value || String(value).trim() === '') return NaN;
        if (value.includes(',') && !value.includes('.')) {
            var commaCount = (value.match(/,/g) || []).length;
            if (commaCount === 1) {
                return parseFloat(value.replace(',', '.'));
            }
        }
        var normalized = String(value).replace(/,/g, '');
        var result = parseFloat(normalized);
        return isNaN(result) ? NaN : result;
    }

    function getDropdownText(dropdownSelector) {
        try {
            var dd = window.jQuery ? window.jQuery(dropdownSelector) : null;
            if (dd && dd.length && typeof dd.dropdown === 'function') {
                var text = dd.dropdown('get text');
                return text || '-';
            }
        } catch (e) {}
        var el = document.querySelector(dropdownSelector + ' .text, ' + dropdownSelector + ' .default.text');
        return el && el.textContent ? el.textContent : '-';
    }

    function getResultData() {
        var cellDensityEl = document.getElementById('cell_density_formatted');
        var cellsPerWellEl = document.getElementById('cells_per_well_formatted');
        var requiredCellsEl = document.getElementById('required_cells_total_formatted');
        var volumeToDiluteEl = document.getElementById('volume_to_dilute');
        var volumeToSeedEl = document.getElementById('volume_to_seed');
        var volumePerWellEl = document.getElementById('volume_plate_perwell_simple');

        var suspensionVolumeEl = document.getElementById('suspension_volume');
        var count1El = document.getElementById('count1');
        var count2El = document.getElementById('count2');
        var count3El = document.getElementById('count3');
        var viability1El = document.getElementById('viability1');
        var viability2El = document.getElementById('viability2');
        var viability3El = document.getElementById('viability3');
        var seedingDensityEl = document.getElementById('seeding_density');
        var cultureVesselEl = document.getElementById('culture_vessel');
        var surfaceAreaEl = document.getElementById('surface_area');
        var mediaVolumeEl = document.getElementById('media_volume');
        var numWellsEl = document.getElementById('num_wells');
        var bufferEl = document.getElementById('buffer');

        var counts = [
            parseDecimalInput(count1El && count1El.value),
            parseDecimalInput(count2El && count2El.value),
            parseDecimalInput(count3El && count3El.value)
        ].filter(function(n){ return typeof n === 'number' && n > 0; });
        var avgCount = counts.length ? (counts.reduce(function(a,b){return a+b;},0) / counts.length).toFixed(2) : '-';

        var viabilities = [
            parseDecimalInput(viability1El && viability1El.value),
            parseDecimalInput(viability2El && viability2El.value),
            parseDecimalInput(viability3El && viability3El.value)
        ].filter(function(n){ return typeof n === 'number' && n > 0; });
        var avgViability = viabilities.length ? (viabilities.reduce(function(a,b){return a+b;},0) / viabilities.length).toFixed(1) : '-';

        var cellTypeText = getDropdownText('#cell_type_dropdown');
        var cultureVesselText = getDropdownText('#culture_vessel_dropdown');

        return {
            cellDensity: cellDensityEl ? cellDensityEl.innerHTML : '',
            cellsPerWell: cellsPerWellEl ? cellsPerWellEl.textContent : '',
            requiredCells: requiredCellsEl ? requiredCellsEl.innerHTML : '',
            volumeToDilute: volumeToDiluteEl ? volumeToDiluteEl.textContent : '',
            volumeToSeed: volumeToSeedEl ? volumeToSeedEl.textContent : '',
            volumePerWell: volumePerWellEl ? volumePerWellEl.textContent : '',

            suspensionVolume: suspensionVolumeEl ? suspensionVolumeEl.value : '',
            liveCellCount: avgCount,
            cellViability: avgViability,
            cellType: cellTypeText || '-',
            seedingDensity: seedingDensityEl ? seedingDensityEl.value : '',
            cultureVessel: cultureVesselText || '-',
            surfaceArea: surfaceAreaEl ? surfaceAreaEl.value : '',
            mediaVolume: mediaVolumeEl ? mediaVolumeEl.value : '',
            wellCount: numWellsEl ? (numWellsEl.value || '0') : '0',
            buffer: bufferEl ? bufferEl.value : '',

            count1: count1El ? count1El.value : '',
            count2: count2El ? count2El.value : '',
            count3: count3El ? count3El.value : '',
            viability1: viability1El ? viability1El.value : '',
            viability2: viability2El ? viability2El.value : '',
            viability3: viability3El ? viability3El.value : ''
        };
    }

    function appendHidden(form, name, value) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value || '';
        form.appendChild(input);
    }

    window.downloadAsExcel = function() {
        if (window.isDownloading) return;
        window.isDownloading = true;

        var data = getResultData();
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/calculator/download-excel/';
        form.style.display = 'none';

        // CSRF (view is csrf_exempt, but include if present)
        var csrftoken = getCookie('csrftoken');
        if (csrftoken) {
            appendHidden(form, 'csrfmiddlewaretoken', csrftoken);
        }

        Object.keys(data).forEach(function(key){ appendHidden(form, key, data[key]); });

        // Timezone
        var tz = 'UTC';
        try {
            var resolved = Intl.DateTimeFormat().resolvedOptions().timeZone;
            if (resolved) tz = resolved;
        } catch(e) {}
        appendHidden(form, 'timezone', tz);

        document.body.appendChild(form);
        try { form.submit(); } catch (e) { console.error('Excel download failed', e); }

        setTimeout(function(){ try { document.body.removeChild(form); } catch(e){} window.isDownloading = false; }, 1500);
    };

    window.downloadAsPdf = function() {
        if (window.isDownloading) return;
        window.isDownloading = true;

        var data = getResultData();
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/calculator/download-pdf/';
        form.style.display = 'none';

        var csrftoken = getCookie('csrftoken');
        if (csrftoken) {
            appendHidden(form, 'csrfmiddlewaretoken', csrftoken);
        }

        Object.keys(data).forEach(function(key){ appendHidden(form, key, data[key]); });

        var tz = 'UTC';
        try { var resolved = Intl.DateTimeFormat().resolvedOptions().timeZone; if (resolved) tz = resolved; } catch(e) {}
        appendHidden(form, 'timezone', tz);

        var warningsDiv = document.getElementById('warnings');
        var warningsText = '';
        if (warningsDiv && !warningsDiv.classList.contains('hidden')) {
            warningsText = warningsDiv.textContent || '';
        }
        appendHidden(form, 'warnings', warningsText);

        document.body.appendChild(form);
        try { form.submit(); } catch (e) { console.error('PDF download failed', e); }
        setTimeout(function(){ try { document.body.removeChild(form); } catch(e){} window.isDownloading = false; }, 1500);
    };
})();


