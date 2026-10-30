"""
PHOTOGRAPHY FINDER SYSTEM  -  Python (Tkinter) + MySQL (XAMPP)

SETUP
1. Open XAMPP Control Panel and START "MySQL" (Apache is not needed).
2. pip install mysql-connector-python
3. python photography_finder.py
The program creates the database, tables and sample packages by itself.
"""
import hashlib, math, os, random, re, smtplib, time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from email.message import EmailMessage
import mysql.connector

# ------------------------- CONFIG -------------------------
DB_CFG = dict(host="localhost", port=3306, user="root", password="")  # XAMPP default
DB_NAME = "photography_finder"
SMTP_EMAIL = ""          # Gmail used to send OTP codes (optional)
SMTP_APP_PASSWORD = ""   # Gmail "App Password" (optional)
# If the two above are empty, the OTP is shown in a pop-up (demo mode).

# ------------------------- THEME --------------------------
BG, CARD, TEXT, MUTED = "#121012", "#0b0a0b", "#efe6dd", "#a89c98"
RED, RED_H, ACC, LINE = "#7d1526", "#9a1c32", "#c2415c", "#3a3436"
SERIF, SANS = "Georgia", "Segoe UI"


# ------------------------- DATABASE -----------------------
SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS packages (
        code VARCHAR(20) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        inclusions TEXT NOT NULL,
        price DECIMAL(10,2) NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS records (
        id INT AUTO_INCREMENT PRIMARY KEY,
        client_name VARCHAR(100) NOT NULL,
        contact VARCHAR(100) NOT NULL,
        session_date DATE NOT NULL,
        session_type VARCHAR(100) NOT NULL,
        package_code VARCHAR(20) NOT NULL,
        FOREIGN KEY (package_code) REFERENCES packages(code)
            ON UPDATE CASCADE ON DELETE RESTRICT)""",
]
SEED = [
    ("BASIC", "Basic Session", "1 hour shoot, 20 edited photos, online gallery", 2500),
    ("STANDARD", "Standard Session", "2 hour shoot, 40 edited photos, 1 outfit change", 4500),
    ("PREMIUM", "Premium Session", "4 hour shoot, 80 edited photos, prints, photo book", 8500),
    ("WEDDING", "Wedding Package", "Full day coverage, 2 photographers, album, video teaser", 25000),
]


class Database:
    def __init__(self):
        c = mysql.connector.connect(**DB_CFG)
        c.cursor().execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        c.close()
        self.con = mysql.connector.connect(database=DB_NAME, **DB_CFG)
        for sql in SCHEMA:
            self.q(sql, commit=True)
        if not self.q("SELECT code FROM packages LIMIT 1"):
            cur = self.con.cursor()
            cur.executemany("INSERT INTO packages VALUES (%s,%s,%s,%s)", SEED)
            self.con.commit()
            cur.close()

    def q(self, sql, args=(), one=False, commit=False):
        self.con.ping(reconnect=True)
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, args)
        if commit:
            self.con.commit()
            res = cur.lastrowid
        else:
            res = cur.fetchone() if one else cur.fetchall()
        cur.close()
        return res


def hash_pw(pw, salt=None):
    salt = salt or os.urandom(8).hex()
    return salt + "$" + hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 50000).hex()


def check_pw(pw, stored):
    return hash_pw(pw, stored.split("$")[0]) == stored


def send_mail(to, code):
    if not SMTP_EMAIL:
        raise RuntimeError("SMTP not configured")
    m = EmailMessage()
    m["Subject"], m["From"], m["To"] = "Photography Finder - password reset code", SMTP_EMAIL, to
    m.set_content(f"Your OTP code is {code}. It expires in 5 minutes.")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as s:
        s.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        s.send_message(m)


# ------------------------- ART (drawn shapes) -------------------
def mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(A, B))


def grad(c, w, h, a, b):
    for y in range(0, int(h) + 4, 4):
        c.create_rectangle(0, y, w, y + 4, fill=mix(a, b, y / max(h, 1)), outline="")


def circ(c, x, y, r, fill, o="", wd=0):
    c.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=o, width=wd)


def rrect(c, x1, y1, x2, y2, r, **k):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2,
           x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **k)


def tilt(c, cx, cy, w, h, deg, **k):
    a, pts = math.radians(deg), []
    for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts += [cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)]
    c.create_polygon(pts, outline="", **k)


def art_camera(c, w, h):
    grad(c, w, h, "#a64258", "#5c2030")
    cx, cy, u = w / 2, h / 2, min(w, h * 1.5)
    c.create_rectangle(cx - .42 * u, cy - .3 * u, cx + .42 * u, cy + .3 * u, fill="#2b2a2e", outline="")
    c.create_rectangle(cx - .42 * u, cy - .3 * u, cx + .42 * u, cy - .15 * u, fill="#d2cfc8", outline="")
    circ(c, cx + .3 * u, cy - .22 * u, .035 * u, "#d12b42")
    for r, col in ((.2, "#a8a59d"), (.17, "#1b1b1e"), (.1, "#26252b"), (.05, "#4a5a8f")):
        circ(c, cx, cy + .03 * u, r * u, col)


def art_lens(c, w, h):
    grad(c, w, h, "#b0465c", "#5a2030")
    cx, cy, R = w / 2, h / 2, min(w * .8, h * .85)
    for k, col in ((1, "#d12b42"), (.94, "#1b1b1e"), (.78, "#a09d95"), (.74, "#2b2a2e"),
                   (.52, "#131216"), (.33, "#46528c")):
        circ(c, cx, cy, R * k, col)
    circ(c, cx - .14 * R, cy - .14 * R, .07 * R, "#c4c6dc")
    circ(c, cx + .14 * R, cy + .14 * R, .035 * R, "#9fa4cc")


def art_polaroid(c, w, h):
    grad(c, w, h, "#e0b8ac", "#bd7a7c")
    u = min(w, h * 1.4)
    for dx, deg, col, dot in ((-.2, -8, "#8b1f33", 0), (.2, 6, "#dc8a60", 1)):
        cx, cy = w / 2 + dx * u, h / 2
        tilt(c, cx, cy, .5 * u, .6 * u, deg, fill="#f6f1ea")
        tilt(c, cx, cy - .04 * u, .42 * u, .42 * u, deg, fill=col)
        if dot:
            circ(c, cx, cy - .04 * u, .08 * u, "#f3d3b0")


def art_film(c, w, h):
    c.create_rectangle(0, 0, w, h, fill="#190a0c", outline="")
    sw = min(h * .62, w * .26)
    gap = (w - 3 * sw) / 4
    for i, col in enumerate(("#e5906a", "#c4566b", "#f0c08a")):
        x = gap + i * (sw + gap)
        c.create_rectangle(x, h * .2, x + sw, h * .82, fill=col, outline="")
    for x in range(8, int(w), 30):
        c.create_rectangle(x, 5, x + 12, 10, fill="#f3e9e2", outline="")


def art_bokeh(c, w, h):
    grad(c, w, h, "#4a1a24", "#7a1f30")
    u = min(w, h * 1.4)
    for x, y, r, col in ((.5, .55, .3, "#d04f65"), (.02, .3, .15, "#e59c7c"), (.98, .25, .12, "#e8b78f"),
                         (.15, .92, .07, "#e08a68"), (.85, .85, .08, "#e8798d")):
        circ(c, w * x, h * y, r * u, col)


def art_tripod(c, w, h):
    grad(c, w, h, "#e38f58", "#9b4637")
    u, cx = min(w, h * 1.4), w / 2
    circ(c, w * .8, h * .4, .16 * u, "#ffd9a0")
    c.create_polygon(0, h * .75, w * .28, h * .55, w * .5, h * .72, w * .8, h * .5, w, h * .62,
                     w, h, 0, h, fill="#3a1018", outline="")
    ty, lw = h * .6, max(2, .02 * u)
    for x in (cx - .26 * u, cx, cx + .26 * u):
        c.create_line(cx, ty, x, h * .97, width=lw, fill="#1a080b")
    rrect(c, cx - .12 * u, ty - .2 * u, cx + .12 * u, ty, 6, fill="#1a080b")


# ------------------------- WIDGET HELPERS ------------------------
class Btn(tk.Canvas):
    def __init__(s, p, text, cmd, fill=True, w=160, h=46):
        super().__init__(p, width=w, height=h, bg=p["bg"], highlightthickness=0, cursor="hand2")
        s.bw, s.bh, s.txt, s.cmd, s.filled = w, h, text, cmd, fill
        s.draw(False)
        s.bind("<Enter>", lambda e: s.draw(True))
        s.bind("<Leave>", lambda e: s.draw(False))
        s.bind("<Button-1>", lambda e: s.cmd())

    def draw(s, hov):
        s.delete("all")
        col = (RED_H if hov else RED) if s.filled else (RED if hov else BG)
        rrect(s, 2, 2, s.bw - 2, s.bh - 2, s.bh // 2, fill=col, outline=RED if s.filled else ACC, width=1.5)
        s.create_text(s.bw / 2, s.bh / 2, text=s.txt.upper(), fill=TEXT, font=(SANS, 10, "bold"))


def link(p, text, cmd):
    l = tk.Label(p, text=text, font=(SANS, 10, "underline"), fg=TEXT, bg=p["bg"], cursor="hand2")
    l.bind("<Button-1>", lambda e: cmd())
    return l


def field(p, label, show="", **grid):
    """Underlined input like the design. Returns the Entry."""
    fr = tk.Frame(p, bg=BG)
    tk.Label(fr, text=label.upper(), font=(SANS, 9), fg=MUTED, bg=BG).pack(anchor="w")
    e = tk.Entry(fr, bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0, show=show,
                 font=(SANS, 12), highlightthickness=0, width=34)
    e.pack(fill="x", pady=(6, 3), ipady=3)
    tk.Frame(fr, bg=LINE, height=1).pack(fill="x")
    if grid:
        fr.grid(**grid)
    else:
        fr.pack(fill="x", pady=(14, 0))
    return e


def logo(p):
    c = tk.Canvas(p, width=34, height=26, bg=BG, highlightthickness=0)
    rrect(c, 2, 6, 32, 24, 4, fill=BG, outline=ACC, width=1.5)
    c.create_rectangle(12, 2, 22, 6, outline=ACC)
    circ(c, 17, 15, 5, BG, ACC, 1.5)
    return c


def heading(p, tag, title, sub):
    logo(p).pack(anchor="w")
    tk.Label(p, text=tag, font=(SANS, 9), fg=MUTED, bg=BG).pack(anchor="w", pady=(8, 0))
    tk.Label(p, text=title, font=(SERIF, 30), fg=TEXT, bg=BG).pack(anchor="w", pady=(8, 0))
    tk.Frame(p, bg=RED, width=56, height=2).pack(anchor="w", pady=(8, 8))
    tk.Label(p, text=sub, font=(SANS, 11), fg=MUTED, bg=BG).pack(anchor="w")


class Scroll(tk.Frame):
    def __init__(s, p):
        super().__init__(p, bg=BG)
        s.c = tk.Canvas(s, bg=BG, highlightthickness=0)
        s.c.pack(fill="both", expand=True)
        s.inner = tk.Frame(s.c, bg=BG)
        win = s.c.create_window(0, 0, window=s.inner, anchor="nw")
        s.inner.bind("<Configure>", lambda e: s.c.configure(scrollregion=s.c.bbox("all")))
        s.c.bind("<Configure>", lambda e: s.c.itemconfig(win, width=e.width))
        s.c.bind_all("<MouseWheel>", s.wheel)

    def wheel(s, e):
        try:
            s.c.yview_scroll(-1 if e.delta > 0 else 1, "units")
        except tk.TclError:
            pass


# ------------------------- HELPERS ---------------------------
def fmt(d):
    return d.strftime("%m/%d/%Y") if hasattr(d, "strftime") else str(d)


def get(e):
    v = e.get().strip()
    return "" if v == "mm/dd/yyyy" else v


def validate(db, name, contact, date, stype, code):
    """Returns (error_message, date_object)."""
    if not all([name, contact, date, stype, code]):
        return "Please fill the required blanks.", None
    try:
        d = datetime.strptime(date, "%m/%d/%Y").date()
    except ValueError:
        return "Session date must be in mm/dd/yyyy format.", None
    if not db.q("SELECT code FROM packages WHERE code=%s", (code,), True):
        codes = ", ".join(p["code"] for p in db.q("SELECT code FROM packages"))
        return f"Package code not found.\nAvailable codes: {codes}", None
    return None, d


# ------------------------- APP --------------------------------
class App(tk.Tk):
    def __init__(s):
        super().__init__()
        s.title("Photography Finder")
        s.geometry("1100x720")
        s.minsize(1000, 700)
        s.configure(bg=BG)
        s.user, s.fails, s.page = None, 0, None
        try:
            s.db = Database()
        except mysql.connector.Error as e:
            messagebox.showerror("MySQL connection failed",
                                 f"Please START MySQL in the XAMPP Control Panel first.\n\n{e}")
            s.destroy()
            raise SystemExit
        s.show(LoginPage)

    def show(s, cls, *a):
        if s.page:
            s.page.destroy()
        s.page = cls(s, *a)


class Page(tk.Frame):
    def __init__(s, app):
        super().__init__(app, bg=BG)
        s.app, s.db = app, app.db
        s.pack(fill="both", expand=True)

    def go(s, cls, *a):
        s.app.show(cls, *a)

    def split(s, art, lw=490):
        c = tk.Canvas(s, width=lw, highlightthickness=0, bg=BG)
        c.pack(side="left", fill="y")
        c.bind("<Configure>", lambda e: (c.delete("all"), art(c, e.width, e.height)))
        r = tk.Frame(s, bg=BG)
        r.pack(side="left", fill="both", expand=True)
        return r

    def topbar(s, p, x=-40):
        f = tk.Frame(p, bg=BG)
        f.place(relx=1, x=x, y=28, anchor="ne")
        tk.Label(f, text=f"WELCOME, {(s.app.user or '').upper()}", font=(SANS, 9), fg=MUTED, bg=BG).pack(anchor="e")
        t = tk.Label(f, font=(SANS, 22), fg=TEXT, bg=BG)
        t.pack(anchor="e")
        d = tk.Label(f, font=(SANS, 10), fg=MUTED, bg=BG)
        d.pack(anchor="e")

        def tick():
            if not t.winfo_exists():
                return
            n = datetime.now()
            t.config(text=n.strftime("%I:%M:%S %p"))
            d.config(text=n.strftime("%A, %B %d, %Y"))
            t.after(1000, tick)
        tick()


# ------------------------- LOGIN / SIGN UP / RESET -------------
class LoginPage(Page):
    def __init__(s, app):
        super().__init__(app)
        r = s.split(art_lens)
        f = tk.Frame(r, bg=BG)
        f.place(relx=.5, rely=.5, anchor="center")
        heading(f, "PHOTOGRAPHY FINDER", "Welcome back", "Log in to your studio.")
        s.u = field(f, "Username")
        s.p = field(f, "Password", "*")
        row = tk.Frame(f, bg=BG)
        row.pack(anchor="w", pady=(26, 0))
        Btn(row, "Log in", s.login).pack(side="left")
        link(row, "Create account", lambda: s.go(SignupPage)).pack(side="left", padx=18)
        link(f, "Forgot password?", lambda: s.go(ForgotPage)).pack(anchor="w", pady=(16, 0))
        s.p.bind("<Return>", lambda e: s.login())
        s.u.focus_set()

    def login(s):
        u, p = s.u.get().strip(), s.p.get()
        if not u or not p:
            return messagebox.showwarning("Fill the blanks", "Please enter your username and password.")
        row = s.db.q("SELECT * FROM users WHERE username=%s", (u,), True)
        if row and check_pw(p, row["password_hash"]):
            s.app.user, s.app.fails = row["username"], 0
            return s.go(Dashboard)
        s.app.fails += 1
        messagebox.showerror("Invalid credentials", "Wrong username or password. Please try again.")
        if s.app.fails >= 5 and messagebox.askyesno("Too many attempts", "Forgot your password? Reset it now?"):
            s.go(ForgotPage)


class SignupPage(Page):
    def __init__(s, app):
        super().__init__(app)
        r = s.split(art_lens)
        f = tk.Frame(r, bg=BG)
        f.place(relx=.5, rely=.5, anchor="center")
        heading(f, "PHOTOGRAPHY FINDER", "Create account", "Set up your studio access.")
        s.u, s.e, s.p = field(f, "Username"), field(f, "Email"), field(f, "Password", "*")
        row = tk.Frame(f, bg=BG)
        row.pack(anchor="w", pady=(26, 0))
        Btn(row, "Sign up", s.signup).pack(side="left")
        link(row, "Back to login", lambda: s.go(LoginPage)).pack(side="left", padx=18)

    def signup(s):
        u, e, p = s.u.get().strip(), s.e.get().strip().lower(), s.p.get()
        if not u or not e or not p:
            return messagebox.showwarning("Fill the blanks", "Please fill in all fields.")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e):
            return messagebox.showwarning("Invalid email", "Please enter a valid email address.")
        if len(p) < 6:
            return messagebox.showwarning("Weak password", "Password must be at least 6 characters.")
        if s.db.q("SELECT id FROM users WHERE username=%s OR email=%s", (u, e), True):
            return messagebox.showerror("Already registered", "Username or email is already in use.")
        s.db.q("INSERT INTO users (username,email,password_hash) VALUES (%s,%s,%s)", (u, e, hash_pw(p)), commit=True)
        messagebox.showinfo("Success", "Sign in successful! You can now log in.")
        s.go(LoginPage)


class ForgotPage(Page):
    def __init__(s, app):
        super().__init__(app)
        r = s.split(art_bokeh)
        f = tk.Frame(r, bg=BG)
        f.place(relx=.5, rely=.5, anchor="center")
        heading(f, "PHOTOGRAPHY FINDER", "Reset password", "We will send a code to your registered email.")
        s.e, s.o = field(f, "Registered email"), field(f, "OTP code")
        s.n, s.c = field(f, "New password", "*"), field(f, "Confirm password", "*")
        row = tk.Frame(f, bg=BG)
        row.pack(anchor="w", pady=(24, 0))
        Btn(row, "Verify", s.verify, w=140).pack(side="left")
        s.rs = link(row, "Send code", s.send)
        s.rs.pack(side="left", padx=18)
        link(f, "Back to login", lambda: s.go(LoginPage)).pack(anchor="w", pady=(14, 0))
        s.otp, s.exp, s.to, s.cool = None, 0, None, 0

    def send(s):
        if s.cool > 0:
            return
        em = s.e.get().strip().lower()
        if not em:
            return messagebox.showwarning("Fill the blanks", "Enter your registered email.")
        if not s.db.q("SELECT id FROM users WHERE email=%s", (em,), True):
            return messagebox.showerror("Email not found", "That email is not registered.")
        s.otp, s.exp, s.to = f"{random.randint(0, 999999):06d}", time.time() + 300, em
        try:
            send_mail(em, s.otp)
            messagebox.showinfo("OTP sent", f"A code was sent to {em}.")
        except Exception:
            messagebox.showinfo("OTP (demo mode)", f"Email sending is not set up.\nYour code is: {s.otp}")
        s.cool = 60
        s.tick()

    def tick(s):
        if not s.rs.winfo_exists():
            return
        if s.cool > 0:
            s.rs.config(text=f"Resend code in {s.cool}s")
            s.cool -= 1
            s.after(1000, s.tick)
        else:
            s.rs.config(text="Resend code")

    def verify(s):
        em, o, n, c = s.e.get().strip().lower(), s.o.get().strip(), s.n.get(), s.c.get()
        if not (em and o and n and c):
            return messagebox.showwarning("Fill the blanks", "Please fill in all fields.")
        if not s.otp or em != s.to:
            return messagebox.showwarning("No code", "Please request a code first.")
        if time.time() > s.exp:
            return messagebox.showerror("Expired", "The code has expired. Request a new one.")
        if o != s.otp:
            return messagebox.showerror("Invalid code", "The code is incorrect.")
        if n != c:
            return messagebox.showerror("Mismatch", "Passwords do not match.")
        if len(n) < 6:
            return messagebox.showwarning("Weak password", "Password must be at least 6 characters.")
        s.db.q("UPDATE users SET password_hash=%s WHERE email=%s", (hash_pw(n), em), commit=True)
        messagebox.showinfo("Success", "Password reset successful. Redirecting you to login.")
        s.go(LoginPage)


# ------------------------- DASHBOARD ---------------------------
class Dashboard(Page):
    def __init__(s, app):
        super().__init__(app)
        s.topbar(s, -60)
        body = tk.Frame(s, bg=BG)
        body.pack(fill="both", expand=True, padx=60, pady=(24, 14))
        heading(body, "MAIN MENU", "Dashboard", "Everything for your sessions, in one place.")
        g = tk.Frame(body, bg=BG)
        g.pack(fill="both", expand=True, pady=(16, 0))
        g.columnconfigure((0, 1, 2), weight=1, uniform="a")
        items = [("01", "Add Record", art_camera, AddPage), ("02", "View Records", art_polaroid, RecordsPage),
                 ("03", "Search Record", art_lens, RecordsPage, True),
                 ("04", "Update Record", art_film, UpdatePage), ("05", "Delete Record", art_bokeh, DeletePage),
                 ("06", "Package Lookup", art_tripod, PackagePage)]
        s.acts = {}
        for i, (n, t, art, cls, *extra) in enumerate(items):
            fn = lambda cls=cls, extra=extra: s.go(cls, *extra)
            s.acts[n[-1]] = fn
            c = tk.Frame(g, bg=CARD, cursor="hand2")
            c.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
            cv = tk.Canvas(c, height=100, highlightthickness=0, bg=CARD)
            cv.pack(fill="x")
            cv.bind("<Configure>", lambda e, cv=cv, art=art: (cv.delete("all"), art(cv, e.width, e.height)))
            tk.Label(c, text=n, font=(SANS, 10), fg=MUTED, bg=CARD).pack(pady=(10, 0))
            tk.Label(c, text=t, font=(SERIF, 15), fg=TEXT, bg=CARD).pack()
            tk.Frame(c, bg=RED, width=40, height=2).pack(pady=(6, 12))
            for w in [c, cv] + c.winfo_children():
                w.bind("<Button-1>", lambda e, fn=fn: fn())
        bar = tk.Frame(body, bg=BG)
        bar.pack(fill="x", pady=(8, 0))
        link(bar, "07   EXIT", s.exit).pack(side="left")
        Btn(bar, "Log out", lambda: s.go(LogoutPage), fill=False, w=140).pack(side="right")
        s.acts["7"] = s.exit
        s.focus_set()
        s.bind("<Key>", lambda e: s.acts.get(e.char, lambda: None)())

    def exit(s):
        if messagebox.askyesno("Exit", "Do you want to close the application?"):
            messagebox.showinfo("Goodbye", "Thank you for using Photography Finder System.")
            s.app.destroy()


class LogoutPage(Page):
    def __init__(s, app):
        super().__init__(app)
        r = s.split(art_tripod)
        f = tk.Frame(r, bg=BG)
        f.place(relx=.5, rely=.5, anchor="center")
        tk.Label(f, text="Log out of your account?", font=(SERIF, 26), fg=TEXT, bg=BG).pack()
        tk.Frame(f, bg=RED, width=56, height=2).pack(pady=10)
        tk.Label(f, text="Thank you for using Photography Finder System.", font=(SANS, 11), fg=MUTED, bg=BG).pack()
        row = tk.Frame(f, bg=BG)
        row.pack(pady=22)
        Btn(row, "Yes, log out", s.out, w=170).pack(side="left", padx=8)
        Btn(row, "Stay", lambda: s.go(Dashboard), fill=False, w=120).pack(side="left", padx=8)

    def out(s):
        s.app.user = None
        s.go(LoginPage)


# ------------------------- ADD RECORD --------------------------
class AddPage(Page):
    def __init__(s, app):
        super().__init__(app)
        r = s.split(art_polaroid, 376)
        s.topbar(r)
        body = tk.Frame(r, bg=BG)
        body.pack(fill="both", expand=True, padx=50, pady=(26, 0))
        heading(body, "01", "Add record", "Enter the client and session details.")
        g = tk.Frame(body, bg=BG)
        g.pack(fill="x", pady=(10, 0))
        g.columnconfigure((0, 1), weight=1, uniform="c")
        L, R = dict(sticky="ew", padx=(0, 20), pady=(14, 0)), dict(sticky="ew", pady=(14, 0))
        s.name = field(g, "Client name", row=0, column=0, **L)
        s.contact = field(g, "Contact details", row=0, column=1, **R)
        s.date = field(g, "Session date", row=1, column=0, **L)
        s.stype = field(g, "Session type / location", row=1, column=1, **R)
        s.code = field(g, "Package code", row=2, column=0, **L)
        s.date.insert(0, "mm/dd/yyyy")
        s.date.config(fg=MUTED)
        s.date.bind("<FocusIn>", lambda e: (s.date.delete(0, "end"), s.date.config(fg=TEXT)) if s.date.get() == "mm/dd/yyyy" else None)
        row = tk.Frame(body, bg=BG)
        row.pack(anchor="w", pady=(28, 0))
        Btn(row, "Save record", s.save, w=170).pack(side="left")
        Btn(row, "Cancel", lambda: s.go(Dashboard), fill=False, w=130).pack(side="left", padx=14)

    def save(s):
        name, contact, date, stype, code = (get(s.name), get(s.contact), get(s.date), get(s.stype), get(s.code).upper())
        err, d = validate(s.db, name, contact, date, stype, code)
        if err:
            return messagebox.showwarning("Check your input", err)
        if s.db.q("SELECT id FROM records WHERE client_name=%s AND session_date=%s", (name, d), True):
            return messagebox.showerror("Already has a record", "This client already has a record on that date.")
        s.db.q("INSERT INTO records (client_name,contact,session_date,session_type,package_code) VALUES (%s,%s,%s,%s,%s)",
               (name, contact, d, stype, code), commit=True)
        if messagebox.askyesno("Record added", "Record successfully added.\nDo you want to add another?"):
            s.go(AddPage)
        else:
            s.go(Dashboard)


# ------------------------- VIEW / SEARCH -----------------------
class RecordsPage(Page):
    ARTS = [art_camera, art_polaroid, art_tripod, art_bokeh]

    def __init__(s, app, focus=False):
        super().__init__(app)
        s.topbar(s, -60)
        body = tk.Frame(s, bg=BG)
        body.pack(fill="both", expand=True, padx=60, pady=(24, 18))
        heading(body, "02 · 03", "Records", "Browse every session or search by client.")
        s.q = field(body, "Search keyword / client name")
        s.q.bind("<KeyRelease>", lambda e: s.load())
        s.sc = Scroll(body)
        s.sc.pack(fill="both", expand=True, pady=(14, 10))
        Btn(body, "Back", lambda: s.go(Dashboard), fill=False, w=120).pack(anchor="w")
        s.load()
        if focus:
            s.q.focus_set()

    def load(s):
        t = f"%{s.q.get().strip()}%"
        rows = s.db.q("""SELECT r.*, p.name AS pname FROM records r LEFT JOIN packages p ON p.code=r.package_code
                         WHERE r.client_name LIKE %s OR r.session_type LIKE %s OR r.package_code LIKE %s
                         OR r.contact LIKE %s ORDER BY r.session_date DESC LIMIT 60""", (t,) * 4)
        inner = s.sc.inner
        for w in inner.winfo_children():
            w.destroy()
        inner.columnconfigure((0, 1), weight=1, uniform="a")
        if not rows:
            tk.Label(inner, text="No records found.", font=(SANS, 12), fg=MUTED, bg=BG).grid(pady=30)
        for i, r in enumerate(rows):
            c = tk.Frame(inner, bg=CARD)
            c.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")
            cv = tk.Canvas(c, height=70, highlightthickness=0, bg=CARD)
            cv.pack(fill="x")
            art = s.ARTS[i % 4]
            cv.bind("<Configure>", lambda e, cv=cv, art=art: (cv.delete("all"), art(cv, e.width, e.height)))
            tk.Label(c, text=f"RECORD {r['id']:02d}", font=(SANS, 9, "bold"), fg=MUTED, bg=CARD).pack(anchor="w", padx=20, pady=(12, 4))
            for cap, val in (("CLIENT", f"{r['client_name']}  ({r['contact']})"),
                             ("SESSION", f"{fmt(r['session_date'])}  ·  {r['session_type']}"),
                             ("PACKAGE", f"{r['pname']}  [{r['package_code']}]")):
                tk.Label(c, text=cap, font=(SANS, 8), fg=MUTED, bg=CARD).pack(anchor="w", padx=20)
                tk.Label(c, text=val, font=(SANS, 11), fg=TEXT, bg=CARD).pack(anchor="w", padx=20, pady=(0, 6))
            tk.Frame(c, height=6, bg=CARD).pack()


# ------------------------- UPDATE / DELETE ---------------------
class FinderPage(Page):
    TAG, TITLE, SUB, ART = "", "", "", None

    def __init__(s, app):
        super().__init__(app)
        r = s.split(s.ART, 376)
        s.topbar(r)
        body = tk.Frame(r, bg=BG)
        body.pack(fill="both", expand=True, padx=50, pady=(26, 0))
        heading(body, s.TAG, s.TITLE, s.SUB)
        row = tk.Frame(body, bg=BG)
        row.pack(fill="x", pady=(8, 0))
        box = tk.Frame(row, bg=BG)
        box.pack(side="left", fill="x", expand=True)
        s.q = field(box, "Record ID or client name")
        Btn(row, "Find", s.find, w=110).pack(side="right", anchor="s", padx=(14, 0))
        s.q.bind("<Return>", lambda e: s.find())
        s.lb = tk.Listbox(body, height=4, bg=CARD, fg=TEXT, selectbackground=RED, relief="flat", bd=0,
                          highlightthickness=0, font=(SANS, 10), activestyle="none")
        s.lb.pack(fill="x", pady=(12, 0))
        s.lb.bind("<<ListboxSelect>>", lambda e: s.pick())
        s.form = tk.Frame(body, bg=BG)
        s.form.pack(fill="x", pady=(6, 0))
        s.rows = []

    def find(s):
        t = s.q.get().strip()
        s.clear()
        s.lb.delete(0, "end")
        if not t:
            return messagebox.showwarning("Fill the blanks", "Enter a record ID or client name.")
        s.rows = s.db.q("SELECT * FROM records WHERE id=%s OR client_name LIKE %s ORDER BY id",
                        (int(t) if t.isdigit() else 0, f"%{t}%"))
        if not s.rows:
            return messagebox.showinfo("No matching record", "No matching record found.")
        for r in s.rows:
            s.lb.insert("end", f"  #{r['id']}   {r['client_name']}   ·   {fmt(r['session_date'])}   ·   {r['package_code']}")
        if len(s.rows) == 1:
            s.lb.selection_set(0)
            s.chosen(s.rows[0])

    def pick(s):
        i = s.lb.curselection()
        if i:
            s.chosen(s.rows[i[0]])

    def clear(s):
        for w in s.form.winfo_children():
            w.destroy()


class UpdatePage(FinderPage):
    TAG, TITLE, SUB, ART = "04", "Update record", "Find a record, then edit its details.", staticmethod(art_film)
    SPEC = [("client_name", "Client name"), ("contact", "Contact details"), ("session_date", "Session date"),
            ("session_type", "Session type / location"), ("package_code", "Package code")]

    def chosen(s, r):
        s.clear()
        s.cur, s.ent = r, {}
        g = tk.Frame(s.form, bg=BG)
        g.pack(fill="x")
        g.columnconfigure((0, 1), weight=1, uniform="c")
        for i, (k, label) in enumerate(s.SPEC):
            e = field(g, label, row=i // 2, column=i % 2, sticky="ew", padx=(0, 18) if i % 2 == 0 else 0, pady=(10, 0))
            e.insert(0, fmt(r[k]))
            s.ent[k] = e
        row = tk.Frame(s.form, bg=BG)
        row.pack(anchor="w", pady=(18, 0))
        Btn(row, "Update", s.save, w=140).pack(side="left")
        Btn(row, "Cancel", s.clear, fill=False, w=120).pack(side="left", padx=12)

    def save(s):
        v = {k: (get(e) or fmt(s.cur[k])) for k, e in s.ent.items()}  # blank = unchanged
        v["package_code"] = v["package_code"].upper()
        err, d = validate(s.db, v["client_name"], v["contact"], v["session_date"], v["session_type"], v["package_code"])
        if err:
            return messagebox.showwarning("Please enter valid details", err)
        if not messagebox.askyesno("Confirm", "Update the selected record?"):
            return messagebox.showinfo("Cancelled", "You have cancelled the update process.")
        s.db.q("""UPDATE records SET client_name=%s, contact=%s, session_date=%s, session_type=%s, package_code=%s
                  WHERE id=%s""", (v["client_name"], v["contact"], d, v["session_type"], v["package_code"], s.cur["id"]), commit=True)
        messagebox.showinfo("Success", "Record updated successfully.")
        s.find()


class DeletePage(FinderPage):
    TAG, TITLE, SUB, ART = "05", "Delete record", "Find the record you want to remove.", staticmethod(art_bokeh)

    def chosen(s, r):
        s.clear()
        tk.Label(s.form, text=f"Selected: #{r['id']}  {r['client_name']}  ({fmt(r['session_date'])})",
                 font=(SANS, 11), fg=TEXT, bg=BG).pack(anchor="w", pady=(6, 0))
        row = tk.Frame(s.form, bg=BG)
        row.pack(anchor="w", pady=(14, 0))
        Btn(row, "Delete", lambda: s.delete(r), w=140).pack(side="left")
        Btn(row, "Cancel", s.clear, fill=False, w=120).pack(side="left", padx=12)

    def delete(s, r):
        if not messagebox.askyesno("Confirm to delete", f"Delete record #{r['id']} ({r['client_name']})?"):
            return messagebox.showinfo("Cancelled", "Deletion cancelled.")
        s.db.q("DELETE FROM records WHERE id=%s", (r["id"],), commit=True)
        messagebox.showinfo("Deleted", "Record successfully deleted.")
        s.find() if s.q.get().strip() else None
        s.clear()


# ------------------------- PACKAGES ----------------------------
class PackagePage(Page):
    def __init__(s, app):
        super().__init__(app)
        s.topbar(s, -60)
        body = tk.Frame(s, bg=BG)
        body.pack(fill="both", expand=True, padx=60, pady=(24, 18))
        heading(body, "06", "Packages", "Look up, add or remove a package.")
        s.q = field(body, "Package code or name")
        s.q.bind("<KeyRelease>", lambda e: s.look())
        card = tk.Frame(body, bg=BG, highlightbackground=LINE, highlightthickness=1)
        card.pack(fill="x", pady=(16, 8))
        cv = tk.Canvas(card, height=110, highlightthickness=0, bg=BG)
        cv.pack(fill="x", padx=18, pady=(18, 10))
        cv.bind("<Configure>", lambda e: (cv.delete("all"), art_film(cv, e.width, e.height)))
        g = tk.Frame(card, bg=BG)
        g.pack(fill="x", padx=18, pady=(0, 16))
        g.columnconfigure((0, 1), weight=1, uniform="a")
        s.v = {}
        for i, (k, cap) in enumerate((("name", "PACKAGE NAME"), ("code", "CODE"), ("inclusions", "INCLUSIONS"), ("price", "PRICE"))):
            f = tk.Frame(g, bg=BG)
            f.grid(row=i // 2, column=i % 2, sticky="w", pady=6)
            tk.Label(f, text=cap, font=(SANS, 9), fg=MUTED, bg=BG).pack(anchor="w")
            s.v[k] = tk.Label(f, font=(SANS, 13), fg=TEXT, bg=BG, wraplength=380, justify="left")
            s.v[k].pack(anchor="w")
        s.avail = tk.Label(body, font=(SANS, 9), fg=MUTED, bg=BG)
        s.avail.pack(anchor="w")
        row = tk.Frame(body, bg=BG)
        row.pack(anchor="w", pady=(14, 0))
        Btn(row, "Add package", lambda: PkgDialog(s), w=170).pack(side="left")
        Btn(row, "Delete package", s.delete, fill=False, w=170).pack(side="left", padx=12)
        Btn(row, "Back", lambda: s.go(Dashboard), fill=False, w=110).pack(side="left")
        s.cur = None
        s.look()

    def look(s):
        t = s.q.get().strip()
        s.cur = s.db.q("SELECT * FROM packages WHERE code=%s OR name LIKE %s ORDER BY code=%s DESC LIMIT 1",
                       (t, f"%{t}%", t), True) if t else None
        p = s.cur
        s.v["name"].config(text=p["name"] if p else ("Package not found" if t else "[Package name]"))
        s.v["code"].config(text=p["code"] if p else "[Code]")
        s.v["inclusions"].config(text=p["inclusions"] if p else "[Inclusions]")
        s.v["price"].config(text=f"₱{float(p['price']):,.2f}" if p else "[Price]")
        s.avail.config(text="Available codes: " + ", ".join(x["code"] for x in s.db.q("SELECT code FROM packages ORDER BY code")))

    def delete(s):
        if not s.cur:
            return messagebox.showwarning("No package", "Look up a package first.")
        if not messagebox.askyesno("Confirm to delete", f"Delete package {s.cur['code']}?"):
            return
        try:
            s.db.q("DELETE FROM packages WHERE code=%s", (s.cur["code"],), commit=True)
            messagebox.showinfo("Deleted", "Package successfully deleted.")
        except mysql.connector.Error:
            messagebox.showerror("Cannot delete", "This package is used by existing records.")
        s.look()


class PkgDialog(tk.Toplevel):
    def __init__(s, page):
        super().__init__(page, bg=BG, padx=34, pady=26)
        s.page = page
        s.title("Add package")
        s.transient(page.winfo_toplevel())
        s.grab_set()
        tk.Label(s, text="Add package", font=(SERIF, 22), fg=TEXT, bg=BG).pack(anchor="w")
        s.n, s.c = field(s, "Package name"), field(s, "Code")
        s.i, s.p = field(s, "Inclusions"), field(s, "Price")
        row = tk.Frame(s, bg=BG)
        row.pack(anchor="w", pady=(22, 0))
        Btn(row, "Save", s.save, w=130).pack(side="left")
        Btn(row, "Cancel", s.destroy, fill=False, w=120).pack(side="left", padx=12)

    def save(s):
        n, c, i, p = s.n.get().strip(), s.c.get().strip().upper(), s.i.get().strip(), s.p.get().strip()
        if not all([n, c, i, p]):
            return messagebox.showwarning("Fill the blanks", "Please fill the required blanks.", parent=s)
        try:
            price = float(p.replace(",", ""))
        except ValueError:
            return messagebox.showwarning("Invalid price", "Price must be a number.", parent=s)
        if s.page.db.q("SELECT code FROM packages WHERE code=%s", (c,), True):
            return messagebox.showerror("Duplicate", "That package code already exists.", parent=s)
        s.page.db.q("INSERT INTO packages VALUES (%s,%s,%s,%s)", (c, n, i, price), commit=True)
        messagebox.showinfo("Success", "Package added.", parent=s)
        s.page.q.delete(0, "end")
        s.page.q.insert(0, c)
        s.page.look()
        s.destroy()


if __name__ == "__main__":
    App().mainloop()
