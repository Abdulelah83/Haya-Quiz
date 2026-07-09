import streamlit as st
import pandas as pd
import time
import random
import os
import json
from datetime import datetime
import google.generativeai as genai

# 1. إعدادات الصفحة والهوية البصرية وتحسين الألوان
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz Pro", 
    page_icon="🎮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة متغيرات الجلسة الأساسية
if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"
if 'generated_room_code' not in st.session_state: st.session_state.generated_room_code = None
if 'admin_authenticated' not in st.session_state: st.session_state.admin_authenticated = False
if 'lang' not in st.session_state: st.session_state.lang = "ar"  # اللغة الافتراضية

# قاموس اللغتين لضمان سهولة التحويل الكامل للموقع
TRANSLATIONS = {
    "ar": {
        "title": "منصة مسابقات هيا  🎯",
        "home": "🏠 الرئيسية",
        "contact": "📞 تواصل معنا",
        "settings": "⚙️ الإعدادات",
        "secret_key": "🔑 أدخل الرمز السري لفتح الإعدادات المتقدمة:",
        "confirm": "🔓 تأكيد الدخول",
        "logout": "🚪 خروج من الإعدادات",
        "wrong_pass": "❌ الرمز السري غير صحيح!",
        "visits": "📊 إجمالي الزيارات التراكمية",
        "ready": "### جاهزون للتحدي والمنافسة الحية الحين؟",
        "create_room": "🏆 إنشاء وإدارة مسابقة حية",
        "join_player": "🎮 دخول كمتسابق",
        "test_yourself": "🕹️ تحدي اختبر نفسك الفردي",
        "groups_mode": "👥 طور المجموعات والفرق قيد التأسيس",
        "footer": "تطوير عبد الإله العنزي | Developed by Abdulelah Al-Enazi",
        "num_q_label": "عدد الأسئلة المطلوبة (من 1 إلى 20):",
        "time_q_label": "الوقت المتاح لكل سؤال (ثواني):",
        "gen_room_btn": "🎲 توليد غرفة المسابقة عبر Gemini AI",
        "q_src_label": "اختر الفئة للجولة المستهدفة:",
        "q_src_kids": "أسئلة الأطفال",
        "q_src_adults": "أسئلة الكبار",
        "q_src_qudrat": "اختبار القدرات والتحصيلي 🇸🇦",
        "correct_notify": "صح بطل كفو! 🥳",
        "wrong_notify": "❌ للأسف إجابة خاطئة ركز في القادم!",
        "correct_is": "💡 الصح هو:"
    },
    "en": {
        "title": "Haya Quiz Platform  🎯",
        "home": "🏠 Home",
        "contact": "📞 Contact Us",
        "settings": "⚙️ Settings",
        "secret_key": "🔑 Enter Password for Advanced Settings:",
        "confirm": "🔓 Confirm Login",
        "logout": "🚪 Exit Settings",
        "wrong_pass": "❌ Incorrect Password!",
        "visits": "📊 Total Cumulative Visits",
        "ready": "### Ready for the Challenge & Live Competition?",
        "create_room": "🏆 Create & Manage Live Quiz",
        "join_player": "🎮 Enter as Contestant",
        "test_yourself": "🕹️ Solo Challenge (Test Yourself)",
        "groups_mode": "👥 Groups Mode is Under Construction",
        "footer": "Developed by Abdulelah Al-Enazi | تطوير عبد الإله العنزي",
        "num_q_label": "Number of Required Questions (1 to 20):",
        "time_q_label": "Time Limit per Question (Seconds):",
        "gen_room_btn": "🎲 Generate Quiz Room via Gemini AI",
        "q_src_label": "Choose Category for Target Round:",
        "q_src_kids": "Kids Questions",
        "q_src_adults": "Adults Questions",
        "q_src_qudrat": "Qudrat & Tahsili Exams 🇸🇦",
        "correct_notify": "Correct! Excellent Job! 🥳",
        "wrong_notify": "❌ Unfortunately Wrong, Focus on Next!",
        "correct_is": "💡 Correct Answer is:"
    }
}

lang_dict = TRANSLATIONS[st.session_state.lang]

# تخصيص CSS للمظهر الفخم والألوان الجذابة مع دعم اتجاه النص حسب اللغة
direction = "rtl" if st.session_state.lang == "ar" else "ltr"
align = "right" if st.session_state.lang == "ar" else "left"

