
DROP TABLE IF EXISTS Constantes;
DROP TABLE IF EXISTS Consultas;
DROP TABLE IF EXISTS Ingresos;
DROP TABLE IF EXISTS Episodios;
DROP TABLE IF EXISTS Citas;
DROP TABLE IF EXISTS Pacientes;
DROP TABLE IF EXISTS Administrativos;
DROP TABLE IF EXISTS Enfermeros;
DROP TABLE IF EXISTS Medicos;
DROP TABLE IF EXISTS Personal;
GO


CREATE TABLE Personal (
    id_empleado INT PRIMARY KEY IDENTITY(1,1), 
    dni VARCHAR(15) UNIQUE NOT NULL, 
    nombre VARCHAR(50), 
    apellidos VARCHAR(100), 
    nombre_usuario VARCHAR(50) UNIQUE,
    email VARCHAR(100),
    password_ VARCHAR(255),
    rol VARCHAR(20)
);

CREATE TABLE Medicos (
    id_medico INT PRIMARY KEY,
    especialidad VARCHAR(100), 
    firma VARCHAR(MAX), 
    FOREIGN KEY (id_medico) REFERENCES Personal(id_empleado)
);

CREATE TABLE Enfermeros (
    id_enfermero INT PRIMARY KEY
    FOREIGN KEY (id_enfermero) REFERENCES Personal(id_empleado)
);

CREATE TABLE Administrativos (
    id_admin INT PRIMARY KEY,
    contador_citas INT DEFAULT 0,
    FOREIGN KEY (id_admin) REFERENCES Personal(id_empleado)
);

CREATE TABLE Pacientes (
    id_paciente INT PRIMARY KEY IDENTITY(1,1), 
    nif VARCHAR(15) UNIQUE NOT NULL, 
    nombre VARCHAR(50), 
    apellido1 VARCHAR(50), 
    apellido2 VARCHAR(50), 
    fecha_nacimiento DATE, 
    genero VARCHAR(10) CHECK (genero IN ('Hombre','Mujer','Otro')),
    estado VARCHAR(20), 
    fecha_registro DATETIME DEFAULT GETDATE(),
    medico_asignado INT, 
    FOREIGN KEY (medico_asignado) REFERENCES Medicos(id_medico)
);

CREATE TABLE Citas (
    id_cita INT PRIMARY KEY IDENTITY(1,1), 
    id_medico INT, 
    id_paciente INT, 
    fecha DATE, 
    hora TIME, 
    FOREIGN KEY (id_medico) REFERENCES Medicos(id_medico),
    FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente),
    CONSTRAINT UQ_Cita UNIQUE (id_medico, fecha, hora)
);

CREATE TABLE Episodios (
    id_episodio INT PRIMARY KEY IDENTITY(1,1), 
    id_paciente INT, 
    fecha_hora_inicio DATETIME DEFAULT GETDATE(), 
    fecha_hora_fin DATETIME, 
    tipo VARCHAR(20) CHECK (tipo IN ('Consulta','Ingreso')),
    FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente)
);

CREATE TABLE Ingresos (
    id_ingreso INT PRIMARY KEY IDENTITY(1,1),
    id_episodio INT NOT NULL,
    num_habitacion VARCHAR(10), 
    dieta TEXT, 
    FOREIGN KEY (id_episodio) REFERENCES Episodios(id_episodio) 
);

CREATE TABLE Consultas (
    id_consulta INT PRIMARY KEY IDENTITY(1,1),
    id_episodio INT NOT NULL,
    diagnostico TEXT, 
    FOREIGN KEY (id_episodio) REFERENCES Episodios(id_episodio) 
);

CREATE TABLE Constantes (
    id_registro INT PRIMARY KEY IDENTITY(1,1), 
    id_episodio INT, 
    id_enfermero INT, 
    fecha DATE DEFAULT CAST(GETDATE() AS DATE), 
    hora TIME DEFAULT CAST(GETDATE() AS TIME), 
    temperatura DECIMAL(4,2),  
    tension VARCHAR(10),  
    FOREIGN KEY (id_episodio) REFERENCES Episodios(id_episodio),
    FOREIGN KEY (id_enfermero) REFERENCES Enfermeros(id_enfermero)
);
GO

---------------------------------------------------------
-- DATOS SINTÉTICOS
---------------------------------------------------------

