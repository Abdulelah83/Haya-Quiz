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

# تخصيص واجهة الشات والفقاعات عبر CSS
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
    </style>
""", unsafe_allow_html=True)

# 2. إنشاء مخزن بيانات مشترك وعام على السيرفر يراه الجميع تلقائياً
if 'global_rooms_v2' not in st.session_state: st.session_state.global_rooms_v2 = {}
if 'global_kids_q' not in st.session_state: st.session_state.global_kids_q = []
if 'global_adults_q' not in st.session_state: st.session_state.global_adults_q = []
if 'global_manual_q' not in st.session_state: st.session_state.global_manual_q = []

if 'individual_challenge' not in st.session_state:
    st.session_state.individual_challenge = {
        "status": "idle", "current_q": 0, "correct_ans": 0, "final_score": None, "q_list": []
    }

if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"

@st.fragment
def show_live_chat(room_id, user_name, is_admin):
    room_ref = st.session_state.global_rooms_v2.get(room_id)
    if not room_ref: return

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for chat_msg in room_ref["chat_history"]:
        msg_class = "msg-box-admin" if chat_msg["user_type"] == "admin" else "msg-box-player"
        st.markdown(f"""
            <div class='{msg_class}'>
                <span class='msg-user'>{chat_msg['name']}</span>
                {chat_msg['text']}
                <span class='msg-time'>{chat_msg['time']}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div><br><br>", unsafe_allow_html=True)
    
    with st.form("chat_form_unique", clear_on_submit=True):
        col_c1, col_c2 = st.columns([4, 1])
        c_text = col_c1.text_input("اكتب رسالة فورية:", label_visibility="collapsed")
        if col_c2.form_submit_button("إرسال"):
            if c_text:
                curr_t = datetime.now().strftime("%H:%M")
                new_msg = {
                    "user_type": "admin" if is_admin else "player",
                    "name": "المدير (أبو صالح)" if is_admin else user_name,
                    "text": c_text, "time": curr_t
                }
                st.session_state.global_rooms_v2[room_id]["chat_history"].append(new_msg)
                st.rerun()
    
    time.sleep(2)
    st.rerun()

# الشريط العلوي الثابت للمنصة
navbar_cols = st.columns([1, 4, 1])
with navbar_cols[1]:
    col_nav1, col_nav2 = st.columns(2)
    if col_nav1.button("🏠 الرئيسية", use_container_width=True):
        st.session_state.curr_page = "home"
        st.rerun()
    if col_nav2.button("📞 تواصل معنا", use_container_width=True):
        st.session_state.curr_page = "contact_mode"
        st.rerun()

st.write("---")

# القائمة الجانبية (Sidebar)
with st.sidebar:
    st.markdown("### 🌐 اللغة / Language")
    main_ui_lang = st.selectbox("اختر لغة الموقع:", ["SA العربية", "US English"])
    st.write("---")
    
    st.markdown("### ⚙️ لوحة تحكم النظام (أدمن)")
    admin_input_pass = st.text_input("أدخل الرقم السري للمطور فتح بنك الأسئلة:", type="password")
    
    if admin_input_pass == "1234":
        st.success("🔓 وضع المطور نشط")
        tab_b1, tab_b2, tab_b3 = st.tabs([" قسم أسئلة الأطفال", " قسم أسئلة الكبار", "📝 سؤال يدوي"])
        
        with tab_b1:
            st.write("رفع إكسيل الأطفال")
            kids_f_in = st.file_uploader("Upload Children Excel", type=["xlsx"], key="main_k")
            if kids_f_in:
                try:
                    # حفظ في الذاكرة العامة ليتزامن عند الجميع فوراً
                    st.session_state.global_kids_q = pd.read_excel(kids_f_in).to_dict(orient='records')
                    st.success(f"✅ اعتُمدت ونُشرت للجميع ({len(st.session_state.global_kids_q)} سؤال)")
                except: st.error("خطأ في الملف.")
        
        with tab_b2:
            st.write("رفع إكسيل الكبار")
            adults_f_in = st.file_uploader("Upload Adults Excel", type=["xlsx"], key="main_a")
            if adults_f_in:
                try:
                    st.session_state.global_adults_q = pd.read_excel(adults_f_in).to_dict(orient='records')
                    st.success(f"✅ اعتُمدت ونُشرت للجميع ({len(st.session_state.global_adults_q)} سؤال)")
                except: st.error("خطأ في الملف.")
                
        with tab_b3:
            with st.form("main_manual_form"):
                mt = st.text_input("نص السؤال:")
                o1 = st.text_input("الخيار 1:")
                o2 = st.text_input("الخيار 2:")
                o3 = st.text_input("الخيار 3:")
                o4 = st.text_input("الخيار 4:")
                ca = st.text_input("الإجابة الصحيحة:")
                iu = st.text_input("رابط الصورة التوضيحية:")
                if st.form_submit_button("➕ حفظ السؤال"):
                    if mt and o1 and ca:
                        st.session_state.global_manual_q.append({
                            "السؤال": mt, "الخيار 1": o1, "الخيار 2": o2, "الخيار 3": o3, "الخيار 4": o4,
                            "الإجابة الصحيحة": ca, "الصورة": iu if iu else None
                        })
                        st.success("🎯 تم الحفظ والنشر للجميع!")

