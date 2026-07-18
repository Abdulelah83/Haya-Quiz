import streamlit as st
import pandas as pd
import time
import random
import os
import json
from datetime import datetime
if 'seen_questions' not in st.session_state: st.session_state.seen_questions = []

# 1. إعدادات الصفحة والهوية البصرية واستهداف ألوان السماء المريحة للعين
st.set_page_config(
    page_title="منصة هيا للمسابقات الاحترافية | Haya-Quiz Pro", 
    page_icon="🎯", 
    layout="wide"
)

# إجبار المتصفح وسفاري على إلغاء القائمة الجانبية تماماً لتنظيف الشاشة
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    .stApp { background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%) !important; }
    
    /* ضبط جودة ووضوح الخطوط لضمان القراءة الممتازة */
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
        padding: 18px;
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
    .dashboard-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
        border: 2px solid #BAE6FD;
        margin-bottom: 15px;
    }
    .footer-text { text-align: center; color: #0369A1; font-size: 1.1rem; font-weight: bold; padding: 20px 0; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# تهيئة متغيرات الجلسة الأساسية للحفاظ على جوهر النظام
if 'curr_page' not in st.session_state: st.session_state.curr_page = "home"
if 'generated_room_code' not in st.session_state: st.session_state.generated_room_code = None
if 'admin_authenticated' not in st.session_state: st.session_state.admin_authenticated = False
if 'lang' not in st.session_state: st.session_state.lang = "ar"

# رابط جوجل شيت الخاص بك محول برمجياً لقراءة البيانات الفورية كمستند CSV
SHEET_ID = "1_Is0imnUnhiyqG49qlvBRdAdbGCADsoNjbdAG2ID7II"
GOOGLE_SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# دالة جلب الأسئلة المباشرة واللحظية من قوقل شيت وتطهير البيانات
@st.cache_data(ttl=2, show_spinner=False)
def load_questions_from_google_sheet():  # تقليل الكاش لثانيتين لضمان المزامنة الفورية عند التعديل في الشيت

    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

def fetch_custom_questions(df, category_filter, topic_filter, count, age_filter=None):
    if df.empty: return []
    filtered_df = df[(df['الفئة'].str.strip() == category_filter) & (df['التصنيف'].str.strip() == topic_filter)]
    
    # منع التكرار
    available_df = filtered_df[~filtered_df['السؤال'].isin(st.session_state.seen_questions)]
    if len(available_df) == 0:
        st.session_state.seen_questions = [] 
        available_df = filtered_df
        
    pool = []
    for _, row in available_df.iterrows():
        pool.append({
            "السؤال": str(row['السؤال']).strip(),
            "الخيار 1 - الصحيح": str(row['الجواب الصحيح']).strip(),
            "الخيار 2": str(row['خيار خاطئ 1']).strip(),
            "الخيار 3": str(row['خيار خاطئ 2']).strip(),
            "الخيار 4": str(row['خيار خاطئ 3']).strip()
        })
    
    random.shuffle(pool)
    selected = pool[:min(count, len(pool))]
    
    # تسجيل الأسئلة الجديدة في الذاكرة
    for q in selected: st.session_state.seen_questions.append(q["السؤال"])
    return selected

# دوال الذاكرة المحلية والزيارات التراكمية التاريخية للمنصة
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

# هيدر التنقل العلوي
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 1])
if col_nav1.button("🏠 الرئيسية", use_container_width=True): st.session_state.curr_page = "home"; st.rerun()
if col_nav2.button("📞 تواصل معنا", use_container_width=True): st.session_state.curr_page = "contact_mode"; st.rerun()
if col_nav3.button("🔄 تحديث الصفحة", use_container_width=True): st.rerun()
current_lang_label = "🌐 English" if st.session_state.lang == "ar" else "🌐 العربية"
if col_nav4.button(current_lang_label, use_container_width=True):
    st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
    st.rerun()

st.write("---")

# جلب قاعدة الأسئلة المحدثة فوراً في الذاكرة الحالية
sheet_data = load_questions_from_google_sheet()

