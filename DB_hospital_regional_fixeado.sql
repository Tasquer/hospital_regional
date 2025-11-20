
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;
SET SESSION sql_notes = 0;

-- =====================================================================
-- PASO 0: VERIFICAR Y CREAR BASE DE DATOS
-- =====================================================================
CREATE DATABASE IF NOT EXISTS hospital_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE hospital_db;

-- =====================================================================
-- PASO 1: LIMPIEZA COMPLETA (ORDEN CRÍTICO: Vistas → Tablas)
-- =====================================================================

-- Eliminar VISTAS primero (usando DROP VIEW, no DROP TABLE)
DROP VIEW IF EXISTS `vista_estadisticas_rn_mensual`;
DROP VIEW IF EXISTS `vista_indicadores_calidad_mensual`;
DROP VIEW IF EXISTS `vista_rem_mensual`;

-- Eliminar TABLAS en orden inverso de dependencias
DROP TABLE IF EXISTS `eventos_clinicos_rn`;
DROP TABLE IF EXISTS `recien_nacidos`;
DROP TABLE IF EXISTS `episodios_parto`;
DROP TABLE IF EXISTS `pacientes`;
DROP TABLE IF EXISTS `tipos_parto`;
DROP TABLE IF EXISTS `pueblos_originarios`;
DROP TABLE IF EXISTS `nacionalidades`;
DROP TABLE IF EXISTS `consultorios`;

-- =====================================================================
-- PASO 2: CREACIÓN DE TABLAS CATÁLOGO
-- =====================================================================

CREATE TABLE `consultorios` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(120) NOT NULL UNIQUE,
  `comuna` VARCHAR(60),
  `activo` BOOLEAN DEFAULT TRUE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_consultorio_activo` (`activo`)
) ENGINE=InnoDB;

CREATE TABLE `nacionalidades` (
  `codigo` CHAR(3) PRIMARY KEY,
  `nombre` VARCHAR(60) NOT NULL UNIQUE,
  `activo` BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE `pueblos_originarios` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(60) NOT NULL UNIQUE,
  `activo` BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE `tipos_parto` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(50) NOT NULL UNIQUE,
  `descripcion` VARCHAR(200),
  `activo` BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

-- =====================================================================
-- PASO 3: CREACIÓN DE TABLAS PRINCIPALES
-- =====================================================================

CREATE TABLE `pacientes` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `rut` VARCHAR(12) NOT NULL UNIQUE COMMENT 'Formato: 12345678-9',
  `dv` CHAR(1) NOT NULL,
  `nombres` VARCHAR(100) NOT NULL,
  `apellido_paterno` VARCHAR(100) NOT NULL,
  `apellido_materno` VARCHAR(100),
  `fecha_nacimiento` DATE NOT NULL,
  `nacionalidad_codigo` CHAR(3) NOT NULL,
  `pueblo_originario_id` INT NULL,
  `consultorio_id` INT NULL,
  `activo` BOOLEAN DEFAULT TRUE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_pacientes_nacionalidad` FOREIGN KEY (`nacionalidad_codigo`) REFERENCES `nacionalidades` (`codigo`),
  CONSTRAINT `fk_pacientes_pueblo` FOREIGN KEY (`pueblo_originario_id`) REFERENCES `pueblos_originarios` (`id`),
  CONSTRAINT `fk_pacientes_consultorio` FOREIGN KEY (`consultorio_id`) REFERENCES `consultorios` (`id`),
  INDEX `idx_paciente_fecha_nacimiento` (`fecha_nacimiento`),
  INDEX `idx_paciente_nombres` (`nombres`, `apellido_paterno`)
) ENGINE=InnoDB;

CREATE TABLE `episodios_parto` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `paciente_id` INT NOT NULL,
  `fecha_hora_parto` DATETIME NOT NULL,
  `tipo_parto_id` INT NOT NULL,
  `fecha_ingreso` DATETIME NOT NULL,
  `edad_materna_parto` TINYINT NOT NULL,
  `paridad` TINYINT NULL COMMENT 'Número de partos previos',
  `control_prenatal` BOOLEAN DEFAULT TRUE,
  `preeclampsia_severa` BOOLEAN DEFAULT FALSE,
  `eclampsia` BOOLEAN DEFAULT FALSE,
  `sepsis` BOOLEAN DEFAULT FALSE,
  `infeccion_ovular` BOOLEAN DEFAULT FALSE,
  `detalle_otra_patologia` TEXT NULL,
  `ligadura_tardia_cordon` BOOLEAN DEFAULT FALSE,
  `contacto_piel_piel` BOOLEAN DEFAULT FALSE,
  `duracion_contacto_min` SMALLINT NULL,
  `lactancia_primera_hora` BOOLEAN DEFAULT FALSE,
  `alojamiento_conjunto` BOOLEAN DEFAULT FALSE,
  `vdrl_positivo` BOOLEAN DEFAULT FALSE,
  `hepatitis_b_positivo` BOOLEAN DEFAULT FALSE,
  `vih_positivo` BOOLEAN DEFAULT FALSE,
  `observaciones` TEXT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_episodios_paciente` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`),
  CONSTRAINT `fk_episodios_tipo_parto` FOREIGN KEY (`tipo_parto_id`) REFERENCES `tipos_parto` (`id`),
  CONSTRAINT `chk_edad_materna` CHECK (`edad_materna_parto` BETWEEN 10 AND 60),
  CONSTRAINT `chk_fecha_ingreso` CHECK (`fecha_ingreso` <= `fecha_hora_parto`),
  INDEX `idx_episodio_fecha_parto` (`fecha_hora_parto`),
  INDEX `idx_episodio_paciente` (`paciente_id`),
  INDEX `idx_episodio_tipo_parto` (`tipo_parto_id`),
  INDEX `idx_episodio_edad_materna` (`edad_materna_parto`)
) ENGINE=InnoDB;

