from src.modelo.VO.LoginVO import LoginVO


class ControladorPrincipal:

    def __init__(self, ref_vista, ref_modelo):
        self._vista = ref_vista
        self._modelo = ref_modelo
    
    def ventanaInciarSesion(self):
        self._vista.show()
    
    def comprobarLogin(self, loginVO):
        UserVO =  self._modelo.comprobarLogin(loginVO) # esto es el UserVO
                
        # este bloque, en vez de imprimir por terminal, debería abrir una ventana nueva, o bien 
        # mostras un mensaje de error

        if UserVO is None:
            print("Usuario y/o contraseña incorrectos.")
            
        else:
            print(f"Login correcto. Bienvenido/a, {UserVO.nombre} (ID: {UserVO.id_empleado}). Rol: {UserVO.rol}")

            self._vista.cerrar()


