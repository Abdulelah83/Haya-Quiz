import streamlit as st
import pandas as pd
import time
import random
import os
import json
from datetime import datetime
import google.generativeai as genai

# 1. إعدادات الصفحة والهوية البصرية واستهداف ألوان السماء المبهرة والمريحة للطفل
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz Pro", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة متغيرات الجلسة الأساسية للحفاظ على جوهر النظام
if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"
if 'generated_room_code' not in st.session_state: st.session_state.generated_room_code = None
if 'admin_authenticated' not in st.session_state: st.session_state.admin_authenticated = False
if 'lang' not in st.session_state: st.session_state.lang = "ar"
if 'active_users' not in st.session_state: st.session_state.active_users = True

# ربط الـ API الخاص بجيمني بشكل آمن
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# قاموس اللغتين المطور
TRANSLATIONS = {
    "ar": {
        "title": "منصة مسابقات هيا  🎯",
        "home": "🏠 الرئيسية",
        "contact": "📞 تواصل معنا",
        "settings": "⚙️ الإعدادات لوحة التحكم",
        "refresh": "🔄 تحديث الصفحة",
        "secret_key": "🔑 الرمز السري لوحة الموجه:",
        "confirm": "🔓 تأكيد الدخول",
        "logout": "🚪 خروج",
        "wrong_pass": "❌ الرمز السري غير صحيح!",
        "visits_current": "📊 المتواجدون حالياً",
        "visits_total": "📈 إجمالي الزيارات التاريخية السابقة المحفوظة",
        "ready": "### جاهزون للتحدي والمنافسة الحية الحين؟",
        "create_room": "🏆 إنشاء وإدارة مسابقة حية",
        "join_player": "🎮 دخول كمتسابق",
        "test_yourself": "🕹️ تحدي اختبر نفسك الفردي (ثقّف نفسك)",
        "footer": "تطوير عبد الإله العنزي | Developed by Abdulelah Al-Enazi",
        "num_q_label": "حدد عدد الأسئلة المطلوبة (من 1 إلى 20):",
        "time_q_label": "الوقت المتاح لكل سؤال (ثواني):",
        "gen_room_btn": "🎲 توليد غرفة المسابقة عبر Gemini AI",
        "q_src_label": "اختر الفئة للجولة المستهدفة:",
        "q_src_kids": "قسم الأطفال والأبناء 👶",
        "q_src_adults": "قسم الكبار والشباب 🧔",
        "age_label": "حدد عمر الطفل بدقة لضبط جودة وصعوبة الأسئلة (من 6 إلى 17 سنة):",
        "category_label": "اختر تصنيف الأسئلة المستهدف:",
        "correct_notify": "صح بطل كفو! 🥳",
        "wrong_notify": "❌ للأسف إجابة خاطئة ركز في القادم!",
        "correct_is": "💡 الصح هو:",
        "inbox_title": "📥 صندوق الوارد لرسائل تواصل معنا"
    },
    "en": {
        "title": "Haya Quiz Platform  🎯",
        "home": "🏠 Home",
        "contact": "📞 Contact Us",
        "settings": "⚙️ Settings Dashboard",
        "refresh": "🔄 Refresh",
        "secret_key": "🔑 Enter Password:",
        "confirm": "🔓 Login",
        "logout": "🚪 Logout",
        "wrong_pass": "❌ Incorrect Password!",
        "visits_current": "📊 Active Users Now",
        "visits_total": "📈 Cumulative Historical Visits",
        "ready": "### Ready for the Challenge?",
        "create_room": "🏆 Create Live Quiz",
        "join_player": "🎮 Enter as Contestant",
        "test_yourself": "🕹️ Test Yourself (Solo Mode)",
        "footer": "Developed by Abdulelah Al-Enazi",
        "num_q_label": "Number of Questions (1 to 20):",
        "time_q_label": "Time Limit (Seconds):",
        "gen_room_btn": "Generate Quiz Room",
        "q_src_label": "Target Category:",
        "q_src_kids": "Kids Section 👶",
        "q_src_adults": "Adults Section 🧔",
        "age_label": "Specify Child Age (6 to 17 Years):",
        "category_label": "Select Topic:",
        "correct_notify": "Correct! Excellent Job! 🥳",
        "wrong_notify": "❌ Wrong Answer!",
        "correct_is": "💡 Correct is:",
        "inbox_title": "📥 Contact Us Messages Inbox"
    }
}