st.markdown(f"""
    <style>
    .main-title {{ text-align: center; color: #4F46E5; font-size: 2.8rem; font-weight: bold; margin-bottom: 5px; direction: {direction}; }}
    .stRadio > div {{ flex-direction: row; justify-content: center; gap: 15px; }}
    div.stButton > button:first-child {{ 
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); 
        color: white; border-radius: 12px; border: none; font-size: 1.1rem; padding: 10px 20px;
    }}
    .chat-container {{ background-color: #E5DDD5; padding: 15px; border-radius: 12px; max-height: 350px; overflow-y: auto; display: flex; flex-direction: column; }}
    .msg-box-admin {{ background-color: #DCF8C6; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: {align}; align-self: flex-end; max-width: 80%; }}
    .msg-box-player {{ background-color: #FFFFFF; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: {align}; align-self: flex-start; max-width: 80%; }}
    .leaderboard-box {{ background: linear-gradient(135deg, #6EE7B7 0%, #3B82F6 100%); padding: 20px; border-radius: 12px; color: white; text-align: center; font-weight: bold; font-size: 1.5rem; margin-bottom: 20px; }}
    .footer-text {{ text-align: center; color: #9CA3AF; font-size: 1rem; font-weight: 500; padding: 20px 0; border-top: 1px solid #E5E7EB; margin-top: 50px; }}
    body {{ direction: {direction}; text-align: {align}; }}
    </style>
""", unsafe_allow_html=True)

