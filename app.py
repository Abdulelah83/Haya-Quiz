import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime

# 1. إعدادات الهوية البصرية والتصميم الفخم للمنصة
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz", 
    page_icon="🎮", 
    layout="wide"
)

# تخصيص واجهة الشات وتنسيق فقاعات الواتساب عبر CSS
st.markdown("""
    <style>
    .main-title { text-align: center; color: #4F46E5; font-size: 2.8rem; font-weight: bold; }
    .sub-title { text-align: center; color: #4B5563; font-size: 1.2rem; margin-bottom: 25px; }
    .stRadio > div { flex-direction: row; justify-content: center; }
    
    /* تنسيق فقاعات المحادثة الشبيه بالواتساب */
    .chat-container { background-color: #E5DDD5; padding: 15px; border-radius: 12px; max-height: 350px; overflow-y: auto; }
    .msg-box-admin { background-color: #DCF8C6; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: right; max-width: 80%; float: right; clear: both; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .msg-box-player { background-color: #FFFFFF; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: right; max-width: 80%; float: left; clear: both; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .msg-user { font-weight: bold; font-size: 0.85rem; color: #075E54; display: block; }
    .msg-time { font-size: 0.7rem; color: #999; text-align: left; display: block; margin-top: 3px; }
    </style>
""", unsafe_allow_html=True)

# 2. إنشاء مخزن بيانات ثابت على السيرفر للمزامنة الحقيقية بين الأجهزة
if 'global_rooms_data' not in st.session_state:
    st.session_state.global_rooms_data = {}

if 'kids_q_bank' not in st.session_state: st.session_state.kids_q_bank = []
if 'adults_q_bank' not in st.session_state: st.session_state.adults_q_bank = []
if 'manual_q_bank' not in st.session_state: st.session_state.manual_q_bank = []

def do_refresh():
    time.sleep(1.2)
    st.rerun()

# الهيدر الأساسي للمنصة
st.markdown("<div class='main-title'>🎮 منصة هيا للمسابقات | Haya-Quiz</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>الواجهة المعتمدة لإدارة المسابقات والتحكم الكامل بالبث والمحادثة الفورية</div>", unsafe_allow_html=True)
st.write("---")

# خيارات الصفحة الأولى الثلاثة الرئيسية
selected_tab = st.radio(
    "🔥 اختر نمط اللعب المفضل لديك اليوم:",
    ["🎮 إدارة مسابقة حية", "🕹️ دخول كمتسابق", "🧠 اكتشف ثقافتك"],
    index=0
)
st.write("---")

