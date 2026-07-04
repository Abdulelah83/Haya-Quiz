import streamlit as st
import pandas as pd
import time
import random

# إعدادات الصفحة
st.set_page_config(page_title="منصة هيا للمسابقات", page_icon="🎮", layout="wide")

# إدارة الذاكرة المستقرة للغرف والمحادثات لضمان الاستقرار على ريندر
if 'rooms_db' not in st.session_state:
    st.session_state.rooms_db = {}

if 'custom_questions' not in st.session_state:
    st.session_state.custom_questions = []

def force_rerun():
    time.sleep(2)
    st.rerun()

# --- واجهة المنصة الرئيسية ---
st.title("🎮 منصة هيا للمسابقات | Haya-Quiz")
st.write("---")

# الخيارات الثلاثة الرئيسية في الصفحة الأولى
main_option = st.radio(
    "اختر نمط اللعب المفضل لديك اليوم:",
    ["🎮 إدارة مسابقة حية", "🕹️ دخول كمتسابق", "🧠 اكتشف ثقافتك"],
    horizontal=True
)

# ----------------- 1️⃣ النمط الأول: إدارة مسابقة حية (المدير) -----------------
if main_option == "🎮 إدارة مسابقة حية":
    
    # [الحالة الأولى: مرحلة الإدخال والتجهيز - قبل توليد الغرفة]
    if 'my_room' not in st.session_state:
        st.header("🔑 إعدادات وتجهيز المسابقة الحية")
        
        # التحقق من الرقم السري للمدير
        admin_password = st.text_input("أدخل الرقم السري للمدير لفتح الصلاحيات:", type="password")
        
        if admin_password == "1234":
            st.success("✅ تم التحقق من الهوية بنجاح.")
            st.write("---")
            
            # خيار تحويل اللغة واختيار الملفات
            lang = st.selectbox("اختر لغة واجهة المسابقة / Select Language:", ["العربية", "English"])
            
            st.write("📂 **تحميل بنك الأسئلة:**")
            col_file1, col_file2 = st.columns(2)
            with col_file1:
                file_kids = st.file_uploader("📥 رفع ملف إكسيل الأطفال (.xlsx)", type=["xlsx"])
                if file_kids:
                    df = pd.read_excel(file_kids)
                    st.session_state.custom_questions = df.to_dict(orient='records')
                    st.success(f"تم اعتماد أسئلة الأطفال ({len(st.session_state.custom_questions)} سؤال)")
                    
            with col_file2:
                file_adults = st.file_uploader("📥 رفع ملف إكسيل البالغين (.xlsx)", type=["xlsx"])
                if file_adults:
                    df = pd.read_excel(file_adults)
                    st.session_state.custom_questions = df.to_dict(orient='records')
                    st.success(f"تم اعتماد أسئلة البالغين ({len(st.session_state.custom_questions)} سؤال)")
            
            # إضافة سؤال يدوي مع صورة
            st.write("📝 **إضافة سؤال يدوي سريع:**")
            with st.form("manual_question_form"):
                q_text = st.text_input("نص السؤال:")
                o1 = st.text_input("الخيار 1:")
                o2 = st.text_input("الخيار 2:")
                o3 = st.text_input("الخيار 3:")
                o4 = st.text_input("الخيار 4:")
                c_ans = st.text_input("الإجابة الصحيحة تماماً:")
                img_url = st.text_input("رابط صورة توضيحية للسؤال (اختياري):")
                
                if st.form_submit_button("➕ حفظ السؤال يدويًا"):
                    if q_text and o1 and c_ans:
                        st.session_state.custom_questions.append({
                            "السؤال": q_text, "الخيار 1": o1, "الخيار 2": o2, "الخيار 3": o3, "الخيار 4": o4,
                            "الإجابة الصحيحة": c_ans, "الصورة": img_url if img_url else None
                        })
                        st.success("تم حفظ السؤال الإضافي بنجاح!")

            st.write("---")
            # محددات البث الحي قبل التوليد
            st.subheader("⏱️ محددات الغرفة والوقت")
            col_setup1, col_setup2 = st.columns(2)
            with col_setup1:
                q_limit = st.number_input("حدد عدد الأسئلة للمسابقة الحالية:", min_value=1, max_value=100, value=10)
            with col_setup2:
                q_duration = st.number_input("حدد مدة كل سؤال (بالثواني):", min_value=5, max_value=120, value=30)
                
            if st.button("✨ تفعيل وإنشاء غرفة المسابقة وتوليد الرقم"):
                if not st.session_state.custom_questions:
                    st.error("الرجاء رفع ملف أسئلة أو إضافة سؤال يدوي أولاً!")
                else:
                    room_id = str(random.randint(1000, 9999))
                    st.session_state.my_room = room_id
                    st.session_state.rooms_db[room_id] = {
                        "players": [],
                        "status": "waiting",
                        "current_question": 0,
                        "questions": st.session_state.custom_questions[:q_limit],
                        "duration": q_duration,
                        "language": lang,
                        "chat": []
                    }
                    st.rerun()
        elif admin_password != "":
            st.error("❌ الرقم السري غير صحيح، يرجى المحاولة مرة أخرى.")

    # [الحالة الثانية: انبثاق لوحة البث النظيفة والدردشة - بعد توليد الغرفة]
    else:
        room_id = st.session_state.my_room
        room_data = st.session_state.rooms_db.get(room_id)
        
        if room_data:
            st.header("📺 لوحة البث المباشر والتحكم عن بعد")
            st.success(f"🎲 تم توليد الغرفة بنجاح! رقم الدخول الفوري للأبناء هو: **{room_id}**")
            st.write(f"🌐 اللغة: **{room_data['language']}** | عدد الأسئلة المخصصة: **{len(room_data['questions'])}** | مدة السؤال: **{room_data['duration']} ثانية**")
            st.write("---")
            
            # تقسيم الشاشة للبث الحي والدردشة عن بعد
            col_live, col_chat = st.columns([2, 1])
            
            with col_live:
                st.subheader("👥 المشتركون المتصلون بالانتظار حالياً:")
                if not room_data["players"]:
                    st.warning("بانتظار دخول الأبناء بالرقم... (الشاشة تتحدث تلقائياً 🔄)")
                else:
                    cols = st.columns(3)
                    for idx, p in enumerate(room_data["players"]):
                        cols[idx % 3].success(f"• {p} جاهز ✅")
                        
                st.write("---")
                if room_data["status"] == "waiting":
                    if st.button("🚀 إطلاق المسابقة وتفعيل السؤال الأول لجميع المتسابقين"):
                        st.session_state.rooms_db[room_id]["status"] = "playing"
                        st.rerun()
                        
                elif room_data["status"] == "playing":
                    q_idx = room_data["current_question"]
                    qs = room_data["questions"]
                    
                    if q_idx < len(qs):
                        st.info(f"📊 السؤال الحالي المعروض الآن ({q_idx + 1}/{len(qs)}): {qs[q_idx]['السؤال']}")
                        if st.button("➡️ نقل المتسابقين وتفعيل السؤال التالي تلقائياً"):
                            st.session_state.rooms_db[room_id]["current_question"] += 1
                            st.rerun()
                    else:
                        st.success("🏁 انتهت الأسئلة المحددة للمسابقة!")
                        st.session_state.rooms_db[room_id]["status"] = "finished"
                        
                st.write("---")
                if st.button("🛑 إغلاق وإنهاء المسابقة كلياً وتدمير الصفحات عند الجميع"):
                    if room_id in st.session_state.rooms_db:
                        del st.session_state.rooms_db[room_id]
                    del st.session_state.my_room
                    st.rerun()
                    
            with col_chat:
                st.subheader("💬 غرفة المحادثة المباشرة للمسابقة")
                st.write("---")
                for msg in room_data["chat"]:
                    st.write(f"**{msg['user']}:** {msg['text']}")
                
                admin_msg = st.text_input("اكتب رسالة للمتسابقين:", key="admin_msg_input")
                if st.button("إرسال الشات"):
                    if admin_msg:
                        st.session_state.rooms_db[room_id]["chat"].append({"user": "المدير", "text": admin_msg})
                        st.rerun()
                        
            force_rerun()

