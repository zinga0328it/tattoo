console.log("=== GALLERY SCRIPT v13 CON LIKE FIXED ===");

var galleryContainer;

document.addEventListener("DOMContentLoaded", function() {
    console.log("DOM loaded, inizializzazione galleria con like...");
    
    galleryContainer = document.getElementById("gallery-container");
    console.log("galleryContainer trovato:", galleryContainer);
    
    if (!galleryContainer) {
        console.error("ERRORE: gallery-container non trovato!");
        return;
    }
    
    loadTattoos();
});

function loadTattoos() {
    console.log("🔄 Caricamento dati inline...");
    
    if (window.tattoosData) {
        console.log("✅ Dati trovati inline:", window.tattoosData);
        displayTattoos(window.tattoosData);
    } else {
        console.log("⚠️ Dati non trovati, provo AJAX...");
        // Fallback AJAX
        fetch("https://www.romastudiotattoo.it/gallery/api/tattoos/")
            .then(response => response.json())
            .then(data => displayTattoos(data))
            .catch(error => {
                console.error("❌ Errore AJAX:", error);
                displayFallback();
            });
    }
}

// Vecchio loadTattoos commentato
/*
function old_loadTattoos() {
    console.log("🔄 Caricamento API Django...");
    
    fetch("https://www.romastudiotattoo.it/gallery/api/tattoos/")
        .then(function(response) {
            console.log("Response status:", response.status);
            if (!response.ok) {
                throw new Error("HTTP error! status: " + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            console.log("✅ JSON caricato:", data);
            displayTattoos(data);
        })
        .catch(function(error) {
            console.error("❌ Errore caricamento JSON:", error);
            displayFallback();
        });
}
*/

function displayTattoos(tattoos) {
    console.log("🖼️ Visualizzazione", tattoos.length, "tatuaggi con like");
    
    if (!tattoos || tattoos.length === 0) {
        displayFallback();
        return;
    }
    
    galleryContainer.innerHTML = "";
    
    for (var i = 0; i < tattoos.length; i++) {
        var tattoo = tattoos[i];
        console.log("Creando elemento per:", tattoo.filename);
        
        createTattooCard(tattoo);
    }
    
    console.log("✅ Galleria popolata con", tattoos.length, "elementi + like");
}

function createTattooCard(tattoo) {
    // Container principale
    var item = document.createElement("div");
    item.className = "tattoo-item";
    item.style.cssText = "margin: 15px; padding: 25px; border: none; border-radius: 20px; text-align: center; background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%); box-shadow: 0 8px 25px rgba(0,0,0,0.15); transition: all 0.3s ease; position: relative; overflow: hidden; border: 1px solid rgba(0,0,0,0.05);";
    
    // Immagine
    var img = document.createElement("img");
    img.src = "images/" + tattoo.filename;
    img.alt = tattoo.description;
    img.style.cssText = "width: 200px; height: 200px; object-fit: cover; border-radius: 10px; cursor: pointer; margin-bottom: 15px; transition: transform 0.3s ease;";
    
    img.onload = function() {
        console.log("✅ Immagine caricata:", this.src);
    };
    
    img.onerror = function() {
        console.error("❌ Errore caricamento:", this.src);
        this.style.background = "#ffebee";
        this.style.border = "2px solid red";
        this.alt = "❌ Immagine non disponibile";
    };
    
    img.onclick = function() {
        openTattooDetail(tattoo.id);
    };
    
    // Descrizione
    var desc = document.createElement("p");
    desc.textContent = tattoo.description;
    desc.style.cssText = "margin: 15px 0; fontSize: 16px; fontWeight: bold; color: #333; lineHeight: 1.4;";

    // Username
    var username = document.createElement("p");
    username.textContent = "👤 " + tattoo.username;
    username.style.cssText = "margin: 10px 0; fontSize: 14px; color: #666; fontStyle: italic;";

    // Data di caricamento
    var uploadDate = document.createElement("p");
    var date = new Date(tattoo.uploaded_at);
    uploadDate.textContent = "📅 " + date.toLocaleDateString("it-IT");
    uploadDate.style.cssText = "margin: 10px 0; fontSize: 14px; color: #666;";
    
    // Container per i like
    var likeContainer = document.createElement("div");
    likeContainer.className = "like-container";
    likeContainer.style.cssText = "display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 20px; padding: 12px 20px; background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); border-radius: 25px; border: 2px solid #e17055;";
    
    // Bottone cuore
    var heartBtn = document.createElement("button");
    heartBtn.innerHTML = "❤️";
    heartBtn.style.cssText = "font-size: 28px; border: none; background: transparent; cursor: pointer; padding: 8px; border-radius: 50%; transition: all 0.3s ease; outline: none;";
    
    // Contatore like
    var likeCount = document.createElement("span");
    likeCount.className = "like-count";
    likeCount.style.cssText = "font-size: 18px; font-weight: bold; color: #e91e63; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);";
    
    // Gestione stato like
    var savedLikes = parseInt(localStorage.getItem("tattoo_likes_" + tattoo.id) || "0");
    var hasLiked = localStorage.getItem("tattoo_liked_" + tattoo.id) === "true";
    
    likeCount.textContent = savedLikes + " likes";
    
    if (hasLiked) {
        heartBtn.style.transform = "scale(1.2)";
        heartBtn.style.filter = "brightness(1.3) drop-shadow(0 0 8px #ff6b6b)";
    }
    
    // Event listener per il like
    heartBtn.onclick = function(e) {
        e.stopPropagation();
        handleLike(tattoo.id, heartBtn, likeCount);
    };
    
    // Hover effects
    heartBtn.onmouseenter = function() {
        this.style.transform = hasLiked ? "scale(1.4)" : "scale(1.3)";
        this.style.filter = "brightness(1.2)";
    };
    
    heartBtn.onmouseleave = function() {
        var currentLiked = localStorage.getItem("tattoo_liked_" + tattoo.id) === "true";
        this.style.transform = currentLiked ? "scale(1.2)" : "scale(1)";
        this.style.filter = currentLiked ? "brightness(1.3) drop-shadow(0 0 8px #ff6b6b)" : "none";
    };
    
    // Assembla
    likeContainer.appendChild(heartBtn);
    likeContainer.appendChild(likeCount);
    
    item.appendChild(img);
    item.appendChild(desc);
    item.appendChild(username);
    item.appendChild(uploadDate);
    item.appendChild(likeContainer);
    
    // Hover effect sulla card
    item.onmouseenter = function() {
        this.style.transform = "translateY(-8px) scale(1.02)";
        this.style.boxShadow = "0 12px 25px rgba(0,0,0,0.2)";
    };
    
    item.onmouseleave = function() {
        this.style.transform = "translateY(0) scale(1)";
        this.style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)";
    };
    
    galleryContainer.appendChild(item);
}

