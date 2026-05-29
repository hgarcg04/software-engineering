import os
from datetime import datetime


class SingletonLog:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self._ruta = os.path.join(
            os.path.dirname(__file__), '..', '..', 'kura_actividad.log'
        )

    def registrar_login_correcto(self, user_vo):
        self._escribir('LOGIN ', user_vo)

    def registrar_login_incorrecto(self, loginVO):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        linea = (
            f"[{timestamp}] LOGIN INCORRECTO | "
            f"usuario_probado={loginVO.nombre}\n"
        )

    def registrar_logout(self, user_vo):
        self._escribir('LOGOUT', user_vo)

    def _escribir(self, evento, user_vo):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        linea = (
            f"[{timestamp}] {evento} | "
            f"id={user_vo.id_empleado} | "
            f"usuario={user_vo.nombre} {user_vo.apellidos} | "
            f"rol={user_vo.rol}\n"
        )
        try:
            with open(self._ruta, 'a', encoding='utf-8') as f:
                f.write(linea)
                print(linea)
        except Exception as e:
            print(f"[Logger] Error escribiendo log: {e}")