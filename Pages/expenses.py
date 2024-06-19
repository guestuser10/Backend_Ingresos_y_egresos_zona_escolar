from database import DB, Expenses, Validate_Expenses, Expenses_Field, Escuela, Categoria, User

from datetime import datetime, date

from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from MySQLdb import IntegrityError

from Pages.validation import validate_school, validate_category, validate_user

from peewee import Join, JOIN, fn

import calendar

from os import getcwd

async def get_tt_amounts_with_expense(school):

    query = (Expenses
            .select(Expenses.category, fn.SUM(Expenses.monto).alias('total_amount'))
            .join(Categoria)
            .where((Expenses.escuela_nombre == school) & (Categoria.nombre != "otros"))
            .group_by(Expenses.category))


    expenses_list = []
    
    for expenses in query:
        expenses_list.append({
            "categoria": expenses.category.nombre,
            "total_monto": expenses.total_amount,
        })

    return expenses_list

async def get_tt_amounts_with_other_expense(school):

    query = (Expenses
            .select(Expenses.category, fn.SUM(Expenses.monto).alias('total_amount'))
            .join(Categoria)
            .where((Expenses.escuela_nombre == school) & (Categoria.nombre == "otros"))
            .group_by(Expenses.category))


    expense_list = []
    
    for expense in query:
        expense_list.append({
            "categoria": expense.category.nombre,
            "total_monto": expense.total_amount,
        })

    return expense_list


async def get_tt_amounts_with_current_month(school):
    current_month = datetime.now().month
    current_year = datetime.now().year

    query = (Expenses
            .select(Expenses.category, fn.SUM(Expenses.monto).alias('total_amount'))
            .join(Categoria)
            .where(
                (Expenses.escuela_nombre == school) &  
                (fn.MONTH(Expenses.fecha) == current_month) & 
                (fn.YEAR(Expenses.fecha) == current_year)
            )
            .group_by(Expenses.category))

    expense_list = []

    for expense in query:
        expense_list.append({
            "categoria": expense.category.nombre,
            "total_monto": expense.total_amount,
        })

    return expense_list

async def get_tt_amounts_with_entered_month(school, month):
    current_year = datetime.now().year

    query = (Expenses
            .select(Expenses.category, fn.SUM(Expenses.monto).alias('total_amount'))
            .join(Categoria)
            .where(
                (Expenses.escuela_nombre == school) & 
                (fn.MONTH(Expenses.fecha) == month) & 
                (fn.YEAR(Expenses.fecha) == current_year)
            )
            .group_by(Expenses.category))

    expense_list = []

    for expense in query:
        expense_list.append({
            "categoria": expense.category.nombre,
            "total_monto": expense.total_amount,
        })

    return expense_list

async def get_tt_amounts_with_year_range(school, start_year, end_year):

    query = (Expenses
            .select(Expenses.category, fn.SUM(Expenses.monto).alias('total_amount'))
            .join(Categoria)
            .where(
                (Expenses.escuela_nombre == school) & 
                (fn.YEAR(Expenses.fecha) >= start_year) & 
                (fn.YEAR(Expenses.fecha) <= end_year))
            .group_by(Expenses.category))

    expense_list = []
    # Ejecutar la consulta y obtener los resultados
    for expense in query:
        expense_list.append({
            "categoria": expense.category.nombre,
            "total_monto": expense.total_amount,
        })

    return expense_list

async def get_tt_amounts_with_year_range2(school, start_year, end_year):

    query = (Expenses
            .select(Expenses.category, fn.SUM(Expenses.monto).alias('total_amount'))
            .join(Categoria)
            .where(
                (Expenses.escuela_nombre == school) & 
                (fn.YEAR(Expenses.fecha) >= start_year) & 
                (fn.YEAR(Expenses.fecha) <= end_year))
            .group_by(Expenses.category))

    expense_list = []
    # Ejecutar la consulta y obtener los resultados
    for expense in query:
        expense_list.append({
            "categoria": expense.category.nombre,
            "total_monto": expense.total_amount,
        })

    return expense_list

async def get_tt_expenses_with_year(school):

    query = (Expenses
            .select(fn.YEAR(Expenses.fecha).alias("year"), fn.SUM(Expenses.monto).alias('total_amount'))
            .join(Categoria)
            .where(
                (Expenses.escuela_nombre == school))
            .group_by(fn.YEAR(Expenses.fecha)))

    expense_list = []
    # Ejecutar la consulta y obtener los resultados
    for expense in query:
        expense_list.append({
            "year": expense.year,
            "total_monto": expense.total_amount,
        })

    return expense_list


