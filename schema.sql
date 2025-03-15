-- MySQL dump 10.13  Distrib 5.7.24, for osx11.1 (x86_64)
--
-- Host: localhost    Database: macroeconomic_db
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `data_sources`
--

DROP TABLE IF EXISTS `data_sources`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_sources` (
  `source_id` int NOT NULL AUTO_INCREMENT,
  `source_name` varchar(255) NOT NULL,
  `source_url` varchar(500) DEFAULT NULL,
  `description` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `api_endpoint` varchar(500) DEFAULT NULL,
  `api_key` varchar(255) DEFAULT NULL,
  `update_frequency` enum('D','W','M','Q','Y') NOT NULL DEFAULT 'M',
  PRIMARY KEY (`source_id`),
  UNIQUE KEY `source_name` (`source_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `indicator_data`
--

DROP TABLE IF EXISTS `indicator_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `indicator_data` (
  `data_id` bigint NOT NULL AUTO_INCREMENT,
  `indicator_id` int NOT NULL,
  `record_date` date NOT NULL,
  `value` decimal(18,6) NOT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`data_id`),
  UNIQUE KEY `indicator_id` (`indicator_id`,`record_date`),
  CONSTRAINT `indicator_data_ibfk_1` FOREIGN KEY (`indicator_id`) REFERENCES `indicators` (`indicator_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=357967 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `indicator_metadata`
--

DROP TABLE IF EXISTS `indicator_metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `indicator_metadata` (
  `metadata_id` int NOT NULL AUTO_INCREMENT,
  `indicator_id` int NOT NULL,
  `importance_tier` enum('1','2','3') NOT NULL,
  `sub_category` varchar(255) DEFAULT NULL,
  `use_case` enum('Short-Term Trading','Long-Term Investment','Macroeconomic Forecasting') NOT NULL,
  `notes` text,
  PRIMARY KEY (`metadata_id`),
  UNIQUE KEY `indicator_id` (`indicator_id`),
  CONSTRAINT `indicator_metadata_ibfk_1` FOREIGN KEY (`indicator_id`) REFERENCES `indicators` (`indicator_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `indicators`
--

DROP TABLE IF EXISTS `indicators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `indicators` (
  `indicator_id` int NOT NULL AUTO_INCREMENT,
  `indicator_name` varchar(255) NOT NULL,
  `fred_series_id` varchar(50) DEFAULT NULL,
  `source` varchar(255) NOT NULL,
  `category` enum('Leading','Coincident','Lagging') NOT NULL,
  `frequency` enum('M','Q','Y','D') NOT NULL,
  `unit` varchar(50) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `abbreviation` varchar(10) NOT NULL,
  `note` text,
  PRIMARY KEY (`indicator_id`),
  UNIQUE KEY `indicator_name` (`indicator_name`),
  UNIQUE KEY `abbreviation` (`abbreviation`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-15 18:10:20