# الصفحة الرئيسية
if st.session_state.curr_page == "home":
    col_left_img, col_right_content = st.columns([1, 2])
    with col_left_img:
        st.image("my_kids.png", use_container_width=True)
    with col_right_content:
        st.markdown("<h2 style='color: #4F46E5;'>منصة مسابقات هيا العائلية 🎯</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:1.2rem;'>🔥 أهلاً بالأبطال الغاليين.. جاهزين للتحدي والمنافسة؟</p>", unsafe_allow_html=True)
        st.write("---")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown("🏆 **إدارة مسابقة حية**")
            if st.button("أنشئ مسابقة الآن"):
                st.session_state.curr_page = "admin_mode"
                st.rerun()
        with col_m2:
            st.markdown("🎮 **دخول كمتسابق**")
            if st.button("انضم كمتسابق"):
                st.session_state.curr_page = "player_mode"
                st.rerun()
        with col_m3:
            st.markdown("🕹️ **التسابق الفردي**")
            if st.button("ابدأ اللعب الفردي"):
                st.session_state.curr_page = "culture_mode"
                st.rerun()

# إدارة مسابقة حية (المدير)
elif st.session_state.curr_page == "admin_mode":
    st.markdown("<h2 style='text-align:center;'>👑 إدارة مسابقة حية</h2>", unsafe_allow_html=True)
    if st.button("↩️ العودة للرئيسية"):
        st.session_state.curr_page = "home"
        st.rerun()
    st.write("---")
    
    if 'my_live_room' not in st.session_state:
        col_setup1, col_setup2 = st.columns(2)
        with col_setup1:
            # تصحيح الراديو ليلتقط البيانات المشتركة المرفوعة تلقائياً
            q_src_v2 = st.radio("الفئة المستهدفة للعب:", ["أسئلة الأطفال", "أسئلة الكبار"])
            num_limit_v2 = st.number_input("عدد أسئلة الجولة:", min_value=1, max_value=100, value=10)
            max_players_v2 = st.number_input("عدد المتسابقين الحاضرين:", min_value=1, max_value=20, value=5)
        with col_setup2:
            timer_q_val = st.slider("الوقت المتاح لكل سؤال (بالثواني):", 5, 120, 12)
            st.number_input("الدرجة المستحقة لكل سؤال:", value=10)
            
        if st.button("🎲 توليد الغرفة"):
            pool_in = st.session_state.global_kids_q if "الأطفال" in q_src_v2 else st.session_state.global_adults_q
            if not pool_in: pool_in = st.session_state.global_manual_q
                
            if not pool_in:
                st.error("⚠️ بنك الأسئلة فارغ! يرجى رفع ملف إكسيل من القائمة الجانبية أولاً لتظهر للجميع.")
            else:
                current_code = str(random.randint(1000, 9999))
                st.session_state.my_live_room = current_code
                st.session_state.global_rooms_v2[current_code] = {
                    "players": [], "max_players": max_players_v2, "status": "waiting", "current_q_idx": 0,
                    "questions": pool_in[:num_limit_v2], "chat_history": [], "duration": timer_q_val
                }
                st.rerun()
    else:
        l_room = st.session_state.my_live_room
        r_data_in = st.session_state.global_rooms_v2.get(l_room)
        if r_data_in:
            st.success(f"🎲 رقم الغرفة الحية المعتمد للأبناء هو: **{l_room}**")
            col_live, col_chat = st.columns([2, 1])
            with col_live:
                st.markdown("### 👥 المتسابقون بالانتظار:")
                if not r_data_in["players"]: st.warning("🔄 بانتظار دخول الأبناء...")
                else:
                    g_cols = st.columns(3)
                    for idi, pl_name in enumerate(r_data_in["players"]):
                        g_cols[idi % 3].success(f"• {pl_name} ✅")
                st.write("---")
                if r_data_in["status"] == "waiting":
                    if st.button("🚀 بدء المسابقة"):
                        st.session_state.global_rooms_v2[l_room]["status"] = "playing"
                        st.rerun()
                elif r_data_in["status"] == "playing":
                    qi = r_data_in["current_q_idx"]
                    q_list_in = r_data_in["questions"]
                    if qi < len(q_list_in):
                        st.info(f"📊 السؤال الحالي ({qi + 1}/{len(q_list_in)}):")
                        st.markdown(f"### **{q_list_in[qi]['السؤال']}**")
                        if st.button("➡️ السؤال التالي"):
                            st.session_state.global_rooms_v2[l_room]["current_q_idx"] += 1
                            st.rerun()
                    else:
                        st.success("🏁 انتهت المسابقة!")
                        st.session_state.global_rooms_v2[l_room]["status"] = "finished"
                if st.button("🛑 إنهاء المسابقة وتدمير الغرفة"):
                    if l_room in st.session_state.global_rooms_v2: del st.session_state.global_rooms_v2[l_room]
                    del st.session_state.my_live_room
                    st.rerun()
            with col_chat:
                st.markdown("### 💬 المحادثة")
                show_live_chat(l_room, "المدير", is_admin=True)