async def create_expenses(expenses_request):

    await validate_school(expenses_request.escuela_nombre)
    await validate_user(expenses_request.user_register)

    if not Categoria.select().where(Categoria.nombre == expenses_request.category).exists():
        raise HTTPException(status_code=400, detail="La categoria no existe")

    try:
        category_id = Categoria.get_or_none(Categoria.nombre == expenses_request.category)

        with DB.atomic():
            expense = Expenses.create(
                escuela_nombre=expenses_request.escuela_nombre,
                category=category_id.id,
                fecha=date.today(),
                monto=expenses_request.monto,
                user_register=expenses_request.user_register,
            )
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")

    return {"mensaje": "Egreso registrado exitosamente"}


async def validate_expenses(id_expense,user_register):

    if not Expenses_Field.select().where(Expenses_Field.id == id_expense).exists():
        raise HTTPException(status_code=400, detail="El documento del egreso no existe")  
    
    await validate_user(user_register)

    try:
        query_rol = User.select().where(User.username == user_register).first()
        query = Validate_Expenses.select().where(Validate_Expenses.id_expenses_field == id_expense).first()

        if query.validado:
            raise HTTPException(status_code=400, detail="El documento del egreso ya se encuentra validado")

        if query_rol.rol == "presidente":
            Validate_Expenses.update(presidente=True).where(Validate_Expenses.id_expenses_field == id_expense).execute()
        elif query_rol.rol == "tesorero":
            Validate_Expenses.update(tesorero=True).where(Validate_Expenses.id_expenses_field == id_expense).execute()
        elif query_rol.rol == "director":
            Validate_Expenses.update(director=True).where(Validate_Expenses.id_expenses_field == id_expense).execute()

        query = Validate_Expenses.select().where(Validate_Expenses.id_expenses_field == id_expense).first()

        if query.presidente==True and query.tesorero==True and query.director==True:
            Validate_Expenses.update(validado=True).where(Validate_Expenses.id_expenses_field == id_expense).execute()

    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")

    return {"mensaje": "Documento validado exitosamente"}

async def save_files(id_expense, field):

    if not Expenses.select().where(Expenses.id == id_expense).exists():
        raise HTTPException(status_code=400, detail="El egreso no existe")
    
    if Expenses_Field.select().where((Expenses_Field.id_expenses == id_expense) &(Expenses_Field.archivo==field)).exists():
        raise HTTPException(status_code=400, detail="El Documento ya existe")

    query_roles = Escuela.select().join(Expenses, on=(Escuela.nombre == Expenses.escuela_nombre)).where(Expenses.id == id_expense).first()
    try:

        #abre el archivo desde el directorio actual en el que estamos + el nombre del archivo y le damos los permisios de 
        #escritura y binario, y hacemos referencia como myfile
        with open(getcwd() + "/Files/" + field.filename, "wb") as myfile:
            #leemos su contenido y lo guardo en la variable content
            content = await field.read()
            #guardamos en myfile el contenido que leimos
            myfile.write(content)
            #cerramos el archivo
            myfile.close()

        with DB.atomic():
            field_request = Expenses_Field.create(
                id_expenses = id_expense,
                archivo= field.filename
            )
            validate_expense = Validate_Expenses.create(
                id_expenses_field=field_request.id,
                presidente_id = query_roles.presidente.id,
                tesorero_id = query_roles.tesorero.id,
                director_id = query_roles.director.id,
                presidente=False,
                tesorero=False,
                director=False,
                validado=False,
            )
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")
    
    return {"mensaje": "Documento guardado exitosamente"}

async def consult_expenses_for_schoolname(escuela_nombre):
    
    if not Expenses.select().where(Expenses.escuela_nombre == escuela_nombre).exists():
        raise HTTPException(status_code=400, detail="No existen egresos de la escuela.")
    
    expenses_dict  = []
    try:
        query=Expenses.select().where(Expenses.escuela_nombre == escuela_nombre).order_by(Expenses.id.desc())

        for expense in query:
            expenses_dict.append({
                "id": expense.id,
                "escuela_nombre": escuela_nombre,
                "category": expense.category.nombre,
                "fecha": expense.fecha,
                "monto": expense.monto,
                "user_register": expense.user_register,
                })
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")
    return expenses_dict

