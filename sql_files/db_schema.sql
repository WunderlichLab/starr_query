/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.4.6-MariaDB, for Linux (x86_64)
--
-- Host: bioed-new.bu.edu    Database: Team9
-- ------------------------------------------------------
-- Server version	11.4.6-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `Associations`
--

DROP TABLE IF EXISTS `Associations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Associations` (
  `eid` int(11) NOT NULL,
  `gid` int(11) NOT NULL,
  `imd_vs_ctrl` double DEFAULT NULL,
  `hksm_vs_20e` double DEFAULT NULL,
  `costarr_20e_vs_ctrl` double DEFAULT NULL,
  `exp_condition` enum('Control','20E','HKSM') NOT NULL,
  `activity` double DEFAULT NULL,
  PRIMARY KEY (`eid`,`gid`,`exp_condition`),
  KEY `gid` (`gid`),
  CONSTRAINT `Associations_ibfk_1` FOREIGN KEY (`eid`) REFERENCES `Enhancers` (`eid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Associations_ibfk_2` FOREIGN KEY (`gid`) REFERENCES `Genes` (`gid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Enhancers`
--

DROP TABLE IF EXISTS `Enhancers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Enhancers` (
  `eid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) DEFAULT NULL,
  `chromosome` varchar(2) DEFAULT NULL,
  `start` int(11) DEFAULT NULL,
  `end` int(11) DEFAULT NULL,
  `tf_counts` varchar(150) DEFAULT NULL,
  `tbs` int(11) DEFAULT NULL,
  PRIMARY KEY (`eid`),
  KEY `location` (`chromosome`,`start`,`end`),
  KEY `idx_enhancer_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8329 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Genes`
--

DROP TABLE IF EXISTS `Genes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Genes` (
  `gid` int(11) NOT NULL AUTO_INCREMENT,
  `geneid` varchar(20) DEFAULT NULL,
  `chromosome` varchar(2) DEFAULT NULL,
  `start` int(11) DEFAULT NULL,
  `end` int(11) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `immune_process` varchar(50) DEFAULT NULL,
  `time_cluster` enum('early_C2','mid_C3','late_C1','late_C4') DEFAULT NULL,
  PRIMARY KEY (`gid`),
  KEY `location` (`chromosome`,`start`,`end`),
  KEY `idx_geneid` (`geneid`)
) ENGINE=InnoDB AUTO_INCREMENT=10525 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-05-21 11:58:27
