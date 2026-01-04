// Sistema di autenticazione FTTH
// Includere questo script in tutte le pagine protette

function checkAuthentication() {
    // Controlla se il cookie di autenticazione esiste
    const cookies = document.cookie.split(';');
    const authCookie = cookies.find(cookie => cookie.trim().startsWith('ftth_auth='));

    if (!authCookie || !authCookie.includes('=true')) {
        // Non autenticato - reindirizza al login
        window.location.href = 'login.html';
        return false;
    }

    return true;
}

function logout() {
    // Rimuovi cookie e reindirizza al login
    document.cookie = 'ftth_auth=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    window.location.href = 'login.html';
}

// Controlla autenticazione al caricamento della pagina
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuthentication()) {
        return; // Non procedere se non autenticato
    }

    // Aggiungi pulsante logout se esiste un elemento con id "logout-btn"
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
        logoutBtn.style.display = 'inline-block';
    }
});