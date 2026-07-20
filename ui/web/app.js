/* ============================================
   Excel2SBOL — Frontend Logic
   pywebview JS ↔ Python API bridge
   ============================================ */

/* ============================================
   SHARED STATE
   ============================================ */

let initialized = false;

/* ============================================
   INIT
   ============================================ */

function init() {
    if (initialized) return;
    initialized = true;

    // Tab switching
    document.querySelectorAll('.tab').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    initConverter();
    initSpreadsheetCreator();

    updateTabIndicator();
    window.addEventListener('resize', updateTabIndicator);
}

window.addEventListener('pywebviewready', () => init());

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => { if (!initialized) init(); }, 500);
});

/* ============================================
   TABS
   ============================================ */

function switchTab(tabId) {
    document.querySelectorAll('.tab').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });
    document.querySelectorAll('.tab-content').forEach(panel => {
        panel.classList.toggle('active', panel.id === 'tab-' + tabId);
    });
    updateTabIndicator();
}

function updateTabIndicator() {
    const activeTab = document.querySelector('.tab.active');
    const indicator = document.getElementById('tab-indicator');
    if (activeTab && indicator) {
        indicator.style.width = activeTab.offsetWidth + 'px';
        indicator.style.transform = `translateX(${activeTab.offsetLeft}px)`;
    }
}

/* ============================================
   CONVERTER
   ============================================ */

let pollingTimer = null;
let currentFilePath = null;

function initConverter() {
    document.getElementById('btn-browse').addEventListener('click', pickFile);
    document.getElementById('chk-signin').addEventListener('change', onSigninToggle);
    document.getElementById('domain-input').addEventListener('input', updateConvertButton);
    document.getElementById('email-input').addEventListener('input', updateConvertButton);
    document.getElementById('password-input').addEventListener('input', updateConvertButton);
    document.getElementById('btn-convert').addEventListener('click', runConversion);
    loadHistory();
}

async function pickFile() {
    if (!window.pywebview?.api) return;
    try {
        const path = await window.pywebview.api.pick_file();
        if (!path) return;
        currentFilePath = path;
        document.getElementById('file-path').value = path.split(/[\\/]/).pop();

        const raw = await window.pywebview.api.get_excel_metadata(path);
        const meta = JSON.parse(raw);

        if (meta.sbol_version === 3) {
            document.getElementById('sbol-v3').checked = true;
        } else {
            document.getElementById('sbol-v2').checked = true;
        }
        if (meta.domain) document.getElementById('domain-input').value = meta.domain;
        if (meta.email)  document.getElementById('email-input').value  = meta.email;

        updateConvertButton();
    } catch (e) {
        console.error('[pickFile]', e);
    }
}

function onSigninToggle(e) {
    document.getElementById('signin-fields').classList.toggle('hidden', !e.target.checked);
    updateConvertButton();
}

async function loadHistory() {
    if (!window.pywebview?.api) return;
    try {
        const raw = await window.pywebview.api.get_history();
        const history = JSON.parse(raw);
        const domainList = document.getElementById('domain-list');
        const emailList  = document.getElementById('email-list');
        domainList.innerHTML = '';
        emailList.innerHTML  = '';
        history.domains.forEach(d => {
            const o = document.createElement('option'); o.value = d; domainList.appendChild(o);
        });
        history.emails.forEach(e => {
            const o = document.createElement('option'); o.value = e; emailList.appendChild(o);
        });
    } catch (e) {
        console.error('[loadHistory]', e);
    }
}

function updateConvertButton() {
    const hasFile   = !!currentFilePath;
    const useSignin = document.getElementById('chk-signin').checked;
    const signinOk  = !useSignin || !!(
        document.getElementById('domain-input').value.trim() &&
        document.getElementById('email-input').value.trim() &&
        document.getElementById('password-input').value
    );
    document.getElementById('btn-convert').disabled = !(hasFile && signinOk);
}

async function runConversion() {
    if (!window.pywebview?.api) { showNotice('error', 'Error', 'Not running inside pywebview.'); return; }
    if (!currentFilePath)       { showNotice('error', 'No file selected', 'Please select an Excel file first.'); return; }

    const config = {
        file_path:   currentFilePath,
        sbol_version: parseInt(document.querySelector('input[name="sbol-version"]:checked').value),
        use_signin:  document.getElementById('chk-signin').checked,
        domain:      document.getElementById('domain-input').value.trim(),
        email:       document.getElementById('email-input').value.trim(),
        password:    document.getElementById('password-input').value,
    };

    setConvStatus('Starting...');
    document.getElementById('progress-section').classList.remove('hidden');
    const btn = document.getElementById('btn-convert');
    btn.disabled = true;
    btn.textContent = 'Converting...';

    try {
        await window.pywebview.api.run_conversion(JSON.stringify(config));
        startConvPolling();
    } catch (e) {
        setConvStatus('Error: ' + e);
        resetConvertButton();
    }
}

