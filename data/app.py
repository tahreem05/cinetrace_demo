"""
CineTrace Flask Application
Run: python app.py
"""
import sys, csv, os, random
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')
from flask import Flask, render_template, jsonify, request, abort, session, redirect, url_for, g
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'cinetrace_super_secret_key_123')

DATA_DIR = os.path.join(os.path.dirname(__file__), "cinetrace_csvs")

# ── Data Loading & Saving ─────────────────────────────────────────────────────

def load_csv(name):
    path = os.path.join(DATA_DIR, f"{name}.csv")
    if not os.path.exists(path): return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def save_csv(name, data_list):
    if not data_list: return
    path = os.path.join(DATA_DIR, f"{name}.csv")
    keys = data_list[0].keys()
    with open(path, 'w', newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data_list)
    if name in _cache:
        _cache[name] = data_list # update cache

_cache = {}
def data(name):
    if name not in _cache: _cache[name] = load_csv(name)
    return _cache[name]

# ── Auth & Context ────────────────────────────────────────────────────────────

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = None
    if user_id:
        users = data('users')
        for u in users:
            if str(u.get('user_id')) == str(user_id):
                g.user = u
                break

@app.context_processor
def inject_global():
    return dict(TMDB_API_KEY=os.getenv('TMDB_API_KEY', ''), current_user=g.user)

# ── Domain Logic ──────────────────────────────────────────────────────────────

def get_films():
    films = data("films")
    directors = {d["director_id"]: d for d in data("directors")}
    cinematographers = {c["cinematographer_id"]: c for c in data("cinematographers")}
    
    genres_map = {}
    for fg in data("film_genres"):
        genres_map.setdefault(fg["film_id"], []).append(fg["genre_id"])
    genre_names = {g["genre_id"]: g["name"] for g in data("genres")}
    
    awards_map = {}
    for a in data("awards"):
        awards_map.setdefault(a["film_id"], []).append(a)
    
    reviews_map = {}
    for r in data("reviews"):
        reviews_map.setdefault(r["film_id"], []).append(r)

    result = []
    for f in films:
        fid = f.get("film_id", "")
        dir_obj = directors.get(f.get("director_id", ""), {})
        cin_obj = cinematographers.get(f.get("cinematographer_id", ""), {})
        
        gids = genres_map.get(fid, [])
        genres = [genre_names.get(g, "") for g in gids if genre_names.get(g)]
        
        revs = reviews_map.get(fid, [])
        ratings = [float(r["rating"]) for r in revs if r.get("rating")]
        avg_rating = round(sum(ratings)/len(ratings), 1) if ratings else None
        
        film_awards = awards_map.get(fid, [])
        won = sum(1 for a in film_awards if a.get("won") in ("Yes", "1") or a.get("outcome") == "Won")
        
        result.append({
            **f,
            "director_name": dir_obj.get("name", f.get("director_id", "")),
            "cinematographer_name": cin_obj.get("name", f.get("cinematographer_id", "")),
            "genres": genres,
            "avg_rating": avg_rating,
            "review_count": len(revs),
            "awards_won": won,
            "total_awards": len(film_awards),
        })
    return result

def get_film_by_id(film_id):
    for f in get_films():
        if str(f.get("film_id")) == str(film_id): return f
    return None

def get_influences_for_film(film_id):
    links = data("influence_links")
    films_idx = {f["film_id"]: f for f in data("films")}
    votes = data("influence_votes")
    
    # Calculate net votes per link
    link_votes = {}
    for v in votes:
        lid = str(v.get('link_id'))
        link_votes[lid] = link_votes.get(lid, 0) + int(v.get('vote', 0))

    result = {"influenced_by": [], "influenced": []}
    for lnk in links:
        lid = str(lnk.get("link_id", ""))
        src = str(lnk.get("source_film_id", ""))
        tgt = str(lnk.get("influenced_film_id", lnk.get("target_film_id", "")))
        net_score = link_votes.get(lid, 0)
        
        if tgt == str(film_id):
            src_film = films_idx.get(src, {})
            result["influenced_by"].append({**lnk, "film_title": src_film.get("title", src), "net_votes": net_score})
        if src == str(film_id):
            tgt_film = films_idx.get(tgt, {})
            result["influenced"].append({**lnk, "film_title": tgt_film.get("title", tgt), "net_votes": net_score})
            
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
    
    total_users = len(data("users"))
    total_dirs = len(data("directors"))
    return render_template("index.html",
        hero=hero, top_rated=top_rated, trending=trending,
        award_films=award_films, genres=genres_list, 
        total_films=len(films), total_users=total_users, total_dirs=total_dirs)

@app.route("/film/<film_id>")
def film_detail(film_id):
    film = get_film_by_id(film_id)
    if not film: abort(404)
    influences = get_influences_for_film(film_id)
    reviews = [r for r in data("reviews") if str(r.get("film_id")) == str(film_id)]
    
    # Crew and Leadp
    crew = []
    lead_crew = []
    for fc in data("film_crew"):
        if str(fc.get("film_id")) == str(film_id):
            for cm in data("crew_members"):
                if str(cm.get("person_id")) == str(fc.get("person_id")):
                    crew_member = {**fc, **cm}
                    crew.append(crew_member)
                    if str(fc.get("leadp")) == "1":
                        lead_crew.append(crew_member)
                    break
                    
    # Movements
    film_movements = []
    for fm in data("film_movements"):
        if str(fm.get("film_id")) == str(film_id):
            for m in data("cinematic_movements"):
                if str(m.get("movement_id")) == str(fm.get("movement_id")):
                    film_movements.append(m)
                    break

    awards = [a for a in data("awards") if str(a.get("film_id")) == str(film_id)]
    return render_template("film.html",
        film=film, influences=influences, reviews=reviews,
        crew=crew[:8], lead_crew=lead_crew, film_movements=film_movements, awards=awards)

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
    elif sort_by == "title": films = sorted(films, key=lambda x: x.get("title",""))
    
    genres_list = sorted({g for f in get_films() for g in f["genres"]})
    return render_template("browse.html", films=films, genres=genres_list, genre_filter=genre_filter, sort_by=sort_by, search=search)