async def consult_expenses_for_date(escuela_nombre, fechaInicio, fechaFinal):
    
    if not Expenses.select().where(Expenses.escuela_nombre == escuela_nombre).exists():
        raise HTTPException(status_code=400, detail="No existen egresos de la escuela.")
    
    if not Expenses.select().where((Expenses.escuela_nombre == escuela_nombre) & (Expenses.fecha >= fechaInicio) &(Expenses.fecha <= fechaFinal)).exists():
        raise HTTPException(status_code=400, detail="No existen egresos en la fecha.")
    
    expenses_dict  = []
    try:
        query=Expenses.select().where((Expenses.escuela_nombre == escuela_nombre) & (Expenses.fecha >= fechaInicio) &(Expenses.fecha <= fechaFinal)).order_by(Expenses.id.desc())

        for expense in query:
            expenses_dict.append({
                "id": expense.id,
                "escuela_nombre": escuela_nombre,
                "category": expense.category.nombre,
                "fecha": expense.fecha,
                "monto": expense.monto,
                "user_register": expense.user_register,
            })
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")
    return expenses_dict

async def consult_expenses_documents(id_expenses):
    
    if not Expenses.select().where(Expenses.id == id_expenses).exists():
        raise HTTPException(status_code=400, detail="No se encontro el egreso.")
    
    if not Expenses_Field.select().where(Expenses_Field.id_expenses == id_expenses).exists():
        raise HTTPException(status_code=400, detail="No se encontro el documento del egreso.")
    
    expenses_dict  = []
    try:
        query=Expenses_Field.select(Expenses_Field.id,
                                        Expenses_Field.id_expenses,
                                        Expenses_Field.archivo,
                                        Validate_Expenses.presidente_id,
                                        Validate_Expenses.tesorero_id,
                                        Validate_Expenses.director_id,
                                        Validate_Expenses.presidente,
                                        Validate_Expenses.tesorero,
                                        Validate_Expenses.director,
                                        Validate_Expenses.validado
                                    ).join(Validate_Expenses, on=(Expenses_Field.id == Validate_Expenses.id_expenses_field)).where(Expenses_Field.id_expenses == id_expenses).first()

        presidente = User.select(User.username).where(User.id == query.validate_expenses.presidente_id).first()
        tesorero = User.select(User.username).where(User.id == query.validate_expenses.tesorero_id).first()
        director = User.select(User.username).where(User.id == query.validate_expenses.director_id).first()
        expenses_dict = {
                "id": query.id,
                "id_expenses": query.id_expenses,
                "archivo": query.archivo,
                "presidente_usuario": presidente.username,
                "tesorero_usuario": tesorero.username,
                "director_usuario": director.username,
                "presidente": query.validate_expenses.presidente,
                "tesorero": query.validate_expenses.tesorero,
                "director": query.validate_expenses.director,
                "validado": query.validate_expenses.validado,
                }
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")
    return expenses_dict

async def get_tt_expenses_with_month_range(school, start_month, end_month):
    # Convertir las cadenas de mes a objetos datetime para manejar el rango correctamente
    start_date = datetime.strptime(start_month, '%Y-%m')
    end_date = datetime.strptime(end_month, '%Y-%m')

    query = (Expenses
            .select(fn.MONTH(Expenses.fecha).alias('month'),
                fn.YEAR(Expenses.fecha).alias('year'),
                fn.SUM(Expenses.monto).alias('total_amount'))
            .where(
                (Expenses.escuela_nombre == school) & 
                ((fn.YEAR(Expenses.fecha) > start_date.year) | ((fn.YEAR(Expenses.fecha) == start_date.year) & (fn.MONTH(Expenses.fecha) >= start_date.month))) &
                ((fn.YEAR(Expenses.fecha) < end_date.year) | ((fn.YEAR(Expenses.fecha) == end_date.year) & (fn.MONTH(Expenses.fecha) <= end_date.month)))
            )
            .group_by(fn.YEAR(Expenses.fecha), fn.MONTH(Expenses.fecha))
            .order_by(fn.YEAR(Expenses.fecha), fn.MONTH(Expenses.fecha)))

    expense_list = []
    # Ejecutar la consulta y obtener los resultados
    for expense in query:
        month_name = calendar.month_name[expense.month]
        expense_list.append({
            "mes": month_name,
            "total_monto": expense.total_amount,
        })

    return expense_list



