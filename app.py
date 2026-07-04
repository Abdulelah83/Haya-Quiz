import streamlit as st
import os
import json
import random
import time
from datetime import datetime
import pandas as pd

# 1. إعدادات الصفحة والهوية البصرية الفخمة الجاذبة
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz Pro", 
    page_icon="🎮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title { text-align: center; color: #4F46E5; font-size: 3rem; font-weight: bold; margin-bottom: 5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }
    .sub-title { text-align: center; color: #6B7280; font-size: 1.3rem; margin-bottom: 30px; }
    .stRadio > div { flex-direction: row; justify-content: center; gap: 15px; }
    
    div.stButton > button:first-child { 
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); 
        color: white; 
        border-radius: 12px; 
        border: none; 
        font-size: 1.1rem; 
        padding: 10px 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover { 
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .message-box { background-color: #F3F4F6; border-right: 5px solid #4F46E5; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .leaderboard-box { background: linear-gradient(135deg, #6EE7B7 0%, #3B82F6 100%); padding: 20px; border-radius: 12px; color: white; text-align: center; font-weight: bold; font-size: 1.5rem; margin-bottom: 20px; }
    .footer-text { text-align: center; color: #9CA3AF; font-size: 1rem; font-weight: 500; padding: 20px 0; border-top: 1px solid #E5E7EB; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# 2. إدارة ملفات التخزين المحلي والذاكرة الدائمة بالسيرفر
DATA_DIR = "database_local"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

def load_local_data(filename, default_value):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f: return json.load(f)
    return default_value

def save_local_data(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

# 3. عدّاد زوار الموقع الدائم والتحليلات
if 'visitor_counted' not in st.session_state:
    visitors = load_local_data("visitors.json", {"total_count": 0, "history": {}})
    visitors["total_count"] += 1
    today_str = datetime.now().strftime("%Y-%m-%d")
    visitors["history"][today_str] = visitors["history"].get(today_str, 0) + 1
    save_local_data("visitors.json", visitors)
    st.session_state.visitor_counted = True

# الذاكرة السحابية المشتركة للغرف والأسئلة (تخزين السيرفر الثابت)
@st.cache_resource
def get_server_db():
    default_q = [
        {"السؤال": "ما الكوكب الأقرب إلى الشمس؟", "الخيار 1 - الصحيح": "عطارد", "الخيار 2": "الزهرة", "الخيار 3": "الأرض", "الخيار 4": "المريخ"},
        {"السؤال": "ما اسم القوة التي تجذب الأشياء نحو الأرض؟", "الخيار 1 - الصحيح": "الجاذبية", "الخيار 2": "الإحتكاك", "الخيار 3": "المغناطيسية", "الخيار 4": "الدفع"}
    ]
    return {"rooms": {}, "kids_q": default_q, "adults_q": [], "messages": []}

s_db = get_server_db()

# تهيئة الجلسة الحالية للمستخدم
if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False
if 'individual_challenge' not in st.session_state: st.session_state.individual_challenge = {"status": "idle", "current_q": 0, "correct_ans": 0, "q_list": []}
if 'generated_room_code' not in st.session_state: st.session_state.generated_room_code = None

manual_questions = load_local_data("manual_questions.json", [])

@st.fragment
def show_live_chat(room_id, user_name, is_admin):
    room_ref = s_db["rooms"].get(room_id)
    if not room_ref: return
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for chat_msg in room_ref["chat_history"]:
        msg_class = "msg-box-admin" if chat_msg["user_type"] == "admin" else "msg-box-player"
        st.markdown(f"<div class='{msg_class}'><span class='msg-user'>{chat_msg['name']}</span>{chat_msg['text']}</div>", unsafe_allow_html=True)
    st.markdown("</div><br>", unsafe_allow_html=True)
    
    with St.form(f"chat_form_{room_id}", clear_on_submit=True):
        col_c1, col_c2 = st.columns([4, 1])
        c_text = col_c1.text_input("اكتب رسالة فورية:", label_visibility="collapsed", key=f"input_{room_id}")
        if col_c2.form_submit_button("إرسال"):
            if c_text:
                curr_t = datetime.now().strftime("%H:%M")
                s_db["rooms"][room_id]["chat_history"].append({"user_type": "admin" if is_admin else "player", "name": "المدير (أبو صالح)" if is_admin else user_name, "text": c_text, "time": curr_t})
                St.rerun()
    Time.sleep(2)
    St.rerun()

# 4. الشريط العلوي الثابت للمنصة
navbar_cols = st.columns([1, 4, 1])
with navbar_cols[1]:
    col_nav1, col_nav2 = st.columns(2)
    if col_nav1.button("🏠 الصفحة الرئيسية", use_container_width=True): st.session_state.curr_page = "home"; st.rerun()
    if col_nav2.button("📞 تواصل معنا", use_container_width=True): st.session_state.curr_page = "contact_mode"; st.rerun()

St.write("---")

# الصفحة الرئيسية
if st.session_state.curr_page == "home":
    St.markdown("<h1 class='main-title'>منصة هيا للمسابقات العائلية 🎯</h1>", unsafe_allow_html=True)
    St.markdown("<p class='sub-title'>المتعة والثقافة في مكان واحد للأبناء والآباء</p>", unsafe_allow_html=True)
    
    col_left_img, col_right_content = st.columns([1, 2])
    with col_left_img:
        if os.path.exists("my_kids.png"): st.image("my_kids.png", use_container_width=True)
        else: st.info("🎮 جاهزون لإطلاق التحدي الحماسي!")
            
    with col_right_content:
        St.write("### اختر نمط اللعب المفضل لديك للحين:")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            if st.button("👑 لوحة تحكم الموجه", use_container_width=True): st.session_state.curr_page = "admin_mode"; st.rerun()
        with col_m2:
            if st.button("🎮 انضم كمتسابق", use_container_width=True): st.session_state.curr_page = "player_mode"; st.rerun()
        with col_m3:
            if st.button("🕹️ تحدي اختبر نفسك", use_container_width=True): st.session_state.curr_page = "culture_mode"; st.rerun()
        with col_m4:
            if st.button("👥 طور المجموعات", use_container_width=True): st.session_state.curr_page = "group_mode"; st.rerun()

# صفحة تواصل معنا
elif st.session_state.curr_page == "contact_mode":
    St.markdown("### 📞 تواصل معنا وإبداء رأيك")
    with st.form("contact_form", clear_on_submit=True):
        p_name = st.text_input("اسمك الكريم:")
        p_msg = st.text_area("اكتب رسالتك أو ملاحظتك هنا:")
        if st.form_submit_button("📤 إرسال الرسالة الآن"):
            if p_name and p_msg:
                current_messages = load_local_data("messages.json", [])
                current_messages.append({"name": p_name, "message": p_msg, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
                save_local_data("messages.json", current_messages)
                St.success("🎉 تم إرسال رسالتك بنجاح وسيتطلع عليها مالك المنصة فوراً!")
            else: st.warning("⚠️ يرجى ملء البيانات.")

# 👑 لوحة تحكم الموجه والمالك
elif st.session_state.curr_page == "admin_mode":
    St.markdown("<h2 style='text-align:center;'>👑 لوحة تحكم مالك المنصة</h2>", unsafe_allow_html=True)
    if not st.session_state.admin_logged_in:
        col_login, _ = st.columns([1, 2])
        with col_login:
            admin_password = st.text_input("أدخل الرقم السري للمالك:", type="password")
            if st.button("🔓 فتح لوحة التحكم"):
                if admin_password == "Abdulelah@2026":
                    st.session_state.admin_logged_in = True; st.rerun()
                else: st.error("❌ الرقم السري غير صحيح.")
    else:
        if st.button("🚪 تسجيل الخروج"): st.session_state.admin_logged_in = False; st.rerun()
        St.write("---")
        
        col_main_admin, col_inbox_side = st.columns([2, 1])
        with col_main_admin:
            st.markdown("### 📊 إحصائيات زوار الموقع")
            visitors_data = load_local_data("visitors.json", {"total_count": 0, "history": {}})
            St.metric(label="إجمالي عدد الزوار الحقيقيين", value=f"{visitors_data['total_count']} زائر")
            if visitors_data["history"]:
                df_visits = pd.DataFrame(list(visitors_data["history"].items()), columns=["التاريخ", "الزيارات"])
                St.line_chart(df_visits.set_index("التاريخ"))
            
            St.write("---")
            # رفع الإكسيل للأطفال والكبار وحفظه في السيرفر دائمياً (💾 التخزين الدائم)
            st.markdown("### 🗂️ رفع وإدارة ملفات الأسئلة")
            kids_file = st.file_uploader("رفع إكسيل الأطفال المحدث:", type=["xlsx"], key="adm_k")
            if kids_file:
                s_db["kids_q"] = pd.read_excel(kids_file).to_dict(orient='records')
                St.success("✅ اعتمدت أسئلة الأطفال بالسيرفر!")
                
            adults_file = st.file_uploader("رفع إكسيل الكبار المحدث:", type=["xlsx"], key="adm_a")
            if adults_file:
                s_db["adults_q"] = pd.read_excel(adults_file).to_dict(orient='records')
                St.success("✅ اعتمدت أسئلة الكبار بالسيرفر!")
            
            St.write("---")
            # 📝 كتابة سؤال يدوي وإدراجه فوراً بالجولة
            St.markdown("### 📝 إضافة سؤال يدوي للمسابقات")
            with st.form("manual_q_form", clear_on_submit=True):
                m_question = st.text_input("نص السؤال اليدوي:")
                opt1 = st.text_input("الخيار 1 (الصحيح):")
                opt2 = st.text_input("الخيار 2:")
                opt3 = st.text_input("الخيار 3:")
                opt4 = st.text_input("الخيار 4:")
                if st.form_submit_button("➕ حفظ وإدراج السؤال اليدوي"):
                    if m_question and opt1:
                        manual_questions.append({"السؤال": m_question, "الخيار 1 - الصحيح": opt1, "الخيار 2": opt2, "الخيار 3": opt3, "الخيار 4": opt4})
                        save_local_data("manual_questions.json", manual_questions)
                        St.success("🎯 تم حفظ السؤال اليدوي!")
            
            St.write("---")
            St.markdown("### 🏆 إدارة المسابقات الحية الحالية")
            if 'my_live_room' not in st.session_state:
                q_src = st.radio("الفئة للجولة المستهدفة:", ["أسئلة الأطفال", "أسئلة الكبار"])
                num_limit = st.number_input("عدد الأسئلة:", min_value=1, value=5)
                timer_val = st.slider("الوقت لكل سؤال (ثواني):", 5, 60, 12)
                
                if st.button("🎲 توليد غرفة المسابقة"):
                    pool = s_db["kids_q"] if "الأطفال" in q_src else s_db["adults_q"]
                    final_pool = manual_questions + pool
                    if not final_pool: st.error("بنك الأسئلة فارغ!")
                    else:
                        if not st.session_state.generated_room_code: st.session_state.generated_room_code = str(random.randint(1000, 9999))
                        room_code = st.session_state.generated_room_code
                        st.session_state.my_live_room = room_code
                        chosen_q = final_pool[:len(manual_questions)] + random.sample(pool, min(len(pool), max(1, int(num_limit) - len(manual_questions))))
                        s_db["rooms"][room_code] = {"players": [], "status": "waiting", "current_q_idx": 0, "questions": chosen_q, "chat_history": [], "duration": timer_val, "scores": {}, "q_start_time": time.time(), "answered_players": []}
                        St.rerun()
            else:
                room_id = st.session_state.my_live_room
                r_data = s_db["rooms"].get(room_id)
                if r_data:
                    St.success(f"🎲 رقم الغرفة المعتمد للأبناء: **{room_id}**")
                    # [تعديل]: إظهار من جاوب على السؤال حياً باللوحة للمدير
                    St.markdown("#### 👥 حالة إجابات المتسابقين الحين:")
                    for pl in r_data["players"]:
                        status_msg = "✅ تمت الإجابة الكفو" if pl in r_data["answered_players"] else "⏳ يفكر بالحساب..."
                        St.write(f"- **{pl}**: {status_msg}")
                    
                    if r_data["status"] == "waiting":
                        if st.button("🚀 إطلاق المسابقة الحية"): s_db["rooms"][room_id]["status"] = "playing"; s_db["rooms"][room_id]["q_start_time"] = time.time(); s_db["rooms"][room_id]["answered_players"] = []; st.rerun()
                    elif r_data["status"] == "playing":
                        qi = r_data["current_q_idx"]; ql = r_data["questions"]
                        if qi < len(ql):
                            St.write(f"❓ السؤال ({qi+1}/{len(ql)}): **{ql[qi]['السؤال']}**")
                            St.success(f"💡 الجواب الصحيح بالإكسيل هو: {ql[qi].get('الخيار 1 - الصحيح')}")
                            
                            elapsed = time.time() - r_data["q_start_time"]
                            remaining = max(0, int(r_data["duration"] - elapsed))
                            St.warning(f"⏳ العداد التنازلي الآلي النشط: {remaining} ثانية متبقية.")
                            
                            # الانتقال الآلي عند انتهاء الوقت بغض النظر عن الموجه
                            if remaining <= 0:
                                s_db["rooms"][room_id]["current_q_idx"] += 1
                                s_db["rooms"][room_id]["q_start_time"] = time.time()
                                s_db["rooms"][room_id]["answered_players"] = []
                                St.rerun()
                            if st.button("➡️ السؤال التالي يدوياً"):
                                s_db["rooms"][room_id]["current_q_idx"] += 1
                                s_db["rooms"][room_id]["q_start_time"] = time.time()
                                s_db["rooms"][room_id]["answered_players"] = []
                                St.rerun()
                            time.sleep(1); st.rerun()
                        else: s_db["rooms"][room_id]["status"] = "finished"; st.rerun()
                    elif r_data["status"] == "finished":
                        St.markdown("<div class='leaderboard-box'>🏆 لوحة الصدارة والأداء النهائية 🏆</div>", unsafe_allow_html=True)
                        sorted_sc = sorted(r_data["scores"].items(), key=lambda x: x[1], reverse=True)
                        # [تعديل]: عرض التشارت والرسم البياني الفخم النهائي لمالك التطبيق
                        df_c = pd.DataFrame(sorted_sc, columns=["المتسابق", "النقاط"])
                        St.bar_chart(df_c, x="المتسابق", y="النقاط")
                        for rank, (p, s) in enumerate(sorted_sc): St.write(f"🏅 المركز {rank+1}: **{p}** بـ {s} نقطة")
                    
                    if st.button("🛑 إنهاء وتدمير الغرفة"):
                        if room_id in s_db["rooms"]: del s_db["rooms"][room_id]
                        del st.session_state.my_live_room; st.session_state.generated_room_code = None; st.rerun()
                        
        with col_inbox_side:
            St.markdown("### 📬 صندوق الوارد (رسائل الزوار)")
            messages_list = load_local_data("messages.json", [])
            for msg in reversed(messages_list): st.markdown(f"<div class='message-box'><strong>👤 {msg['name']}:</strong><p>{msg['message']}</p></div>", unsafe_allow_html=True)

# نمط المتسابقين (الأبناء) مع التحديث الآلي وتثقيف الأطفال
elif st.session_state.curr_page == "player_mode":
    St.header("🕹️ شاشة انضمام المتسابقين الأبطال")
    if st.button("↩️ العودة للرئيسية"):
        if 'joined_live_room' in st.session_state:
            rj = st.session_state.joined_live_room; nj = st.session_state.my_joined_name
            if rj in s_db["rooms"] and nj in s_db["rooms"][rj]["players"]: s_db["rooms"][rj]["players"].remove(nj)
            del st.session_state.joined_live_room
        st.session_state.curr_page = "home"; st.rerun()
        
    if 'joined_live_room' not in st.session_state:
        c_code = st.text_input("أدخل رقم الغرفة:")
        c_name = st.text_input("أدخل اسمك الكريم:")
        if st.button("🚪 انضمام للتحدي"):
            if c_code in s_db["rooms"]:
                s_db["rooms"][c_code]["players"].append(c_name)
                s_db["rooms"][c_code]["scores"][c_name] = 0
                st.session_state.joined_live_room = c_code
                st.session_state.my_joined_name = c_name; st.rerun()
            else: st.error("الغرفة غير موجودة حالياً.")
    else:
        room_id = st.session_state.joined_live_room; p_name = st.session_state.my_joined_name
        r_data = s_db["rooms"].get(room_id)
        if r_data:
            col_pl, col_pchat = st.columns([2, 1])
            with col_pl:
                if r_data["status"] == "waiting": St.info("👋 متصل بنجاح! انتظر إطلاق التحدي والمسابقة من الموجه...")
                elif r_data["status"] == "playing":
                    qi = r_data["current_q_idx"]; ql = r_data["questions"]
                    if qi < len(ql):
                        St.markdown(f"<h3>❓ السؤال {qi+1}</h3>", unsafe_allow_html=True)
                        St.markdown(f"<h2>{ql[qi]['السؤال']}</h2>", unsafe_allow_html=True)
                        
                        correct_ans = str(ql[qi].get("الخيار 1 - الصحيح", ""))
                        if f"shuffled_opts_{qi}" not in st.session_state:
                            opts = [correct_ans, str(ql[qi].get("الخيار 2", "")), str(ql[qi].get("الخيار 3", "")), str(ql[qi].get("الخيار 4", ""))]
                            random.shuffle(opts); st.session_state[f"shuffled_opts_{qi}"] = opts
                        
                        sel = st.radio("اختر جوابك الصحيح الفخم:", st.session_state[f"shuffled_opts_{qi}"], key=f"p_sel_{qi}")
                        
                        elapsed = time.time() - r_data["q_start_time"]
                        remaining = max(0, int(r_data["duration"] - elapsed))
                        St.warning(f"⏳ متبقي عندك للتفكير والحل: {remaining} ثانية!")
                        
                        # [تعديل]: إشعار الطفل بالخطأ وتثقيفه فور انتهاء الوقت دايركت تلقائياً
                        if remaining <= 0:
                            St.error("❌ انتهى وقت السؤال المخصص ولم تقم بالإجابة في الوقت المحدد!")
                            St.info(f"💡 المعلومة التثقيفية الصحيحة هي: **{correct_ans}**")
                            time.sleep(3); st.rerun()
                            
                        if st.button("✔️ اعتماد الجواب النهائي"):
                            if p_name not in s_db["rooms"][room_id]["answered_players"]: s_db["rooms"][room_id]["answered_players"].append(p_name)
                            if sel == correct_ans: st.balloons(); st.success("إجابة كفو وصحيحة بطل! 🥳") ; s_db["rooms"][room_id]["scores"][p_name] += 10
                            else: 
                                St.error("❌ للأسف الإجابة خاطئة!")
                                St.info(f"💡 معلومة لتثقيفك: الإجابة الصحيحة هي **{correct_ans}**")
                        time.sleep(1); st.rerun()
                    else: St.success("🏁 انتهت الأسئلة بانتظار إعلان النتائج من المدير...")
                elif r_data["status"] == "finished":
                    St.markdown("<div class='leaderboard-box'>🏆 لوحة صدارة الأبطال الختامية 🏆</div>", unsafe_allow_html=True)
                    for k, v in sorted(r_data["scores"].items(), key=lambda x: x[1], reverse=True): St.write(f"### 🎖️ البطل {k}: حصد {v} نقطة")
            with col_pchat: show_live_chat(room_id, p_name, is_admin=False)

# 🕹️ نمط تحدي اختبر نفسك الفردي (تعطيل الكبار تلقائياً لحين رفع ملفهم)
elif st.session_state.curr_page == "culture_mode":
    St.markdown("### 🧠 نمط اختبر نفسك وثقف ذاتك (الفردي)")
    if st.button("↩️ العودة للرئيسية"): st.session_state.individual_challenge = {"status": "idle", "current_q": 0, "correct_ans": 0, "q_list": []}; st.session_state.curr_page = "home"; st.rerun()
    St.write("---")
    
    c_status = st.session_state.individual_challenge["status"]
    if c_status == "idle":
        q_choice = st.radio("اختر القسم الثقافي للتحدي:", ["قسم الأطفال 👶", "قسم الكبار 🧔 (غير مفعل الحين)"])
        # [تعديل]: تفعيل الدياكتيفيت وقفل قسم الكبار تلقائياً لحين رفع ملفهم بالسيرفر
        if "الكبار" in q_choice and not s_db["adults_q"]:
            St.error("⚠️ هذا القسم غير مفعل حالياً (Deactivated) لعدم توفر الأسئلة بالكواليس. يرجى الطلب من المطور رفع إكسيل الكبار لوحة الموجه أولاً.")
        else:
            if st.button("✨ ابدأ التحدي الفردي الحين"):
                pool = s_db["kids_q"] if "الأطفال" in q_choice else s_db["adults_q"]
                st.session_state.individual_challenge["q_list"] = random.sample(pool, min(len(pool), 10))
                st.session_state.individual_challenge["status"] = "playing"; st.session_state.individual_challenge["current_q"] = 0; st.session_state.individual_challenge["correct_ans"] = 0; st.rerun()
    elif c_status == "playing":
        qc = st.session_state.individual_challenge["current_q"]; qlc = st.session_state.individual_challenge["q_list"]
        if qc < len(qlc):
            St.write(f"❓ السؤال ({qc+1}/{len(qlc)}): **{qlc[qc]['السؤال']}**")
            c_ans = str(qlc[qc].get("الخيار 1 - الصحيح", ""))
            opts = [c_ans, str(qlc[qc].get("الخيار 2", "")), str(qlc[qc].get("الخيار 3", "")), str(qlc[qc].get("الخيار 4", ""))]
            sel = st.radio("اختر الجواب الصحيح:", opts, key=f"solo_q_{qc}")
            if st.button("✔️ اعتماد الإجابة"):
                if sel == c_ans: st.session_state.individual_challenge["correct_ans"] += 1; st.success("صح كفو! ✅")
                else: st.error(f"خطأ! ❌ الصح هو: {c_ans}")
                st.session_state.individual_challenge["current_q"] += 1; st.rerun()
        else: st.session_state.individual_challenge["status"] = "finished"; st.rerun()
    elif c_status == "finished":
        St.success(f"🏆 النتيجة النهائية: لقد أجبت بشكل صحيح على {st.session_state.individual_challenge['correct_ans']} من أصل {len(st.session_state.individual_challenge['q_list'])} سؤال!")
        if st.button("🔄 إعادة التحدي من جديد"): st.session_state.individual_challenge = {"status": "idle", "current_q": 0, "correct_ans": 0, "q_list": []}; st.rerun()

# طور المجموعات الجديد
elif st.session_state.curr_page == "group_mode":
    St.markdown("### 👥 طور المجموعات والفرق المشتركة")
    St.info("🚧 هذا الطور قيد التأسيس البرمجي الهندسي وسيتم ربطه وتفعيله بالخطوة القادمة مباشرة...")
    if st.button("↩️ العودة للرئيسية"): st.session_state.curr_page = "home"; st.rerun()

# 5. تذييل حقوق الملكية الثابتة للمطور عبد الإله العنزي باللغتين
st.markdown("<div class='footer-text'>تطوير عبد الإله العنزي | Developed by Abdulelah Al-Anzi</div>", unsafe_allow_html=True)
