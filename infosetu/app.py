import os, re, secrets, sqlite3, functools
from datetime import datetime, timedelta
from flask import Flask, g, send_from_directory, render_template, request, redirect, url_for, session, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
from i18n import T, LANGS, STATUSES, DEPTS
import search
from analyzer import analyze

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "infosetu.db")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")
UPLOAD_DIR = os.path.join(BASE, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
MAGIC = {"pdf": b"%PDF", "png": b"\x89PNG", "jpg": b"\xff\xd8", "jpeg": b"\xff\xd8"}
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT,
  role TEXT DEFAULT 'user', lang TEXT DEFAULT 'en', created_at TEXT);
CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY, slug TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY, ref TEXT UNIQUE, user_id INTEGER, dept_id INTEGER,
  category TEXT, description TEXT, lang TEXT, status TEXT DEFAULT 'submitted', remarks TEXT DEFAULT '',
  created_at TEXT, updated_at TEXT, full_name TEXT, email TEXT, doc_file TEXT, doc_name TEXT, quality INTEGER);
CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, request_id INTEGER, status TEXT, remark TEXT, at TEXT);
CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY, user_id INTEGER, ref TEXT, status TEXT,
  is_read INTEGER DEFAULT 0, at TEXT);
"""
JOIN = ("SELECT r.*, d.slug, u.username FROM requests r JOIN departments d ON d.id=r.dept_id "
        "JOIN users u ON u.id=r.user_id")


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def _close(_):
    d = g.pop("db", None)
    if d:
        d.close()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def tr(k):
    return T[k].get(session.get("lang", "en")) or T[k]["en"]


def me():
    if "u" not in g:
        uid = session.get("uid")
        g.u = db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone() if uid else None
    return g.u


def login_required(f):
    @functools.wraps(f)
    def w(*a, **k):
        if not me():
            return redirect(url_for("login"))
        return f(*a, **k)
    return w


def admin_required(f):
    @functools.wraps(f)
    def w(*a, **k):
        if not me():
            return redirect(url_for("login"))
        if me()["role"] != "admin":
            abort(403)
        return f(*a, **k)
    return w


@app.before_request
def _csrf():
    session.setdefault("_t", secrets.token_hex(16))
    if request.method == "POST" and request.form.get("_t") != session["_t"]:
        abort(400)


@app.context_processor
def _ctx():
    lang = session.get("lang", "en")
    return dict(
        t=tr, lang=lang, LANGS=LANGS, STATUSES=STATUSES, me=me(), tok=session["_t"],
        status_label=lambda s: STATUSES[s][lang],
        dept_label=lambda s: DEPTS[s][lang],
        depts=lambda: db().execute("SELECT * FROM departments").fetchall(),
    )


# ---------- helpers ----------
def reindex(rid):
    r = db().execute(JOIN + " WHERE r.id=?", (rid,)).fetchone()
    search.index({"id": r["id"], "ref": r["ref"], "user_id": r["user_id"], "username": r["username"], "full_name": r["full_name"], "email": r["email"],
                  "category": r["category"], "description": r["description"], "status": r["status"],
                  "dept": " ".join(DEPTS[r["slug"]].values())})


def stats(uid=None):
    w, p = (" WHERE user_id=?", [uid]) if uid else ("", [])
    c = {r["status"]: r["c"] for r in db().execute(
        "SELECT status, COUNT(*) c FROM requests" + w + " GROUP BY status", p)}
    return dict(total=sum(c.values()), in_progress=c.get("in_progress", 0), resolved=c.get("resolved", 0),
                pending=sum(c.get(k, 0) for k in ("submitted", "received", "assigned")))


def query_requests(uid=None):
    q = request.args.get("q", "").strip()
    st = request.args.get("status", "")
    dp = request.args.get("dept", "")
    sql, p = JOIN + " WHERE 1=1", []
    if uid:  # ownership is ALWAYS enforced in SQL, even when Elasticsearch is used
        sql += " AND r.user_id=?"; p.append(uid)
    if st in STATUSES:
        sql += " AND r.status=?"; p.append(st)
    if dp.isdigit():
        sql += " AND r.dept_id=?"; p.append(int(dp))
    if q:
        ids = search.search(q, uid)
        if ids is None:
            sql += (" AND (r.ref LIKE ? OR r.category LIKE ? OR r.description LIKE ? OR u.username LIKE ? "
                    "OR r.full_name LIKE ? OR r.email LIKE ?)")
            p += [f"%{q}%"] * 6
        elif not ids:
            return [], q, st, dp
        else:
            sql += " AND r.id IN (%s)" % ",".join("?" * len(ids)); p += ids
    return db().execute(sql + " ORDER BY r.id DESC", p).fetchall(), q, st, dp


def get_req(ref, uid=None):
    sql, p = JOIN + " WHERE r.ref=?", [ref]
    if uid:
        sql += " AND r.user_id=?"; p.append(uid)
    r = db().execute(sql, p).fetchone()
    if not r:
        abort(404)
    h = db().execute("SELECT * FROM history WHERE request_id=? ORDER BY id", (r["id"],)).fetchall()
    return r, h


# ---------- auth ----------
@app.route("/")
def index():
    u = me()
    if not u:
        return redirect(url_for("login"))
    return redirect(url_for("admin" if u["role"] == "admin" else "dashboard"))


@app.route("/lang/<code>")
def set_lang(code):
    if code in dict(LANGS):
        session["lang"] = code
        if me():
            db().execute("UPDATE users SET lang=? WHERE id=?", (code, me()["id"]))
            db().commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = db().execute("SELECT * FROM users WHERE username=?", (request.form["username"].strip(),)).fetchone()
        if u and check_password_hash(u["password_hash"], request.form["password"]):
            session["uid"], session["lang"] = u["id"], u["lang"]
            return redirect(url_for("index"))
        flash(tr("err_login"))
    return render_template("auth.html", mode="login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        un, pw = request.form["username"].strip(), request.form["password"]
        err = None
        if not re.fullmatch(r"[A-Za-z0-9_.]{3,30}", un) or db().execute(
                "SELECT 1 FROM users WHERE username=?", (un,)).fetchone():
            err = "err_exists"
        elif pw != request.form.get("confirm"):
            err = "err_match"
        elif len(pw) < 6:
            err = "err_short"
        if err:
            flash(tr(err))
        else:
            db().execute("INSERT INTO users(username,password_hash,lang,created_at) VALUES(?,?,?,?)",
                         (un, generate_password_hash(pw), session.get("lang", "en"), now()))
            db().commit()
            return redirect(url_for("login"))
    return render_template("auth.html", mode="signup")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- user side (every query is limited to the logged-in user) ----------
@app.route("/dashboard")
@login_required
def dashboard():
    u = me()
    if u["role"] == "admin":
        return redirect(url_for("admin"))
    recent = db().execute(JOIN + " WHERE r.user_id=? ORDER BY r.id DESC LIMIT 5", (u["id"],)).fetchall()
    notes = db().execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 8", (u["id"],)).fetchall()
    return render_template("dashboard.html", s=stats(u["id"]), recent=recent, notes=notes)


@app.route("/notifications/read", methods=["POST"])
@login_required
def read_notes():
    db().execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (me()["id"],))
    db().commit()
    return redirect(url_for("dashboard"))


def read_form():
    f = request.form
    d = dict(full_name=f.get("full_name", "").strip(), email=f.get("email", "").strip(),
             dept=f.get("dept", ""), category=f.get("category", "").strip(),
             description=f.get("description", "").strip())
    ok = d["full_name"] and d["category"] and d["description"] and EMAIL.match(d["email"]) and d["dept"].isdigit()
    return d, (None if ok else "err_fields")


def validate(v, rate=True, exclude_id=None):
    """Run the analyzer plus anti-spam checks. Returns (messages, quality_score)."""
    lang = session.get("lang", "en")
    row = db().execute("SELECT slug FROM departments WHERE id=?", (int(v["dept"]),)).fetchone()
    if not row:
        return [tr("err_fields")], 0
    errs, score = analyze(v, lang, row["slug"], tr, dict(LANGS)[lang], lambda s: DEPTS[s][lang])
    if not errs:
        uid = me()["id"]
        q, p = "SELECT 1 FROM requests WHERE user_id=? AND lower(description)=lower(?)", [uid, v["description"]]
        if exclude_id:
            q += " AND id<>?"; p.append(exclude_id)
        if db().execute(q, p).fetchone():
            errs.append(tr("err_dup"))
        if rate:
            since = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
            if db().execute("SELECT COUNT(*) FROM requests WHERE user_id=? AND created_at>=?", (uid, since)).fetchone()[0] >= 5:
                errs.append(tr("err_rate"))
    return errs, score


def save_doc(f):
    """Validate (extension + file signature) and store an upload. Returns (stored, original) or None."""
    if not f or not f.filename or "." not in f.filename:
        return None
    ext = f.filename.rsplit(".", 1)[-1].lower()
    if ext not in MAGIC:
        return None
    head = f.read(8); f.seek(0)
    if not head.startswith(MAGIC[ext]):
        return None
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    stored = secrets.token_hex(16) + "." + ext
    f.save(os.path.join(UPLOAD_DIR, stored))
    return stored, os.path.basename(f.filename)[:120]


def send_doc(r):
    if not r["doc_file"]:
        abort(404)
    return send_from_directory(UPLOAD_DIR, r["doc_file"], as_attachment=True,
                               download_name=r["doc_name"] or r["doc_file"])


@app.errorhandler(413)
def _too_big(_):
    flash(tr("err_doc"))
    return redirect(request.referrer or url_for("index"))


@app.route("/new", methods=["GET", "POST"])
@login_required
def new_request():
    v = {}
    if request.method == "POST":
        v, err = read_form()
        msgs, score, doc = ([tr(err)] if err else []), 0, None
        if not msgs:
            msgs, score = validate(v)
        if not msgs:  # save the file only after every text check has passed
            doc = save_doc(request.files.get("document"))
            if not doc:
                msgs = [tr("err_doc")]
        if not msgs:
            cur = db().execute(
                "INSERT INTO requests(user_id,dept_id,category,description,lang,created_at,updated_at,"
                "full_name,email,doc_file,doc_name,quality) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (me()["id"], int(v["dept"]), v["category"], v["description"], session.get("lang", "en"),
                 now(), now(), v["full_name"], v["email"], doc[0], doc[1], score))
            rid = cur.lastrowid
            ref = f"PIR-{10000 + rid}"
            db().execute("UPDATE requests SET ref=? WHERE id=?", (ref, rid))
            db().execute("INSERT INTO history(request_id,status,remark,at) VALUES(?,?,?,?)", (rid, "submitted", "", now()))
            db().commit()
            reindex(rid)
            flash(tr("submitted_msg"))
            return redirect(url_for("detail", ref=ref))
        for m in msgs[:4]:
            flash(m)
    return render_template("new.html", v=v, editing=False, has_doc=False)


@app.route("/requests")
@login_required
def my_requests():
    rows, q, st, dp = query_requests(me()["id"])
    return render_template("requests.html", rows=rows, q=q, status=st, dept=dp, admin=False)


@app.route("/request/<ref>")
@login_required
def detail(ref):
    r, h = get_req(ref, me()["id"])
    return render_template("detail.html", r=r, hist=h, admin=False)


@app.route("/request/<ref>/doc")
@login_required
def my_doc(ref):
    r, _ = get_req(ref, me()["id"])
    return send_doc(r)


@app.route("/request/<ref>/edit", methods=["GET", "POST"])
@login_required
def edit(ref):
    r, _ = get_req(ref, me()["id"])
    if r["status"] != "submitted":  # lock once an admin starts processing
        flash(tr("locked"))
        return redirect(url_for("detail", ref=ref))
    v = dict(full_name=r["full_name"], email=r["email"], dept=r["dept_id"],
             category=r["category"], description=r["description"])
    if request.method == "POST":
        v, err = read_form()
        msgs, score, doc = ([tr(err)] if err else []), 0, None
        if not msgs:
            msgs, score = validate(v, rate=False, exclude_id=r["id"])
        file = request.files.get("document")
        if not msgs:
            if file and file.filename:
                doc = save_doc(file)
                if not doc:
                    msgs = [tr("err_doc")]
            elif not r["doc_file"]:
                msgs = [tr("err_doc")]
        if not msgs:
            db().execute("UPDATE requests SET dept_id=?,category=?,description=?,full_name=?,email=?,lang=?,quality=?,"
                         "updated_at=? WHERE id=? AND user_id=?",
                         (int(v["dept"]), v["category"], v["description"], v["full_name"], v["email"],
                          session.get("lang", "en"), score, now(), r["id"], me()["id"]))
            if doc:
                db().execute("UPDATE requests SET doc_file=?, doc_name=? WHERE id=? AND user_id=?",
                             (doc[0], doc[1], r["id"], me()["id"]))
                if r["doc_file"]:
                    try:
                        os.remove(os.path.join(UPLOAD_DIR, r["doc_file"]))
                    except OSError:
                        pass
            db().commit()
            reindex(r["id"])
            flash(tr("saved"))
            return redirect(url_for("detail", ref=ref))
        for m in msgs[:4]:
            flash(m)
    return render_template("new.html", v=v, editing=True, has_doc=bool(r["doc_file"]))


# ---------- admin side ----------
@app.route("/admin")
@admin_required
def admin():
    rows, q, st, dp = query_requests()
    by_dept = db().execute("SELECT d.slug, COUNT(r.id) c FROM departments d LEFT JOIN requests r "
                           "ON r.dept_id=d.id GROUP BY d.id ORDER BY c DESC").fetchall()
    return render_template("admin.html", s=stats(), by_dept=by_dept, rows=rows, q=q, status=st, dept=dp, admin=True)


@app.route("/admin/request/<ref>", methods=["GET", "POST"])
@admin_required
def admin_detail(ref):
    r, h = get_req(ref)
    if request.method == "POST":
        st, dp, rm = request.form["status"], int(request.form["dept"]), request.form.get("remark", "").strip()
        if st not in STATUSES:
            abort(400)
        db().execute("UPDATE requests SET status=?, dept_id=?, remarks=CASE WHEN ?<>'' THEN ? ELSE remarks END, "
                     "updated_at=? WHERE id=?", (st, dp, rm, rm, now(), r["id"]))
        db().execute("INSERT INTO history(request_id,status,remark,at) VALUES(?,?,?,?)", (r["id"], st, rm, now()))
        if st != r["status"]:
            db().execute("INSERT INTO notifications(user_id,ref,status,at) VALUES(?,?,?,?)",
                         (r["user_id"], r["ref"], st, now()))
        db().commit()
        reindex(r["id"])
        flash(tr("saved"))
        return redirect(url_for("admin_detail", ref=ref))
    return render_template("detail.html", r=r, hist=h, admin=True)


@app.route("/admin/request/<ref>/doc")
@admin_required
def admin_doc(ref):
    r, _ = get_req(ref)
    return send_doc(r)


@app.route("/admin/users")
@admin_required
def admin_users():
    rows = db().execute("SELECT u.*, (SELECT COUNT(*) FROM requests WHERE user_id=u.id) c FROM users u "
                        "ORDER BY u.id").fetchall()
    return render_template("users.html", rows=rows)


# ---------- startup ----------
def boot():
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    have = {row[1] for row in c.execute("PRAGMA table_info(requests)")}
    for col in ("full_name", "email", "doc_file", "doc_name", "quality"):
        if col not in have:
            c.execute(f"ALTER TABLE requests ADD COLUMN {col} TEXT")
    for s in DEPTS:
        c.execute("INSERT OR IGNORE INTO departments(slug) VALUES(?)", (s,))
    if not c.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():
        c.execute("INSERT INTO users(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                  ("admin", generate_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123")), "admin", now()))
    c.commit()
    ids = [r[0] for r in c.execute("SELECT id FROM requests")]
    c.close()
    search.init()
    with app.app_context():
        for i in ids:
            reindex(i)


boot()

if __name__ == "__main__":
    app.run(debug=True)
