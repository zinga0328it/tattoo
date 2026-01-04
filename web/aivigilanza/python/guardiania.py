#!/usr/bin/env python3
"""
guardiania.py - Generatore Preventivi/Contratti Servizio Guardiania
Servicess.net - Vigilanza Privata

Genera PDF con:
- Dati fornitore e cliente
- Articoli contrattuali
- Calcolo automatico prezzo (operatori x ore x tariffa)
- QR Code per pagamento IBAN
- Campi firma
"""

import os
import sys
from datetime import datetime, timedelta
from io import BytesIO

# Dipendenze: pip install reportlab qrcode pillow
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib import colors
    import qrcode
except ImportError as e:
    print(f"❌ Dipendenza mancante: {e}")
    print("Installa con: pip install reportlab qrcode pillow")
    sys.exit(1)


# ============================================================================
# CONFIGURAZIONE FORNITORE (dati fissi Servicess.net)
# ============================================================================
FORNITORE = {
    "nome": "Servicess.net",
    "indirizzo": "Vicolo della Residenza N.6, 01019 Vetralla (VT)",
    "codice_fiscale": "PPELSN79M18H501R",
    "partita_iva": "10807641005",
    "titolare": "Alessandro Pepe",
    "telefono": "+39 351 012 0753",
    "iban": "IT81A0366901600590252668266",
    "banca": "Revolut Bank UAB",
    "bic": "REVOITM2",
}

# Tariffa oraria di default
TARIFFA_ORARIA_DEFAULT = 20.00


# ============================================================================
# FUNZIONI UTILITÀ
# ============================================================================

def genera_qr_iban(iban: str, importo: float = None, causale: str = "") -> BytesIO:
    """Genera QR code per pagamento IBAN (EPC QR standard europeo)."""
    # Formato EPC QR (SEPA Credit Transfer)
    # https://en.wikipedia.org/wiki/EPC_QR_code
    importo_str = f"EUR{importo:.2f}" if importo else ""
    qr_data = f"""BCD
002
1
SCT

{FORNITORE['nome']}
{iban}
{importo_str}


{causale}"""
    
    # Se non c'è importo, QR semplice con solo IBAN
    if not importo:
        qr_data = f"IBAN: {iban}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def calcola_totale(num_operatori: int, ore_per_operatore: int, tariffa_oraria: float) -> float:
    """Calcola il totale del preventivo."""
    return num_operatori * ore_per_operatore * tariffa_oraria


# ============================================================================
# GENERATORE PDF CONTRATTO/PREVENTIVO
# ============================================================================

