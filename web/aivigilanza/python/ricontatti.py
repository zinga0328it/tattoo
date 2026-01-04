#!/usr/bin/env python3
"""
Modulo per generazione contratti di ricontatto e consulenza
Genera PDF con i dati del richiedente e il contratto accettato
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import qrcode
from io import BytesIO
import hashlib

# === DATI AZIENDA ===
AZIENDA = {
    "nome": "Servicess.net",
    "titolare": "Alessandro Pepe",
    "indirizzo": "Via G. Galopini, 1",
    "cap": "00133",
    "citta": "Roma",
    "provincia": "RM",
    "piva": "10807641005",
    "cf": "PPELSN79M18H501R",
    "email": "info@servicess.net",
    "telefono": "+39 328 0120753",
    "sito": "https://servicess.net"
}

# Colori
BRAND_BLUE = HexColor("#4da3ff")
DARK_BG = HexColor("#0b1320")
TEXT_DARK = HexColor("#212529")


def genera_hash_contratto(dati: dict) -> str:
    """Genera hash univoco per il contratto"""
    stringa = f"{dati.get('nome','')}{dati.get('cognome','')}{dati.get('email','')}{datetime.now().isoformat()}"
    return hashlib.sha256(stringa.encode()).hexdigest()[:16].upper()


def genera_qr_code(url: str, size: int = 100) -> Image:
    """Genera QR code come immagine ReportLab"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return Image(buffer, width=size, height=size)