function startConvPolling() {
    if (pollingTimer) clearInterval(pollingTimer);
    pollingTimer = setInterval(async () => {
        try {
            const data = JSON.parse(await window.pywebview.api.get_progress());
            setConvStatus(data.message);
            if (data.finished) {
                clearInterval(pollingTimer);
                pollingTimer = null;
                document.getElementById('progress-section').classList.add('hidden');
                resetConvertButton();
                if (data.success) showNotice('success', 'Conversion complete', data.message);
                else              showNotice('error', 'Conversion failed', data.message);
            }
        } catch (e) { console.error('[conv poll]', e); }
    }, 500);
}

function setConvStatus(msg) {
    document.getElementById('status-text').textContent = msg;
}

function resetConvertButton() {
    const btn = document.getElementById('btn-convert');
    btn.textContent = 'Convert';
    updateConvertButton();
}

/* ============================================
   SPREADSHEET CREATOR — STATE
   ============================================ */

let scCustomSheets  = [];  // [{name, columns:[{header,sbolTerm,type,...}]}]
let seEditingIndex  = null; // index into scCustomSheets when editing; null = new

const SC_TYPE_LABELS = {
    resources:    'Parts Library',
    strains:      'Strains',
    sample_design:'Sample Design',
    study:        'Study',
    custom:       'Custom',
};

// Steps per template type (step 2 = Parts, for resources and custom)
const SC_STEPS = {
    resources:    [1, 2, 3, 4],
    strains:      [1, 3, 4],
    sample_design:[1, 3, 4],
    study:        [1, 3, 4],
    custom:       [1, 2, 3, 4],
};

let scStep        = 1;
let scType        = null;  // "resources"|"strains"|"sample_design"|"study"
let scOutputFolder = null;
let scPollTimer   = null;
let scSheetOrder  = [];    // F19: ordered sheet names = workbook tab order
let scSheetDisplay = {};   // F19: built-in sheet name -> display name

/* ============================================
   SPREADSHEET CREATOR — INIT
   ============================================ */

function initSpreadsheetCreator() {
    // Type cards
    document.querySelectorAll('.sc-type-card').forEach(card => {
        card.addEventListener('click', () => onTypeCardClick(card));
    });

    // Catalog is loaded per-type when step 2 is entered (see scGoToStep)

    // Select / Deselect all
    document.getElementById('sc-btn-select-all').addEventListener('click', () => {
        document.querySelectorAll('.sc-part-chk').forEach(chk => {
            chk.checked = true;
            syncPartItem(chk.closest('.sc-part-item'), chk);
        });
        validatePartsStep();
    });
    document.getElementById('sc-btn-deselect-all').addEventListener('click', () => {
        document.querySelectorAll('.sc-part-chk').forEach(chk => {
            chk.checked = false;
            syncPartItem(chk.closest('.sc-part-item'), chk);
        });
        validatePartsStep();
    });

    // Library name → live filename preview + re-validate so Next enables/disables
    document.getElementById('sc-library-name').addEventListener('input', () => {
        updatePreview();
        scValidateCurrentStep(true);
    });

    // Custom sheet editor
    document.getElementById('sc-add-sheet-btn').addEventListener('click', () => openSheetEditor(null));
    document.getElementById('se-close-btn').addEventListener('click', closeSheetEditor);
    document.getElementById('se-cancel-btn').addEventListener('click', closeSheetEditor);
    document.getElementById('se-save-btn').addEventListener('click', saveSheetEditor);
    document.getElementById('se-add-col-btn').addEventListener('click', () => addColumnRow());
    initColDragDrop(document.getElementById('se-col-list'));
    initSheetOrderDragDrop(document.getElementById('sc-order-list'));  // F19

    // Advanced toggle
    document.getElementById('sc-advanced-toggle').addEventListener('click', () => {
        const fields = document.getElementById('sc-advanced-fields');
        const arrow  = document.getElementById('sc-advanced-arrow');
        const hidden = fields.classList.toggle('hidden');
        arrow.classList.toggle('open', !hidden);
    });

    // Output folder
    document.getElementById('sc-btn-folder').addEventListener('click', pickOutputFolder);

    // Navigation
    document.getElementById('sc-btn-back').addEventListener('click', scBack);
    document.getElementById('sc-btn-next').addEventListener('click', scNext);

    // Set today's date as default

    scGoToStep(1);
}

/* ============================================
   SPREADSHEET CREATOR — CATALOG LOAD
   ============================================ */

async function loadSheetCatalog(templateType) {
    if (!window.pywebview?.api) return;
    try {
        const raw    = await window.pywebview.api.get_sheet_catalog(templateType || 'resources');
        const groups = JSON.parse(raw);
        buildPartCheckboxes(groups);
    } catch (e) {
        console.error('[loadSheetCatalog]', e);
    }
}