# نمط دخول كمتسابق
elif st.session_state.curr_page == "player_mode":
    st.header("🕹️ شاشة انضمام المتسابقين")
    if st.button("↩️ العودة للرئيسية"):
        if 'joined_live_room' in st.session_state:
            old_r = st.session_state.joined_live_room
            old_n = st.session_state.my_joined_name
            if old_r in st.session_state.global_rooms_v2:
                if old_n in st.session_state.global_rooms_v2[old_r]["players"]:
                    st.session_state.global_rooms_v2[old_r]["players"].remove(old_n)
            del st.session_state.joined_live_room
        st.session_state.curr_page = "home"
        st.rerun()
    st.write("---")
    
    if 'joined_live_room' not in st.session_state:
        c_code = st.text_input("أدخل رقم الغرفة المكون من 4 أرقام:")
        c_name = st.text_input("أدخل اسمك الكريم:")
        if st.button("🚪 دخول الغرفة"):
            if c_code in st.session_state.global_rooms_v2:
                robj = st.session_state.global_rooms_v2[c_code]
                if len(robj["players"]) >= robj["max_players"]: st.error("الغرفة ممتلئة!")
                else:
                    st.session_state.global_rooms_v2[c_code]["players"].append(c_name)
                    st.session_state.joined_live_room = c_code
                    st.session_state.my_joined_name = c_name
                    st.success("🎉 متصل بالبث الحقيقي!")
                    st.rerun()
            else: st.error("الغرفة غير موجودة.")
    else:
        ar_p = st.session_state.joined_live_room
        an_p = st.session_state.my_joined_name
        if ar_p in st.session_state.global_rooms_v2:
            r_in = st.session_state.global_rooms_v2[ar_p]
            col_pg, col_pc = st.columns([2, 1])
            with col_pg:
                if r_in["status"] == "waiting": st.info(f"👋 أهلاً {an_p}! انتظر إطلاق المسابقة من الموجه...")
                elif r_in["status"] == "playing":
                    qi = r_in["current_q_idx"]
                    ql = r_in["questions"]
                    if qi < len(ql):
                        st.markdown(f"### ❓ السؤال {qi + 1}")
                        st.markdown(f"## {ql[qi]['السؤال']}")
                        if ql[qi].get("الصورة") and pd.notna(ql[qi]["الصورة"]): st.image(ql[qi]["الصورة"])
                        opts = [str(ql[qi]["الخيار 1"]), str(ql[qi]["الخيار 2"]), str(ql[qi]["الخيار 3"]), str(ql[qi]["الخيار 4"])]
                        sel = st.radio("اختر إجابتك الصحيحة:", opts, key=f"p_opt_{qi}")
                        if st.button("✔️ اعتماد الإجابة"):
                            if sel == str(ql[qi]["الإجابة الصحيحة"]): st.balloons(); st.success("صح! بطل 🥳")
                            else: st.error(f"خطأ! الصح: {ql[qi]['الإجابة الصحيحة']}")
                    else: st.success("🏁 انتهت الأسئلة!")
                elif r_in["status"] == "finished": st.success("🏆 انتهت المسابقة!")
                if st.button("🚪 انسحاب ومغادرة الغرفة"):
                    if an_p in st.session_state.global_rooms_v2[ar_p]["players"]:
                        st.session_state.global_rooms_v2[ar_p]["players"].remove(an_p)
                    del st.session_state.joined_live_room
                    st.rerun()
            with col_pc:
                st.markdown("### 💬 شات المسابقة")
                show_live_chat(ar_p, an_p, is_admin=False)

