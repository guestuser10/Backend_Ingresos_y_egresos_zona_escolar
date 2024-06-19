from database import Escuela,DetalleEscuela,ExtraEscuela, DB, Income
from schemas.sch_escuela import DetalleEscuelaCreate, ExtraEscueCreate, DetalleEscuelaUpdate, ExtraEscueUpdate
from fastapi import HTTPException

from MySQLdb import IntegrityError

from peewee import DoesNotExist, JOIN, IntegrityError, fn

from datetime import datetime

from os import getcwd

async def get_all_schools():

    school_info = list(Escuela.select())

    return [
        {
            "escuela": school.nombre,
        } 

        for school in school_info]



"""async def create_escuela(nombre):

    if Escuela.select().where(Escuela.nombre == nombre).exists():
        raise HTTPException(status_code=400, detail="La escuela ya existe")
    
    try:

        escuela = Escuela.create(
        
            nombre = nombre,
        )

    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")

    return {"mensaje": "Escuela creada exitosamente"}"""


async def create_escuela(nombre, detalle_request: DetalleEscuelaCreate, extra_request: ExtraEscueCreate):

    consulta = Escuela.select().where(Escuela.nombre == nombre).first()
    if consulta:
        if consulta.activate:
            raise HTTPException(status_code=400, detail="La escuela ya existe")
    
    try:

        with DB.atomic():

            escuela = Escuela.create(nombre = nombre, logo=" ",
                                    activate=True)
            detalle_escuela = DetalleEscuela.create(
                escuela_nombre=escuela,
                clave=detalle_request.clave,
                domicilio=detalle_request.domicilio,
                localidad=detalle_request.localidad,
                zona=detalle_request.zona,
                sector=detalle_request.sector,
                telefono=detalle_request.telefono,
                activate=True
            )
            extra_escuela = ExtraEscuela.create(
                escuela_nombre=escuela,
                no_familia=extra_request.NoFamilia,
                cuota=extra_request.Cuota,
                tt_alumnos=extra_request.TTAlumnos,
                tt_grupos=extra_request.TTGrupos,
                turno=extra_request.Turno,
                activate=True
            )

    except IntegrityError as err:
        # Imprimir el mensaje de error real para depurar
        print(f"Error de integridad: {err}")
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")

    return {"mensaje": "Escuela creada exitosamente"}

async def save_logo(nombre_escuela, logoEscuela):

    query1 = Escuela.select().where(Escuela.nombre == nombre_escuela).first()

    if query1 is None:
        raise HTTPException(status_code=404, detail="Escuela no encontrada")
        
    if query1.activate==False:
        raise HTTPException(status_code=400, detail="Escuela no encontrada")

    try:

        #abre el archivo desde el directorio actual en el que estamos + el nombre del archivo y le damos los permisios de 
        #escritura y binario, y hacemos referencia como myfile
        with open(getcwd() + "/logos/" + logoEscuela.filename, "wb") as myfile:
            #leemos su contenido y lo guardo en la variable content
            content = await logoEscuela.read()
            #guardamos en myfile el contenido que leimos
            myfile.write(content)
            #cerramos el archivo
            myfile.close()

        Escuela.update(logo=logoEscuela.filename).where(Escuela.nombre == nombre_escuela).execute()

    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")
    
    return {"mensaje": "Logo guardado exitosamente"}

async def consult_escuelas(nombre_escuela):

    try:

        query1 = Escuela.select().where(Escuela.nombre == nombre_escuela).first()

        if query1 is None:
            raise HTTPException(status_code=404, detail="Escuela no encontrada")
        
        if query1.activate==False:
            raise HTTPException(status_code=400, detail="Escuela no encontrada")
        
        query2 = DetalleEscuela.select().where(DetalleEscuela.escuela_nombre == nombre_escuela).first()
        query3 = ExtraEscuela.select().where(ExtraEscuela.escuela_nombre == nombre_escuela).first()

        escuela_dict = {
            "id": query1.id,
            "nombre": query1.nombre,
            "logo": query1.logo,
            "clave": query2.clave,
            "domicilio": query2.domicilio,
            "localidad": query2.localidad,
            "zona": query2.zona,
            "sector": query2.sector,
            "telefono": query2.telefono,
            "no_familia": query3.no_familia,
            "cuota": query3.cuota,
            "tt_alumnos": query3.tt_alumnos,
            "tt_grupos": query3.tt_grupos,
            "turno": query3.turno,
        }
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Escuela no encontrada")
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, contacta al administrador.")
    return escuela_dict