function buildPartCheckboxes(groups) {
    const container = document.getElementById('sc-parts-container');
    container.innerHTML = '';

    groups.forEach(({ group, sheets }) => {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'sc-parts-group';

        const heading = document.createElement('div');
        heading.className = 'sc-parts-group-title';
        heading.textContent = group;
        groupDiv.appendChild(heading);

        const grid = document.createElement('div');
        grid.className = 'sc-parts-grid';

        sheets.forEach(sheet => {
            scSheetDisplay[sheet.name] = sheet.display_name;  // F19
            const label = document.createElement('label');
            label.className = 'sc-part-item' + (sheet.default_checked ? ' checked' : '');
            label.dataset.defaultChecked = sheet.default_checked ? 'true' : 'false';

            const chk = document.createElement('input');
            chk.type      = 'checkbox';
            chk.className = 'sc-part-chk';
            chk.value     = sheet.name;
            chk.checked   = sheet.default_checked;

            const nameSpan = document.createElement('span');
            nameSpan.className   = 'sc-part-name';
            nameSpan.textContent = sheet.display_name;

            label.appendChild(chk);
            label.appendChild(nameSpan);

            if (sheet.hint) {
                const hint = document.createElement('span');
                hint.className   = 'sc-part-hint';
                hint.textContent = sheet.hint;
                label.appendChild(hint);
            }

            label.addEventListener('click', (e) => {
                e.preventDefault();
                chk.checked = !chk.checked;
                syncPartItem(label, chk);
                validatePartsStep();
            });

            grid.appendChild(label);
        });

        groupDiv.appendChild(grid);

        container.appendChild(groupDiv);
    });

    validatePartsStep();
}

/* ============================================
   SPREADSHEET CREATOR — STEP NAV
   ============================================ */

function scNext() {
    if (!scValidateCurrentStep()) return;

    const steps = scType ? SC_STEPS[scType] : [1, 2, 3, 4];
    const idx   = steps.indexOf(scStep);
    if (idx < steps.length - 1) {
        scGoToStep(steps[idx + 1]);
    } else {
        runGeneration();
    }
}

function scBack() {
    const steps = scType ? SC_STEPS[scType] : [1, 2, 3, 4];
    const idx   = steps.indexOf(scStep);
    if (idx > 0) scGoToStep(steps[idx - 1]);
}

function scGoToStep(n) {
    scStep = n;

    // Show/hide panels
    [1, 2, 3, 4].forEach(i => {
        const panel = document.getElementById(`sc-panel-${i}`);
        if (panel) panel.classList.toggle('hidden', i !== n);
    });

    // Update stepper
    updateStepIndicator();

    // Update nav buttons
    const steps = scType ? SC_STEPS[scType] : [1, 2, 3, 4];
    const idx   = steps.indexOf(n);

    const backBtn = document.getElementById('sc-btn-back');
    const nextBtn = document.getElementById('sc-btn-next');

    backBtn.style.visibility = idx === 0 ? 'hidden' : 'visible';

    const isLast = idx === steps.length - 1;
    nextBtn.textContent = isLast ? 'Create Spreadsheet' : 'Next →';

    // Validate to set enabled state
    scValidateCurrentStep(true);

    // Load catalog when entering step 2 (type-specific)
    if (n === 2) {
        const title = document.getElementById('sc-panel-2-title');
        if (title) title.textContent = scType === 'custom'
            ? 'Which sheets do you need?'
            : 'Which part types do you need?';
        loadSheetCatalog(scType);
    }

    // Update preview on step 4
    if (n === 4) updatePreview();
}

function updateStepIndicator() {
    const steps = scType ? SC_STEPS[scType] : [1, 2, 3, 4];

    [1, 2, 3, 4].forEach(i => {
        const node = document.getElementById(`sc-node-${i}`);
        if (!node) return;

        const included = steps.includes(i);
        const isCurrent   = i === scStep;
        const isCompleted = steps.indexOf(i) < steps.indexOf(scStep);

        node.classList.remove('active', 'completed', 'skipped');
        if (!included) {
            node.classList.add('skipped');
        } else if (isCurrent) {
            node.classList.add('active');
        } else if (isCompleted) {
            node.classList.add('completed');
        }
    });

    // Lines
    [[1, 2, 'sc-line-12'], [2, 3, 'sc-line-23'], [3, 4, 'sc-line-34']].forEach(([a, b, id]) => {
        const line  = document.getElementById(id);
        if (!line) return;
        const stepsA = scType ? SC_STEPS[scType] : [1, 2, 3, 4];
        const aCompleted = stepsA.indexOf(a) < stepsA.indexOf(scStep);
        line.classList.toggle('completed', aCompleted);
    });
}

/* ============================================
   SPREADSHEET CREATOR — VALIDATION
   ============================================ */