CREATE TABLE `recien_nacidos` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `episodio_parto_id` INT NOT NULL,
  `sexo` ENUM('Masculino', 'Femenino', 'Indeterminado') NOT NULL,
  `peso_gramos` INT NOT NULL,
  `talla_cm` INT NOT NULL,
  `perimetro_cefalico_cm` DECIMAL(4,1) NULL,
  `apgar1` TINYINT,
  `apgar5` TINYINT,
  `edad_gestacional_semanas` TINYINT,
  `reanimacion` ENUM('Ninguna', 'Básica', 'Avanzada') DEFAULT 'Ninguna',
  `tiene_malformacion` BOOLEAN DEFAULT FALSE,
  `malformacion_detalle` TEXT NULL,
  `diagnostico_alta` VARCHAR(255) NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_rn_episodio` FOREIGN KEY (`episodio_parto_id`) REFERENCES `episodios_parto` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_peso_rn` CHECK (`peso_gramos` BETWEEN 400 AND 6500),
  CONSTRAINT `chk_apgar1` CHECK (`apgar1` BETWEEN 0 AND 10),
  CONSTRAINT `chk_apgar5` CHECK (`apgar5` BETWEEN 0 AND 10),
  CONSTRAINT `chk_edad_gestacional` CHECK (`edad_gestacional_semanas` BETWEEN 20 AND 45),
  INDEX `idx_rn_episodio` (`episodio_parto_id`),
  INDEX `idx_rn_peso` (`peso_gramos`),
  INDEX `idx_rn_edad_gestacional` (`edad_gestacional_semanas`)
) ENGINE=InnoDB;

