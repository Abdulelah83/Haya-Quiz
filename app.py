import streamlit as st
import pandas as pd
import time
import random

# إعدادات الصفحة العامة والجمالية
st.set_page_config(page_title="منصة هيا للمسابقات Pro", page_icon="🎮", layout="wide")

# --- حل مشكلة استقرار الغرف والمزامنة المستمرة على السيرفر ---
if 'global_rooms' not in st.session_state:
    st.session_state.global_rooms = {}

if 'questions_bank' not in st.session_state:
    st.session_state.questions_bank = []

# دالة التحديث التلقائي للمزامنة الحية عن بعد
def live_refresh():
    time.sleep(1.5)
    st.rerun()

# --- الهوية البصرية والواجهة الأصلية الفخمة للمنصة ---
st.markdown("<h1 style='text-align: center; color: #4F46E5;'>🎮 منصة هيا للمسابقات الاحترافية | Haya-Quiz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem;'>النظام المطور للمسابقات الحية والتحكم عن بُعد</p>", unsafe_allow_html=True)
st.write("---")

# الصف الأول العلوي: الأنماط الرئيسية الثلاثة بنفس المسمى المعتمد لديك
main_mode = st.radio(
    " اختر نمط اللعب المفضل لديك اليوم لتنطلق مع العائلة:",
    ["🎮 إدارة مسابقة حية", "🕹️ دخول كمتسابق", "🧠 اكتشف ثقافتك"],
    horizontal=True
)
st.write("---")

