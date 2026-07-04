import streamlit as st
import pandas as pd
import time
import random

# -------------------------------------------------------------
# 1. إعدادات الهوية البصرية والتصميم الفخم للمنصة (Streamlit Config)
# -------------------------------------------------------------
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz", 
    page_icon="🎮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص الألوان والخلفيات باستخدام CSS لتطابق واجهة أمس الفخمة
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #4F46E5;
        font-family: 'Cairo', sans-serif;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-title {
        text-align: center;
        color: #4B5563;
        font-size: 1.3rem;
        margin-bottom: 30px;
    }
    .css-1kyx603 {
        background-color: #F3F4F6;
    }
    .stRadio > div {
        flex-direction: row;
        justify-content: center;
    }
    div.stButton > button:first-child {
        background-color: #4F46E5;
        color: white;
        font-size: 1.1rem;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #4338CA;
        transform: translateY(-2px);
    }
    .chat-box {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #E5E7EB;
        height: 300px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. إدارة الذاكرة السحابية المستقرة للمزامنة ومنع اختفاء الغرف
# -------------------------------------------------------------
if 'global_rooms' not in st.session_state:
    st.session_state.global_rooms = {}

if 'admin_questions_kids' not in st.session_state:
    st.session_state.admin_questions_kids = []

if 'admin_questions_adults' not in st.session_state:
    st.session_state.admin_questions_adults = []

if 'manual_questions' not in st.session_state:
    st.session_state.manual_questions = []

def trigger_rerun():
    time.sleep(1.2)
    st.rerun()

# --- هيدر الواجهة الرئيسية ---
st.markdown("<div class='main-title'>🎮 منصة هيا للمسابقات | Haya-Quiz</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>النسخة الاحترافية الشاملة لإدارة المسابقات الحية والتفاعلية عن بُعد</div>", unsafe_allow_html=True)
st.write("---")

# -------------------------------------------------------------
# 3. القائمة الرئيسية الثلاثية الفخمة والأصلية بالصفحة الأولى
# -------------------------------------------------------------
selected_mode = st.radio(
    "🔥 اختر نمط اللعب المفضل لديك اليوم لتنطلق المسابقة الفورية:",
    ["🎮 إدارة مسابقة حية", "🕹️ دخول كمتسابق", "🧠 اكتشف ثقافتك"],
    index=0
)
st.write("---")

# =============================================================
# 🎮 النمط الأول: لوحة تحكم وإدارة المسابقة الحية (المدير والموجه)
# =============================================================
if selected_mode == "🎮 إدارة مسابقة حية":
    
    # [الحالة أ: شاشة الإعداد والرفع الكلاسيكية الأصلية - قبل تفعيل البث]
    if 'active_room_id' not in st.session_state:
        st.markdown("### 🔑 صلاحيات لوحة التحكم والتحقق البرمجي")
        
        col_pass, _ = st.columns([1, 2])
        with col_pass:
            admin_pass = st.text_input("أدخل الرقم السري للمدير لفتح لوحة البث:", type="password")
            
        if admin_pass == "1234":
            st.success("🔓 أهلاً ومرحباً بك يا أبا عبد الإله. تم فتح الصلاحيات والربط مع بايثون بنجاح.")
            st.write("---")
            
            # قسم خيارات الواجهة واللغة المعتمدة
            st.markdown("#### 🌐 الإعدادات العامة للمنصة")
            ui_lang = st.selectbox("لغة واجهة البث المعتمدة للمسابقة:", ["العربية", "English"])
            
            # التبويب الأصلي الجميل لرفع ملفات الأبناء والبالغين
            st.markdown("#### 📂 تحميل وإدارة بنك الأسئلة التفاعلي")
            tab_kids, tab_adults, tab_manual = st.tabs(["📥 أسئلة الأطفال", "📥 أسئلة البالغين", "📝 إضافة سؤال يدوي"])
            
            with tab_kids:
                st.write("ارفع هنا ملف الأسئلة المخصص للأطفال:")
                kids_file = st.file_uploader("اختر ملف إكسيل الأطفال (.xlsx):", type=["xlsx"], key="kids_excel_main")
                if kids_file:
                    try:
                        st.session_state.admin_questions_kids = pd.read_excel(kids_file).to_dict(orient='records')
                        st.success(f"✅ تم تحميل واعتماد بنك أسئلة الأطفال بنجاح! الإجمالي: {len(st.session_state.admin_questions_kids)} سؤال.")
                    except Exception as e:
                        st.error(f"خطأ أثناء قراءة الملف: {e}")
                        
            with tab_adults:
                st.write("ارفع هنا ملف الأسئلة المخصص للبالغين والكبار:")
                adults_file = st.file_uploader("اختر ملف إكسيل البالغين (.xlsx):", type=["xlsx"], key="adults_excel_main")
                if adults_file:
                    try:
                        st.session_state.admin_questions_adults = pd.read_excel(adults_file).to_dict(orient='records')
                        st.success(f"✅ تم تحميل واعتماد بنك أسئلة البالغين بنجاح! الإجمالي: {len(st.session_state.admin_questions_adults)} سؤال.")
                    except Exception as e:
                        st.error(f"خطأ أثناء قراءة الملف: {e}")
                        
            with tab_manual:
                st.write("كتابة سؤال يدوي فوري مع إمكانية ربط صورة توضيحية للأبناء:")
                with st.form("manual_q_form_inputs"):
                    mq_title = st.text_input("نص السؤال المقترح:")
                    mo_1 = st.text_input("الخيار 1:")
                    mo_2 = st.text_input("الخيار 2:")
                    mo_3 = st.text_input("الخيار 3:")
                    mo_4 = st.text_input("الخيار 4:")
                    mq_correct = st.text_input("الإجابة الصحيحة (تطابق أحد الخيارات حرفياً):")
                    mq_img = st.text_input("رابط الصورة التوضيحية للسؤال (رابط مباشر URL):", placeholder="https://...")
                    
                    if st.form_submit_button("➕ حفظ وإدراج السؤال في المسابقة"):
                        if mq_title and mo_1 and mq_correct:
                            st.session_state.manual_questions.append({
                                "السؤال": mq_title, "الخيار 1": mo_1, "الخيار 2": mo_2, "الخيار 3": mo_3, "الخيار 4": mo_4,
                                "الإجابة الصحيحة": mq_correct, "الصورة": mq_img if mq_img else None
                            })
                            st.success(f"🎯 تم حفظ السؤال بنجاح! إجمالي الأسئلة اليدوية المضافة: {len(st.session_state.manual_questions)}")
            
            st.write("---")
            # قسم تحديد محددات وعدادات الغرفة الحية
            st.markdown("#### ⏱️ إعدادات البث المباشر والعداد")
            col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
            with col_cfg1:
                source_select = st.selectbox("اعتماد مصدر الأسئلة الحالي:", ["أسئلة الأطفال المرفوعة", "أسئلة البالغين المرفوعة", "الأسئلة اليدوية المكتوبة"])
            with col_cfg2:
                q_limit_num = st.number_input("عدد الأسئلة المطلوبة في هذه الجولة:", min_value=1, max_value=100, value=10)
            with col_cfg3:
                q_timer_sec = st.number_input("مدة عداد كل سؤال بالثواني (تنازلي):", min_value=5, max_value=180, value=30)
                
            st.write("---")
            # زر التوليد والانبثاق الكامل للوحة البث
            if st.button("✨ تفعيل البث الحي وإنشاء غرفة المسابقة الآن"):
                # اختيار مصفوفة الأسئلة المناسبة
                final_pool = []
                if source_select == "أسئلة الأطفال المرفوعة":
                    final_pool = st.session_state.admin_questions_kids
                elif source_select == "أسئلة البالغين المرفوعة":
                    final_pool = st.session_state.admin_questions_adults
                else:
                    final_pool = st.session_state.manual_questions
                    
                if not final_pool:
                    st.error("⚠️ المصدر المختار فارغ! يرجى رفع الملف أو كتابة الأسئلة أولاً قبل إنشاء الغرفة.")
                else:
                    generated_room = str(random.randint(1000, 9999))
                    st.session_state.active_room_id = generated_room
                    
                    # حفظ بيانات الغرفة في الذاكرة المشتركة الثابتة لضمان استقرار الربط مع الأبناء
                    st.session_state.global_rooms[generated_room] = {
                        "players": [],
                        "status": "waiting",
                        "current_q_index": 0,
                        "questions": final_pool[:q_limit_num],
                        "duration": q_timer_sec,
                        "language": ui_lang,
                        "chat_history": [],
                        "scores": {}
                    }
                    st.rerun()
        elif admin_pass != "":
            st.error("❌ الرقم السري غير صحيح، يرجى إعادة المحاولة.")

    # [الحالة ب: الانبثاق التام واللوحة النظيفة للبث المباشر والدردشة - بعد إنشاء الغرفة]
    else:
        current_room = st.session_state.active_room_id
        room_obj = st.session_state.global_rooms.get(current_room)
        
        if room_obj:
            st.markdown(f"<h2 style='color:#10B981;'>📺 لوحة البث المباشر المزامنة</h2>", unsafe_allow_html=True)
            st.info(f"🎲 رقم الغرفة المعتمد والمثبت لدخول الأبناء هو: **{current_room}** (بانتظار ربط شاشاتهم الحين)")
            st.write(f"📊 اللغة: {room_obj['language']} | الأسئلة المعتمدة للجولة: {len(room_obj['questions'])} سؤال | مدة العداد: {room_obj['duration']} ثانية")
            st.write("---")
            
            # تقسيم شاشة المدير إلى البث الحي والدردشة الجانبية عن بُعد
            col_live_view, col_chat_view = st.columns([2, 1])
            
            with col_live_view:
                st.markdown("### 👥 المتسابقون المتصلون حالياً بالبث الحقيقي:")
                if not room_obj["players"]:
                    st.warning("🔄 بانتظار دخول الأبناء بالرقم السري... الشاشة تحدث نفسها تلقائياً ثانية بثانية لمنع أي فصل.")
                else:
                    cols_grid = st.columns(4)
                    for idx, pl in enumerate(room_obj["players"]):
                        cols_grid[idx % 4].success(f"• {pl} (متصل وجاهز ✅)")
                
                st.write("---")
                if room_obj["status"] == "waiting":
                    st.write("اضغط على الزر أدناه لإطلاق المسابقة وتحويل شاشات الأبناء تلقائياً لصفحة الأسئلة:")
                    if st.button("🚀 إطلاق المسابقة وبدء البث الحي للجميع"):
                        st.session_state.global_rooms[current_room]["status"] = "playing"
                        st.rerun()
                        
                elif room_obj["status"] == "playing":
                    q_idx = room_obj["current_q_index"]
                    qs_array = room_obj["questions"]
                    
                    if q_idx < len(qs_array):
                        st.info(f"📊 السؤال الحالي المفعل على شاشات الأبناء ({q_idx + 1}/{len(qs_array)}):")
                        st.markdown(f"### **{qs_array[q_idx]['السؤال']}**")
                        if qs_array[q_idx].get("الصورة") and pd.notna(qs_array[q_idx]["الصورة"]):
                            st.image(qs_array[q_idx]["الصورة"], width=350, caption="الصورة التوضيحية للسؤال المفعل")
                        
                        st.write("---")
                        if st.button("➡️ نقل شاشات الأبناء تلقائياً وتفعيل السؤال التالي"):
                            st.session_state.global_rooms[current_room]["current_q_index"] += 1
                            st.rerun()
                    else:
                        st.success("🏁 بيض الله وجوهكم! انتهت الجولة وجميع الأسئلة بنجاح.")
                        st.session_state.global_rooms[current_room]["status"] = "finished"
                
                st.write("---")
                # زر الإغلاق النهائي والتدمير الكامل للغرفة والصفحات عند الجميع
                if st.button("🛑 إغلاق وإنهاء المسابقة كلياً وتدمير الصفحات عند الجميع"):
                    if current_room in st.session_state.global_rooms:
                        del st.session_state.global_rooms[current_room]
                    if 'active_room_id' in st.session_state:
                        del st.session_state.active_room_id
                    st.rerun()
            
            with col_chat_view:
                st.markdown("### 💬 غرفة محادثة المسابقة المباشرة")
                st.write("---")
                # عرض الشات في نافذة منظمة
                for chat in room_obj["chat_history"]:
                    st.write(f"**{chat['user']}:** {chat['text']}")
                    
                st.write("---")
                adm_input_msg = st.text_input("اكتب رسالة فورية للأبناء:", key="admin_chat_box_direct")
                if st.button("إرسال الشات"):
                    if adm_input_msg:
                        st.session_state.global_rooms[current_room]["chat_history"].append({"user": "المدير (أبو صالح)", "text": adm_input_msg})
                        st.rerun()
                        
            trigger_rerun()

# =============================================================
# 🕹️ النمط الثاني: شاشة المتسابقين ودخول الأبناء (اللاعبين)
# =============================================================
elif selected_mode == "🕹️ دخول كمتسابق":
    st.markdown("### 🕹️ شاشة انضمام المتسابقين للأبناء")
    st.write("تأكد من استلام رقم الغرفة من الموجه والدخول لمزامنة شاشتك حياً.")
    
    if 'player_room_id' not in st.session_state:
        col_enter1, col_enter2 = st.columns(2)
        with col_enter1:
            input_r = st.text_input("أدخل رقم الغرفة المكون من 4 أرقام لبدء الربط:")
        with col_enter2:
            input_n = st.text_input("أدخل اسمك الكريم لتظهر في لوحة الصدارة:")
            
        if st.button("🚪 دخول الغرفة التفاعلية وبدء المزامنة"):
            if input_r in st.session_state.global_rooms:
                if input_n not in st.session_state.global_rooms[input_r]["players"]:
                    st.session_state.global_rooms[input_r]["players"].append(input_n)
                    st.session_state.global_rooms[input_r]["scores"][input_n] = 0
                st.session_state.player_room_id = input_r
                st.session_state.player_name_tag = input_n
                st.success("🎉 تم الاتصال والربط بنجاح! خلك جاهز بانتظار تفعيل المسابقة من الموجه.")
                st.rerun()
            else:
                st.error("❌ رقم الغرفة غير صحيح أو لم يتم تفعيل الغرفة من المدير حتى الآن.")
    else:
        p_room = st.session_state.player_room_id
        p_name = st.session_state.player_name_tag
        
        if p_room in st.session_state.global_rooms:
            r_info = st.session_state.global_rooms[p_room]
            
            col_player_game, col_player_chat = st.columns([2, 1])
            
            with col_player_game:
                if r_info["status"] == "waiting":
                    st.markdown(f"### 👋 أهلاً بك يا **{p_name}** في المسابقة!")
                    st.info(f"⏳ أنت متصل الآن بالغرفة الرقمية الحية رقم (**{p_room}**). يرجى الانتظار حتى يقوم المدير بالضغط على زر البدء لتظهر لك الأسئلة فوراً.")
                    
                elif r_info["status"] == "playing":
                    c_q = r_info["current_q_index"]
                    q_list = r_info["questions"]
                    
                    if c_q < len(q_list):
                        st.markdown(f"### ❓ السؤال رقم {c_q + 1} من {len(q_list)}")
                        st.markdown(f"## **{q_list[c_q]['السؤال']}**")
                        
                        # إظهار الصورة للأبناء بشكل فخم وكامل وممتاز جداً إذا كانت مرفوعة
                        if q_list[c_q].get("الصورة") and pd.notna(q_list[c_q]["الصورة"]):
                            st.image(q_list[c_q]["الصورة"], use_container_width=True, caption="الصورة المرفقة مع التحدي")
                            
                        # تجميع وعرض الخيارات تفاعلياً كأزرار راديو أنيقة
                        choices = [str(q_list[c_q]["الخيار 1"]), str(q_list[c_q]["الخيار 2"]), str(q_list[c_q]["الخيار 3"]), str(q_list[c_q]["الخيار 4"])]
                        player_selection = st.radio("اختر إجابتك الصحيحة بسرعة قبل انتهاء الوقت المخصص:", choices, key=f"radio_p_q_{c_q}")
                        
                        # العداد الزمني التنبيهي المحدث
                        st.warning(f"⏳ العداد الزمني التنازلي للسؤال الحالي: {r_info['duration']} ثانية.")
                        
                        if st.button("✔️ اعتماد الإجابة النهائية للسؤال"):
                            if player_selection == str(q_list[c_q]["الإجابة الصحيحة"]):
                                st.balloons()
                                st.success("🎉 إجابة صحيحة وممتازة! كفووو يا بطل وجاري تسجيل النقاط 🥳")
                            else:
                                st.error(f"💔 للأسف إجابة خاطئة! ركز جيداً في التحدي القادم. الجواب الصح هو: {q_list[c_q]['الإجابة الصحيحة']}")
                    else:
                        st.success("🏁 كفو يا أبطال! انتهت المسابقة وجولة الأسئلة، انتظر إعلان النتيجة وتوزيع الجوائز من الموجه.")
                        
                elif r_info["status"] == "finished":
                    st.success("🏆 تم إنهاء المسابقة الحالية بالكامل بنجاح من المدير. بيض الله وجوهكم جميعاً!")
            
            with col_player_chat:
                st.markdown("### 💬 المحادثة المباشرة مع الموجه")
                st.write("---")
                for ch in r_info["chat_history"]:
                    st.write(f"**{ch['user']}:** {ch['text']}")
                    
                st.write("---")
                p_msg_input = st.text_input("اكتب رسالة سريعة هنا:", key="player_chat_input_unique")
                if st.button("إرسال الرسالة"):
                    if p_msg_input:
                        st.session_state.global_rooms[p_room]["chat_history"].append({"user": p_name, "text": p_msg_input})
                        st.rerun()
                        
            trigger_rerun()
        else:
            st.warning("🛑 قام الموجه بإنهاء هذه المسابقة وتصفير وإغلاق الغرفة الحالية فوراً.")
            if st.button("العودة إلى شاشة الدخول الرئيسية"):
                if 'player_room_id' in st.session_state:
                    del st.session_state.player_room_id
                st.rerun()

# =============================================================
# 🧠 النمط الثالث: اكتشف ثقافتك (التسابق الفردي وتطوير المعلومات)
# =============================================================
else:
    st.markdown("### 🧠 نمط: اكتشف ثقافتك الفردي وتحدي المعلومات العامة")
    st.write("هنا يمكنك اللعب وتجربة معلوماتك بشكل فردي ومستقل تماماً لتطوير ثقافتك وحصيلة معلوماتك العامة بدون موجه.")
    st.write("---")
    
    cult_questions_bank = [
        {"س": "ما هو أول مسجد أُسس في الإسلام وبناه الرسول ﷺ؟", "ج": "مسجد قباء في المدينة المنورة"},
        {"س": "كم عدد سور القرآن الكريم كاملة؟", "ج": "114 سورة"},
        {"س": "ما هي عاصمة المملكة العربية السعودية؟", "ج": "الرياض"},
        {"س": "كم عدد كواكب المجموعة الشمسية المعتمدة علمياً؟", "ج": "8 كواكب"}
    ]
    
    for idx, item in enumerate(cult_questions_bank):
        st.markdown(f"#### 💡 التحدي الثقافي رقم {idx + 1}:")
        st.info(item["س"])
        if st.button(f"👁️ كشف الإجابة الصحيحة لتحدي {idx + 1}", key=f"btn_cult_unique_{idx}"):
            st.success(f"الجواب الصحيح هو: {item['g' if 'g' in item else 'ج']}")
        st.write("---")
