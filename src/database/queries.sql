-- PERSONAL
CREATE TABLE Personal (
    id_empleado INT PRIMARY KEY, 
    dni VARCHAR(15) UNIQUE NOT NULL, 
    nombre VARCHAR(50) NOT NULL, 
    apellidos VARCHAR(100) NOT NULL, 
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL, 
    email VARCHAR(100),
    password_ VARCHAR(255) NOT NULL, 
    estado_cuenta VARCHAR(20), 
    rol VARCHAR(20) NOT NULL 
);

CREATE TABLE Medicos (
    id_medico INT PRIMARY KEY, 
    especialidad VARCHAR(100), 
    firma TEXT, 
    FOREIGN KEY (id_medico) REFERENCES Personal(id_empleado) 
);

CREATE TABLE Enfermeros (
    id_enfermero INT PRIMARY KEY, 
    FOREIGN KEY (id_enfermero) REFERENCES Personal(id_empleado) 
);

CREATE TABLE Administrativos (
    id_admin INT PRIMARY KEY, 
    contador_citas INT DEFAULT 0, 
    FOREIGN KEY (id_admin) REFERENCES Personal(id_empleado) 
);

-- PACIENTES
CREATE TABLE Pacientes (
    id_paciente INT PRIMARY KEY, 
    nif VARCHAR(15) UNIQUE NOT NULL, 
    nombre VARCHAR(50), 
    apellido1 VARCHAR(50), 
    apellido2 VARCHAR(50), 
    fecha_nacimiento DATE, 
    genero VARCHAR(10), 
    estado VARCHAR(20), 
    fecha_registro DATETIME, 
    telefono VARCHAR(20), 
    direccion TEXT, 
    email VARCHAR(100), 
    contacto_emergencia VARCHAR(100),
    alergias TEXT, 
    grupo_sangre VARCHAR(5), 
    medico_asignado INT, 
    FOREIGN KEY (medico_asignado) REFERENCES Medicos(id_medico)
);

-- CITAS
CREATE TABLE Citas (
    id_cita INT PRIMARY KEY, 
    id_empleado INT, 
    id_paciente INT, 
    fecha DATE, 
    hora TIME, 
    FOREIGN KEY (id_empleado) REFERENCES Medicos(id_medico),
    FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente)
);

-- HISTORIAL CLÍNICO DIGITAL
CREATE TABLE Episodios (
    id_episodio INT PRIMARY KEY, 
    id_paciente INT, 
    fecha_hora_inicio DATETIME, 
    fecha_hora_fin DATETIME, 
    tipo VARCHAR(20),
    FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente)
);

CREATE TABLE Ingresos (
    id_ingreso INT PRIMARY KEY,
    num_habitacion VARCHAR(10), 
    dieta TEXT, 
    FOREIGN KEY (id_ingreso) REFERENCES Episodios(id_episodio) 
);

CREATE TABLE Consultas (
    id_consulta INT PRIMARY KEY,
    diagnostico TEXT, 
    FOREIGN KEY (id_consulta) REFERENCES Episodios(id_episodio) 
);

-- CONSTANTES VITALES
CREATE TABLE Constantes (
    id_registro INT PRIMARY KEY, 
    id_episodio INT, 
    id_enfermero INT, 
    fecha DATE, 
    hora TIME, 
    temperatura DECIMAL(4,2),  
    tension VARCHAR(10),  
    FOREIGN KEY (id_episodio) REFERENCES Episodios(id_episodio),
    FOREIGN KEY (id_enfermero) REFERENCES Enfermeros(id_enfermero)
);