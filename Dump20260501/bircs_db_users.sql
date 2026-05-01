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
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` varchar(50) NOT NULL,
  `rfid_code` varchar(100) DEFAULT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `contact_no` varchar(20) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `q1` varchar(255) DEFAULT NULL,
  `a1` varchar(255) DEFAULT NULL,
  `q2` varchar(255) DEFAULT NULL,
  `a2` varchar(255) DEFAULT NULL,
  `q3` varchar(255) DEFAULT NULL,
  `a3` varchar(255) DEFAULT NULL,
  `role` varchar(50) DEFAULT 'Staff',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `position` varchar(50) DEFAULT NULL,
  `suspension_until` datetime DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Active',
  `profile_pic` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_id` (`employee_id`),
  UNIQUE KEY `rfid_code` (`rfid_code`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'0213213','1261907250','TJ','Quibol','N/A','Admin@1234','What is your mother\'s maiden name?','asd','What is your mother\'s maiden name?','dsa','What is your mother\'s maiden name?','sad','Kapitan','2026-02-13 13:19:35',NULL,NULL,'None','Blocked',NULL),(2,'090909','1245981922','TJ','Quibol','N/A','Jumong@1234','What is your mother\'s maiden name?','asd','What is your mother\'s maiden name?','asd','What is your mother\'s maiden name?','asd','Kapitan','2026-02-23 09:14:57',NULL,NULL,NULL,'Active',NULL),(3,'1132','1245425634','Rainier','Kahayon','N/A','Rainier@1234','What is your mother\'s maiden name?','mama','What is your mother\'s maiden name?','mama','What is your mother\'s maiden name?','mama','Kapitan','2026-03-01 13:05:12',NULL,NULL,NULL,'Active',NULL),(4,'231131','1245557570','Chesca','Rosales','N/A','Ches@12345','What is your mother\'s maiden name?','dad','What was the name of your first pet?','dad','What city were you born in?','dad','Staff','2026-03-18 11:39:09',NULL,NULL,'None','Active',NULL),(5,'87324','1244393186','Kristan','Ariate','N/A','Ariate@123','What was the name of your first pet?','mama','What is your favorite food?','mama','What is your mother\'s maiden name?','mama','Staff','2026-03-20 09:52:33',NULL,NULL,'None','Active',NULL),(6,'323323','','Jordan','Cabading','N/A','Jordan@123','What is your mother\'s maiden name?','Mama','What was the name of your first pet?','Mama','What city were you born in?','Mama','Lupon','2026-04-20 11:50:05',NULL,NULL,NULL,'Active',NULL),(7,'112233','1245258770','Ches','Rosales','09123456789','Ches@1234','What is your mother\'s maiden name?','mother','What was the name of your first pet?','pet','What city were you born in?','city','Staff','2026-04-30 14:43:58','Staff',NULL,NULL,'Active','C:/Users/Jumong/PyCharmMiscProject/BIRCS/bircs_package/assets/profiles/emp_112233.png');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-01 17:20:38