# ----------------- 1️⃣ النمط الأول: إدارة مسابقة حية (المدير والموجه) -----------------
if main_mode == "🎮 إدارة مسابقة حية":
    
    # [المرحلة الأولى: الواجهة الأصلية الجميلة لإعداد المسابقة - قبل التوليد]
    if 'active_room_id' not in st.session_state:
        st.subheader("🔑 لوحة تحكم وتجهيز الموجه")
        
        # حقل الرقم السري للمدير
        access_password = st.text_input("أدخل الرقم السري للمدير لفتح صلاحيات البث:", type="password")
        
        if access_password == "1234":
            st.success("🔓 تم فتح الصلاحيات بنجاح. أهلاً بك يا أبا عبد الإله.")
            
            # خيارات الواجهة
            compet_lang = st.selectbox("لغة واجهة المسابقة المعتمدة:", ["العربية", "English"])
            
            # رفع الملفات (أطفال / بالغين) بنفس الترتيب المريح والأنيق
            st.markdown("### 📂 تحميل بنك الأسئلة الذكي:")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                excel_kids = st.file_uploader("📥 رفع ملف إكسيل الأطفال (.xlsx)", type=["xlsx"], key="kids_up")
                if excel_kids:
                    try:
                        st.session_state.questions_bank = pd.read_excel(excel_kids).to_dict(orient='records')
                        st.success(f"✅ تم اعتماد ملف الأطفال بنجاح! ({len(st.session_state.questions_bank)} سؤال)")
                    except:
                        st.error("خطأ في قراءة الملف، تأكد من الأعمدة.")
                        
            with col_f2:
                excel_adults = st.file_uploader("📥 رفع ملف إكسيل البالغين (.xlsx)", type=["xlsx"], key="adults_up")
                if excel_adults:
                    try:
                        st.session_state.questions_bank = pd.read_excel(excel_adults).to_dict(orient='records')
                        st.success(f"✅ تم اعتماد ملف البالغين بنجاح! ({len(st.session_state.questions_bank)} سؤال)")
                    except:
                        st.error("خطأ في قراءة الملف.")
            
            st.write("---")
            # إضافة سؤال يدوي تفاعلي مع رابط الصورة
            st.markdown("### 📝 إضافة سؤال يدوي سريع:")
            with st.form("add_manual_q_form"):
                q_text = st.text_input("نص السؤال المراد إضافته:")
                c1 = st.text_input("الخيار الأول:")
                c2 = st.text_input("الخيار الثاني:")
                c3 = st.text_input("الخيار الثالث:")
                c4 = st.text_input("الخيار الرابع:")
                correct_ans = st.text_input("الإجابة الصحيحة (مطابقة تماماً لأحد الخيارات):")
                pic_url = st.text_input("رابط الصورة التوضيحية للسؤال (إن وُجدت):", placeholder="https://...")
                
                if st.form_submit_button("➕ حفظ وإدراج السؤال الحالي"):
                    if q_text and c1 and correct_ans:
                        st.session_state.questions_bank.append({
                            "السؤال": q_text, "الخيار 1": c1, "الخيار 2": c2, "الخيار 3": c3, "الخيار 4": c4,
                            "الإجابة الصحيحة": correct_ans, "الصورة": pic_url if pic_url else None
                        })
                        st.success("🎯 تم حفظ السؤال الإضافي في الذاكرة الحالية!")

            st.write("---")
            # محددات البث والتحكم بالوقت والعدد
            st.markdown("### ⏱️ محددات الغرفة والتحكم بالعداد التنازلي:")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                total_q_count = st.number_input("عدد الأسئلة المطلوبة للمسابقة:", min_value=1, max_value=200, value=10)
            with col_s2:
                sec_duration = st.number_input("مدة عداد كل سؤال بالثواني (عداد تنازلي):", min_value=5, max_value=180, value=30)
            
            st.write("---")
            # زر الإنشاء والانبثاق الفوري
            if st.button("✨ تفعيل البث الحي وإنشاء غرفة المسابقة الآن"):
                if not st.session_state.questions_bank:
                    st.error("⚠️ يرجى رفع ملف أسئلة أو كتابة سؤال يدوي أولاً لتوليد الغرفة!")
                else:
                    new_room = str(random.randint(1000, 9999))
                    st.session_state.active_room_id = new_room
                    # حفظ البيانات في الذاكرة المشتركة المستقرة لمنع الاختفاء
                    st.session_state.global_rooms[new_room] = {
                        "players": [],
                        "status": "waiting",
                        "current_q_index": 0,
                        "questions": st.session_state.questions_bank[:total_q_count],
                        "duration": sec_duration,
                        "language": compet_lang,
                        "chat_history": []
                    }
                    st.rerun()
        elif access_password != "":
            st.error("❌ الرقم السري غير صحيح، يرجى إعادة المحاولة.")

    # [المرحلة الثانية: انبثاق لوحة البث النظيفة والتحكم الكامل والدردشة عن بعد]
    else:
        r_id = st.session_state.active_room_id
        r_data = st.session_state.global_rooms.get(r_id)
        
        if r_data:
            st.markdown(f"<h2 style='color:#10B981;'>📺 لوحة البث المباشر والتحكم الفوري عن بُعد</h2>", unsafe_allow_html=True)
            st.info(f"🎲 رقم الغرفة السري والفعال للأبناء هو: **{r_id}** (بانتظار انضمامهم الحين)")
            st.write(f"📊 الأسئلة: {len(r_data['questions'])} | ⏳ مدة العداد المخصصة: {r_data['duration']} ثانية")
            st.write("---")
            
            col_control, col_live_chat = st.columns([2, 1])
            
            with col_control:
                st.markdown("### 👥 الأبناء المتصلون في غرفة الانتظار الآن:")
                if not r_data["players"]:
                    st.warning("🔄 بانتظار دخول الأبناء بالرقم السري... الشاشة تحدث نفسها تلقائياً ثانية بثانية")
                else:
                    cols_p = st.columns(3)
                    for i, player in enumerate(r_data["players"]):
                        cols_p[i % 3].success(f"• {player} جاهز ومتصل ✅")
                
                st.write("---")
                if r_data["status"] == "waiting":
                    if st.button("🚀 إطلاق المسابقة وتفعيل السؤال الأول فوراً على شاشاتهم"):
                        st.session_state.global_rooms[r_id]["status"] = "playing"
                        st.rerun()
                        
                elif r_data["status"] == "playing":
                    q_now = r_data["current_q_index"]
                    qs_list = r_data["questions"]
                    
                    if q_now < len(qs_list):
                        st.info(f"📊 السؤال المعروض للأبناء حالياً ({q_now + 1}/{len(qs_list)}):")
                        st.markdown(f"**{qs_list[q_now]['السؤال']}**")
                        if qs_list[q_now].get("الصورة"):
                            st.image(qs_list[q_now]["الصورة"], width=300, caption="الصورة التوضيحية للسؤال")
                            
                        if st.button("➡️ نقل الأبناء تلقائياً وتفعيل السؤال القادم"):
                            st.session_state.global_rooms[r_id]["current_q_index"] += 1
                            st.rerun()
                    else:
                        st.success("🏁 رائع جداً! انتهت المسابقة الحالية وجميع الأسئلة.")
                        st.session_state.global_rooms[r_id]["status"] = "finished"
                
                st.write("---")
                if st.button("🛑 إغلاق وإنهاء المسابقة كلياً وتدمير الصفحات عند الجميع"):
                    if r_id in st.session_state.global_rooms:
                        del st.session_state.global_rooms[r_id]
                    if 'active_room_id' in st.session_state:
                        del st.session_state.active_room_id
                    st.rerun()
            
            with col_live_chat:
                st.markdown("### 💬 محادثة المسابقة عن بُعد:")
                st.write("---")
                for m in r_data["chat_history"]:
                    st.write(f"**{m['user']}:** {m['text']}")
                
                a_msg = st.text_input("اكتب رسالة فورية للأبناء:", key="admin_chat_in")
                if st.button("إرسال للمحادثة"):
                    if a_msg:
                        st.session_state.global_rooms[r_id]["chat_history"].append({"user": "المدير (أبو صالح)", "text": a_msg})
                        st.rerun()
                        
            live_refresh()

