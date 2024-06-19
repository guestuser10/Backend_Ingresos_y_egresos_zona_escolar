from fastapi import HTTPException
from database import User, User_Info, Supervisor


async def login(username, password):

    try:

        sup_info = Supervisor.get_or_none((Supervisor.username == username) & (Supervisor.password == password))
        user = User.get_or_none((User.username == username) & (User.password == password))
        
        if sup_info == None:
            pass
        
        else:
            
            sup_list = [{
                
                "id": sup_info.id,
                "rol": sup_info.rol
                
            }]
            
            return sup_list
        
        if user == None:
            pass
        
        else:
            
            user_info = User_Info.select().where(User_Info.user_id == user.id)
            user_info_list = [{

                "id": user.id,
                "rol": user.rol,
                "escuela": user_i.escuela,

            } for user_i in user_info]
            
            return user_info_list
        
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    except User.DoesNotExist as e:
        raise HTTPException(status_code=404, detail=f"El usuario: '{user.username}' no fue encontrado")