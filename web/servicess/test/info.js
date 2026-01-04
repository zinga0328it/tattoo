// Funzione per salvare la mail in un cookie per 1 anno
function salvaEmail(email) {
  document.cookie = "email=" + encodeURIComponent(email) + "; path=/; max-age=31536000";
}

// Mostra un banner per l'accettazione dei log/cookie
function mostraAvvisoLog() {
  if (!document.cookie.includes("accetta_log=1")) {
    const banner = document.createElement("div");
    banner.id = "avviso-log";
    banner.style = "position:fixed;bottom:0;left:0;width:100%;background:#222;color:#fff;padding:16px;text-align:center;z-index:9999;";
    banner.innerHTML = `
      Questo sito raccoglie dati di accesso per motivi di sicurezza e statistica. Proseguendo accetti la registrazione dei log.<br>
      <button id="accetta-log-btn" style="margin-top:8px;padding:6px 18px;">Accetta</button>
    `;
    document.body.appendChild(banner);
    document.getElementById("accetta-log-btn").onclick = function() {
      document.cookie = "accetta_log=1; path=/; max-age=31536000";
      document.body.removeChild(banner);
    };
  }
}

// Chiamata alla funzione per mostrare il banner
mostraAvvisoLog();