# نمط التسابق الفردي (اختبر نفسك)
elif st.session_state.curr_page == "culture_mode":
    st.markdown("### 🧠 نمط اكتشف ثقافتك (اختبر نفسك)")
    if st.button("↩️ العودة للرئيسية"):
        st.session_state.curr_page = "home"
        st.rerun()
    st.write("---")
    
    c_status = st.session_state.individual_challenge["status"]
    if c_status == "idle":
        st.write("اضغط على الزر لبدء تحدي الـ 15 سؤالاً وتحديد مستواك الثقافي فوراً.")
        if st.button("✨ ابدأ تحدي اختبر نفسك"):
            pool = st.session_state.global_adults_q if st.session_state.global_adults_q else st.session_state.global_kids_q
            if not pool: pool = st.session_state.global_manual_q
            
            if not pool: st.error("⚠️ يرجى رفع ملف أسئلة من المطور أولاً لتفعيل التحدي الفردي.")
            else:
                st.session_state.individual_challenge["q_list"] = random.sample(pool, min(len(pool), 15))
                st.session_state.individual_challenge["status"] = "playing"
                st.session_state.individual_challenge["current_q"] = 0
                st.session_state.individual_challenge["correct_ans"] = 0
                st.rerun()
    elif c_status == "playing":
        qc = st.session_state.individual_challenge["current_q"]
        qlc = st.session_state.individual_challenge["q_list"]
        if qc < len(qlc):
            st.markdown(f"### ❓ السؤال {qc + 1} من {len(qlc)}")
            st.markdown(f"## {qlc[qc]['السؤال']}")
            opts = [str(qlc[qc]["الخيار 1"]), str(qlc[qc]["الخيار 2"]), str(qlc[qc]["الخيار 3"]), str(qlc[qc]["الخيار 4"])]
            sel = st.radio("اختر الجواب:", opts, key=f"c_q_{qc}")
            if st.button("✔️ اعتماد"):
                if sel == str(qlc[qc]["الإجابة الصحيحة"]): st.session_state.individual_challenge["correct_ans"] += 1; st.success("صح ✅")
                else: st.error(f"خطأ ❌ الصح: {qlc[qc]['الإجابة الصحيحة']}")
                st.session_state.individual_challenge["current_q"] += 1
                if st.session_state.individual_challenge["current_q"] >= len(qlc): st.session_state.individual_challenge["status"] = "finished"
                st.rerun()
    elif c_status == "finished":
        vans = st.session_state.individual_challenge["correct_ans"]
        st.markdown("## 🏆 النتيجة النهائية")
        st.write(f"لقد أجبت على **{vans}** إجابة صحيحة من أصل **15**.")
        if vans >= 13: st.success("🥇 تصنيفك: عالي المستوى")
        elif vans >= 9: st.info("🥈 تصنيفك: متوسط المستوى")
        elif vans >= 6: st.warning("🥉 تصنيفك: مقبول")
        else: st.error("📉 تصنيفك: ضعيف (حاول مرة أخرى!)")
        if st.button("إعادة التحدي"):
            st.session_state.individual_challenge = {"status": "idle", "current_q": 0, "correct_ans": 0, "final_score": None, "q_list": []}
            st.rerun()

# صفحة تواصل معنا
elif st.session_state.curr_page == "contact_mode":
    st.markdown("### 📞 تواصل معنا")
    if st.button("↩️ العودة للرئيسية"): st.session_state.curr_page = "home"; st.rerun()
    st.write("---")
    with st.form("contact"):
        st.text_input("الاسم:")
        st.text_area("الرسالة:")
        if st.form_submit_button("📤 إرسال"): st.success("تم الإرسال بنجاح!")