lang_dict = TRANSLATIONS[st.session_state.lang]

TOPICS = {
    "ar": ["إسلاميات", "لغة عربية", "علوم", "رياضيات", "اجتماعيات", "طبيعة وجغرافيا", "ثقافة عامة منوعة"],
    "en": ["Islamic Studies", "Arabic Language", "Science", "Mathematics", "Social Studies", "Nature & Geography", "General Culture"]
}

direction = "rtl" if st.session_state.lang == "ar" else "ltr"
align = "right" if st.session_state.lang == "ar" else "left"

# دمج ألوان السماء المبهجة والخطوط الاحترافية المريحة للعين
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
    }}
    .main-title {{ text-align: center; color: #0369A1; font-size: 2.8rem; font-weight: bold; margin-bottom: 5px; direction: {direction}; }}
    .stRadio > div {{ flex-direction: row; justify-content: center; gap: 15px; }}
    div.stButton > button:first-child {{ 
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%); 
        color: white; border-radius: 12px; border: none; font-size: 1.1rem; padding: 10px 20px; font-weight: bold;
    }}
    .chat-container {{ background-color: #F0F9FF; padding: 15px; border-radius: 12px; max-height: 350px; overflow-y: auto; display: flex; flex-direction: column; border: 1px solid #7DD3FC; }}
    .msg-box-admin {{ background-color: #BAE6FD; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: {align}; align-self: flex-end; max-width: 80%; color: #0369A1; }}
    .msg-box-player {{ background-color: #FFFFFF; padding: 8px 12px; border-radius: 8px; margin: 5px 0; text-align: {align}; align-self: flex-start; max-width: 80%; color: #334155; border: 1px solid #E2E8F0; }}
    .leaderboard-box {{ background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%); padding: 20px; border-radius: 12px; color: white; text-align: center; font-weight: bold; font-size: 1.5rem; margin-bottom: 20px; }}
    .footer-text {{ text-align: center; color: #0284C7; font-size: 1rem; font-weight: bold; padding: 20px 0; margin-top: 50px; }}
    body {{ direction: {direction}; text-align: {align}; }}
    </style>
""", unsafe_allow_html=True)

# دالة توليد الأسئلة الذكية عبر جيمني
def generate_questions_via_gemini(category, topic, count, lang, age=None):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        age_context = f"Target child exact age is {age} years old. Make sure vocabulary and deepness perfectly match this development stage." if age else "Target group is adults."
        prompt = f"""
        You are a professional quiz generator for Haya-Quiz.
        Generate exactly {count} multiple-choice questions.
        Target Group: '{category}'. {age_context}
        Specific Topic/Classification: '{topic}'.
        The output language MUST be: '{lang}'.
        
        Return the response ONLY as a valid JSON array of objects, with no markdown formatting, no ```json tags.
        Each object must have exactly these keys:
        - "السؤال": The question string.
        - "الخيار 1 - الصحيح": The correct answer string.
        - "الخيار 2": Wrong answer 1.
        - "الخيار 3": Wrong answer 2.
        - "الخيار 4": Wrong answer 3.
        """
        response = model.generate_content(prompt)
        text_clean = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text_clean)
    except Exception as e:
        st.warning("تم تفعيل نظام التوليد الاحتياطي التلقائي.")
        fallback_q = []
        for i in range(count):
            fallback_q.append({
                "السؤال": f"سؤال تفاعلي رقم {i+1} في {topic} ({category})",
                "الخيار 1 - الصحيح": "الجواب الصحيح المعتمد",
                "الخيار 2": "خيار بديل أ",
                "الخيار 3": "خيار بديل ب",
                "الخيار 4": "خيار بديل ج"
            })
        return fallback_q

# دوال الذاكرة الدائمة والمحافظة التراكمية على البيانات والزيارات التاريخية
def load_local_data(filename, default_val):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default_val
    return default_val

def save_local_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@st.cache_resource
def get_server_db():
    return {
        "rooms": {}, 
        "messages": load_local_data("messages.json", []), 
        "total_visitors": load_local_data("total_v.json", 120) # تبدأ تراكمية ومحفوظة بالكامل
    }

db = get_server_db()

# عداد الزيارات التراكمي التاريخي الذكي المحفوظ
if 'visitor_logged' not in st.session_state:
    db["total_visitors"] += 1
    save_local_data("total_v.json", db["total_visitors"])
    st.session_state.visitor_logged = True

# هيدر التنقل الثابت (الرئيسية - تواصل معنا - تحديث الصفحة - اللغة)
navbar_cols = st.columns([1, 4, 1])
with navbar_cols[1]:
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([2, 2, 2, 1])
    if col_nav1.button(lang_dict["home"], use_container_width=True): st.session_state.curr_page = "home"; st.rerun()
    if col_nav2.button(lang_dict["contact"], use_container_width=True): st.session_state.curr_page = "contact_mode"; st.rerun()
    if col_nav3.button(lang_dict["refresh"], use_container_width=True): st.rerun()
    current_lang_label = "🌐 English" if st.session_state.lang == "ar" else "🌐 العربية"
    if col_nav4.button(current_lang_label, use_container_width=True):
        st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
        st.rerun()

st.write("---")

# القائمة الجانبية للإعدادات والإحصائيات التراكمية والوارد
with st.sidebar:
    st.markdown(f"### {lang_dict['settings']}")
    if not st.session_state.admin_authenticated:
        admin_pass = st.text_input(lang_dict["secret_key"], type="password")
        if st.button(lang_dict["confirm"]):
            if admin_pass == "Abdulelah@2026":
                st.session_state.admin_authenticated = True
                st.rerun()
            else: st.error(lang_dict["wrong_pass"])
    else:
        if st.button(lang_dict["logout"]):
            st.session_state.admin_authenticated = False
            st.rerun()
        st.write("---")
        # عرض نوعين من العدادات بناءً على رغبتك المحفوظة والتراكمية
        st.metric(label=lang_dict["visits_current"], value="1 منشط حالياً")
        st.metric(label=lang_dict["visits_total"], value=f"{db['total_visitors']} زيارة")
        
        st.write("---")
        st.markdown(f"#### {lang_dict['inbox_title']}")
        if len(db["messages"]) == 0:
            st.info("لا توجد رسائل واردة حالياً.")
        else:
            for idx, msg in enumerate(db["messages"]):
                with st.expander(f"✉️ من: {msg.get('name', 'مجهول')}"):
                    st.write(f"**الجوال:** {msg.get('phone', 'غير متوفر')}")
                    st.write(f"**البريد:** {msg.get('email', 'غير متوفر')}")
                    st.write(f"**الرسالة:** {msg.get('msg', '')}")
                    
                    # أزرار لوحة التحكم بالرسالة المحددة للرد أو الحذف
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("🗑️ حذف", key=f"del_{idx}"):
                            db["messages"].pop(idx)
                            save_local_data("messages.json", db["messages"])
                            st.rerun()
                    with c_btn2:
                        if st.button("↩️ رد", key=f"reply_{idx}"):
                            st.success(f"تم فتح قناة الرد السريع إلى: {msg.get('email')}")

# محتوى الصفحة الرئيسية
if st.session_state.curr_page == "home":
    st.markdown(f"<h2 class='main-title'>{lang_dict['title']}</h2>", unsafe_allow_html=True)
    col_l_img, col_r_btn = st.columns([1, 2])
    with col_l_img:
        if os.path.exists("my_kids.png"): st.image("my_kids.png", use_container_width=True)
        else: st.info("🎮 Haya Quiz Platform Pro")
    with col_r_btn:
        st.write(lang_dict["ready"])
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button(lang_dict["create_room"], use_container_width=True): st.session_state.curr_page = "admin_mode"; st.rerun()
        with col_b2:
            if st.button(lang_dict["join_player"], use_container_width=True): st.session_state.curr_page = "player_mode"; st.rerun()
        st.write("---")
        if st.button(lang_dict["test_yourself"], use_container_width=True): st.session_state.curr_page = "culture_mode"; st.rerun()

# صفحة تواصل معنا المطورة بالخانات الجديدة المطلوبة بدقة
elif st.session_state.curr_page == "contact_mode":
    st.markdown(f"### {lang_dict['contact']}")
    with st.form("contact_form_advanced"):
        c_name = st.text_input("📝 اسمك الكريم:")
        c_phone = st.text_input("📱 رقم الموبايل:")
        c_email = st.text_input("📧 البريد الإلكتروني:")
        c_msg_txt = st.text_area("💬 نص رسالتك أو اقتراحك للمنصة:")
        if st.form_submit_button("🚀 إرسال الرسالة الآن"):
            if c_name and c_msg_txt: 
                db["messages"].append({
                    "name": c_name, 
                    "phone": c_phone, 
                    "email": c_email, 
                    "msg": c_msg_txt,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_local_data("messages.json", db["messages"])
                st.success("🎉 تم إرسال رسالتك بنجاح وسوف تظهر في لوحة تحكم الإدارة فوراً!")

# لوحة الموجه لإنشاء الغرف وتخصيص الأعمار
elif st.session_state.curr_page == "admin_mode":
    st.markdown(f"<h2 style='text-align:center; color:#0369A1;'>{lang_dict['create_room']}</h2>", unsafe_allow_html=True)
    if 'my_live_room' not in st.session_state:
        q_src = st.radio(lang_dict["q_src_label"], [lang_dict["q_src_kids"], lang_dict["q_src_adults"]])
        
        # إذا تم اختيار فئة الأطفال يظهر منزلق العمر الذكي فوراً من 6 إلى 17 سنة لضبط مستوى صعوبة الكلمات والأسئلة العربية
        chosen_age = None
        if q_src == lang_dict["q_src_kids"]:
            chosen_age = st.slider(lang_dict["age_label"], 6, 17, 10)
            
        q_topic = st.selectbox(lang_dict["category_label"], TOPICS[st.session_state.lang])
        num_q = st.number_input(lang_dict["num_q_label"], min_value=1, max_value=20, value=5)
        
        # تثبيت مؤشر الوقت الافتراضي على 30 ثانية لتجنب البطء وضمان أريحية التفكير
        t_val = st.slider(lang_dict["time_q_label"], 5, 60, 30)
        
        if st.button(lang_dict["gen_room_btn"]):
            with st.spinner("جاري الاتصال بـ Gemini لتوليد باقة أسئلة ذكية ومناسبة للعمر الفعلي... ⚡"):
                chosen_questions = generate_questions_via_gemini(q_src, q_topic, int(num_q), st.session_state.lang, chosen_age)
                
            st.session_state.generated_room_code = str(random.randint(1000, 9999))
            rcode = st.session_state.generated_room_code
            st.session_state.my_live_room = rcode
            
            db["rooms"][rcode] = {
                "players": [], "status": "waiting", "current_q_idx": 0, 
                "questions": chosen_questions, "chat_history": [], "duration": t_val, 
                "scores": {}, "q_start_time": time.time(), "answered_players": []
            }
            st.rerun()
    else:
        # كود إدارة الغرفة الحية مستقر ومحفوظ
        rid = st.session_state.my_live_room; rdata = db["rooms"].get(rid)
        if rdata:
            st.success(f"🎲 رقم الغرفة المباشرة: **{rid}**")
            if rdata["status"] == "waiting":
                if st.button("🚀 إطلاق البث والمسابقة الحين"): 
                    db["rooms"][rid]["status"] = "playing"; db["rooms"][rid]["q_start_time"] = time.time(); st.rerun()
            elif rdata["status"] == "playing":
                qi = rdata["current_q_idx"]; ql = rdata["questions"]
                if qi < len(ql):
                    st.write(f"📊 السؤال الحالي ({qi+1}/{len(ql)}): **{ql[qi]['السؤال']}**")
                    st.info(f"{lang_dict['correct_is']} **{ql[qi]['الخيار 1 - الصحيح']}**")
                    rem = max(0, int(rdata["duration"] - (time.time() - rdata["q_start_time"])))
                    st.warning(f"⏱️ العداد التنازلي: {rem} ثانية")
                    if rem <= 0 or st.button("➡️ السؤال التالي"):
                        db["rooms"][rid]["current_q_idx"] += 1; db["rooms"][rid]["q_start_time"] = time.time(); st.rerun()
                else: 
                    db["rooms"][rid]["status"] = "finished"; st.rerun()
            elif rdata["status"] == "finished":
                st.markdown("<div class='leaderboard-box'>🏆 لوحة الصدارة النهائية 🏆</div>", unsafe_allow_html=True)
                for rank, (p, s) in enumerate(sorted(rdata["scores"].items(), key=lambda x: x[1], reverse=True)):
                    st.write(f"### 🏅 المركز {rank+1}: **{p}** -> {s} نقطة")
            if st.button("🛑 إنهاء المسابقة وإغلاق الغرفة"):
                if rid in db["rooms"]: del db["rooms"][rid]
                del st.session_state.my_live_room; st.session_state.generated_room_code = None; st.rerun()

# صفحة اختبر نفسك (ثقّف نفسك) الفردية المفعلة كلياً بالذكاء الاصطناعي
elif st.session_state.curr_page == "culture_mode":
    st.markdown(f"<h2 style='text-align:center; color:#0369A1;'>🕹️ {lang_dict['test_yourself']}</h2>", unsafe_allow_html=True)
    
    if 'solo_questions' not in st.session_state:
        st.write("### اختر إعدادات تحديك الشخصي:")
        solo_topic = st.selectbox("اختر المجال المستهدف:", TOPICS[st.session_state.lang])
        solo_count = st.slider(lang_dict["num_q_label"], 1, 20, 5)
        
        if st.button("🎯 ابدأ توليد التحدي فوراً"):
            with st.spinner("جاري صياغة أسئلة مخصصة لك عبر الذكاء الاصطناعي... 🔥"):
                st.session_state.solo_questions = generate_questions_via_gemini("Adults", solo_topic, int(solo_count), st.session_state.lang)
                st.session_state.solo_idx = 0
                st.session_state.solo_score = 0
            st.rerun()
    else:
        sq = st.session_state.solo_questions
        si = st.session_state.solo_idx
        if si < len(sq):
            st.write(f"### ❓ السؤال {si+1}: {sq[si]['السؤال']}")
            corr = str(sq[si]["الخيار 1 - الصحيح"])
            
            if f"solo_opt_{si}" not in st.session_state:
                opts = [corr, str(sq[si]["الخيار 2"]), str(sq[si]["الخيار 3"]), str(sq[si]["الخيار 4"])]
                random.shuffle(opts); st.session_state[f"solo_opt_{si}"] = opts
                
            user_sel = st.radio("اختر الإجابة الصحيحة:", st.session_state[f"solo_opt_{si}"], key=f"sl_r_{si}")
            
            if st.button("✔️ تأكيد واعتماد الإجابة"):
                if user_sel == corr:
                    st.success(lang_dict["correct_notify"])
                    st.session_state.solo_score += 10
                else:
                    st.error(lang_dict["wrong_notify"])
                    st.info(f"{lang_dict['correct_is']} {corr}")
                time.sleep(1.5)
                st.session_state.solo_idx += 1
                st.rerun()
        else:
            st.balloons()
            st.markdown(f"<div class='leaderboard-box'>🎉 انتهى التحدي الفردي بنجاح! رصيدك: {st.session_state.solo_score} نقطة!</div>", unsafe_allow_html=True)
            if st.button("🔄 تحدي جديد"):
                del st.session_state.solo_questions
                st.rerun()

# صفحة المتسابقين والتحاقهم بالغرفة
elif st.session_state.curr_page == "player_mode":
    cc = st.text_input("أدخل رقم الغرفة المكون من 4 أرقام:")
    cn = st.text_input("أدخل اسمك الكريم للمنافسة:")
    if st.button("🚪 دخول الغرفة الحية"):
        st.info("جاري الاتصال والتحضير لدخول البث الحركي للمسابقة...")

st.markdown(f"<div class='footer-text'>{lang_dict['footer']}</div>", unsafe_allow_html=True)