function handleLike(tattooId, heartBtn, likeCount) {
    var isLiked = localStorage.getItem("tattoo_liked_" + tattooId) === "true";
    var currentLikes = parseInt(localStorage.getItem("tattoo_likes_" + tattooId) || "0");
    
    if (!isLiked) {
        // Aggiungi like
        currentLikes++;
        localStorage.setItem("tattoo_likes_" + tattooId, currentLikes.toString());
        localStorage.setItem("tattoo_liked_" + tattooId, "true");
        
        // Animazione cuore
        heartBtn.style.transform = "scale(1.6)";
        heartBtn.style.filter = "brightness(1.5) drop-shadow(0 0 15px #ff6b6b)";
        heartBtn.innerHTML = "💖";
        
        // Ripristina dopo animazione
        setTimeout(function() {
            heartBtn.innerHTML = "❤️";
            heartBtn.style.transform = "scale(1.2)";
            heartBtn.style.filter = "brightness(1.3) drop-shadow(0 0 8px #ff6b6b)";
        }, 300);
        
        // Crea effetto particelle migliorato
        createSimpleHeartEffect(heartBtn);
        
        console.log("👍 Like aggiunto al tatuaggio", tattooId);
        
    } else {
        // Rimuovi like
        currentLikes = Math.max(0, currentLikes - 1);
        localStorage.setItem("tattoo_likes_" + tattooId, currentLikes.toString());
        localStorage.setItem("tattoo_liked_" + tattooId, "false");
        
        heartBtn.style.transform = "scale(0.8)";
        heartBtn.style.filter = "brightness(0.8)";
        
        setTimeout(function() {
            heartBtn.style.transform = "scale(1)";
            heartBtn.style.filter = "none";
        }, 200);
        
        console.log("👎 Like rimosso dal tatuaggio", tattooId);
    }
    
    likeCount.textContent = currentLikes + " likes";
    
    // Vibrazione su mobile
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
}

function createSimpleHeartEffect(button) {
    // Effetto semplice senza errori
    var rect = button.getBoundingClientRect();
    
    for (var i = 0; i < 3; i++) {
        setTimeout(function(index) {
            var heart = document.createElement("div");
            heart.innerHTML = "💖";
            heart.style.cssText = "position: fixed; font-size: 20px; pointer-events: none; z-index: 9999; transition: all 1s ease-out; opacity: 1;";
            heart.style.left = (rect.left + rect.width/2) + "px";
            heart.style.top = (rect.top + rect.height/2) + "px";
            
            document.body.appendChild(heart);
            
            // Animazione
            setTimeout(function() {
                heart.style.transform = "translateY(-50px) scale(0.5)";
                heart.style.opacity = "0";
            }, 50);
            
            // Rimuovi elemento
            setTimeout(function() {
                if (heart.parentNode) {
                    heart.parentNode.removeChild(heart);
                }
            }, 1100);
            
        }, i * 100, i);
    }
}

function displayFallback() {
    console.log("⚠️ Visualizzazione fallback...");
    galleryContainer.innerHTML = "<div style=\"margin: 20px; padding: 25px; border: 2px solid orange; text-align: center; border-radius: 15px; background: #fff9e6;\"><h3>🖼️ Galleria in costruzione</h3><p>Le immagini verranno caricate a breve!</p><img src=\"images/test.jpg\" alt=\"Test\" style=\"width: 200px; height: 200px; object-fit: cover; margin: 15px 0; border-radius: 10px;\"><div style=\"margin-top: 20px; padding: 10px; background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); border-radius: 25px; display: inline-flex; align-items: center; gap: 10px;\"><button style=\"font-size: 24px; border: none; background: transparent; cursor: pointer;\">❤️</button><span style=\"font-size: 16px; font-weight: bold; color: #e91e63;\">0 likes</span></div></div>";
}

console.log("📄 Gallery script v13 con like fixed caricato completamente");

// Funzione per aprire i dettagli del tatuaggio
function openTattooDetail(tattooId) {
    window.open('/detail.html?id=' + tattooId, '_blank');
}
