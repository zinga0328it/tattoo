console.log("=== GALLERY TEST SCRIPT AVVIATO ===");

document.addEventListener("DOMContentLoaded", function() {
    console.log("DOM caricato, inizializzazione galleria...");
    
    var galleryContainer = document.getElementById("gallery-container");
    console.log("Container trovato:", galleryContainer);
    
    if (!galleryContainer) {
        console.error("ERRORE: gallery-container non trovato!");
        return;
    }
    
    // Test 1: Inserimento diretto HTML (senza template literals)
    console.log("Test 1: Inserimento diretto immagine test.jpg");
    galleryContainer.innerHTML = "<div style=\"border: 2px solid red; padding: 10px;\"><img src=\"images/test.jpg\" alt=\"Test\" style=\"width: 200px; height: 200px; object-fit: cover;\" onload=\"console.log(Immagine
