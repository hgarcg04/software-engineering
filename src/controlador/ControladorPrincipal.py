from src.modelo.VO.LoginVO import LoginVO
from src.vista.Enfermeros.LogicaEnfermeros import VentanaEnfermeros
from src.vista.LogicaMedicos import VentanaMedico
from src.vista.Administrativos.LogicaAdministrativos import VentanaAdministrativos
from src.modelo.Logica import Logica
from src.controlador.ControladorEnfermeros import ControladorEnfermeros
from src.controlador.ControladorAdministrativos import ControladorAdministrativos
from src.controlador.ControladorMedicos import ControladorMedicos
from src.modelo.SingletonLog import SingletonLog


class ControladorPrincipal:

    def __init__(self, ref_vista, ref_modelo):
        self._vista = ref_vista
        self._modelo = ref_modelo
        self.usuario_actualVO = None
        self._logger = SingletonLog()
    
    def ventanaInciarSesion(self):

        self._vista.showMaximized()
        self._vista.show()
    
    def verificar_credenciales(self, usuario, password):
        loginVO = LoginVO(usuario, password)
        return self._modelo.comprobarLogin(loginVO)  # devuelve userVO o None
    
    
    def comprobarLogin(self, texto_nombre, texto_password):
        loginVO = LoginVO(texto_nombre, texto_password)
        self.usuario_actualVO =  self._modelo.comprobarLogin(loginVO) # Objeto UserVO


                

        if self.usuario_actualVO is None:
            self._logger.registrar_login_incorrecto(loginVO)
            print("Usuario y/o contraseña incorrectos.")

            self._vista.lanzar_warning()

            self._vista.limpiar_campos()
            self._vista.show()
            return

        if self.usuario_actualVO.estado == 0:  # primer login
            self._vista.abrir_cambio_contrasena()
            return

        
        elif self.usuario_actualVO.rol == 'enfermero':
            self._logger.registrar_login_correcto(self.usuario_actualVO)
            self._ventana_enfermero = VentanaEnfermeros()
            
            self._ventana_enfermero.showMaximized()
            self._ventana_enfermero.show()

            self._vista.cerrar()

            # señal para cerrar sesion y volver al login
            self._ventana_enfermero.signal_logout.connect(self.volver_al_login)

           

            controlador = ControladorEnfermeros(self._ventana_enfermero, self._modelo, self.usuario_actualVO, self)
            self._ventana_enfermero.controlador = controlador

        elif self.usuario_actualVO.rol == 'medico': #Comprobar minuscula o mayuscula
            self._logger.registrar_login_correcto(self.usuario_actualVO)
            self._ventana_medico = VentanaMedico()

            # self._ventana_medico.showFullScreen() # esto abre la ventana en pantalla completa. (ache y manu, si os molesta comentarlo y
                                                    # lo descomentamos el dia de la presentación)
            self._ventana_medico.showMaximized()
            self._ventana_medico.show()
            self._vista.cerrar()

            self._ventana_medico.signal_logout.connect(self.volver_al_login)


            controlador = ControladorMedicos(self._ventana_medico, self._modelo, self.usuario_actualVO, self)
            self._ventana_medico.controlador = controlador

        elif self.usuario_actualVO.rol == 'administrativo': #Comprobar minuscula o mayuscula
            self._logger.registrar_login_correcto(self.usuario_actualVO)
            self._ventana_administrativo = VentanaAdministrativos()
            #self._ventana_administrativo.showFullScreen() # esto abre la ventana en pantalla completa. (ache y manu, si os molesta comentarlo y
                                                          # lo descomentamos el dia de la presentación)
            self._ventana_administrativo.showMaximized()
            self._ventana_administrativo.show()
            self._vista.cerrar()

            self._ventana_administrativo.signal_logout.connect(self.volver_al_login)


            controlador = ControladorAdministrativos(self._ventana_administrativo, self._modelo, self.usuario_actualVO)
            self._ventana_administrativo.controlador = controlador



    def volver_al_login(self):
        self._logger.registrar_logout(self.usuario_actualVO)
        self.usuario_actualVO = None
        
        self._vista.limpiar_campos()

        self._vista.show()

    def cambiar_password(self, nueva, userVO):
        self._modelo.cambiarPassword(nueva, userVO)
        self._modelo.activarUsuario(userVO)