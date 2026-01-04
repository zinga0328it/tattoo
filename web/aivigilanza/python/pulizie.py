#!/usr/bin/env python3
"""
Generatore PDF Contratti Pulizie - Servicess.net
3 tipi di servizio:
- Pulizie Ordinarie: €15/ora
- Pulizie Straordinarie: €20/ora
- Sanificazione: €20/ora
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO
import qrcode
import os

# ============== DATI AZIENDALI ==============
FORNITORE = {
    "nome": "Servicess.net",
    "indirizzo": "Vicolo della Residenza N.6, 01019 Vetralla (VT)",
    "piva": "10807641005",
    "cf": "PPELSN79M18H501R",
    "titolare": "Alessandro Pepe",
    "iban": "IT81A0366901600590252668266",
    "banca": "Revolut Bank UAB",
    "bic": "REVOITM2",
    "email": "info@servicess.net",
    "telefono": "+39 351 012 0753"
}

# ============== TARIFFE ==============
TARIFFE = {
    "ordinarie": 15.0,      # Pulizie ordinarie €15/ora
    "straordinarie": 20.0,  # Pulizie straordinarie €20/ora
    "sanificazione": 20.0   # Sanificazione €20/ora
}

NOMI_SERVIZIO = {
    "ordinarie": "Pulizie Ordinarie",
    "straordinarie": "Pulizie Straordinarie",
    "sanificazione": "Sanificazione Ambienti"
}


def genera_qr_iban(iban: str, importo: float = None, causale: str = "") -> BytesIO:
    """Genera QR code per pagamento IBAN (EPC QR standard europeo)."""
    importo_str = f"EUR{importo:.2f}" if importo else ""
    qr_data = f"""BCD
002
1
SCT

{FORNITORE['nome']}
{iban}
{importo_str}