def genera_contratto_ricontatto(
    nome: str,
    cognome: str,
    email: str,
    telefono: str = "",
    indirizzo: str = "",
    citta: str = "",
    cap: str = "",
    cf_piva: str = "",
    tipo_servizio: str = "",
    descrizione_richiesta: str = "",
    output_path: str = None
) -> str:
    """
    Genera PDF contratto di ricontatto.
    
    Args:
        nome, cognome, email: dati obbligatori
        telefono, indirizzo, citta, cap, cf_piva: dati opzionali
        tipo_servizio: vigilanza, pulizie, sicurezza, altro
        descrizione_richiesta: note aggiuntive
        output_path: percorso file PDF
    
    Returns:
        Percorso del PDF generato
    """
    
    # Path output
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_safe = f"{nome}_{cognome}".replace(' ', '_')[:30]
        output_path = f"/var/www/aivigilanza/contratti/ricontatto_{nome_safe}_{timestamp}.pdf"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Genera hash contratto
    hash_contratto = genera_hash_contratto({
        "nome": nome,
        "cognome": cognome, 
        "email": email
    })
    
    # Data e ora
    data_ora = datetime.now()
    data_str = data_ora.strftime("%d/%m/%Y")
    ora_str = data_ora.strftime("%H:%M:%S")
    
    # Tipo servizio formattato
    tipi_servizio = {
        "vigilanza": "Vigilanza Privata",
        "pulizie": "Pulizie Professionali",
        "sicurezza": "Consulenza Sicurezza",
        "web": "Servizi Web",
        "altro": "Altro"
    }
    servizio_desc = tipi_servizio.get(tipo_servizio, tipo_servizio or "Non specificato")
    
    # Documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Stili
    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=BRAND_BLUE,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    style_subtitle = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    style_heading = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=BRAND_BLUE,
        spaceBefore=15,
        spaceAfter=8
    )
    
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14
    )
    
    style_small = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=8,
        textColor=HexColor("#6c757d"),
        alignment=TA_CENTER
    )
    
    # Contenuto
    elements = []
    
    # Header
    elements.append(Paragraph("📄 CONTRATTO DI RICONTATTO E CONSULENZA", style_title))
    elements.append(Paragraph(f"Documento generato il {data_str} alle {ora_str}", style_subtitle))
    elements.append(Spacer(1, 20))
    
    # Parti contraenti
    elements.append(Paragraph("PARTI CONTRAENTI", style_heading))
    
    # Tabella parti
    parti_data = [
        ["FORNITORE", "RICHIEDENTE"],
        [
            f"{AZIENDA['nome']}\n"
            f"Titolare: {AZIENDA['titolare']}\n"
            f"{AZIENDA['indirizzo']}\n"
            f"{AZIENDA['cap']} {AZIENDA['citta']} ({AZIENDA['provincia']})\n"
            f"P.IVA: {AZIENDA['piva']}\n"
            f"C.F.: {AZIENDA['cf']}\n"
            f"Email: {AZIENDA['email']}\n"
            f"Tel: {AZIENDA['telefono']}",
            
            f"{nome} {cognome}\n"
            f"Email: {email}\n"
            f"Telefono: {telefono or 'Non fornito'}\n"
            f"Indirizzo: {indirizzo or 'Non fornito'}\n"
            f"CAP/Città: {cap} {citta}\n"
            f"CF/P.IVA: {cf_piva or 'Non fornito'}"
        ]
    ]
    
    parti_table = Table(parti_data, colWidths=[8*cm, 8*cm])
    parti_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#ffffff")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor("#f8f9fa")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#dee2e6")),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(parti_table)
    elements.append(Spacer(1, 20))
    
    # Richiesta
    elements.append(Paragraph("OGGETTO DELLA RICHIESTA", style_heading))
    
    richiesta_data = [
        ["Tipo di Servizio:", servizio_desc],
        ["Descrizione:", descrizione_richiesta or "Richiesta generica di informazioni e preventivo"]
    ]
    
    richiesta_table = Table(richiesta_data, colWidths=[4*cm, 12*cm])
    richiesta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor("#e9ecef")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#dee2e6")),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(richiesta_table)
    elements.append(Spacer(1, 20))
    
    # Articoli contratto
    elements.append(Paragraph("TERMINI E CONDIZIONI", style_heading))
    
    articoli = [
        ("Art. 1 - OGGETTO", 
         "Il presente contratto ha ad oggetto la richiesta di ricontatto e consulenza "
         "per i servizi di vigilanza privata e/o pulizie professionali offerti da Servicess.net."),
        
        ("Art. 2 - CONSULENZA GRATUITA",
         "Servicess.net si impegna a ricontattare il richiedente per fornire informazioni "
         "accurate e complete sui propri servizi, inclusa la formulazione di un preventivo "
         "personalizzato. La consulenza è completamente gratuita e non comporta alcun obbligo "
         "di stipula contrattuale."),
        
        ("Art. 3 - TRATTAMENTO DATI PERSONALI",
         "I dati personali forniti saranno trattati nel rispetto del Regolamento (UE) 2016/679 (GDPR) "
         "e utilizzati esclusivamente per le finalità indicate: rispondere alla richiesta di ricontatto, "
         "fornire informazioni sui servizi e formulare preventivi. I dati saranno conservati per un "
         "periodo massimo di 2 anni dalla raccolta."),
        
        ("Art. 4 - CONSENSO AL TRATTAMENTO",
         "Il richiedente dichiara di aver letto e compreso l'informativa privacy e acconsente "
         "esplicitamente al trattamento dei propri dati personali per le finalità sopra indicate."),
        
        ("Art. 5 - DIRITTI DELL'INTERESSATO",
         "L'interessato ha diritto di accedere ai propri dati, richiederne la rettifica o la "
         "cancellazione, opporsi al trattamento o richiedere la portabilità dei dati, contattando "
         f"il Titolare del trattamento all'indirizzo email {AZIENDA['email']}."),
        
        ("Art. 6 - FORO COMPETENTE",
         "Per qualsiasi controversia derivante dal presente contratto sarà competente "
         "in via esclusiva il Foro di Roma."),
        
        ("Art. 7 - ACCETTAZIONE ELETTRONICA",
         "Il presente contratto si intende accettato con la sottoscrizione elettronica "
         "del modulo di richiesta online. La firma elettronica ha valore legale ai sensi "
         "del Regolamento eIDAS (UE) n. 910/2014.")
    ]
    
    for titolo, testo in articoli:
        elements.append(Paragraph(f"<b>{titolo}</b>", style_body))
        elements.append(Paragraph(testo, style_body))
    
    elements.append(Spacer(1, 25))
    
    # Firma e QR
    elements.append(Paragraph("SOTTOSCRIZIONE ELETTRONICA", style_heading))
    
    # Genera QR con link al sito
    qr_img = genera_qr_code(AZIENDA['sito'], size=80)
    
    firma_data = [
        [
            f"Contratto sottoscritto elettronicamente\n\n"
            f"Richiedente: {nome} {cognome}\n"
            f"Email: {email}\n"
            f"Data: {data_str} - Ora: {ora_str}\n\n"
            f"Hash documento: {hash_contratto}",
            qr_img
        ]
    ]
    
    firma_table = Table(firma_data, colWidths=[11*cm, 3*cm])
    firma_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor("#e8f4ff")),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
        ('FONTSIZE', (0, 0), (0, 0), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, BRAND_BLUE),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(firma_table)
    
    elements.append(Spacer(1, 30))
    
    # Footer
    elements.append(Paragraph(
        f"Documento generato automaticamente da {AZIENDA['sito']} - ID: {hash_contratto}",
        style_small
    ))
    elements.append(Paragraph(
        f"© {data_ora.year} {AZIENDA['nome']} - Tutti i diritti riservati",
        style_small
    ))
    
    # Build PDF
    doc.build(elements)
    
    return output_path


# Test
if __name__ == "__main__":
    pdf = genera_contratto_ricontatto(
        nome="Mario",
        cognome="Rossi",
        email="mario.rossi@email.it",
        telefono="333 1234567",
        indirizzo="Via Roma 1",
        citta="Roma",
        cap="00100",
        cf_piva="RSSMRA80A01H501Z",
        tipo_servizio="vigilanza",
        descrizione_richiesta="Vorrei informazioni per servizio di guardiania notturna",
        output_path="/tmp/test_ricontatto.pdf"
    )
    print(f"✅ PDF generato: {pdf}")
