-- voice.categories definition

CREATE TABLE `categories` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `gid` varchar(64) COLLATE utf8mb4_bin NOT NULL COMMENT '全局id',
  `created_by` varchar(100) COLLATE utf8mb4_bin NOT NULL COMMENT '创建人',
  `created_at` bigint(20) NOT NULL COMMENT '创建时间',
  `updated_by` varchar(100) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '更新人',
  `updated_at` bigint(20) DEFAULT NULL COMMENT '更新时间',
  `is_deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `name` varchar(255) COLLATE utf8mb4_bin NOT NULL COMMENT '名称',
  PRIMARY KEY (`id`),
  KEY `categories_gid_IDX` (`gid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;


-- voice.episodes definition

CREATE TABLE `episodes` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `gid` varchar(64) COLLATE utf8mb4_bin NOT NULL COMMENT '全局id',
  `created_by` varchar(100) COLLATE utf8mb4_bin NOT NULL COMMENT '创建人',
  `created_at` bigint(20) NOT NULL COMMENT '创建时间',
  `updated_by` varchar(100) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '更新人',
  `updated_at` bigint(20) DEFAULT NULL COMMENT '更新时间',
  `is_deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `podcast_gid` varchar(64) COLLATE utf8mb4_bin NOT NULL COMMENT '全局id',
  `content` longtext COLLATE utf8mb4_bin NOT NULL COMMENT '内容',
  `gen_status` int(11) NOT NULL,
  `order` bigint(20) NOT NULL,
  `voice_resource_id` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL,
  `title` varchar(255) COLLATE utf8mb4_bin NOT NULL COMMENT '标题',
  `episode_size` bigint(20) NOT NULL DEFAULT '0' COMMENT 'audio file size',
  `key` varchar(256) COLLATE utf8mb4_bin DEFAULT NULL,
  `link` varchar(512) COLLATE utf8mb4_bin DEFAULT NULL,
  `cover_resource_id` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '封面资源id',
  `pub_time` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `audios_gid_IDX` (`gid`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=926 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;


-- voice.podcasts definition

CREATE TABLE `podcasts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `gid` varchar(64) COLLATE utf8mb4_bin NOT NULL COMMENT '全局id',
  `created_by` varchar(100) COLLATE utf8mb4_bin NOT NULL COMMENT '创建人',
  `created_at` bigint(20) NOT NULL COMMENT '创建时间',
  `updated_by` varchar(100) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '更新人',
  `updated_at` bigint(20) DEFAULT NULL COMMENT '更新时间',
  `is_deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `source` varchar(64) COLLATE utf8mb4_bin NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `author` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `cover_resource_id` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL,
  `book_resource_id` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL,
  `gen_status` int(11) NOT NULL,
  `description` text CHARACTER SET utf8 COLLATE utf8_bin,
  `language` varchar(64) COLLATE utf8mb4_bin NOT NULL,
  `category_id` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL,
  `share_time` bigint(20) DEFAULT NULL,
  `url` varchar(256) COLLATE utf8mb4_bin DEFAULT NULL,
  `frequency` varchar(128) COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'execute frequency',
  `first_execute_time` bigint(20) DEFAULT NULL,
  `timer_id` varchar(256) COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'id',
  `share_enable` tinyint(4) NOT NULL DEFAULT '0',
  `frequency_value` int(10) unsigned NOT NULL DEFAULT '1',
  `share_token` varchar(256) COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'rss share token',
  PRIMARY KEY (`id`),
  UNIQUE KEY `albums_gid_IDX` (`gid`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;


-- voice.resources definition

CREATE TABLE `resources` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `gid` varchar(100) COLLATE utf8mb4_bin NOT NULL COMMENT '全局id',
  `created_by` varchar(100) COLLATE utf8mb4_bin NOT NULL COMMENT '创建人',
  `created_at` bigint(20) NOT NULL COMMENT '创建时间',
  `updated_by` varchar(100) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '更新人',
  `updated_at` bigint(20) DEFAULT NULL COMMENT '更新时间',
  `is_deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `name` varchar(128) COLLATE utf8mb4_bin NOT NULL COMMENT '资源名称',
  `resource_type` varchar(64) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `resources_gid_IDX` (`gid`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5144 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;


-- voice.users definition

CREATE TABLE `users` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `gid` varchar(100) COLLATE utf8mb4_bin NOT NULL COMMENT '全局id',
  `created_by` varchar(100) COLLATE utf8mb4_bin NOT NULL COMMENT '创建人',
  `created_at` bigint(20) NOT NULL COMMENT '创建时间',
  `updated_by` varchar(100) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '更新人',
  `updated_at` bigint(20) DEFAULT NULL COMMENT '更新时间',
  `is_deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `name` varchar(255) COLLATE utf8mb4_bin NOT NULL COMMENT '用户名称',
  `email` varchar(255) COLLATE utf8mb4_bin NOT NULL COMMENT '用户邮箱',
  PRIMARY KEY (`id`),
  KEY `users_gid_IDX` (`gid`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;