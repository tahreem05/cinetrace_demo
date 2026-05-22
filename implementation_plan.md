# Goal Description

Implement the full suite of user roles, data relationships, and views (A through E) for CineTrace as defined by the application architecture rules. This includes adding authentication, user watchlists, cinematic movements tracking, and an admin moderation panel. The application will continue to use the existing CSV schema, utilizing Python to read and write to the CSV files to maintain state.

## User Review Required

> [!IMPORTANT]
> **Data Persistence via CSV**: I will implement the write functionality (adding reviews, creating watchlists, voting, flagging) by reading/writing directly to your existing CSV files (`reviews.csv`, `watchlists.csv`, etc.). Is this acceptable, or are you intending to migrate to a real SQL database during this session? Assuming CSVs for now based on "make do with what is already present".

> [!WARNING]
> **Authentication Security**: For rapid prototyping, I will implement a basic `Flask.session` login system. Passwords in the `users.csv` appear to be hashed (e.g., SHA-256). I will add a simple login form that verifies against these hashes (or plain text if you prefer for testing).

## Open Questions

- **Passwords**: Do you know the plain text password for the admin/user accounts in `users.csv`, or should I provide a backdoor/dropdown just for testing purposes so you can easily switch roles without needing the real passwords?
- **Influence Voting**: When a user clicks upvote/downvote on an "Inspired By" link, should that refresh the page, or do you want an asynchronous AJAX/fetch call to update it instantly? (I plan to use AJAX for a smoother Netflix-like experience).

## Proposed Changes

### Backend Enhancements (`app.py`)
- **Session Management**: Integrate `Flask.secret_key` and session tracking for `user_id` and `role`.
- **New CSV Writers**: Create helper functions (`add_review`, `create_watchlist`, `flag_review`, `vote_influence`) that append to or rewrite the respective CSV files to persist state.
- **Data Model Enrichment**: 
  - Update `get_film_by_id` to include `Cinematographers` (1:1), `Film_Movements`, and `Crew_Members` (filtering by `leadp`).
  - Calculate net influence scores for `Influence_Links` by joining with `Influence_Votes`.
- **New Routes**:
  - `/login`, `/logout` (Authentication)
  - `/movements` (View C)
  - `/watchlists` (View D)
  - `/admin` (View E)
  - `/api/review`, `/api/vote`, `/api/watchlist/add`, `/api/review/moderate` (AJAX endpoints)

### Frontend Views (`templates/`)

#### [MODIFY] `base.html`
- Update the global navigation to include links based on session role:
  - Guest: `Login`
  - User: `My Watchlists`, `Logout`
  - Admin: `Admin Panel`, `My Watchlists`, `Logout`
- Include basic styling for the new forms and admin tables.

#### [MODIFY] `index.html` & Modal Logic (View A & B)
- **View A**: Ensure the Statistical Badges at the top dynamically count total films, directors, and active users (from `users.csv`).
- **View B (Modal/Detail)**: 
  - Show Cinematographer alongside Director.
  - Highlight "Lead Crew" members dynamically.
  - Display Cinematic Movements tags.
  - **Influence Votes**: Add small up/down arrow icons next to "Inspired By" links, showing net score.
  - **Reviews**: Add a "Write a Review" form block for logged-in users. Add a "Flag 🚩" button for Admins on each review.
  - **Watchlist**: Add an "Add to Watchlist" button for logged-in users.

#### [NEW] `movements.html` (View C)
- A directory page listing all `Cinematic_Movements` (origin, years, description).
- Clicking a movement displays a filtered grid of assigned films.

#### [NEW] `watchlists.html` (View D)
- A personal workspace for users to create a new watchlist (with `is_public` toggle).
- Displays their lists and the nested films, with a "Remove" button for each film.

#### [NEW] `admin.html` (View E)
- A table-based moderation feed showing all reviews where `is_flagged = 1`.
- Buttons to "Dismiss Flag" (resets to 0) or "Delete Review" (removes from CSV).

#### [NEW] `login.html`
- A sleek, dark-themed login form.

## Verification Plan

### Automated Tests
- Server restart and syntax verification in Flask.

### Manual Verification
- **Login as Admin**: Access the Admin Panel, flag a review on a film profile, verify it appears in the Admin Panel, and then delete it.
- **Login as User**: Create a Watchlist, add a film to it, write a review, and upvote an influence link. Verify all CSVs persist the changes.
- **Guest**: Verify restricted areas redirect to login. Ensure the Cinematic Movements page displays correctly.
