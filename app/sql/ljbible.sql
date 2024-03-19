CREATE TABLE `books` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `book_name_cn` varchar(30) UNIQUE NOT NULL,
  `abbrevation_cn` varchar(30) UNIQUE NOT NULL,
  `book_name_eng` varchar(30) UNIQUE NOT NULL,
  `abbrevation_eng` varchar(30) UNIQUE NOT NULL,
  `new_or_old` varchar(30),
  `book_type` varchar(10),
  `ac_bc_time` varchar(30),
  `location` varchar(30),
  `author` varchar(10),
  `chapter_num` integer,
  `created_at` timestamp
);

CREATE TABLE `book_contents` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `book_name_cn` varchar(30) UNIQUE NOT NULL,
  `version` varchar(50),
  `descriptions` varchar(500),
  `crawler_link` varchar(100),
  `book_id` integer,
  `created_at` timestamp
);

CREATE TABLE `chapters` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `chapter_num` integer,
  `body` text,
  `crawler_link` varchar(100),
  `book_content_id` integer,
  `created_at` timestamp
);

CREATE TABLE `titles` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `title` varchar(100),
  `level` integer,
  `version` varchar(10),
  `crawler_link` varchar(100),
  `chapter_id` integer NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `verses` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `verse_num` integer,
  `verse_level` varchar(10),
  `verse_gold` bool,
  `verse_liked` bool,
  `chapter_num` integer NOT NULL,
  `chapter_id` integer NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `verse_contents` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `original_content` varchar(300),
  `content_with_mark` varchar(300),
  `version` varchar(50),
  `crawler_link` varchar(100),
  `verse_id` integer NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `comments` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `comment_num` integer,
  `mark` integer,
  `content` varchar(10000) NOT NULL,
  `verse_content_id` integer,
  `crawler_link` varchar(100),
  `created_at` timestamp
);

CREATE TABLE `beads` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `bead_num` varchar(10),
  `bead_range` varchar(50),
  `mark` varchar(10),
  `content` varchar(10000) NOT NULL,
  `verse_content_id` integer,
  `crawler_link` varchar(100),
  `created_at` timestamp
);

CREATE TABLE `bead_contents` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `used_cn_abbrevation` varchar(10) NOT NULL,
  `used_eng_abbrevation` varchar(10) NOT NULL,
  `located_cn_abbrevation` varchar(10) NOT NULL,
  `located_eng_abbrevation` varchar(10) NOT NULL,
  `used_chapter_num` integer,
  `used_verse_num` integer,
  `located_chapter_num` integer,
  `located_verse_num` integer,
  `content` varchar(1000) NOT NULL,
  `original_content` varchar(1000) NOT NULL,
  `bead_id` integer,
  `verse_content_id` integer,
  `crawler_link` varchar(100),
  `created_at` timestamp
);

ALTER TABLE `book_contents` ADD FOREIGN KEY (`book_id`) REFERENCES `books` (`id`);

ALTER TABLE `chapters` ADD FOREIGN KEY (`book_content_id`) REFERENCES `book_contents` (`id`);

ALTER TABLE `titles` ADD FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`);

ALTER TABLE `verses` ADD FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`);

ALTER TABLE `verse_contents` ADD FOREIGN KEY (`id`) REFERENCES `verses` (`id`);

ALTER TABLE `comments` ADD FOREIGN KEY (`verse_content_id`) REFERENCES `verse_contents` (`id`);

ALTER TABLE `beads` ADD FOREIGN KEY (`verse_content_id`) REFERENCES `verse_contents` (`id`);

ALTER TABLE `bead_contents` ADD FOREIGN KEY (`bead_id`) REFERENCES `beads` (`id`);

ALTER TABLE `bead_contents` ADD FOREIGN KEY (`verse_content_id`) REFERENCES `verse_contents` (`id`);
