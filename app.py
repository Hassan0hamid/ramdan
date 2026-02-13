import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="الحقيبة الرمضانية - هندسة وعمارة",
    page_icon="🌙",
    layout="centered"
)

# --- 2. تنسيق CSS (لجعل التطبيق عربي وجميل) ---
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3 { font-family: 'Tajawal', sans-serif; color: #1f77b4; text-align: center; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #ddd; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. صورة البوستر (لو رفعتها) ---
try:
    st.image("poster.jpeg", use_container_width=True) 
except:
    pass

# --- 4. تحميل البيانات ---
# ⚠️⚠️ هام: خت رابط ملف الـ CSV حقك هنا بين علامات التنصيص
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpVaFIFaIybxYXbO6ECjCzUFVRiVERCTKy6D-hFRPyKkzwzwDgJamRCuDBHfKCsg85m5vM9fBbVf1U/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        # تنظيف الأرقام: تحويلها لأرقام وحساب المجموع لو في تكرار
        df['المبلغ'] = pd.to_numeric(df['المبلغ'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return pd.DataFrame()

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

    # عرض العدادات
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 المجموع الكلي", f"{total_collected:,.0f}")
    with col2:
        st.metric("🎒 حقيبة رمضانية", f"{bags_collected}")
    with col3:
        st.metric("📉 نسبة الإنجاز", f"{progress*100:.1f}%")

    st.progress(min(progress, 1.0))
    st.divider()

    # --- 6. ساحة التنافس (الرسم البياني) ---
    st.subheader("🏆 ترتيب الأقسام حسب المستويات")
    
    # قائمة المستويات بنفس طريقة كتابتك في الشيت بالضبط
    # (لاحظ: كتبت "ألاول" بالهمزة زي ما انت كاتبها في البيانات)
    levels_order = ["ألاول", "الثاني", "الثالث", "الرابع", "الخامس"]
    
    # إنشاء التبويبات
    tabs = st.tabs(levels_order)
    
    for i, level_name in enumerate(levels_order):
        with tabs[i]:
            # تصفية البيانات حسب المستوى
            # بنجمع البيانات عشان لو في سطرين لنفس القسم يجمعهم (مثلاً مدني دفعوا مرتين)
            level_df = df[df['المستوى'] == level_name].groupby('القسم')['المبلغ'].sum().reset_index()
            
            if not level_df.empty:
                # ترتيب الداتا من الأكبر للأصغر
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
                    title=f"منافسة المستوى {level_name}"
                )
                
                # خط الهدف (3 حقائب = 570,000)
                target_line = 570000
                fig.add_vline(x=target_line, line_dash="dash", line_color="green", annotation_text="هدف 3 حقائب")
                
                # تحسين الشكل
                fig.update_layout(xaxis_title="", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', height=400)
                fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # تحية للمتصدر
                leader = level_df.iloc[-1]
                if leader['المبلغ'] > 0:
                    st.success(f"🥇 متصدر المستوى {level_name}: قسم {leader['القسم']} ({leader['المبلغ']:,} ج.س)")
            else:
                st.info("لا توجد بيانات مسجلة لهذا المستوى بعد.")

    st.divider()
    
    # --- 7. الحسابات البنكية ---
    with st.expander("💳 اضغط هنا لعرض أرقام الحسابات", expanded=False):
        st.markdown("""
        <div style="text-align: center;">
        <b>بنك الخر