-- PERSONAL (Médicos, Enfermeros, Admins)
INSERT INTO Personal (dni, nombre, apellidos, nombre_usuario, email, password_, rol) VALUES
('12345678A', 'Javier', 'García Fernández', 'jgarcia', 'jgarcia@clinicaleon.es', 'hash_pass_1', 'Medico'),
('23456789B', 'María', 'López González', 'mlopez', 'mlopez@clinicaleon.es', 'hash_pass_2', 'Medico'),
('34567890C', 'Sergio', 'Díez Camino', 'sdiez', 'sdiez@clinicaleon.es', 'hash_pass_3', 'Medico'),
('45678901D', 'Elena', 'Martínez Robla', 'emartinez', 'emartinez@clinicaleon.es', 'hash_pass_4', 'Enfermero'),
('56789012E', 'Pablo', 'Gutiérrez Tascón', 'pgutierrez', 'pgutierrez@clinicaleon.es', 'hash_pass_5', 'Enfermero'),
('67890123F', 'Lucía', 'Blanco Villadangos', 'lblanco', 'lblanco@clinicaleon.es', 'hash_pass_6', 'Administrativo');

-- MEDICOS (IDs corresponden a Personal)
INSERT INTO Medicos (id_medico, especialidad, firma) VALUES
(1, 'Medicina Interna', 'Firma_Digital_JGF'),
(2, 'Traumatología', 'Firma_Digital_MLG'),
(3, 'Cardiología', 'Firma_Digital_SDC');

-- ENFERMEROS
INSERT INTO Enfermeros (id_enfermero) VALUES (4), (5);

-- ADMINISTRATIVOS
INSERT INTO Administrativos (id_admin, contador_citas) VALUES (6, 0);

INSERT INTO Pacientes (nif, nombre, apellido1, apellido2, fecha_nacimiento, genero, estado, medico_asignado) VALUES
('71400111X', 'Manuel', 'Álvarez', 'Cimadevilla', '1955-05-12', 'Hombre', 'Activo', 1),
('71422333Y', 'Carmen', 'Mera', 'Getino', '1982-10-20', 'Mujer', 'Activo', 2),
('71555666Z', 'Roberto', 'Ferrero', 'Pola', '1990-02-15', 'Hombre', 'Activo', 3),
('71666777K', 'Sara', 'García', 'Del Egido', '1978-08-05', 'Mujer', 'Inactivo', 1),
('71888999J', 'Begoña', 'Orejas', 'Lorenzana', '1962-12-30', 'Mujer', 'Activo', 2);


-- CITAS
INSERT INTO Citas (id_medico, id_paciente, fecha, hora) VALUES
(1, 1, '2024-03-10', '09:00:00'),
(2, 2, '2024-03-10', '10:30:00'),
(3, 3, '2024-03-11', '11:00:00'),
(1, 5, '2024-03-12', '12:00:00');

-- EPISODIOS (Ingresos o Consultas)
INSERT INTO Episodios (id_paciente, fecha_hora_inicio, tipo) VALUES
(1, '2024-03-10 09:05:00', 'Consulta'),
(2, '2024-03-10 10:45:00', 'Ingreso'),
(3, '2024-03-11 11:15:00', 'Consulta'),
(5, '2024-03-12 12:10:00', 'Consulta');


-- CONSULTAS (Relacionadas con Episodios 1, 3 y 4)
INSERT INTO Consultas (id_episodio, diagnostico) VALUES
(1, 'Resfriado común con congestión nasal severa. Se receta reposo.'),
(3, 'Arritmia leve detectada. Se solicita ECG de esfuerzo.'),
(4, 'Control rutinario post-operatorio. Evolución favorable.');

-- INGRESOS (Relacionado con Episodio 2)
INSERT INTO Ingresos (id_episodio, num_habitacion, dieta) VALUES
(2, 'H-204', 'Dieta blanda post-quirúrgica, baja en sodio.');

-- CONSTANTES (Tomadas por los enfermeros durante los episodios)
INSERT INTO Constantes (id_episodio, id_enfermero, fecha, hora, temperatura, tension) VALUES
(1, 4, '2024-03-10', '09:10:00', 37.5, '120/80'),
(2, 5, '2024-03-10', '11:00:00', 36.8, '115/75'),
(2, 5, '2024-03-10', '18:00:00', 38.2, '130/85'), 
(3, 4, '2024-03-11', '11:20:00', 36.6, '145/95'); 



SELECT 
    p.id_empleado 'ID',
    p.dni 'DNI',
    p.nombre 'Nombre',
    p.apellidos 'Apellidos',
    p.nombre_usuario 'Nombre usuario',
    p.email 'Mail',
    m.especialidad 'Especialidad',
    m.firma 'Firma'
FROM Personal p
INNER JOIN Medicos m ON p.id_empleado = m.id_medico;

SELECT *from  episodios