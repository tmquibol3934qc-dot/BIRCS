-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: bircs_db
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `incidents`
--

LOCK TABLES `incidents` WRITE;
/*!40000 ALTER TABLE `incidents` DISABLE KEYS */;
INSERT INTO `incidents` VALUES (1,'2026-892','Kahayon','Jumong','09388453042','Ps3 Caloocan','02/15/2026','05:05 PM','2','Ang aso ni Jumong daw ay maingay at muntik na maka kagat ng bata, ngayun ang gusto ni Kahayon ay mag bayad ng compensation at pag papa turok sa bata','Resolved','Rainier Kahayon','2026-03-03 08:50:05','Barangay Conciliation','2 days','Mag babayad si Jumong ng compensation na nag kaka halaga ng 3000 para sa kabuoang turok ng bata kabilang na ang 6 na turok para asa anti rabies at 1 anti tetano at mag kaka sundong itatali nalang ang aso malapit o sa loob ng bakuran ni Jumong'),(2,'2026-864','Krizzy','Kristan','09277767840','Ps5 caloocan','02/28/2026','03:05 PM','2','Maingay daw si Kristan sa oras ng gabi sa mga oras ng 10 PM at nag v videoke pa raw at humihiyaw upang magising ang mga anak ni Krizzy at hindi naka pasok ang kanyang asawa','Pending','Rainier Kahayon','2026-03-03 08:53:06',NULL,NULL,NULL),(3,'2026-216','Chesca','Krizzy','09388453042','Ps.2 Caloocan','03/03/2025','02:15 PM','2','Maingay daw ang aso ni Krizzy at hindi manlang nya tinatali ang aso sa kanilang bahay hanggang sa nag simula nalang itong dumumi sa tapat ng iba\'t ibang bahay at muntik pang maka kagat ng ibang bata pero hindi naman natuloy','Resolved','Chesca Rosales','2026-03-03 08:55:28','Barangay Conciliation','','Itatali nalang ang aso, malapit sa bakuran at hindi na hahayaang maka lapit sa mga kabataan'),(4,'2026-229','Rainier','Drew','09388453041','ps.3 BSCC','19/03/2026','11:30 AM','2','Drew is too noisy, masyado siyang maingay at nag videoke pa ng tanghaling tapat at nagigising ang mga anak ni Rainier','Resolved','Chesca Rosales','2026-03-20 09:33:21','Barangay Conciliation','','Tatahimik nalang daw ang respondent sa oras na ka gustuhan ng complainant para hindi na maka gawa pa ng anu mang gulo at ingay'),(5,'2026-969','TJ','Chesca','093884231','ps.5 BSCC','10/03/2026','02:05 PM','2','Maingay raw ang aso at hindi nakakapag pa tulog ng mga bata sa tanghali kaka tahol muntik pang maka kagat ng bata','Urgent','Chesca Rosales','2026-03-20 09:38:54',NULL,NULL,NULL);
/*!40000 ALTER TABLE `incidents` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-20 18:02:49
