-- MySQL dump 10.13  Distrib 8.4.5, for Linux (x86_64)
--
-- Host: localhost    Database: django
-- ------------------------------------------------------
-- Server version	8.4.5

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
-- Table structure for table `OTP`
--

DROP TABLE IF EXISTS `OTP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OTP` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `code` char(4) DEFAULT NULL,
  `is_used` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `OTP_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OTP`
--

LOCK TABLES `OTP` WRITE;
/*!40000 ALTER TABLE `OTP` DISABLE KEYS */;
/*!40000 ALTER TABLE `OTP` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add usuario',7,'add_usuario'),(26,'Can change usuario',7,'change_usuario'),(27,'Can delete usuario',7,'delete_usuario'),(28,'Can view usuario',7,'view_usuario'),(29,'Can add login attempt',8,'add_loginattempt'),(30,'Can change login attempt',8,'change_loginattempt'),(31,'Can delete login attempt',8,'delete_loginattempt'),(32,'Can view login attempt',8,'view_loginattempt'),(33,'Can add otp',9,'add_otp'),(34,'Can change otp',9,'change_otp'),(35,'Can delete otp',9,'delete_otp'),(36,'Can view otp',9,'view_otp'),(37,'Can add captcha store',10,'add_captchastore'),(38,'Can change captcha store',10,'change_captchastore'),(39,'Can delete captcha store',10,'delete_captchastore'),(40,'Can view captcha store',10,'view_captchastore');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `captcha_captchastore`
--

DROP TABLE IF EXISTS `captcha_captchastore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `captcha_captchastore` (
  `id` int NOT NULL AUTO_INCREMENT,
  `challenge` varchar(32) NOT NULL,
  `response` varchar(32) NOT NULL,
  `hashkey` varchar(40) NOT NULL,
  `expiration` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hashkey` (`hashkey`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `captcha_captchastore`
--

LOCK TABLES `captcha_captchastore` WRITE;
/*!40000 ALTER TABLE `captcha_captchastore` DISABLE KEYS */;
INSERT INTO `captcha_captchastore` VALUES (42,'TDQT','tdqt','688c1f0b719a97fc8cbcdf5299293fe284858a64','2025-06-23 20:35:21.629252'),(43,'JZLK','jzlk','96cacf84fb9f3066055e2d4c44d540e7a77d39f8','2025-06-23 20:35:27.766732'),(44,'POPB','popb','118c3acbd890409df14b03301b3a2f0551aa3205','2025-06-23 20:35:30.249672'),(45,'VGGY','vggy','8058949629bafed6c37345fafa800d11bec215eb','2025-06-23 20:35:31.797647'),(46,'GOXE','goxe','5b870b0a9c7da42ccd5774bc88460c5f8256a7d1','2025-06-23 20:35:32.792924'),(47,'OXPH','oxph','70aae66a0f74bfc1f781be941e875a76e41dcd03','2025-06-23 20:35:34.153718'),(50,'XSPZ','xspz','adaefc38c1a9d3c9fce533f37d478eb8d86f0f1c','2025-06-23 20:37:45.450078');
/*!40000 ALTER TABLE `captcha_captchastore` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(10,'captcha','captchastore'),(5,'contenttypes','contenttype'),(8,'proyecto','loginattempt'),(9,'proyecto','otp'),(7,'proyecto','usuario'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-05-21 01:57:09.289503'),(2,'auth','0001_initial','2025-05-21 01:57:10.206295'),(3,'admin','0001_initial','2025-05-21 01:57:10.450708'),(4,'admin','0002_logentry_remove_auto_add','2025-05-21 01:57:10.464279'),(5,'admin','0003_logentry_add_action_flag_choices','2025-05-21 01:57:10.478372'),(6,'contenttypes','0002_remove_content_type_name','2025-05-21 01:57:10.624590'),(7,'auth','0002_alter_permission_name_max_length','2025-05-21 01:57:10.718644'),(8,'auth','0003_alter_user_email_max_length','2025-05-21 01:57:10.748822'),(9,'auth','0004_alter_user_username_opts','2025-05-21 01:57:10.759269'),(10,'auth','0005_alter_user_last_login_null','2025-05-21 01:57:10.842321'),(11,'auth','0006_require_contenttypes_0002','2025-05-21 01:57:10.847378'),(12,'auth','0007_alter_validators_add_error_messages','2025-05-21 01:57:10.857931'),(13,'auth','0008_alter_user_username_max_length','2025-05-21 01:57:10.954048'),(14,'auth','0009_alter_user_last_name_max_length','2025-05-21 01:57:11.053170'),(15,'auth','0010_alter_group_name_max_length','2025-05-21 01:57:11.077251'),(16,'auth','0011_update_proxy_permissions','2025-05-21 01:57:11.088754'),(17,'auth','0012_alter_user_first_name_max_length','2025-05-21 01:57:11.180515'),(18,'sessions','0001_initial','2025-05-21 01:57:11.239950'),(19,'proyecto','0001_initial','2025-05-31 20:11:01.772213'),(20,'proyecto','0002_otp','2025-05-31 22:26:19.079779'),(21,'proyecto','0003_auto_20250611_0431','2025-06-11 04:31:58.049563'),(22,'captcha','0001_initial','2025-06-22 22:53:31.179105'),(23,'captcha','0002_alter_captchastore_id','2025-06-22 22:53:31.187426');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('0r590eyma4tgqpdz8oxibj948shfbgih','eyJ1c3VhcmlvIjoiYWRtaW4iLCJ1c2VyX2lkIjoxLCJvdHBfc2VudCI6dHJ1ZSwiYXV0aGVudGljYXRlZCI6dHJ1ZX0:1uS3Q8:dBCvqIeAj5LU2cuomUatpSwzqLmCdFjrSCK946fxfAQ','2025-06-19 01:46:24.367374'),('2n461uh3b3xwflcypldhurbvu0e5ssge','eyJ1c3VhcmlvIjoiYWRtaW4iLCJ1c2VyX2lkIjoxLCJvdHBfc2VudCI6dHJ1ZSwiYXV0aGVudGljYXRlZCI6dHJ1ZX0:1uSWXh:D42hBEGlD2_QFoljPE_dRlFfZMkNoMulZJMMpUnOKus','2025-06-20 08:52:09.683744'),('6cucdpfsjf2vlg2lhfxnxnob08e74uic','eyJ1c3VhcmlvIjoiYWRtaW4iLCJ1c2VyX2lkIjoxLCJvdHBfc2VudCI6dHJ1ZSwiYXV0aGVudGljYXRlZCI6dHJ1ZX0:1uSjKT:gCBbh8GYKdcEQIr2V42UsbokXwmXdqTrH75rnPQEHQM','2025-06-20 22:31:21.779685'),('90skjz2fsbotonciknqpq7qno45mzqm2','eyJ1c3VhcmlvIjoiYWRtaW4iLCJ1c2VyX2lkIjoxLCJvdHBfc2VudCI6dHJ1ZSwiYXV0aGVudGljYXRlZCI6dHJ1ZX0:1uSSpX:yuvJpB_8XNAsN_iR0s4sGgvvccZHw4sdN4pOLDM0uTE','2025-06-20 04:54:19.175815'),('adr382cjjrg2xdxeaelrlqzosnqifig6','eyJ1c3VhcmlvIjoiYWRtaW4iLCJ1c2VyX2lkIjoxLCJvdHBfc2VudCI6dHJ1ZX0:1uSkhe:APXOwVDura53oFCdgQflgilzqlNfqL79umqZywMEXFo','2025-06-20 23:59:22.396215'),('bvf8ifejditmqje2ntb07qyvx8ubqr2f','eyJ1c3VhcmlvIjoiYWRtaW4iLCJ1c2VyX2lkIjoxLCJvdHBfc2VudCI6dHJ1ZSwiYXV0aGVudGljYXRlZCI6dHJ1ZX0:1uPFZ5:RKlP2NNI2uVzeeybAPDXbHbEw5ejv67fr1lTT6VyKWw','2025-06-11 08:08:03.724670'),('oiejqhj8n6lotpawfl0xw4msj2m0b2w0','eyJ1c3VhcmlvIjoiYWRtaW4iLCJ1c2VyX2lkIjoxLCJvdHBfc2VudCI6dHJ1ZSwiYXV0aGVudGljYXRlZCI6dHJ1ZX0:1uTAOg:zy_2l5vlxZJ3wOHgQ8HIkDMCwlMHOjkA9MzUaqFWXN0','2025-06-22 03:25:30.538579'),('p1k9zdcwcc45cfdhv7892kyzp8e8zdm2','eyJ1c3VhcmlvIjoiYWRtaW4ifQ:1uNL6w:Gc31Q2Njv9-nQTTuxLAmiuj2i0qU81sMM4AaWEmmfhs','2025-06-06 01:39:06.399649'),('rqns17cnoh7ia120tilja2blqxjvisha','eyJ1c3VhcmlvIjoiYWRtaW4iLCJvdHBfc2VudCI6dHJ1ZX0:1uM9Tz:QgcOEag3fidyn6WJezFBeiDBq9xPHp522Ym71PtnTxA','2025-06-02 19:01:59.630466'),('tr35ua4o350jd1lo2m2417lkr0k2ztv5','eyJ1c3VhcmlvIjoiYWRtaW4iLCJ1c2VyX2lkIjoxLCJvdHBfc2VudCI6dHJ1ZSwiYXV0aGVudGljYXRlZCI6dHJ1ZX0:1uPPg5:EJxNTDv_d7J1LCB4prRjZpnFNedSBxQAAQSYs24FhLk','2025-06-11 18:55:57.210136'),('ts4dnls0iapakxzg7nf4zc4s24gqf5b8','eyJ1c3VhcmlvIjoiYWRtaW4iLCJ1c2VyX2lkIjoxLCJvdHBfc2VudCI6dHJ1ZSwiYXV0aGVudGljYXRlZCI6dHJ1ZX0:1uSksY:uv3wcHZGsVmbOmlowO1MAUi-_-Xd5CYl5mbjbsFjl5I','2025-06-21 00:10:38.119855');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyecto_loginattempt`
--

DROP TABLE IF EXISTS `proyecto_loginattempt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto_loginattempt` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `ip` char(39) NOT NULL,
  `username` varchar(150) NOT NULL,
  `attempts` int unsigned NOT NULL,
  `last_attempt` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `proyecto_loginattempt_chk_1` CHECK ((`attempts` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyecto_loginattempt`
--

LOCK TABLES `proyecto_loginattempt` WRITE;
/*!40000 ALTER TABLE `proyecto_loginattempt` DISABLE KEYS */;
INSERT INTO `proyecto_loginattempt` VALUES (1,'127.0.0.1','admin',0,'2025-06-23 20:31:26.632119'),(2,'127.0.0.1','12',6,'2025-05-31 20:14:04.253248'),(3,'127.0.0.1','s',2,'2025-06-01 00:50:21.926773'),(4,'127.0.0.1','1',10,'2025-06-02 17:57:57.533940'),(5,'127.0.0.1','2',1,'2025-05-31 20:16:00.815156'),(6,'127.0.0.1','a',1,'2025-05-31 20:48:03.479082'),(7,'127.0.0.1','aadmin',1,'2025-06-02 17:06:11.447145');
/*!40000 ALTER TABLE `proyecto_loginattempt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyecto_otp`
--

DROP TABLE IF EXISTS `proyecto_otp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto_otp` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_used` tinyint(1) NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyecto_otp`
--

LOCK TABLES `proyecto_otp` WRITE;
/*!40000 ALTER TABLE `proyecto_otp` DISABLE KEYS */;
INSERT INTO `proyecto_otp` VALUES (1,'831746','2025-06-11 04:33:27.159070',1,1),(2,'493415','2025-06-11 06:28:43.656179',1,1),(3,'584053','2025-06-11 06:49:08.714933',1,1),(4,'195319','2025-06-11 06:53:46.526827',1,1),(5,'885607','2025-06-11 06:56:40.719320',1,1),(6,'555214','2025-06-11 07:00:58.737302',1,1),(7,'557310','2025-06-11 07:02:22.871636',1,1),(8,'626566','2025-06-11 07:07:40.750663',1,1),(9,'753081','2025-06-11 17:52:56.943065',1,1),(10,'455470','2025-06-11 17:55:37.357654',1,1),(11,'583522','2025-06-11 18:00:37.514876',1,1),(12,'368691','2025-06-11 18:03:22.929674',1,1),(13,'519863','2025-06-11 18:30:41.169158',1,1),(14,'359482','2025-06-11 18:35:22.159602',1,1),(15,'354324','2025-06-11 18:41:05.600575',1,1),(16,'826085','2025-06-11 19:12:57.337136',1,1),(17,'845337','2025-06-19 00:37:52.971060',1,1),(18,'756559','2025-06-20 03:34:19.551953',1,1),(19,'734842','2025-06-20 03:37:12.208099',1,1),(20,'316625','2025-06-20 04:22:55.704426',1,1),(21,'579576','2025-06-20 07:50:59.394558',1,1),(22,'549021','2025-06-20 17:47:55.583489',1,1),(23,'737561','2025-06-20 22:58:02.771902',1,1),(24,'868222','2025-06-21 03:23:38.179416',1,1),(25,'910643','2025-06-21 20:43:11.718082',1,1),(26,'765951','2025-06-21 23:24:08.057268',1,1),(27,'161702','2025-06-21 23:36:25.261540',1,1),(28,'434294','2025-06-21 23:37:38.623290',1,1),(29,'695997','2025-06-22 00:36:38.539963',1,1),(30,'893728','2025-06-22 00:37:47.016132',1,1),(31,'184708','2025-06-22 02:01:43.505937',1,1),(32,'271558','2025-06-22 03:31:23.172294',1,1),(33,'177494','2025-06-22 23:32:01.585367',1,1),(34,'821703','2025-06-22 23:56:10.860068',1,1),(35,'618584','2025-06-23 05:03:44.163710',1,1),(36,'345006','2025-06-23 20:31:26.641929',1,1);
/*!40000 ALTER TABLE `proyecto_otp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyecto_usuario`
--

DROP TABLE IF EXISTS `proyecto_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto_usuario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyecto_usuario`
--

LOCK TABLES `proyecto_usuario` WRITE;
/*!40000 ALTER TABLE `proyecto_usuario` DISABLE KEYS */;
/*!40000 ALTER TABLE `proyecto_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servidores`
--

DROP TABLE IF EXISTS `servidores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servidores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `ip` varchar(45) NOT NULL,
  `usuario` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip` (`ip`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servidores`
--

LOCK TABLES `servidores` WRITE;
/*!40000 ALTER TABLE `servidores` DISABLE KEYS */;
INSERT INTO `servidores` VALUES (1,'debian1','192.168.1.141','debian','pbkdf2_sha256$260000$sO7TTiv5SRmcyzp0EskwxB$vMnxkmakbxfbDS7zezZdPIswe/DVIN0aQoqvccIIrHI=','2025-06-22 03:36:11'),(2,'debian2','192.168.1.239','debian','pbkdf2_sha256$1000000$OGUp2HhYPt4bGn75O0Zd1c$F/o4wbLsLLO2/ciWh9UA+kwM2I5hJLk282V53lX2Eak=','2025-06-22 23:57:52');
/*!40000 ALTER TABLE `servidores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `correo` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin','pbkdf2_sha256$260000$Atib8dV19uyVi9xu4AN73S$Djq2Q4iWOZcIKQKiV0qiG/Q+U0CfJKEpADzw48Q5plQ=','bryant_2017@outlook.com');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-23 15:29:50