async def update_school_base(nombre,nuevonombre,nuevologo):
    with DB.atomic():
        # Busca la escuela por el nombre actual
        escuela = Escuela.get(Escuela.nombre == nombre)
        
        if escuela is None:
            raise HTTPException(status_code=404, detail="Escuela no encontrada")
    
        if escuela.activate==False:
            raise HTTPException(status_code=400, detail="Escuela no encontrada")
        
        # Actualiza el nombre en DetalleEscuela y ExtraEscuela
        DetalleEscuela.update(escuela_nombre=nuevonombre).where(DetalleEscuela.escuela_nombre == nombre).execute()
        ExtraEscuela.update(escuela_nombre=nuevonombre).where(ExtraEscuela.escuela_nombre == nombre).execute()
        
        # Ahora que las claves foráneas han sido actualizadas, actualiza el nombre de la escuela
        escuela.nombre = nuevonombre
        escuela.logo = nuevologo
        escuela.save()
    return {"mensaje": "Nombre de la escuela actualizada exitosamente"}
    
async def update_school_place(school_request: DetalleEscuelaUpdate):
    query = DetalleEscuela.select().where(DetalleEscuela.escuela_nombre == school_request.escuela_nombre).first()

    if query is None:
        raise HTTPException(status_code=404, detail="Escuela no encontrada")
    
    if query.activate==False:
        raise HTTPException(status_code=400, detail="Escuela no encontrada")

    if query:

        query.clave = school_request.clave
        query.domicilio = school_request.domicilio
        query.localidad = school_request.localidad
        query.zona = school_request.zona
        query.sector = school_request.sector
        query.telefono = school_request.telefono
    
        query.save()
        return {"mensaje": "Datos de la localizacion de la escuela actualizados exitosamente"}
    
async def update_school_parents(school_request: ExtraEscueUpdate):
    query = ExtraEscuela.select().where(ExtraEscuela.escuela_nombre == school_request.escuela_nombre).first()

    if query is None:
        raise HTTPException(status_code=404, detail="Escuela no encontrada")
    
    if query.activate==False:
        raise HTTPException(status_code=400, detail="Escuela no encontrada")

    if query:

        query.no_familia = school_request.NoFamilia
        query.cuota = school_request.Cuota
        query.tt_alumnos = school_request.TTAlumnos
        query.tt_grupos = school_request.TTGrupos
        query.turno = school_request.Turno
    
        query.save()
        return {"mensaje": "Datos de los alumos de la escuela actualizados exitosamente"}
    
async def delete_school(nombre):

    query1 = Escuela.select().where(Escuela.nombre == nombre).first()

    if query1 is None:
        raise HTTPException(status_code=404, detail="Escuela no encontrada")

    query2 = DetalleEscuela.select().where(DetalleEscuela.escuela_nombre == nombre).first()
    query3 = ExtraEscuela.select().where(ExtraEscuela.escuela_nombre == nombre).first()

    query1.activate = False
    query1.save()
    query2.activate = False
    query2.save()
    query3.activate = False
    query3.save()
    
    return {"mensaje": "Escuela dada de baja exitosamente"}


async def get_tt_cuotaEsperada(school):
    query1 = ExtraEscuela.select().where(ExtraEscuela.escuela_nombre == school).first()

    if query1 is None:
        raise HTTPException(status_code=404, detail="Escuela no encontrada")
    
    total_cuota = query1.cuota * query1.tt_alumnos

    # Definir el rango de fechas para el ciclo escolar actual
    current_year = datetime.now().year
    start_date = datetime(current_year, 1, 1)
    end_date = datetime(current_year, 12, 31)

    total_recolectado = (Income
                        .select(fn.SUM(Income.amount))
                        .where(
                            (Income.school_name == school) &
                            (Income.category_id == 2) &
                            (Income.date.between(start_date, end_date))
                        ).scalar() or 0)

    school_list = {
            "total_esperado": total_cuota,
            "total_recolectado": total_recolectado,
        }

    return school_list