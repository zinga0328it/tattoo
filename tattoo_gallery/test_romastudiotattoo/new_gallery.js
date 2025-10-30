// Carica i dati dei tatuaggi dal JSON (generato dinamicamente)
let tattoosData = [];

async function loadTattoosData() {
    try {
        const response = await fetch('tattoos.json');
        if (response.ok) {
            tattoosData = await response.json();
            console.log(`Caricati ${tattoosData.length} tatuaggi dal database`);
        } else {
            console.warn('JSON non disponibile, uso fallback');
            tattoosData = [
                {filename: 'ale0328it_AgACAgQAAxkBAAM0aM3c1F3zbYvcf2QGgX5MNsxLLtYAApzIMRuFpHFS4zm6OJRGbIUBAAMCAAN5AAM2BA.jpg', description: 'Tatuaggio artistico', username: 'Anonimo', alt_text: 'Tatuaggio - Roma Studio Tattoo'},
                {filename: 'ale0328it_AgACAgQAAxkBAAM6aM3fcqVAax3ykcFmIU7WbfHR1dgAAp7IMRuFpHFSdT0Gfxz5j7YBAAMCAAN5AAM2BA.jpg', description: 'Tatuaggio tradizionale', username: 'Anonimo', alt_text: 'Tatuaggio - Roma Studio Tattoo'},
                {filename: 'ale0328it_AgACAgQAAxkBAAM8aM3kGLOYaLxQq-Lq2-11FyXIYQEAAqTIMRuFpHFSeaaLy96TlX8BAAMCAAN5AAM2BA.jpg', description: 'Tatuaggio moderno', username: 'Anonimo', alt_text: 'Tatuaggio - Roma Studio Tattoo'},
                {filename: 'ale0328it_AgACAgQAAxkBAAMuaM3bSqcX9oj4kq7Yd5rwWLLqcmAAApjIMRuFpHFSSvEAAWpBq5NKAQADAgADeQADNgQ.jpg', description: 'Tatuaggio geometrico', username: 'Anonimo', alt_text: 'Tatuaggio - Roma Studio Tattoo'},
                {filename: 'ale0328it_AgACAgQAAxkBAAMwaM3cVeI3-x-1AAGFvhR2cAcFGtjZAAKayDEbhaRxUuHq9XTmjhtXAQADAgADeQADNgQ.jpg', description: 'Tatuaggio realistico', username: 'Anonimo', alt_text: 'Tatuaggio - Roma Studio Tattoo'},
                {filename: 'ale0328it_AgACAgQAAxkBAAMyaM3cmNmPOqFGRFVVxbZcsIICabUAApvIMRuFpHFSFehbWH_yKh0BAAMCAAN5AAM2BA.jpg', description: 'Tatuaggio giapponese', username: 'Anonimo', alt_text: 'Tatuaggio - Roma Studio Tattoo'}
            ];
        }
    } catch (error) {
        console.error('Errore caricamento JSON:', error);
        tattoosData = [
            {filename: 'ale0328it_AgACAgQAAxkBAAM0aM3c1F3zbYvcf2QGgX5MNsxLLtYAApzIMRuFpHFS4zm6OJRGbIUBAAMCAAN5AAM2BA.jpg', description: 'Tatuaggio artistico', username: 'Anonimo', alt_text: 'Tatuaggio - Roma Studio Tattoo'}
        ];
    }
}

function loadImages() {
    tattoosData.forEach(tattoo => {
        const img = new Image();
        img.src = tattoo.image_url || `images/${tattoo.filename}`;
        img.onload = () => {
            img.alt = tattoo.alt_text || 'Tatuaggio';
            img.title = tattoo.description || 'Tatuaggio';
            img.style.width = '200px';
            img.style.height = '200px';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '10px';
            img.style.transition = 'opacity 1s ease-in-out';
            img.style.cursor = 'pointer';
            
            // Crea il container del tatuaggio
            const tattooItem = document.createElement('div');
            tattooItem.className = 'tattoo-item';
            
            // Aggiungi descrizione sotto l'immagine
            const descriptionDiv = document.createElement('div');
            descriptionDiv.className = 'tattoo-description';
            descriptionDiv.innerHTML = `<strong>${tattoo.username}</strong>: ${tattoo.description}`;
            descriptionDiv.style.fontSize = '12px';
            descriptionDiv.style.textAlign = 'center';
            descriptionDiv.style.marginTop = '5px';
            descriptionDiv.style.maxWidth = '200px';
            
            // Crea il container dei like
            const likeContainer = document.createElement('div');
            likeContainer.className = 'like-container';
            
            // Crea il pulsante like
            const likeButton = document.createElement('button');
            likeButton.className = 'like-button';
            likeButton.innerHTML = '❤️';
            likeButton.title = 'Mi piace';
            
            // Disabilita il pulsante se l'utente ha già messo like
            const fileName = tattoo.filename;
            if (hasUserLiked(fileName)) {
                likeButton.classList.add('disabled');
                likeButton.title = 'Hai già messo like';
            }
            
            // Crea il contatore dei like
            const likeCount = document.createElement('span');
            likeCount.className = 'like-count';
            likeCount.textContent = getLikes(fileName);
            
            // Gestisci il click sul pulsante like
            likeButton.addEventListener('click', (e) => {
                e.stopPropagation();
                
                if (hasUserLiked(fileName)) {
                    likeButton.style.transform = 'scale(1.2)';
                    setTimeout(() => likeButton.style.transform = 'scale(1)', 200);
                    return;
                }
                
                const currentLikes = addLike(fileName);
                likeCount.textContent = currentLikes;
                likeButton.classList.add('liked');
                likeButton.classList.add('disabled');
                likeButton.title = 'Hai già messo like';
                setTimeout(() => likeButton.classList.remove('liked'), 300);
            });
            
            // Gestisci il click sull'immagine (fade out)
            img.addEventListener('click', () => {
                img.classList.add('fade-out');
                setTimeout(() => {
                    tattooItem.remove();
                }, 1000);
            });
            
            // Assembla gli elementi
            likeContainer.appendChild(likeButton);
            likeContainer.appendChild(likeCount);
            tattooItem.appendChild(img);
            tattooItem.appendChild(descriptionDiv);
            tattooItem.appendChild(likeContainer);
            galleryContainer.appendChild(tattooItem);
        };
        img.onerror = () => {
            console.log(`Immagine non trovata: ${tattoo.filename}`);
        };
    });
}