function scValidateCurrentStep(silent = false) {
    const nextBtn = document.getElementById('sc-btn-next');
    let valid = false;

    if (scStep === 1) {
        valid = scType !== null;
        nextBtn.disabled = !valid;
        return valid;
    }

    if (scStep === 2) {
        const anyChecked = [...document.querySelectorAll('.sc-part-chk')].some(c => c.checked);
        valid = anyChecked || scCustomSheets.length > 0;
        if (!silent) {
            document.getElementById('sc-no-parts-warning').classList.toggle('hidden', valid);
        }
        nextBtn.disabled = !valid;
        return valid;
    }

    if (scStep === 3) {
        const name = document.getElementById('sc-library-name').value.trim();
        valid = name.length > 0;
        if (!silent) {
            document.getElementById('sc-name-warning').classList.toggle('hidden', valid);
        }
        nextBtn.disabled = !valid;
        return valid;
    }

    if (scStep === 4) {
        valid = !!scOutputFolder;
        if (!silent) {
            document.getElementById('sc-folder-warning').classList.toggle('hidden', valid);
        }
        nextBtn.disabled = !valid;
        return valid;
    }

    return true;
}

/* ============================================
   SPREADSHEET CREATOR — TYPE SELECTION
   ============================================ */

function onTypeCardClick(card) {
    document.querySelectorAll('.sc-type-card').forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    scType = card.dataset.type;

    // Show/hide Parts step node based on type
    const node2 = document.getElementById('sc-node-2');
    node2.classList.toggle('skipped', scType !== 'resources' && scType !== 'custom');

    scValidateCurrentStep(true);
    updateStepIndicator();
}

/* ============================================
   SPREADSHEET CREATOR — PARTS
   ============================================ */

function syncPartItem(label, chk) {
    label.classList.toggle('checked', chk.checked);
}

function validatePartsStep() {
    const anyChecked = [...document.querySelectorAll('.sc-part-chk')].some(c => c.checked);
    const valid = anyChecked || scCustomSheets.length > 0;
    document.getElementById('sc-no-parts-warning').classList.toggle('hidden', valid);
    document.getElementById('sc-btn-next').disabled = !valid;
    renderDependencyWarnings();
    syncSheetOrder();
}

/* F19: keep the sheet-order list in sync with the current selection (checked
   built-in sheets + custom sheets), then render it. The list's order is the
   workbook tab order sent to the generator. */
function _selectedSheetNames() {
    const names = [...document.querySelectorAll('.sc-part-chk')]
        .filter(c => c.checked).map(c => c.value);
    scCustomSheets.forEach(s => {
        const n = (s.name || '').trim();
        if (n) names.push(n);
    });
    return names;
}

function _sheetDisplay(name) {
    return scSheetDisplay[name] || name;
}

function syncSheetOrder() {
    const selected = _selectedSheetNames();
    const sel = new Set(selected);
    // drop deselected, keep existing order
    scSheetOrder = scSheetOrder.filter(n => sel.has(n));
    // append newly-selected (in discovery order); user can then drag
    selected.forEach(n => { if (!scSheetOrder.includes(n)) scSheetOrder.push(n); });
    renderSheetOrderList();
}

function renderSheetOrderList() {
    const section = document.getElementById('sc-order-section');
    const list = document.getElementById('sc-order-list');
    if (!section || !list) return;
    list.innerHTML = '';
    // only worth showing once there is more than one tab to arrange
    section.classList.toggle('hidden', scSheetOrder.length < 2);
    scSheetOrder.forEach(name => {
        const row = document.createElement('div');
        row.className = 'sc-order-item';
        row.draggable = true;
        row.dataset.name = name;
        row.innerHTML = '<span class="sc-order-handle" title="Drag to reorder">⠿</span>'
                      + '<span class="sc-order-name"></span>';
        row.querySelector('.sc-order-name').textContent = _sheetDisplay(name);
        list.appendChild(row);
    });
}

/* F6: non-blocking dependency advisories. Each key is a sheet that references
   other local objects; `anyOf` lists sheets that would satisfy that reference.
   These never block "Next" — they just flag combinations that won't fully
   resolve at conversion (the references use Object_ID lookups into the same
   workbook). */
const SC_DEPENDENCIES = {
    cds:             { anyOf: ['protein'],       msg: 'CDS "Encodes for" references a Protein.' },
    ncrna:           { anyOf: ['rna'],           msg: 'ncRNA "Encodes for" references an RNA.' },
    complex:         { anyOf: ['protein', 'cds'],msg: 'Complex "Components IDs" reference other parts (e.g. Protein or CDS).' },
    'sample design': { anyOf: ['supplement'],    msg: 'Sample Design "Supplements" reference the Supplement sheet.' },
};

