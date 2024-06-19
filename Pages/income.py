from database import DB, Income, Categoria, Expenses

from datetime import datetime, date

from fastapi import HTTPException

from MySQLdb import IntegrityError

from peewee import fn

import calendar

from Pages.validation import validate_school, validate_category, validate_user
######################################################################################

async def get_tt_amounts(school):

    query = (Income
             .select(Income.category, fn.SUM(Income.amount).alias('total_amount'))
             .join(Categoria)
             .where((Income.school_name == school) & (Categoria.nombre != "otros"))
             .group_by(Income.category))


    income_list = []
    
    for income in query:
        income_list.append({
            "categoria": income.category.nombre,
            "total_monto": income.total_amount,
        })

    return income_list

async def get_tt_other_amounts(school):

    query = (Income
            .select(Income.otros_especificar, fn.SUM(Income.amount).alias('total_amount'))
            .join(Categoria)
            .where((Income.school_name == school) & (Categoria.nombre == "otros"))
            .group_by(Income.otros_especificar))


    income_list = []
    
    for income in query:
        income_list.append({
            "categoria": income.otros_especificar,
            "total_monto": income.total_amount,
        })

    return income_list


async def get_tt_amounts_with_current_month(school):
    current_month = datetime.now().month
    current_year = datetime.now().year

    query = (Income
            .select(Income.category, fn.SUM(Income.amount).alias('total_amount'))
            .join(Categoria)
            .where(
                (Income.school_name == school) & 
                (Categoria.nombre != "otros") & 
                (fn.MONTH(Income.date) == current_month) & 
                (fn.YEAR(Income.date) == current_year)
            )
            .group_by(Income.category))

    income_list = []

    for income in query:
        income_list.append({
            "categoria": income.category.nombre,
            "total_monto": income.total_amount,
        })

    return income_list

async def get_tt_other_amounts_with_current_month(school):
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    print(current_month)

    query = (Income
            .select(Income.otros_especificar, fn.SUM(Income.amount).alias('total_amount'))
            .join(Categoria)
            .where(
                (Income.school_name == school) & 
                (Categoria.nombre == "otros") & 
                (fn.MONTH(Income.date) == current_month) & 
                (fn.YEAR(Income.date) == current_year)
            )
            .group_by(Income.otros_especificar))

    income_list = []

    for income in query:
        income_list.append({
            "categoria": income.otros_especificar,
            "total_monto": income.total_amount,
        })

    return income_list


async def get_tt_amounts_with_entered_month(school, month):
    current_year = datetime.now().year

    query = (Income
            .select(Income.category, fn.SUM(Income.amount).alias('total_amount'))
            .join(Categoria)
            .where(
                (Income.school_name == school) & 
                (Categoria.nombre != "otros") & 
                (fn.MONTH(Income.date) == month) & 
                (fn.YEAR(Income.date) == current_year)
            )
            .group_by(Income.category))

    income_list = []

    for income in query:
        income_list.append({
            "categoria": income.category.nombre,
            "total_monto": income.total_amount,
        })

    return income_list

async def get_tt_other_amounts_with_entered_month(school, month):
    current_year = datetime.now().year
    

    query = (Income
            .select(Income.otros_especificar, fn.SUM(Income.amount).alias('total_amount'))
            .join(Categoria)
            .where(
                (Income.school_name == school) & 
                (Categoria.nombre == "otros") & 
                (fn.MONTH(Income.date) == month) & 
                (fn.YEAR(Income.date) == current_year)
            )
            .group_by(Income.otros_especificar))

    income_list = []

    for income in query:
        income_list.append({
            "categoria": income.otros_especificar,
            "total_monto": income.total_amount,
        })

    return income_list


async def get_tt_amounts_with_year_range(school, start_year, end_year):

    query = (Income
            .select(Income.category, fn.SUM(Income.amount).alias('total_amount'))
            .join(Categoria)
            .where(
                (Income.school_name == school) & 
                (Categoria.nombre != "otros") &
                (fn.YEAR(Income.date) >= start_year) & 
                (fn.YEAR(Income.date) <= end_year))
            .group_by(Income.category))

    income_list = []
    # Ejecutar la consulta y obtener los resultados
    for income in query:
        income_list.append({
            "categoria": income.category.nombre,
            "total_monto": income.total_amount,
        })

    return income_list

async def get_tt_other_amounts_with_year_range(school, start_year, end_year):

    query = (Income
            .select(Income.otros_especificar, fn.SUM(Income.amount).alias('total_amount'))
            .join(Categoria)
            .where(
                (Income.school_name == school) & 
                (Categoria.nombre == "otros") &
                (fn.YEAR(Income.date) >= start_year) & 
                (fn.YEAR(Income.date) <= end_year))
            .group_by(Income.otros_especificar))

    income_list = []
    # Ejecutar la consulta y obtener los resultados
    for income in query:
        income_list.append({
            "categoria": income.otros_especificar,
            "total_monto": income.total_amount,
        })

    return income_list


async def get_tt_incomes_with_year(school):

    query = (Income
            .select(fn.YEAR(Income.date).alias("year"), fn.SUM(Income.amount).alias('total_amount'))
            .join(Categoria)
            .where(
                (Income.school_name == school))
            .group_by(fn.YEAR(Income.date)))

    income_list = []
    # Ejecutar la consulta y obtener los resultados
    for income in query:
        income_list.append({
            "year": income.year,
            "total_monto": income.total_amount,
        })

    return income_list