def genera_contratto_guardiania(
    # Dati cliente
    cliente_nome: str,
    cliente_indirizzo: str,
    cliente_cf: str = "",
    # Parametri servizio
    num_operatori: int = 10,
    ore_per_operatore: int = 1,
    tariffa_oraria: float = TARIFFA_ORARIA_DEFAULT,
    data_inizio: str = None,
    durata_giorni: int = 1,
    # Servizi inclusi
    servizi: list = None,
    # Output
    output_path: str = None,
    luogo: str = "Roma",
) -> str:
    """
    Genera un PDF di contratto/preventivo per servizio di guardiania.
    
    Args:
        cliente_nome: Nome e cognome del cliente
        cliente_indirizzo: Indirizzo del cliente
        cliente_cf: Codice fiscale del cliente
        num_operatori: Numero di operatori
        ore_per_operatore: Ore per operatore
        tariffa_oraria: Tariffa oraria (€)
        data_inizio: Data inizio servizio (formato DD/MM/YYYY), default oggi
        durata_giorni: Durata in giorni
        servizi: Lista servizi (default: tutti)
        output_path: Percorso file output (default: contratto_guardiania_LUOGO.pdf)
        luogo: Luogo del contratto
    
    Returns:
        Percorso del file PDF generato
    """
    
    # Default values
    if data_inizio is None:
        data_inizio = datetime.now().strftime("%d/%m/%Y")
    
    if servizi is None:
        servizi = [
            "Sorveglianza con telecamere intelligenti",
            "Investigazioni private",
            "Vigilanza antintrusione e controllo accessi",
        ]
    
    if output_path is None:
        output_path = f"contratto_guardiania_{luogo.lower().replace(' ', '_')}.pdf"
    
    # Calcolo totale
    totale = calcola_totale(num_operatori, ore_per_operatore, tariffa_oraria)
    
    # Setup documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )
    
    # Stili
    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold',
    )
    
    style_heading = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=11,
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    )
    
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=14,
    )
    
    style_small = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT,
        spaceAfter=4,
    )
    
    # Contenuto
    story = []
    
    # === TITOLO ===
    story.append(Paragraph("CONTRATTO DI PRESTAZIONE SERVIZI DI VIGILANZA PRIVATA", style_title))
    story.append(Spacer(1, 10))
    
    # === PARTI ===
    parti_text = f"""
    <b>Tra:</b><br/>
    {FORNITORE['nome']}, con sede legale in {FORNITORE['indirizzo']}, 
    Codice Fiscale {FORNITORE['codice_fiscale']}, Partita IVA {FORNITORE['partita_iva']}, 
    rappresentata dal titolare {FORNITORE['titolare']}, di seguito denominata "Fornitore"<br/>
    <b>e</b><br/>
    <b>Cliente:</b><br/>
    Nome e Cognome: {cliente_nome}<br/>
    Indirizzo: {cliente_indirizzo}<br/>
    Codice Fiscale: {cliente_cf if cliente_cf else "_________________________"}
    """
    story.append(Paragraph(parti_text, style_body))
    story.append(Spacer(1, 10))
    
    # === PREMESSO CHE ===
    story.append(Paragraph("PREMESSO CHE:", style_heading))
    premessa = """
    Il Fornitore opera nel settore della sicurezza e della vigilanza privata, impiegando personale 
    qualificato e tecnologie avanzate, nel rispetto delle normative vigenti;<br/>
    Il Cliente intende avvalersi dei servizi del Fornitore per la propria attività/immobile;
    """
    story.append(Paragraph(premessa, style_body))
    
    # === ART. 1 - OGGETTO ===
    story.append(Paragraph("ART. 1 - OGGETTO DEL CONTRATTO", style_heading))
    servizi_text = "Il presente contratto ha per oggetto la prestazione dei seguenti servizi di sicurezza:<br/>"
    for servizio in servizi:
        servizi_text += f"- {servizio};<br/>"
    story.append(Paragraph(servizi_text, style_body))
    
    # === ART. 2 - DURATA ===
    story.append(Paragraph("ART. 2 - DURATA E DECORRENZA", style_heading))
    durata_text = f"""
    Il presente contratto prevede un servizio di {ore_per_operatore} {'ora' if ore_per_operatore == 1 else 'ore'} 
    {'giornaliera' if ore_per_operatore == 1 else 'giornaliere'} per un totale di {durata_giorni} 
    {'giorno' if durata_giorni == 1 else 'giorni'} {'consecutivo' if durata_giorni == 1 else 'consecutivi'}, 
    a partire dalla data del {data_inizio}.
    """
    story.append(Paragraph(durata_text, style_body))
    
    # === ART. 3 - OBBLIGHI FORNITORE ===
    story.append(Paragraph("ART. 3 - OBBLIGHI DEL FORNITORE", style_heading))
    obblighi_fornitore = """
    Il Fornitore garantisce:<br/>
    - Il rispetto della normativa in materia di sicurezza, privacy e trattamento dati personali.<br/>
    - L'impiego di personale qualificato e autorizzato.<br/>
    - La manutenzione e il corretto funzionamento degli impianti.
    """
    story.append(Paragraph(obblighi_fornitore, style_body))
    
    # === ART. 4 - OBBLIGHI CLIENTE ===
    story.append(Paragraph("ART. 4 - OBBLIGHI DEL CLIENTE", style_heading))
    obblighi_cliente = """
    Il Cliente si impegna a:<br/>
    - Pagare tempestivamente le fatture emesse.<br/>
    - Consentire l'accesso ai locali per interventi tecnici.<br/>
    - Segnalare tempestivamente malfunzionamenti.
    """
    story.append(Paragraph(obblighi_cliente, style_body))
    
    # === ART. 5 - PAGAMENTO ===
    story.append(Paragraph("ART. 5 - PAGAMENTO", style_heading))
    pagamento_text = f"""
    Il compenso per i servizi è calcolato come segue:<br/>
    - Numero di operatori: {num_operatori}<br/>
    - Ore per operatore: {ore_per_operatore}<br/>
    - Tariffa oraria: €{tariffa_oraria:.2f}<br/>
    <b>Totale: €{totale:.2f}</b><br/><br/>
    Scansiona il QR code per pagare velocemente:
    """
    story.append(Paragraph(pagamento_text, style_body))
    
    # QR Code
    qr_buffer = genera_qr_iban(FORNITORE['iban'], totale, f"Guardiania {cliente_nome}")
    qr_image = Image(qr_buffer, width=40*mm, height=40*mm)
    story.append(qr_image)
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"<b>IBAN:</b> {FORNITORE['iban']}", style_small))
    
    # === ART. 6 - RECESSO ===
    story.append(Paragraph("ART. 6 - RECESSO E SOSPENSIONE", style_heading))
    recesso = """
    Ciascuna parte potrà recedere dal contratto con un preavviso scritto di 30 (trenta) giorni.
    Eventuali ritardi o inadempienze comporteranno l'immediata sospensione dei servizi.
    """
    story.append(Paragraph(recesso, style_body))
    
    # === ART. 7 - FORO ===
    story.append(Paragraph("ART. 7 - FORO COMPETENTE", style_heading))
    story.append(Paragraph(f"Per qualsiasi controversia sarà competente in via esclusiva il Foro di {luogo}.", style_body))
    
    # === ART. 8 - PRIVACY ===
    story.append(Paragraph("ART. 8 - PRIVACY E TRATTAMENTO DATI", style_heading))
    privacy = """
    Il Cliente prende atto che i dati personali e le immagini raccolte nell'ambito del presente 
    contratto saranno trattati dal Fornitore in conformità al Regolamento UE 2016/679 (GDPR) e 
    alla normativa nazionale vigente, esclusivamente per finalità legate all'esecuzione dei 
    servizi di vigilanza e sicurezza.
    """
    story.append(Paragraph(privacy, style_body))
    
    # === FIRME ===
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Luogo e data: {luogo}, {data_inizio}", style_body))
    story.append(Spacer(1, 15))
    
    # Tabella firme
    firma_data = [
        ["_________________________", "_________________________"],
        [f"Fornitore: {FORNITORE['nome']}", "Cliente:"],
    ]
    firma_table = Table(firma_data, colWidths=[80*mm, 80*mm])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(firma_table)
    
    # Genera PDF
    doc.build(story)
    
    print(f"✅ Contratto generato: {output_path}")
    print(f"   Cliente: {cliente_nome}")
    print(f"   Totale: €{totale:.2f}")
    
    return output_path


