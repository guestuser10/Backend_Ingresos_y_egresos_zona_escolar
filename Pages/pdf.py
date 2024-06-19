from peewee import fn

from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os


from Pages.escuelas import consult_escuelas

from fastapi import HTTPException

from database import Supervisor, Escuela, Reports, Income, Expenses, User_Info

from peewee import DoesNotExist

from Pages.income import get_tt_amounts_with_year_range, get_tt_other_amounts_with_year_range
from Pages.expenses import get_tt_amounts_with_year_range2

#region reportlab imports
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
#endregion

def format_currency(value):
    
    return f"${value:,.2f}"

def get_supervisor(id):

    supervisor = Supervisor.get_by_id(id)
    
    return supervisor

async def get_number_report(school: str):

    if not Escuela.select().where((Escuela.nombre == school) & (Escuela.activate == True)).exists():
        raise HTTPException(status_code=400, detail="La escuela no existe")
    
    ultimo_reporte = Reports.select().where(Reports.escuela == school).order_by(Reports.numero_reporte.desc()).first()
    
    if ultimo_reporte:
        return ultimo_reporte.numero_reporte + 1
    else:
        return 1

async def get_school_names(school:str):
    
    if not Escuela.select().where(Escuela.nombre == school).exists():
        raise HTTPException(status_code=400, detail="La escuela no existe")
    
    
    try:
            escuela = Escuela.get(Escuela.nombre == school)

            presidente_info = User_Info.get(User_Info.user_id == escuela.presidente_id)
            director_info = User_Info.get(User_Info.user_id == escuela.director_id)
            tesorero_info = User_Info.get(User_Info.user_id == escuela.tesorero_id)

            school_list = [{
                "presidente": f"{presidente_info.name} {presidente_info.last_name}",
                "director": f"{director_info.name} {director_info.last_name}",
                "tesorero": f"{tesorero_info.name} {tesorero_info.last_name}"
            }]
            
            return school_list

    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Información de usuario no encontrada")



async def create_pdf(pdf_request):
    
    #region styles
    styles = getSampleStyleSheet()

    title_standard = ParagraphStyle(
        "title_standard",                
        fontSize=12,                   
        alignment=1,                   
        fontName="Times-Roman",
        leading=15,
    )
    
    title_bold = ParagraphStyle(
        "title_bold",
        fontSize=12,                   
        alignment=1,                   
        fontName="Times-Bold",
        leading=15,
    )
    
    title_bold_records = ParagraphStyle(
        "title_bold_records",
        fontSize=11,                   
        alignment=0,                   
        fontName="Times-Bold",
        leading=15,
    )
    
    title_bold_amounts = ParagraphStyle(
        "title_bold_amounts",
        fontSize=11,                   
        alignment=2,                   
        fontName="Times-Bold",
    )
    
    title_normal_amounts = ParagraphStyle(
        "title_normal_amounts",
        fontSize=11,                   
        alignment=2,                   
        fontName="Times-Roman",
    )
    
    title_signament = ParagraphStyle(
        "title_signament",
        fontSize=8,                   
        alignment=1,                   
        fontName="Times-Roman",
    )
    
    title_signament_bold = ParagraphStyle(
        "title_signament_bold",
        fontSize=8,                   
        alignment=1,                   
        fontName="Times-Bold",
    )
    
    title_fecha = ParagraphStyle(
        "title_fecha",
        fontSize=11,                   
        alignment=0,                   
        fontName="Times-Roman",
        leading=15,
    )
    
    # Agregar el nuevo estilo al diccionario de estilos
    styles.add(title_standard)
    styles.add(title_bold)
    styles.add(title_bold_records)
    styles.add(title_bold_amounts)
    styles.add(title_normal_amounts)
    styles.add(title_signament)
    styles.add(title_signament_bold)
    styles.add(title_fecha)
    
    #endregion
    
    info_names = await get_school_names(pdf_request.school)
    
    incomes = await get_tt_amounts_with_year_range(pdf_request.school, pdf_request.start_year, pdf_request.end_year)
    other_incomes = await get_tt_other_amounts_with_year_range(pdf_request.school, pdf_request.start_year, pdf_request.end_year)
    
    expenses = await get_tt_amounts_with_year_range2(pdf_request.school, pdf_request.start_year, pdf_request.end_year)
    
    num_reporte = await get_number_report(pdf_request.school)
    supervisor = get_supervisor(1)
    info_school = await consult_escuelas(pdf_request.school)
    
    pdf_path = pdf_request.doc_name + ".pdf"

    margin = 0.1 * inch
    
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=letter,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )

    # Crear una lista para almacenar los elementos
    story = []

    titles_pdf(story, styles, supervisor.estado, num_reporte, pdf_request.start_year, pdf_request.end_year)
    
    info_pdf(story, info_school)
    
    tt_ingreso = incomes_pdf(story, styles, incomes, other_incomes)
    
    tt_egreso = expenses_pdf(story, styles, expenses)
    
    final_amount_pdf(story, tt_ingreso, tt_egreso)
    
    signature_section_pdf(story, styles, info_names, info_school["zona"])
    
    doc.title = "Informe Anual"
    doc.build(story)
    
    return pdf_path
    
