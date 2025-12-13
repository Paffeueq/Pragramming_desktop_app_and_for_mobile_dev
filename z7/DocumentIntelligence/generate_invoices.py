#!/usr/bin/env python3
"""
Generator testowych faktur dla Azure Document Intelligence
Tworzy 3 przyk³adowe faktury w formacie PDF
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime, timedelta
from pathlib import Path

def create_invoice_1():
    """Faktura 1: ACME Corp"""
    pdf_path = "invoice_acme_001.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6
    )
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Company Info
    company_info = [
        ['<b>ACME Corporation</b>', '', '<b>Invoice Details</b>'],
        ['ul. Handlowa 15', 'Bill To:', 'Invoice #: INV-2025-001'],
        ['80-001 Gdańsk', 'Tech Solutions sp. z o.o.', 'Date: December 13, 2025'],
        ['POLAND', 'ul. Warszawska 88, Warszawa', 'Due Date: January 13, 2026'],
        ['NIP: PL1234567890', '02-100 Warsaw, POLAND', 'Currency: PLN'],
    ]
    
    table = Table(company_info, colWidths=[2.5*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Items Table
    items_data = [
        ['<b>Item</b>', '<b>Description</b>', '<b>Unit Price</b>', '<b>Qty</b>', '<b>Amount</b>'],
        ['SKU-2025-A1', 'Software License - Professional', '500.00 PLN', '2', '1,000.00 PLN'],
        ['SKU-2025-B2', 'Technical Support - 1 Year', '200.00 PLN', '1', '200.00 PLN'],
        ['SKU-2025-C3', 'Consulting Hours', '150.00 PLN', '8', '1,200.00 PLN'],
        ['', '', '', '', ''],
        ['', 'Subtotal:', '', '', '2,400.00 PLN'],
        ['', 'VAT (23%):', '', '', '552.00 PLN'],
        ['', '<b>Total:</b>', '', '', '<b>2,952.00 PLN</b>'],
    ]
    
    table_items = Table(items_data, colWidths=[1*inch, 2.5*inch, 1.2*inch, 0.8*inch, 1.2*inch])
    table_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#e8f0ff')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(table_items)
    story.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9)
    story.append(Paragraph("Payment Method: Bank Transfer | IBAN: PL61109010140000071219812874", footer_style))
    story.append(Paragraph("Thank you for your business!", footer_style))
    
    doc.build(story)
    print(f"✅ Utworzono: {pdf_path}")
    return pdf_path


def create_invoice_2():
    """Faktura 2: Global Tech Services"""
    pdf_path = "invoice_globaltech_002.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2d5016'),
        spaceAfter=6
    )
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Company Info
    company_info = [
        ['<b>Global Tech Services GmbH</b>', '', '<b>Invoice Information</b>'],
        ['Technologiepark 42', 'Sold To:', 'Invoice No.: GTS-EU-2025-0847'],
        ['10115 Berlin', 'DataCorp International', 'Issue Date: December 10, 2025'],
        ['GERMANY', 'Main Street 200, London, UK', 'Due Date: December 31, 2025'],
        ['USt-ID: DE123456789', 'Contact: John Smith', 'Currency: EUR'],
    ]
    
    table = Table(company_info, colWidths=[2.5*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Items Table
    items_data = [
        ['<b>Article</b>', '<b>Description</b>', '<b>Unit Price</b>', '<b>Qty</b>', '<b>Total</b>'],
        ['ART-001', 'Cloud Infrastructure Setup', '2,500.00 EUR', '1', '2,500.00 EUR'],
        ['ART-002', 'Data Migration Service', '1,800.00 EUR', '1', '1,800.00 EUR'],
        ['ART-003', 'Security Audit & Consulting', '3,200.00 EUR', '1', '3,200.00 EUR'],
        ['ART-004', 'Maintenance & Support (6 months)', '900.00 EUR', '1', '900.00 EUR'],
        ['', '', '', '', ''],
        ['', 'Net Total:', '', '', '8,400.00 EUR'],
        ['', 'VAT (19%):', '', '', '1,596.00 EUR'],
        ['', '<b>Invoice Total:</b>', '', '', '<b>9,996.00 EUR</b>'],
    ]
    
    table_items = Table(items_data, colWidths=[1*inch, 2.5*inch, 1.2*inch, 0.8*inch, 1.2*inch])
    table_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5016')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#f0f5e8')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(table_items)
    story.append(Spacer(1, 0.2*inch))
    
    # Payment Info
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9)
    story.append(Paragraph("Payment Instructions: Wire Transfer | Bank: Deutsche Bank | Account: 123456789", footer_style))
    story.append(Paragraph("Terms: Net 30 days from invoice date", footer_style))
    
    doc.build(story)
    print(f"✅ Utworzono: {pdf_path}")
    return pdf_path


def create_invoice_3():
    """Faktura 3: Tech Startup Inc"""
    pdf_path = "invoice_techstartup_003.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#c41e3a'),
        spaceAfter=6
    )
    story.append(Paragraph("FACTURA", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Company Info (bilingual: Spanish/English)
    company_info = [
        ['<b>Tech Startup Inc.</b>', '', '<b>Datos de la Factura</b>'],
        ['Silicon Valley Center', 'Facturado a:', 'Número: 2025-12-847'],
        ['San Francisco, CA 94102', 'Enterprise Solutions LLC', 'Fecha: 12 de diciembre de 2025'],
        ['USA', '1500 Tech Drive, Austin, TX 78701', 'Vencimiento: 12 de enero de 2026'],
        ['Tax ID: 94-1234567', 'USA', 'Moneda: USD'],
    ]
    
    table = Table(company_info, colWidths=[2.5*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Items Table
    items_data = [
        ['<b>Item</b>', '<b>Descripción</b>', '<b>Precio Unit.</b>', '<b>Cant.</b>', '<b>Subtotal</b>'],
        ['TSI-2025-01', 'Web Application Development', '5,000.00 USD', '1', '5,000.00 USD'],
        ['TSI-2025-02', 'API Integration & Testing', '2,500.00 USD', '1', '2,500.00 USD'],
        ['TSI-2025-03', 'Deployment & Configuration', '1,500.00 USD', '1', '1,500.00 USD'],
        ['TSI-2025-04', 'Training & Documentation', '1,200.00 USD', '1', '1,200.00 USD'],
        ['', '', '', '', ''],
        ['', 'Subtotal:', '', '', '10,200.00 USD'],
        ['', 'Impuestos (10%):', '', '', '1,020.00 USD'],
        ['', '<b>Total a Pagar:</b>', '', '', '<b>11,220.00 USD</b>'],
    ]
    
    table_items = Table(items_data, colWidths=[1*inch, 2.5*inch, 1.2*inch, 0.8*inch, 1.2*inch])
    table_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#ffe8eb')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(table_items)
    story.append(Spacer(1, 0.2*inch))
    
    # Payment Terms
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9)
    story.append(Paragraph("Método de pago: ACH Transfer | Bank: Wells Fargo | Routing: 121000248", footer_style))
    story.append(Paragraph("Términos: Pago neto en 30 días | Gracias por su negocio", footer_style))
    
    doc.build(story)
    print(f"✅ Utworzono: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    # Create directory if not exists
    Path(".").mkdir(exist_ok=True)
    
    print("📋 Generowanie testowych faktur...\n")
    invoices = []
    invoices.append(create_invoice_1())
    invoices.append(create_invoice_2())
    invoices.append(create_invoice_3())
    
    print(f"\n✅ Wszystkie {len(invoices)} faktury zostały utworzone!")
    print(f"\nPliki:")
    for inv in invoices:
        print(f"  - {inv}")
