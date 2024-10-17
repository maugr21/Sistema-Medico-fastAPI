CREATE TABLE `Paciente` (
  `Id_paciente` INT PRIMARY KEY AUTO_INCREMENT,
  `Nombre_paciente` VARCHAR(100),
  `Apellidos_paciente` VARCHAR(100),
  `CURP_paciente` VARCHAR(18),
  `Fecha_Nacimiento_paciente` DATE,
  `Email_paciente` VARCHAR(100),
  `Password_paciente` VARCHAR(100),
  `Pad_cronicos_paciente` TEXT
);

CREATE TABLE `Medico` (
  `Id_medico` INT PRIMARY KEY AUTO_INCREMENT,
  `Nombres_medico` VARCHAR(100),
  `Apellidos_medico` VARCHAR(100),
  `Cedula_Profesional` VARCHAR(20),
  `Especialidad` VARCHAR(50),
  `CURP_medico` VARCHAR(18),
  `Experiencia_medico` TEXT
);

CREATE TABLE `Hospital_Clinica` (
  `Id_hospital` INT PRIMARY KEY AUTO_INCREMENT,
  `Nombre_hospital` VARCHAR(100),
  `Direccion` VARCHAR(200)
);

CREATE TABLE `Medicos_Hospital` (
  `Id_medico` INT,
  `Id_hospital` INT
);

CREATE TABLE `Cita_Medica` (
  `Id_cita` INT PRIMARY KEY AUTO_INCREMENT,
  `Id_paciente` INT,
  `Id_medico` INT,
  `Fecha_cita` DATETIME,
  `Costo_cita` DECIMAL(10,2),
  `Id_hospital` INT,
  `Confirm_cita` BOOLEAN
);

CREATE TABLE `Exp_Clinico_Paciente` (
  `Id_expediente` INT PRIMARY KEY AUTO_INCREMENT,
  `Id_paciente` INT,
  `Id_medico` INT,
  `Anotaciones_nuevas_paciente` TEXT,
  `Fecha_Cita` DATETIME
);

CREATE TABLE `Rec_Medica_Paciente` (
  `Id_receta` INT PRIMARY KEY AUTO_INCREMENT,
  `Id_paciente` INT,
  `Id_medico` INT,
  `Anotaciones_receta_paciente` TEXT,
  `Fecha_Cita` DATETIME
);

CREATE TABLE `Historial_Citas` (
  `Id_historial` INT PRIMARY KEY AUTO_INCREMENT,
  `Id_cita` INT,
  `Estado_cita` VARCHAR(20),
  `Fecha_actualizacion_estado` DATETIME
);

ALTER TABLE `Medicos_Hospital` ADD FOREIGN KEY (`Id_medico`) REFERENCES `Medico` (`Id_medico`);

ALTER TABLE `Medicos_Hospital` ADD FOREIGN KEY (`Id_hospital`) REFERENCES `Hospital_Clinica` (`Id_hospital`);

ALTER TABLE `Cita_Medica` ADD FOREIGN KEY (`Id_paciente`) REFERENCES `Paciente` (`Id_paciente`);

ALTER TABLE `Cita_Medica` ADD FOREIGN KEY (`Id_medico`) REFERENCES `Medico` (`Id_medico`);

ALTER TABLE `Cita_Medica` ADD FOREIGN KEY (`Id_hospital`) REFERENCES `Hospital_Clinica` (`Id_hospital`);

ALTER TABLE `Exp_Clinico_Paciente` ADD FOREIGN KEY (`Id_paciente`) REFERENCES `Paciente` (`Id_paciente`);

ALTER TABLE `Exp_Clinico_Paciente` ADD FOREIGN KEY (`Id_medico`) REFERENCES `Medico` (`Id_medico`);

ALTER TABLE `Rec_Medica_Paciente` ADD FOREIGN KEY (`Id_paciente`) REFERENCES `Paciente` (`Id_paciente`);

ALTER TABLE `Rec_Medica_Paciente` ADD FOREIGN KEY (`Id_medico`) REFERENCES `Medico` (`Id_medico`);

ALTER TABLE `Historial_Citas` ADD FOREIGN KEY (`Id_cita`) REFERENCES `Cita_Medica` (`Id_cita`);
