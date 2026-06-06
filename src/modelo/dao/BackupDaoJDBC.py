import os
import shutil
from datetime import datetime
from src.modelo.Conexion.Conexion import Conexion


class BackupDaoJDBC(Conexion):
    """
    DAO responsable de ejecutar la copia de seguridad.
    Dos operaciones posibles según el tipo elegido:
      - 'completa': backup de BD + copia del archivo de log
      - 'bd':       solo backup de BD

    Estrategia de escritura:
      SQL Server solo puede escribir en rutas accesibles por su cuenta de servicio.
      Por eso el .bak se genera primero en la carpeta por defecto de backups de SQL
      Server (donde siempre tiene permisos) y luego Python lo mueve al directorio
      elegido por el usuario.
    """

    SQL_BACKUP_BD = (
        "BACKUP DATABASE [{database}] TO DISK = N'{ruta_tmp}'"
        " WITH FORMAT, INIT, NAME = N'KURA-Full'"
    )

    SQL_DEFAULT_BACKUP_DIR = "SELECT SERVERPROPERTY('InstanceDefaultBackupPath')"

    SQL_HISTORIAL = """
        SELECT TOP 20
            fecha, hora, tipo, tamanio_kb, realizado_por
        FROM BackupHistorial
        ORDER BY fecha DESC, hora DESC
    """

    SQL_INSERTAR_HISTORIAL = """
        INSERT INTO BackupHistorial (fecha, hora, tipo, tamanio_kb, realizado_por)
        VALUES (?, ?, ?, ?, ?)
    """

    def _obtener_dir_backup_sqlserver(self, cursor):
        """Devuelve la carpeta de backups por defecto de la instancia SQL Server."""
        try:
            cursor.execute(self.SQL_DEFAULT_BACKUP_DIR)
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception as e:
            print(f"BackupDaoJDBC: no se pudo obtener la ruta por defecto: {e}")
        # Fallback: carpeta temporal del sistema, donde cualquier proceso puede escribir
        return os.environ.get('TEMP', os.path.expanduser('~'))

    def realizar_backup(self, ruta_destino, tipo, user_vo):
        """
        Ejecuta la copia de seguridad y registra el resultado en BackupHistorial.

        Parámetros
        ----------
        ruta_destino : str   — directorio elegido por el administrativo
        tipo         : str   — 'completa' | 'bd'
        user_vo      : UserVO

        Retorna
        -------
        (exito: bool, mensaje: str, tamanio_kb: int)
        """
        ahora = datetime.now()
        timestamp = ahora.strftime('%Y%m%d_%H%M%S')
        fecha_str = ahora.strftime('%Y-%m-%d')
        hora_str  = ahora.strftime('%H:%M:%S')
        nombre_bak = f"KURA_backup_{timestamp}.bak"

        cursor = self.getCursor()

        # ── 1. Determinar ruta temporal donde SQL Server SÍ puede escribir ───
        dir_tmp   = self._obtener_dir_backup_sqlserver(cursor)
        ruta_tmp  = os.path.join(dir_tmp, nombre_bak)

        # ── 2. Ejecutar BACKUP DATABASE hacia la ruta temporal ────────────────
        try:
            sql = self.SQL_BACKUP_BD.format(
                database = self._database,
                ruta_tmp = ruta_tmp.replace("'", "''")   # escapar comillas simples
            )
            cursor.execute(sql)
            try:
                cursor.fetchall()
            except Exception:
                pass
        except Exception as e:
            return False, f"Error al generar el backup de base de datos: {e}", 0

        # ── 3. Copiar el .bak al directorio elegido por el usuario ───────────
        # Usamos copy2 en lugar de move: SQL Server mantiene el archivo bloqueado
        # con sus propios permisos, pero sí permite leerlo/copiarlo.
        ruta_final = os.path.join(ruta_destino, nombre_bak)
        try:
            shutil.copy2(ruta_tmp, ruta_final)
        except Exception as e:
            return False, (
                f"El backup se generó en '{ruta_tmp}' pero no se pudo copiar "
                f"al destino seleccionado: {e}"
            ), 0

        # Intentar borrar el temporal; si no se puede, no es crítico
        try:
            os.remove(ruta_tmp)
        except Exception:
            pass

        # ── 4. Copia del archivo de log (solo en modo completa) ───────────────
        if tipo == 'completa':
            try:
                ruta_log_origen = os.path.normpath(
                    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'kura_actividad.log')
                )
                if os.path.exists(ruta_log_origen):
                    nombre_log = f"KURA_log_{timestamp}.log"
                    shutil.copy2(ruta_log_origen, os.path.join(ruta_destino, nombre_log))
            except Exception as e:
                print(f"BackupDaoJDBC: no se pudo copiar el log de actividad: {e}")

        # ── 5. Calcular tamaño ────────────────────────────────────────────────
        tamanio_kb = 0
        try:
            if os.path.exists(ruta_final):
                tamanio_kb = os.path.getsize(ruta_final) // 1024
        except Exception:
            pass

        # ── 6. Registrar en historial ─────────────────────────────────────────
        tipo_legible = "Completa" if tipo == 'completa' else "Solo BD"
        nombre_usuario = f"{user_vo.nombre} {user_vo.apellidos}"
        try:
            cursor.execute(self.SQL_INSERTAR_HISTORIAL,
                           (fecha_str, hora_str, tipo_legible, tamanio_kb, nombre_usuario))
            self.conexion.commit()
        except Exception as e:
            print(f"BackupDaoJDBC: no se pudo registrar en historial: {e}")

        return True, f"Copia de seguridad completada: {nombre_bak}", tamanio_kb

    def obtener_historial(self):
        """
        Devuelve las últimas 20 entradas del historial de copias.
        Cada fila: (fecha, hora, tipo, tamanio_kb, realizado_por)
        """
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_HISTORIAL)
            return cursor.fetchall()
        except Exception as e:
            print(f"BackupDaoJDBC: error obteniendo historial: {e}")
            return []

    def comprobar_espacio(self, ruta_destino):
        """
        Comprueba si hay espacio suficiente en el destino.
        Retorna (hay_espacio: bool, libre_kb: int, necesario_kb: int)
        """
        cursor = self.getCursor()
        try:
            cursor.execute("""
                SELECT SUM(size) * 8
                FROM sys.database_files
                WHERE type_desc = 'ROWS'
            """)
            row = cursor.fetchone()
            necesario_kb = int(row[0]) if row and row[0] else 0
        except Exception:
            necesario_kb = 0

        try:
            libre_kb = shutil.disk_usage(ruta_destino).free // 1024
        except Exception:
            libre_kb = necesario_kb + 1

        return libre_kb >= necesario_kb, libre_kb, necesario_kb