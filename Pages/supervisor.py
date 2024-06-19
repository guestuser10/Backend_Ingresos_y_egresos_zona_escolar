from database import Supervisor, DB

from fastapi import HTTPException

async def get_sup(id):
    
    sup_info = Supervisor.get_by_id(id)

    # Construir la lista de usuarios con su información y rol
    sup_info_list = [{
        "id": sup_info.id,
        "username": sup_info.username,
        "password": sup_info.password,
        "rol": sup_info.rol,
        "name": sup_info.name,
        "estado": sup_info.estado,

    }]

    return sup_info_list


async def update_sup(name, sup_request):

    if not Supervisor.select().where(Supervisor.name == name).exists():
        raise HTTPException(status_code=400, detail="Datos incorrectos o inexistentes")
    
    with DB.atomic():
        
        sup = Supervisor.get(Supervisor.name == name)
        
        username = sup_request.username
        password = sup_request.password
        name = sup_request.name
        estado = sup_request.estado
        
        sup.username    = username
        sup.password    = password
        sup.name        = name
        sup.estado      = estado
        sup.save()

    
    return {"mensaje": "El supervisor se ha actualizado exitosamente"}