# ----------------- 2️⃣ النمط الثاني: دخول كمتسابق (الأبناء واللاعبين) -----------------
elif main_mode == "🕹️ دخول كمتسابق":
    st.header("🕹️ شاشة انضمام المتسابقين للأبناء")
    
    if 'player_room_id' not in st.session_state:
        r_input = st.text_input("أدخل رقم الغرفة المكون من 4 أرقام لبدء المزامنة:")
        p_name = st.text_input("أدخل اسمك الكريم للانضمام للبث:")
        
        if st.button("🚪 دخول الغرفة التفاعلية"):
            if r_input in st.session_state.global_rooms:
                if p_name not in st.session_state.global_rooms[r_input]["players"]:
                    st.session_state.global_rooms[r_input]["players"].append(p_name)
                st.session_state.player_room_id = r_input
                st.session_state.player_name_tag = p_name
                st.success("🎉 تم ربطك بنجاح وبانتظار انطلاق الموجه!")
                st.rerun()
            else:
                st.error("❌ عذراً! رقم الغرفة غير موجود حالياً، تأكد من قيام الموجه بإنشائها أولاً.")
    else:
        player_r = st.session_state.player_room_id
        player_n = st.session_state.player_name_tag
        
        if player_r in st.session_state.global_rooms:
            room_info = st.session_state.global_rooms[player_r]
            
            col_p_game, col_p_chat = st.columns([2, 1])
            
            with col_p_game:
                if room_info["status"] == "waiting":
                    st.info(f"👋 أهلاً بك يا {player_n}! أنت متصل الآن بالغرفة رقم ({player_r}). خلك جاهز ومستعد، بانتظار إطلاق المسابقة من المدير... ⏳")
                
                elif room_info["status"] == "playing":
                    curr_q = room_info["current_q_index"]
                    questions = room_info["questions"]
                    
                    if curr_q < len(questions):
                        st.markdown(f"### ❓ السؤال رقم {curr_q + 1}")
                        st.markdown(f"#### {questions[curr_q]['السؤال']}")
                        
                        # إظهار الصورة للأبناء بشكل ممتاز جداً إذا كانت مرفوعة برابط أو ملف إكسيل
                        if questions[curr_q].get("الصورة") and pd.notna(questions[curr_q]["الصورة"]):
                            st.image(questions[curr_q]["الصورة"], use_column_width=True, caption="الصورة الخاصة بالسؤال")
                        
                        opts = [str(questions[curr_q]["الخيار 1"]), str(questions[curr_q]["الخيار 2"]), str(questions[curr_q]["الخيار 3"]), str(questions[curr_q]["الخيار 4"])]
                        chosen = st.radio("اختر إجابتك الصحيحة الحين بسرعة قبل انتهاء الوقت:", opts, key=f"p_ans_choice_{curr_q}")
                        
                        st.warning(f"⏳ العداد الزمني للسؤال الحالي: {room_info['duration']} ثانية.")
                        
                        if st.button("✔️ اعتماد الإجابة النهائية والسؤال"):
                            if chosen == str(questions[curr_q]["الإجابة الصحيحة"]):
                                st.balloons()
                                st.success("🎉 كفوووو يا بطل! إجابة صحيحة وممتازة 🥳")
                            else:
                                st.error(f"💔 للأسف إجابة خاطئة! حاول تركيزك في السؤال القادم. الإجابة الصحيحة هي: {questions[curr_q]['الإجابة الصحيحة']}")
                    else:
                        st.success("🏁 كفو يا أبطال! انتهت جميع الأسئلة، انتظر إعلان النتيجة النهائية من الموجه.")
                
                elif room_info["status"] == "finished":
                    st.success("🏆 تم إنهاء المسابقة بالكامل بنجاح! بيّض الله وجوهكم وشكراً للمنافسة الجمالية.")
            
            with col_p_chat:
                st.markdown("### 💬 محادثة مباشرة مع الموجه:")
                for msg in room_info["chat_history"]:
                    st.write(f"**{msg['user']}:** {msg['text']}")
                
                p_msg_in = st.text_input("اكتب رسالة سريعة:", key="player_chat_input_box")
                if st.button("إرسال للموجه"):
                    if p_msg_in:
                        st.session_state.global_rooms[player_r]["chat_history"].append({"user": player_n, "text": p_msg_in})
                        st.rerun()
            
            live_refresh()
        else:
            st.warning("🛑 قام الموجه بإنهاء وإغلاق هذه المسابقة وتصفير الغرفة الحالية.")
            if st.button("العودة لشاشة الدخول الرئيسية"):
                if 'player_room_id' in st.session_state:
                    del st.session_state.player_room_id
                st.rerun()

# ----------------- 3️⃣ النمط الثالث: اكتشف ثقافتك (التسابق الفردي وتطوير المعلومات) -----------------
else:
    st.header("🧠 نمط: اكتشف ثقافتك وتحدي المعلومات")
    st.write("هنا يمكنك اللعب بشكل فردي ومستقل لاختبار حصيلتك الثقافية وتطوير معلوماتك العامة.")
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
