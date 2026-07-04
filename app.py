import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime

# -------------------------------------------------------------
# 1. إعدادات الصفحة والهوية البصرية الفخمة للمنصة (Streamlit Config)
# -------------------------------------------------------------
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz Pro", 
    page_icon="🎮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص واجهة الشات وتنسيق فقاعات الواتساب عبر CSS
st.markdown("""
    <style>
    .main-title { text-align: center; color: #4F46E5; font-size: 2.8rem; font-weight: bold; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #4B5563; font-size: 1.2rem; margin-bottom: 25px; }
    .stRadio > div { flex-direction: row; justify-content: center; }
    div.stButton > button:first-child { background-color: #4F46E5; color: white; border-radius: 8px; border: none; font-size: 1rem; }
    div.stButton > button:first-child:hover { background-color: #4338CA; }
    
    /* تنسيق فقاعات المحادثة الشبيه بالواتساب */
    .chat-container { background-color: #E5DDD5; padding: 15px; border-radius: 12px; max-height: 350px; overflow-y: auto; display: flex; flex-direction: column; }
    .msg-box-admin { background-color: #DCF8C6; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: right; align-self: flex-end; max-width: 80%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .msg-box-player { background-color: #FFFFFF; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: right; align-self: flex-start; max-width: 80%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .msg-user { font-weight: bold; font-size: 0.85rem; color: #075E54; display: block; margin-bottom: 3px; }
    .msg-time { font-size: 0.7rem; color: #999; text-align: left; display: block; margin-top: 3px; }
    
    /* تنسيق شريط النقل العلوي */
    .nav-bar { display: flex; justify-content: center; gap: 20px; background-color: #F9FAFB; padding: 10px; border-radius: 8px; border: 1px solid #E5E7EB; margin-bottom: 20px; }
    .nav-link { text-decoration: none; color: #4B5563; font-weight: bold; font-size: 1.1rem; cursor: pointer; padding: 5px 10px; border-radius: 5px; }
    .nav-link:hover { background-color: #E5E7EB; color: #111827; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. إدارة الذاكرة السحابية المستقرة للمزامنة ومنع اختفاء الغرف
# -------------------------------------------------------------
if 'global_rooms_v2' not in st.session_state: st.session_state.global_rooms_v2 = {}
if 'kids_q_v2' not in st.session_state: st.session_state.kids_q_v2 = []
if 'adults_q_v2' not in st.session_state: st.session_state.adults_q_v2 = []
if 'manual_q_v2' not in st.session_state: st.session_state.manual_q_v2 = []

# إدارة الحالة الخاصة بالتحدي الفردي "اختبر نفسك"
if 'individual_challenge' not in st.session_state:
    st.session_state.individual_challenge = {
        "status": "idle", "current_q": 0, "correct_ans": 0, "final_score": None, "q_list": []
    }

# دالة التحديث الجزئي (Fragment) لتحديث الشات بهدوء بدون وميض الصفحة
@st.fragment
def show_live_chat(room_id, user_name, is_admin):
    room_ref = st.session_state.global_rooms_v2.get(room_id)
    if not room_ref: return

    # عرض فقاعات المحادثة (الواتساب)
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
    
    # حقل الإدخال وزر الإرسال
    with st.form("chat_form_unique", clear_on_submit=True):
        col_c1, col_c2 = st.columns([4, 1])
        c_text = col_c1.text_input("اكتب رسالة فورية:", label_visibility="collapsed")
        if col_c2.form_submit_button("إرسال الشات"):
            if c_text:
                curr_t = datetime.now().strftime("%H:%M")
                new_msg = {
                    "user_type": "admin" if is_admin else "player",
                    "name": "المدير (أبو صالح)" if is_admin else user_name,
                    "text": c_text, "time": curr_t
                }
                st.session_state.global_rooms_v2[room_id]["chat_history"].append(new_msg)
                st.rerun() # تحديث الفقاعات فقط داخل مربع الشات
    
    # تحديث الشات بهدوء كل ثانيتين
    time.sleep(2)
    st.rerun()

# --- الشريط العلوي الثابت للمنصة (Navigation) ---
# (زر الرجوع للخلف يختفي هنا في الرئيسية)
navbar_cols = st.columns([1, 4, 1])
with navbar_cols[1]:
    st.markdown("""
        <div class='nav-bar'>
            <a class='nav-link' id='nav_home'>🏠 الرئيسية</a>
            <a class='nav-link' id='nav_contact'>📞 تواصل معنا</a>
        </div>
    """, unsafe_allow_html=True)
st.write("---")

# إدارة الحالة لعرض الأنماط والرجوع للخلف
if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"

# --- القائمة الجانبية (Sidebar) لـ "رقم الأدمن واللغة" ---
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات العامة")
    main_ui_lang = st.selectbox("اختر لغة المنصة المعتمدة:", ["العربية", "English"])
    st.write("---")
    
    st.markdown("#### 🔑 لوحة تحكم الأدمن والأسئلة")
    admin_input_pass = st.text_input("أدخل رقم الأدمن السري لفتح بنك الأسئلة:", type="password")
    
    # تفعيل شاشة بنك الأسئلة فقط إذا تم كتابة الرقم السري
    if admin_input_pass == "1234":
        st.success("🔓 تم فتح الصلاحيات المتقدمة للأدمن بنجاح.")
        tab_b1, tab_b2, tab_b3 = st.tabs(["📥 ملفات الأطفال", "📥 ملفات البالغين", "📝 إضافة سؤال يدوي"])
        
        with tab_b1:
            kids_f_in = st.file_uploader("📥 رفع إكسيل الأطفال (.xlsx):", type=["xlsx"], key="main_k")
            if kids_f_in:
                try:
                    st.session_state.kids_q_v2 = pd.read_excel(kids_f_in).to_dict(orient='records')
                    st.success(f"✅ تم اعتماد أسئلة الأطفال ({len(st.session_state.kids_q_v2)} سؤال)")
                except: st.error("خطأ في بنية الملف.")
        
        with tab_b2:
            adults_f_in = st.file_uploader("📥 رفع إكسيل البالغين (.xlsx):", type=["xlsx"], key="main_a")
            if adults_f_in:
                try:
                    st.session_state.adults_q_v2 = pd.read_excel(adults_f_in).to_dict(orient='records')
                    st.success(f"✅ تم اعتماد أسئلة البالغين ({len(st.session_state.adults_q_v2)} سؤال)")
                except: st.error("خطأ في بنية الملف.")
                
        with tab_b3:
            st.write("إضافة سؤال يدوي تفاعلي مع الصورة:")
            with st.form("main_manual_form"):
                mt = st.text_input("نص السؤال:")
                o1 = st.text_input("الخيار 1:")
                o2 = st.text_input("الخيار 2:")
                o3 = st.text_input("الخيار 3:")
                o4 = st.text_input("الخيار 4:")
                ca = st.text_input("الإجابة الصحيحة تماماً:")
                iu = st.text_input("رابط الصورة التوضيحية (URL):")
                
                if st.form_submit_button("➕ حفظ السؤال"):
                    if mt and o1 and ca:
                        st.session_state.manual_q_v2.append({
                            "السؤال": mt, "الخيار 1": o1, "الخيار 2": o2, "الخيار 3": o3, "الخيار 4": o4,
                            "الإجابة الصحيحة": ca, "الصورة": iu if iu else None
                        })
                        st.success("🎯 تم حفظ وإدراج السؤال في الذاكرة بنجاح!")
    
    st.write("---")
    st.write("منصة هيا - النسخة المعتمدة والمستقرة.")

# --- الواجهة الرئيسية للموقع (الصفحة الأولى) ---
if st.session_state.curr_page == "home":
    st.markdown("<div class='main-title'>🎮 منصة هيا للمسابقات | Haya-Quiz</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>المنصة الاحترافية الشاملة لإدارة المسابقات والمحاكاة الحية والدردشة التفاعلية عن بُعد</div>", unsafe_allow_html=True)
    st.write("---")
    
    # الأنماط الرئيسية الثلاثة في الصفحة الأولى
    main_options_cols = st.columns(3)
    
    with main_options_cols[0]:
        st.markdown("### 🎮 إدارة مسابقة حية")
        st.write("للموجهين والمدراء لإطلاق الغرف والتحكم عن بعد.")
        if st.button("🚀 دخول كمدير"):
            st.session_state.curr_page = "admin_mode"
            st.rerun()
            
    with main_options_cols[1]:
        st.markdown("### 🕹️ دخول كمتسابق")
        st.write("انضم للمسابقة الحية المزامنة مع الأصدقاء ثانية بثانية.")
        if st.button("🚪 دخول كمتسابق"):
            st.session_state.curr_page = "player_mode"
            st.rerun()
            
    with main_options_cols[2]:
        st.markdown("### 🧠 اكتشف ثقافتك")
        st.write("تعلم وشارك في تحدي المعلومات الفردي 'اختبر نفسك'.")
        if st.button("🧠 ابدأ الثقافة"):
            st.session_state.curr_page = "culture_mode"
            st.rerun()
    st.write("---")
    # خانة تواصل معنا في الصفحة الرئيسية
    st.markdown("#### 📧 خانة التواصل مع إدارة المنصة")
    with st.form("contact_form_main"):
        st.text_input("اسمك الكريم:")
        st.text_area("رسالتك:")
        if st.form_submit_button("📤 إرسال للفريق الفني"):
            st.success("شكراً لتواصلك! سيتم الرد عليك قريباً جداً.")

# =============================================================
# 🎮 النمط الأول: لوحة إدارة المسابقة الحية (المدير والموجه)
# =============================================================
elif st.session_state.curr_page == "admin_mode":
    st.header("📺 لوحة البث المباشر والتحكم الفوري للموجه")
    
    # [تعديل]: زر الرجوع للخلف يظهر فقط داخل الصفحات الداخلية
    if st.button("↩️ الرجوع للقائمة الرئيسية", key="back_to_home_admin"):
        st.session_state.curr_page = "home"
        st.rerun()
    st.write("---")
    
    # [الحالة أ: لوحة التجهيز الأصلية الكلاسيكية - بدون رقم سري للغرفة]
    if 'my_live_room' not in st.session_state:
        st.markdown("### 🛠️ محددات وإعدادات المسابقة الحية")
        
        # [تعديل جديد]: فصل صلاحيات رقم الأدمن عن صفحة المدير
        # فُتحت الصفحة مباشرة بدون أي رقم سري للغرفة
        
        col_setup1, col_setup2, col_setup3 = st.columns(3)
        with col_setup1:
            q_src_v2 = st.selectbox("المصدر المعتمد للأسئلة:", ["أسئلة الأطفال المرفوعة", "أسئلة البالغين المرفوعة", "الأسئلة اليدوية المكتوبة"])
        with col_setup2:
            num_limit_v2 = st.number_input("عدد الأسئلة المطلوبة في هذه الجولة:", min_value=1, max_value=100, value=10)
        with col_setup3:
            max_players_v2 = st.number_input("الحد الأقصى لعدد المتسابقين (اللاعبين):", min_value=1, max_value=20, value=5)
            
        st.write("---")
        # زر التوليد والانبثاق الكامل للوحة البث النظيفة
        if st.button("✨ تفعيل وإنشاء غرفة المسابقة الآن والبدء"):
            pool_in = []
            if q_src_v2 == "أسئلة الأطفال المرفوعة": pool_in = st.session_state.kids_q_v2
            elif q_src_v2 == "أسئلة البالغين المرفوعة": pool_in = st.session_state.adults_q_v2
            else: pool_in = st.session_state.manual_q_v2
                
            if not pool_in:
                st.error("⚠️ المصدر المختار فارغ! يرجى تحميل ملف إكسيل أو كتابة أسئلة أولاً.")
            else:
                # [تعديل]: توليد رقم الغرفة المعتمد والمثبت لدخول الأبناء
                current_code = str(random.randint(1000, 9999))
                st.session_state.my_live_room = current_code
                
                # حفظ البيانات في الذاكرة المستقرة لمنع خطأ الرقم
                st.session_state.global_rooms_v2[current_code] = {
                    "players": [],
                    "max_players": max_players_v2,
                    "status": "waiting",
                    "current_q_idx": 0,
                    "questions": pool_in[:num_limit_v2],
                    "chat_history": []
                }
                st.rerun()
                
    # [الحالة ب: الانبثاق الكامل للوحة البث النظيفة والشات الاحترافي]
    else:
        l_room = st.session_state.my_live_room
        r_data_in = st.session_state.global_rooms_v2.get(l_room)
        
        if r_data_in:
            st.info(f"🎲 تم تثبيت رقم الغرفة الحية لدخول الأبناء: **{l_room}** (بانتظار ربط شاشاتهم الحين)")
            st.write(f"📊 الأسئلة: {len(r_data_in['questions'])} | المشتركون الحين: **{len(r_data_in['players'])}/{r_data_in['max_players']}**")
            st.write("---")
            
            # تقسيم شاشة المدير إلى البث الحي والشات الاحترافي (بدون وميض للصفحة)
            col_ بث_مباشر, col_ شات_احترافي = st.columns([2, 1])
            
            with col_ بث_مباشر:
                st.markdown("### 👥 المتسابقون المتصلون حالياً:")
                if not r_data_in["players"]:
                    st.warning("🔄 بانتظار دخول الأبناء بالرقم السري... الشاشة تحدث نفسها تلقائياً بهدوء.")
                else:
                    g_ cols = st.columns(3)
                    for idi, pl_name in enumerate(r_data_in["players"]):
                        g_ cols[idi % 3].success(f"• {pl_name} (متصل وجاهز ✅)")
                        
                st.write("---")
                if r_data_in["status"] == "waiting":
                    st.write("اضغط على الزر أدناه لإطلاق المسابقة وتحويل شاشات الأبناء تلقائياً لصفحة الأسئلة:")
                    if st.button("🚀 إطلاق المسابقة وبدء البث الحي للجميع"):
                        st.session_state.global_rooms_v2[l_room]["status"] = "playing"
                        st.rerun()
                        
                elif r_data_in["status"] == "playing":
                    qi = r_data_in["current_q_idx"]
                    q_list_in = r_data_in["questions"]
                    
                    if qi < len(q_list_in):
                        st.info(f"📊 السؤال الحالي المفعل للأبناء ({qi + 1}/{len(q_list_in)}):")
                        st.markdown(f"### **{q_list_in[qi]['السؤال']}**")
                        if q_list_in[qi].get("الصورة"):
                            st.image(q_list_in[qi]["الصورة"], width=300)
                            
                        if st.button("➡️ نقل المتسابقين وتفعيل السؤال التالي فوراً"):
                            st.session_state.global_rooms_v2[l_room]["current_q_idx"] += 1
                            st.rerun()
                    else:
                        st.success("🏁 بيّض الله وجوهكم! انتهت الأسئلة المحددة بنجاح.")
                        st.session_state.global_rooms_v2[l_room]["status"] = "finished"
                
                st.write("---")
                # [تعديل]: زر إنهاء المسابقة 🛑 أحمر بارز عند المدير
                if st.button("🛑 إغلاق وإنهاء المسابقة كلياً وتدمير الغرفة للجميع"):
                    if l_room in st.session_state.global_rooms_v2:
                        del st.session_state.global_rooms_v2[l_room]
                    if 'my_live_room' in st.session_state:
                        del st.session_state.my_live_room
                    st.rerun()
                    
            with col_ شات_احترافي:
                st.markdown("### 💬 شات المسابقة عن بُعد (واتساب)")
                # تفعيل الشات المطور والفقاعات الاحترافية وتحديثه بهدوء (Fragment)
                show_live_chat(l_room, "المدير", is_admin=True)

# =============================================================
# 🕹️ النمط الثاني: شاشة المتسابقين ودخول الأبناء (اللاعبين)
# =============================================================
elif st.session_state.curr_page == "player_mode":
    st.markdown("### 🕹️ شاشة انضمام الأبناء للمنافسة الحية")
    
    # زر الرجوع للخلف يظهر فقط داخل الصفحات الداخلية
    if st.button("↩️ الرجوع للقائمة الرئيسية", key="back_to_home_player"):
        # [تعديل جديد]: تصفير حالة الانضمام عند الرجوع للخلف
        if 'joined_live_room' in st.session_state:
            active_r_old = st.session_state.joined_live_room
            p_name_old = st.session_state.my_joined_name
            if active_r_old in st.session_state.global_rooms_v2:
                if p_name_old in st.session_state.global_rooms_v2[active_r_old]["players"]:
                    st.session_state.global_rooms_v2[active_r_old]["players"].remove(p_name_old)
            del st.session_state.joined_live_room
        st.session_state.curr_page = "home"
        st.rerun()
    st.write("---")
    
    if 'joined_live_room' not in st.session_state:
        col_in_p1, col_in_p2 = st.columns(2)
        with col_in_p1:
            code_in_p = st.text_input("أدخل رقم الغرفة المستلم من الموجه لبدء الربط:")
        with col_in_p2:
            name_in_p = st.text_input("أدخل اسمك الكريم للانضمام الحقيقي:")
            
        if st.button("🚪 دخول الغرفة التفاعلية وبدء المزامنة"):
            # التحقق المستقر من وجود الغرفة لمنع خطأ الرقم
            if code_in_p in st.session_state.global_rooms_v2:
                current_r_obj = st.session_state.global_rooms_v2[code_in_p]
                
                # التحقق من ميزة الحد الأقصى لعدد اللاعبين المحددة من المدير
                if len(current_r_obj["players"]) >= current_r_obj["max_players"]:
                    st.error("⚠️ عذراً! الغرفة ممتلئة بالكامل ووصلت للحد الأقصى من المتسابقين.")
                else:
                    if name_in_p not in current_r_obj["players"]:
                        st.session_state.global_rooms_v2[code_in_p]["players"].append(name_in_p)
                    st.session_state.joined_live_room = code_in_p
                    st.session_state.my_joined_name = name_in_p
                    st.success("🎉 تم ربطك بنجاح بالغرفة رقم! خلك جاهز للبث.")
                    st.rerun()
            else:
                st.error("❌ رقم الغرفة غير صحيح أو تم إغلاقها من المدير. تأكد من الرقم مجدداً.")
    else:
        active_r_p = st.session_state.joined_live_room
        name_p_in = st.session_state.my_joined_name
        
        if active_r_p in st.session_state.global_rooms_v2:
            current_r_in = st.session_state.global_rooms_v2[active_r_p]
            
            col_p_bith, col_p_shat = st.columns([2, 1])
            
            with col_p_bith:
                if current_r_in["status"] == "waiting":
                    st.markdown(f"### 👋 أهلاً بك يا **{name_p_in}**")
                    st.info(f"⏳ تم ربط شاشتك بنجاح وبانتظار تحويلها تلقائياً لصفحة الأسئلة عند البدء.")
                elif current_r_in["status"] == "playing":
                    idx_qi = current_r_in["current_q_idx"]
                    questions_list = current_r_in["questions"]
                    
                    if idx_qi < len(questions_list):
                        st.markdown(f"### ❓ السؤال رقم {idx_qi + 1} من {len(questions_list)}")
                        st.markdown(f"## **{questions_list[idx_qi]['السؤال']}**")
                        
                        # إظهار الصورة للأبناء بشكل كامل وممتاز ومطابق لأمس
                        if questions_list[idx_qi].get("الصورة") and pd.notna(questions_list[idx_qi]["الصورة"]):
                            st.image(questions_list[idx_qi]["الصورة"], use_container_width=True)
                            
                        opts_qi = [str(questions_list[idx_qi]["الخيار 1"]), str(questions_list[idx_qi]["الخيار 2"]), str(questions_list[idx_qi]["الخيار 3"]), str(questions_list[idx_qi]["الخيار 4"])]
                        ans_p_in = st.radio("اختر إجابتك الصحيحة بسرعة قبل نهاية الوقت:", opts_qi, key=f"radio_choice_{idx_qi}")
                        
                        st.warning("⏳ العداد الزمني للسؤال يعمل... خلك سريع!")
                        
                        if st.button("✔️ اعتماد الإجابة النهائية"):
                            if ans_p_in == str(questions_list[idx_qi]["الإجابة الصحيحة"]):
                                st.balloons()
                                st.success("🎉 إجابة صحيحة كفوووو يا بطل! 🥳")
                            else:
                                st.error(f"💔 للأسف إجابة خاطئة! حاول في السؤال القادم. الإجابة الصحيحة هي: {questions_list[idx_qi]['الإجابة الصحيحة']}")
                    else:
                        st.success("🏁 كفو يا أبطال! انتهت الأسئلة وفي انتظار النتيجة النهائية من الموجه.")
                elif current_r_in["status"] == "finished":
                    st.success("🏆 تم إنهاء المسابقة الحالية بالكامل بنجاح من المدير. بيّض الله وجوهكم.")
                
                st.write("---")
                # [تعديل]: زر للمتسابق (لو زعل أو أراد الانسحاب) 🚪 انسحاب ومغادرة الغرفة
                if st.button("🚪 انسحاب ومغادرة الغرفة", key="leave_room_unique_btn"):
                    # حذف اسمه تلقائياً من قائمة المتسابقين عند المدير
                    if active_r_p in st.session_state.global_rooms_v2:
                        if name_p_in in st.session_state.global_rooms_v2[active_r_p]["players"]:
                            st.session_state.global_rooms_v2[active_r_p]["players"].remove(name_p_in)
                    del st.session_state.joined_live_room
                    del st.session_state.my_joined_name
                    st.rerun() # تعود شاشته هو فقط إلى القائمة الرئيسية للموقع
                    
            with col_p_shat:
                st.markdown("### 💬 شات المسابقة المباشرة للمتسابق")
                # تفعيل الشات المطور والفقاعات الاحترافية وتحديثه بهدوء (Fragment)
                show_live_chat(active_r_p, name_p_in, is_admin=False)
                
        else:
            st.warning("🛑 قام الموجه بإغلاق وإنهـاء الغرفة الحالية لانتهاء المسابقة.")
            if st.button("العودة لصفحة الدخول الرئيسية"):
                if 'joined_live_room' in st.session_state: del st.session_state.joined_live_room
                st.rerun()

# =============================================================
# 🧠 النمط الثالث: اكتشف ثقافتك (تحدي اختبر نفسك الفردي)
# =============================================================
elif st.session_state.curr_page == "culture_mode":
    st.markdown("### 🧠 نمط اكتشف ثقافتك وتحدي اختبر نفسك")
    
    # زر الرجوع للخلف يظهر فقط داخل الصفحات الداخلية
    if st.button("↩️ الرجوع للقائمة الرئيسية", key="back_to_home_culture"):
        st.session_state.curr_page = "home"
        st.rerun()
    st.write("---")
    
    st.markdown("#### ⏱️ تحدي اختبر نفسك الفردي (15 سؤال)")
    st.write("لتعلم وتجربة حصيلتك الثقافية بشكل مستقل تماماً.")
    st.write("---")
    
    cult_status = st.session_state.individual_challenge["status"]
    
    # [الحالة أ: لوحة البدء الأصلية - Deactivate الأسئلة العشوائية المكتوبة سابقاً]
    if cult_status == "idle":
        # تم إلغاء وتعطيل الأسئلة القديمة المكتوبة، ويحتوي فقط على زر واحد
        st.write("اضغط على الزر أدناه لبدء تحدي الـ 15 سؤالاً وتحديد مستواك الثقافي فوراً.")
        if st.button("✨ ابدأ تحدي اختبر نفسك الحين"):
            
            # اختيار مصفوفة الأسئلة المخصصة للأطفال أو البالغين بشكل ذكي
            # (سنعتمد ملفات الأطفال أو البالغين المرفوعة بالأعلى)
            pool_ кульت_in = []
            if st.session_state.adults_q_v2:
                pool_ кульت_in = st.session_state.adults_q_v2
            elif st.session_state.kids_q_v2:
                pool_ кульت_in = st.session_state.kids_q_v2
                
            if not pool_ кульت_in:
                st.error("⚠️ المصدر المختار فارغ! يرجى رفع ملف إكسيل للبالغين أو الأطفال أولاً لفتح التحدي الفردي.")
            else:
                # [تعديل جديد]: تفعيل ميزة الـ 15 سؤالاً فقط من بنك الأسئلة الذكي
                # سحب 15 سؤالاً فقط بشكل عشوائي وذكي
                selected_q_ cult_15 = random.sample(pool_ кульت_in, 15)
                
                # تفعيل التحدي وحفظ المصفوفة
                st.session_state.individual_challenge["status"] = "playing"
                st.session_state.individual_challenge["q_list"] = selected_q_ cult_15
                st.session_state.individual_challenge["current_q"] = 0
                st.session_state.individual_challenge["correct_ans"] = 0
                st.rerun()
                
    # [الحالة ب: مرحلة اللعب الفردي الحية]
    elif cult_status == "playing":
        qi_c = st.session_state.individual_challenge["current_q"]
        qs_list_c = st.session_state.individual_challenge["q_list"]
        
        if qi_c < 15:
            st.markdown(f"### ❓ التحدي الفردي رقم {qi_c + 1} من 15")
            st.markdown(f"## **{qs_list_c[qi_c]['السؤال']}**")
            
            opts_ cult_c = [str(qs_list_c[qi_c]["الخيار 1"]), str(qs_list_c[qi_c]["الخيار 2"]), str(qs_list_c[qi_c]["الخيار 3"]), str(qs_list_c[qi_c]["الخيار 4"])]
            ans_ cult_c_in = st.radio("اختر إجابتك الصحيحة الحين بسرعة قبل فوات الأوان:", opts_ cult_c, key=f"radio_icult_{qi_c}")
            
            if st.button("✔️ اعتماد الإجابة والسؤال", key=f"btn_icult_{qi_c}"):
                if ans_ cult_c_in == str(qs_list_c[qi_c]["الإجابة الصحيحة"]):
                    st.success("🎉 إجابة صحيحة كفو يا بطل! 🥳")
                    st.session_state.individual_challenge["correct_ans"] += 1
                else:
                    st.error(f"💔 للأسف إجابة خاطئة! الجواب الصح هو: {qs_list_c[qi_c]['الإجابة الصحيحة']}")
                
                # [تعديل جديد]: تحديث السؤال رقم 15 الفوري وتفعيل النتيجة
                st.session_state.individual_challenge["current_q"] += 1
                if st.session_state.individual_challenge["current_q"] >= 15:
                    st.session_state.individual_challenge["status"] = "finished"
                st.rerun()
                
    # [الحالة ج: شاشة النتيجة والتصنيف التلقائي الفخم للمستوى]
    elif cult_status == "finished":
        correct_n = st.session_state.individual_challenge["correct_ans"]
        
        # [تعديل جديد]: تفعيل ميزة شاشة النتيجة الفخمة والتصنيف الختامي
        st.markdown("<h2 style='text-align:center;'>🏆 النتيجة النهائية للتحدي الفردي</h2>", unsafe_allow_html=True)
        st.write(f"🎉 بيّض الله وجهك يا بطل! لقد جاوبت على **{correct_n}** سؤالاً صح من أصل **15** سؤال.")
        st.write("---")
        
        # التصنيف التلقائي للتحدي الفردي الحية على السيرفر
        # عالي المستوى، متوسط، مقبول، ضعيف (مع عبارة تشجيعية)
        classification = ""
        classify_class = ""
        if correct_n >= 13:
            classification = "🥇 عالي المستوى (ممتاز جداً)"
            classify_class = "stSuccess"
        elif correct_n >= 9:
            classification = "🥈 متوسط المستوى (ممتاز)"
            classify_class = "stInfo"
        elif correct_n >= 6:
            classification = "🥉 مقبول (جيد)"
            classify_class = "stWarning"
        else:
            classification = "📉 ضعيف"
            classify_class = "stError"
            
        # إظهار فقاعة التصنيف
        if classify_class == "stSuccess": st.success(f"تصنيفك الثقافي بناءً على إجاباتك هو: **{classification}**")
        elif classify_class == "stInfo": st.info(f"تصنيفك الثقافي بناءً على إجاباتك هو: **{classification}**")
        elif classify_class == "stWarning": st.warning(f"تصنيفك الثقافي بناءً على إجاباتك هو: **{classification}**")
        elif classify_class == "stError": st.error(f"تصنيفك الثقافي بناءً على إجاباتك هو: **{classification}**، مع عبارة تشجيعية للمحاولة مرة أخرى.")
            
        st.write("---")
        if st.button("العودة للقائمة الرئيسية"):
            st.session_state.curr_page = "home"
            # تصفير حالة التحدي الفردي للعودة
            st.session_state.individual_challenge = {
                "status": "idle", "current_q": 0, "correct_ans": 0, "final_score": None, "q_list": []
            }
            st.rerun()

# ----------------- 📧 خانة تواصل معنا في الشريط العلوي (الرئيسية) -----------------
# (سيتم عرضها فقط إذا تم الضغط على زر تواصل معنا في الشريط العلوي الحية)
elif st.session_state.curr_page == "contact_mode":
    st.markdown("### 📞 تواصل معنا")
    if st.button("↩️ الرجوع للقائمة الرئيسية", key="back_to_home_contact"):
        st.session_state.curr_page = "home"
        st.rerun()
    st.write("---")
    st.markdown("#### 📧 خانة تواصل معنا - تفعيل الشريط العلوي الثابت")
    with st.form("contact_form_sidebar_unique"):
        st.text_input("اسمك الكريم:")
        st.text_area("رسالتك المباشرة:")
        if st.form_submit_button("📤 إرسال للفريق"):
            st.success("تم إرسال تواصلك بنجاح! سيتم الرد عليك قريباً.")