# =============================================================
# 🎮 النمط الأول: إدارة مسابقة حية (لوحة الموجه والمدير)
# =============================================================
if selected_tab == "🎮 إدارة مسابقة حية":
    
    # [الحالة أ: شاشة التجهيز الأصلية الكاملة - قبل إنشاء الغرفة]
    if 'my_active_room' not in st.session_state:
        st.subheader("🔑 التحقق البرمجي وصلاحيات الموجه")
        
        col_p, _ = st.columns([1, 2])
        with col_p:
            password_check = st.text_input("أدخل الرقم السري لفتح لوحة البث المباشر:", type="password")
            
        if password_check == "1234":
            st.success("🔓 تم فتح الصلاحيات بنجاح يا أبا عبد الإله. يمكنك الآن التحكم بالمنصة كلياً.")
            st.write("---")
            
            # الإعدادات العامة لنسخة أمس
            st.markdown("#### 🌐 إعدادات واجهة البث واللغة")
            chosen_language = st.selectbox("اللغة الرسمية للمسابقة الحالية:", ["العربية", "English"])
            
            st.markdown("#### 📂 إدارة ورفع بنك الأسئلة التفاعلي")
            tab1, tab2, tab3 = st.tabs(["📥 أسئلة الأطفال", "📥 أسئلة البالغين", "📝 إضافة سؤال يدوي"])
            
            with tab1:
                st.write("ارفع هنا ملف الأسئلة المخصص للأطفال والكواليس:")
                kids_f = st.file_uploader("اختر ملف إكسيل الأطفال (.xlsx):", type=["xlsx"], key="kids_excel")
                if kids_f:
                    try:
                        st.session_state.kids_q_bank = pd.read_excel(kids_f).to_dict(orient='records')
                        st.success(f"✅ تم تحميل واعتماد ملف الأطفال بنجاح! الإجمالي: {len(st.session_state.kids_q_bank)} سؤال.")
                    except: st.error("خطأ في بنية الملف المرفوع.")
                        
            with tab2:
                st.write("ارفع هنا ملف الأسئلة المخصص للبالغين:")
                adults_f = st.file_uploader("اختر ملف إكسيل البالغين (.xlsx):", type=["xlsx"], key="adults_excel")
                if adults_f:
                    try:
                        st.session_state.adults_q_bank = pd.read_excel(adults_f).to_dict(orient='records')
                        st.success(f"✅ تم تحميل واعتماد ملف البالغين بنجاح! الإجمالي: {len(st.session_state.adults_q_bank)} سؤال.")
                    except: st.error("خطأ في بنية الملف المرفوع.")
                        
            with tab3:
                st.write("إضافة سؤال تفاعلي فوري وكتابة الخيارات والروابط يدوياً:")
                with st.form("manual_form_new"):
                    m_title = st.text_input("نص السؤال المقترح:")
                    mo1 = st.text_input("الخيار الأول:")
                    mo2 = st.text_input("الخيار الثاني:")
                    mo3 = st.text_input("الخيار الثالث:")
                    mo4 = st.text_input("الخيار الرابع:")
                    m_correct = st.text_input("الإجابة الصحيحة تماماً:")
                    m_url = st.text_input("رابط الصورة التوضيحية للسؤال (إن وُجدت):")
                    
                    if st.form_submit_button("➕ حفظ وإدراج السؤال في المسابقة الحالي"):
                        if m_title and mo1 and m_correct:
                            st.session_state.manual_q_bank.append({
                                "السؤال": m_title, "الخيار 1": mo1, "الخيار 2": mo2, "الخيار 3": mo3, "الخيار 4": mo4,
                                "الإجابة الصحيحة": m_correct, "الصورة": m_url if m_url else None
                            })
                            st.success("🎯 تم حفظ وإدراج السؤال في الذاكرة بنجاح!")
            
            st.write("---")
            # [تعديل جديد]: تحديد عدد اللاعبين والتحكم بالعداد والأسئلة
            st.markdown("#### ⏱️ إعدادات التحكم ومحددات الغرفة الحية")
            col_cfg1, col_cfg2, col_cfg3, col_cfg4 = st.columns(4)
            with col_cfg1:
                q_src = st.selectbox("المصدر المعتمد للأسئلة:", ["أسئلة الأطفال المرفوعة", "أسئلة البالغين المرفوعة", "الأسئلة اليدوية المكتوبة"])
            with col_cfg2:
                limit_q = st.number_input("عدد الأسئلة المطلوبة في هذه الجولة:", min_value=1, max_value=100, value=10)
            with col_cfg3:
                timer_q = st.number_input("مدة عداد كل سؤال بالثواني:", min_value=5, max_value=120, value=30)
            with col_cfg4:
                # ميزة تحديد كم لاعب في اللعبة المطلوبة
                max_players_num = st.number_input("الحد الأقصى لعدد المتسابقين (اللاعبين):", min_value=1, max_value=20, value=5)
                
            st.write("---")
            if st.button("✨ تفعيل البث الحي وإنشاء غرفة المسابقة الآن"):
                current_pool = []
                if q_src == "أسئلة الأطفال المرفوعة": current_pool = st.session_state.kids_q_bank
                elif q_src == "أسئلة البالغين المرفوعة": current_pool = st.session_state.adults_q_bank
                else: current_pool = st.session_state.manual_q_bank
                    
                if not current_pool:
                    st.error("⚠️ المصدر المختار فارغ! يرجى تحميل ملف إكسيل أو كتابة أسئلة أولاً.")
                else:
                    room_code = str(random.randint(1000, 9999))
                    st.session_state.my_active_room = room_code
                    
                    # حفظ البيانات في المخزن الثابت لضمان عدم حدوث خطأ في الرقم عند الأبناء
                    st.session_state.global_rooms_data[room_code] = {
                        "players": [],
                        "max_players": max_players_num,
                        "status": "waiting",
                        "current_q_index": 0,
                        "questions": current_pool[:limit_q],
                        "duration": timer_q,
                        "language": chosen_language,
                        "chat_history": []
                    }
                    st.rerun()
        elif password_check != "":
            st.error("❌ الرقم السري غير صحيح، يرجى المحاولة مرة أخرى.")

    # [الحالة ب: الانبثاق الكامل ولوحة البث النظيفة والشات الاحترافي]
    else:
        active_room = st.session_state.my_active_room
        room_data = st.session_state.global_rooms_data.get(active_room)
        
        if room_data:
            st.markdown(f"<h2 style='color:#10B981;'>📺 لوحة البث المباشر المزامنة</h2>", unsafe_allow_html=True)
            st.info(f"🎲 رقم الغرفة الفعال لدخول الأبناء هو: **{active_room}** (بانتظار ربط شاشاتهم حالياً)")
            st.write(f"🌐 اللغة: {room_data['language']} | الأسئلة: {len(room_data['questions'])} | الحد الأقصى للاعبين: **{len(room_data['players'])}/{room_data['max_players']}**")
            st.write("---")
            
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.markdown("### 👥 المتسابقون المتصلون حياً بالمسابقة:")
                if not room_data["players"]:
                    st.warning("🔄 بانتظار دخول الأبناء بالرقم السري... الشاشة تقوم بالتحديث تلقائياً ثانية بثانية.")
                else:
                    grid = st.columns(4)
                    for idx, player in enumerate(room_data["players"]):
                        grid[idx % 4].success(f"• {player} (جاهز ✅)")
                
                st.write("---")
                if room_data["status"] == "waiting":
                    if st.button("🚀 إطلاق المسابقة وبدء البث الحي للجميع"):
                        st.session_state.global_rooms_data[active_room]["status"] = "playing"
                        st.rerun()
                elif room_data["status"] == "playing":
                    q_now = room_data["current_q_index"]
                    qs_arr = room_data["questions"]
                    
                    if q_now < len(qs_arr):
                        st.info(f"📊 السؤال الحالي المفعل للأبناء ({q_now + 1}/{len(qs_arr)}):")
                        st.markdown(f"### **{qs_arr[q_now]['السؤال']}**")
                        if qs_arr[q_now].get("الصورة") and pd.notna(qs_arr[q_now]["الصورة"]):
                            st.image(qs_arr[q_now]["الصورة"], width=300)
                        
                        if st.button("➡️ نقل شاشات الأبناء وتفعيل السؤال التالي"):
                            st.session_state.global_rooms_data[active_room]["current_q_index"] += 1
                            st.rerun()
                    else:
                        st.success("🏁 انتهت الجولة وجميع الأسئلة المحددة بنجاح!")
                        st.session_state.global_rooms_data[active_room]["status"] = "finished"
                
                st.write("---")
                if st.button("🛑 إغلاق وإنهاء المسابقة وتدمير الغرفة نهائياً"):
                    if active_room in st.session_state.global_rooms_data:
                        del st.session_state.global_rooms_data[active_room]
                    if 'my_active_room' in st.session_state:
                        del st.session_state.my_active_room
                    st.rerun()
            
            with col_right:
                st.markdown("### 💬 شات المسابقة (واتساب)")
                # صندوق المحادثة الاحترافي المطور بفقاعات الواتساب
                st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
                for msg in room_data["chat_history"]:
                    box_class = "msg-box-admin" if msg["role"] == "admin" else "msg-box-player"
                    st.markdown(f"""
                        <div class='{box_class}'>
                            <span class='msg-user'>{msg['user']}</span>
                            {msg['text']}
                            <span class='msg-time'>{msg['time']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div><br><br>", unsafe_allow_html=True)
                
                adm_input = st.text_input("اكتب رسالة سريعة للجميع:", key="adm_chat_field")
                if st.button("إرسال الشات"):
                    if adm_input:
                        now_time = datetime.now().strftime("%H:%M")
                        st.session_state.global_rooms_data[active_room]["chat_history"].append({
                            "user": "المدير (أبو صالح)", "text": adm_input, "role": "admin", "time": now_time
                        })
                        st.rerun()
                        
            do_refresh()

# =============================================================
# 🕹️ النمط الثاني: شاشة المتسابقين ودخول الأبناء (اللاعبين)
# =============================================================
elif selected_tab == "🕹️ دخول كمتسابق":
    st.markdown("### 🕹️ شاشة انضمام المتسابقين للأبناء")
    
    if 'joined_room_code' not in st.session_state:
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            in_code = st.text_input("أدخل رقم الغرفة المكون من 4 أرقام الموضح عند المدير:")
        with col_in2:
            in_name = st.text_input("أدخل اسمك الكريم للمنافسة حياً:")
            
        if st.button("🚪 دخول الغرفة التفاعلية"):
            # التحقق المستقر من وجود الغرفة في الذاكرة لمنع خطأ الرقم
            if in_code in st.session_state.global_rooms_data:
                r_obj = st.session_state.global_rooms_data[in_code]
                
                # التحقق من ميزة الحد الأقصى لعدد اللاعبين المحددة من المدير
                if len(r_obj["players"]) >= r_obj["max_players"]:
                    st.error("⚠️ عذراً! الغرفة ممتلئة بالكامل ووصلت للحد الأقصى من اللاعبين المسموح به.")
                else:
                    if in_name not in r_obj["players"]:
                        st.session_state.global_rooms_data[in_code]["players"].append(in_name)
                    st.session_state.joined_room_code = in_code
                    st.session_state.my_player_name = in_name
                    st.success("🎉 تم الاتصال والربط الحقيقي بنجاح! خلك جاهز للبث.")
                    st.rerun()
            else:
                st.error("❌ رقم الغرفة غير موجود أو تم إغلاقها من المدير. تأكد من الرقم مجدداً.")
    else:
        p_room = st.session_state.joined_room_code
        p_name = st.session_state.my_player_name
        
        if p_room in st.session_state.global_rooms_data:
            r_info = st.session_state.global_rooms_data[p_room]
            
            col_p_left, col_p_right = st.columns([2, 1])
            
            with col_p_left:
                if r_info["status"] == "waiting":
                    st.markdown(f"### 👋 أهلاً ومرحباً بك يا **{p_name}**")
                    st.info(f"⏳ تم ربط شاشتك بنجاح بالغرفة الحية رقم ({p_room}). انتظر حتى يضغط الموجه على زر انطلاق المسابقة لتظهر الأسئلة فوراً.")
                elif r_info["status"] == "playing":
                    idx_q = r_info["current_q_index"]
                    qs_list = r_info["questions"]
                    
                    if idx_q < len(qs_list):
                        st.markdown(f"### ❓ السؤال رقم {idx_q + 1} من {len(qs_list)}")
                        st.markdown(f"## **{qs_list[idx_q]['السؤال']}**")
                        
                        # ظهور الصور للأبناء بشكل ممتاز وكامل ومطابق لأمس
                        if qs_list[idx_q].get("الصورة") and pd.notna(qs_list[idx_q]["الصورة"]):
                            st.image(qs_list[idx_q]["الصورة"], use_container_width=True)
                            
                        opts = [str(qs_list[idx_q]["الخيار 1"]), str(qs_list[idx_q]["الخيار 2"]), str(qs_list[idx_q]["الخيار 3"]), str(qs_list[idx_q]["الخيار 4"])]
                        ans_chosen = st.radio("اختر إجابتك الصحيحة الحين بسرعة قبل نهاية الوقت:", opts, key=f"p_choice_{idx_q}")
                        
                        st.warning(f"⏳ الوقت المخصص لعداد السؤال: {r_info['duration']} ثانية.")
                        
                        if st.button("✔️ اعتماد الإجابة النهائية للسؤال"):
                            if ans_chosen == str(qs_list[idx_q]["الإجابة الصحيحة"]):
                                st.balloons()
                                st.success("🎉 كفووو يا بطل! إجابة صحيحة وممتازة 🥳")
                            else:
                                st.error(f"💔 للأسف إجابة خاطئة! ركز في القادم. الإجابة الصحيحة هي: {qs_list[idx_q]['الإجابة الصحيحة']}")
                    else:
                        st.success("🏁 كفو يا أبطال! انتهت الأسئلة وفي انتظار النتيجة النهائية من الموجه.")
                elif r_info["status"] == "finished":
                    st.success("🏆 تم إنهاء المسابقة بالكامل بنجاح من المدير. بيّض الله وجوهكم.")
            
            with col_p_right:
                st.markdown("### 💬 شات المسابقة (واتساب)")
                st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
                for msg in r_info["chat_history"]:
                    box_class = "msg-box-admin" if msg["role"] == "admin" else "msg-box-player"
                    st.markdown(f"""
                        <div class='{box_class}'>
                            <span class='msg-user'>{msg['user']}</span>
                            {msg['text']}
                            <span class='msg-time'>{msg['time']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div><br><br>", unsafe_allow_html=True)
                
                p_input = st.text_input("اكتب رسالة للموجه:", key="p_chat_field")
                if st.button("إرسال الرسالة"):
                    if p_input:
                        now_time = datetime.now().strftime("%H:%M")
                        st.session_state.global_rooms_data[p_room]["chat_history"].append({
                            "user": p_name, "text": p_input, "role": "player", "time": now_time
                        })
                        st.rerun()
            
            do_refresh()
        else:
            st.warning("🛑 قام الموجه بإغلاق وتدمير الغرفة الحالية لانتهاء المسابقة.")
            if st.button("العودة لشاشة الدخول الرئيسية"):
                if 'joined_room_code' in st.session_state: del st.session_state.joined_room_code
                st.rerun()

# =============================================================
# 🧠 النمط الثالث: اكتشف ثقافتك (التسابق الفردي وتطوير المعلومات)
# =============================================================
else:
    st.markdown("### 🧠 نمط: اكتشف ثقافتك وتحدي المعلومات العامة")
    st.write("هنا يمكنك اللعب الفردي واختبار معلوماتك العامة وتطوير ثقافتك بدون موجه أو غرف بث حي.")
    st.write("---")
    
    cultural_bank = [
        {"س": "ما هو أول مسجد أُسس في الإسلام؟", "ج": "مسجد قباء في المدينة المنورة"},
        {"س": "كم عدد كواكب المجموعة الشمسية المعتمدة رسمياً؟", "ج": "8 كواكب"},
        {"س": "ما هي عاصمة المملكة العربية السعودية؟", "ج": "الرياض"}
    ]
    for idx, item in enumerate(cultural_bank):
        st.markdown(f"#### 💡 التحدي الثقافي رقم {idx + 1}:")
        st.info(item["س"])
        if st.button(f"👁️ كشف الإجابة الصحيحة للتحدي {idx + 1}", key=f"cult_btn_{idx}"):
            st.success(f"الجواب الصحيح: {item['ج']}")
        st.write("---")
