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
-- Table structure for table `culture_vessels`
--

CREATE TABLE `culture_vessels` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `plate_format` varchar(255) NOT NULL,
  `surface_area_cm2` double DEFAULT NULL,
  `media_volume_per_well_ml` double DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `culture_vessels`
--

INSERT INTO `culture_vessels` (`id`, `plate_format`, `surface_area_cm2`, `media_volume_per_well_ml`, `created_at`, `updated_at`) VALUES
(5, '96-well plate', 0.32, 0.1, NULL, NULL),
(9, '6-well plate', 9.6, 2.5, NULL, NULL),
(10, '12-well plate', 3.5, 1, NULL, NULL),
(11, '24-well plate', 1.9, 0.5, NULL, NULL),
(12, '48-well plate', 1.1, 0.25, NULL, NULL),
(14, '384-well plate', 0.056, 0.03, NULL, NULL),
(15, 'Other', 0, 0, NULL, '2025-06-11 11:22:44');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `culture_vessels`
--
ALTER TABLE `culture_vessels`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `culture_vessels`
--
ALTER TABLE `culture_vessels`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