async def get_net_income_with_year(school):
    # Consulta de ingresos por año
    income_query = (Income
                    .select(fn.YEAR(Income.date).alias("year"), fn.SUM(Income.amount).alias('total_amount'))
                    .where(Income.school_name == school)
                    .group_by(fn.YEAR(Income.date)))

    income_dict = {}
    for income in income_query:
        income_dict[income.year] = income.total_amount

    # Consulta de egresos por año
    expense_query = (Expenses
                    .select(fn.YEAR(Expenses.fecha).alias("year"), fn.SUM(Expenses.monto).alias('total_amount'))
                    .where(Expenses.escuela_nombre == school)
                    .group_by(fn.YEAR(Expenses.fecha)))

    expense_dict = {}
    for expense in expense_query:
        expense_dict[expense.year] = expense.total_amount

    # Calcular el ingreso neto por año (ingresos - egresos)
    net_income_list = []
    all_years = set(income_dict.keys()).union(set(expense_dict.keys()))
    
    for year in all_years:
        total_income = income_dict.get(year, 0)
        total_expense = expense_dict.get(year, 0)
        net_income = total_income - total_expense
        net_income_list.append({
            "year": year,
            "net_income": net_income,
        })

    return net_income_list

async def get_all_incomes_with_school(school):
    
    if not Income.select().where(Income.school_name == school).exists():
        raise HTTPException(status_code=400, detail="No existen ingresos de la escuela")

    income_info = (Income.select().where(Income.school_name == school).order_by(Income.id.desc()))

    school_info_list = []
 
    for income in income_info:

        if income.category == "otros":

            school_info_list.append({
                "id": income.id,
                "escuela": income.school_name,
                "categoria": income.category.nombre,
                "especificar": income.otros_especificar,
                "date": income.date,
                "amount": income.amount,
                "user_register": income.user_register,
            })
        
        else:

            school_info_list.append({

                "id": income.id,
                "escuela": income.school_name,
                "categoria": income.category.nombre,
                "date": income.date,
                "amount": income.amount,
                "user_register": income.user_register,
            })


    
    return school_info_list

async def get_all_incomes_with_date(school, start_date, end_date):
    
    if not Income.select().where(Income.school_name == school).exists():
        raise HTTPException(status_code=400, detail="No existen ingresos de la escuela")
    
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    income_info = (Income.select().where((Income.school_name == school) & (Income.date >= start_date) & (Income.date <= end_date)).order_by(Income.id.desc()))

    school_info_list = []
    
    for income in income_info:

        if income.category == "otros":

            school_info_list.append({
                "id": income.id,
                "escuela": income.school_name,
                "categoria": income.category.nombre,
                "especificar": income.otros_especificar,
                "date": income.date,
                "amount": income.amount,
                "user_register": income.user_register,
            })
        
        else:

            school_info_list.append({

                "id": income.id,
                "escuela": income.school_name,
                "categoria": income.category.nombre,
                "date": income.date,
                "amount": income.amount,
                "user_register": income.user_register,
            })

    return school_info_list

async def create_income(income_request):

    await validate_school(income_request.school_name)

    if income_request.category.lower() == "otros":

        print(income_request.category.lower())
        print(income_request.otros_especificar)

        if income_request.otros_especificar == "":
            raise HTTPException(status_code=400, detail="Se requiere especificar una categoría adicional para 'Otros'")
        elif income_request.otros_especificar is None:
            raise HTTPException(status_code=400, detail="El valor de 'otros_especificar' no puede ser None cuando la categoría es 'otros'")
        
    else:

        await validate_category(income_request.category)
        income_request.otros_especificar = None


    await validate_user(income_request.user_register)

    try:

        category_id = Categoria.get_or_none(Categoria.nombre == income_request.category)
        
        print(category_id)
        with DB.atomic():

            income = Income.create(

                school_name=income_request.school_name,
                category=category_id.id,
                otros_especificar=income_request.otros_especificar,
                date=date.today(),
                amount=income_request.amount,
                user_register=income_request.user_register,
            )
            
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")

    return {"mensaje": "Ingreso registrado exitosamente"}

async def get_tt_amounts_with_month_range(school, start_month, end_month):
    # Convertir las cadenas de mes a objetos datetime para manejar el rango correctamente
    start_date = datetime.strptime(start_month, '%Y-%m')
    end_date = datetime.strptime(end_month, '%Y-%m')

    query = (Income
            .select(fn.MONTH(Income.date).alias('month'),
                fn.YEAR(Income.date).alias('year'),
                fn.SUM(Income.amount).alias('total_amount'))
            .where(
                (Income.school_name == school) & 
                ((fn.YEAR(Income.date) > start_date.year) | ((fn.YEAR(Income.date) == start_date.year) & (fn.MONTH(Income.date) >= start_date.month))) &
                ((fn.YEAR(Income.date) < end_date.year) | ((fn.YEAR(Income.date) == end_date.year) & (fn.MONTH(Income.date) <= end_date.month)))
            )
            .group_by(fn.YEAR(Income.date), fn.MONTH(Income.date))
            .order_by(fn.YEAR(Income.date), fn.MONTH(Income.date)))

    income_list = []
    # Ejecutar la consulta y obtener los resultados
    for income in query:
        month_name = calendar.month_name[income.month]
        income_list.append({
            "mes": month_name,
            "total_monto": income.total_amount,
        })

    return income_list
