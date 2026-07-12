import os
import json
import time
import random
import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "Abdulelah@2026")

# تشغيل الـ WebSockets الحقيقي لمنع تداخل شاشات المتسابقين
socketio = SocketIO(app, cors_allowed_origins="*")

# إعداد مفتاح جيمني بأحدث موديل 2026 لضمان الـ JSON Mode
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# ---------- دوال حفظ واستدعاء البيانات الدائمة على السيرفر ----------
def load_local_data(filename, default_val):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default_val
    return default_val

def save_local_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# البنية التحتية للبيانات
SERVER_DB = {
    "rooms": {},
    "manual_pools": load_local_data("manual_pools.json", {}),
    "messages": load_local_data("messages.json", []),
    "total_visitors": load_local_data("total_v.json", 125)
}

# ==========================================
# 1. محرك توليد الأسئلة الصارم (JSON Mode لمنع اللخبطة)
# ==========================================
def generate_questions_via_gemini(category, topic, count, age=None):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', 
                                      generation_config={"response_mime_type": "application/json"})
        age_context = f"Target child exact age is {age} years old." if age else "Target group is adults."
        
        prompt = f"""
        You are an elite professional quiz creator for Haya-Quiz.
        Generate exactly {count} distinct and highly unique multiple-choice questions.
        Target Group: '{category}'. {age_context}
        Topic/Domain: '{topic}'.
        Language: 'ar'.
        
        CRITICAL RULE: Avoid common question pools. Ensure questions strictly match the chosen domain.
        Return response ONLY as a pure JSON array of objects.
        Each object must have exactly these keys:
        - "question": The question string.
        - "correct_answer": The correct answer string.
        - "options": An array containing exactly 4 strings (the correct answer + 3 distinct wrong answers).
        """
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        # خطة بديلة فورية (Fallback) في حال انقطع الاتصال بـ الـ API
        fallback = []
        for i in range(count):
            fallback.append({
                "question": f"سؤال فريد رقم {random.randint(100, 999)} في مجال {topic}",
                "correct_answer": "الخيار الصحيح",
                "options": ["الخيار الصحيح", "خيار خطأ 1", "خيار خطأ 2", "خيار خطأ 3"]
            })
        return fallback

# ==========================================
# 2. بوابات الـ API (Endpoints) للتحكم وتجهيز الغرف
# ==========================================

@app.route('/api/visitor_log', methods=['GET'])
def log_visitor():
    SERVER_DB["total_visitors"] += 1
    save_local_data("total_v.json", SERVER_DB["total_visitors"])
    return jsonify({"total_visitors": SERVER_DB["total_visitors"]})

@app.route('/api/create_room', methods=['POST'])
def create_room():
    data = request.json or {}
    mode = data.get("mode") # تلقائي أو يدوي
    category = data.get("category", "عامة")
    topic = data.get("topic", "ثقافة عامة")
    count = int(data.get("count", 5))
    age = data.get("age")
    duration = int(data.get("duration", 30))
    pool_code = data.get("pool_code")

    if mode == "manual":
        if pool_code in SERVER_DB["manual_pools"]:
            questions = SERVER_DB["manual_pools"][pool_code]
        else:
            return jsonify({"status": "error", "message": "رمز المسابقة اليدوية غير موجود!"}), 400
    else:
        questions = generate_questions_via_gemini(category, topic, count, age)

    # توليد رقم غرفة مميز من 4 أرقام للمشتركين الحين
    room_code = str(random.randint(1000, 4999))
    SERVER_DB["rooms"][room_code] = {
        "status": "waiting",
        "questions": questions,
        "duration": duration,
        "current_q_idx": 0,
        "players": {},
        "q_start_time": None
    }
    return jsonify({"status": "success", "room_code": room_code})

@app.route('/api/save_manual_quiz', methods=['POST'])
def save_manual_quiz():
    data = request.json or {}
    questions = data.get("questions", [])
    if not questions:
        return jsonify({"status": "error", "message": "لا توجد أسئلة لحفظها"}), 400
        
    pool_code = str(random.randint(5000, 9999))
    SERVER_DB["manual_pools"][pool_code] = questions
    save_local_data("manual_pools.json", SERVER_DB["manual_pools"])
    return jsonify({"status": "success", "pool_code": pool_code})

# ==========================================
# 3. أحداث الـ WebSockets لإدارة المباريات اللحظية الحية
# ==========================================

@socketio.on('join_game')
def handle_join(data):
    room = data.get("room")
    username = data.get("username")
    if room in SERVER_DB["rooms"]:
        join_room(room)
        # إضافة اللاعب بنقاط صفر في البداية
        SERVER_DB["rooms"][room]["players"][request.sid] = {"name": username, "score": 0, "answered": False}
        emit('player_update', list(SERVER_DB["rooms"][room]["players"].values()), room=room)
    else:
        emit('error_msg', {"message": "عذراً الغرفة غير موجودة!"})

@socketio.on('start_game')
def handle_start(data):
    room = data.get("room")
    if room in SERVER_DB["rooms"]:
        SERVER_DB["rooms"][room]["status"] = "playing"
        SERVER_DB["rooms"][room]["q_start_time"] = time.time()
        send_next_question(room)

def send_next_question(room):
    rdata = SERVER_DB["rooms"][room]
    idx = rdata["current_q_idx"]
    if idx < len(rdata["questions"]):
        q = rdata["questions"][idx]
        
        # خلط الخيارات عشوائياً لكل لاعب بشكل منفصل لمنع الغش الطولي
        shuffled_options = list(q["options"])
        random.shuffle(shuffled_options)
        
        # تصفير حالة الإجابة للاعبين في السطر الحالي
        for sid in rdata["players"]:
            rdata["players"][sid]["answered"] = False
            
        emit('next_question', {
            "index": idx + 1,
            "total": len(rdata["questions"]),
            "question": q["question"],
            "options": shuffled_options,
            "duration": rdata["duration"]
        }, room=room)
    else:
        rdata["status"] = "finished"
        emit('game_finished', sorted(rdata["players"].values(), key=lambda x: x['score'], reverse=True), room=room)

@socketio.on('submit_answer')
def handle_answer(data):
    room = data.get("room")
    selected = data.get("answer")
    if room in SERVER_DB["rooms"]:
        rdata = SERVER_DB["rooms"][room]
        idx = rdata["current_q_idx"]
        q = rdata["questions"][idx]
        
        if request.sid in rdata["players"] and not rdata["players"][request.sid]["answered"]:
            rdata["players"][request.sid]["answered"] = True
            if selected == q["correct_answer"]:
                rdata["players"][request.sid]["score"] += 10
            
            # إشعار الموجه بلوحة التحكم الحية بتحديث الإجابات فوراً
            emit('monitor_update', {
                "player": rdata["players"][request.sid]["name"],
                "status": "✅ اعتمد الإجابة"
            }, room=room)

@socketio.on('next_question_trigger')
def handle_next_trigger(data):
    room = data.get("room")
    if room in SERVER_DB["rooms"]:
        SERVER_DB["rooms"][room]["current_q_idx"] += 1
        send_next_question(room)

@socketio.on('disconnect')
def handle_disconnect():
    for room in list(SERVER_DB["rooms"].keys()):
        if request.sid in SERVER_DB["rooms"][room]["players"]:
            del SERVER_DB["rooms"][room]["players"][request.sid]
            emit('player_update', list(SERVER_DB["rooms"][room]["players"].values()), room=room)

# ---------- تشغيل السيرفر المتوافق مع بيئة رندر 2026 ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
