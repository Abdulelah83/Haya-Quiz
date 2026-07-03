import streamlit as st
import pandas as pd
import io
import random
import os

# إعداد الصفحة وتثبيت الهوية الرسمية (مسابقات هيا)
st.set_page_config(page_title="مسابقات هيا 🎯", page_icon="🎯", layout="wide")

# إدارة الحالة البرمجية للموقع (State Management)
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'kids_questions' not in st.session_state:
    st.session_state.kids_questions = None
if 'adults_questions' not in st.session_state:
    st.session_state.adults_questions = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'contact_messages' not in st.session_state:
    st.session_state.contact_messages = []
if 'show_contact_form' not in st.session_state:
    st.session_state.show_contact_form = False

# --- خيار تحويل اللغة في أعلى القائمة الجانبية ---
st.sidebar.markdown("### 🌐 Language / اللغة")
lang = st.sidebar.selectbox("اختر لغة الموقع:", ["العربية 🇸🇦", "English 🇺🇸"])
is_ar = lang == "العربية 🇸🇦"

# قاموس النصوص الكامل للترجمة الحية (تم تصحيح كلمة الأبطال هنا)
txt = {
    "title": "🎯 منصة مسابقات هيا العائلية" if is_ar else "🎯 Haya Family Quiz Platform",
    "sub": "أهلاً بالأبطال الغاليين.. جاهزين للتحدي والمنافسة؟ 🔥" if is_ar else "Welcome to the Champions! Ready for the big challenge? 🔥",
    "admin_btn": "أنشئ مسابقة الآن" if is_ar else "Create Quiz Now",
    "admin_head": "👑 إدارة مسابقة حية" if is_ar else "👑 Live Quiz Management",
    "admin_desc": "أنشئ غرفة مسابقة جديدة، وتحكم بالأسئلة والوقت وتحدى أصدقائك وعائلتك." if is_ar else "Create a new quiz room, control time and questions, and challenge your family.",
    "player_head": "🎮 دخول كمتسابق" if is_ar else "🎮 Join as Competitor",
    "player_desc": "أدخل الرمز السري الممنوح لك من مدير المسابقة وانضم للتحدي فوراً." if is_ar else "Enter the secret room code given by the manager and join the challenge immediately.",
    "player_btn": "انضم كمتسابق" if is_ar else "Join as Competitor",
    "single_head": "🕹️ التسابق الفردي" if is_ar else "🕹️ Single Player Mode",
    "single_desc": "اختبر معلوماتك بشكل سريع بمفردك واكتشف مستواك الحقيقي." if is_ar else "Quickly test your knowledge alone and discover your true level.",
    "single_btn": "ابدأ اللعب الفردي" if is_ar else "Start Single Player",
    "contact_btn": "📬 تواصل معنا" if is_ar else "📬 Contact Us",
    "contact_form_head": "### ✉️ أرسل تفاصيل طلبك للإدارة" if is_ar else "### ✉️ Send Your Details to Admin",
    "name_label": "الاسم الكريم:" if is_ar else "Your Name:",
    "contact_label": "البريد الإلكتروني أو رقم التواصل:" if is_ar else "Email or Phone:",
    "msg_label": "نص رسالتك:" if is_ar else "Your Message:",
    "send_btn": "🚀 إرسال الرسالة" if is_ar else "🚀 Send Message",
    "back_btn": "🔙 العودة للرئيسية" if is_ar else "🔙 Back to Home",
    "logout": "🚪 تسجيل الخروج" if is_ar else "🚪 Logout",
    "admin_title": "### ⚙️ لوحة تحكم النظام (أدمن)" if is_ar else "### ⚙️ System Admin Panel",
    "kids_section": "#### 👶 قسم أسئلة الأطفال" if is_ar else "#### 👶 Kids Questions Section",
    "adults_section": "#### 🧔 قسم أسئلة الكبار" if is_ar else "#### 🧔 Adults Questions Section",
    "upload_kids": "📥 رفع إكسيل الأطفال" if is_ar else "📥 Upload Kids Excel",
    "upload_adults": "📥 رفع إكسيل الكبار" if is_ar else "📥 Upload Adults Excel",
    "delete_btn": "🗑️ حذف الملف" if is_ar else "🗑️ Delete File",
    "manual_head": "#### ✍️ إضافة سؤال يدوي" if is_ar else "#### ✍️ Add Manual Question",
    "save_q_btn": "➕ حفظ السؤال في النظام" if is_ar else "➕ Save Question"
}

