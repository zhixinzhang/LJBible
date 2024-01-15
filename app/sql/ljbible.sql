CREATE TABLE `books` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `book_name` varchar(255) UNIQUE NOT NULL,
  `book_name_abbreviation` char UNIQUE NOT NULL,
  `new_or_old` char,
  `version` char,
  `create_time` varchar(255),
  `author` char,
  `descriptions` varchar(255),
  `ezoe_link` varchar(100),
  `created_at` timestamp
);

CREATE TABLE `chapaters` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `body` text,
  `ezoe_link` varchar(100),
  `book_id` integer,
  `created_at` timestamp
);

CREATE TABLE `verses` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `original_content` varchar(255),
  `content_with_mark` varchar(255),
  `version` char,
  `author` char,
  `ezoe_link` varchar(100),
  `chapater_number` integer NOT NULL,
  `chapater_id` integer NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `comments` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `prefix_content` varchar(255),
  `content` varchar(255) NOT NULL,
  `verse_id` integer,
  `ezoe_link` varchar(100),
  `created_at` timestamp
);

CREATE TABLE `beads` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `prefix_content` varchar(255),
  `content` varchar(255),
  `verse_id` integer,
  `ezoe_link` varchar(100),
  `created_at` timestamp
);

ALTER TABLE `chapaters` ADD FOREIGN KEY (`book_id`) REFERENCES `books` (`id`);

ALTER TABLE `verses` ADD FOREIGN KEY (`chapater_id`) REFERENCES `chapaters` (`id`);

ALTER TABLE `comments` ADD FOREIGN KEY (`verse_id`) REFERENCES `verses` (`id`);

ALTER TABLE `beads` ADD FOREIGN KEY (`verse_id`) REFERENCES `verses` (`id`);