# الصفحة الرئيسية للمنصة
if st.session_state.curr_page == "home":
    st.markdown("<h2 style='text-align:center; color:#0369A1;'>مسابقات هيا   🎯</h2>", unsafe_allow_html=True)
    if os.path.exists("my_kids.png"): 
        st.image("my_kids.png", use_container_width=True)
        
    st.markdown("<p style='text-align:center; font-size:1.3rem;'>جاهزون للتحدي والمنافسة الحية المباشرة الحين؟</p>", unsafe_allow_html=True)
    
    if st.button("🏆 إنشاء وإدارة مسابقة ذكية حية", use_container_width=True): st.session_state.curr_page = "admin_mode"; st.rerun()
    if st.button("📝 كتابة اسئلة يدوية مخصّصة", use_container_width=True): st.session_state.curr_page = "manual_setup_mode"; st.rerun()
    if st.button("🎮 دخول كمتسابق في جولة حية", use_container_width=True): st.session_state.curr_page = "player_mode"; st.rerun()
    if st.button("🕹️ تحدي اختبر نفسك الفردي", use_container_width=True): st.session_state.curr_page = "culture_mode"; st.rerun()

# نظام الموجه لتركيب وحفظ أسئلة يدوية مخصصة
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
        else:
            st.error("الرجاء تعبئة الأسئلة والأجوبة الصحيحة أولاً قبل الحفظ!")