function computeDependencyWarnings() {
    const selected = new Set(
        [...document.querySelectorAll('.sc-part-chk')].filter(c => c.checked).map(c => c.value)
    );
    scCustomSheets.forEach(s => selected.add((s.name || '').trim().toLowerCase()));

    const warnings = [];
    selected.forEach(name => {
        const dep = SC_DEPENDENCIES[name];
        if (!dep) return;
        if (!dep.anyOf.some(req => selected.has(req))) {
            warnings.push(`"${name}" is selected without ${dep.anyOf.join(' or ')}. ${dep.msg}`);
        }
    });
    return warnings;
}

function renderDependencyWarnings() {
    const el = document.getElementById('sc-dep-warning');
    if (!el) return;
    const warnings = computeDependencyWarnings();
    if (warnings.length === 0) {
        el.classList.add('hidden');
        el.textContent = '';
        return;
    }
    el.classList.remove('hidden');
    el.innerHTML = warnings.map(w => '⚠ ' + escHtml(w)).join('<br>');
}

/* ============================================
   SPREADSHEET CREATOR — OUTPUT FOLDER
   ============================================ */

async function pickOutputFolder() {
    if (!window.pywebview?.api) return;
    try {
        const folder = await window.pywebview.api.pick_folder();
        if (folder) {
            scOutputFolder = folder;
            document.getElementById('sc-output-folder').value = folder;
            document.getElementById('sc-folder-warning').classList.add('hidden');
            document.getElementById('sc-btn-next').disabled = false;
            updatePreview();
        }
    } catch (e) {
        console.error('[pickOutputFolder]', e);
    }
}

/* ============================================
   SPREADSHEET CREATOR — PREVIEW
   ============================================ */

function updatePreview() {
    const libName = document.getElementById('sc-library-name').value.trim() || 'MyLibrary';
    const safeName = libName.replace(/[^\w\s\-]/g, '').trim().replace(/\s+/g, '_') || 'MyLibrary';
    const typeLabel = {
        resources: 'Resources', strains: 'Strains',
        sample_design: 'SampleDesign', study: 'Study', custom: 'Custom'
    }[scType] || '—';

    document.getElementById('sc-preview-filename').textContent =
        scType ? `${safeName}_${typeLabel}.xlsm` : '—';
    document.getElementById('sc-preview-type').textContent =
        scType ? SC_TYPE_LABELS[scType] : '—';

    const partsRow = document.getElementById('sc-preview-parts-row');
    if (scType === 'resources' || scType === 'custom') {
        partsRow.style.display = '';
        const selected = [...document.querySelectorAll('.sc-part-chk')]
            .filter(c => c.checked).map(c => c.value);
        const customLabel = scCustomSheets.length
            ? ` + ${scCustomSheets.length} custom`
            : '';
        document.getElementById('sc-preview-parts').textContent =
            (selected.length ? selected.join(', ') : '') + customLabel || '—';
    } else {
        partsRow.style.display = 'none';
    }
}

/* ============================================
   SPREADSHEET CREATOR — GENERATE
   ============================================ */

async function runGeneration() {
    if (!window.pywebview?.api) { showNotice('error', 'Error', 'Not running inside pywebview.'); return; }
    if (!scOutputFolder) {
        document.getElementById('sc-folder-warning').classList.remove('hidden');
        return;
    }

    const selectedParts = [...document.querySelectorAll('.sc-part-chk')]
        .filter(c => c.checked).map(c => c.value);

    const sbolVersion = parseInt(
        document.querySelector('input[name="sc-sbol-version"]:checked').value
    );

    const config = {
        template_type:  scType,
        selected_parts: selectedParts,
        custom_sheets:  scCustomSheets,
        sheet_order:    scSheetOrder,   // F19: workbook tab order
        output_folder:  scOutputFolder,
        metadata: {
            library_name:      document.getElementById('sc-library-name').value.trim(),
            collection_id:     document.getElementById('sc-collection-id').value.trim(),
            version:           document.getElementById('sc-version').value.trim() || '1',
            author:            document.getElementById('sc-author').value.trim(),
            email:             document.getElementById('sc-email').value.trim(),
            lab:               document.getElementById('sc-lab').value.trim(),
            institution:       document.getElementById('sc-institution').value.trim(),
            description:       document.getElementById('sc-description').value.trim(),
            pubmed_id:         document.getElementById('sc-pubmed').value.trim(),
            sbol_version:      sbolVersion,
            domain:            document.getElementById('sc-domain').value.trim(),
            master_collection: document.getElementById('sc-master-collection').value.trim(),
        },
    };

    // Show progress
    const progressSection = document.getElementById('sc-progress-section');
    progressSection.classList.remove('hidden');
    document.getElementById('sc-status-text').textContent = 'Generating...';

    const nextBtn = document.getElementById('sc-btn-next');
    const backBtn = document.getElementById('sc-btn-back');
    nextBtn.disabled = true;
    backBtn.style.visibility = 'hidden';

    try {
        await window.pywebview.api.generate_spreadsheet(JSON.stringify(config));
        startScPolling(progressSection, nextBtn, backBtn);
    } catch (e) {
        progressSection.classList.add('hidden');
        backBtn.style.visibility = 'visible';
        nextBtn.disabled = false;
        showNotice('error', 'Generation error', String(e));
    }
}

