document.addEventListener('DOMContentLoaded', function() {
    // --- Søgefunktion ---
    const searchInput = document.getElementById('search');
    const assetList = document.getElementById('asset-list');

    // Hent og vis aktiver baseret på søgeterm
    searchInput.addEventListener('input', async function(e) {
        const searchTerm = e.target.value.trim();
        if (searchTerm.length === 0) {
            assetList.innerHTML = '<div class="asset-item">Indtast søgeord eller scan QR-kode...</div>';
            assetList.classList.add('hidden');
            return;
        }
        try {
            const response = await fetch(`/api/assets/?search=${encodeURIComponent(searchTerm)}`);
            const assets = await response.json();
            if (assets.length > 0) {
                assetList.innerHTML = assets.map(asset =>
                    `<div class="asset-item" data-vpid="${asset.VPID}">${asset.VPID}: ${asset.name}</div>`
                ).join('');
                assetList.classList.remove('hidden');
            } else {
                assetList.innerHTML = '<div class="asset-item">Ingen aktiver fundet.</div>';
                assetList.classList.remove('hidden');
            }
        } catch (error) {
            console.error("Fejl ved hentning af aktiver:", error);
            assetList.innerHTML = '<div class="asset-item">Fejl ved hentning af data.</div>';
            assetList.classList.remove('hidden');
        }
    });

    // --- Simuler QR-scanning ---
    document.getElementById('scan-btn').addEventListener('click', function() {
        const simulatedQR = prompt("Indtast QR-kode (simuleret):");
        if (simulatedQR) {
            searchInput.value = simulatedQR;
            searchInput.dispatchEvent(new Event('input')); // Trigger søgning
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
                    const preview = document.getElementById('preview');
                    preview.src = event.target.result;
                    preview.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        };
        input.click();
    });

    // --- Indsend fejlrapport (OPDATERET TIL AT BRUGE SKJULT INPUT-FELT) ---
    document.getElementById('report-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const description = document.getElementById('description').value;
        const preview = document.getElementById('preview');
        const vpid = searchInput.value.trim();

        if (!vpid) {
            alert("Indtast venligst et aktiv (søg eller scan QR).");
            return;
        }

        const imageData = preview.classList.contains('hidden') ? null : preview.src;
        const sprog = document.getElementById('sprog-input').value;  // Hent sprog fra skjult felt

        try {
            const response = await fetch('/api/reports/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    VPID: vpid,
                    description: description,
                    image: imageData,
                    sprog: sprog  // Send det valgte sprog
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                alert(`Rapport indsendt! (ID: ${data.report_id})`);
                e.target.reset();
                preview.classList.add('hidden');
            } else {
                alert(`Fejl: ${data.message}`);
            }
        } catch (error) {
            console.error("Fejl ved indsendelse:", error);
            alert("Der opstod en fejl. Prøv igen.");
        }
    });
});
