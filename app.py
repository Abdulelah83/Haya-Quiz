import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime

# 1. إعدادات الصفحة والهوية البصرية الفخمة والألوان الجذابة
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz Pro", 
    page_icon="🎮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص CSS للمظهر الفخم
st.markdown("""
    <style>
    .main-title { text-align: center; color: #4F46E5; font-size: 2.8rem; font-weight: bold; margin-bottom: 5px; }
    .stRadio > div { flex-direction: row; justify-content: center; gap: 15px; }
    div.stButton > button:first-child { 
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); 
        color: white; border-radius: 12px; border: none; font-size: 1.1rem; padding: 10px 20px;
    }
    .chat-container { background-color: #E5DDD5; padding: 15px; border-radius: 12px; max-height: 350px; overflow-y: auto; display: flex; flex-direction: column; }
    .msg-box-admin { background-color: #DCF8C6; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: right; align-self: flex-end; max-width: 80%; }
    .msg-box-player { background-color: #FFFFFF; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: right; align-self: flex-start; max-width: 80%; }
    .message-box { background-color: #F3F4F6; border-right: 5px solid #4F46E5; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-size: 0.9rem; }
    .leaderboard-box { background: linear-gradient(135deg, #6EE7B7 0%, #3B82F6 100%); padding: 20px; border-radius: 12px; color: white; text-align: center; font-weight: bold; font-size: 1.5rem; }
    .footer-text { text-align: center; color: #9CA3AF; font-size: 1rem; font-weight: 500; padding: 20px 0; border-top: 1px solid #E5E7EB; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# 2. الذاكرة الدائمة المحصنة في السيرفر لحفظ الأسئلة والرسائل والزوار للضيوف دائماً
@st.cache_resource
def get_server_db():
    default_q = [
        {"السؤال": "ما الكوكب الأقرب إلى الشمس؟", "الخيار 1 - الصحيح": "عطارد", "الخيار 2": "الزهرة", "الخيار 3": "الأرض", "الخيار 4": "المريخ"},
        {"السؤال": "ما اسم القوة التي تجذب الأشياء نحو الأرض؟", "الخيار 1 - الصحيح": "الجاذبية", "الخيار 2": "الإحتكاك", "الخيار 3": "المغناطيسية", "الخيار 4": "الدفع"}
    ]
    return {"rooms": {}, "kids_q": default_q, "adults_q": [], "manual_q": [], "messages": [], "total_visitors": 0, "visitor_history": {}}

db = get_global_db() if 'get_global_db' in globals() else get_server_db()

# عداد الزوار الذكي
if 'counted' not in st.session_state:
    db["total_visitors"] += 1
    today = datetime.now().strftime("%Y-%m-%d")
    db["visitor_history"][today] = db["visitor_history"].get(today, 0) + 1
    st.session_state.counted = True

# تهيئة الجلسة
if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"
if 'generated_room_code' not in st.session_state: st.session_state.generated_room_code = None

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
        c_text = col_c1.text_input("اكتب رسالة:", label_visibility="collapsed", key=f"in_{room_id}")
        if col_c2.form_submit_button("إرسال"):
            if c_text:
                db["rooms"][room_id]["chat_history"].append({"user_type": "admin" if is_admin else "player", "name": "المدير (أبو صالح)" if is_admin else user_name, "text": c_text})
                st.rerun()
    time.sleep(2); st.rerun()

# الشريط العلوي للتنقل
navbar_cols = st.columns([1, 4, 1])
with navbar_cols[1]:
    col_nav1, col_nav2 = st.columns(2)
    if col_nav1.button("🏠 الرئيسية", use_container_width=True): st.session_state.curr_page = "home"; st.rerun()
    if col_nav2.button("📞 تواصل معنا", use_container_width=True): st.session_state.curr_page = "contact_mode"; st.rerun()

st.write("---")

# 📥 خانة المالك (لوحة المطور) مستقلة ومؤمنة بالكامل على اليسار (القائمة الجانبية Sidebar)
with st.sidebar:
    st.markdown("### ⚙️ لوحة المالك (أدمن)")
    admin_pass = st.text_input("أدخل الرقم السري للمالك:", type="password")
    
    if admin_pass == "Abdulelah@2026":
        st.success("🔓 مرحباً أبا عبد الإله")
        
        # إحصائيات الزوار والتشارت
        st.metric(label="📊 عدد زوار الموقع الكلي", value=f"{db['total_visitors']} زائر")
        if db["visitor_history"]:
            df_v = pd.DataFrame(list(db["visitor_history"].items()), columns=["التاريخ", "الزيارات"])
            st.line_chart(df_v.set_index("التاريخ"), height=150)
            
        st.write("---")
        # رفع الأسئلة لتبقى محفوظة دائماً للضيوف
        st.markdown("📂 **تحميل الأسئلة الدائمة**")
        k_file = st.file_uploader("إكسيل الأطفال:", type=["xlsx"], key="side_k")
        if k_file: db["kids_q"] = pd.read_excel(k_file).to_dict(orient='records'); st.success("تم الحفظ!")
        
        a_file = st.file_uploader("إكسيل الكبار:", type=["xlsx"], key="side_a")
        if a_file: db["adults_q"] = pd.read_excel(a_file).to_dict(orient='records'); st.success("تم الحفظ!")
        
        st.write("---")
        # إضافة سؤال يدوي
        st.markdown("📝 **إضافة سؤال يدوي**")
        with st.form("side_manual_form", clear_on_submit=True):
            mq = st.text_input("السؤال:")
            o1 = st.text_input("خيار 1 (الصحيح):")
            o2 = st.text_input("خيار 2:")
            o3 = st.text_input("خيار 3:")
            o4 = st.text_input("خيار 4:")
            if st.form_submit_button("حفظ السؤال اليدوي"):
                if mq and o1: db["manual_q"].append({"السؤال": mq, "الخيار 1 - الصحيح": o1, "الخيار 2": o2, "الخيار 3": o3, "الخيار 4": o4}); st.success("تم الإدراج!")
                
        st.write("---")
        # صندوق الوارد يسار الصفحة
        st.markdown("📬 **صندوق وارد الرسائل**")
        if not db["messages"]: st.info("الصندوق فارغ.")
        for msg in reversed(db["messages"]):
            st.markdown(f"<div class='message-box'><strong>👤 {msg['name']}:</strong><br>{msg['msg']}</div>", unsafe_allow_html=True)

# الصفحة الرئيسية
if st.session_state.curr_page == "home":
    st.markdown("<h2 style='text-align:center; color:#4F46E5;'>منصة مسابقات هيا العائلية 🎯</h2>", unsafe_allow_html=True)
    col_l_img, col_r_btn = st.columns([1, 2])
    with col_l_img:
        st.image("my_kids.png", use_container_width=True) if os.path.exists("my_kids.png") else st.info("🎮 تحدي المسابقات الحية")
    with col_r_btn:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🏆 إدارة مسابقة حية", use_container_width=True): st.session_state.curr_page = "admin_mode"; st.rerun()
        with col_b2:
            if st.button("🎮 دخول كمتسابق", use_container_width=True): st.session_state.curr_page = "player_mode"; st.rerun()
        st.write("---")
        col_b3, col_b4 = st.columns(2)
        with col_b3:
            if st.button("🕹️ تحدي اختبر نفسك", use_container_width=True): st.session_state.curr_page = "culture_mode"; st.rerun()
        with col_b4:
            st.info("👥 طور المجموعات قيد التأسيس")

# تواصل معنا
elif st.session_state.curr_page == "contact_mode":
    st.markdown("### 📞 تواصل معنا")
    with st.form("contact"):
        name = st.text_input("الاسم:")
        msg_txt = st.text_area("الرسالة:")
        if st.form_submit_button("📤 إرسال"):
            if name and msg_txt: db["messages"].append({"name": name, "msg": msg_txt}); st.success("تم الإرسال لمالك الموقع!")

# إدارة مسابقة حية (المدير في المنتصف)
elif st.session_state.curr_page == "admin_mode":
    st.markdown("<h2 style='text-align:center;'>🏆 إدارة المسابقة الحية</h2>", unsafe_allow_html=True)
    if 'my_live_room' not in st.session_state:
        q_src = st.radio("اختر الفئة للجولة:", ["أسئلة الأطفال", "أسئلة الكبار"])
        num_q = st.number_input("عدد الأسئلة:", min_value=1, value=5)
        t_val = st.slider("الوقت لكل سؤال (ثواني):", 5, 60, 12)
        
        if st.button("🎲 توليد غرفة المسابقة"):
            pool = db["kids_q"] if "الأطفال" in q_src else db["adults_q"]
            final_pool = db["manual_q"] + pool
            if not final_pool: st.error("بنك الأسئلة فارغ! ارفع ملفاً من لوحة المالك على اليسار أولاً.")
            else:
                if not st.session_state.generated_room_code: st.session_state.generated_room_code = str(random.randint(1000, 9999))
                rcode = st.session_state.generated_room_code; st.session_state.my_live_room = rcode
                chosen = final_pool[:len(db["manual_q"])] + random.sample(pool, min(len(pool), max(1, int(num_q) - len(db["manual_q"]))))
                db["rooms"][rcode] = {"players": [], "status": "waiting", "current_q_idx": 0, "questions": chosen, "chat_history": [], "duration": t_val, "scores": {}, "q_start_time": time.time(), "answered_players": []}
                st.rerun()
    else:
        rid = st.session_state.my_live_room; rdata = db["rooms"].get(rid)
        if rdata:
            st.success(f"🎲 رقم الغرفة المعتمد للأبناء: **{rid}**")
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.markdown("#### 👥 حالة إجابات المتسابقين:")
                for pl in rdata["players"]:
                    st.write(f"- **{pl}**: {'✅ تمت الإجابة' if pl in rdata['answered_players'] else '⏳ يفكر...'}")
                st.write("---")
                if rdata["status"] == "waiting":
                    if st.button("🚀 بدء المسابقة"): db["rooms"][rid]["status"] = "playing"; db["rooms"][rid]["q_start_time"] = time.time(); db["rooms"][rid]["answered_players"] = []; st.rerun()
                elif rdata["status"] == "playing":
                    qi = rdata["current_q_idx"]; ql = rdata["questions"]
                    if qi < len(ql):
                        st.write(f"❓ السؤال ({qi+1}/{len(ql)}): **{ql[qi]['السؤال']}**")
                        c_ans = str(ql[qi].get("الخيار 1 - الصحيح", ""))
                        st.success(f"💡 الجواب الصحيح بالإكسيل هو: {c_ans}")
                        
                        rem = max(0, int(rdata["duration"] - (time.time() - rdata["q_start_time"])))
                        st.warning(f"⏳ متبقي: {rem} ثانية.")
                        if rem <= 0:
                            db["rooms"][rid]["current_q_idx"] += 1; db["rooms"][rid]["q_start_time"] = time.time(); db["rooms"][rid]["answered_players"] = []; st.rerun()
                        if st.button("➡️ السؤال التالي"):
                            db["rooms"][rid]["current_q_idx"] += 1; db["rooms"][rid]["q_start_time"] = time.time(); db["rooms"][rid]["answered_players"] = []; st.rerun()
                        time.sleep(1); st.rerun()
                    else: db["rooms"][rid]["status"] = "finished"; st.rerun()
                elif rdata["status"] == "finished":
                    st.markdown("<div class='leaderboard-box'>🏆 لوحة الصدارة النهائية (Dashboard) 🏆</div>", unsafe_allow_html=True)
                    sorted_sc = sorted(rdata["scores"].items(), key=lambda x: x[1], reverse=True)
                    df_chart = pd.DataFrame(sorted_sc, columns=["المتسابق", "النقاط"])
                    st.bar_chart(df_chart, x="المتسابق", y="النقاط")
                if st.button("🛑 تدمير الغرفة"):
                    if rid in db["rooms"]: del db["rooms"][rid]
                    del st.session_state.my_live_room; st.session_state.generated_room_code = None; st.rerun()
            with col_r: show_live_chat(rid, "المدير", is_admin=True)

# دخول كمتسابق (الأبناء)
elif st.session_state.curr_page == "player_mode":
    st.header("🕹️ شاشة المتسابقين")
    if 'joined_live_room' not in st.session_state:
        cc = st.text_input("أدخل رقم الغرفة:")
        cn = st.text_input("اسمك الكريم:")
        if st.button("🚪 دخول"):
            if cc in db["rooms"]: db["rooms"][cc]["players"].append(cn); db["rooms"][cc]["scores"][cn] = 0; st.session_state.joined_live_room = cc; st.session_state.my_joined_name = cn; st.rerun()
            else: st.error("الغرفة غير موجودة.")
    else:
        rid = st.session_state.joined_live_room; pname = st.session_state.my_joined_name; rdata = db["rooms"].get(rid)
        if rdata:
            col_l, col_r = st.columns([2, 1])
            with col_l:
                if rdata["status"] == "waiting": st.info("⏳ بانتظار إطلاق التحدي من الموجه...")
                elif rdata["status"] == "playing":
                    qi = rdata["current_q_idx"]; ql = rdata["questions"]
                    if qi < len(ql):
                        st.write(f"### السؤال {qi+1}: {ql[qi]['السؤال']}")
                        c_ans = str(ql[qi].get("الخيار 1 - الصحيح", ""))
                        if f"sh_opts_{qi}" not in st.session_state:
                            opts = [c_ans, str(ql[qi].get("الخيار 2", "")), str(ql[qi].get("الخيار 3", "")), str(ql[qi].get("الخيار 4", ""))]
                            random.shuffle(opts); st.session_state[f"sh_opts_{qi}"] = opts
                        sel = st.radio("اختر الجواب الصحيح:", st.session_state[f"sh_opts_{qi}"], key=f"p_s_{qi}")
                        
                        rem = max(0, int(rdata["duration"] - (time.time() - rdata["q_start_time"])))
                        st.warning(f"⏳ متبقي عندك: {rem} ثانية!")
                        if rem <= 0:
                            st.error("❌ انتهى الوقت المخصص للحل!")
                            st.info(f"💡 المعلومة الصحيحة لتثقيفك هي: **{c_ans}**")
                            time.sleep(3); st.rerun()
                        if st.button("✔️ اعتماد الإجابة"):
                            if pname not in db["rooms"][rid]["answered_players"]: db["rooms"][rid]["answered_players"].append(pname)
                            if sel == c_ans: st.balloons(); st.success("صح بطل! 🥳"); db["rooms"][rid]["scores"][pname] += 10
                            else: st.error("❌ خطأ!"); st.info(f"💡 معلومة لتثقيفك: الصح هو **{c_ans}**")
                        time.sleep(1); st.rerun()
                    else: st.success("🏁 انتهت الأسئلة بانتظار إعلان لوحة الصدارة...")
                elif rdata["status"] == "finished":
                    st.markdown("<div class='leaderboard-box'>🏆 النتيجة الختامية للأبطال 🏆</div>", unsafe_allow_html=True)
                    for k, v in sorted(rdata["scores"].items(), key=lambda x: x[1], reverse=True): st.write(f"### البطل {k}: {v} نقطة")
            with col_r: show_live_chat(rid, pname, is_admin=False)

# نمط اختبر نفسك (تعطيل الكبار تلقائياً)
elif st.session_state.curr_page == "culture_mode":
    st.markdown("### 🧠 نمط اختبر نفسك الفردي")
    if st.button("↩️ العودة"): st.session_state.individual_challenge = {"status": "idle", "current_q": 0, "correct_ans": 0, "q_list": []}; st.session_state.curr_page = "home"; st.rerun()
    c_status = st.session_state.individual_challenge["status"]
    if c_status == "idle":
        q_choice = st.radio("اختر القسم:", ["قسم الأطفال 👶", "قسم الكبار 🧔 (غير مفعل الحين)"])
        if "الكبار" in q_choice and not db["adults_q"]: st.error("⚠️ هذا القسم غير مفعل حالياً (Deactivated) لعدم توفر الأسئلة بالكواليس.")
        else:
            if st.button("✨ ابدأ"):
                pool = db["kids_q"] if "الأطفال" in q_choice else db["adults_q"]
                st.session_state.individual_challenge["q_list"] = random.sample(pool, min(len(pool), 10))
                st.session_state.individual_challenge["status"] = "playing"; st.session_state.individual_challenge["current_q"] = 0; st.session_state.individual_challenge["correct_ans"] = 0; st.rerun()
    elif c_status == "playing":
        qc = st.session_state.individual_challenge["current_q"]; qlc = st.session_state.individual_challenge["q_list"]
        if qc < len(qlc):
            st.write(f"❓ السؤال ({qc+1}/{len(qlc)}): **{qlc[qc]['السؤال']}**")
            c_ans = str(qlc[qc].get("الخيار 1 - الصحيح", ""))
            opts = [c_ans, str(qlc[qc].get("الخيار 2", "")), str(qlc[qc].get("الخيار 3", "")), str(qlc[qc].get("الخيار 4", ""))]
            sel = st.radio("الخيارات:", opts, key=f"s_q_{qc}")
            if st.button("✔️ اعتماد"):
                if sel == c_ans: st.session_state.individual_challenge["correct_ans"] += 1; st.success("صح ✅")
                else: st.error(f"خطأ! الصح: {c_ans}")
                st.session_state.individual_challenge["current_q"] += 1; st.rerun()
        else: st.session_state.individual_challenge["status"] = "finished"; st.rerun()
    elif c_status == "finished":
        st.success(f"🏆 النتيجة: إجاباتك الصحيحة {st.session_state.individual_challenge['correct_ans']} من أصل {len(st.session_state.individual_challenge['q_list'])}")

# 5. التوقيع الثابت بالكامل أسفل الشاشة
st.markdown("<div class='footer-text'>تطوير عبد الإله العنزي | Developed by Abdulelah Al-Anzi</div>", unsafe_allow_html=True)
