document.addEventListener('DOMContentLoaded', function() {
    // --- Elementer ---
    const searchInput = document.getElementById('search');
    const assetList = document.getElementById('asset-list');
    const reportForm = document.getElementById('report-form');
    const preview = document.getElementById('preview');
    const selectedAssetLabel = document.getElementById('selected-asset-label');

    // --- Global state ---
    let selectedAssetVPID = null;

    // --- Oversættelser (matcher index.html) ---
    const translations = {
        da: {
            searchPlaceholder: "Søg efter aktiv eller scan QR...",
            noAssets: "Ingen aktiver fundet.",
            scanPrompt: "Indtast QR-kode (simuleret):",
            noAssetSelected: "Indtast venligst et aktiv (søg eller scan QR).",
            reportSuccess: "Rapport indsendt!",
            reportError: "Der opstod en fejl. Prøv igen.",
            fetchError: "Fejl ved hentning af data."
        }
    };

    // --- Hent og vis aktiver ---
    async function loadAssets(searchTerm = '') {
        try {
            const url = searchTerm
                ? `/api/assets/?search=${encodeURIComponent(searchTerm)}`
                : '/api/assets/';

            const response = await fetch(url);
            const assets = await response.json();

            if (assets.length > 0) {
                assetList.innerHTML = assets.map(asset =>
                    `<div class="asset-item" data-vpid="${asset.VPID}" onclick="selectAsset('${asset.VPID}', this)">
                        <strong>${asset.VPID}</strong> - ${asset.name}
                        ${asset.description ? `<div class="asset-description">${asset.description}</div>` : ''}
                    </div>`
                ).join('');
                assetList.classList.remove('hidden');
            } else {
                assetList.innerHTML = `<div class="asset-item">${translations.da.noAssets}</div>`;
                assetList.classList.remove('hidden');
            }
        } catch (error) {
            console.error("Fejl ved hentning af aktiver:", error);
            assetList.innerHTML = `<div class="asset-item">${translations.da.fetchError}</div>`;
            assetList.classList.remove('hidden');
        }
    }

    // --- Søgefunktion ---
    searchInput.addEventListener('input', async function(e) {
        const searchTerm = e.target.value.trim();
        if (searchTerm.length === 0) {
            assetList.innerHTML = `<div class="asset-item">${translations.da.searchPlaceholder}</div>`;
            assetList.classList.add('hidden');
            return;
        }
        await loadAssets(searchTerm);
    });

    // --- Vælg aktiv (tilføjet for konsistens med index.html) ---
    window.selectAsset = function(vpid, element) {
        document.querySelectorAll('.asset-item').forEach(el => el.classList.remove('selected'));
        element.classList.add('selected');
        selectedAssetVPID = vpid;
        searchInput.value = vpid;
        selectedAssetLabel.textContent = vpid;
    };

    // --- Nulstil søgefeltet ---
    function resetSearch() {
        searchInput.value = '';
        selectedAssetVPID = null;
        selectedAssetLabel.textContent = translations.da.noAssetSelected;
        loadAssets(); // Genindlæs alle aktiver
    }

    // --- Simuler QR-scanning ---
    document.getElementById('scan-btn').addEventListener('click', function() {
        const simulatedQR = prompt(translations.da.scanPrompt);
        if (simulatedQR) {
            searchInput.value = simulatedQR;
            searchInput.dispatchEvent(new Event('input'));
        }
    });

    // --- Kamera-funktionalitet ---
    document.getElementById('camera-btn').addEventListener('click', function() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.capture = 'environment';
        input.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    preview.src = event.target.result;
                    preview.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        };
        input.click();
    });

    // --- Indsend fejlrapport ---
    reportForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const description = document.getElementById('description').value;
        const vpid = selectedAssetVPID || searchInput.value.trim();
        const sprog = document.getElementById('sprog-input').value;

        if (!vpid) {
            alert(translations.da.noAssetSelected);
            return;
        }

        const imageData = preview.classList.contains('hidden') ? null : preview.src;

        try {
            const response = await fetch('/api/reports/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    VPID: vpid,
                    description: description,
                    image: imageData,
                    sprog: sprog
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                alert(`${translations.da.reportSuccess} (ID: ${data.report_id || ''})`);
                e.target.reset();
                preview.classList.add('hidden');
                resetSearch(); // NULSTIL SØGEFELTET
            } else {
                alert(`${translations.da.reportError}: ${data.message || ''}`);
            }
        } catch (error) {
            console.error("Fejl ved indsendelse:", error);
            alert(translations.da.reportError);
        }
    });

    // --- Indlæs alle aktiver ved start ---
    loadAssets();
});
