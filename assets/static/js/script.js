// Søgefunktion (opdaterer asset-listen live)
document.getElementById('search').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    fetch(`/api/assets/?search=${searchTerm}`)
        .then(response => response.json())
        .then(data => {
            const assetList = document.getElementById('asset-list');
            assetList.innerHTML = '';
            data.forEach(asset => {
                const item = document.createElement('div');
                item.className = 'asset-item';
                item.textContent = `${asset.VPID}: ${asset.name}`;
                item.addEventListener('click', () => {
                    document.getElementById('description').value =
                        `[${asset.VPID}] ${asset.name}: `;
                });
                assetList.appendChild(item);
            });
        });
});

// Scan QR-knap
document.getElementById('scan-btn').addEventListener('click', function() {
    // Simuler QR-scanning (erstat med ægte QR-scanner)
    const simulatedQR = prompt("Indtast QR-kode (simuleret):");
    if (simulatedQR) {
        fetch(`/api/assets/?search=${simulatedQR}`)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    document.getElementById('description').value =
                        `[${data[0].VPID}] ${data[0].name}: `;
                }
            });
});

// Kamera-knap
document.getElementById('camera-btn').addEventListener('click', function() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.capture = 'environment'; // Åbner kamera på mobil
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                document.getElementById('preview').src = event.target.result;
                document.getElementById('preview').classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });
    input.click();
});

// Indsend fejlrapport (med oversættelse til dansk)
document.getElementById('report-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const description = document.getElementById('description').value;
    const imageInput = document.getElementById('image');
    const formData = new FormData();

    // Oversæt til dansk hvis nødvendigt (placeholder - brug en ægte API)
    const translatedDesc = description; // Her skal du kalde en oversættelses-API

    formData.append('description', translatedDesc);
    if (imageInput.files[0]) {
        formData.append('image', imageInput.files[0]);
    }

    fetch('/api/reports/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert("Rapport indsendt!");
        document.getElementById('report-form').reset();
        document.getElementById('preview').classList.add('hidden');
    })
    .catch(error => {
        alert("Fejl: " + error);
    });
});