function startScPolling(progressSection, nextBtn, backBtn) {
    if (scPollTimer) clearInterval(scPollTimer);
    scPollTimer = setInterval(async () => {
        try {
            const data = JSON.parse(await window.pywebview.api.get_sc_progress());
            document.getElementById('sc-status-text').textContent = data.message;

            if (data.finished) {
                clearInterval(scPollTimer);
                scPollTimer = null;
                progressSection.classList.add('hidden');

                if (data.success) {
                    showNotice('success', 'Spreadsheet created', data.message);
                    resetSpreadsheetCreator();
                } else {
                    showNotice('error', 'Generation failed', data.message);
                    backBtn.style.visibility = 'visible';
                    nextBtn.disabled = false;
                    nextBtn.textContent = 'Create Spreadsheet';
                }
            }
        } catch (e) {
            console.error('[sc poll]', e);
        }
    }, 600);
}

/* ============================================
   SPREADSHEET CREATOR — RESET
   ============================================ */

/* ============================================
   SHEET EDITOR MODAL (UI-8 / UI-9)
   ============================================ */

function openSheetEditor(editIndex) {
    seEditingIndex = editIndex;
    const isEdit   = editIndex !== null;

    document.getElementById('se-modal-title').textContent =
        isEdit ? 'Edit Sheet' : 'Add Custom Sheet';
    document.getElementById('se-name-warning').classList.add('hidden');

    const nameInput = document.getElementById('se-sheet-name');
    const colList   = document.getElementById('se-col-list');
    colList.innerHTML = '';

    if (isEdit) {
        const sheet = scCustomSheets[editIndex];
        nameInput.value = sheet.name;
        sheet.columns.forEach(col => addColumnRow(col));
    } else {
        nameInput.value = '';
    }

    syncColEmpty();
    document.getElementById('se-overlay').classList.remove('hidden');
    nameInput.focus();
}

function closeSheetEditor() {
    document.getElementById('se-overlay').classList.add('hidden');
    seEditingIndex = null;
}

function saveSheetEditor() {
    const name = document.getElementById('se-sheet-name').value.trim();
    if (!name) {
        document.getElementById('se-name-warning').classList.remove('hidden');
        document.getElementById('se-sheet-name').focus();
        return;
    }
    document.getElementById('se-name-warning').classList.add('hidden');

    const columns = collectColumnRows();
    const entry   = { name, columns };

    if (seEditingIndex !== null) {
        scCustomSheets[seEditingIndex] = entry;
    } else {
        scCustomSheets.push(entry);
    }

    closeSheetEditor();
    refreshCustomSheetsList();
    validatePartsStep();
    updatePreview();
}

function collectColumnRows() {
    return [...document.querySelectorAll('#se-col-list .se-col-row')].map(row => {
        const type = row.querySelector('.se-col-type').value;
        const col  = {
            header:   row.querySelector('.se-col-header').value.trim(),
            sbolTerm: row.querySelector('.se-col-term').value.trim(),
            type,
        };
        if (type === 'tyto') {
            col.ontoName = row.querySelector('.se-onto-name')?.value.trim() || '';
        } else if (type === 'sheet') {
            col.lookupSheet  = row.querySelector('.se-lookup-sheet')?.value.trim() || '';
            col.fromCol      = row.querySelector('.se-from-col')?.value.trim() || 'A';
            col.toCol        = row.querySelector('.se-to-col')?.value.trim() || 'B';
            col.replacement  = row.querySelector('.se-replacement')?.checked || false;
        } else if (type === 'objectid') {
            col.parentLookup = row.querySelector('.se-parent-lookup')?.checked || false;
        }
        return col;
    });
}

function addColumnRow(data = null) {
    const colList = document.getElementById('se-col-list');

    const row = document.createElement('div');
    row.className   = 'se-col-row';
    row.draggable   = true;

    row.innerHTML = `
        <span class="se-drag-handle" title="Drag to reorder">⠿</span>
        <div class="se-col-fields">
            <div class="se-col-top">
                <input type="text" class="se-col-header" placeholder="Column header"
                       value="${escHtml(data?.header || '')}">
                <input type="text" class="se-col-term" list="se-sbol-terms"
                       placeholder="SBOL term" value="${escHtml(data?.sbolTerm || '')}">
                <select class="se-col-type">
                    <option value="plain">Plain</option>
                    <option value="tyto">Tyto lookup</option>
                    <option value="sheet">Sheet lookup</option>
                    <option value="objectid">Object ID lookup</option>
                </select>
            </div>
            <div class="se-col-subfields hidden"></div>
        </div>
        <button class="se-col-remove" type="button" title="Remove">✕</button>`;

    const typeSelect = row.querySelector('.se-col-type');
    if (data?.type) typeSelect.value = data.type;

    typeSelect.addEventListener('change', () =>
        updateColumnSubfields(row, typeSelect.value, null));
    updateColumnSubfields(row, typeSelect.value, data);

    row.querySelector('.se-col-remove').addEventListener('click', () => {
        row.remove();
        syncColEmpty();
    });

    colList.appendChild(row);
    syncColEmpty();
}

