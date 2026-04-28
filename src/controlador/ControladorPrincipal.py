from src.modelo.VO.LoginVO import LoginVO
from src.vista.LogicaEnfermeros import VentanaEnfermeros
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.Logica import Logica
from src.controlador.ControladorEnfermeros import ControladorEnfermeros

class ControladorPrincipal:

    def __init__(self, ref_vista, ref_modelo):
        self._vista = ref_vista
        self._modelo = ref_modelo
        self.usuario_actualVO = None
    
    def ventanaInciarSesion(self):
        self._vista.show()
    
    
    
    def comprobarLogin(self, loginVO):
        self.usuario_actualVO =  self._modelo.comprobarLogin(loginVO) # Objeto UserVO
                

        if self.usuario_actualVO is None:
            print("Usuario y/o contraseña incorrectos.")
        
        elif self.usuario_actualVO.rol == 'enfermero':
            self._ventana_enfermero = VentanaEnfermeros()
            self._ventana_enfermero.show()
            self._vista.cerrar()

            # señal para cerrar sesion y volver al login
            self._ventana_enfermero.signal_logout.connect(self.volver_al_login)

           
            modelo = Logica()
            controlador = ControladorEnfermeros(self._ventana_enfermero, modelo, self.usuario_actualVO)
            self._ventana_enfermero.controlador = controlador
            

        # Falta implementar los otros dos usuarios
        else:
            print(f"Login correcto. Bienvenido/a, {self.usuario_actualVO.nombre} (ID: {self.usuario_actualVO.id_empleado}). Rol: {self.usuario_actualVO.rol}")

            self._vista.cerrar()

    def volver_al_login(self):
        self.usuario_actualVO = None
        
        self._vista.limpiar_campos()

        self._vista.show() 
        print("Sesión cerrada correctamente.")
