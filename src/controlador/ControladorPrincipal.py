from src.modelo.VO.LoginVO import LoginVO
from src.vista.LogicaEnfermeros import VentanaEnfermeros
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.Logica import Logica
from src.controlador.ControladorEnfermeros import ControladorEnfermeros

class ControladorPrincipal:

    def __init__(self, ref_vista, ref_modelo):
        self._vista = ref_vista
        self._modelo = ref_modelo
    
    def ventanaInciarSesion(self):
        self._vista.show()
    
    def comprobarLogin(self, loginVO):
        UserVO =  self._modelo.comprobarLogin(loginVO)
                
        # este bloque, en vez de imprimir por terminal, debería abrir una ventana nueva, o bien 
        # mostras un mensaje de error

        if UserVO is None:
            print("Usuario y/o contraseña incorrectos.")
        
        elif UserVO.rol == 'Enfermero':
            print(f"Enfermero/a {UserVO.nombre} {UserVO.apellidos} ha inciado sesión.")
            self._ventana_enfermero = VentanaEnfermeros()

            self._ventana_enfermero.lbl_user_name.setText(f"Enfermero/a: {UserVO.nombre} {UserVO.apellidos}")
            self._ventana_enfermero.show()
            self._vista.cerrar()

            
            modelo = Logica()
            controlador = ControladorEnfermeros(self._ventana_enfermero, modelo)

            self._ventana_enfermero.controlador = controlador
            

            
        else:
            print(f"Login correcto. Bienvenido/a, {UserVO.nombre} (ID: {UserVO.id_empleado}). Rol: {UserVO.rol}")

            self._vista.cerrar()


