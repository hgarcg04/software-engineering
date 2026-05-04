from src.modelo.VO.LoginVO import LoginVO
from src.vista.LogicaEnfermeros import VentanaEnfermeros
from src.vista.LogicaMedicos import VentanaMedico
from src.vista.LogicaAdministrativos import VentanaAdministrativos
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.Logica import Logica
from src.controlador.ControladorEnfermeros import ControladorEnfermeros
from src.controlador.ControladorAdministrativos import ControladorAdministrativos
from src.controlador.ControladorMedicos import ControladorMedicos


class ControladorPrincipal:

    def __init__(self, ref_vista, ref_modelo):
        self._vista = ref_vista
        self._modelo = ref_modelo
        self.usuario_actualVO = None
    
    def ventanaInciarSesion(self):

        self._vista.showMaximized()
        self._vista.show()
    
    
    
    def comprobarLogin(self, texto_nombre, texto_password):
        loginVO = LoginVO(texto_nombre, texto_password)

        self.usuario_actualVO =  self._modelo.comprobarLogin(loginVO) # Objeto UserVO
                

        if self.usuario_actualVO is None:
            print("Usuario y/o contraseña incorrectos.")
        
        elif self.usuario_actualVO.rol == 'enfermero':
            self._ventana_enfermero = VentanaEnfermeros()
            
            self._ventana_enfermero.showMaximized()
            self._ventana_enfermero.show()

            self._vista.cerrar()

            # señal para cerrar sesion y volver al login
            self._ventana_enfermero.signal_logout.connect(self.volver_al_login)

           
            modelo = Logica()
            controlador = ControladorEnfermeros(self._ventana_enfermero, modelo, self.usuario_actualVO)
            self._ventana_enfermero.controlador = controlador

        elif self.usuario_actualVO.rol == 'medico': #Comprobar minuscula o mayuscula
            self._ventana_medico = VentanaMedico()

            # self._ventana_medico.showFullScreen() # esto abre la ventana en pantalla completa. (ache y manu, si os molesta comentarlo y
                                                    # lo descomentamos el dia de la presentación)
            self._ventana_medico.showMaximized()
            self._ventana_medico.show()
            self._vista.cerrar()

            self._ventana_medico.signal_logout.connect(self.volver_al_login)

            modelo = Logica()
            controlador = ControladorMedicos(self._ventana_medico, modelo, self.usuario_actualVO)
            self._ventana_medico.controlador = controlador

        elif self.usuario_actualVO.rol == 'administrativo': #Comprobar minuscula o mayuscula
            self._ventana_administrativo = VentanaAdministrativos()
            #self._ventana_administrativo.showFullScreen() # esto abre la ventana en pantalla completa. (ache y manu, si os molesta comentarlo y
                                                          # lo descomentamos el dia de la presentación)
            self._ventana_administrativo.showMaximized()
            self._ventana_administrativo.show()
            self._vista.cerrar()

            self._ventana_administrativo.signal_logout.connect(self.volver_al_login)

            modelo = Logica()
            controlador = ControladorAdministrativos(self._ventana_administrativo, modelo, self.usuario_actualVO)
            self._ventana_administrativo.controlador = controlador
            
        else:
            print(f"Login correcto. Bienvenido/a, {self.usuario_actualVO.nombre} (ID: {self.usuario_actualVO.id_empleado}). Rol: {self.usuario_actualVO.rol}")

            self._vista.cerrar()

    def volver_al_login(self):
        self.usuario_actualVO = None
        
        self._vista.limpiar_campos()

        self._vista.show() 
        print("Sesión cerrada correctamente.")
