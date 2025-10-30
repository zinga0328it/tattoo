// Versione ULTRA-SEMPLICE per test (senza template literals)
document.addEventListener("DOMContentLoaded", function() {
    var container = document.getElementById("gallery-container");
    if (container) {
        // Inserisci direttamente HTML semplice
        container.innerHTML = "<div style=\"margin: 10px; padding: 10px; border: 2px solid green;\"><img src=\"images/test.jpg\" alt=\"Test\" style=\"width: 200px; height: 200px; object-fit: cover; border-radius: 8px;\"><p style=\"text-align: center; margin-top: 10px;\">Tatuaggio di prova</p></div>";
    }
});