CREATE TABLE `eventos_clinicos_rn` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `recien_nacido_id` INT NOT NULL,
  `tipo_evento` ENUM(
    'Profilaxis Ocular',
    'Vacuna Hepatitis B',
    'Vacuna BCG',
    'Tamizaje Auditivo',
    'Tamizaje PKU/TSH',
    'Tamizaje Cardiopatías'
  ) NOT NULL,
  `fecha_hora` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `resultado` VARCHAR(100) NULL,
  `observaciones` TEXT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_eventos_rn` FOREIGN KEY (`recien_nacido_id`) REFERENCES `recien_nacidos` (`id`) ON DELETE CASCADE,
  UNIQUE KEY `uq_evento_por_rn` (`recien_nacido_id`, `tipo_evento`),
  INDEX `idx_evento_fecha` (`fecha_hora`),
  INDEX `idx_evento_tipo` (`tipo_evento`)
) ENGINE=InnoDB;

-- =====================================================================
-- PASO 4: CREACIÓN DE VISTAS
-- =====================================================================

CREATE VIEW `vista_rem_mensual` AS
SELECT
  DATE_FORMAT(ep.fecha_hora_parto, '%Y-%m') AS `mes`,
  p.rut AS `rut_paciente`,
  CONCAT(p.nombres, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS `nombre_completo`,
  ep.edad_materna_parto,
  tp.nombre AS `tipo_parto`,
  rn.sexo AS `sexo_rn`,
  rn.peso_gramos,
  rn.edad_gestacional_semanas,
  rn.apgar1,
  rn.apgar5,
  ep.ligadura_tardia_cordon,
  ep.contacto_piel_piel,
  ep.lactancia_primera_hora,
  ep.alojamiento_conjunto,
  ep.control_prenatal
FROM `episodios_parto` ep
JOIN `pacientes` p ON ep.paciente_id = p.id
JOIN `tipos_parto` tp ON ep.tipo_parto_id = tp.id
LEFT JOIN `recien_nacidos` rn ON rn.episodio_parto_id = ep.id;

CREATE VIEW `vista_indicadores_calidad_mensual` AS
SELECT
  DATE_FORMAT(fecha_hora_parto, '%Y-%m') AS `mes`,
  COUNT(*) AS `total_partos`,
  ROUND(SUM(ligadura_tardia_cordon) * 100.0 / NULLIF(COUNT(*), 0), 2) AS `porc_ligadura_tardia`,
  ROUND(SUM(contacto_piel_piel) * 100.0 / NULLIF(COUNT(*), 0), 2) AS `porc_contacto_piel`,
  ROUND(SUM(lactancia_primera_hora) * 100.0 / NULLIF(COUNT(*), 0), 2) AS `porc_lactancia_temprana`,
  ROUND(SUM(alojamiento_conjunto) * 100.0 / NULLIF(COUNT(*), 0), 2) AS `porc_alojamiento_conjunto`,
  ROUND(SUM(control_prenatal) * 100.0 / NULLIF(COUNT(*), 0), 2) AS `porc_control_prenatal`
FROM `episodios_parto`
GROUP BY `mes`
ORDER BY `mes` DESC;

CREATE VIEW `vista_estadisticas_rn_mensual` AS
SELECT
  DATE_FORMAT(ep.fecha_hora_parto, '%Y-%m') AS `mes`,
  COUNT(rn.id) AS `total_rn`,
  ROUND(AVG(rn.peso_gramos), 0) AS `peso_promedio`,
  ROUND(AVG(rn.edad_gestacional_semanas), 1) AS `edad_gestacional_promedio`,
  SUM(CASE WHEN rn.peso_gramos < 2500 THEN 1 ELSE 0 END) AS `rn_bajo_peso`,
  SUM(CASE WHEN rn.apgar5 < 7 THEN 1 ELSE 0 END) AS `rn_apgar_bajo`,
  SUM(CASE WHEN rn.tiene_malformacion = TRUE THEN 1 ELSE 0 END) AS `rn_con_malformacion`
FROM `episodios_parto` ep
LEFT JOIN `recien_nacidos` rn ON rn.episodio_parto_id = ep.id
GROUP BY `mes`
ORDER BY `mes` DESC;

-- =====================================================================
-- PASO 5: RESTAURAR CONFIGURACIONES
-- =====================================================================

SET FOREIGN_KEY_CHECKS=1;
SET SESSION sql_notes = 1;

-- =====================================================================
-- PASO 6: DATOS DE PRUEBA 
-- =====================================================================
-- Insertar nacionalidades
INSERT INTO `nacionalidades` (`codigo`, `nombre`) VALUES
('CHL', 'Chile'),
('PER', 'Perú'),
('BOL', 'Bolivia'),
('ARG', 'Argentina'),
('VEN', 'Venezuela');

-- Insertar tipos de parto
INSERT INTO `tipos_parto` (`nombre`, `descripcion`) VALUES
('Normal', 'Parto vaginal sin complicaciones'),
('Cesárea', 'Parto por cesárea electiva o de emergencia'),
('Fórceps', 'Parto vaginal asistido con fórceps'),
('Vacuum', 'Parto vaginal asistido con extracción por vacío');

-- Insertar pueblos originarios
INSERT INTO `pueblos_originarios` (`nombre`) VALUES
('Mapuche'),
('Aymara'),
('Rapa Nui'),
('Diaguita'),
('Quechua');

-- Insertar consultorios
INSERT INTO `consultorios` (`nombre`, `comuna`) VALUES
('CESFAM Violeta Parra', 'Chillán'),
('CESFAM Los Volcanes', 'Chillán Viejo'),
('Consultorio de Pinto', 'Pinto'),
('CESFAM Bulnes', 'Bulnes');

-- Insertar paciente de ejemplo
INSERT INTO `pacientes` (
  `rut`, `dv`, `nombres`, `apellido_paterno`, `apellido_materno`,
  `fecha_nacimiento`, `nacionalidad_codigo`, `consultorio_id`
) VALUES
('12345678', '5', 'María José', 'González', 'Muñoz', '1995-03-15', 'CHL', 1),
('98765432', '1', 'Carmen', 'Silva', 'Rojas', '1988-07-22', 'CHL', 1);

-- Insertar episodio de parto
INSERT INTO `episodios_parto` (
  `paciente_id`, `fecha_hora_parto`, `tipo_parto_id`, `fecha_ingreso`,
  `edad_materna_parto`, `paridad`, `control_prenatal`,
  `ligadura_tardia_cordon`, `contacto_piel_piel`, `lactancia_primera_hora`
) VALUES
(1, '2024-10-15 14:30:00', 1, '2024-10-15 08:00:00', 29, 0, TRUE, TRUE, TRUE, TRUE),
(2, '2024-10-16 09:15:00', 2, '2024-10-16 07:30:00', 36, 1, TRUE, TRUE, TRUE, FALSE);

-- Insertar recién nacidos
INSERT INTO `recien_nacidos` (
  `episodio_parto_id`, `sexo`, `peso_gramos`, `talla_cm`,
  `apgar1`, `apgar5`, `edad_gestacional_semanas`
) VALUES
(1, 'Femenino', 3200, 48, 9, 9, 39),
(2, 'Masculino', 3450, 50, 8, 9, 38);

-- Insertar eventos clínicos
INSERT INTO `eventos_clinicos_rn` (`recien_nacido_id`, `tipo_evento`, `resultado`) VALUES
(1, 'Profilaxis Ocular', 'Aplicado'),
(1, 'Vacuna Hepatitis B', 'Aplicado'),
(2, 'Profilaxis Ocular', 'Aplicado'),
(2, 'Vacuna BCG', 'Aplicado');


-- =====================================================================
-- FIN DEL SCRIPT --
-- =====================================================================