CREATE DATABASE cinetrace;
USE cinetrace;

CREATE TABLE Directors (
    director_id INT PRIMARY KEY,
    name VARCHAR(100),
    nationality VARCHAR(50),
    birth_year INT,
    biography TEXT
);

CREATE TABLE Cinematographers (
    cinematographer_id INT PRIMARY KEY,
    name VARCHAR(100),
    nationality VARCHAR(50),
    birth_year INT
);
CREATE TABLE Films (
    film_id INT PRIMARY KEY,
    title VARCHAR(100),
    release_year INT,
    country VARCHAR(50),
    synopsis TEXT,
    director_id INT,
    cinematographer_id INT,
    budget DECIMAL(12,2),
    language VARCHAR(50),
    runtime_min INT,

    FOREIGN KEY (director_id) REFERENCES Directors(director_id),
    FOREIGN KEY (cinematographer_id) REFERENCES Cinematographers(cinematographer_id)
);


CREATE TABLE Genres (
    genre_id INT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    description TEXT
);

CREATE TABLE Film_Genres (
    film_id INT,
    genre_id INT,

    PRIMARY KEY (film_id, genre_id),
    FOREIGN KEY (film_id) REFERENCES Films(film_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE Influence_Links (
    link_id INT PRIMARY KEY,
    source_film_id INT,
    target_film_id INT,
    influence_type VARCHAR(50),
    evidence_url TEXT,
    notes TEXT,
    recorded_at DATE,

    FOREIGN KEY (source_film_id) REFERENCES Films(film_id),
    FOREIGN KEY (target_film_id) REFERENCES Films(film_id)
);


CREATE TABLE Cinematic_Movements (
    movement_id INT PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    origin_country VARCHAR(50),
    start_year INT,
    end_year INT,
    description TEXT
);

CREATE TABLE Film_Movements (
    film_id INT,
    movement_id INT,
    role VARCHAR(50),

    PRIMARY KEY (film_id, movement_id),
    FOREIGN KEY (film_id) REFERENCES Films(film_id),
    FOREIGN KEY (movement_id) REFERENCES Cinematic_Movements(movement_id)
);

CREATE TABLE Crew_Members (
    person_id INT PRIMARY KEY,
    full_name VARCHAR(100),
    nationality VARCHAR(50),
    specialisation VARCHAR(50)
);


CREATE TABLE Film_Crew (
    film_id INT,
    person_id INT,
    role VARCHAR(50),
    leadp BOOLEAN,

    PRIMARY KEY (film_id, person_id),
    FOREIGN KEY (film_id) REFERENCES Films(film_id),
    FOREIGN KEY (person_id) REFERENCES Crew_Members(person_id)
);


CREATE TABLE Awards (
    award_id INT PRIMARY KEY,
    film_id INT,
    award_name VARCHAR(100),
    category VARCHAR(100),
    year INT,
    outcome VARCHAR(50),

    FOREIGN KEY (film_id) REFERENCES Films(film_id)
);

CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(20),
    created_at TIMESTAMP
);

CREATE TABLE Reviews (
    review_id INT PRIMARY KEY,
    user_id INT,
    film_id INT,
    body TEXT,
    rating TINYINT,
    created_at TIMESTAMP,
    is_flagged BOOLEAN,

    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (film_id) REFERENCES Films(film_id)
);

CREATE TABLE Watchlists (
    list_id INT PRIMARY KEY,
    user_id INT,
    list_name VARCHAR(100),
    is_public BOOLEAN,
    created_at TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
CREATE TABLE Watchlist_Items (
    list_id INT,
    film_id INT,
    added_at TIMESTAMP,

    PRIMARY KEY (list_id, film_id),
    FOREIGN KEY (list_id) REFERENCES Watchlists(list_id),
    FOREIGN KEY (film_id) REFERENCES Films(film_id)
);

CREATE TABLE Influence_Votes (
    vote_id INT PRIMARY KEY,
    link_id INT,
    user_id INT,
    vote TINYINT,
    voted_at TIMESTAMP,

    FOREIGN KEY (link_id) REFERENCES Influence_Links(link_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

SELECT * FROM Crew_Members;


SELECT * FROM users;
SELECT * FROM genres;
SELECT * FROM Crew_Members;
SELECT * FROM Reviews;
SELECT COUNT(*) FROM Directors;
SELECT COUNT(*) FROM Directors;
SELECT COUNT(*) FROM Films;