def titles_pdf(story, styles, estado:str, num_reporte:int, start_date:str, end_date:str):

    # Textos
    text1 = Paragraph(f"GOBIERNO DEL ESTADO DE {estado.upper()}", styles['title_bold'])
    text2 = Paragraph("SECRETARÍA DE EDUCACIÓN PUBLICA Y CULTURA", styles['title_standard'])
    text3 = Paragraph("DIRECCIÓN DE VINCULACIÓN SOCIAL", styles['title_standard'])

    # Lista de párrafos
    text = [text1, text2, text3]

    # Imagen
    img_path = 'logo.PNG'
    img_width = 2 * inch  # Ajusta el ancho de la imagen
    img_height = 0.8 * inch  # Ajusta el alto de la imagen
    img = Image(img_path, width=img_width, height=img_height)

    # Crear una tabla con 1 fila y 2 columnas
    data = [[img, text]]
    table = Table(data, colWidths=[img_width, 6 * inch], rowHeights=[img_height])

    # Estilo de la tabla
    style = TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Alinear imagen al centro
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),  # Centrar verticalmente la imagen
        ('ALIGN', (1, 0), (1, 2), 'RIGHT'),  # Alinear texto a la derecha
        ('VALIGN', (1, 0), (1, 2), 'MIDDLE'),  # Centrar verticalmente el texto
    ])

    table.setStyle(style)
    
    # Añadir la tabla al story
    story.append(table)

    text4 = Paragraph("COORDINACIÓN ESTATAL DE UNIDADES DE ATENCIÓN A PADRES DE FAMILIA", styles['title_standard'])
    story.append(text4)
    
    story.append(Spacer(1, 5))
    
    text5 = Paragraph(f"{num_reporte}° Informe Financiero de las Asociaciones de Padres de Familia", styles['title_bold']) 
    story.append(text5)
    
    text6 = Paragraph(f"Ciclo escolar {start_date} - {end_date}", styles['title_standard']) 
    story.append(text6)
    
def info_pdf(story, info_school):

    cuota_format = format_currency(info_school.get("cuota", 0))  
    
    # Crear una tabla de 5x3
    data = [
        [f'Escuela                  {info_school["nombre"]}',         f'Clave: {info_school["clave"]} ',       f'Turno: {info_school["turno"]}'],
        [f'Zona:                    {info_school["zona"]}',         f'Sector: {info_school["sector"]}',      f'Domicilio: {info_school["domicilio"]}'],
        [f'Localidad:               {info_school["localidad"]}',    f'Telefono: {info_school["telefono"]}',  ''],
        [f'No. de Padre de Familia: {info_school["no_familia"]}',   '',                                      f'Cuota de Padres de Familia: {cuota_format}'],
        [f'Total de Alumnos:        {info_school["tt_alumnos"]}',   '',                                      f'Total de Grupos: {info_school["tt_grupos"]}']
    ]
    
    table = Table(data, colWidths=[2.5 * inch] * 3, rowHeights=[0.3 * inch] * 5)
    
    story.append(Spacer(2, 10))
    
    style = TableStyle([
        # Alineación: primera columna a la izquierda, segunda en el centro, tercera a la derecha
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        # Verticalmente alineado hacia arriba solo en la primera fila
        ('VALIGN', (0, 0), (-1, 0), 'TOP'),
        # Fuente y tamaño de fuente
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        # Estilo de bordes
        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
        ('LINEBEFORE', (0, 0), (0, -1), 0.5, colors.black),
        ('LINEAFTER', (-1, 0), (-1, -1), 0.5, colors.black),
    ])
    table.setStyle(style)
    
    story.append(table)

def incomes_pdf(story, styles, incomes, other_incomes):
    
    tt_incomes = sum(income['total_monto'] for income in incomes)
    tt_other_incomes = sum(income['total_monto'] for income in other_incomes)
    
    # Crear datos de la tabla de ingresos dinámicamente
    data = [[Paragraph('A. INGRESOS ECONÓMICOS.', styles['title_bold_records'])]]
    
    data.append(['TOTAL DE INGRESOS PRIMER PERIODO'])
    
    for ingreso in incomes:
        data.append([ingreso['categoria'], format_currency(ingreso['total_monto'])])
    
    data.append(['Otros ingresos (especifique): '])
    
    for other in other_incomes:
            data.append([other['categoria'], format_currency(other['total_monto'])])
    
    data.append([
        Paragraph('TOTAL DE INGRESOS:', styles['title_bold_amounts']),
        Paragraph(format_currency(tt_incomes + tt_other_incomes), styles['title_normal_amounts'])
    ])
    
    # Crear una tabla con tantas filas como ingresos haya
    table = Table(data, colWidths=[5.5 * inch, 2 * inch], rowHeights=[0.2 * inch] * len(data))
    
    story.append(Spacer(2, 10))
    
    style = TableStyle([
        # Alineación
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        # Fuente y tamaño de fuente
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        # Estilo de bordes y fondos
        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
        ('LINEBEFORE', (0, 0), (0, -1), 0.5, colors.black),
        ('LINEAFTER', (-1, 0), (-1, -1), 0.5, colors.black),
    ])
    table.setStyle(style)
    
    story.append(table)
    
    return tt_incomes + tt_other_incomes
    
