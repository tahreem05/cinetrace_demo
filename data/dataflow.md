##CineTrace Dataflow
Data Input
Admins add films, directors, cinematographers, genres, and influence relationships.
Users create accounts, reviews, and watchlists.
Database Flow
Films table acts as the central entity.
Films connect to Directors and Cinematographers through foreign keys.
Genres are linked using Film_Genres.
Influence_Links creates self-referencing film relationships.
Reviews depend on both Users and Films.
Watchlists connect Users and Films through Watchlist_Items.
Outputs
Film detail pages
Influence chain exploration
Director profiles
Reporting queries
Review displays
Statistics and analytics
Future AI/recommendation inputs