@app.route("/directors")
def directors():
    dirs = data("directors")
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
    movs = data("cinematic_movements")
    return render_template("movements.html", movements=movs)

@app.route("/watchlists")
def watchlists():
    if not g.user: return redirect(url_for('login'))
    uid = str(g.user['user_id'])
    lists = [w for w in data("watchlists") if str(w.get("user_id")) == uid]
    items = data("watchlist_items")
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
    # Flagged reviews
    reviews = data("reviews")
    flagged = [r for r in reviews if str(r.get("is_flagged")) == "1"]
    return render_template("admin.html", flagged_reviews=flagged)

# ── Auth Routes ───────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        for u in data("users"):
            if u.get("email") == email and u.get("password_hash") == password:
                session['user_id'] = u['user_id']
                return redirect(url_for('index'))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── API / Mutation Endpoints ──────────────────────────────────────────────────

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
    reviews = data("reviews")
    new_id = str(max([int(r.get("review_id", 0)) for r in reviews] + [0]) + 1)
    new_rev = {
        "review_id": new_id,
        "user_id": g.user["user_id"],
        "film_id": r_data.get("film_id"),
        "body": r_data.get("body"),
        "rating": r_data.get("rating"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_flagged": "0"
    }
    reviews.append(new_rev)
    save_csv("reviews", reviews)
    return jsonify({"success": True})

@app.route("/api/vote", methods=["POST"])
def api_vote():
    if not g.user: return jsonify({"error": "Unauthorized"}), 401
    v_data = request.json
    link_id = str(v_data.get("link_id"))
    vote_val = v_data.get("vote") # 1 or -1
    
    votes = data("influence_votes")
    uid = str(g.user["user_id"])
    
    # Check if existing
    existing = next((v for v in votes if str(v.get("link_id")) == link_id and str(v.get("user_id")) == uid), None)
    if existing:
        existing["vote"] = str(vote_val)
        existing["voted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        new_id = str(max([int(v.get("vote_id", 0)) for v in votes] + [0]) + 1)
        votes.append({
            "vote_id": new_id,
            "link_id": link_id,
            "user_id": uid,
            "vote": str(vote_val),
            "voted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    save_csv("influence_votes", votes)
    return jsonify({"success": True})

@app.route("/api/review/moderate", methods=["POST"])
def api_moderate_review():
    if not g.user or g.user.get("role") != "admin": return jsonify({"error": "Forbidden"}), 403
    m_data = request.json
    rev_id = str(m_data.get("review_id"))
    action = m_data.get("action") # 'delete' or 'dismiss'
    
    reviews = data("reviews")
    if action == "delete":
        reviews = [r for r in reviews if str(r.get("review_id")) != rev_id]
    elif action == "dismiss":
        for r in reviews:
            if str(r.get("review_id")) == rev_id:
                r["is_flagged"] = "0"
                break
    elif action == "flag":
        for r in reviews:
            if str(r.get("review_id")) == rev_id:
                r["is_flagged"] = "1"
                break
    save_csv("reviews", reviews)
    return jsonify({"success": True})

@app.route("/api/watchlist/add", methods=["POST"])
def api_watchlist_add():
    if not g.user: return jsonify({"error": "Unauthorized"}), 401
    w_data = request.json
    list_name = w_data.get("list_name", "Personal Watchlist")
    film_id = w_data.get("film_id")
    uid = str(g.user["user_id"])
    
    watchlists = data("watchlists")
    user_list = next((w for w in watchlists if str(w.get("user_id")) == uid and w.get("list_name") == list_name), None)
    
    if not user_list:
        new_lid = str(max([int(w.get("list_id", 0)) for w in watchlists] + [0]) + 1)
        user_list = {
            "list_id": new_lid, "user_id": uid, "list_name": list_name,
            "is_public": "0", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        watchlists.append(user_list)
        save_csv("watchlists", watchlists)
        
    items = data("watchlist_items")
    # Check if already added
    if not any(str(i.get("list_id")) == str(user_list["list_id"]) and str(i.get("film_id")) == str(film_id) for i in items):
        items.append({
            "list_id": user_list["list_id"],
            "film_id": film_id,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_csv("watchlist_items", items)
        
    return jsonify({"success": True})

@app.route("/api/watchlist/remove", methods=["POST"])
def api_watchlist_remove():
    if not g.user: return jsonify({"error": "Unauthorized"}), 401
    w_data = request.json
    list_id = str(w_data.get("list_id"))
    film_id = str(w_data.get("film_id"))
    
    items = data("watchlist_items")
    items = [i for i in items if not (str(i.get("list_id")) == list_id and str(i.get("film_id")) == film_id)]
    save_csv("watchlist_items", items)
    return jsonify({"success": True})

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  🎬  CineTrace is running!")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)