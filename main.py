from fastapi import FastAPI, UploadFile, File

from typing import Optional

from fastapi.responses import FileResponse

from database import DB as connection 
from database import create_database
from database import User, User_Info, Income, Escuela, DetalleEscuela, ExtraEscuela, Categoria, SubCategoria, Supervisor, Reports, Validate_Expenses,Expenses, Expenses_Field

from os import getcwd, makedirs
from fastapi.middleware.cors import CORSMiddleware

#region Pages

import Pages.login as p_login
import Pages.users as p_users
import Pages.categoria as p_categoria
import Pages.escuelas as p_escuelas
import Pages.income as p_income
import Pages.pdf as p_pdf
import Pages.expenses as p_expenses
import Pages.supervisor as p_sup


#endregion

#region Record

from records import all_records

#endregion 

#region schemas

from schemas.sch_categorias import CategoriaUpdate, CategoriaCrear
from schemas.sch_users import UserInfoCreate, UserInfoUpdate, UserUpdate
from schemas.sch_income import  IncomeCreate
from schemas.sch_escuela import DetalleEscuelaCreate, DetalleEscuelaUpdate, ExtraEscueCreate, ExtraEscueUpdate
from schemas.sch_pdf import PDFCreate
from schemas.sch_escuela import DetalleEscuelaCreate, DetalleEscuelaUpdate, ExtraEscueCreate, ExtraEscueUpdate
from schemas.sch_expenses import ExpensesCreate
from schemas.sch_supervisor import SupUpdate

#endregion

