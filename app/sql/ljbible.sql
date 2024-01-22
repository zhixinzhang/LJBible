CREATE TABLE `books` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `book_name` varchar(10) UNIQUE NOT NULL,
  `book_name_abbreviation` varchar(5) UNIQUE NOT NULL,
  `new_or_old` varchar(5),
  `version` varchar(10),
  `create_time` varchar(255),
  `author` varchar(10),
  `descriptions` varchar(100),
  `ezoe_link` varchar(100),
  `created_at` timestamp
);

CREATE TABLE `chapters` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `chapter_num` integer,
  `body` text,
  `ezoe_link` varchar(100),
  `book_id` integer,
  `created_at` timestamp
);

CREATE TABLE `titles` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `title` varchar(255),
  `level` integer,
  `version` varchar(10),
  `ezoe_link` varchar(100),
  `chapater_id` integer NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `verses` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `verse_num` integer,
  `original_content` varchar(300),
  `content_with_mark` varchar(300),
  `content_structure` varchar(255),
  `version` varchar(50),
  `author` varchar(50),
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

ALTER TABLE `chapters` ADD FOREIGN KEY (`book_id`) REFERENCES `books` (`id`);

ALTER TABLE `titles` ADD FOREIGN KEY (`chapater_id`) REFERENCES `chapters` (`id`);

ALTER TABLE `verses` ADD FOREIGN KEY (`chapater_id`) REFERENCES `chapters` (`id`);

ALTER TABLE `comments` ADD FOREIGN KEY (`verse_id`) REFERENCES `verses` (`id`);

ALTER TABLE `beads` ADD FOREIGN KEY (`verse_id`) REFERENCES `verses` (`id`);