def expenses_pdf(story, styles, expenses):
    
    tt_expense = sum(expense['total_monto'] for expense in expenses)
    
    # Crear datos de la tabla de ingresos dinámicamente
    data = [[Paragraph('B. EGRESOS REGISTRADOS', styles['title_bold_records'])]]
    data.append(['TOTAL DE EGRESOS PRIMER PERIODO'])
    
    for egreso in expenses:
        data.append([egreso['categoria'], format_currency(egreso['total_monto'])])
    
    
    data.append([
        Paragraph('TOTAL DE EGRESOS:', styles['title_bold_amounts']),
        Paragraph(format_currency(tt_expense), styles['title_normal_amounts'])
    ])
    # Crear una tabla con tantas filas como ingresos haya
    table = Table(data, colWidths=[5.5 * inch, 2 * inch], rowHeights=[0.2 * inch] * len(data))
    
    story.append(Spacer(2, 10))
    
    style = TableStyle([
        # Alineación
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        # Fuente y tamaño de fuente
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        # Estilo de bordes y fondos
        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
        ('LINEBEFORE', (0, 0), (0, -1), 0.5, colors.black),
        ('LINEAFTER', (-1, 0), (-1, -1), 0.5, colors.black),
    ])
    table.setStyle(style)
    
    story.append(table)
    
    return tt_expense 
    
def final_amount_pdf(story, tt_ingresos: float, tt_egresos: float):
    
    saldo = tt_ingresos - tt_egresos
    
    # Datos para la tabla de 1x1
    data = [['Saldo', format_currency(saldo)]]
    
    # Crear una tabla de 1x1
    table = Table(data, colWidths=[5.5 * inch, 2 * inch], rowHeights=[0.5 * inch])

    # Estilos de la tabla
    style = TableStyle([
        ('ALIGN', (0, 0), (-2, -1), 'RIGHT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ])
    table.setStyle(style)
    
    # Añadir la tabla al Story
    story.append(table)

def signature_section_pdf(story, styles, info_names, zona):
    
    presidente = info_names[0]['presidente'].upper()
    director = info_names[0]['director'].upper()
    tesorero = info_names[0]['tesorero'].upper()
    supervisor = get_supervisor(1).name.upper()
    

    # Datos para la tabla de 1x1
    data = [['Fecha:', '']]
    
    # Crear una tabla de 1x1
    table = Table(data, colWidths=[5.5 * inch, 2 * inch], rowHeights=[0.5 * inch])

    # Estilos de la tabla
    style = TableStyle([
        ('ALIGN', (0, 0), (-2, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ])
    table.setStyle(style)
    
    story.append(table)
    
    story.append(Spacer(1, 0.5 * inch)) 

    data = [
        [Paragraph('_____________________________________________________',  styles['title_signament_bold']),  Paragraph('_____________________________________________________',  styles['title_signament_bold'])],
        [Paragraph(presidente,  styles['title_signament']),                        Paragraph(tesorero,     styles['title_signament'])],
        [Paragraph('PRESIDENTE DE LA MESA DIRECTIVA',  styles['title_signament']), Paragraph('TESORERO DE LA MESA DIRECTIVA',   styles['title_signament'])],
        [Paragraph('', ),                                       Paragraph('', )],
        [Paragraph('', ),                                       Paragraph('', )],
        [Paragraph('', ),                                       Paragraph('', )],
        [Paragraph('', ),                                       Paragraph('', )],
        [Paragraph('_____________________________________________________', styles['title_signament_bold']),  Paragraph('_____________________________________________________',  styles['title_signament_bold'])],
        [Paragraph(director,        styles['title_signament']),                    Paragraph(supervisor,   styles['title_signament'])],
        [Paragraph('VoBo DIRECTOR', styles['title_signament']),                    Paragraph(f'VoBo SUPERVISOR ESCOLAR {zona}',  styles['title_signament'])],
    ]

    # Crear la tabla
    table = Table(data, colWidths=[4 * inch, 4 * inch], rowHeights=[0.2 * inch] *  10)

    style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Primera columna alineada a la izquierda
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'), # Segunda columna alineada a la derecha
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Times-Roman'), # Primera columna en Times-Roman
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'), # Segunda columna en Times-Roman
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white), # Quitar bordes poniendo el color blanco
        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.white), # Quitar bordes entre celdas
        ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors.white) # Quitar bordes entre celdas
    ])
    table.setStyle(style)

    # Añadir la tabla al Story
    story.append(table)
