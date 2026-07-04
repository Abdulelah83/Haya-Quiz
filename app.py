import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime

# 1. إعدادات الصفحة والهوية البصرية
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz Pro", 
    page_icon="🎮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص CSS
st.markdown("""
    <style>
    .main-title { text-align: center; color: #4F46E5; font-size: 2.8rem; font-weight: bold; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #4B5563; font-size: 1.2rem; margin-bottom: 25px; }
    .stRadio > div { flex-direction: row; justify-content: center; }
    div.stButton > button:first-child { background-color: #4F46E5; color: white; border-radius: 8px; border: none; font-size: 1rem; }
    div.stButton > button:first-child:hover { background-color: #4338CA; }
    .chat-container { background-color: #E5DDD5; padding: 15px; border-radius: 12px; max-height: 350px; overflow-y: auto; display: flex; flex-direction: column; }
    .msg-box-admin { background-color: #DCF8C6; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: right; align-self: flex-end; max-width: 80%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .msg-box-player { background-color: #FFFFFF; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: right; align-self: flex-start; max-width: 80%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .msg-user { font-weight: bold; font-size: 0.85rem; color: #075E54; display: block; margin-bottom: 3px; }
    .msg-time { font-size: 0.7rem; color: #999; text-align: left; display: block; margin-top: 3px; }
    .leaderboard-box { background: linear-gradient(135deg, #6EE7B7 0%, #3B82F6 100%); padding: 20px; border-radius: 12px; color: white; text-align: center; font-weight: bold; font-size: 1.5rem; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# الذاكرة المحصنة
@st.cache_resource
def get_global_db():
    return {"rooms": {}, "kids_q": [], "adults_q": [], "manual_q": []}

db = get_global_db()

if 'individual_challenge' not in st.session_state:
    st.session_state.individual_challenge = {"status": "idle", "current_q": 0, "correct_ans": 0, "q_list": []}

if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"
if 'generated_room_code' not in st.session_state: st.session_state.generated_room_code = None

@st.fragment
def show_live_chat(room_id, user_name, is_admin):
    room_ref = db["rooms"].get(room_id)
    if not room_ref: return
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for chat_msg in room_ref["chat_history"]:
        msg_class = "msg-box-admin" if chat_msg["user_type"] == "admin" else "msg-box-player"
        st.markdown(f"<div class='{msg_class}'><span class='msg-user'>{chat_msg['name']}</span>{chat_msg['text']}<span class='msg-time'>{chat_msg['time']}</span></div>", unsafe_allow_html=True)
    st.markdown("</div><br>", unsafe_allow_html=True)
    
    with st.form(f"chat_form_{room_id}", clear_on_submit=True):
        col_c1, col_c2 = st.columns([4, 1])
        c_text = col_c1.text_input("اكتب رسالة فورية:", label_visibility="collapsed", key=f"input_{room_id}")
        if col_c2.form_submit_button("إرسال"):
            if c_text:
                curr_t = datetime.now().strftime("%H:%M")
                db["rooms"][room_id]["chat_history"].append({"user_type": "admin" if is_admin else "player", "name": "المدير (أبو صالح)" if is_admin else user_name, "text": c_text, "time": curr_t})
                st.rerun()
    time.sleep(2)
    st.rerun()

# الشريط العلوي الثابت
navbar_cols = st.columns([1, 4, 1])
with navbar_cols[1]:
    col_nav1, col_nav2 = st.columns(2)
    if col_nav1.button("🏠 الرئيسية", use_container_width=True): st.session_state.curr_page = "home"; st.rerun()
    if col_nav2.button("📞 تواصل معنا", use_container_width=True): st.session_state.curr_page = "contact_mode"; st.rerun()

st.write("---")

# القائمة الجانبية (Sidebar)
with st.sidebar:
    st.markdown("### 🌐 الإعدادات")
    main_ui_lang = st.selectbox("اختر لغة الموقع:", ["SA العربية", "US English"])
    st.write("---")
    st.markdown("### ⚙️ لوحة المطور (أدمن)")
    admin_input_pass = st.text_input("أدخل الرقم السري للمطور فتح بنك الأسئلة:", type="password")
    
    if admin_input_pass == "1234":
        st.success("🔓 وضع المطور نشط")
        tab_b1, tab_b2, tab_b3 = st.tabs(["أسئلة الأطفال", "أسئلة الكبار", "📝 سؤال يدوي"])
        
        with tab_b1:
            kids_f_in = st.file_uploader("رفع إكسيل الأطفال:", type=["xlsx"], key="main_k")
            if kids_f_in:
                try:
                    db["kids_q"] = pd.read_excel(kids_f_in).to_dict(orient='records')
                    st.success(f"✅ اعتُمدت ({len(db['kids_q'])} سؤال)")
                except: st.error("خطأ في بنية الملف.")
        
        with tab_b2:
            adults_f_in = st.file_uploader("رفع إكسيل الكبار:", type=["xlsx"], key="main_a")
            if adults_f_in:
                try:
                    db["adults_q"] = pd.read_excel(adults_f_in).to_dict(orient='records')
                    st.success(f"✅ اعتُمدت ({len(db['adults_q'])} سؤال)")
                except: st.error("خطأ في بنية الملف.")
        
        with tab_b3:
            # [تعديل]: كتابة سؤال يدوي تفاعلي صحيح يظهر ضمن الأسئلة بالكامل
            with st.form("main_manual_form"):
                mt = st.text_input("نص السؤال اليدوي:")
                o1 = st.text_input("الخيار 1 (الصحيح طرداً):")
                o2 = st.text_input("الخيار 2:")
                o3 = st.text_input("الخيار 3:")
                o4 = st.text_input("الخيار 4:")
                if st.form_submit_button("➕ حفظ وإدراج السؤال اليدوي"):
                    if mt and o1:
                        db["manual_q"].append({"السؤال": mt, "الخيار 1 - الصحيح": o1, "الخيار 2": o2, "الخيار 3": o3, "الخيار 4": o4})
                        st.success("🎯 تم حفظ السؤال اليدوي ونشره بنجاح!")

# الصفحة الرئيسية
if st.session_state.curr_page == "home":
    col_left_img, col_right_content = st.columns([1, 2])
    with col_left_img: st.image("my_kids.png", use_container_width=True)
    with col_right_content:
        st.markdown("<h2 style='color: #4F46E5;'>منصة مسابقات هيا العائلية 🎯</h2>", unsafe_allow_html=True)
        st.write("---")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            if st.button("🏆 أنشئ مسابقة الآن", use_container_width=True): st.session_state.curr_page = "admin_mode"; st.rerun()
        with col_m2:
            if st.button("🎮 انضم كمتسابق", use_container_width=True): st.session_state.curr_page = "player_mode"; st.rerun()
        with col_m3:
            if st.button("🕹️ ابدأ اللعب الفردي", use_container_width=True): st.session_state.curr_page = "culture_mode"; st.rerun()

# إدارة مسابقة حية (المدير)
elif st.session_state.curr_page == "admin_mode":
    st.markdown("<h2 style='text-align:center;'>👑 لوحة تحكم الموجه</h2>", unsafe_allow_html=True)
    if st.button("↩️ العودة للرئيسية"): st.session_state.curr_page = "home"; st.rerun()
    st.write("---")
    
    if 'my_live_room' not in st.session_state:
        col_setup1, col_setup2 = st.columns(2)
        with col_setup1:
            q_src_v2 = st.radio("الفئة المستهدفة للعب:", ["أسئلة الأطفال", "أسئلة الكبار"])
            num_limit_v2 = st.number_input("عدد أسئلة الجولة:", min_value=1, max_value=100, value=10)
            max_players_v2 = st.number_input("عدد المتسابقين الحاضرين:", min_value=1, max_value=20, value=5)
        with col_setup2:
            timer_q_val = st.slider("الوقت المتاح لكل سؤال (بالثواني):", 5, 120, 12)
            
        if st.button("🎲 توليد الغرفة"):
            pool_in = db["kids_q"] if "الأطفال" in q_src_v2 else db["adults_q"]
            
            # [تعديل]: دمج السؤال اليدوي ليكون أول الأسئلة دائماً إذا وُجد
            final_pool = db["manual_q"] + pool_in
            
            if not final_pool:
                st.error("⚠️ بنك الأسئلة فارغ! يرجى رفع ملف إكسيل أو كتابة سؤال يدوي أولاً.")
            else:
                if not st.session_state.generated_room_code:
                    st.session_state.generated_room_code = str(random.randint(1000, 9999))
                current_code = st.session_state.generated_room_code
                st.session_state.my_live_room = current_code
                
                # اختيار وتنوع الأسئلة عشوائياً من الإكسيل
                chosen_q = final_pool[:len(db["manual_q"])] + random.sample(pool_in, min(len(pool_in), max(1, int(num_limit_v2) - len(db["manual_q"]))))
                
                db["rooms"][current_code] = {
                    "players": [], "max_players": max_players_v2, "status": "waiting", "current_q_idx": 0,
                    "questions": chosen_q, "chat_history": [], "duration": timer_q_val, "scores": {},
                    "q_start_time": time.time(), "answered_players": []
                }
                st.rerun()
    else:
        l_room = st.session_state.my_live_room
        r_data_in = db["rooms"].get(l_room)
        if r_data_in:
            st.success(f"🎲 رقم الغرفة الحية المعتمد للأبناء هو: **{l_room}**")
            col_live, col_chat = st.columns([2, 1])
            with col_live:
                st.markdown("### 👥 المتسابقون المتصلون:")
                if not r_data_in["players"]: st.warning("🔄 بانتظار دخول الأبناء...")
                else:
                    g_cols = st.columns(3)
                    for idi, pl_name in enumerate(r_data_in["players"]):
                        # [تعديل]: إظهار من جاوب على السؤال حياً لتسهيل النقل
                        has_ans = "✅ تمت الإجابة" if pl_name in r_data_in["answered_players"] else "⏳ يفكر..."
                        g_cols[idi % 3].info(f"• {pl_name}: {has_ans}")
                st.write("---")
                
                if r_data_in["status"] == "waiting":
                    if st.button("🚀 بدء المسابقة"):
                        db["rooms"][l_room]["status"] = "playing"
                        db["rooms"][l_room]["q_start_time"] = time.time()
                        db["rooms"][l_room]["answered_players"] = []
                        st.rerun()
                elif r_data_in["status"] == "playing":
                    qi = r_data_in["current_q_idx"]
                    q_list_in = r_data_in["questions"]
                    if qi < len(q_list_in):
                        st.info(f"📊 السؤال الحالي ({qi + 1}/{len(q_list_in)}):")
                        st.markdown(f"### **{q_list_in[qi]['السؤال']}**")
                        
                        correct_ans_str = str(q_list_in[qi].get("الخيار 1 - الصحيح", ""))
                        st.success(f"💡 الإجابة الصحيحة في الإكسيل هي: **{correct_ans_str}**")
                        
                        # حساب العداد التنازلي والانتقال الآلي للكل
                        elapsed = time.time() - r_data_in["q_start_time"]
                        remaining = max(0, int(r_data_in["duration"] - elapsed))
                        st.warning(f"⏱️ العداد التنازلي المزامَن: {remaining} ثانية متبقية.")
                        
                        # [تعديل]: تجاوز الوقت ينتقل دايركت تلقائياً ويعلن خطأ المتأخر
                        if remaining <= 0:
                            db["rooms"][l_room]["current_q_idx"] += 1
                            db["rooms"][l_room]["q_start_time"] = time.time()
                            db["rooms"][l_room]["answered_players"] = []
                            st.rerun()
                        
                        if st.button("➡️ السؤال التالي يدوياً"):
                            db["rooms"][l_room]["current_q_idx"] += 1
                            db["rooms"][l_room]["q_start_time"] = time.time()
                            db["rooms"][l_room]["answered_players"] = []
                            st.rerun()
                        time.sleep(1)
                        st.rerun()
                    else:
                        db["rooms"][l_room]["status"] = "finished"
                        st.rerun()
                        
                elif r_data_in["status"] == "finished":
                    st.markdown("<div class='leaderboard-box'>🏆 لوحة صدارة الأبطال النهائية 🏆</div>", unsafe_allow_html=True)
                    sorted_scores = sorted(r_data_in["scores"].items(), key=lambda x: x[1], reverse=True)
                    
                    # [تعديل]: بناء داشبورد تشارت ورسم بياني مرضي وفخم جداً للأولاد
                    df_chart = pd.DataFrame(sorted_scores, columns=["المتسابق", "النقاط"])
                    st.bar_chart(data=df_chart, x="المتسابق", y="النقاط", color="#4F46E5")
                    
                    for rank, (player, score) in enumerate(sorted_scores):
                        medal = "🥇" if rank == 0 else "🥈" if rank == 1 else "🥉" if rank == 2 else "🎖️"
                        st.write(f"### {medal} المركز {rank+1}: **{player}** حصد **{score}** نقطة!")
                
                if st.button("🛑 إنهاء وتدمير الغرفة"):
                    if l_room in db["rooms"]: del db["rooms"][l_room]
                    del st.session_state.my_live_room
                    st.session_state.generated_room_code = None
                    st.rerun()
            with col_chat: show_live_chat(l_room, "المدير", is_admin=True)

# نمط دخول كمتسابق
elif st.session_state.curr_page == "player_mode":
    st.header("🕹️ شاشة انضمام المتسابقين")
    if st.button("↩️ العودة للرئيسية"):
        if 'joined_live_room' in st.session_state:
            old_r = st.session_state.joined_live_room; old_n = st.session_state.my_joined_name
            if old_r in db["rooms"] and old_n in db["rooms"][old_r]["players"]: db["rooms"][old_r]["players"].remove(old_n)
            del st.session_state.joined_live_room
        st.session_state.curr_page = "home"; st.rerun()
    st.write("---")
    
    if 'joined_live_room' not in st.session_state:
        c_code = st.text_input("أدخل رقم الغرفة المكون من 4 أرقام:")
        c_name = st.text_input("أدخل اسمك الكريم:")
        if st.button("🚪 دخول الغرفة"):
            if c_code in db["rooms"]:
                robj = db["rooms"][c_code]
                if len(robj["players"]) >= robj["max_players"]: st.error("الغرفة ممتلئة!")
                elif c_name in robj["players"]: st.warning("الاسم مسجل بالفعل!")
                else:
                    db["rooms"][c_code]["players"].append(c_name)
                    db["rooms"][c_code]["scores"][c_name] = 0
                    st.session_state.joined_live_room = c_code
                    st.session_state.my_joined_name = c_name
                    st.success("🎉 متصل بالبث الحقيقي!")
                    st.rerun()
            else: st.error("الغرفة غير موجودة.")
    else:
        ar_p = st.session_state.joined_live_room; an_p = st.session_state.my_joined_name
        if ar_p in db["rooms"]:
            r_in = db["rooms"][ar_p]
            col_pg, col_pc = st.columns([2, 1])
            with col_pg:
                if r_in["status"] == "waiting": st.info(f"👋 أهلاً {an_p}! انتظر إطلاق المسابقة من الموجه...")
                elif r_in["status"] == "playing":
                    qi = r_in["current_q_idx"]; ql = r_in["questions"]
                    if qi < len(ql):
                        st.markdown(f"### ❓ السؤال {qi + 1}")
                        st.markdown(f"<h2>{ql[qi]['السؤال']}</h2>", unsafe_allow_html=True)
                        
                        correct_ans = str(ql[qi].get("الخيار 1 - الصحيح", ""))
                        
                        if f"shuffled_opts_{qi}" not in st.session_state:
                            raw_opts = [correct_ans, str(ql[qi].get("الخيار 2", "")), str(ql[qi].get("الخيار 3", "")), str(ql[qi].get("الخيار 4", ""))]
                            random.shuffle(raw_opts)
                            st.session_state[f"shuffled_opts_{qi}"] = raw_opts
                        
                        opts = st.session_state[f"shuffled_opts_{qi}"]
                        sel = st.radio("اختر إجابتك الصحيحة الحين:", opts, key=f"p_opt_{qi}")
                        
                        elapsed = time.time() - r_in["q_start_time"]
                        remaining = max(0, int(r_in["duration"] - elapsed))
                        st.warning(f"⏳ متبقي عندك للتفكير: {remaining} ثانية!")
                        
                        # [تعديل]: رسالة فوارة حتمية للطفل وتثقيفه بالخطأ فور تجاوز الوقت
                        if remaining <= 0:
                            st.error(f"❌ انتهى الوقت المخصص! لقد أخطأت في الحل لعدم الإجابة بالوقت المحدد.")
                            st.info(f"💡 معلومة لتثقيفك: الإجابة الصحيحة هي **{correct_ans}**")
                            time.sleep(2)
                            st.rerun()
                        
                        if st.button("✔️ اعتماد الإجابة"):
                            if an_p not in db["rooms"][ar_p]["answered_players"]:
                                db["rooms"][ar_p]["answered_players"].append(an_p)
                            if sel == correct_ans:
                                db["rooms"][ar_p]["scores"][an_p] += 10
                                st.balloons(); st.success("صح! كفو يا بطل 🥳")
                            else: 
                                st.error(f"💔 إجابة خاطئة للتحدي!")
                                st.info(f"💡 معلومة لتثقيفك: الإجابة الصحيحة هي **{correct_ans}**")
                        time.sleep(1)
                        st.rerun()
                    else: st.success("🏁 انتهت الأسئلة!")
                elif r_in["status"] == "finished":
                    st.markdown("<div class='leaderboard-box'>🏆 النتيجة الختامية للأبطال 🏆</div>", unsafe_allow_html=True)
                    sorted_p_scores = sorted(r_in["scores"].items(), key=lambda x: x[1], reverse=True)
                    for rank, (player, score) in enumerate(sorted_p_scores):
                        st.write(f"### المركز {rank+1} البطل {player}: حصد {score} نقطة!")
                if st.button("🚪 مغادرة الغرفة"):
                    if an_p in db["rooms"][ar_p]["players"]: db["rooms"][ar_p]["players"].remove(an_p)
                    del st.session_state.joined_live_room; st.rerun()
            with col_pc: show_live_chat(ar_p, an_p, is_admin=False)
        else:
            st.warning("🛑 تم إغلاق الغرفة.")
            if st.button("العودة الرئيسية"): del st.session_state.joined_live_room; st.rerun()

# نمط التسابق الفردي
elif st.session_state.curr_page == "culture_mode":
    st.markdown("### 🧠 نمط اكتشف ثقافتك (اختبر نفسك)")
    if st.button("↩️ العودة للرئيسية"): st.session_state.curr_page = "home"; st.rerun()
    st.write("---")
    c_status = st.session_state.individual_challenge["status"]
    if c_status == "idle":
        if st.button("✨ ابدأ تحدي اختبر نفسك"):
            pool = db["adults_q"] if db["adults_q"] else db["kids_q"]
            if not pool: st.error("⚠️ يرجى رفع ملف أسئلة أولاً.")
            else:
                st.session_state.individual_challenge["q_list"] = random.sample(pool, min(len(pool), 15))
                st.session_state.individual_challenge["status"] = "playing"; st.session_state.individual_challenge["current_q"] = 0; st.session_state.individual_challenge["correct_ans"] = 0; st.rerun()
    elif c_status == "playing":
        qc = st.session_state.individual_challenge["current_q"]; qlc = st.session_state.individual_challenge["q_list"]
        if qc < len(qlc):
            st.markdown(f"### ❓ السؤال {qc + 1} من {len(qlc)}")
            st.markdown(f"## {qlc[qc]['السؤال']}")
            c_ans = str(qlc[qc].get("الخيار 1 - الصحيح", ""))
            opts = [c_ans, str(qlc[qc].get("الخيار 2", "")), str(qlc[qc].get("الخيار 3", "")), str(qlc[qc].get("الخيار 4", ""))]
            sel = st.radio("اختر الجواب:", opts, key=f"c_q_{qc}")
            if st.button("✔️ اعتماد"):
                if sel == c_ans: st.session_state.individual_challenge["correct_ans"] += 1; st.success("صح ✅")
                else: st.error(f"خطأ ❌ الصح: {c_ans}")
                st.session_state.individual_challenge["current_q"] += 1
                if st.session_state.individual_challenge["current_q"] >= len(qlc): st.session_state.individual_challenge["status"] = "finished"
                st.rerun()
    elif c_status == "finished":
        vans = st.session_state.individual_challenge["correct_ans"]
        st.markdown("## 🏆 النتيجة النهائية")
        st.write(f"لقد أجبت على **{vans}** من **15**.")
        if vans >= 13: st.success("🥇 تصنيفك: عالي المستوى")
        else: st.error("📉 حاول مرة أخرى!")
        if st.button("إعادة التحدي"): st.session_state.individual_challenge = {"status": "idle", "current_q": 0, "correct_ans": 0, "q_list": []}; st.rerun()

# صفحة تواصل معنا
elif st.session_state.curr_page == "contact_mode":
    st.markdown("### 📞 تواصل معنا")
    if st.button("↩️ العودة للرئيسية"): st.session_state.curr_page = "home"; st.rerun()
    st.write("---")
    with st.form("contact"):
        st.text_input("الاسم:")
        st.text_area("الرسالة:")
        if st.form_submit_button("📤 إرسال"): st.success("تم الإرسال بنجاح!")