function updateColumnSubfields(row, type, data) {
    const sub = row.querySelector('.se-col-subfields');
    sub.innerHTML = '';

    if (type === 'tyto') {
        sub.innerHTML = `
            <div class="se-sub-row">
                <span class="se-sub-label">Ontology</span>
                <input type="text" class="se-onto-name" placeholder="e.g. SO, GO, SBO"
                       value="${escHtml(data?.ontoName || '')}">
            </div>`;
    } else if (type === 'sheet') {
        sub.innerHTML = `
            <div class="se-sub-row">
                <span class="se-sub-label">Lookup sheet</span>
                <input type="text" class="se-lookup-sheet" placeholder="Sheet name"
                       value="${escHtml(data?.lookupSheet || '')}">
            </div>
            <div class="se-sub-row">
                <span class="se-sub-label">From col</span>
                <input type="text" class="se-from-col" placeholder="A"
                       style="width:60px" value="${escHtml(data?.fromCol || 'A')}">
                <span class="se-sub-label" style="margin-left:10px">To col</span>
                <input type="text" class="se-to-col" placeholder="B"
                       style="width:60px" value="${escHtml(data?.toCol || 'B')}">
            </div>
            <label class="se-sub-toggle">
                <input type="checkbox" class="se-replacement" ${data?.replacement ? 'checked' : ''}>
                Replacement lookup
            </label>`;
    } else if (type === 'objectid') {
        sub.innerHTML = `
            <label class="se-sub-toggle">
                <input type="checkbox" class="se-parent-lookup" ${data?.parentLookup ? 'checked' : ''}>
                Parent lookup
            </label>`;
    }

    sub.classList.toggle('hidden', type === 'plain');
}

function syncColEmpty() {
    const colList = document.getElementById('se-col-list');
    const empty   = document.getElementById('se-col-empty');
    empty.classList.toggle('hidden', colList.children.length > 0);
}

function refreshCustomSheetsList() {
    const list = document.getElementById('sc-custom-sheets-list');
    list.innerHTML = '';

    scCustomSheets.forEach((sheet, idx) => {
        const colSummary = sheet.columns.length
            ? sheet.columns.map(c => c.header || '?').join(', ')
            : 'no columns';

        const row = document.createElement('div');
        row.className = 'sc-custom-sheet-row';
        row.innerHTML = `
            <div class="sc-custom-sheet-info">
                <div class="sc-custom-sheet-name">${escHtml(sheet.name)}</div>
                <div class="sc-custom-sheet-cols">${escHtml(colSummary)}</div>
            </div>
            <div class="sc-custom-sheet-actions">
                <button class="sc-custom-action-btn" data-action="edit" data-idx="${idx}">Edit</button>
                <button class="sc-custom-action-btn remove" data-action="remove" data-idx="${idx}">✕</button>
            </div>`;
        list.appendChild(row);
    });

    list.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.dataset.idx, 10);
            if (btn.dataset.action === 'edit') {
                openSheetEditor(idx);
            } else {
                scCustomSheets.splice(idx, 1);
                refreshCustomSheetsList();
                validatePartsStep();
                updatePreview();
            }
        });
    });
}

/* --- Drag-and-drop for column rows --------- */

let _dragSrc = null;

function initColDragDrop(colList) {
    colList.addEventListener('dragstart', e => {
        const row = e.target.closest('.se-col-row');
        if (!row) return;
        _dragSrc = row;
        row.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    });

    colList.addEventListener('dragend', () => {
        if (_dragSrc) _dragSrc.classList.remove('dragging');
        colList.querySelectorAll('.se-col-row').forEach(r =>
            r.classList.remove('drag-over'));
        _dragSrc = null;
    });

    colList.addEventListener('dragover', e => {
        e.preventDefault();
        const row = e.target.closest('.se-col-row');
        if (!row || row === _dragSrc) return;
        colList.querySelectorAll('.se-col-row').forEach(r =>
            r.classList.remove('drag-over'));
        row.classList.add('drag-over');
        const rect  = row.getBoundingClientRect();
        const after = e.clientY > rect.top + rect.height / 2;
        colList.insertBefore(_dragSrc, after ? row.nextSibling : row);
    });

    colList.addEventListener('drop', e => {
        e.preventDefault();
    });
}