app = FastAPI(title="Escuela", description="Software para el uso y administracion de una escuela", version='1.0.1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_database('escuela')

#region Inicio del servidor
@app.on_event('startup')
def startup():
        
    if connection.is_closed():
        connection.connect()

    connection.create_tables([Supervisor])
    connection.create_tables([User])
    connection.create_tables([User_Info])

    
    connection.create_tables([Escuela])
    connection.create_tables([DetalleEscuela])
    connection.create_tables([ExtraEscuela])
    connection.create_tables([Categoria])
    connection.create_tables([Income])
    connection.create_tables([Reports])
    connection.create_tables([SubCategoria])

    connection.create_tables([Expenses])
    connection.create_tables([Validate_Expenses])
    connection.create_tables([Expenses_Field])

    all_records()
    makedirs(getcwd() + "/Files", exist_ok=True)
    makedirs(getcwd() + "/logos", exist_ok=True)


@app.on_event('shutdown')
def shutdown():

    if not connection.is_closed():
            connection.close()  
#endregion


@app.get("/")
def read_root():
    return {"Hello": "World"}

#region Login

@app.post('/login', tags=["login"])
async def Login(user: str, password: str):
    return await p_login.login(user, password)

#endregion

#region Users

@app.get("/user/info/consulta/id/{id}", tags=["User"])
async def get_user_id(id: str, activate: Optional[bool] = True):
    return await p_users.get_user_id(id, activate)

@app.get("/users/info/consulta/escuela/{escuela}", tags=["User"])
async def get_all_users_info_escuela(escuela: str, activate: Optional[bool] = True):
    return await p_users.get_all_users_info_escuela(escuela, activate)

@app.get("/users/info/consulta/rol/{rol}", tags=["User"])
async def get_all_users_info_rol(rol: str, activate: Optional[bool] = True):
    return await p_users.get_all_users_info_rol(rol, activate)

@app.get("/users/info/consulta/", tags=["User"])
async def get_all_users_info(activate: Optional[bool] = True):
    return await p_users.get_all_users_info(activate)

@app.post('/users/create', tags=["User"])
async def create_user(rol: str, password: str, user_request: UserInfoCreate):
    return await p_users.create_user(rol, password, user_request)

@app.put("/users/update/user", tags=["User"])
async def update_user(user_request: UserUpdate):
    return await p_users.update_user(user_request)

@app.put("/users/update/user_info", tags=["User"])
async def update_user_info(user_request: UserInfoUpdate):
    return await p_users.update_user_info(user_request)

@app.delete('/users/delete', tags=["User"])
async def delete_user(user_id: str):
    return await p_users.delete_user(user_id)

#endregion

#region Categoria

@app.get('/categoria/consulta/all/ingresos', tags=["categoria"])
async def consultar_categoria_todos_ingresos():
    return await p_categoria.get_all_incomes()

@app.get('/categoria/consulta/all/egresos', tags=["categoria"])
async def consultar_categoria_todos_egresos():
    return await p_categoria.get_all_expenses()

@app.get('/categoria/consulta/ingresos', tags=["categoria"])
async def consultar_categoria_ingresos():
    return await p_categoria.consult_categoria_income()

@app.get('/categoria/consulta/egresos', tags=["categoria"])
async def consultar_categoria_egresos():
    return await p_categoria.consult_categoria_expenses()

@app.get('/categoria/consulta/escuela/ingresos', tags=["categoria"])
async def consultar_categoria_egresos(nombre_escuela: str):
    return await p_categoria.consult_categoria_school_income(nombre_escuela)

@app.get('/categoria/consulta/escuela/egresos', tags=["categoria"])
async def consultar_categoria_egresos(nombre_escuela: str):
    return await p_categoria.consult_categoria_school_expenses(nombre_escuela)

@app.post('/categoria/crear', tags=["categoria"])
async def crear_categoria(categoria_request: CategoriaCrear):
    return await p_categoria.create_categoria(categoria_request)

@app.put('/categoria/actualizar', tags=['categoria'])
async def update_cliente(categoria_nombre, categoria_tipo,categoria_request: CategoriaUpdate):
    return await p_categoria.update_categoria(categoria_nombre, categoria_tipo, categoria_request)

#endregion

#region incomes
@app.get('/income/consulta/escuela/{escuela}', tags=["Income"])
async def get_all_incomes_with_school(school:str):
    return await p_income.get_all_incomes_with_school(school)

@app.get('/income/consulta/date/{escuela}', tags=["Income"])
async def get_all_incomes_with_date(school:str, start_date:str, end_date:str):
    return await p_income.get_all_incomes_with_date(school, start_date, end_date)

@app.post('/income/create', tags=["Income"])
async def create_income(income_request:IncomeCreate):
    return await p_income.create_income(income_request)

#endregion

#region Escuelas

@app.get('/escuela/consulta/', tags=["Escuela"])
async def get_all_schools():
    return await p_escuelas.get_all_schools()

@app.post('/escuela/create', tags=["Escuela"])
async def create_user(nombre:str, detalle_request: DetalleEscuelaCreate, extra_request: ExtraEscueCreate):
    return await p_escuelas.create_escuela(nombre,detalle_request,extra_request )

@app.post('/escuela/saveLogo', tags=["Escuela"])
async def save_logo(nombre_escuela: str, logo: UploadFile = File(...)):
    return await p_escuelas.save_logo(nombre_escuela, logo)

@app.get('/escuela/consulta/{escuela}', tags=["Escuela"])
async def get_all_schools(school:str):
    return await p_escuelas.consult_escuelas(school)

@app.put("/escuela/actualizar/nombre", tags=["Escuela"])
async def update_schools(school:str,newname:str,newlogo:str):
    return await p_escuelas.update_school_base(school,newname,newlogo)

@app.put("/escuela/actualizar/localizacion", tags=["Escuela"])
async def update_schools_place(school_request: DetalleEscuelaUpdate):
    return await p_escuelas.update_school_place(school_request)

@app.put("/escuela/actualizar/alumnado", tags=["Escuela"])
async def update_schools_parents(school_request: ExtraEscueUpdate):
    return await p_escuelas.update_school_parents(school_request)

@app.delete('/escuela/delete', tags=["Escuela"])
async def delete_school(school: str):
    return await p_escuelas.delete_school(school)

@app.get("/logo/{name_logo}", tags=["Escuela"])
async def get_logo(name_logo: str):
    #regrasa del directorio actual donde estamos + el nombre del archivo
    return FileResponse(getcwd() + "/logos/" + name_logo)

#endregion

#region Supervisor
@app.get("/supervisor/consulta/id/{id}", tags=["Supervisor"])
async def get_supervisor(id: int):
    return await p_sup.get_sup(id)

@app.put("/supervisor/actualizar/", tags=["Supervisor"])
async def get_supervisor(name:str, sup_reques: SupUpdate):
    return await p_sup.update_sup(name, sup_reques)

#endregion


#region pdf
@app.post("/pdf/create/", tags=["PDF"])
async def crete_pdf(pdf_request:PDFCreate):
    pdf_path = await p_pdf.create_pdf(pdf_request)
    return FileResponse(path=pdf_path, filename=pdf_request.doc_name + ".pdf", media_type='application/pdf')
#endregion

#region expenses

@app.post('/expenses/create', tags=["Expenses"])
async def create_expense(expenses_request:ExpensesCreate):
    return await p_expenses.create_expenses(expenses_request)

@app.put('/expenses/validated', tags=["Expenses"])
async def validate_expense(id_expense_file:int,user_register:str):
    return await p_expenses.validate_expenses(id_expense_file,user_register)

@app.post('/expenses/saveFiles', tags=["Expenses"])
async def save_files(id_expense: int, file: UploadFile = File(...)):
    return await p_expenses.save_files(id_expense, file)

@app.get('/expenses/consultar/escuela/{escuela_nombre}', tags=["Expenses"])
async def consult_expenses_for_schoolname(escuela_nombre:str):
    return await p_expenses.consult_expenses_for_schoolname(escuela_nombre)

@app.get('/expenses/consultar/fecha/{fecha}', tags=["Expenses"])
async def consult_expenses_for_date(escuela_nombre:str,fechaInicial:str,fechaFinal:str):
    return await p_expenses.consult_expenses_for_date(escuela_nombre,fechaInicial,fechaFinal)

@app.get('/expensesFile/consultar/{id_expenses}', tags=["Expenses"])
async def consult_expenses_documents(id_expenses:int):
    return await p_expenses.consult_expenses_documents(id_expenses)

@app.get("/file/{name_file}", tags=["Expenses"])
async def get_file(name_file: str):
    #regrasa del directorio actual donde estamos + el nombre del archivo
    return FileResponse(getcwd() + "/Files/" + name_file)

#endregion

#region dashboard

@app.get('/dashboard/get/incomes', tags=["Dashboard Income"])
async def get_all_incomes(school: str):
    return await p_income.get_tt_amounts(school)

@app.get('/dashboard/get/other_incomes', tags=["Dashboard Income"])
async def get_all_other_incomes(school: str):
    return await p_income.get_tt_other_amounts(school)

@app.get('/dashboard/get/incomes/current_month', tags=["Dashboard Income"])
async def get_all_incomes_with_current_month(school: str):
    return await p_income.get_tt_amounts_with_current_month(school)

@app.get('/dashboard/get/other_incomes/current_month', tags=["Dashboard Income"])
async def get_all_other_incomes_with_current_month(school: str):
    return await p_income.get_tt_other_amounts_with_current_month(school)

@app.get('/dashboard/get/incomes/entered_month', tags=["Dashboard Income"])
async def get_all_incomes_with_entered_month(school: str, month:int):
    return await p_income.get_tt_amounts_with_entered_month(school, month)

@app.get('/dashboard/get/other_incomes/entered_month', tags=["Dashboard Income"])
async def get_all_other_incomes_with_entered_month(school: str, month:int):
    return await p_income.get_tt_other_amounts_with_entered_month(school, month)

@app.get('/dashboard/get/incomes/year_range', tags=["Dashboard Income"])
async def get_all_incomes_with_year_range(school: str, start_year:int, end_year:int):
    return await p_income.get_tt_amounts_with_year_range(school, start_year, end_year)

@app.get('/dashboard/get/other_incomes/year_range', tags=["Dashboard Income"])
async def get_all_other_incomes_with_year_range(school: str, start_year:int, end_year:int):
    return await p_income.get_tt_other_amounts_with_year_range(school, start_year, end_year)

@app.get('/dashboard/get/incomes/for_year', tags=["Dashboard Income"])
async def get_all_other_incomes_for_year(school: str):
    return await p_income.get_tt_incomes_with_year(school)

@app.get('/dashboard/get/incomes/month_range', tags=["Dashboard Income"])
async def get_tt_amounts_with_month_range(school: str, start_date:str, end_date:str):
    return await p_income.get_tt_amounts_with_month_range(school, start_date, end_date)


#endregion


#region Dashboard expense

@app.get('/dashboard/get_all/expenses', tags=["Dashboard Expense"])
async def get_all_expenses(school: str):
    return await p_expenses.get_tt_amounts_with_expense(school)

@app.get('/dashboard/get_all/other_expenses', tags=["Dashboard Expense"])
async def get_all_other_expenses(school: str):
    return await p_expenses.get_tt_amounts_with_other_expense(school)

@app.get('/dashboard/get/expenses/current_month', tags=["Dashboard Expense"])
async def get_all_expenses_with_current_month(school: str):
    return await p_expenses.get_tt_amounts_with_current_month(school)

@app.get('/dashboard/get/expenses/entered_month', tags=["Dashboard Expense"])
async def get_all_expenses_with_entered_month(school: str, month: str):
    return await p_expenses.get_tt_amounts_with_entered_month(school, month)

@app.get('/dashboard/get/expenses/year_range', tags=["Dashboard Expense"])
async def get_all_expenses_with_year_range(school: str, start_year:int, end_year:int):
    return await p_expenses.get_tt_amounts_with_year_range(school, start_year, end_year)

@app.get('/dashboard/get/expenses/for_year', tags=["Dashboard Expense"])
async def get_all_expenses_for_year(school: str):
    return await p_expenses.get_tt_expenses_with_year(school)

@app.get('/dashboard/get/expenses/month_range', tags=["Dashboard Expense"])
async def get_tt_expenses_with_month_range(school: str, start_year:str, end_year:str):
    return await p_expenses.get_tt_expenses_with_month_range(school, start_year, end_year)

@app.get('/dashboard/get/expensesDocument/for_user', tags=["Dashboard Expense"])
async def get_tt_expenses_document(user: str):
    return await p_expenses.get_tt_expenses_document(user)

"""@app.get('/dashboard/get/expensesDocument/for_month', tags=["Dashboard Expense"])
async def get_tt_expenses_document_for_month(user: str, start_year:str, end_year:str):
    return await p_expenses.get_tt_expenses_document_for_month(user, start_year, end_year)"""

#endregion


#region promedio
@app.get('/dashboard/get/promedio/for_year', tags=["Dashboard promedio"])
async def get_promedio_for_year(school: str):
    return await p_income.get_net_income_with_year(school)

@app.get('/dashboard/get/cuotaEsperada/for_school', tags=["Dashboard promedio"])
async def get_tt_cuotaEsperada(school: str):
    return await p_escuelas.get_tt_cuotaEsperada(school)
