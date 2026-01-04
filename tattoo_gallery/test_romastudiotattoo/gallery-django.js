// GALLERY.JS AGGIORNATO PER SISTEMA DJANGO
// Sostituisce completamente il vecchio gallery.js

console.log('🚀 Gallery.js Django-powered caricato!');

// Configurazione API
const API_BASE = '/gallery/api';

// Cache per le API
let tattoosCache = null;
let lastUpdate = null;

// Carica tutti i tatuaggi (con cache)
async function loadTattoos(forceRefresh = false) {
    // Usa cache se disponibile e recente (< 5 minuti)
    if (!forceRefresh && tattoosCache && lastUpdate && 
        (Date.now() - lastUpdate) < 5 * 60 * 1000) {
        return tattoosCache;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tattoos/`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const tattoos = await response.json();
        
        // Aggiorna cache
        tattoosCache = tattoos;
        lastUpdate = Date.now();
        
        console.log(`✅ Caricati ${tattoos.length} tatuaggi dalla API Django`);
        return tattoos;
        
    } catch (error) {
        console.error('❌ Errore caricamento API Django:', error);
        
        // Fallback: prova a caricare dal JSON statico
        try {
            const fallbackResponse = await fetch('/tattoos.json');
            const fallbackData = await fallbackResponse.json();
            console.log('📦 Fallback: usando JSON statico');
            return fallbackData;
        } catch (fallbackError) {
            console.error('❌ Errore anche con fallback JSON:', fallbackError);
            throw new Error('Impossibile caricare i tatuaggi');
        }
    }
}

// Carica dettagli di un singolo tatuaggio
async function loadTattooDetail(tattooId) {
    try {
        const response = await fetch(`${API_BASE}/tattoo/${tattooId}/`);
        if (!response.ok) {
            throw new Error(`Tatuaggio ${tattooId} non trovato`);
        }
        
        const tattoo = await response.json();
        console.log(`✅ Dettagli caricati per tatuaggio ${tattooId}`);
        return tattoo;
        
    } catch (error) {
        console.error(`❌ Errore caricamento dettagli ${tattooId}:`, error);
        throw error;
    }
}

// Carica tatuaggi di un artista specifico
async function loadArtistTattoos(username) {
    try {
        const response = await fetch(`${API_BASE}/artist/${encodeURIComponent(username)}/`);
        if (!response.ok) {
            throw new Error(`Artista ${username} non trovato`);
        }
        
        const tattoos = await response.json();
        console.log(`✅ Caricati ${tattoos.length} tatuaggi per artista ${username}`);
        return tattoos;
        
    } catch (error) {
        console.error(`❌ Errore caricamento artista ${username}:`, error);
        throw error;
    }
}

// Crea elemento HTML per un tatuaggio (homepage)
function createTattooItem(tattoo, isHomepage = false) {
    const date = new Date(tattoo.uploaded_at).toLocaleDateString('it-IT');
    
    if (isHomepage) {
        return `
            <div class="gallery-item" onclick="openTattooDetail(${tattoo.id})">
                <img src="${tattoo.image_url}" alt="${tattoo.description}" loading="lazy">
                <div class="overlay">
                    <h3>${tattoo.description}</h3>
                    <p>👤 ${tattoo.username}</p>
                    <p>📅 ${date}</p>
                    <div class="cta">
                        <span>👆 Clicca per dettagli e contatto Telegram</span>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Formato per galleria completa
        return `
            <div class="tattoo-card" onclick="openTattooDetail(${tattoo.id})">
                <img src="${tattoo.image_url}" alt="${tattoo.description}" class="tattoo-image" loading="lazy">
                <div class="tattoo-info">
                    <div class="tattoo-description">${tattoo.description}</div>
                    <div class="tattoo-author">👤 ${tattoo.username}</div>
                    <div class="tattoo-date">📅 ${date}</div>
                    <a href="${tattoo.telegram_url}" class="telegram-link" onclick="event.stopPropagation()">
                        💬 Contatta ${tattoo.username}
                    </a>
                </div>
            </div>
        `;
    }
}

// Apre la pagina dettaglio
function openTattooDetail(tattooId) {
    window.location.href = `/detail.html?id=${tattooId}`;
}

// Filtra tatuaggi per ricerca
function filterTattoos(tattoos, searchTerm) {
    if (!searchTerm) return tattoos;
    
    const term = searchTerm.toLowerCase();
    return tattoos.filter(tattoo => 
        tattoo.description.toLowerCase().includes(term) ||
        tattoo.username.toLowerCase().includes(term)
    );
}

// Ordina tatuaggi
function sortTattoos(tattoos, sortBy = 'newest') {
    const sorted = [...tattoos];
    
    switch (sortBy) {
        case 'newest':
            return sorted.sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at));
        case 'oldest':
            return sorted.sort((a, b) => new Date(a.uploaded_at) - new Date(b.uploaded_at));
        case 'artist':
            return sorted.sort((a, b) => a.username.localeCompare(b.username));
        default:
            return sorted;
    }
}

// Funzioni di utilità per gestire errori
function showError(container, message) {
    if (typeof container === 'string') {
        container = document.getElementById(container);
    }
    
    if (container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 50px; color: #e74c3c; background: #ffeaea; border-radius: 10px;">
                ⚠️ ${message}
            </div>
        `;
    }
}

function showLoading(container, message = 'Caricamento...') {
    if (typeof container === 'string') {
        container = document.getElementById(container);
    }
    
    if (container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 50px; color: #666;">
                🎨 ${message}
            </div>
        `;
    }
}

// Debug: mostra stato della cache
function getCacheInfo() {
    return {
        hasCachedData: !!tattoosCache,
        cacheSize: tattoosCache ? tattoosCache.length : 0,
        lastUpdate: lastUpdate ? new Date(lastUpdate).toLocaleString('it-IT') : null,
        cacheAge: lastUpdate ? Math.round((Date.now() - lastUpdate) / 1000) : null
    };
}

// Esporta funzioni per debug globale
window.tattooGallery = {
    loadTattoos,
    loadTattooDetail,
    loadArtistTattoos,
    getCacheInfo,
    clearCache: () => {
        tattoosCache = null;
        lastUpdate = null;
        console.log('🗑️ Cache svuotata');
    }
};

console.log('✅ Gallery.js Django-powered pronto! Debug: window.tattooGallery');
