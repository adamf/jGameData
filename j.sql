CREATE TABLE IF NOT EXISTS GAME (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    jarchiveID INTEGER NOT NULL,
    playDate VARCHAR(255),
    firstPlayer INTEGER,
    firstScore INTEGER,
    secondPlayer INTEGER,
    secondScore INTEGER,
    thirdPlayer INTEGER,
    thirdScore INTEGER
    );

CREATE TABLE IF NOT EXISTS CATEGORY (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    game INTEGER NOT NULL,
    round INTEGER NOT NULL,
    boardPosition INTEGER
    );

CREATE TABLE IF NOT EXISTS PLAYER (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    fullName VARCHAR(255) NOT NULL,
    nick VARCHAR(255) NOT NULL,
    description VARCHAR(255)
    );

CREATE TABLE IF NOT EXISTS CLUE (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    text VARCHAR(255) NOT NULL,
    game INTEGER NOT NULL,
    category INTEGER NOT NULL,
    value INTEGER,
    answer VARCHAR(255) NOT NULL,
    isDD INTEGER NOT NULL,
    pickIndex INTEGER
    );

CREATE TABLE IF NOT EXISTS ANSWER (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    player VARCHAR(255) NOT NULL,
    clue INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    wager INTEGER,
    turn INTEGER,
    text VARCHAR(255)
    );
