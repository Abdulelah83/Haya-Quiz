import streamlit as st
import pandas as pd
import time
import random
import os
import json
from datetime import datetime
import google.generativeai as genai

# 1. إعدادات الصفحة والهوية البصرية واستهداف ألوان السماء المريحة للعين
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz Pro", 
    page_icon="🎯", 
    layout="wide"
)

# إجبار المتصفح وسفاري على إلغاء القائمة الجانبية تماماً لتنظيف الشاشة من الخط العمودي المشوه
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    .stApp { background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%) !important; }
    
    /* ضبط جودة ووضوح الخطوط لضمان القراءة الممتازة للأطفال والكبار */
    h1, h2, h3, p, label, .stMarkdown { 
        color: #0F172A !important; 
        font-weight: bold !important; 
        font-family: 'Cairo', sans-serif !important;
    }
    .question-text {
        color: #1E3A8A !important;
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        border-right: 6px solid #0284C7;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stRadio label {
        color: #1E293B !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
    div.stButton > button:first-child { 
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important; 
        color: white !important; border-radius: 12px !important; border: none !important; 
        font-size: 1.2rem !important; padding: 12px 24px !important; font-weight: bold !important;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
    }
    .input-label {
        color: #1E3A8A !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        margin-bottom: 5px;
    }
    .footer-text { text-align: center; color: #0369A1; font-size: 1.1rem; font-weight: bold; padding: 20px 0; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# تهيئة متغيرات الجلسة الأساسية للحفاظ على جوهر النظام
if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"
if 'generated_room_code' not in st.session_state: st.session_state.generated_room_code = None
if 'admin_authenticated' not in st.session_state: st.session_state.admin_authenticated = False
if 'lang' not in st.session_state: st.session_state.lang = "ar"

# ربط الـ API الخاص بجيمني بشكل آمن
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# دوال الذاكرة الدائمة والمحافظة التراكمية على المسابقات والزيارات التاريخية
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
        "manual_pools": load_local_data("manual_pools.json", {}), 
        "messages": load_local_data("messages.json", []), 
        "total_visitors": load_local_data("total_v.json", 125)
    }

db = get_server_db()

if 'visitor_logged' not in st.session_state:
    db["total_visitors"] += 1
    save_local_data("total_v.json", db["total_visitors"])
    st.session_state.visitor_logged = True

# دالة توليد الأسئلة من جيمني مع إلزامية عدم التكرار كلياً وتوليد مجالات متنوعة ونادرة
def generate_questions_via_gemini(category, topic, count, lang, age=None):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        age_context = f"Target child exact age is {age} years old." if age else "Target group is adults."
        prompt = f"""
        You are an elite professional quiz creator for Haya-Quiz.
        Generate exactly {count} distinct and highly unique multiple-choice questions.
        Target Group: '{category}'. {age_context}
        Topic/Domain: '{topic}'.
        Language: '{lang}'.
        
        CRITICAL RULE FOR VARIETY: Do NOT repeat questions from common or standard pools. Make them highly educational, creative, diverse, and never-before-seen.
        
        Return response ONLY as a pure JSON array of objects, with no markdown formatting, no ```json tags.
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
        fallback_q = []
        for i in range(count):
            fallback_q.append({
                "السؤال": f"سؤال فريد ومميز رقم {random.randint(100, 999)} في {topic} ({category})",
                "الخيار 1 - الصحيح": "الجواب الصحيح المعتمد",
                "الخيار 2": "خيار بديل أ", "الخيار 3": "خيار بديل ب", "الخيار 4": "خيار بديل ج"
            })
        return fallback_q

# هيدر التنقل العلوي المتناسق والعريض جداً للجوالات لمنع التداخل واللخبطة
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 1])
if col_nav1.button("🏠 الرئيسية", use_container_width=True): st.session_state.curr_page = "home"; st.rerun()
if col_nav2.button("📞 تواصل معنا", use_container_width=True): st.session_state.curr_page = "contact_mode"; st.rerun()
if col_nav3.button("🔄 تحديث الصفحة", use_container_width=True): st.rerun()
current_lang_label = "🌐 English" if st.session_state.lang == "ar" else "🌐 العربية"
if col_nav4.button(current_lang_label, use_container_width=True):
    st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
    st.rerun()

st.write("---")

# الصفحة الرئيسية للمنصة
if st.session_state.curr_page == "home":
    st.markdown("<h2 style='text-align:center; color:#0369A1;'>منصة مسابقات هيا الفاخرة  🎯</h2>", unsafe_allow_html=True)
    if os.path.exists("my_kids.png"): 
        st.image("my_kids.png", use_container_width=True)
        
    st.markdown("<p style='text-align:center; font-size:1.3rem;'>جاهزون للتحدي والمنافسة الحية المباشرة الحين؟</p>", unsafe_allow_html=True)
    
    # توزيع الأزرار بشكل طولي عريض ومريح جداً للضغط على شاشات الجوال وسفاري
    if st.button("🏆 إنشاء وإدارة مسابقة ذكية حية (عبر جيمني AI)", use_container_width=True): st.session_state.curr_page = "admin_mode"; st.rerun()
    if st.button("📝 نظام الموجه لتركيب أسئلة يدوية مخصصة", use_container_width=True): st.session_state.curr_page = "manual_setup_mode"; st.rerun()
    if st.button("🎮 دخول كمتسابق في جولة حية", use_container_width=True): st.session_state.curr_page = "player_mode"; st.rerun()
    if st.button("🕹️ تحدي اختبر نفسك الفردي (ثقّف نفسك الفوري)", use_container_width=True): st.session_state.curr_page = "culture_mode"; st.rerun()

# 📝 نظام الموجه لتركيب وحفظ أسئلة يدوية مخصصة
elif st.session_state.curr_page == "manual_setup_mode":
    st.markdown("<h2 style='text-align:center; color:#0369A1;'>📝 لوحة تصميم وحفظ المسابقات اليدوية</h2>", unsafe_allow_html=True)
    
    num_manual_q = st.number_input("📌 كم عدد الأسئلة التي تريد إدخالها بنفسك؟", min_value=1, max_value=20, value=5)
    
    manual_list = []
    for idx in range(int(num_manual_q)):
        st.markdown(f"#### ❓ صياغة السؤال رقم {idx+1}")
        q_txt = st.text_input(f"اكتب نص السؤال ({idx+1}):", key=f"mq_{idx}")
        ans_1 = st.text_input(f"الجواب الصحيح والأكيد ({idx+1}):", key=f"ma1_{idx}")
        ans_2 = st.text_input(f"خيار خاطئ أ ({idx+1}):", key=f"ma2_{idx}")
        ans_3 = st.text_input(f"خيار خاطئ ب ({idx+1}):", key=f"ma3_{idx}")
        ans_4 = st.text_input(f"خيار خاطئ ج ({idx+1}):", key=f"ma4_{idx}")
        
        if q_txt and ans_1:
            manual_list.append({
                "السؤال": q_txt, "الخيار 1 - الصحيح": ans_1,
                "الخيار 2": ans_2 if ans_2 else "خيار خطأ 1",
                "الخيار 3": ans_3 if ans_3 else "خيار خطأ 2",
                "الخيار 4": ans_4 if ans_4 else "خيار خطأ 3"
            })
            
    if st.button("💾 حفظ باقة الأسئلة وإصدار الرقم السري", use_container_width=True):
        if len(manual_list) > 0:
            pool_code = str(random.randint(5000, 9999))
            db["manual_pools"][pool_code] = manual_list
            save_local_data("manual_pools.json", db["manual_pools"])
            st.success(f"🎉 تم حفظ مسابقتك بنجاح في السيرفر! الرمز المميز الخاص بها هو: **{pool_code}**")
            st.info("انسخ هذا الرقم الآن واذهب لقسم إنشاء الغرف لإطلاقها للمشتركين.")
        else:
            st.error("الرجاء تعبئة الأسئلة والأجوبة الصحيحة أولاً قبل الحفظ!")

# لوحة الموجه وإدارة الغرف
elif st.session_state.curr_page == "admin_mode":
    st.markdown("<h2 style='text-align:center; color:#0369A1;'>🏆 لوحة التحكم وإطلاق الغرف الحية</h2>", unsafe_allow_html=True)
    
    if 'my_live_room' not in st.session_state:
        mode_select = st.radio("⚙️ اختر نوع ونظام الأسئلة للجولة الحالية:", ["توليد تلقائي ذكي عبر جيمني AI", "استدعاء مسابقة يدوية محفوظة برقم مميز"])
        
        chosen_questions = []
        t_val = 30
        
        if mode_select == "توليد تلقائي ذكي عبر جيمني AI":
            q_src = st.radio("اختر الفئة المستهدفة:", ["قسم الأطفال والأبناء 👶", "قسم الكبار والشباب 🧔"])
            chosen_age = None
            if q_src == "قسم الأطفال والأبناء 👶":
                chosen_age = st.slider("حدد عمر الطفل بدقة لضبط جودة وصعوبة الأسئلة (من 6 إلى 17 سنة):", 6, 17, 10)
            q_topic = st.selectbox("اختر تصنيف ومجال الجولة الحالية:", ["إسلاميات", "لغة عربية", "علوم", "رياضيات", "اجتماعيات", "طبيعة وجغرافيا", "ثقافة عامة منوعة"])
            num_q = st.number_input("حدد عدد الأسئلة المطلوبة:", min_value=1, max_value=20, value=5)
            t_val = st.slider("الوقت المتاح لكل سؤال (ثواني):", 5, 60, 30)
            
            if st.button("🎲 إنشاء غرفتك عبر الذكاء الاصطناعي", use_container_width=True):
                with st.spinner("جاري صياغة أسئلة منوعة ونادرة لا تتكرر أبداً عبر جيمني... ⚡"):
                    chosen_questions = generate_questions_via_gemini(q_src, q_topic, int(num_q), "ar", chosen_age)
        else:
            input_pool_id = st.text_input("📝 أدخل رقم المسابقة المميز الذي قمت بحفظه مسبقاً:")
            t_val = st.slider("الوقت المتاح لكل سؤال (ثواني):", 5, 60, 30)
            if st.button("🔓 استدعاء الأسئلة وتشغيل الغرفة", use_container_width=True):
                if input_pool_id in db["manual_pools"]:
                    chosen_questions = db["manual_pools"][input_pool_id]
                    st.success("تم العثور على الأسئلة اليدوية بنجاح وتم ربطها بالغرفة الحية الحين!")
                else:
                    st.error("رقم المسابقة غير صحيح أو غير موجود على السيرفر!")
                    
        if len(chosen_questions) > 0:
            st.session_state.generated_room_code = str(random.randint(1000, 4999))
            rcode = st.session_state.generated_room_code
            st.session_state.my_live_room = rcode
            
            db["rooms"][rcode] = {
                "players": [], "status": "waiting", "current_q_idx": 0, 
                "questions": chosen_questions, "duration": t_val, 
                "scores": {}, "player_answers": {}, "q_start_time": time.time()
            }
            st.rerun()
    else:
        rid = st.session_state.my_live_room; rdata = db["rooms"].get(rid)
        if rdata:
            st.markdown(f"<div style='background-color:#0284C7; color:white; padding:15px; border-radius:12px; text-align:center; font-size:1.4rem;'>🎯 رقم الغرفة الحية للمشتركين الحين: <strong>{rid}</strong></div>", unsafe_allow_html=True)
            
            st.write(f"👥 عدد المتسابقين المتصلين حالياً: {len(rdata['players'])}")
            
            if rdata["status"] == "waiting":
                if st.button("🚀 إطلاق المسابقة وبدء البث الحي للمتسابقين", use_container_width=True): 
                    db["rooms"][rid]["status"] = "playing"; db["rooms"][rid]["q_start_time"] = time.time(); st.rerun()
            elif rdata["status"] == "playing":
                qi = rdata["current_q_idx"]; ql = rdata["questions"]
                if qi < len(ql):
                    st.markdown(f"<div class='question-text'>📊 السؤال الحالي ({qi+1}/{len(ql)}): {ql[qi]['السؤال']}</div>", unsafe_allow_html=True)
                    st.success(f"💡 الإجابة الصحيحة المعتمدة: **{ql[qi]['الخيار 1 - الصحيح']}**")
                    
                    # لوحة حية ومباشرة للموجه لمراقبة ورؤية إجابات المتسابقين واحداً تلو الآخر فوراً وبدقة
                    st.markdown("#### 👁️ شاشة رصد ومراقبة إجابات المشتركين اللحظية:")
                    for p in rdata["players"]:
                        p_ans = rdata["player_answers"].get(f"{qi}_{p}", "⏳ لم يعتمد إجابته بعد")
                        st.write(f"- **{p}:** {p_ans}")
                        
                    rem = max(0, int(rdata["duration"] - (time.time() - rdata["q_start_time"])))
                    st.warning(f"⏱️ العداد التنازلي المباشر: {rem} ثانية")
                    if rem <= 0 or st.button("➡️ الانتقال للسؤال التالي", use_container_width=True):
                        db["rooms"][rid]["current_q_idx"] += 1; db["rooms"][rid]["q_start_time"] = time.time(); st.rerun()
                else: 
                    db["rooms"][rid]["status"] = "finished"; st.rerun()
            elif rdata["status"] == "finished":
                st.markdown("<div class='leaderboard-box'>🏆 لوحة الفائزين النهائية 🏆</div>", unsafe_allow_html=True)
                sorted_scores = sorted(rdata["scores"].items(), key=lambda x: x[1], reverse=True)
                for rank, (p, s) in enumerate(sorted_scores):
                    st.write(f"### 🏅 المركز {rank+1}: **{p}** -> برصيد {s} نقطة كاملة!")
                    
            if st.button("🛑 إنهاء هذه الجولة وإغلاق الغرفة بالكامل", use_container_width=True):
                if rid in db["rooms"]: del db["rooms"][rid]
                del st.session_state.my_live_room; st.session_state.generated_room_code = None; st.rerun()

# دخول كمتسابق - تحسين الألوان والخطوط وخانات الإدخال لتكون واضحة جداً وعريضة
elif st.session_state.curr_page == "player_mode":
    st.markdown("<h2 style='text-align:center; color:#0369A1;'>🎮 ساحة المتسابقين ودخول المنافسة</h2>", unsafe_allow_html=True)
    
    if 'joined_live_room' not in st.session_state:
        st.markdown("<label class='input-label'>🔢 أدخل رقم الغرفة المكون من 4 أرقام:</label>", unsafe_allow_html=True)
        cc = st.text_input("", key="p_room_input", label_visibility="collapsed")
        
        st.markdown("<label class='input-label'>📝 أدخل اسمك الكريم للمنافسة الحية:</label>", unsafe_allow_html=True)
        cn = st.text_input("", key="p_name_input", label_visibility="collapsed")
        
        if st.button("🚪 دخول الغرفة واعتماد اسمي الحين", use_container_width=True):
            if cc in db["rooms"]: 
                if cn not in db["rooms"][cc]["players"]:
                    db["rooms"][cc]["players"].append(cn)
                    db["rooms"][cc]["scores"][cn] = 0
                st.session_state.joined_live_room = cc
                st.session_state.my_joined_name = cn
                st.success("🎉 تم اتصالك ودخولك بنجاح للغرفة الحية!")
                st.rerun()
            else:
                st.error("❌ عذراً، رقم الغرفة غير موجود حالياً أو أغلقت!")
    else:
        rid = st.session_state.joined_live_room; pname = st.session_state.my_joined_name; rdata = db["rooms"].get(rid)
        if rdata:
            st.markdown(f"<div style='background-color:#0EA5E9; color:white; padding:10px; border-radius:8px; text-align:center; font-size:1.1rem; font-weight:bold;'>أنت متصل الآن بالغرفة رقم: {rid} | المتسابق: {pname}</div>", unsafe_allow_html=True)
            
            if rdata["status"] == "waiting":
                st.info("⏳ خليك مستعد.. الموجه يجمع اللاعبين الحين وسيبدأ إطلاق الأسئلة فوراً!")
                if st.button("🔄 تحديث وانتظار الإشارة", use_container_width=True): st.rerun()
            elif rdata["status"] == "playing":
                qi = rdata["current_q_idx"]; ql = rdata["questions"]
                if qi < len(ql):
                    st.markdown(f"<div class='question-text'>❓ السؤال الحالي ({qi+1}): {ql[qi]['السؤال']}</div>", unsafe_allow_html=True)
                    c_ans = str(ql[qi]["Gl_1"] if "Gl_1" in ql[qi] else ql[qi]["الخيار 1 - الصحيح"])
                    
                    if f"sh_opts_{qi}" not in st.session_state:
                        opts = [c_ans, str(ql[qi]["الخيار 2"]), str(ql[qi]["الخيار 3"]), str(ql[qi]["الخيار 4"])]
                        random.shuffle(opts); st.session_state[f"sh_opts_{qi}"] = opts
                        
                    st.markdown("<p style='color:#1E3A8A; font-weight:bold; font-size:1.15rem; margin-bottom:2px;'>اختر جوابك الصحيح بكل ثقة:</p>", unsafe_allow_html=True)
                    sel = st.radio("", st.session_state[f"sh_opts_{qi}"], key=f"p_s_{qi}", label_visibility="collapsed")
                    
                    rem = max(0, int(rdata["duration"] - (time.time() - rdata["q_start_time"])))
                    st.markdown(f"<p style='color:#C2410C; font-weight:bold; font-size:1.2rem;'>⏳ الوقت المتبقي لديك: {rem} ثانية</p>", unsafe_allow_html=True)
                    
                    if st.button("✔️ اعتماد الإجابة الآن", key=f"btn_sub_{qi}", use_container_width=True):
                        rdata["player_answers"][f"{qi}_{pname}"] = sel
                        if sel == c_ans:
                            st.success("صح بطل كفو! إجابة ممتازة 🥳")
                            db["rooms"][rid]["scores"][pname] += 10
                        else:
                            st.error("❌ للأسف إجابة خاطئة ركز في القادم!")
                        time.sleep(1.2)
                        st.rerun()
            elif rdata["status"] == "finished":
                st.balloons()
                st.success("🏆 انتهت جولة التحدي والمنافسة بنجاح! طالع شاشة الموجه لمعرفة الفائز الأول!")

# صفحة اختبر نفسك (ثقّف نفسك) الفردية الفورية مع تنظيف شامل ومنع التكرار
elif st.session_state.curr_page == "culture_mode":
    st.markdown("<h2 style='text-align:center; color:#0369A1;'>🕹️ تحدي اختبر نفسك الفردي (ثقّف نفسك)</h2>", unsafe_allow_html=True)
    
    if 'solo_questions' not in st.session_state:
        st.write("### اختر إعدادات تحديك الفوري المخصص:")
        solo_topic = st.selectbox("اختر المجال أو الفئة:", ["إسلاميات", "لغة عربية", "علوم", "رياضيات", "اجتماعيات", "طبيعة وجغرافيا", "ثقافة عامة منوعة"])
        solo_count = st.slider("حدد عدد الأسئلة المطلوبة في هذه الجولة:", 1, 20, 5)
        
        if st.button("🎯 ابدأ إطلاق وتوليد المسابقة فوراً", use_container_width=True):
            with st.spinner("جاري صياغة أسئلة مخصصة نادرة وغير مكررة أبداً... 🔥"):
                st.session_state.solo_questions = generate_questions_via_gemini("Adults", solo_topic, int(solo_count), "ar")
                st.session_state.solo_idx = 0
                st.session_state.solo_score = 0
            st.rerun()
    else:
        sq = st.session_state.solo_questions; si = st.session_state.solo_idx
        if si < len(sq):
            st.markdown(f"<div class='question-text'>❓ السؤال {si+1}: {sq[si]['السؤال']}</div>", unsafe_allow_html=True)
            corr = str(sq[si]["الخيار 1 - الصحيح"])
            
            if f"solo_opt_{si}" not in st.session_state:
                opts = [corr, str(sq[si]["الخيار 2"]), str(sq[si]["الخيار 3"]), str(sq[si]["الخيار 4"])]
                random.shuffle(opts); st.session_state[f"solo_opt_{si}"] = opts
                
            st.markdown("<p style='color:#1E3A8A; font-weight:bold; font-size:1.15rem; margin-bottom:2px;'>اختر الإجابة الصحيحة:</p>", unsafe_allow_html=True)
            user_sel = st.radio("", st.session_state[f"sh_opts_{qi}" if 'qi' in locals() else f"solo_opt_{si}"], key=f"sl_r_{si}", label_visibility="collapsed")
            
            if st.button("✔️ تأكيد واعتماد الإجابة", use_container_width=True):
                if user_sel == corr:
                    st.success("صح بطل كفو! 🥳")
                    st.session_state.solo_score += 10
                else:
                    st.error("❌ للأسف إجابة خاطئة ركز في القادم!")
                    st.info(f"💡 الصح هو: {corr}")
                time.sleep(1.5)
                st.session_state.solo_idx += 1
                st.rerun()
        else:
            st.balloons()
            st.markdown(f"<div class='leaderboard-box'>🎉 انتهى التحدي بنجاح! رصيدك الكلي: {st.session_state.solo_score} نقطة!</div>", unsafe_allow_html=True)
            if st.button("🔄 بدء جولة تحدي جديدة بمجال مغاير وأسئلة جديدة", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith("solo_opt_") or key.startswith("sl_r_"): del st.session_state[key]
                del st.session_state.solo_questions
                st.rerun()

# تواصل معنا
elif st.session_state.curr_page == "contact_mode":
    st.markdown("### 📞 تواصل معنا")
    with st.form("contact_advanced"):
        c_name = st.text_input("📝 اسمك الكريم:")
        c_phone = st.text_input("📱 رقم الموبايل:")
        c_email = st.text_input("📧 البريد الإلكتروني:")
        c_msg_txt = st.text_area("💬 رسالتك أو اقتراحك:")
        if st.form_submit_button("🚀 إرسال الرسالة الآن"):
            if c_name and c_msg_txt:
                db["messages"].append({"name": c_name, "phone": c_phone, "email": c_email, "msg": c_msg_txt})
                save_local_data("messages.json", db["messages"])
                st.success("🎉 تم الإرسال بنجاح!")

st.write("---")

# 📥 صندوق الإعدادات والرسائل والزيارات التراكمية التاريخية بأسفل الصفحة
with st.expander("⚙️ إعدادات لوحة الموجه (خاص بالمدير فقط)"):
    if not st.session_state.admin_authenticated:
        admin_pass = st.text_input("🔑 أدخل الرمز السري لوحة الموجه:", type="password", key="main_admin_pass")
        if st.button("🔓 تأكيد الدخول", key="main_admin_confirm"):
            if admin_pass == "Abdulelah@2026":
                st.session_state.admin_authenticated = True
                st.rerun()
            else: st.error("❌ الرمز السري غير صحيح!")
    else:
        if st.button("🚪 خروج من الإدارة", key="main_admin_logout"):
            st.session_state.admin_authenticated = False
            st.rerun()
        st.write("---")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric(label="📊 المتواجدون حالياً", value="1 منشط")
        col_m2.metric(label="📈 إجمالي الزيارات التاريخية التراكمية المحفوظة", value=f"{db['total_visitors']} زيارة")
        
        st.write("---")
        st.markdown("#### 📥 صندوق الوارد لرسائل تواصل معنا")
        if len(db["messages"]) == 0: st.info("لا توجد رسائل واردة حالياً.")
        else:
            for idx, msg in enumerate(db["messages"]):
                with st.expander(f"✉️ من: {msg.get('name', 'مجهول')}"):
                    st.write(f"**الجوال:** {msg.get('phone', 'غير متوفر')}")
                    st.write(f"**البريد:** {msg.get('email', 'غير متوفر')}")
                    st.write(f"**الرسالة:** {msg.get('msg', '')}")
                    if st.button("🗑️ حذف الرسالة", key=f"del_main_{idx}"):
                        db["messages"].pop(idx)
                        save_local_data("messages.json", db["messages"])
                        st.rerun()

st.markdown("<div class='footer-text'>تطوير عبد الإله العنزي | Developed by Abdulelah Al-Enazi</div>", unsafe_allow_html=True)
