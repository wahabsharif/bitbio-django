-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Aug 21, 2025 at 05:41 AM
-- Server version: 10.11.14-MariaDB
-- PHP Version: 8.4.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `devzeeteck_bit_bio`
--

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `sku` varchar(255) DEFAULT NULL,
  `seeding_density` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `product_name`, `sku`, `seeding_density`, `created_at`, `updated_at`) VALUES
(164, 'ioAstrocytes', 'ioEA1093', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(165, 'ioGABAergic Neurons', 'io1003', 150000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(166, 'ioGABAergic Neurons APP V717I/V717I', 'io1081', 150000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(167, 'ioGABAergic Neurons APP V717I/WT', 'io1085', 150000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(168, 'ioGlutamatergic Neurons', 'io1001', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(169, 'ioGlutamatergic Neurons APP KM670/671NL / KM670/671NL', 'io1059', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(170, 'ioGlutamatergic Neurons APP KM670/671NL/WT', 'io1061', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(171, 'ioGlutamatergic Neurons APP V717I/V717I', 'io1063', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(172, 'ioGlutamatergic Neurons APP V717I/WT', 'io1067', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(173, 'ioGlutamatergic Neurons GBA null/R159W', 'io1007', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(174, 'ioGlutamatergic Neurons HTT 50CAG/WT', 'ioEA1004', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(175, 'ioGlutamatergic Neurons MAPT N279K/N279K', 'io1014', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(176, 'ioGlutamatergic Neurons MAPT N279K/WT', 'io1009', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(177, 'ioGlutamatergic Neurons MAPT P301S/P301S', 'io1008', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(178, 'ioGlutamatergic Neurons MAPT P301S/WT', 'io1015', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(179, 'ioGlutamatergic Neurons PINK1 Q456X/Q456X', 'io1076', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(180, 'ioGlutamatergic Neurons PINK1 Q456X/WT', 'io1079', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(181, 'ioGlutamatergic Neurons PRKN R275W/R275W', 'io1020', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(182, 'ioGlutamatergic Neurons PRKN R275W/WT', 'io1013', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(183, 'ioGlutamatergic Neurons PSEN1 M146L/M146L', 'io1069', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(184, 'ioGlutamatergic Neurons PSEN1 M146L/WT', 'io1072', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(185, 'ioGlutamatergic Neurons SNCA A53T/A53T', 'io1088', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(186, 'ioGlutamatergic Neurons SNCA A53T/WT', 'io6005', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(187, 'ioGlutamatergic Neurons TDP-43 M337V/M337V', 'ioEA1005', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(188, 'ioGlutamatergic Neurons TDP-43 M337V/WT', 'ioEA1006', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(189, 'CRISPRa-Ready ioGlutamatergic Neurons', 'io1099', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(190, 'CRISPRi-Ready ioGlutamatergic Neurons', 'io1098', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(191, 'CRISPRko-Ready ioGlutamatergic Neurons', 'io1090', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(192, 'ioMicroglia Female', 'io1029', 39500, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(193, 'ioMicroglia Male', 'io1021', 39500, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(194, 'CRISPRko-Ready ioMicroglia Male', 'io1094', 39500, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(195, 'GFP ioMicroglia Male', 'io1096', 39500, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(196, 'ioMicroglia APOE 4/3 C112R/WT', 'io1033', 39500, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(197, 'ioMicroglia APOE 4/4 C112R/C112R', 'io1032', 39500, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(198, 'ioMicroglia TREM2 R47H/R47H', 'io1035', 39500, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(199, 'ioMicroglia TREM2 R47H/WT', 'io1038', 39500, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(200, 'ioMotor Neurons', 'io1027', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(201, 'ioMotor Neurons FUS P525L/P525L', 'io1052', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(202, 'ioMotor Neurons FUS P525L/WT', 'io1055', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(203, 'ioMotor Neurons SOD-1 G93A/G93A', 'io1041', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(204, 'ioMotor Neurons SOD-1 G93A/WT', 'io1042', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(205, 'ioMotor Neurons TDP-43 M337V/M337V', 'io1046', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(206, 'ioMotor Neurons TDP-43 M337V/WT', 'io1050', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(207, 'ioMotor Neurons TDP-43 A382T/WT', 'io6019', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(208, 'ioMotor Neurons TDP-43 N352S/WT', 'io6017', 30000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(209, 'ioOligodendrocyte-like cells', 'io1028', 27000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(210, 'ioSensory Neurons', 'io1024', 60000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(211, 'ioSkeletal Myocytes', 'io1002', 100000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(212, 'ioSkeletal Myocytes DMD Exon 44 Deletion', 'io1018', 100000, '2025-06-02 11:56:11', '2025-06-02 11:56:11'),
(213, 'ioSkeletal Myocytes DMD Exon 52 Deletion', 'io1019', 100000, '2025-06-02 11:56:11', '2025-06-02 11:56:11');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=214;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
