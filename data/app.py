"""
CineTrace Flask Application - MySQL Version
Run: python app.py
"""
import sys
import os
import random
from datetime import datetime
from flask import Flask, render_template, jsonify, request, abort, session, redirect, url_for, g
from dotenv import load_dotenv
import mysql.connector

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'cinetrace_super_secret_key_123')

# ── Database Connection ───────────────────────────────────────────────────────

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "8808"),
        database=os.getenv("DB_DATABASE", "cinetrace")
    )

# ── Auth & Context ────────────────────────────────────────────────────────────

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = None
    if user_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
            g.user = cursor.fetchone()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error loading session user: {e}")

@app.context_processor
def inject_global():
    return dict(TMDB_API_KEY=os.getenv('TMDB_API_KEY', '1f4be0841289cfad32ff525e985b1e95'), current_user=g.user)

# ── Domain Logic ──────────────────────────────────────────────────────────────

def get_films():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch films and direct relations (Directors, Cinematographers)
    cursor.execute("""
        SELECT f.*, d.name AS director_name, c.name AS cinematographer_name 
        FROM Films f
        LEFT JOIN Directors d ON f.director_id = d.director_id
        LEFT JOIN Cinematographers c ON f.cinematographer_id = c.cinematographer_id
    """)
    films = cursor.fetchall()
    
    # 2. Fetch genres mapping
    cursor.execute("""
        SELECT fg.film_id, g.name AS genre_name 
        FROM Film_Genres fg
        JOIN Genres g ON fg.genre_id = g.genre_id
    """)
    genres_list = cursor.fetchall()
    genres_map = {}
    for g in genres_list:
        genres_map.setdefault(g['film_id'], []).append(g['genre_name'])
        
    # 3. Fetch reviews statistics
    cursor.execute("""
        SELECT film_id, AVG(rating) as avg_rating, COUNT(*) as review_count 
        FROM Reviews 
        GROUP BY film_id
    """)
    reviews_list = cursor.fetchall()
    reviews_map = {r['film_id']: r for r in reviews_list}
    
    # 4. Fetch awards statistics
    cursor.execute("""
        SELECT film_id, 
               SUM(CASE WHEN outcome = 'Won' THEN 1 ELSE 0 END) as awards_won,
               COUNT(*) as total_awards
        FROM Awards
        GROUP BY film_id
    """)
    awards_list = cursor.fetchall()
    awards_map = {a['film_id']: a for a in awards_list}
    
    cursor.close()
    conn.close()
    
    result = []
    for f in films:
        fid = f['film_id']
        rev = reviews_map.get(fid, {})
        aw = awards_map.get(fid, {})
        
        # Format DECIMAL fields to float
        if f.get('budget'):
            f['budget'] = float(f['budget'])
            
        result.append({
            **f,
            "director_name": f.get("director_name") or f.get("director_id", ""),
            "cinematographer_name": f.get("cinematographer_name") or f.get("cinematographer_id", ""),
            "genres": genres_map.get(fid, []),
            "avg_rating": round(float(rev['avg_rating']), 1) if rev.get('avg_rating') else None,
            "review_count": rev.get('review_count', 0),
            "awards_won": int(aw.get('awards_won') or 0),
            "total_awards": aw.get('total_awards', 0),
        })
    return result

def get_film_by_id(film_id):
    films = get_films()
    for f in films:
        if str(f.get("film_id")) == str(film_id): 
            return f
    return None

