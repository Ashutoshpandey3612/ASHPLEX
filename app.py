# ================================
# 🔥 ASHPLEX ADVANCED FEATURES
# Like + Share + Premium + Ads + Splash Screen
# ================================

from flask import Flask, render_template_string, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "ashplex_secret"


# =========================================
# DATABASE
# =========================================

conn = sqlite3.connect("ashplex.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    premium TEXT DEFAULT 'FREE'
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS liked_songs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_phone TEXT,
    song_name TEXT
)
""")

conn.commit()


# =========================================
# SPLASH SCREEN
# =========================================

SPLASH_HTML = """

<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX</title>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>

body{
    margin:0;
    background:black;
    color:white;
    font-family:Arial;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
    overflow:hidden;
}

.container{
    text-align:center;
}

.logo{
    font-size:70px;
    margin-bottom:20px;
}

h1{
    font-size:50px;
    margin:0;
}

p{
    color:#aaa;
    margin-top:10px;
}

.btn{
    margin-top:30px;
    padding:14px 30px;
    border:none;
    border-radius:30px;
    background:#ff0033;
    color:white;
    font-size:18px;
    cursor:pointer;
}

</style>
</head>

<body>

<div class="container">

<div class="logo">🎧</div>

<h1>ASHPLEX</h1>

<p>Your Mood. Your Music. Your World.</p>

<button class="btn"
onclick="window.location='/login'">
Continue
</button>

</div>

</body>
</html>

"""


# =========================================
# LOGIN PAGE
# =========================================

LOGIN_HTML = """

<!DOCTYPE html>
<html>
<head>

<title>Login</title>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>

body{
    margin:0;
    background:black;
    color:white;
    font-family:Arial;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}

.box{
    width:350px;
    background:#111;
    padding:30px;
    border-radius:20px;
}

input{
    width:100%;
    padding:14px;
    margin-top:15px;
    border:none;
    border-radius:12px;
    background:#222;
    color:white;
}

button{
    width:100%;
    padding:14px;
    margin-top:20px;
    border:none;
    border-radius:30px;
    background:#ff0033;
    color:white;
    font-size:18px;
}

</style>
</head>

<body>

<div class="box">

<h1>📱 Login with Phone</h1>

<form method="POST">

<input type="text"
name="phone"
placeholder="Enter Phone Number">

<button type="submit">
Login
</button>

</form>

</div>

</body>
</html>

"""


# =========================================
# HOME PAGE
# =========================================

HOME_HTML = """

<!DOCTYPE html>
<html>
<head>

<title>ASHPLEX</title>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>

body{
    margin:0;
    background:black;
    color:white;
    font-family:Arial;
}

.header{
    padding:20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.banner{
    margin:20px;
    padding:20px;
    border-radius:20px;
    background:#111;
}

.song{
    margin:20px;
    padding:15px;
    border-radius:20px;
    background:#111;
}

.actions{
    margin-top:15px;
}

.btn{
    padding:10px 16px;
    border:none;
    border-radius:30px;
    margin-right:10px;
    cursor:pointer;
}

.like{
    background:#ff0033;
    color:white;
}

.share{
    background:#333;
    color:white;
}

.premium{
    background:gold;
    color:black;
}

.ad{
    margin:20px;
    padding:20px;
    border-radius:20px;
    background:#222;
    text-align:center;
    color:#aaa;
}

</style>

<script>

function shareSong(song){

    if(navigator.share){

        navigator.share({
            title:song,
            text:"Listen on ASHPLEX",
            url:window.location.href
        })

    }else{

        alert("Sharing not supported")

    }
}

</script>

</head>

<body>

<div class="header">

<h1>🎧 ASHPLEX</h1>

<div>

<span>
👑 {{premium}}
</span>

</div>

</div>


<div class="banner">

<h2>Your Mood. Your Music. Your World.</h2>

<p>
Created by Ashutosh Pandey
</p>

</div>


{% if premium == 'FREE' %}

<div class="ad">

📢 Advertisement Banner

</div>

{% endif %}


<div class="song">

<h2>❤️ Pehla Nasha</h2>

<p>Udit Narayan</p>

<div class="actions">

<button class="btn like">
❤️ Like
</button>

<button class="btn share"
onclick="shareSong('Pehla Nasha')">
📤 Share
</button>

<button class="btn premium">
👑 Premium
</button>

</div>

</div>


<div class="song">

<h2>🎵 Tujhe Dekha To</h2>

<p>Kumar Sanu</p>

<div class="actions">

<button class="btn like">
❤️ Like
</button>

<button class="btn share"
onclick="shareSong('Tujhe Dekha To')">
📤 Share
</button>

<button class="btn premium">
👑 Premium
</button>

</div>

</div>

</body>
</html>

"""


# =========================================
# ROUTES
# =========================================

@app.route("/")
def splash():
    return render_template_string(SPLASH_HTML)


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        phone = request.form["phone"]

        cur.execute(
            "INSERT INTO users(phone) VALUES(?)",
            (phone,)
        )

        conn.commit()

        session["phone"] = phone

        return redirect("/home")

    return render_template_string(LOGIN_HTML)


@app.route("/home")
def home():

    if "phone" not in session:
        return redirect("/login")

    phone = session["phone"]

    cur.execute(
        "SELECT premium FROM users WHERE phone=?",
        (phone,)
    )

    data = cur.fetchone()

    premium = "FREE"

    if data:
        premium = data[0]

    return render_template_string(
        HOME_HTML,
        premium=premium
    )


# =========================================
# RUN
# =========================================

if __name__ == "__main__":
    app.run(debug=True)