# ----------------- 2️⃣ النمط الثاني: دخول كمتسابق (الأبناء) -----------------
elif main_option == "🕹️ دخول كمتسابق":
    st.header("🕹️ انضمام للمسابقة الحية")
    
    if 'current_player_room' not in st.session_state:
        room_input = st.text_input("أدخل رقم الغرفة المكون من 4 أرقام:")
        p_name = st.text_input("أدخل اسمك الكريم للمنافسة:")
        
        if st.button("🚪 دخول الغرفة المباشرة"):
            if room_input in st.session_state.rooms_db:
                if p_name not in st.session_state.rooms_db[room_input]["players"]:
                    st.session_state.rooms_db[room_input]["players"].append(p_name)
                st.session_state.current_player_room = room_input
                st.session_state.player_identity = p_name
                st.success("تم الدخول والربط المزامَن بنجاح!")
                st.rerun()
            else:
                st.error("الغرفة غير موجودة حالياً أو تم إغلاقها من المدير.")
    else:
        r_id = st.session_state.current_player_room
        p_name = st.session_state.player_identity
        
        if r_id in st.session_state.rooms_db:
            r_data = st.session_state.rooms_db[r_id]
            
            col_p_live, col_p_chat = st.columns([2, 1])
            
            with col_p_live:
                if r_data["status"] == "waiting":
                    st.info(f"👋 أهلاً بك يا {p_name}! تم ربطك بالغرفة الفعالة. انتظر الموجه حتى يطلق المسابقة ⏳")
                elif r_data["status"] == "playing":
                    q_idx = r_data["current_question"]
                    qs = r_data["questions"]
                    
                    if q_idx < len(qs):
                        st.subheader(f"🤔 السؤال رقم {q_idx + 1}")
                        st.write(qs[q_idx]["السؤال"])
                        
                        if qs[q_idx].get("الصورة") and pd.notna(qs[q_idx]["الصورة"]):
                            st.image(qs[q_idx]["الصورة"], use_column_width=True)
                            
                        options = [str(qs[q_idx]["الخيار 1"]), str(qs[q_idx]["الخيار 2"]), str(qs[q_idx]["الخيار 3"]), str(qs[q_idx]["الخيار 4"])]
                        ans = st.radio("اختر إجابتك الصحيحة بسرعة:", options, key=f"p_ans_{q_idx}")
                        
                        st.warning(f"⏳ الوقت المحدد للسؤال الحالي: {r_data['duration']} ثانية.")
                        
                        if st.button("✔️ اعتماد الإجابة"):
                            if ans == str(qs[q_idx]["الإجابة الصحيحة"]):
                                st.balloons()
                                st.success("إجابة صحيحة! كفوو يا بطل 🥳")
                            else:
                                st.error(f"إجابة خاطئة! الإجابة الصح هي: {qs[q_idx]['الإجابة الصحيحة']}")
                    else:
                        st.success("🏁 انتهت الأسئلة! بانتظار الموجه لإعلان النتيجة النهائية.")
                elif r_data["status"] == "finished":
                    st.success("🏆 انتهت المسابقة بالكامل، بيّض الله وجوهكم جميعاً!")
            
            with col_p_chat:
                st.subheader("💬 الدردشة مع الموجه")
                for msg in r_data["chat"]:
                    st.write(f"**{msg['user']}:** {msg['text']}")
                p_msg = st.text_input("اكتب رسالة:", key="p_msg_input")
                if st.button("إرسال"):
                    if p_msg:
                        st.session_state.rooms_db[r_id]["chat"].append({"user": p_name, "text": p_msg})
                        st.rerun()
            
            force_rerun()
        else:
            st.warning("⚠️ قام الموجه بإنهاء المسابقة وإغلاق الغرفة الحالية فوراً.")
            if st.button("العودة إلى القائمة الرئيسية"):
                del st.session_state.current_player_room
                st.rerun()

# ----------------- 3️⃣ النمط الثالث: اكتشف ثقافتك (التسابق الفردي سابقاً) -----------------
else:
    st.header("🧠 نمط: اكتشف ثقافتك الفردي")
    st.write("هنا يمكنك اللعب الفردي واختبار معلوماتك العامة وتطوير ثقافتك بدون موجه أو غرف بث حي.")
    st.write("---")
    
    sample_q = [
        {"ق": "كم عدد كواكب المجموعة الشمسية？", "ج": "8 كواكب"},
        {"ق": "ما هي عاصمة المملكة العربية السعودية؟", "ج": "الرياض"}
    ]
    for idx, sq in enumerate(sample_q):
        st.subheader(f"💡 تحدي الثقافة {idx + 1}:")
        st.write(sq["ق"])
        if st.button(f"👁️ إظهار الإجابة الصحيحة لتحدي {idx + 1}", key=f"cult_{idx}"):
            st.success(sq["ج"])