# ============================================================================
# CLI - Interfaccia a riga di comando
# ============================================================================

def main():
    """Esempio di utilizzo da riga di comando."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera contratti/preventivi per servizio di guardiania",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python guardiania.py --cliente "Mario Rossi" --indirizzo "Via Roma 123, Roma" --operatori 10
  python guardiania.py --cliente "Azienda SRL" --indirizzo "Milano" --operatori 5 --ore 8 --tariffa 25
        """
    )
    
    parser.add_argument("--cliente", required=True, help="Nome cliente")
    parser.add_argument("--indirizzo", required=True, help="Indirizzo cliente")
    parser.add_argument("--cf", default="", help="Codice fiscale cliente")
    parser.add_argument("--operatori", type=int, default=10, help="Numero operatori (default: 10)")
    parser.add_argument("--ore", type=int, default=1, help="Ore per operatore (default: 1)")
    parser.add_argument("--tariffa", type=float, default=20.0, help="Tariffa oraria € (default: 20)")
    parser.add_argument("--giorni", type=int, default=1, help="Durata in giorni (default: 1)")
    parser.add_argument("--luogo", default="Roma", help="Luogo contratto (default: Roma)")
    parser.add_argument("--output", help="File output (default: auto)")
    
    args = parser.parse_args()
    
    genera_contratto_guardiania(
        cliente_nome=args.cliente,
        cliente_indirizzo=args.indirizzo,
        cliente_cf=args.cf,
        num_operatori=args.operatori,
        ore_per_operatore=args.ore,
        tariffa_oraria=args.tariffa,
        durata_giorni=args.giorni,
        luogo=args.luogo,
        output_path=args.output,
    )


if __name__ == "__main__":
    # Se eseguito senza argomenti, genera un esempio
    if len(sys.argv) == 1:
        print("🔧 Generazione contratto di esempio...")
        genera_contratto_guardiania(
            cliente_nome="Mario Rossi",
            cliente_indirizzo="Roma",
            cliente_cf="",
            num_operatori=10,
            ore_per_operatore=1,
            tariffa_oraria=20.00,
            durata_giorni=1,
            luogo="Roma",
            output_path="contratto_guardiania_esempio.pdf",
        )
    else:
        main()
