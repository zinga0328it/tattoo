// AGGIORNAMENTO GALLERY.JS PER LINK ALLE PAGINE DETTAGLIO
// Aggiorna il tuo gallery.js esistente con questa funzione

// Aggiungi questa funzione per gestire i click sulle immagini
function createGalleryItem(tattoo) {
    return `
        <div class="gallery-item" onclick="openTattooDetail(${tattoo.id})">
            <img src="${tattoo.image_url}" alt="${tattoo.description}" loading="lazy">
            <div class="overlay">
                <h3>${tattoo.description}</h3>
                <p>👤 ${tattoo.username}</p>
                <p>📅 ${new Date(tattoo.uploaded_at).toLocaleDateString('it-IT')}</p>
                <div class="cta">
                    <span>👆 Clicca per dettagli e contatto Telegram</span>
                </div>
            </div>
        </div>
    `;
}

// Funzione per aprire la pagina dettaglio
function openTattooDetail(tattooId) {
    window.location.href = `/detail.html?id=${tattooId}`;
}

// ISTRUZIONI PER L'AGGIORNAMENTO:
// 1. Apri il tuo gallery.js esistente
// 2. Sostituisci la funzione che crea gli elementi della galleria con createGalleryItem()
// 3. Aggiungi la funzione openTattooDetail()
// 4. Assicurati che ogni elemento della galleria abbia onclick="openTattooDetail(ID)"

console.log('🔗 Gallery.js aggiornato per collegamenti dettaglio!');
