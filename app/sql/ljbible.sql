CREATE TABLE `books` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `book_name` varchar(30) UNIQUE NOT NULL,
  `book_name_abbreviation` varchar(30) UNIQUE NOT NULL,
  `book_name_eng` varchar(30) UNIQUE NOT NULL,
  `book_name_abbreviation_eng` varchar(30) UNIQUE NOT NULL,
  `book_type` varchar(30),
  `chapter_count` integer,
  `new_or_old` varchar(5),
  `version` varchar(50),
  `author` varchar(30),
  `descriptions` varchar(500),
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
  `title` varchar(100),
  `level` integer,
  `version` varchar(10),
  `ezoe_link` varchar(100),
  `chapter_id` integer NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `verses` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `verse_num` integer,
  `verse_level` varchar(10),
  `verse_gold` bool,
  `verse_liked` bool,
  `chapter_number` integer NOT NULL,
  `chapter_id` integer NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `verse_contents` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `original_content` varchar(300),
  `content_with_mark` varchar(300),
  `version` varchar(50),
  `ezoe_link` varchar(100),
  `verse_id` integer NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `comments` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `comment_num` integer,
  `mark` integer,
  `content` varchar(10000) NOT NULL,
  `verse_id` integer,
  `ezoe_link` varchar(100),
  `created_at` timestamp
);

CREATE TABLE `beads` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `bead_num` varchar(10),
  `mark` varchar(10),
  `content` varchar(10000) NOT NULL,
  `verse_id` integer,
  `ezoe_link` varchar(100),
  `created_at` timestamp
);

ALTER TABLE `chapters` ADD FOREIGN KEY (`book_id`) REFERENCES `books` (`id`);

ALTER TABLE `titles` ADD FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`);

ALTER TABLE `verses` ADD FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`);

ALTER TABLE `comments` ADD FOREIGN KEY (`verse_id`) REFERENCES `verses` (`id`);

ALTER TABLE `verse_contents` ADD FOREIGN KEY (`id`) REFERENCES `verses` (`id`);

ALTER TABLE `beads` ADD FOREIGN KEY (`verse_id`) REFERENCES `verses` (`id`);
