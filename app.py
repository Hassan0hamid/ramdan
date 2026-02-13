import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="الحقيبة الرمضانية - هندسة وعمارة",
    page_icon="🌙",
    layout="centered"
)

# --- 2. تنسيق CSS (تعديل العناوين لتكون واضحة) ---
st.markdown("""
<style>
    /* اتجاه الصفحة لليمين */
    .stApp { direction: rtl; text-align: right; }
    
    /* الخطوط والعناوين */
    h1, h2, h3 { font-family: 'Tajawal', sans-serif; color: #1f77b4; text-align: center; }
    
    /* --- تصميم الكروت (المربعات) --- */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important; /* خلفية بيضاء نقية */
        padding: 15px;
        border-radius: 15px; /* زوايا دائرية أكثر */
        border: 2px solid #e0e0e0; /* إطار رمادي خفيف */
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* ظل خفيف */
    }
    
    /* --- تنسيق العناوين (الكلام الفوق الرقم) --- */
    div[data-testid="stMetricLabel"] {
        color: #1f77b4 !important; /* لون أزرق واضح */
        font-size: 18px !important; /* تكبير الخط */
        font-weight: 900 !important; /* خط عريض جداً */
        margin-bottom: 5px !important;
    }
    
    /* --- تنسيق الرقم نفسه --- */
    div[data-testid="stMetricValue"] {
        color: #000000 !important; /* أسود غامق */
        font-size: 28px !important; /* رقم كبير */
        font-weight: bold !important;
    }

    /* توسيط التبويبات */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. صورة البوستر ---
try:
    st.image("poster.jpeg", use_container_width=True) 
except:
    pass

# --- 4. تحميل البيانات ---
# الرابط الخاص بك
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpVaFIFaIybxYXbO6ECjCzUFVRiVERCTKy6D-hFRPyKkzwzwDgJamRCuDBHfKCsg85m5vM9fBbVf1U/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        # تنظيف البيانات
        df.columns = df.columns.str.strip()
        if 'المستوى' in df.columns:
            df['المستوى'] = df['المستوى'].astype(str).str.strip()
            df['المستوى'] = df['المستوى'].str.replace('ألاول', 'الأول')
            df['المستوى'] = df['المستوى'].str.replace('الاول', 'الأول')
            df['المستوى'] = df['المستوى'].str.replace('الاولي', 'الأول')
        
        # تنظيف الأرقام
        df['المبلغ'] = df['المبلغ'].astype(str).str.replace(',', '').str.replace(' ', '')
        df['المبلغ'] = pd.to_numeric(df['المبلغ'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data(sheet_url)

if not df.empty:
    # --- 5. الإحصائيات العامة ---
    st.title("🌙 وسابقوا..")
    st.markdown("<h5 style='text-align: center; color: gray;'>منافسة الخير - كلية الهندسة والعمارة</h5>", unsafe_allow_html=True)
    
    TARGET_AMOUNT = 38000000
    BAG_COST = 190000
    TARGET_BAGS = 200

    total_collected = df['المبلغ'].sum()
    bags_collected = int(total_collected / BAG_COST)
    progress = total_collected / TARGET_AMOUNT

    # عرض الكروت (تأكدنا من وضوح العناوين هنا)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 المجموع الكلي", value=f"{total_collected:,.0f}")
    with col2:
        st.metric(label="🎒 حقائب رمضانية", value=f"{bags_collected}")
    with col3:
        st.metric(label="📊 نسبة الإنجاز", value=f"{progress*100:.1f}%")

    st.progress(min(progress, 1.0))
    st.divider()

    # --- 6. ساحة التنافس ---
    st.subheader("🏆 ترتيب الأقسام حسب المستويات")
    
    levels_order = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس"]
    tabs = st.tabs(levels_order)
    
    for i, level_name in enumerate(levels_order):
        with tabs[i]:
            current_level_data = df[df['المستوى'] == level_name]
            level_df = current_level_data.groupby('القسم')['المبلغ'].sum().reset_index()
            
            if not level_df.empty:
                level_df = level_df.sort_values(by='المبلغ', ascending=True)

                fig = px.bar(
                    level_df, 
                    x='المبلغ', y='القسم', orientation='h',
                    text='المبلغ', color='المبلغ', 
                    color_continuous_scale='Blues',
                    title=f"منافسة {level_name}"
                )
                
                fig.add_vline(x=570000, line_dash="dash", line_color="green", annotation_text="هدف 3 حقائب")
                fig.update_layout(xaxis_title="", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', height=400)
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                
                leader = level_df.iloc[-1]
                if leader['المبلغ'] > 0:
                    st.success(f"🥇 المتصدر: {leader['القسم']} ({leader['المبلغ']:,})")
            else:
                st.info(f"لا توجد بيانات مسجلة لـ {level_name} حتى الآن.")

    st.divider()
    
    # --- 7. الحسابات البنكية ---
    with st.expander("💳 اضغط هنا لعرض أرقام الحسابات", expanded=False):
        st.markdown("""
        <div style="text-align: center; direction: rtl;">
        **بنك الخرطوم (بنكك):** `4195521` (زبيدة فؤاد عثمان)<br><br>
        **بنك فيصل (فوري):** `52092340` (محمد جلال الدين الشيخ)<br><br>
        **بنك أمدرمان الوطني (أوكاش):** `643344` (محمد جلال الدين الشيخ)<br>
        <hr>
        📲 **لإرسال الإشعار:** `0112551093`
        </div>
        """, unsafe_allow_html=True) 

else:
    st.error("⚠️ جاري تحميل البيانات...")

if st.button('🔄 تحديث البيانات'):
    st.cache_data.clear()
    st.rerun()
