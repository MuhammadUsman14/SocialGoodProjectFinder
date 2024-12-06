DROP DATABASE if exists social_good;
CREATE DATABASE social_good;

use social_good;

drop table if exists Users;
create table Users (
	user_id       INT       not null     primary key      auto_increment,
	first_name       VARCHAR(75)        not null,
	last_name        VARCHAR(80),
	email            VARCHAR(140)       unique       not null,
	password_hash    VARCHAR(255)       not null,
	mobile_number    VARCHAR(20)        unique,
	address          VARCHAR(255),
	location_lat         DECIMAL(9, 6),
	location_lon         DECIMAL(9, 6),
	created_at       DATETIME        default     current_timestamp      not null
);

ALTER TABLE Users AUTO_INCREMENT = 12100;

-- Create table skills
drop table if exists Skills;
create table Skills (
	skill_id       INT       not null     primary key      auto_increment,
	skill_name       VARCHAR(100)       unique       not null
);

ALTER TABLE Skills AUTO_INCREMENT = 00001;


-- Create table UserSkills
drop table if exists UserSkills;
create table UserSkills (
	user_id        INT       not null,
	skill_id       INT       not null,
	PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES Skills(skill_id) ON DELETE CASCADE
);


-- Create table Organization
drop table if exists Organizations;
create table Organizations (
	organization_id        INT       not null     primary key       auto_increment,
	name         VARCHAR(150)       not null,
	contact_name      VARCHAR(150)    ,
	contact_email     VARCHAR(150)         unique,
	contact_phone     VARCHAR(20)           unique,
	website           VARCHAR(255)     not null,
	address           VARCHAR(255)     not null,
	joined_at         DATETIME      default       current_timestamp     not null
);

ALTER TABLE Organizations AUTO_INCREMENT = 00510;


-- Create Volunteer Opportunities;
drop table if exists Volunteer_Opportunities;
create table Volunteer_Opportunities (
	opportunity_id        INT     primary key      auto_increment     not null,
	title        VARCHAR(150)     not null,
	description       TEXT       ,
	required_skills      TEXT,
	location_address      VARCHAR(255)     ,
	location_lat        DECIMAL(9, 6)      ,
	location_lon        DECIMAL(9, 6)       ,
	time_commitment     INT,
	category       VARCHAR(75),
	organization_id       INT,
	start_date        DATE,
	end_date          DATE,
	FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE CASCADE
);

ALTER TABLE Volunteer_Opportunities AUTO_INCREMENT = 10040;

-- Create table Opportunities_Skills
drop table if exists Opportunities_Skills;
create table Opportunities_Skills (
	opportunity_id        INT       not null,
	skill_id       INT       not null,
	PRIMARY KEY (opportunity_id, skill_id),
    FOREIGN KEY (opportunity_id) REFERENCES Volunteer_Opportunities(opportunity_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES Skills(skill_id) ON DELETE CASCADE
);

-- Create User_Opportunities table to track interest in opportunities
DROP TABLE IF EXISTS User_Opportunities;
CREATE TABLE User_Opportunities (
    record_id         INT       NOT NULL      PRIMARY KEY      AUTO_INCREMENT,
    user_id           INT       NOT NULL,
    opportunity_id    INT       NOT NULL,
    expressed_on      DATETIME  DEFAULT CURRENT_TIMESTAMP NOT NULL,
    comment           TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (opportunity_id) REFERENCES Volunteer_Opportunities(opportunity_id) ON DELETE CASCADE
);

ALTER TABLE User_Opportunities AUTO_INCREMENT = 30000;


-- Create VolunteerHours table
DROP TABLE IF EXISTS VolunteerHours;
CREATE TABLE VolunteerHours (
    record_id      INT       NOT NULL      PRIMARY KEY      AUTO_INCREMENT,
    user_id        INT       NOT NULL,
    opportunity_id      INT       NOT NULL,
    hours_volunteered        DECIMAL(5, 2),
    date         DATE        NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (opportunity_id) REFERENCES Volunteer_Opportunities(opportunity_id) ON DELETE CASCADE
);

ALTER TABLE VolunteerHours AUTO_INCREMENT = 00050;


-- Create Donations table
DROP TABLE IF EXISTS Donations;
CREATE TABLE Donations (
    donation_id      INT     NOT NULL     PRIMARY KEY      AUTO_INCREMENT,
    user_id          INT     NOT NULL,
    organization_id      INT      NOT NULL,
    amount        DECIMAL(10,2)       NOT NULL,
    date        DATE         NOT NULL,
    purpose     VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE CASCADE
);

ALTER TABLE Donations AUTO_INCREMENT = 01690;


-- Create Feedback table
DROP TABLE IF EXISTS UserFeedback;
CREATE TABLE UserFeedback (
    review_id       INT      NOT NULL      PRIMARY KEY      AUTO_INCREMENT,
    user_id         INT      NOT NULL,
    opportunity_id     INT      NOT NULL,
    rating         INT           CHECK (rating BETWEEN 1 AND 5),
    comment        TEXT,
    reviewed_on       DATETIME       DEFAULT      CURRENT_TIMESTAMP      NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (opportunity_id) REFERENCES Volunteer_Opportunities(opportunity_id) ON DELETE CASCADE
);

ALTER TABLE UserFeedback AUTO_INCREMENT = 00100;