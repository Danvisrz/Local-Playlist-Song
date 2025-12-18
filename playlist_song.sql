CREATE DATABASE  IF NOT EXISTS `playlist` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `playlist`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: playlist
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
-- Table structure for table `song`
--

DROP TABLE IF EXISTS `song`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `song` (
  `song_id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `artist` varchar(255) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `file_path` varchar(500) NOT NULL,
  PRIMARY KEY (`song_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `song`
--

LOCK TABLES `song` WRITE;
/*!40000 ALTER TABLE `song` DISABLE KEYS */;
INSERT INTO `song` VALUES (1,'Dear God','Avenged Sevenfold',442,'C:/Users/DANV/Music/Playlist Lagu/Avenged Sevenfold - Dear God.mp3'),(2,'21 Guns','Green Day',526,'C:/Users/DANV/Music/Playlist Lagu/Green Day - 21 Guns.mp3'),(3,'Basket Case','Green Day',314,'C:/Users/DANV/Music/Playlist Lagu/Green Day - Basket Case.mp3'),(4,'Akhir Tak Bahagia','Misellia Ikwan',305,'C:/Users/DANV/Music/Playlist Lagu/Misellia - Akhir Tak Bahagia.mp3'),(5,'Bergema Sampai Selamanya','Nadhif Basamalah',452,'C:/Users/DANV/Music/Playlist Lagu/Nadhif Basalamah - bergema sampai selamanya.mp3'),(6,'33x','Perunggu',833,'C:/Users/DANV/Music/Playlist Lagu/Perunggu - 33x.mp3'),(7,'Girl Like Me','PinkPantheress',224,'C:/Users/DANV/Music/Playlist Lagu/PinkPantheress - Girl Like Me.mp3'),(8,'Illegal','PinkPantheress',232,'C:/Users/DANV/Music/Playlist Lagu/PinkPantheress - Illegal.mp3'),(9,'Stars','PinkPantheress',222,'C:/Users/DANV/Music/Playlist Lagu/PinkPantheress - Stars.mp3'),(10,'Stateside','PinkPantheress',250,'C:/Users/DANV/Music/Playlist Lagu/PinkPantheress - Stateside.mp3');
/*!40000 ALTER TABLE `song` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-18 11:38:01
