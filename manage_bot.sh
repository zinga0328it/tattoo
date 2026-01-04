#!/bin/bash

# Script di gestione per il bot Roma Studio Tattoo
# Uso: ./manage_bot.sh [start|stop|restart|status|logs|enable|disable]

SERVICE_NAME="tattoo-bot.service"
LOG_FILE="/home/alex/web/tatuaggi/bot.log"
ERROR_LOG="/home/alex/web/tatuaggi/bot_error.log"

case "$1" in
    start)
        echo "🚀 Avvio del bot..."
        sudo systemctl start $SERVICE_NAME
        echo "✅ Bot avviato!"
        ;;
    stop)
        echo "🛑 Arresto del bot..."
        sudo systemctl stop $SERVICE_NAME
        echo "✅ Bot arrestato!"
        ;;
    restart)
        echo "🔄 Riavvio del bot..."
        sudo systemctl restart $SERVICE_NAME
        echo "✅ Bot riavviato!"
        ;;
    status)
        echo "📊 Status del bot:"
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        echo "📋 Ultimi log del bot:"
        echo "=== BOT LOG ==="
        tail -n 20 $LOG_FILE
        echo ""
        echo "=== ERROR LOG ==="
        tail -n 10 $ERROR_LOG 2>/dev/null || echo "Nessun errore registrato"
        ;;
    enable)
        echo "⚡ Abilito avvio automatico..."
        sudo systemctl enable $SERVICE_NAME
        echo "✅ Avvio automatico abilitato!"
        ;;
    disable)
        echo "❌ Disabilito avvio automatico..."
        sudo systemctl disable $SERVICE_NAME
        echo "✅ Avvio automatico disabilitato!"
        ;;
    *)
        echo "🤖 Script di gestione Bot Roma Studio Tattoo"
        echo ""
        echo "Uso: $0 {start|stop|restart|status|logs|enable|disable}"
        echo ""
        echo "Comandi disponibili:"
        echo "  start     - Avvia il bot"
        echo "  stop      - Ferma il bot"
        echo "  restart   - Riavvia il bot"
        echo "  status    - Mostra lo stato del bot"
        echo "  logs      - Mostra gli ultimi log"
        echo "  enable    - Abilita avvio automatico"
        echo "  disable   - Disabilita avvio automatico"
        echo ""
        echo "Esempi:"
        echo "  $0 start"
        echo "  $0 logs"
        echo "  $0 status"
        exit 1
        ;;
esac

exit 0