async def get_tt_expenses_document(user):
    query_Usuario = User.select().where(User.username == user).first()
    documentos = 0
    documentosNoValidados = 0
    if query_Usuario.rol == "presidente":
        query_documentos_todos = (Validate_Expenses
            .select(Validate_Expenses.validado, Validate_Expenses.presidente)
            .where(
                (Validate_Expenses.presidente_id == query_Usuario.id) 
                )
            .group_by(Validate_Expenses.id)
            .order_by(Validate_Expenses.id))
        
        for expense in query_documentos_todos:
            documentos+=1
            if expense.presidente == False:
                documentosNoValidados+=1
        
        expense_list = {
            "total_documentos": documentos,
            "total_documentos_faltantes": documentosNoValidados,
        }

    elif query_Usuario.rol == "tesorero":
        query_documentos_todos = (Validate_Expenses
            .select(Validate_Expenses.validado, Validate_Expenses.tesorero)
            .where(
                (Validate_Expenses.tesorero_id == query_Usuario.id) 
                )
            .group_by(Validate_Expenses.id)
            .order_by(Validate_Expenses.id))

        for expense in query_documentos_todos:
            documentos+=1
            if expense.tesorero == False:
                documentosNoValidados+=1
        
        expense_list = {
            "total_documentos": documentos,
            "total_documentos_faltantes": documentosNoValidados,
        }

    elif query_Usuario.rol == "director":
        query_documentos_todos = (Validate_Expenses
            .select(Validate_Expenses.validado, Validate_Expenses.director)
            .where(
                (Validate_Expenses.director_id == query_Usuario.id) 
                )
            .group_by(Validate_Expenses.id)
            .order_by(Validate_Expenses.id))
        
        for expense in query_documentos_todos:
            documentos+=1
            if expense.director == False:
                documentosNoValidados+=1
        
        expense_list = {
            "total_documentos": documentos,
            "total_documentos_faltantes": documentosNoValidados,
        }

    return expense_list


"""async def get_tt_expenses_document_for_month(user, start_month, end_month):
    query_Usuario = User.select().where(User.username == user).first()
    documentos = 0
    documentosNoValidados = 0
    # Convertir las cadenas de mes a objetos datetime para manejar el rango correctamente
    start_date = datetime.strptime(start_month, '%Y-%m-01')
    end_date = datetime.strptime(end_month, '%Y-%m-01')
    end_date = (end_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    if query_Usuario.rol == "presidente":
        query_documentos_todos = (Validate_Expenses
            .select(Validate_Expenses.validado, Validate_Expenses.presidente)
            .join(Expenses, on=(Validate_Expenses.id_expenses_field == Expenses.id))
            .where(
                (Validate_Expenses.presidente_id == query_Usuario.id) &
                (Expenses.fecha.between(start_date, end_date))
                )
            .group_by(Validate_Expenses.id)
            .order_by(Validate_Expenses.id))
        
        for expense in query_documentos_todos:
            documentos+=1
            if expense.presidente == False:
                documentosNoValidados+=1
        
        expense_list = {
            "total_documentos": documentos,
            "total_documentos_faltantes": documentosNoValidados,
        }

    elif query_Usuario.rol == "tesorero":
        query_documentos_todos = (Validate_Expenses
            .select(Validate_Expenses.validado, Validate_Expenses.tesorero)
            .where(
                (Validate_Expenses.tesorero_id == query_Usuario.id) 
                )
            .group_by(Validate_Expenses.id)
            .order_by(Validate_Expenses.id))







        for expense in query_documentos_todos:
            documentos+=1
            if expense.tesorero == False:
                documentosNoValidados+=1
        
        expense_list = {
            "total_documentos": documentos,
            "total_documentos_faltantes": documentosNoValidados,
        }

    elif query_Usuario.rol == "director":
        query_documentos_todos = (Validate_Expenses
            .select(Validate_Expenses.validado, Validate_Expenses.director)
            .where(
                (Validate_Expenses.director_id == query_Usuario.id) 
                )
            .group_by(Validate_Expenses.id)
            .order_by(Validate_Expenses.id))
        
        for expense in query_documentos_todos:
            documentos+=1
            if expense.director == False:
                documentosNoValidados+=1
        
        expense_list = {
            "total_documentos": documentos,
            "total_documentos_faltantes": documentosNoValidados,
        }

    return expense_list"""