def get_influences_for_film(film_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Calculate net votes per link_id from Influence_Votes
    cursor.execute("""
        SELECT link_id, COALESCE(SUM(vote), 0) as net_votes 
        FROM Influence_Votes 
        GROUP BY link_id
    """)
    votes_list = cursor.fetchall()
    votes_map = {str(v['link_id']): int(v['net_votes']) for v in votes_list}
    
    # Fetch influence links where source or target is film_id
    cursor.execute("""
        SELECT il.*, 
               f_src.title AS src_title, 
               f_tgt.title AS tgt_title
        FROM Influence_Links il
        JOIN Films f_src ON il.source_film_id = f_src.film_id
        JOIN Films f_tgt ON il.target_film_id = f_tgt.film_id
        WHERE il.source_film_id = %s OR il.target_film_id = %s
    """, (film_id, film_id))
    links = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    result = {"influenced_by": [], "influenced": []}
    for lnk in links:
        lid = str(lnk["link_id"])
        src = str(lnk["source_film_id"])
        tgt = str(lnk["target_film_id"])
        net_score = votes_map.get(lid, 0)
        
        # Format recorded_at date
        if lnk.get('recorded_at') and hasattr(lnk['recorded_at'], 'strftime'):
            lnk['recorded_at'] = lnk['recorded_at'].strftime("%Y-%m-%d")
            
        if tgt == str(film_id):
            result["influenced_by"].append({
                **lnk, 
                "film_title": lnk.get("src_title", src), 
                "net_votes": net_score
            })
        if src == str(film_id):
            result["influenced"].append({
                **lnk, 
                "film_title": lnk.get("tgt_title", tgt), 
                "net_votes": net_score
            })
            
    # Sort by net votes
    result["influenced_by"] = sorted(result["influenced_by"], key=lambda x: x["net_votes"], reverse=True)
    result["influenced"] = sorted(result["influenced"], key=lambda x: x["net_votes"], reverse=True)
    return result

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    films = get_films()
    hero = sorted([f for f in films if f.get("avg_rating")], key=lambda x: float(x["avg_rating"] or 0), reverse=True)[:1]
    hero = hero[0] if hero else (films[0] if films else {})
    top_rated   = sorted([f for f in films if f.get("avg_rating")], key=lambda x: float(x["avg_rating"] or 0), reverse=True)[:12]
    trending    = random.sample(films, min(12, len(films))) if films else []
    award_films = sorted([f for f in films if f["awards_won"] > 0], key=lambda x: -x["awards_won"])[:12]
    genres_list = sorted({g for f in films for g in f["genres"]})
    
    # Query total users, directors dynamically from DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Directors")
    total_dirs = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return render_template("index.html",
        hero=hero, top_rated=top_rated, trending=trending,
        award_films=award_films, genres=genres_list, 
        total_films=len(films), total_users=total_users, total_dirs=total_dirs)

@app.route("/film/<film_id>")
def film_detail(film_id):
    film = get_film_by_id(film_id)
    if not film: abort(404)
    influences = get_influences_for_film(film_id)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch reviews with usernames
    cursor.execute("""
        SELECT r.*, u.username 
        FROM Reviews r
        JOIN Users u ON r.user_id = u.user_id
        WHERE r.film_id = %s
    """, (film_id,))
    reviews = cursor.fetchall()
    for r in reviews:
        if r.get('created_at') and hasattr(r['created_at'], 'strftime'):
            r['created_at'] = r['created_at'].strftime("%Y-%m-%d %H:%M:%S")
            
    # Fetch key crew members
    cursor.execute("""
        SELECT fc.*, cm.full_name, cm.nationality, cm.specialisation
        FROM Film_Crew fc
        JOIN Crew_Members cm ON fc.person_id = cm.person_id
        WHERE fc.film_id = %s
    """, (film_id,))
    crew = cursor.fetchall()
    lead_crew = [c for c in crew if str(c.get("leadp")) in ("1", "True", "true")]
    
    # Fetch movements
    cursor.execute("""
        SELECT fm.*, cm.name, cm.origin_country, cm.start_year, cm.end_year, cm.description
        FROM Film_Movements fm
        JOIN Cinematic_Movements cm ON fm.movement_id = cm.movement_id
        WHERE fm.film_id = %s
    """, (film_id,))
    film_movements = cursor.fetchall()
    
    # Fetch awards
    cursor.execute("SELECT * FROM Awards WHERE film_id = %s", (film_id,))
    awards = cursor.fetchall()
    
    # Fetch user watchlists
    user_watchlists = []
    if g.user:
        cursor.execute("SELECT * FROM Watchlists WHERE user_id = %s", (g.user['user_id'],))
        user_watchlists = cursor.fetchall()
        
    cursor.close()
    conn.close()
    
    return render_template("film.html",
        film=film, influences=influences, reviews=reviews,
        crew=crew[:8], lead_crew=lead_crew, film_movements=film_movements, awards=awards,
        user_watchlists=user_watchlists)

@app.route("/browse")
def browse():
    films = get_films()
    genre_filter = request.args.get("genre", "")
    sort_by      = request.args.get("sort", "rating")
    search       = request.args.get("q", "").lower()
    
    if genre_filter: films = [f for f in films if genre_filter in f["genres"]]
    if search: films = [f for f in films if search in f.get("title","").lower() or search in f.get("director_name","").lower()]
    
    if sort_by == "rating": films = sorted(films, key=lambda x: float(x.get("avg_rating") or 0), reverse=True)
    elif sort_by == "year": films = sorted(films, key=lambda x: int(x.get("release_year") or 0), reverse=True)
    elif sort_by == "title": films = sorted(films, key=lambda x: x.get("title","").lower())
    elif sort_by == "awards": films = sorted(films, key=lambda x: int(x.get("awards_won") or 0), reverse=True)
    
    genres_list = sorted({g for f in get_films() for g in f["genres"]})
    return render_template("browse.html", films=films, genres=genres_list, genre_filter=genre_filter, sort_by=sort_by, search=search)

@app.route("/directors")
def directors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Directors")
    dirs = cursor.fetchall()
    cursor.close()
    conn.close()
    
    films = get_films()
    dir_films = {}
    for f in films: dir_films.setdefault(f.get("director_id", ""), []).append(f)
    result = []
    for d in dirs:
        dfs = dir_films.get(d["director_id"], [])
        ratings = [float(f["avg_rating"]) for f in dfs if f.get("avg_rating")]
        result.append({**d,
            "film_count": len(dfs),
            "avg_rating": round(sum(ratings)/len(ratings),1) if ratings else None,
            "best_film": sorted(dfs, key=lambda x: float(x.get("avg_rating") or 0), reverse=True)[0] if dfs else None,
        })
    result = sorted(result, key=lambda x: x["film_count"], reverse=True)
    return render_template("directors.html", directors=result)

@app.route("/movements")
def movements():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Cinematic_Movements")
    movs = cursor.fetchall()
    
    selected_mov_id = request.args.get("id")
    selected_movement = None
    movement_films = []
    
    if selected_mov_id:
        cursor.execute("SELECT * FROM Cinematic_Movements WHERE movement_id = %s", (selected_mov_id,))
        selected_movement = cursor.fetchone()
        if selected_movement:
            cursor.execute("SELECT film_id FROM Film_Movements WHERE movement_id = %s", (selected_mov_id,))
            film_ids = [str(r['film_id']) for r in cursor.fetchall()]
            if film_ids:
                all_films = get_films()
                movement_films = [f for f in all_films if str(f['film_id']) in film_ids]
                
    cursor.close()
    conn.close()
    
    return render_template("movements.html", movements=movs, selected_movement=selected_movement, movement_films=movement_films)

@app.route("/watchlists")
def watchlists():
    if not g.user: return redirect(url_for('login'))
    uid = str(g.user['user_id'])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Watchlists WHERE user_id = %s", (uid,))
    lists = cursor.fetchall()
    
    cursor.execute("""
        SELECT wi.*, f.title 
        FROM Watchlist_Items wi
        JOIN Films f ON wi.film_id = f.film_id
    """)
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    films_idx = {str(f["film_id"]): f for f in get_films()}
    
    for lst in lists:
        lid = str(lst["list_id"])
        lst["films"] = []
        for itm in items:
            if str(itm["list_id"]) == lid and str(itm["film_id"]) in films_idx:
                lst["films"].append(films_idx[str(itm["film_id"])])
                
    return render_template("watchlists.html", watchlists=lists)

@app.route("/admin")
def admin_panel():
    if not g.user or g.user.get('role') != 'admin':
        abort(403)
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, u.username, f.title AS film_title
        FROM Reviews r
        JOIN Users u ON r.user_id = u.user_id
        JOIN Films f ON r.film_id = f.film_id
        WHERE r.is_flagged = 1
    """)
    flagged = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template("admin.html", flagged_reviews=flagged)

# ── Auth Routes ───────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE email = %s AND password_hash = %s", (email, password))
        u = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if u:
            session['user_id'] = u['user_id']
            return redirect(url_for('index'))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── API / Mutation Endpoints ──────────────────────────────────────────────────

@app.route("/api/films")
def api_films():
    films = get_films()
    return jsonify(films)

@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").lower()
    if not q:
        return jsonify([])
    films = get_films()
    results = [f for f in films if q in f.get("title", "").lower() or q in f.get("director_name", "").lower()]
    return jsonify(results[:8])

@app.route("/api/film_details/<film_id>")
def api_film_details(film_id):
    film = get_film_by_id(film_id)
    if not film: return jsonify({"error": "Not found"}), 404
    influences = get_influences_for_film(film_id)
    return jsonify({"film": film, "influences": influences})

@app.route("/api/review", methods=["POST"])
def api_add_review():
    if not g.user: return jsonify({"error": "Unauthorized"}), 401
    r_data = request.json
    film_id = r_data.get("film_id")
    body = r_data.get("body")
    rating = r_data.get("rating")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(review_id), 0) + 1 FROM Reviews")
    new_id = cursor.fetchone()[0]
    
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO Reviews (review_id, user_id, film_id, body, rating, created_at, is_flagged)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (new_id, g.user["user_id"], film_id, body, rating, created_at, 0))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": True})

@app.route("/api/vote", methods=["POST"])
def api_vote():
    if not g.user: return jsonify({"error": "Unauthorized"}), 401
    v_data = request.json
    link_id = str(v_data.get("link_id"))
    vote_val = v_data.get("vote") # 1 or -1
    uid = g.user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if vote already exists for this link and user
    cursor.execute("SELECT * FROM Influence_Votes WHERE link_id = %s AND user_id = %s", (link_id, uid))
    existing = cursor.fetchone()
    
    voted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if existing:
        cursor.execute("""
            UPDATE Influence_Votes 
            SET vote = %s, voted_at = %s 
            WHERE vote_id = %s
        """, (vote_val, voted_at, existing['vote_id']))
    else:
        cursor.execute("SELECT COALESCE(MAX(vote_id), 0) + 1 FROM Influence_Votes")
        new_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO Influence_Votes (vote_id, link_id, user_id, vote, voted_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (new_id, link_id, uid, vote_val, voted_at))
        
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": True})

@app.route("/api/review/moderate", methods=["POST"])
def api_moderate_review():
    if not g.user or g.user.get("role") != "admin": return jsonify({"error": "Forbidden"}), 403
    m_data = request.json
    rev_id = str(m_data.get("review_id"))
    action = m_data.get("action") # 'delete', 'dismiss', 'flag'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if action == "delete":
        cursor.execute("DELETE FROM Reviews WHERE review_id = %s", (rev_id,))
    elif action == "dismiss":
        cursor.execute("UPDATE Reviews SET is_flagged = 0 WHERE review_id = %s", (rev_id,))
    elif action == "flag":
        cursor.execute("UPDATE Reviews SET is_flagged = 1 WHERE review_id = %s", (rev_id,))
        
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/watchlist/add", methods=["POST"])
def api_watchlist_add():
    if not g.user: return jsonify({"error": "Unauthorized"}), 401
    w_data = request.json
    list_name = w_data.get("list_name", "Personal Watchlist")
    film_id = w_data.get("film_id")
    uid = g.user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if watchlist exists for user
    cursor.execute("SELECT * FROM Watchlists WHERE user_id = %s AND list_name = %s", (uid, list_name))
    user_list = cursor.fetchone()
    
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not user_list:
        cursor.execute("SELECT COALESCE(MAX(list_id), 0) + 1 FROM Watchlists")
        new_lid = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO Watchlists (list_id, user_id, list_name, is_public, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (new_lid, uid, list_name, 0, created_at))
        conn.commit()
        
        cursor.execute("SELECT * FROM Watchlists WHERE list_id = %s", (new_lid,))
        user_list = cursor.fetchone()
        
    if film_id:
        # Check if already added
        cursor.execute("SELECT * FROM Watchlist_Items WHERE list_id = %s AND film_id = %s", (user_list["list_id"], film_id))
        existing_item = cursor.fetchone()
        if not existing_item:
            added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO Watchlist_Items (list_id, film_id, added_at)
                VALUES (%s, %s, %s)
            """, (user_list["list_id"], film_id, added_at))
            conn.commit()
            
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/watchlist/remove", methods=["POST"])
def api_watchlist_remove():
    if not g.user: return jsonify({"error": "Unauthorized"}), 401
    w_data = request.json
    list_id = str(w_data.get("list_id"))
    film_id = str(w_data.get("film_id"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Watchlist_Items WHERE list_id = %s AND film_id = %s", (list_id, film_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  🎬  CineTrace (MySQL Mode) is running!")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)