# لوحة التحكم وإطلاق الغرف الحية
elif st.session_state.curr_page == "admin_mode":
    st.markdown("<h2 style='text-align:center; color:#0369A1;'>🏆 لوحة التحكم وإطلاق الغرف الحية</h2>", unsafe_allow_html=True)
    
    if 'my_live_room' not in st.session_state:
        mode_select = st.radio("⚙️ اختر نظام جلب الأسئلة للجولة الحالية:", ["سحب تلقائي مباشر من جدول Google Sheets", "استدعاء مسابقة يدوية محفوظة برقم مميز"])
        chosen_questions = []
        t_val = 30
        live_q_weight = st.selectbox("🎯 اختر وزن/درجة كل سؤال في هذه الجولة الحية:", [5, 10, 15, 20], index=1)
        
        if mode_select == "سحب تلقائي مباشر من جدول Google Sheets":
            q_src = st.radio("اختر الفئة المستهدفة:", ["قسم الأطفال والأبناء 👶", "قسم الكبار والشباب 🧔"])
            chosen_age = None
            if q_src == "قسم الأطفال والأبناء 👶":
                chosen_age = st.slider("حدد عمر الطفل بدقة لفلترة وتطابق الأسئلة المتوفرة في الشيت (من 6 إلى 17 سنة):", 6, 17, 7)
                
            q_topic = st.selectbox("اختر تصنيف ومجال الجولة الحالية:", ["إسلاميات", "لغة عربية", "علوم", "رياضيات", "اجتماعيات", "طبيعة وجغرافيا", "ثقافة عامة"])
            num_q = st.number_input("حدد عدد الأسئلة المطلوبة للحلبة التنافسية:", min_value=1, max_value=50, value=5)
            t_val = st.slider("الوقت المتاح لكل سؤال (ثواني):", 5, 60, 30)
            
            if st.button("🎲 استخراج الأسئلة الفورية وإطلاق الغرفة الحية الحين", use_container_width=True):
                target_tag = "أطفال" if q_src == "قسم الأطفال والأبناء 👶" else "كبار"
                chosen_questions = fetch_custom_questions(sheet_data, target_tag, q_topic, int(num_q), chosen_age)
                if len(chosen_questions) == 0:
                    st.error(f"⚠️ لم نجد أسئلة كافية في جدول قوقل تطابق هذه الفلاتر: ({target_tag} - {q_topic}). يرجى إضافة المزيد في الشيت وسيقرأها الموقع تلقائياً!")
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
                "scores": {}, "correct_counts": {}, "player_answers": {}, 
                "q_weight": live_q_weight, "q_start_time": time.time()
            }
            st.rerun()
    else:
        rid = st.session_state.my_live_room; rdata = db["rooms"].get(rid)
        if rdata:
            st.markdown(f"<div style='background-color:#0284C7; color:white; padding:15px; border-radius:12px; text-align:center; font-size:1.4rem;'>🎯 رقم الغرفة الحية للمشتركين الحين: <strong>{rid}</strong> | وزن السؤال: {rdata.get('q_weight', 10)} نقاط</div>", unsafe_allow_html=True)
            st.write(f"👥 عدد المتسابقين المتصلين حالياً: {len(rdata['players'])}")
            
            if rdata["status"] == "waiting":
                if st.button("🚀 إطلاق المسابقة وبدء البث الحي للمتسابقين", use_container_width=True): 
                    db["rooms"][rid]["status"] = "playing"; db["rooms"][rid]["q_start_time"] = time.time(); st.rerun()
            elif rdata["status"] == "playing":
                qi = rdata["current_q_idx"]; ql = rdata["questions"]
                if qi < len(ql):
                    st.markdown(f"<div class='question-text'>📊 السؤال الحالي ({qi+1}/{len(ql)}): {ql[qi]['السؤال']}</div>", unsafe_allow_html=True)
                    st.success(f"💡 الإجابة الصحيحة المعتمدة في الجدول: **{ql[qi]['الخيار 1 - الصحيح']}**")
                    
                    st.markdown("#### 👁️ شاشة رصد ومراقبة إجابات المشتركين اللحظية:")
                    for p in rdata["players"]:
                        p_ans = rdata["player_answers"].get(f"{qi}_{p}", "⏳ لم يعتمد إجابته بعد")
                        st.write(f"- **{p}:** {p_ans}")
                        
                    rem = max(0, int(rdata["duration"] - (time.time() - rdata["q_start_time"])))
                    st.warning(f"⏱️ العداد التنازلي المباشر: {rem} ثانية")
                    
                    if st.button("⏩ الانتقال للسؤال التالي فوراً", use_container_width=True):
                        db["rooms"][rid]["current_q_idx"] += 1
                        db["rooms"][rid]["q_start_time"] = time.time()
                        st.rerun()
                else: 
                    db["rooms"][rid]["status"] = "finished"; st.rerun()
            elif rdata["status"] == "finished":
                st.markdown("<h2 style='text-align:center; color:#0369A1;'>🏆 الداشبورد ولوحة الفائزين النهائية 🏆</h2>", unsafe_allow_html=True)
                total_q = len(rdata["questions"])
                weight = rdata.get("q_weight", 10)
                max_score = total_q * weight
                sorted_scores = sorted(rdata["scores"].items(), key=lambda x: x[1], reverse=True)
                
                for rank, (p, score) in enumerate(sorted_scores):
                    corrects = rdata.get("correct_counts", {}).get(p, 0)
                    wrongs = total_q - corrects
                    pct = round((score / max_score) * 100) if max_score > 0 else 0
                    
                    st.markdown(f"""
                    <div class='dashboard-card'>
                        <h3 style='color:#0284C7;'>🏅 المركز {rank+1}: {p}</h3>
                        <h2 style='color:#0369A1;'>النتيجة: {score} / {max_score} نقطة ({pct}%)</h2>
                        <p style='color:#15803D;'>✅ الإجابات الصحيحة: {corrects} | ❌ الخاطئة: {wrongs}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            if st.button("🛑 إنهاء هذه الجولة وإغلاق الغرفة بالكامل", use_container_width=True):
                if rid in db["rooms"]: del db["rooms"][rid]
                del st.session_state.my_live_room; st.session_state.generated_room_code = None; st.rerun()

# دخول كمتسابق
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
                    db["rooms"][cc]["correct_counts"][cn] = 0
                st.session_state.joined_live_room = cc
                st.session_state.my_joined_name = cn
                st.success("🎉 تم اتصالك ودخولك بنجاح للغرفة الحية!")
                st.rerun()
            else:
                st.error("❌ عذراً، رقم الغرفة غير موجود حالياً أو أغلقت!")
    else:
        rid = st.session_state.joined_live_room; pname = st.session_state.my_joined_name; rdata = db["rooms"].get(rid)
        if not rdata or pname not in rdata.get("players", []):
            st.warning("⚠️ تم إغلاق الغرفة أو الخروج منها.")
            if st.button("🔄 العودة لصفحة الدخول"):
                if 'joined_live_room' in st.session_state: del st.session_state.joined_live_room
                st.rerun()
        else:
            st.markdown(f"<div style='background-color:#0EA5E9; color:white; padding:10px; border-radius:8px; text-align:center; font-size:1.1rem; font-weight:bold;'>أنت متصل الآن بالغرفة رقم: {rid} | المتسابق: {pname}</div>", unsafe_allow_html=True)
            if st.button("🔴 الخروج والإنسحاب من المسابقة", key="player_exit_btn", use_container_width=True):
                if pname in rdata["players"]: rdata["players"].remove(pname)
                if pname in rdata["scores"]: del rdata["scores"][pname]
                del st.session_state.joined_live_room; del st.session_state.my_joined_name; st.rerun()
            
            st.write("---")
            if rdata["status"] == "waiting":
                st.info("⏳ خليك مستعد.. الموجه يجمع اللاعبين الحين وسيبدأ إطلاق الأسئلة فوراً!")
                if st.button("🔄 تحديث وانتظار الإشارة", use_container_width=True): st.rerun()
            elif rdata["status"] == "playing":
                qi = rdata["current_q_idx"]; ql = rdata["questions"]
                if "p_last_q" not in st.session_state: st.session_state.p_last_q = qi
                if qi != st.session_state.p_last_q:
                    st.session_state.p_last_q = qi
                    st.rerun()
                
                if qi < len(ql):
                    st.markdown(f"<div class='question-text'>❓ السؤال الحالي ({qi+1}/{len(ql)}): {ql[qi]['السؤال']}</div>", unsafe_allow_html=True)
                    c_ans = str(ql[qi]["الخيار 1 - الصحيح"])
                    if f"sh_opts_{qi}" not in st.session_state:
                        opts = [c_ans, str(ql[qi]["الخيار 2"]), str(ql[qi]["الخيار 3"]), str(ql[qi]["الخيار 4"])]
                        random.shuffle(opts)
                        st.session_state[f"sh_opts_{qi}"] = opts
                        
                    st.markdown("<p style='color:#1E3A8A; font-weight:bold; font-size:1.15rem; margin-bottom:2px;'>اختر جوابك الصحيح بكل ثقة:</p>", unsafe_allow_html=True)
                    sel = st.radio("", st.session_state[f"sh_opts_{qi}"], key=f"p_s_{qi}", label_visibility="collapsed")
                    
                    ans_key = f"{qi}_{pname}"
                    has_answered = ans_key in rdata["player_answers"]
                    
                    if not has_answered:
                        if st.button("✔️ اعتماد الإجابة الآن", key=f"btn_sub_{qi}", use_container_width=True):
                            rdata["player_answers"][ans_key] = sel
                            weight = rdata.get("q_weight", 10)
                            if sel == c_ans:
                                db["rooms"][rid]["scores"][pname] += weight
                                db["rooms"][rid]["correct_counts"][pname] += 1
                            st.rerun()
                    else:
                        chosen_val = rdata["player_answers"][ans_key]
                        if chosen_val == c_ans: st.success("🎉 إجابة صحيحة وكفو! ممتاز جداً!")
                        else: st.error(f"❌ إجابة خاطئة! الإجابة الصحيحة هي: **{c_ans}**")
                        if st.button("⚡ جاهز للسؤال التالي (تحديث الشاشة)", key=f"sync_next_{qi}", use_container_width=True): st.rerun()
                else:
                    st.info("⏳ بانتظار إعلان النتائج النهائية من الموجه.")
                    if st.button("🔄 تحديث ورؤية النتيجة النهائية", key="refresh_final_player"): st.rerun()
            elif rdata["status"] == "finished":
                st.balloons()
                total_q = len(rdata["questions"]); weight = rdata.get("q_weight", 10); max_score = total_q * weight
                my_score = rdata["scores"].get(pname, 0); corrects = rdata.get("correct_counts", {}).get(pname, 0); wrongs = total_q - corrects
                pct = round((my_score / max_score) * 100) if max_score > 0 else 0
                
                st.markdown("<h2 style='text-align:center; color:#0369A1;'>📊 داشبورد ونتيجتك النهائية</h2>", unsafe_allow_html=True)
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1: st.markdown(f"<div class='dashboard-card'><h3>🎯 مجموع النقاط</h3><h1>{my_score} / {max_score}</h1><p>النسبة: {pct}%</p></div>", unsafe_allow_html=True)
                with col_p2: st.markdown(f"<div class='dashboard-card'><h3>✅ الصحيحة</h3><h1>{corrects}</h1><p>من {total_q} سؤال</p></div>", unsafe_allow_html=True)
                with col_p3: st.markdown(f"<div class='dashboard-card'><h3>❌ الخاطئة</h3><h1>{wrongs}</h1><p>أسئلة لم توفق بها</p></div>", unsafe_allow_html=True)

# صفحة اختبر نفسك الفردية (ثقف نفسك بسحب مباشر وحقيقي من جوجل شيت)
elif st.session_state.curr_page == "culture_mode":
    st.markdown("<h2 style='text-align:center; color:#0369A1;'>🕹️ تحدي اختبر نفسك الفردي (ثقّف نفسك)</h2>", unsafe_allow_html=True)
    
    if 'solo_questions' not in st.session_state:
        st.write("### ⚙️ اختر إعدادات تحديك الفوري المخصص:")
        solo_target = st.radio("اختر الفئة المستهدفة للتحدي:", ["قسم الأطفال والأبناء 👶", "قسم الكبار والشباب 🧔"])
        solo_age = None
        if solo_target == "قسم الأطفال والأبناء 👶":
            solo_age = st.slider("حدد عمر الطفل بدقة (من 6 إلى 17 سنة):", 6, 17, 7)
            
        solo_topic = st.selectbox("اختر المجال أو الفئة السحابية:", ["إسلاميات", "لغة عربية", "علوم", "رياضيات", "اجتماعيات", "طبيعة وجغرافيا", "ثقافة عامة"])
        solo_count = st.slider("حدد عدد الأسئلة المطلوبة في هذه الجولة:", 1, 20, 5)
        q_weight = st.selectbox("🎯 اختر وزن/درجة كل سؤال في هذه الجولة:", [5, 10, 15, 20], index=1)
        
        if st.button("🎯 ابدأ التحدي الفوري من بنك جوجل شيت", use_container_width=True):
            target_label = "أطفال" if solo_target == "قسم الأطفال والأبناء 👶" else "كبار"
            fetched_qs = fetch_custom_questions(sheet_data, target_label, solo_topic, int(solo_count), solo_age)
            
            if len(fetched_qs) > 0:
                # --- إضافة سطر الخلط هنا لمنع التكرار ---
                import random 
                random.shuffle(fetched_qs)
                # ----------------------------------------
                
                st.session_state.solo_questions = fetched_qs
                st.session_state.solo_idx = 0
                st.session_state.solo_correct_cnt = 0
                st.session_state.solo_wrong_cnt = 0
                st.session_state.q_weight = q_weight
                st.rerun()

            else:
                st.error(f"⚠️ لم يعثر النظام على أسئلة كافية تطابق الخيارات المحددة في الشيت حالياً. يرجى إضافة الأسئلة في الشيت لتظهر هنا فوراً!")
    else:
        sq = st.session_state.solo_questions; si = st.session_state.solo_idx
        weight = st.session_state.get('q_weight', 10)
        
        if si < len(sq):
            st.markdown(f"<div class='question-text'>❓ السؤال ({si+1}/{len(sq)}): {sq[si]['السؤال']}</div>", unsafe_allow_html=True)
            corr = str(sq[si]["الخيار 1 - الصحيح"])
            if f"solo_opt_{si}" not in st.session_state:
                opts = [corr, str(sq[si]["الخيار 2"]), str(sq[si]["الخيار 3"]), str(sq[si]["الخيار 4"])]
                random.shuffle(opts)
                st.session_state[f"solo_opt_{si}"] = opts
                
            st.markdown("<p style='color:#1E3A8A; font-weight:bold; font-size:1.15rem; margin-bottom:2px;'>اختر الإجابة الصحيحة:</p>", unsafe_allow_html=True)
            user_sel = st.radio("", st.session_state[f"solo_opt_{si}"], key=f"sl_r_{si}", label_visibility="collapsed")
            
            if st.button("✔️ تأكيد واعتماد الإجابة", use_container_width=True):
                if user_sel == corr:
                    st.success("صح بطل كفو! 🥳")
                    st.session_state.solo_correct_cnt += 1
                else:
                    st.error(f"❌ للأسف إجابة خاطئة! الإجابة الصحيحة هي: **{corr}**")
                    st.session_state.solo_wrong_cnt += 1
                time.sleep(1.2)
                st.session_state.solo_idx += 1
                st.rerun()
        else:
            st.balloons()
            total_q = len(sq); correct_cnt = st.session_state.solo_correct_cnt; wrong_cnt = st.session_state.solo_wrong_cnt
            earned_score = correct_cnt * weight; max_score = total_q * weight; percentage = round((earned_score / max_score) * 100) if max_score > 0 else 0
            
            st.markdown("<h2 style='text-align:center; color:#0369A1;'>📊 لوحة النتائج والداشبورد النهائي</h2>", unsafe_allow_html=True)
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1: st.markdown(f"<div class='dashboard-card'><h3>🎯 الدرجة الكلية</h3><h1>{earned_score} / {max_score}</h1><p>النسبة المئوية: {percentage}%</p></div>", unsafe_allow_html=True)
            with col_d2: st.markdown(f"<div class='dashboard-card'><h3>✅ الصحيحة</h3><h1>{correct_cnt}</h1><p>من إجمالي {total_q} سؤال</p></div>", unsafe_allow_html=True)
            with col_d3: st.markdown(f"<div class='dashboard-card'><h3>❌ الخاطئة</h3><h1>{wrong_cnt}</h1><p>أسئلة تحتاج لمراجعة</p></div>", unsafe_allow_html=True)
                
            if st.button("🔄 بدء جولة تحدي جديدة بمجال آخر", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith("solo_opt_") or key.startswith("sl_r_"): del st.session_state[key]
                del st.session_state.solo_questions; st.rerun()

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

# صندوق الإعدادات والرسائل ولوحة إحصائيات الأسئلة والأعمار المزامنة التاريخية بأسفل الصفحة
with st.expander("⚙️"):
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
        
        st.markdown("<h3 style='color:#0284C7;'>📊 لوحة رصد وإحصائيات الأسئلة التزامنية التلقائية (من جوجل شيت)</h3>", unsafe_allow_html=True)
        if not sheet_data.empty:
            total_questions_in_sheet = len(sheet_data)
            kids_q_count = len(sheet_data[sheet_data['الفئة'].str.strip() == 'أطفال'])
            adults_q_count = len(sheet_data[sheet_data['الفئة'].str.strip() == 'كبار'])
            
            col_st1, col_st2, col_st3 = st.columns(3)
            with col_st1: st.metric(label="📈 العدد الكلي للأسئلة المكتشفة في الشيت حالياً", value=f"{total_questions_in_sheet} سؤال")
            with col_st2: st.metric(label="👶 إجمالي أسئلة قسم الأطفال والأبناء", value=f"{kids_q_count} سؤال")
            with col_st3: st.metric(label="🧔 إجمالي أسئلة قسم الشباب والكبار", value=f"{adults_q_count} سؤال")
                
            st.markdown("#### 📁 أعداد توزيع الأسئلة الحالية بالتفصيل حسب التصنيفات:")
            topics_list = ["إسلاميات", "لغة عربية", "علوم", "رياضيات", "اجتماعيات", "طبيعة وجغرافيا", "ثقافة عامة"]
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            cols_cycle = [col_t1, col_t2, col_t3, col_t4]
            for i, t_name in enumerate(topics_list):
                count_t = len(sheet_data[sheet_data['التصنيف'].str.strip() == t_name])
                with cols_cycle[i % 4]: st.write(f"- **{t_name}:** {count_t} سؤال")
        else:
            st.info("لم يتم جلب أي بيانات أسئلة بعد، يرجى ملء جدول جوجل شيت بالبيانات.")

        st.write("---")
        col_m1, col_m2 = st.columns(2)
        st.metric(label="📊 المتواجدون حالياً", value="1 منشط")
        db_visitors = db['total_visitors']
        st.metric(label="📈 إجمالي الزيارات التاريخية التراكمية المحفوظة", value=f"{db_visitors} زيارة")

st.markdown("<div class='footer-text'>تطوير عبد الإله العنزي | Developed by Abdulelah Al-Enazi</div>", unsafe_allow_html=True)
