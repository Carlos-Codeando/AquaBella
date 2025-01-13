# database.py
import sqlite3
from datetime import datetime
from tkinter import messagebox
from threading import Lock

class DatabaseManager:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance.connection = None
        return cls._instance
    
    def __init__(self):
        if self.connection is None:
            try:
                self.connection = sqlite3.connect('spa_database.db', check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al inicializar la base de datos: {str(e)}")
                raise

    def get_connection(self):
        return self.connection
    
    def get_cursor(self):
        return self.connection.cursor()
    
    def commit(self):
        self.connection.commit()
        
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_database(self):
        cursor = self.get_cursor()

        # Crear tabla de pacientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                sexo TEXT NOT NULL,
                fecha_nacimiento DATE NOT NULL,
                edad INTEGER NOT NULL,
                telefono TEXT NOT NULL,
                correo TEXT
            )
        ''')
        
        # Crear tabla de asistentes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asistentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT NOT NULL
            )
        ''')
        
        # Tabla de tratamientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tratamientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                costo REAL NOT NULL,
                es_promocion BOOLEAN
            )
        ''')
        
        # Tabla de tratamientos asignados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tratamientos_asignados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                tratamiento_id INTEGER,
                asistente_id INTEGER,
                vendedor_id INTEGER NULL,
                porcentaje_asistente REAL NOT NULL,
                porcentaje_vendedor REAL NULL,
                sesiones_asignadas INTEGER NOT NULL,
                sesiones_pagadas INTEGER NOT NULL,
                sesiones_restantes INTEGER NOT NULL,
                costo_total REAL NOT NULL,
                total_pagado REAL NOT NULL,
                saldo_pendiente REAL NOT NULL,
                comision_vendedor REAL NULL,    
                comision_asistente REAL NULL,  
                fecha_asignacion DATE NOT NULL,
                fecha_primera_sesion DATE NOT NULL,
                estado TEXT,
                es_promocion BOOLEAN,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (tratamiento_id) REFERENCES tratamientos (id),
                FOREIGN KEY (asistente_id) REFERENCES asistentes (id),
                FOREIGN KEY (vendedor_id) REFERENCES asistentes (id)
            )
        ''')
        
        # Tabla de sesiones realizadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sesiones_realizadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tratamiento_asignado_id INTEGER,
                fecha_sesion DATE NOT NULL,
                numero_sesion INTEGER NOT NULL,
                proxima_cita DATE,
                monto_abonado REAL,
                estado_sesion TEXT,
                asistente_id INTEGER, 
                estado_pago TEXT,
                porcentaje_asistente REAL,
                nombre_componente TEXT,
                comision_sumada BOOLEAN DEFAULT 0,
                realizada BOOLEAN DEFAULT 0, 
                FOREIGN KEY (tratamiento_asignado_id) REFERENCES tratamientos_asignados (id)
            )
        ''')
        
        # Resto de las tablas...
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promocion_componentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tratamiento_asignado_id INTEGER,  
                tratamiento_id INTEGER,
                sesiones_asignadas INTEGER NOT NULL,
                sesiones_restantes INTEGER NOT NULL,
                FOREIGN KEY (tratamiento_asignado_id) REFERENCES tratamientos_asignados (id),
                FOREIGN KEY (tratamiento_id) REFERENCES tratamientos (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promocion_detalles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                promocion_id INTEGER NOT NULL,
                nombre_componente TEXT NOT NULL,
                cantidad_sesiones INTEGER NOT NULL,
                precio_componente REAL NOT NULL,
                FOREIGN KEY (promocion_id) REFERENCES tratamientos (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos_asistentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asistente_id INTEGER NOT NULL,
                tratamiento_asignado_id INTEGER NOT NULL,
                sesion_id INTEGER,
                monto REAL NOT NULL,
                fecha_pago DATE NOT NULL,
                detalle TEXT,  
                tipo_comision TEXT NOT NULL,
                FOREIGN KEY (asistente_id) REFERENCES asistentes (id),
                FOREIGN KEY (tratamiento_asignado_id) REFERENCES tratamientos_asignados (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sesion_id INTEGER NOT NULL,
                monto REAL NOT NULL,
                fecha_pago DATE NOT NULL,
                FOREIGN KEY (sesion_id) REFERENCES sesiones_realizadas (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reportes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                concepto TEXT NOT NULL,
                ingreso REAL DEFAULT 0,
                egreso REAL DEFAULT 0,
                detalle TEXT
            )
        ''')
        
        self.commit()

    def execute_query(self, query, params=(), fetch=False):
        try:
            cursor = self.get_cursor()
            cursor.execute(query, params)
            result = cursor.fetchall() if fetch else None
            self.commit()
            return result
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", f"Error: {e}")
            return None

    def obtener_id_asistente_por_nombre(self, nombre_asistente):
        try:
            cursor = self.get_cursor()
            cursor.execute("SELECT id FROM asistentes WHERE nombre = ?", (nombre_asistente,))
            id_asistente = cursor.fetchone()
            return id_asistente[0] if id_asistente else None
        except sqlite3.Error as e:
            print(f"Error al obtener ID del asistente: {e}")
            return None

# Crear una instancia global del DatabaseManager
db = DatabaseManager()

# Funciones wrapper para mantener la compatibilidad con el código existente
def create_database():
    db.create_database()

def execute_query(query, params=(), fetch=False):
    return db.execute_query(query, params, fetch)

def obtener_id_asistente_por_nombre(nombre_asistente):
    return db.obtener_id_asistente_por_nombre(nombre_asistente)