/* F19: drag-to-reorder for the sheet-order list (mirrors initColDragDrop).
   On drop the workbook tab order (scSheetOrder) is rebuilt from the DOM. */
function initSheetOrderDragDrop(list) {
    if (!list) return;
    let src = null;
    list.addEventListener('dragstart', e => {
        const row = e.target.closest('.sc-order-item');
        if (!row) return;
        src = row;
        row.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    });
    list.addEventListener('dragend', () => {
        if (src) src.classList.remove('dragging');
        list.querySelectorAll('.sc-order-item').forEach(r => r.classList.remove('drag-over'));
        src = null;
        scSheetOrder = [...list.querySelectorAll('.sc-order-item')].map(r => r.dataset.name);
    });
    list.addEventListener('dragover', e => {
        e.preventDefault();
        const row = e.target.closest('.sc-order-item');
        if (!row || row === src) return;
        list.querySelectorAll('.sc-order-item').forEach(r => r.classList.remove('drag-over'));
        row.classList.add('drag-over');
        const rect  = row.getBoundingClientRect();
        const after = e.clientY > rect.top + rect.height / 2;
        list.insertBefore(src, after ? row.nextSibling : row);
    });
    list.addEventListener('drop', e => e.preventDefault());
}

/* --- HTML escape helper -------------------- */

function escHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function resetSpreadsheetCreator() {
    scType         = null;
    scOutputFolder = null;
    scCustomSheets = [];
    scSheetOrder   = [];   // F19
    refreshCustomSheetsList();

    // Clear type selection
    document.querySelectorAll('.sc-type-card').forEach(c => c.classList.remove('selected'));

    // Reset parts to their catalog defaults
    document.querySelectorAll('.sc-part-item').forEach(label => {
        const chk = label.querySelector('input[type="checkbox"]');
        chk.checked = label.dataset.defaultChecked === 'true';
        syncPartItem(label, chk);
    });

    // Clear metadata fields
    ['sc-library-name','sc-collection-id','sc-author','sc-email','sc-lab',
     'sc-institution','sc-description','sc-pubmed','sc-domain',
     'sc-master-collection'].forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('sc-version').value = '1';   // keeps its default
    document.getElementById('sc-sbol-v2').checked = true;

    // Reset output folder
    document.getElementById('sc-output-folder').value = '';

    // Hide all warnings
    ['sc-no-parts-warning','sc-name-warning','sc-folder-warning'].forEach(id => {
        document.getElementById(id).classList.add('hidden');
    });

    // Close advanced if open
    document.getElementById('sc-advanced-fields').classList.add('hidden');
    document.getElementById('sc-advanced-arrow').classList.remove('open');

    scGoToStep(1);
}


/* ============================================
   NOTICE MODAL (error / success dialogs)
   Replaces native window.alert() so dialogs carry a
   semantic icon and match the app's design.
   ============================================ */

const NOTICE_ICONS = {
    error:   '<svg viewBox="0 0 24 24"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
    success: '<svg viewBox="0 0 24 24"><path d="M21.801 10A10 10 0 1 1 17 3.335"/><path d="m9 11 3 3L22 4"/></svg>',
};

function showNotice(type, title, message) {
    const overlay = document.getElementById('notice-overlay');
    if (!overlay) {  // fallback if markup is missing
        alert((title ? title + '\n\n' : '') + (message || ''));
        return;
    }
    const kind = type === 'success' ? 'success' : 'error';
    const icon = document.getElementById('notice-icon');
    icon.className = 'notice-icon ' + kind;
    icon.innerHTML = NOTICE_ICONS[kind];
    document.getElementById('notice-title').textContent = title || (kind === 'success' ? 'Success' : 'Error');
    document.getElementById('notice-message').textContent = message || '';
    overlay.classList.remove('closing');  // F17: clear any in-flight exit
    overlay.classList.remove('hidden');
    document.getElementById('notice-ok-btn').focus();
}

function hideNotice() {
    const overlay = document.getElementById('notice-overlay');
    if (!overlay || overlay.classList.contains('hidden')) return;
    // F17: play the exit animation, then hide. display:none cancels animations,
    // so add .closing first and only set .hidden once it finishes.
    const reduce = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { overlay.classList.add('hidden'); return; }
    overlay.classList.add('closing');
    let done = false;
    const finish = () => {
        if (done) return;
        done = true;
        overlay.classList.add('hidden');
        overlay.classList.remove('closing');
    };
    overlay.addEventListener('animationend', finish, { once: true });
    setTimeout(finish, 260);  // fallback if animationend does not fire
}

(function wireNotice() {
    const overlay = document.getElementById('notice-overlay');
    const okBtn = document.getElementById('notice-ok-btn');
    if (okBtn) okBtn.addEventListener('click', hideNotice);
    if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) hideNotice(); });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay && !overlay.classList.contains('hidden')) hideNotice();
    });
})();
