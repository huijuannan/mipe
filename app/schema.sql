-- init database

use mipetest;

DROP TABLE IF EXISTS User;
CREATE TABLE User(
    id INT NOT NULL AUTO_INCREMENT, 
    ghName VARCHAR(45) UNIQUE, 
    email VARCHAR(45),
    PRIMARY KEY(id));

DROP TABLE IF EXISTS Author;
CREATE TABLE Author (
    id INT AUTO_INCREMENT,
    ghName VARCHAR(45) UNIQUE,
    PRIMARY KEY(id));

DROP TABLE IF EXISTS Subscribe;
CREATE TABLE Subscribe (
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    PRIMARY KEY (user_id, book_id));

DROP TABLE IF EXISTS Book;
CREATE TABLE Book (
    id INT AUTO_INCREMENT,
    url VARCHAR(100) UNIQUE,
    name VARCHAR(45),
    author_id INT,
    PRIMARY KEY(id));