# تخصيص الألوان وإضافة تنسيق البانر الطولي الاحترافي (CSS)
st.markdown(f"""
    <style>
    .main {{ background-color: #F8F9FA; }}
    h1, h2, h3 {{ color: #1E3A8A; font-family: 'Cairo', sans-serif; text-align: center; }}
    .welcome-text {{ text-align: center; font-size: 24px; color: #D97706; font-weight: bold; margin-top: 15px; margin-bottom: 20px; }}
    
    /* تصميم الصورة بشكل طولي (بانر عمودي) ممتد على جانب الصفحة */
    .vertical-banner {{
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        border: 3px solid #F59E0B;
        margin-bottom: 25px;
    }}
    .vertical-banner img {{
        width: 100%;
        max-height: 500px;
        object-fit: cover;
    }}

    .stButton>button {{
        background-color: #F59E0B;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        padding: 10px 24px;
        width: 100%;
    }}
    .stButton>button:hover {{ background-color: #D97706; color: white; }}
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #1E3A8A;
        color: white;
        text-align: center;
        padding: 8px;
        font-family: 'Cairo', sans-serif;
        font-size: 14px;
        z-index: 100;
    }}
    </style>
    """, unsafe_allow_html=True)

def show_footer():
    st.markdown("""
        <div class="footer">
            تطوير: عبدالإله العنزي | Developed by Abdulelah Al-Enazi 💻
        </div>
        """, unsafe_allow_html=True)

