import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="الحقيبة الرمضانية - هندسة وعمارة",
    page_icon="🌙",
    layout="centered"
)

# --- 2. تنسيق CSS (إصلاح الألوان والخطوط) ---
st.markdown("""
<style>
    /* اتجاه الصفحة لليمين */
    .stApp { direction: rtl; text-align: right; }
    
    /* الخطوط والعناوين */
    h1, h2, h3 { font-family: 'Tajawal', sans-serif; color: #1f77b4; text-align: center; }
    
    /* --- إصلاح مشكلة الكروت في الوضع الليلي --- */
    /* إجبار الخلفية تكون بيضاء */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #d1d5db;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* إجبار لون العنوان يكون رمادي */
    div[data-testid="stMetricLabel"] {
        color: #555555 !important;
        font-weight: bold;
    }
    
    /* إجبار لون الرقم يكون أسود */
    div[data-testid="stMetricValue"] {
        color: #000000 !important;
    }

    /* توسيط التبويبات */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. صورة البوستر (اختياري) ---
try:
    st.image("poster.jpeg", use_container_width=True) 
except:
    pass

# --- 4. تحميل وتنظيف البيانات ---
# الرابط الخاص بك
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpVaFIFaIybxYXbO6ECjCzUFVRiVERCTKy6D-hFRPyKkzwzwDgJamRCuDBHfKCsg85m5vM9fBbVf1U/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        
        # تنظيف أسماء الأعمدة (إزالة أي مسافات زائدة)
        df.columns = df.columns.str.strip()
        
        # --- معالجة ذكية للنصوص (توحيد الهمزات) ---
        if 'المستوى' in df.columns:
            # تحويل الكل لنص ومسح المسافات
            df['المستوى'] = df['المستوى'].astype(str).str.strip()
            # استبدال الكلمات المحتملة بالكتابة الصحيحة
            df['المستوى'] = df['المستوى'].str.replace('ألاول', 'الأول')
            df['المستوى'] = df['المستوى'].str.replace('الاول', 'الأول')
            df['المستوى'] = df['المستوى'].str.replace('الاولي', 'الأول')
        
        # --- تنظيف الأرقام ---
        # إزالة الفواصل والمسافات وتحويلها لرقم، والخانة الفاضية تبقى صفر
        df['المبلغ'] = df['المبلغ'].astype(str).str.replace(',', '').str.replace(' ', '')
        df['المبلغ'] = pd.to_numeric(df['المبلغ'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        return pd.DataFrame()

# استدعاء البيانات
df = load_data(sheet_url)

if not df.empty:
    # --- 5. الإحصائيات العامة (العدادات) ---
    st.title("🌙 وسابقوا..")
    st.markdown("<h5 style='text-align: center; color: gray;'>منافسة الخير - كلية الهندسة والعمارة</h5>", unsafe_allow_html=True)
    
    # الثوابت
    TARGET_AMOUNT = 38000000
    BAG_COST = 190000
    TARGET_BAGS = 200

    # الحسابات
    total_collected = df['المبلغ'].sum()
    bags_collected = int(total_collected / BAG_COST)
    progress = total_collected / TARGET_AMOUNT

    # عرض الكروت
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 المجموع الكلي", f"{total_collected:,.0f}")
    with col2:
        st.metric("🎒 حقيبة رمضانية", f"{bags_collected}")
    with col3:
        st.metric("📉 نسبة الإنجاز", f"{progress*100:.1f}%")

    # شريط التقدم
    st.progress(min(progress, 1.0))
    st.divider()

    # --- 6. ساحة التنافس (الرسوم البيانية) ---
    st.subheader("🏆 ترتيب الأقسام حسب المستويات")
    
    # القائمة الصحيحة (تم توحيد البيانات عليها في دالة التحميل)
    levels_order = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس"]
    
    # إنشاء التبويبات
    tabs = st.tabs(levels_order)
    
    for i, level_name in enumerate(levels_order):
        with tabs[i]:
            # فلترة البيانات للمستوى الحالي
            current_level_data = df[df['المستوى'] == level_name]
            
            # تجميع المبالغ (عشان لو القسم مكرر يجمعه)
            # بنستخدم groupby عشان نضمن إن كل قسم يظهر مرة واحدة بمجموع مبالغه
            level_df = current_level_data.groupby('القسم')['المبلغ'].sum().reset_index()
            
            # التحقق إنو في أقسام مسجلة في الشيت (حتى لو رصيدها صفر)
            if not level_df.empty:
                # ترتيب حسب المبلغ (الأعلى فوق)
                level_df = level_df.sort_values(by='المبلغ', ascending=True)

                # الرسم البياني
                fig = px.bar(
                    level_df, 
                    x='المبلغ', 
                    y='القسم', 
                    orientation='h',
                    text='المبلغ', 
                    color='المبلغ', 
                    color_continuous_scale='Blues',
                    title=f"منافسة {level_name}"
                )
                
                # خط الهدف (3 حقائب)
                fig.add_vline(x=570000, line_dash="dash", line_color="green", annotation_text="هدف 3 حقائب")
                
                # تحسين شكل الرسم
                fig.update_layout(xaxis_title="", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', height=400)
                # تنسيق الرقم الظاهر (عشان يظهر كامل حتى لو صفر)
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # رسالة للمتصدر (تظهر فقط لو المبلغ أكبر من صفر)
                leader = level_df.iloc[-1]
                if leader['المبلغ'] > 0:
                    st.success(f"🥇 المتصدر: {leader['القسم']} ({leader['المبلغ']:,})")
            else:
                st.info(f"لا توجد بيانات مسجلة لـ {level_name} حتى الآن.")

    st.divider()
    
    # --- 7. الحسابات البنكية ---
    with st.expander("💳 اضغط هنا لعرض أرقام الحسابات وتفاصيل التحويل", expanded=False):
        st.markdown("""
        <div style="text-align: center; direction: rtl;">
        
        **بنك الخرطوم (بنكك):** <br>
        `4195521` <br>
        (زبيدة فؤاد عثمان)
        <br><br>
        
        **بنك فيصل الإسلامي (فوري):** <br>
        `52092340` <br>
        (محمد جلال الدين الشيخ)
        <br><br>
        
        **بنك أمدرمان الوطني (أوكاش):** <br>
        `643344` <br>
        (محمد جلال الدين الشيخ)
        
        <hr>
        📲 **لإرسال الإشعار وتأكيد التحويل:** <br>
        `0112551093`
        </div>
        """, unsafe_allow_html=True) 

else:
    st.error("⚠️ لم يتم تحميل البيانات. تأكد من أن الرابط يعمل وأن الملف منشور بصيغة CSV.")

# زر تحديث يدوي
if st.button('🔄 تحديث البيانات'):
    st.cache_data.clear()
    st.rerun()
