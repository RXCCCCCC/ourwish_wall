-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: ourwish_wall
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comment_likes`
--

DROP TABLE IF EXISTS `comment_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comment_likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `comment_id` int NOT NULL,
  `user_uid` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_comment_user_like` (`comment_id`,`user_uid`),
  KEY `ix_comment_likes_user_uid` (`user_uid`),
  KEY `ix_comment_likes_comment_id` (`comment_id`),
  CONSTRAINT `comment_likes_ibfk_1` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comment_likes`
--

LOCK TABLES `comment_likes` WRITE;
/*!40000 ALTER TABLE `comment_likes` DISABLE KEYS */;
/*!40000 ALTER TABLE `comment_likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `wish_id` int NOT NULL,
  `user_uid` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nickname` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `likes` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ix_comments_wish_id` (`wish_id`),
  KEY `ix_comments_user_uid` (`user_uid`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`wish_id`) REFERENCES `wishes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,1,'Visitor_001','游客甲','😊','说得太好了！红色文化是我们的根！','2026-01-21 13:20:34',0),(2,1,'Visitor_002','游客乙','👍','支持！应该让更多人知道德兴的红色历史。','2026-01-21 15:20:34',0),(3,2,'TechFan_999','科技粉','🚀','VR 复原是个好主意，科技让历史更生动！','2026-01-21 23:20:34',0),(28,21,'1769069031100','RXCCCCCC','','6666','2026-01-23 13:05:31',0);
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `likes`
--

DROP TABLE IF EXISTS `likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `wish_id` int NOT NULL,
  `user_uid` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_wish_user_like` (`wish_id`,`user_uid`),
  KEY `ix_likes_user_uid` (`user_uid`),
  KEY `ix_likes_wish_id` (`wish_id`),
  CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`wish_id`) REFERENCES `wishes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `likes`
--

LOCK TABLES `likes` WRITE;
/*!40000 ALTER TABLE `likes` DISABLE KEYS */;
INSERT INTO `likes` VALUES (1,1,'Visitor_001','2026-01-22 09:20:34'),(2,1,'Visitor_002','2026-01-22 09:20:34'),(3,2,'TechFan_999','2026-01-22 09:20:34'),(44,21,'1769069031100','2026-01-23 13:05:26');
/*!40000 ALTER TABLE `likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rate_limits`
--

DROP TABLE IF EXISTS `rate_limits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rate_limits` (
  `id` int NOT NULL AUTO_INCREMENT,
  `client_ip` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_rate_limits_created_at` (`created_at`),
  KEY `ix_rate_limits_client_ip` (`client_ip`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rate_limits`
--

LOCK TABLES `rate_limits` WRITE;
/*!40000 ALTER TABLE `rate_limits` DISABLE KEYS */;
INSERT INTO `rate_limits` VALUES (1,'127.0.0.1','post_wish','2026-01-22 09:33:36'),(2,'127.0.0.1','post_wish','2026-01-22 09:35:49'),(3,'127.0.0.1','post_wish','2026-01-22 13:25:57'),(4,'127.0.0.1','post_wish','2026-01-22 14:00:04'),(5,'127.0.0.1','post_wish','2026-01-22 14:08:04'),(6,'127.0.0.1','post_wish','2026-01-22 14:11:55'),(7,'127.0.0.1','post_wish','2026-01-22 14:14:07'),(8,'127.0.0.1','post_wish','2026-01-22 14:19:28'),(9,'127.0.0.1','post_wish','2026-01-22 14:27:33'),(10,'127.0.0.1','post_wish','2026-01-22 14:27:59'),(11,'127.0.0.1','post_wish','2026-01-22 14:28:05'),(12,'127.0.0.1','post_wish','2026-01-22 14:54:43'),(13,'127.0.0.1','post_wish','2026-01-22 14:57:43'),(14,'127.0.0.1','post_wish','2026-01-22 15:02:07'),(15,'127.0.0.1','post_wish','2026-01-22 15:02:39'),(16,'127.0.0.1','post_wish','2026-01-23 13:05:21');
/*!40000 ALTER TABLE `rate_limits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishes`
--

DROP TABLE IF EXISTS `wishes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_uid` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nickname` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `ai_response` text COLLATE utf8mb4_unicode_ci,
  `likes` int DEFAULT NULL,
  `client_ip` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_wishes_created_at` (`created_at`),
  KEY `ix_wishes_user_uid` (`user_uid`),
  KEY `ix_wishes_category` (`category`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishes`
--

LOCK TABLES `wishes` WRITE;
/*!40000 ALTER TABLE `wishes` DISABLE KEYS */;
INSERT INTO `wishes` VALUES (1,'RedGuard_001','张建国','👴','红色传承','愿德兴的红色故事代代相传，让更多年轻人了解这片土地的革命历史。','星星之火，可以燎原。您的心愿是传承的火种。',88,NULL,'2026-01-20 09:20:34'),(2,'TechPioneer_007','李科技','🧑‍💻','产业发展','希望能用VR技术复原方志敏纪念馆，让历史场景活起来，让更多人沉浸式体验红色文化。','科技赋能，产业兴旺，您的想法很有远见。',56,NULL,'2026-01-21 09:20:34'),(3,'GreenGuardian_888','王环保','🌱','生态环保','希望德兴能建设更多的生态公园，让红色旅游与绿色生态完美结合。','绿水青山就是金山银山，您的愿望让人敬佩。',45,NULL,'2026-01-21 21:20:34'),(4,'VillageBuilder_666','刘乡建','👨‍🌾','乡村建设','期待家乡的道路更宽更平，让红色旅游的游客能更方便地到达各个景点。','乡村振兴，未来可期，您的建议充满智慧。',72,NULL,'2026-01-22 03:20:34'),(5,'CultureKeeper_520','陈文化','📚','红色传承','建议在学校开设更多红色文化课程，让孩子们从小就接受革命传统教育。','历史不会忘记，传承永不停歇，感谢您的守护。',103,NULL,'2026-01-22 06:20:34'),(21,'1769069031100','RXCCCCCC','','红色传承','xmxmxm','红色血脉代代传，愿你心中信仰之光永远闪耀。',1,'127.0.0.1','2026-01-23 13:05:21');
/*!40000 ALTER TABLE `wishes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-23 21:17:00