# دالة لتوليد الأسئلة فورياً وذكياً عبر Gemini بحد أقصى 20 سؤالاً
def generate_questions_via_gemini(category, count, lang):
    try:
        # الاتصال بنموذج Gemini الفائق والذكي المتاح في حسابك
        genai.configure() 
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are a professional quiz generator for a platform called Haya-Quiz.
        Generate exactly {count} multiple-choice questions for the category: '{category}'.
        The output language MUST be: '{lang}'.
        
        Return the response ONLY as a valid JSON array of objects, with no markdown formatting, no ```json tags.
        Each object must have exactly these keys:
        - "السؤال": The question string.
        - "الخيار 1 - الصحيح": The correct answer string.
        - "الخيار 2": Wrong answer 1.
        - "الخيار 3": Wrong answer 2.
        - "الخيار 4": Wrong answer 3.
        """
        
        response = model.generate_content(prompt)
        text_clean = response.text.strip().replace("```json", "").replace("```", "")
        questions_list = json.loads(text_clean)
        return questions_list
    except Exception as e:
        # حل بديل (Fallback) في حال حدوث أي خطأ بالاتصال لتأمين استمرار اللعبة دون توقف
        st.warning(f"AI connection notice, using standby questions.")
        fallback_q = []
        for i in range(count):
            fallback_q.append({
                "السؤال": f"سؤال تجريبي رقم {i+1} في قسم {category}",
                "الخيار 1 - الصحيح": "الخيار الصحيح",
                "الخيار 2": "خيار خطأ أ",
                "الخيار 3": "خيار خطأ ب",
                "الخيار 4": "خيار خطأ ج"
            })
        return fallback_q

# دوال مساعدة لربط وحفظ البيانات دائمياً في ملفات السيرفر الصلبة
def load_local_data(filename, default_val):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default_val
    return default_val

def save_local_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@st.cache_resource
def get_server_db():
    return {
        "rooms": {}, 
        "messages": load_local_data("messages.json", []), 
        "total_visitors": load_local_data("total_v.json", 0), 
        "visitor_history": load_local_data("history_v.json", {})
    }

db = get_server_db()

# محرك العداد الذكي للزوار التراكمي
if 'counted' not in st.session_state:
    db["total_visitors"] += 1
    today_str = datetime.now().strftime("%Y-%m-%d")
    db["visitor_history"][today_str] = db["visitor_history"].get(today_str, 0) + 1
    save_local_data("total_v.json", db["total_visitors"])
    save_local_data("history_v.json", db["visitor_history"])
    st.session_state.counted = True

@st.fragment
def show_live_chat(room_id, user_name, is_admin):
    room_ref = db["rooms"].get(room_id)
    if not room_ref: return
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for chat_msg in room_ref["chat_history"]:
        msg_class = "msg-box-admin" if chat_msg["user_type"] == "admin" else "msg-box-player"
        st.markdown(f"<div class='{msg_class}'><strong>{chat_msg['name']}:</strong> {chat_msg['text']}</div>", unsafe_allow_html=True)
    st.markdown("</div><br>", unsafe_allow_html=True)
    with st.form(f"chat_form_{room_id}", clear_on_submit=True):
        col_c1, col_c2 = st.columns([4, 1])
        c_text = col_c1.text_input("Message / رسالة:", label_visibility="collapsed", key=f"in_{room_id}")
        if col_c2.form_submit_button("Send" if st.session_state.lang == "en" else "إرسال"):
            if c_text:
                db["rooms"][room_id]["chat_history"].append({"user_type": "admin" if is_admin else "player", "name": "المدير " if is_admin else user_name, "text": c_text})
                st.rerun()
    time.sleep(2); st.rerun()

# الشريط العلوي الثابت للمنصة وزر تحويل اللغة الذكي
navbar_cols = st.columns([1, 4, 1])
with navbar_cols[1]:
    col_nav1, col_nav2, col_nav3 = st.columns([2, 2, 1])
    if col_nav1.button(lang_dict["home"], use_container_width=True): st.session_state.curr_page = "home"; st.rerun()
    if col_nav2.button(lang_dict["contact"], use_container_width=True): st.session_state.curr_page = "contact_mode"; st.rerun()
    
    # زر تحويل اللغة الفوري
    current_lang_label = "🌐 English" if st.session_state.lang == "ar" else "🌐 العربية"
    if col_nav3.button(current_lang_label, use_container_width=True):
        st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
        st.rerun()

st.write("---")

# القائمة الجانبية (Sidebar) المحصنة للتحكم والزيارات والتنبيهات المذكورة
with st.sidebar:
    st.markdown(f"### {lang_dict['settings']}")
    if not st.session_state.admin_authenticated:
        admin_pass = st.text_input(lang_dict["secret_key"], type="password")
        if st.button(lang_dict["confirm"]):
            if admin_pass == "Abdulelah@2026":
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error(lang_dict["wrong_pass"])
    else:
        if st.button(lang_dict["logout"]):
            st.session_state.admin_authenticated = False
            st.rerun()
        st.write("---")
        st.metric(label=lang_dict["visits"], value=f"{db['total_visitors']}")

# الصفحة الرئيسية للموقع
if st.session_state.curr_page == "home":
    st.markdown(f"<h2 style='text-align:center; color:#4F46E5;'>{lang_dict['title']}</h2>", unsafe_allow_html=True)
    col_l_img, col_r_btn = st.columns([1, 2])
    with col_l_img:
        if os.path.exists("my_kids.png"): st.image("my_kids.png", use_container_width=True)
        else: st.info("🎮 Haya Multi-Quiz System")
            
    with col_r_btn:
        st.write(lang_dict["ready"])
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button(lang_dict["create_room"], use_container_width=True): st.session_state.curr_page = "admin_mode"; st.rerun()
        with col_b2:
            if st.button(lang_dict["join_player"], use_container_width=True): st.session_state.curr_page = "player_mode"; st.rerun()
        st.write("---")
        col_b3, col_b4 = st.columns(2)
        with col_b3:
            if st.button(lang_dict["test_yourself"], use_container_width=True): st.session_state.curr_page = "culture_mode"; st.rerun()
        with col_b4:
            st.info(lang_dict["groups_mode"])

# صفحة تواصل معنا
elif st.session_state.curr_page == "contact_mode":
    st.markdown(f"### {lang_dict['contact']}")
    with st.form("contact"):
        c_name = st.text_input("Name / الاسم:")
        c_msg_txt = st.text_area("Your Message / رسالتك:")
        if st.form_submit_button("Send / إرسال"):
            if c_name and c_msg_txt: 
                db["messages"].append({"name": c_name, "msg": c_msg_txt})
                save_local_data("messages.json", db["messages"])
                st.success("🎉 Sent Successfully! / تم الإرسال بنجاح!")

# لوحة الموجه وإدارة المسابقات الحية لتوليد الأسئلة من 1 إلى 20 عبر جيمني
elif st.session_state.curr_page == "admin_mode":
    st.markdown(f"<h2 style='text-align:center;'>{lang_dict['create_room']}</h2>", unsafe_allow_html=True)
    if 'my_live_room' not in st.session_state:
        q_src = st.radio(lang_dict["q_src_label"], [lang_dict["q_src_kids"], lang_dict["q_src_adults"], lang_dict["q_src_qudrat"]])
        
        # ميزة اختيار من 1 إلى 20 سؤالاً التي طلبتها بدقة
        num_q = st.number_input(lang_dict["num_q_label"], min_value=1, max_value=20, value=5)
        t_val = st.slider(lang_dict["time_q_label"], 5, 60, 15)
        
        if st.button(lang_dict["gen_room_btn"]):
            with st.spinner("Gemini is generating elite questions... ⚡"):
                chosen_questions = generate_questions_via_gemini(q_src, int(num_q), st.session_state.lang)
                
            if not st.session_state.generated_room_code: 
                st.session_state.generated_room_code = str(random.randint(1000, 9999))
            rcode = st.session_state.generated_room_code
            st.session_state.my_live_room = rcode
            
            db["rooms"][rcode] = {
                "players": [], "status": "waiting", "current_q_idx": 0, 
                "questions": chosen_questions, "chat_history": [], "duration": t_val, 
                "scores": {}, "q_start_time": time.time(), "answered_players": []
            }
            st.rerun()
    else:
        rid = st.session_state.my_live_room; rdata = db["rooms"].get(rid)
        if rdata:
            st.success(f"🎲 Room Code / رقم الغرفة: **{rid}**")
            col_l, col_r = st.columns([2, 1])
            with col_l:
                if rdata["status"] == "waiting":
                    if st.button("🚀 Start Quiz / إطلاق البث"): 
                        db["rooms"][rid]["status"] = "playing"; db["rooms"][rid]["q_start_time"] = time.time(); st.rerun()
                elif rdata["status"] == "playing":
                    qi = rdata["current_q_idx"]; ql = rdata["questions"]
                    if qi < len(ql):
                        st.write(f"📊 Question ({qi+1}/{len(ql)}): **{ql[qi]['السؤال']}**")
                        st.success(f"{lang_dict['correct_is']} **{ql[qi]['الخيار 1 - الصحيح']}**")
                        
                        rem = max(0, int(rdata["duration"] - (time.time() - rdata["q_start_time"])))
                        st.warning(f"⏱️ Timer: {rem}s")
                        if rem <= 0 or st.button("➡️ Next Question / التالي"):
                            db["rooms"][rid]["current_q_idx"] += 1; db["rooms"][rid]["q_start_time"] = time.time(); st.rerun()
                        time.sleep(1); st.rerun()
                    else: 
                        db["rooms"][rid]["status"] = "finished"; st.rerun()
                elif rdata["status"] == "finished":
                    st.markdown("<div class='leaderboard-box'>🏆 Leaderboard 🏆</div>", unsafe_allow_html=True)
                    for rank, (p, s) in enumerate(sorted(rdata["scores"].items(), key=lambda x: x[1], reverse=True)):
                        st.write(f"### 🏅 {rank+1}: **{p}** -> {s} Pts!")
                if st.button("🛑 Close Room / إنهاء الغرفة"):
                    if rid in db["rooms"]: del db["rooms"][rid]
                    del st.session_state.my_live_room; st.session_state.generated_room_code = None; st.rerun()
            with col_r: show_live_chat(rid, "المدير", is_admin=True)

# دخول كمتسابق والضغط السريع الفوري على زر اعتماد الإجابة
elif st.session_state.curr_page == "player_mode":
    if 'joined_live_room' not in st.session_state:
        cc = st.text_input("Room Code (4 Digits):")
        cn = st.text_input("Your Name:")
        if st.button("🚪 Enter Room"):
            if cc in db["rooms"]: 
                db["rooms"][cc]["players"].append(cn); db["rooms"][cc]["scores"][cn] = 0
                st.session_state.joined_live_room = cc; st.session_state.my_joined_name = cn; st.rerun()
    else:
        rid = st.session_state.joined_live_room; pname = st.session_state.my_joined_name; rdata = db["rooms"].get(rid)
        if rdata:
            col_l, col_r = st.columns([2, 1])
            with col_l:
                if rdata["status"] == "waiting": st.info("⏳ Waiting for Admin to start...")
                elif rdata["status"] == "playing":
                    qi = rdata["current_q_idx"]; ql = rdata["questions"]
                    if qi < len(ql):
                        st.write(f"### ❓ {ql[qi]['السؤال']}")
                        c_ans = str(ql[qi]["الخيار 1 - الصحيح"])
                        
                        if f"sh_opts_{qi}" not in st.session_state:
                            opts = [c_ans, str(ql[qi]["الخيار 2"]), str(ql[qi]["الخيار 3"]), str(ql[qi]["الخيار 4"])]
                            random.shuffle(opts); st.session_state[f"sh_opts_{qi}"] = opts
                            
                        sel = st.radio("Choose / اختر:", st.session_state[f"sh_opts_{qi}"], key=f"p_s_{qi}")
                        rem = max(0, int(rdata["duration"] - (time.time() - rdata["q_start_time"])))
                        st.warning(f"⏳ Time Left: {rem}s")
                        
                        # الضغط اللحظي السريع للاعتماد لمعرفة النتيجة فوراً
                        if st.button("✔️ Submit Answer / اعتماد الإجابة"):
                            if sel == c_ans:
                                st.success(lang_dict["correct_notify"])
                                db["rooms"][rid]["scores"][pname] += 10
                            else:
                                st.error(lang_dict["wrong_notify"])
                                st.info(f"{lang_dict['correct_is']} {c_ans}")
                            time.sleep(2)
                        time.sleep(1); st.rerun()
            with col_r: show_live_chat(rid, pname, is_admin=False)

# تذييل الحقوق الثابت بلغتين المطور بالكامل
st.markdown(f"<div class='footer-text'>{lang_dict['footer']}</div>", unsafe_allow_html=True)
