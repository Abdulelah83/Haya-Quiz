import streamlit as st
import os
import json
import random
import time
from datetime import datetime
import pandas as pd

# 1. إعدادات الهوية البصرية والألوان الجاذبة الفخمة
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
    
    /* تصميم الرسائل الواردة */
    .message-box {
        background-color: #F3F4F6;
        border-right: 5px solid #4F46E5;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    
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

# 2. إدارة ملفات التخزين المحلي
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

# 3. عدّاد زوار الموقع
if 'visitor_counted' not in st.session_state:
    visitors = load_local_data("visitors.json", {"total_count": 0, "history": {}})
    visitors["total_count"] += 1
    
    # تسجيل تاريخ الزيارة للرسم البياني
    today_str = datetime.now().strftime("%Y-%m-%d")
    visitors["history"][today_str] = visitors["history"].get(today_str, 0) + 1
    
    save_local_data("visitors.json", visitors)
    st.session_state.visitor_counted = True

# تهيئة متغيرات الجلسة
if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False
if 'rooms' not in st.session_state: st.session_state.rooms = {}

# تحميل بنك الأسئلة والمخزون اليدوي
manual_questions = load_local_data("manual_questions.json", [])

# 4. الشريط العلوي الثابت
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

# عرض المحتوى بناءً على الصفحة الحالية
if st.session_state.curr_page == "home":
    st.markdown("<h1 class='main-title'>منصة هيا للمسابقات العائلية 🎯</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>المتعة والثقافة في مكان واحد للأبناء والآباء</p>", unsafe_allow_html=True)
    
    col_left_img, col_right_content = st.columns([1, 2])
    with col_left_img:
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

elif st.session_state.curr_page == "contact_mode":
    st.markdown("### 📞 تواصل معنا وإبداء رأيك")
    with st.form("contact_form", clear_on_submit=True):
        p_name = st.text_input("اسمك الكريم:")
        p_msg = st.text_area("اكتب رسالتك أو ملاحظتك هنا:")
        if st.form_submit_button("📤 إرسال الرسالة الآن"):
            if p_name and p_msg:
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

# 👑 لوحة تحكم الموجه والمطور (محدثة بالكامل)
elif st.session_state.curr_page == "admin_mode":
    st.markdown("<h2 style='text-align:center;'>👑 لوحة تحكم مالك المنصة</h2>", unsafe_allow_html=True)
    
    # قفل الأمان الرقمي (🔐 تأمين حساب المالك)
    if not st.session_state.admin_logged_in:
        col_login, _ = st.columns([1, 2])
        with col_login:
            st.write("### 🔒 تسجيل الدخول لمالك التطبيق")
            admin_password = st.text_input("أدخل الرقم السري القوي للمالك:", type="password")
            if st.button("🔓 فتح لوحة التحكم"):
                # الرقم السري القوي والمحدث الخاص بك
                if admin_password == "Abdulelah@2026":
                    st.session_state.admin_logged_in = True
                    st.success("تم التحقق بنجاح! جاري فتح اللوحة...")
                    st.rerun()
                else:
                    st.error("❌ الرقم السري غير صحيح، حاول مرة أخرى.")
    else:
        # زر تسجيل الخروج الثابت (🚪 لوق اوت)
        col_out1, col_out2 = st.columns([5, 1])
        with col_out2:
            if st.button("🚪 تسجيل الخروج"):
                st.session_state.admin_logged_in = False
                st.rerun()
        
        st.write("---")
        
        # تقسيم الشاشة: يمين (التحكم والإحصائيات)، يسار (صندوق الوارد)
        col_main_admin, col_inbox_side = st.columns([2, 1])
        
        with col_main_admin:
            st.markdown("### 📊 إحصائيات زوار الموقع")
            visitors_data = load_local_data("visitors.json", {"total_count": 0, "history": {}})
            st.metric(label="إجمالي عدد الزوار الحقيقيين", value=f"{visitors_data['total_count']} زائر")
            
            # عرض تشارت الزيارات (📈 تشارت الإحصائيات)
            if visitors_data["history"]:
                st.write("📈 منحنى الزيارات اليومي للمنصة:")
                df_visits = pd.DataFrame(list(visitors_data["history"].items()), columns=["التاريخ", "الزيارات"])
                st.line_chart(df_visits.set_index("التاريخ"))
            
            st.write("---")
            
            # 📝 كتابة سؤال يدوي وحفظه فوراً
            st.markdown("### 📝 إضافة سؤال يدوي للمتسابقين")
            with st.form("manual_q_form", clear_on_submit=True):
                m_question = st.text_input("نص السؤال اليدوي:")
                opt1 = st.text_input("الخيار 1 (الإجابة الصحيحة دائماً هنا برمجياً):")
                opt2 = st.text_input("الخيار 2:")
                opt3 = st.text_input("الخيار 3:")
                opt4 = st.text_input("الخيار 4:")
                
                if st.form_submit_button("➕ حفظ وإدراج السؤال"):
                    if m_question and opt1 and opt2 and opt3 and opt4:
                        manual_questions.append({
                            "السؤال": m_question,
                            "الخيار 1 - الصحيح": opt1,
                            "الخيار 2": opt2,
                            "الخيار 3": opt3,
                            "الخيار 4": opt4
                        })
                        save_local_data("manual_questions.json", manual_questions)
                        st.success(f"🎯 تم حفظ السؤال بنجاح! إجمالي الأسئلة اليدوية الحين: {len(manual_questions)}")
                    else:
                        st.warning("⚠️ يرجى ملء السؤال وجميع الخيارات الأربعة.")
                        
        # 📬 صندوق وارد "تواصل معنا" (يسار الصفحة بعد إدخال الرقم السري)
        with col_inbox_side:
            st.markdown("### 📬 صندوق الوارد (رسائل الزوار)")
            messages_list = load_local_data("messages.json", [])
            
            if not messages_list:
                st.info("📭 لا توجد رسائل جديدة في صندوق الوارد حالياً.")
            else:
                for idx, msg in enumerate(reversed(messages_list)):
                    st.markdown(f"""
                        <div class='message-box'>
                            <strong>👤 المرسل:</strong> {msg['name']}<br>
                            <strong>📅 التاريخ:</strong> {msg['time']}<br>
                            <p style='margin-top:5px; color:#374151;'>💬 {msg['message']}</p>
                        </div>
                    """, unsafe_allow_html=True)

elif st.session_state.curr_page == "player_mode":
    st.info("🕹️ واجهة المتسابقين والأبناء - قيد التحديث للتزامن السريع والعداد الآلي...")
elif st.session_state.curr_page == "culture_mode":
    st.info("🧠 نمط اختبر نفسك الفردي - قيد الضبط والتعطيل المؤقت لحين رفع ملف الكبار...")

# 5. التوقيع الثابت والحقوق أسفل كل صفحات المنصة بالعربي والإنجليزي
st.markdown("<div class='footer-text'>تطوير عبد الإله العنزي | Developed by Abdulelah Al-Anzi</div>", unsafe_allow_html=True)
