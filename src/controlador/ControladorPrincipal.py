from src.modelo.VO.LoginVO import LoginVO

class ControladorPrincipal:

    def __init__(self, ref_vista, ref_modelo):
        self._vista = ref_vista
        self._modelo = ref_modelo
    
    def ventanaInciarSesion(self):
        self._vista.show()
        self._modelo.ejemploSelect()
    
    def comprobarLogin(self, nombre, passw):
        login = LoginVO(nombre, passw)
        resultado = self._modelo.consultarLogin(login)

        if resultado is None:
            print("No existe")
            
        else:
            self._vista.close()
            # falta abrir otro objeto vista con la nueva ventana