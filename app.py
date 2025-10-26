from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3, os, uuid, datetime

app = Flask(__name__)
app.secret_key = "Passwort"

def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS consents (id TEXT PRIMARY KEY, timestamp TEXT, ip TEXT, ua TEXT, version TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, message TEXT, consent_id TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit(); conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/consent", methods=["POST"])
def consent():
    cid = str(uuid.uuid4())
    ts = datetime.datetime.utcnow().isoformat()+"Z"
    ip = request.remote_addr
    ua = request.headers.get("User-Agent","")
    ver = "v1"
    conn = sqlite3.connect("data.db"); c = conn.cursor()
    c.execute("INSERT INTO consents (id,timestamp,ip,ua,version) VALUES (?,?,?,?,?)",(cid,ts,ip,ua,ver))
    conn.commit(); conn.close()
    return {"token": cid}, 201

@app.route("/submit", methods=["POST"])
def submit():
    token = request.form.get("consent_token")
    if not token:
        return "Bitte zuerst zustimmen.", 400
    conn = sqlite3.connect("data.db"); c = conn.cursor()
    c.execute("SELECT id FROM consents WHERE id = ?", (token,))
    if not c.fetchone():
        conn.close(); return "Ungültige Einwilligung.", 400
    name = request.form.get("name","")
    msg = request.form.get("message","")
    c.execute("INSERT INTO submissions (name,message,consent_id) VALUES (?,?,?)",(name,msg,token))
    conn.commit(); conn.close()
    return "Danke, Nachricht gespeichert."

@app.route("/get_messages")
def get_messages():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT name, message FROM submissions ORDER BY created_at DESC")
    messages = [{"name": row[0], "message": row[1]} for row in c.fetchall()]
    conn.close()
    return messages

if __name__=="__main__":
    init_db()
    app.run(debug=True)