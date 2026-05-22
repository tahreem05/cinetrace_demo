use cinetrace;


/* =========================================================
   M5: DATA POPULATION VALIDATION QUERIES
   Database: cinetrace
========================================================= */


/* =========================================================
   1. ROW COUNT VALIDATION
   Confirms data exists in each table
========================================================= */

SELECT COUNT(*) AS directors_count FROM Directors;
SELECT COUNT(*) AS cinematographers_count FROM Cinematographers;
SELECT COUNT(*) AS films_count FROM Films;
SELECT COUNT(*) AS genres_count FROM Genres;
SELECT COUNT(*) AS film_genres_count FROM Film_Genres;
SELECT COUNT(*) AS influence_links_count FROM Influence_Links;
SELECT COUNT(*) AS movements_count FROM Cinematic_Movements;
SELECT COUNT(*) AS film_movements_count FROM Film_Movements;
SELECT COUNT(*) AS crew_members_count FROM Crew_Members;
SELECT COUNT(*) AS film_crew_count FROM Film_Crew;
SELECT COUNT(*) AS awards_count FROM Awards;
SELECT COUNT(*) AS users_count FROM Users;
SELECT COUNT(*) AS reviews_count FROM Reviews;
SELECT COUNT(*) AS watchlists_count FROM Watchlists;
SELECT COUNT(*) AS watchlist_items_count FROM Watchlist_Items;
SELECT COUNT(*) AS influence_votes_count FROM Influence_Votes;


/* =========================================================
   2. NULL CHECKS ON KEY COLUMNS
   Ensures important foreign/primary keys are not NULL
========================================================= */

SELECT * 
FROM Films
WHERE film_id IS NULL
   OR director_id IS NULL
   OR cinematographer_id IS NULL;

SELECT *
FROM Reviews
WHERE review_id IS NULL
   OR user_id IS NULL
   OR film_id IS NULL;

SELECT *
FROM Film_Genres
WHERE film_id IS NULL
   OR genre_id IS NULL;

SELECT *
FROM Film_Crew
WHERE film_id IS NULL
   OR person_id IS NULL;

SELECT *
FROM Watchlists
WHERE list_id IS NULL
   OR user_id IS NULL;

SELECT *
FROM Watchlist_Items
WHERE list_id IS NULL
   OR film_id IS NULL;


/* =========================================================
   3. FOREIGN KEY / JOIN INTEGRITY CHECKS
   Confirms referenced records actually exist
========================================================= */

-- Films linked correctly to Directors
SELECT f.film_id, f.title, d.name AS director_name
FROM Films f
JOIN Directors d
ON f.director_id = d.director_id;

-- Films linked correctly to Cinematographers
SELECT f.film_id, f.title, c.name AS cinematographer_name
FROM Films f
JOIN Cinematographers c
ON f.cinematographer_id = c.cinematographer_id;

-- Reviews linked correctly to Users and Films
SELECT r.review_id,
       u.username,
       f.title,
       r.rating
FROM Reviews r
JOIN Users u
ON r.user_id = u.user_id
JOIN Films f
ON r.film_id = f.film_id;

-- Film genres integrity check
SELECT f.title,
       g.name AS genre
FROM Film_Genres fg
JOIN Films f
ON fg.film_id = f.film_id
JOIN Genres g
ON fg.genre_id = g.genre_id;

-- Watchlist integrity check
SELECT w.list_name,
       u.username,
       f.title
FROM Watchlist_Items wi
JOIN Watchlists w
ON wi.list_id = w.list_id
JOIN Users u
ON w.user_id = u.user_id
JOIN Films f
ON wi.film_id = f.film_id;


/* =========================================================
   END OF VALIDATION
========================================================= */
