import streamlit as st
import os
import json
import random
import time
from datetime import datetime

# 1. إعدادات الهوية البصرية والألوان الجاذبة الفخمة (🎨 تحسين الجاذبية البصرية)
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz Pro", 
    page_icon="🎮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص التصميم عبر CSS ليصبح حيوي ومناسب للأطفال والكبار
st.markdown("""
    <style>
    /* ألوان حيوية متدرجة للخلفية والعناوين */
    .main-title { text-align: center; color: #4F46E5; font-size: 3rem; font-weight: bold; margin-bottom: 5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }
    .sub-title { text-align: center; color: #6B7280; font-size: 1.3rem; margin-bottom: 30px; }
    
    /* تنسيق أزرار الراديو والخيارات */
    .stRadio > div { flex-direction: row; justify-content: center; gap: 15px; }
    
    /* تصميم أزرار المنصة بشكل جذاب */
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
    
    /* توقيع أسفل الصفحة الثابت والفخم */
    .footer-text { 
        text-align: center; 
        color: #9CA3AF; 
        font-size: 1rem; 
        font-weight: 500; 
        padding: 20px 0; 
        border-top: 1px solid #E5E7EB;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. إدارة ملفات التخزين المحلي لضمان بقاء البيانات الدائمة في السيرفر (💾 التخزين الدائم)
DATA_DIR = "database_local"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def load_local_data(filename, default_value):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_value

def save_local_data(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 3. محرك العداد الذكي لرصد الزوار الحقيقيين (📊 عدّاد زوار الموقع)
if 'visitor_counted' not in st.session_state:
    visitors = load_local_data("visitors.json", {"total_count": 0})
    visitors["total_count"] += 1
    save_local_data("visitors.json", visitors)
    st.session_state.visitor_counted = True

# تهيئة المتغيرات الأساسية لجلسة المستخدم
if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False

# 4. الشريط العلوي الثابت للمنصة لسهولة التنقل
navbar_cols = st.columns([1, 4, 1])
with navbar_cols[1]:
    col_nav1, col_nav2 = st.columns(2)
    if col_nav1.button("🏠 الصفحة الرئيسية", use_container_width=True):
        st.session_state.curr_page = "home"
        st.rerun()
    if col_nav2.button("📞 تواصل معنا", use_container_width=True):
        st.session_state.curr_page = "contact_mode"
        st.rerun()

st.write("---")

# 5. عرض محتوى الصفحة بناءً على خيار المستخدم
if st.session_state.curr_page == "home":
    st.markdown("<h1 class='main-title'>منصة هيا للمسابقات العائلية 🎯</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>المتعة والثقافة في مكان واحد للأبناء والآباء</p>", unsafe_allow_html=True)
    
    col_left_img, col_right_content = st.columns([1, 2])
    with col_left_img:
        # التأكد من وجود الصورة أو وضع مساحة بديلة جذابة
        if os.path.exists("my_kids.png"):
            st.image("my_kids.png", use_container_width=True)
        else:
            st.info("🎮 جاهزون لإطلاق التحدي الحماسي!")
            
    with col_right_content:
        st.write("### اختر نمط اللعب المفضل لديك للحين:")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            if st.button("👑 لوحة تحكم الموجه", use_container_width=True): 
                st.session_state.curr_page = "admin_mode"
                st.rerun()
        with col_m2:
            if st.button("🎮 انضم كمتسابق", use_container_width=True): 
                st.session_state.curr_page = "player_mode"
                st.rerun()
        with col_m3:
            if st.button("🕹️ تحدي اختبر نفسك", use_container_width=True): 
                st.session_state.curr_page = "culture_mode"
                st.rerun()

# صفحة تواصل معنا (📬 إرسال الرسائل وحفظها)
elif st.session_state.curr_page == "contact_mode":
    st.markdown("### 📞 تواصل معنا وإبداء رأيك")
    with st.form("contact_form", clear_on_submit=True):
        p_name = st.text_input("اسمك الكريم:")
        p_msg = st.text_area("اكتب رسالتك أو ملاحظتك هنا:")
        if st.form_submit_button("📤 إرسال الرسالة الآن"):
            if p_name and p_msg:
                # تحميل الرسائل القديمة وإضافة الجديدة لها لتخزينها دائمياً
                current_messages = load_local_data("messages.json", [])
                current_messages.append({
                    "name": p_name,
                    "message": p_msg,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_local_data("messages.json", current_messages)
                st.success("🎉 تم إرسال رسالتك بنجاح وسيتطلع عليها مالك المنصة فوراً!")
            else:
                st.warning("⚠️ يرجى ملء الاسم ونص الرسالة قبل الإرسال.")

# الأنماط الأخرى سنقوم باستدعائها وربطها تباعاً ليبقى الكود نظيفاً
elif st.session_state.curr_page == "admin_mode":
    st.info("⚙️ شاشة الموجه ولوحة التحكم - قيد التحديث الفوري مع الأزرار المؤمنة والتشارتات...")
elif st.session_state.curr_page == "player_mode":
    st.info("🕹️ واجهة المتسابقين والأبناء - قيد التحديث للتزامن السريع والعداد الآلي...")
elif st.session_state.curr_page == "culture_mode":
    st.info("🧠 نمط اختبر نفسك الفردي - قيد الضبط والتعطيل المؤقت لحين رفع ملف الكبار...")

# 6. التوقيع الثابت والحقوق أسفل كل صفحات المنصة (✍️ توقيع أسفل الصفحة)
st.markdown("<div class='footer-text'>تطوير عبد الإله العنزي | Developed by Abdulelah Al-Anzi</div>", unsafe_allow_html=True)