{causale}"""
    
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


def genera_contratto_pulizie(
    # Dati cliente
    cliente_nome: str,
    cliente_indirizzo: str = "",
    cliente_cf: str = "",
    # Tipo servizio
    tipo_servizio: str = "straordinarie",  # ordinarie, straordinarie, sanificazione
    # Parametri servizio
    num_operatori: int = 1,
    ore_totali: int = 4,
    tariffa_oraria: float = None,  # Se None, usa tariffa di default per tipo
    data_inizio: str = None,
    luogo: str = "Roma",
    note: str = "",
    # Output
    output_path: str = None,
) -> str:
    """
    Genera un PDF di contratto/preventivo per servizio pulizie.
    
    Args:
        tipo_servizio: "ordinarie" (€15/h), "straordinarie" (€20/h), "sanificazione" (€20/h)
    """
    
    # Determina tariffa
    if tariffa_oraria is None:
        tariffa_oraria = TARIFFE.get(tipo_servizio, 20.0)
    
    nome_servizio = NOMI_SERVIZIO.get(tipo_servizio, "Pulizie Straordinarie")
    
    # Calcola totale
    totale = num_operatori * ore_totali * tariffa_oraria
    
    # Data
    oggi = datetime.now()
    data_contratto = oggi.strftime("%d/%m/%Y")
    if not data_inizio:
        data_inizio = "Da concordare"
    
    # Output path
    if not output_path:
        output_path = f"contratto_pulizie_{tipo_servizio}_{oggi.strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Crea documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    # Stili
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='TitoloContratto',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#1a5f2a')
    ))
    styles.add(ParagraphStyle(
        name='Sottotitolo',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=15,
        textColor=colors.HexColor('#2d7a3e')
    ))
    styles.add(ParagraphStyle(
        name='Articolo',
        parent=styles['Heading3'],
        fontSize=11,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor('#1a5f2a')
    ))
    styles.add(ParagraphStyle(
        name='TestoContratto',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='DatiAzienda',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey
    ))
    
    # Contenuto
    story = []
    
    # === INTESTAZIONE ===
    story.append(Paragraph(f"CONTRATTO DI {nome_servizio.upper()}", styles['TitoloContratto']))
    story.append(Paragraph(f"N° {oggi.strftime('%Y%m%d%H%M')}", styles['Sottotitolo']))
    story.append(Spacer(1, 0.5*cm))
    
    # === PARTI CONTRAENTI ===
    story.append(Paragraph("<b>PARTI CONTRAENTI</b>", styles['Articolo']))
    
    fornitore_text = f"""
    <b>FORNITORE:</b><br/>
    {FORNITORE['nome']}<br/>
    {FORNITORE['indirizzo']}<br/>
    P.IVA: {FORNITORE['piva']} - C.F.: {FORNITORE['cf']}<br/>
    Legale Rappresentante: {FORNITORE['titolare']}<br/>
    Tel: {FORNITORE['telefono']} - Email: {FORNITORE['email']}
    """
    story.append(Paragraph(fornitore_text, styles['TestoContratto']))
    story.append(Spacer(1, 0.3*cm))
    
    cliente_text = f"""
    <b>CLIENTE:</b><br/>
    {cliente_nome}<br/>
    {cliente_indirizzo if cliente_indirizzo else 'Indirizzo: ________________________________'}<br/>
    C.F./P.IVA: {cliente_cf if cliente_cf else '________________________________'}
    """
    story.append(Paragraph(cliente_text, styles['TestoContratto']))
    story.append(Spacer(1, 0.5*cm))
    
    # === OGGETTO DEL CONTRATTO ===
    story.append(Paragraph("<b>Art. 1 - OGGETTO DEL CONTRATTO</b>", styles['Articolo']))
    
    if tipo_servizio == "ordinarie":
        descrizione = """Il presente contratto ha per oggetto l'esecuzione di servizi di <b>Pulizia Ordinaria</b> 
        presso i locali indicati dal Cliente. Il servizio comprende: pulizia pavimenti, spolveratura superfici, 
        pulizia servizi igienici, svuotamento cestini, pulizia vetri interni."""
    elif tipo_servizio == "sanificazione":
        descrizione = """Il presente contratto ha per oggetto l'esecuzione di servizi di <b>Sanificazione Ambienti</b> 
        presso i locali indicati dal Cliente. Il servizio comprende: sanificazione completa con prodotti certificati, 
        disinfezione superfici, trattamento antibatterico, nebulizzazione ambienti, rilascio certificato di sanificazione."""
    else:  # straordinarie
        descrizione = """Il presente contratto ha per oggetto l'esecuzione di servizi di <b>Pulizia Straordinaria</b> 
        presso i locali indicati dal Cliente. Il servizio comprende: pulizia profonda pavimenti, rimozione sporco 
        incrostato, pulizia vetri interni ed esterni, trattamento superfici speciali, pulizia post-ristrutturazione."""
    
    story.append(Paragraph(descrizione, styles['TestoContratto']))
    story.append(Spacer(1, 0.3*cm))
    
    # === DETTAGLI SERVIZIO ===
    story.append(Paragraph("<b>Art. 2 - DETTAGLI DEL SERVIZIO</b>", styles['Articolo']))
    
    dettagli_data = [
        ['Tipo Servizio:', nome_servizio],
        ['Luogo:', luogo],
        ['Data Inizio:', data_inizio],
        ['Numero Operatori:', str(num_operatori)],
        ['Ore Totali:', str(ore_totali)],
        ['Tariffa Oraria:', f"€{tariffa_oraria:.2f}"],
    ]
    
    if note:
        dettagli_data.append(['Note:', note])
    
    dettagli_table = Table(dettagli_data, colWidths=[5*cm, 10*cm])
    dettagli_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(dettagli_table)
    story.append(Spacer(1, 0.5*cm))
    
    # === CORRISPETTIVO ===
    story.append(Paragraph("<b>Art. 3 - CORRISPETTIVO</b>", styles['Articolo']))
    
    calcolo_text = f"""
    Il corrispettivo per il servizio è così calcolato:<br/><br/>
    <b>{num_operatori}</b> operatori × <b>{ore_totali}</b> ore × <b>€{tariffa_oraria:.2f}</b>/ora = 
    """
    story.append(Paragraph(calcolo_text, styles['TestoContratto']))
    
    # Box totale evidenziato
    totale_data = [[f"TOTALE: €{totale:.2f}"]]
    totale_table = Table(totale_data, colWidths=[8*cm])
    totale_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f5e9')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#2d7a3e')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(totale_table)
    story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph(
        "Il pagamento dovrà essere effettuato entro 7 giorni dalla conclusione del servizio, "
        "tramite bonifico bancario alle coordinate indicate.",
        styles['TestoContratto']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # === MODALITÀ DI PAGAMENTO ===
    story.append(Paragraph("<b>Art. 4 - MODALITÀ DI PAGAMENTO</b>", styles['Articolo']))
    
    # Genera QR code
    causale = f"{nome_servizio} - {cliente_nome}"
    qr_buffer = genera_qr_iban(FORNITORE['iban'], totale, causale)
    qr_image = Image(qr_buffer, width=3*cm, height=3*cm)
    
    # Tabella pagamento con QR
    iban_data = [
        ['Intestatario:', FORNITORE['nome']],
        ['IBAN:', FORNITORE['iban']],
        ['Banca:', FORNITORE['banca']],
        ['Causale:', causale],
    ]
    
    iban_table = Table(iban_data, colWidths=[3*cm, 9*cm])
    iban_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    payment_layout = Table([[iban_table, qr_image]], colWidths=[12*cm, 4*cm])
    payment_layout.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
        ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(payment_layout)
    story.append(Spacer(1, 0.5*cm))
    
    # === OBBLIGHI DELLE PARTI ===
    story.append(Paragraph("<b>Art. 5 - OBBLIGHI DEL FORNITORE</b>", styles['Articolo']))
    story.append(Paragraph(
        "Il Fornitore si impegna a: eseguire il servizio a regola d'arte con personale qualificato; "
        "utilizzare prodotti professionali e attrezzature idonee; rispettare le normative sulla sicurezza; "
        "fornire documentazione fotografica prima/dopo (su richiesta); rilasciare certificato di pulizia/sanificazione.",
        styles['TestoContratto']
    ))
    
    story.append(Paragraph("<b>Art. 6 - OBBLIGHI DEL CLIENTE</b>", styles['Articolo']))
    story.append(Paragraph(
        "Il Cliente si impegna a: garantire l'accesso ai locali negli orari concordati; "
        "segnalare eventuali aree o oggetti che richiedono attenzione particolare; "
        "effettuare il pagamento nei termini stabiliti.",
        styles['TestoContratto']
    ))
    
    # === RECESSO ===
    story.append(Paragraph("<b>Art. 7 - RECESSO E CANCELLAZIONE</b>", styles['Articolo']))
    story.append(Paragraph(
        "In caso di cancellazione da parte del Cliente con meno di 24 ore di preavviso, "
        "sarà dovuto un rimborso spese pari al 30% del corrispettivo. "
        "Il Fornitore potrà recedere in caso di mancato pagamento di precedenti servizi.",
        styles['TestoContratto']
    ))
    
    # === FORO COMPETENTE ===
    story.append(Paragraph("<b>Art. 8 - FORO COMPETENTE</b>", styles['Articolo']))
    story.append(Paragraph(
        f"Per qualsiasi controversia sarà competente in via esclusiva il Foro di Roma.",
        styles['TestoContratto']
    ))
    story.append(Spacer(1, 0.8*cm))
    
    # === FIRME ===
    story.append(Paragraph(f"<b>Luogo e data:</b> {luogo}, {data_contratto}", styles['TestoContratto']))
    story.append(Spacer(1, 0.5*cm))
    
    firme_data = [
        ['IL FORNITORE', 'IL CLIENTE'],
        ['', ''],
        ['_' * 25, '_' * 25],
        [FORNITORE['titolare'], cliente_nome if cliente_nome != "Cliente" else ''],
    ]
    
    firme_table = Table(firme_data, colWidths=[8*cm, 8*cm])
    firme_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(firme_table)
    
    # === FOOTER ===
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f"{FORNITORE['nome']} - {FORNITORE['indirizzo']} - P.IVA {FORNITORE['piva']}",
        styles['DatiAzienda']
    ))
    
    # Genera PDF
    doc.build(story)
    
    print(f"✅ Contratto pulizie generato: {output_path}")
    print(f"   Tipo: {nome_servizio}")
    print(f"   Cliente: {cliente_nome}")
    print(f"   Totale: €{totale:.2f}")
    
    return output_path


# ============== TEST ==============
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Genera contratto pulizie PDF')
    parser.add_argument('--tipo', choices=['ordinarie', 'straordinarie', 'sanificazione'], 
                        default='straordinarie', help='Tipo servizio')
    parser.add_argument('--cliente', default='Mario Rossi', help='Nome cliente')
    parser.add_argument('--operatori', type=int, default=1, help='Numero operatori')
    parser.add_argument('--ore', type=int, default=4, help='Ore totali')
    parser.add_argument('--luogo', default='Roma', help='Luogo servizio')
    parser.add_argument('--output', help='Path output PDF')
    
    args = parser.parse_args()
    
    print("🧹 Generazione contratto pulizie di esempio...")
    
    genera_contratto_pulizie(
        cliente_nome=args.cliente,
        tipo_servizio=args.tipo,
        num_operatori=args.operatori,
        ore_totali=args.ore,
        luogo=args.luogo,
        output_path=args.output
    )