# --- الصفحة الرئيسية ---
def show_home():
    # تقسيم الصفحة بشكل طولي احترافي: عمود نحيف للصورة الطولية وعمود عريض للمحتوى
    col_layout1, col_layout2 = st.columns([1, 3])
    
    with col_layout1:
        # فحص وجود الصورة الحقيقية لعرضها ممتدة طولياً
        if os.path.exists("my_kids.png"):
            st.markdown('<div class="vertical-banner">', unsafe_allow_html=True)
            st.image("my_kids.png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        elif os.path.exists("my_kids.jpg"):
            st.markdown('<div class="vertical-banner">', unsafe_allow_html=True)
            st.image("my_kids.jpg", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="vertical-banner">', unsafe_allow_html=True)
            st.image("https://img.freepik.com/free-vector/children-quiz-show-concept-illustration_114360-22285.jpg", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    with col_layout2:
        st.title(txt["title"])
        st.markdown(f'<div class="welcome-text">{txt["sub"]}</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader(txt["admin_head"])
            st.write(txt["admin_desc"])
            if st.button(txt["admin_btn"]):
                st.session_state.page = 'create_quiz'
                st.rerun()
                
        with col2:
            st.subheader(txt["player_head"])
            st.write(txt["player_desc"])
            if st.button(txt["player_btn"]):
                st.session_state.page = 'join_quiz'
                st.rerun()
                
        with col3:
            st.subheader(txt["single_head"])
            st.write(txt["single_desc"])
            if st.button(txt["single_btn"]):
                st.session_state.page = 'single_player'
                st.rerun()

    st.markdown("---")
    
    if st.button(txt["contact_btn"]):
        st.session_state.show_contact_form = not st.session_state.show_contact_form
        st.rerun()
        
    if st.session_state.show_contact_form:
        st.markdown(txt["contact_form_head"])
        with st.form(key='contact_form', clear_on_submit=True):
            c_name = st.text_input(txt["name_label"])
            c_email = st.text_input(txt["contact_label"])
            c_msg = st.text_area(txt["msg_label"])
            submit_msg = st.form_submit_button(txt["send_btn"])
            
            if submit_msg:
                if c_name and c_msg:
                    st.session_state.contact_messages.append({"الاسم": c_name, "التواصل": c_email, "الرسالة": c_msg})
                    st.success("تم إرسال رسالتك بنجاح! ✅" if is_ar else "Message sent successfully! ✅")
                else:
                    st.error("الرجاء تعبئة الحقول المطلوبة." if is_ar else "Please fill required fields.")

# --- لوحة تحكم النظام (أدمن) ---
def show_super_admin():
    st.sidebar.markdown(txt["admin_title"])
    
    if not st.session_state.admin_logged_in:
        admin_password = st.sidebar.text_input("رمز صلاحيات النظام" if is_ar else "Admin Password", type="password", key="admin_pass_input")
        if st.sidebar.button("🔐 تسجيل الدخول" if is_ar else "🔐 Login"):
            if admin_password == "Abdulelah2026":
                st.session_state.admin_logged_in = True
                st.sidebar.success("تم التحقق بنجاح! 🎉" if is_ar else "Verified! 🎉")
                st.rerun()
            else:
                st.sidebar.error("الرمز السري خاطئ! 🛑" if is_ar else "Wrong code! 🛑")
                
    else:
        st.sidebar.success("🔓 وضع المطور عبدالإله نشط" if is_ar else "🔓 Developer Abdulelah Active")
        
        if st.sidebar.button(txt["logout"]):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        st.sidebar.markdown("---")
        
        # صندوق الرسائل
        st.sidebar.markdown("#### 📥 صندوق الرسائل" if is_ar else "#### 📥 Inbox")
        if not st.session_state.contact_messages:
            st.sidebar.info("صندوق الوارد فارغ حالياً." if is_ar else "Inbox is empty.")
        else:
            for idx, msg in enumerate(st.session_state.contact_messages):
                with st.sidebar.expander(f"✉️ من: {msg['الاسم']}"):
                    st.write(f"**التواصل:** {msg['التواصل']}")
                    st.write(f"**الرسالة:** {msg['الرسالة']}")
                    
        st.sidebar.markdown("---")
        
        # 👶 قسم الأطفال
        st.sidebar.markdown(txt["kids_section"])
        if st.session_state.kids_questions is None:
            uploaded_kids = st.sidebar.file_uploader(txt["upload_kids"], type=["xlsx"], key="kids_up")
            if uploaded_kids is not None:
                st.session_state.kids_questions = pd.read_excel(uploaded_kids)
                st.sidebar.success("تم التفعيل! ✅")
                st.rerun()
        else:
            st.sidebar.markdown(f"<div style='background-color: #E0F2FE; padding: 8px; border-radius: 5px; color: #0369A1; font-weight: bold;'>📋 يحتوي على: {len(st.session_state.kids_questions)} سؤال</div>", unsafe_allow_html=True)
            if st.sidebar.button(txt["delete_btn"], key="del_kids"):
                st.session_state.kids_questions = None
                st.rerun()

        st.sidebar.markdown("---")

        # 🧔 قسم الكبار
        st.sidebar.markdown(txt["adults_section"])
        if st.session_state.adults_questions is None:
            uploaded_adults = st.sidebar.file_uploader(txt["upload_adults"], type=["xlsx"], key="adults_up")
            if uploaded_adults is not None:
                st.session_state.adults_questions = pd.read_excel(uploaded_adults)
                st.sidebar.success("تم التفعيل! ✅")
                st.rerun()
        else:
            st.sidebar.markdown(f"<div style='background-color: #FEF3C7; padding: 8px; border-radius: 5px; color: #B45309; font-weight: bold;'>📋 يحتوي على: {len(st.session_state.adults_questions)} سؤال</div>", unsafe_allow_html=True)
            if st.sidebar.button(txt["delete_btn"], key="del_adults"):
                st.session_state.adults_questions = None
                st.rerun()

        st.sidebar.markdown("---")
        
        # ✍️ قسم إضافة سؤال يدوي
        st.sidebar.markdown(txt["manual_head"])
        with st.sidebar.form(key='manual_question_form'):
            q_type = st.selectbox("الفئة المستهدفة:" if is_ar else "Category:", ["الأطفال 👶", "البالغين 🧔"])
            q_cat = st.text_input("التصنيف (دين، علوم...):" if is_ar else "Classification:")
            q_age = st.text_input("العمر المناسب (مثال: 8-10):" if is_ar else "Suitable Age:", value="عام")
            q_text = st.text_area("نص السؤال:" if is_ar else "Question Text:")
            q_ans = st.text_input("الخيار 1 (الجواب الصحيح):" if is_ar else "Option 1 (Correct Answer):")
            q_wrong1 = st.text_input("الخيار 2 (خاطئ):" if is_ar else "Option 2 (Wrong):")
            q_wrong2 = st.text_input("الخيار 3 (خاطئ):" if is_ar else "Option 3 (Wrong):")
            q_wrong4 = st.text_input("الخيار 4 (خاطئ):" if is_ar else "Option 4 (Wrong):")
            
            submit_button = st.form_submit_button(label=txt["save_q_btn"])
            
            if submit_button:
                if q_text and q_ans:
                    new_row = {
                        "رقم": random.randint(1000, 9999), "التصنيف": q_cat, "العمر المناسب": q_age,
                        "السؤال": q_text, "الخيار 1 - الصحيح": q_ans, "الخيار 2": q_wrong1,
                        "الخيار 3": q_wrong2, "الخيار 4": q_wrong4, "ملاحظة": "إضافة يدوية"
                    }
                    new_df = pd.DataFrame([new_row])
                    
                    if "الأطفال" in q_type:
                        if st.session_state.kids_questions is None: st.session_state.kids_questions = new_df
                        else: st.session_state.kids_questions = pd.concat([st.session_state.kids_questions, new_df], ignore_index=True)
                    else:
                        if st.session_state.adults_questions is None: st.session_state.adults_questions = new_df
                        else: st.session_state.adults_questions = pd.concat([st.session_state.adults_questions, new_df], ignore_index=True)
                            
                    st.sidebar.success("تم حفظ السؤال!" if is_ar else "Question Saved!")
                    st.rerun()

# --- صفحة إنشاء مسابقة ---
def show_create_quiz():
    st.header(txt["admin_head"])
    col1, col2 = st.columns(2)
    with col1:
        kids_label = "أسئلة أطفال 👶" if st.session_state.kids_questions is not None else "أسئلة أطفال 👶 (غير مفعّل)"
        adults_label = "أسئلة بالغين 🧔" if st.session_state.adults_questions is not None else "أسئلة بالغين 🧔 (غير مفعّل)"
        
        target_group = st.radio("الفئة المستهدفة للعب:" if is_ar else "Target Group:", [kids_label, adults_label])
        num_players = st.number_input("عدد المتسابقين الحاضرين:" if is_ar else "Number of Players:", min_value=1, max_value=20, value=5)
        num_questions = st.number_input("عدد أسئلة الجولة:" if is_ar else "Number of Questions:", min_value=5, max_value=50, value=10)
    
    with col2:
        time_per_question = st.slider("الوقت المتاح لكل سؤال (بالثواني):" if is_ar else "Time per question:", min_value=5, max_value=30, value=12)
        points_per_question = st.number_input("الدرجة المستحقة لكل سؤال:" if is_ar else "Points per question:", min_value=1, max_value=50, value=10)
        
    if st.button("🎲 توليد الغرفة" if is_ar else "🎲 Generate Room"):
        if "غير مفعّل" in target_group:
            st.error("❌ لا يمكن بدء المسابقة لعدم وجود ملف مرفوع!")
        else:
            room_code = random.randint(1000, 9999)
            st.success(f"رمز الغرفة الرئيسي: {room_code}" if is_ar else f"Main Room Code: {room_code}")
            
    if st.button(txt["back_btn"]):
        st.session_state.page = 'home'
        st.rerun()

# --- صفحة انضمام المتسابق ---
def show_join_quiz():
    st.header(txt["player_head"])
    player_name = st.text_input("اكتب اسمك الكريم:" if is_ar else "Enter Your Name:")
    player_code = st.text_input("أدخل الرمز السري:" if is_ar else "Enter Secret Code:")
    
    if st.button("🚪 دخول الغرفة" if is_ar else "🚪 Enter Room"):
        if player_name and player_code:
            st.balloons()
            st.success(f"مرحباً {player_name}.. شد حيلك الحين تبدأ المنافسة 😂" if is_ar else f"Welcome {player_name}! Get ready to compete 😂")
            
    if st.button(txt["back_btn"]):
        st.session_state.page = 'home'
        st.rerun()

# --- صفحة اللعب الفردي ---
def show_single_player():
    st.header(txt["single_head"])
    if st.session_state.kids_questions is None:
        st.warning("يرجى رفع ملف أسئلة الأطفال أولاً." if is_ar else "Please upload kids questions file first.")
    else:
        if is_ar:
            st.info("السؤال: ما هو الكوكب الأقرب إلى الشمس؟")
            ans = st.radio("اختر إجابتك:", ["الأرض", "عطارد", "المريخ", "المشتري"])
        else:
            st.info("Question: Which planet is closest to the Sun?")
            ans = st.radio("Choose answer:", ["Earth", "Mercury", "Mars", "Jupiter"])
            
        if st.button("تأكيد الإجابة" if is_ar else "Confirm Answer"):
            if ans in ["عطارد", "Mercury"]: st.success("إجابة صحيحة! ممتاز 🌟" if is_ar else "Correct Answer! Awesome 🌟")
            else: st.error("إجابة خاطئة!" if is_ar else "Wrong Answer!")
                
    if st.button(txt["back_btn"]):
        st.session_state.page = 'home'
        st.rerun()

# --- التوجيه البرمجي الرئيسي للواجهات ---
show_super_admin()

if st.session_state.page == 'home': show_home()
elif st.session_state.page == 'create_quiz' : show_create_quiz()
elif st.session_state.page == 'join_quiz': show_join_quiz()
elif st.session_state.page == 'single_player': show_single_player()

show_footer()