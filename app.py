import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="الحقيبة الرمضانية - هندسة وعمارة",
    page_icon="🌙",
    layout="centered"
)

# --- 2. تنسيق CSS (عام) ---
st.markdown("""
<style>
    /* اتجاه الصفحة */
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3 { font-family: 'Tajawal', sans-serif; color: #1f77b4; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. دالة لرسم الكروت (Custom HTML) ---
# الدالة دي بتبني الكرت بتصميم HTML عشان نضمن الألوان 100%
def custom_card(title, value, sub_value=None):
    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    ">
        <h4 style="color: #1f77b4; margin: 0; font-size: 16px; font-weight: bold;">{title}</h4>
        <p style="color: #000000; font-size: 24px; font-weight: bold; margin: 5px 0;">{value}</p>
        {f'<p style="color: #666; font-size: 12px; margin: 0;">{sub_value}</p>' if sub_value else ''}
    </div>
    """, unsafe_allow_html=True)

# --- 4. تحميل البيانات ---
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpVaFIFaIybxYXbO6ECjCzUFVRiVERCTKy6D-hFRPyKkzwzwDgJamRCuDBHfKCsg85m5vM9fBbVf1U/pub?output=csv"

@st.cache_data(ttl=60) # تحديث كل 60 ثانية
def load_data(url):
    try:
        df = pd.read_csv(url)
        
        # تنظيف العناوين
        df.columns = df.columns.str.strip()
        
        # توحيد الهمزات في المستويات
        if 'المستوى' in df.columns:
            df['المستوى'] = df['المستوى'].astype(str).str.strip()
            df['المستوى'] = df['المستوى'].str.replace(r'[أإآ]ل', 'ال', regex=True) # توحيد كل الألفات
            df['المستوى'] = df['المستوى'].str.replace('الاول', 'الأول') # تصحيح نهائي
            df['المستوى'] = df['المستوى'].str.replace('ألاول', 'الأول')

        # تنظيف الأرقام (أهم خطوة)
        # بنحولها لنص، نمسح أي حاجة ما رقم، ونحولها لرقم تاني
        df['المبلغ'] = df['المبلغ'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['المبلغ'] = pd.to_numeric(df['المبلغ'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data(sheet_url)

# --- 5. العرض الرئيسي ---
# صورة البوستر
try:
    st.image("poster.jpeg", use_container_width=True) 
except:
    pass

if not df.empty:
    st.title("🌙 وسابقوا..")
    
    # الحسابات
    TARGET_AMOUNT = 38000000
    BAG_COST = 190000
    
    total_collected = df['المبلغ'].sum()
    bags_collected = int(total_collected / BAG_COST)
    progress = total_collected / TARGET_AMOUNT

    # --- عرض الكروت المخصصة (الحل لمشكلة الألوان) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        custom_card("💰 المجموع الكلي", f"{total_collected:,.0f}")
    with col2:
        custom_card("🎒 حقائب رمضانية", f"{bags_collected}")
    with col3:
        custom_card("📊 نسبة الإنجاز", f"{progress*100:.1f}%")

    st.progress(min(progress, 1.0))
    st.divider()

    # --- ساحة التنافس ---
    st.subheader("🏆 ترتيب الأقسام")
    
    # القائمة الموحدة
    levels_order = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس"]
    tabs = st.tabs(levels_order)
    
    for i, level_name in enumerate(levels_order):
        with tabs[i]:
            # تنظيف ومطابقة الاسم للبحث
            search_name = level_name.replace("أ", "ا").replace("إ", "ا") # تبسيط للبحث
            
            # فلترة مرنة (تبحث عن الكلمة حتى لو الهمزة اختلفت)
            current_level_data = df[df['المستوى'].str.contains(level_name, na=False) | 
                                    df['المستوى'].str.contains(search_name, na=False)]
            
            level_df = current_level_data.groupby('القسم')['المبلغ'].sum().reset_index()
            
            if not level_df.empty:
                level_df = level_df.sort_values(by='المبلغ', ascending=True)

                fig = px.bar(
                    level_df, 
                    x='المبلغ', y='القسم', orientation='h',
                    text='المبلغ', color='المبلغ', 
                    color_continuous_scale='Blues'
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

    # --- 🔍 قسم التأكد من البيانات (Debug) ---
    # القسم ده حيوريك الموقع قاري شنو بالضبط من الشيت
    with st.expander("🕵️‍♂️ عرض البيانات الخام (للتأكد من القراءة الصحيحة)"):
        st.write("البيانات كما وصلت من Google Sheets:")
        st.dataframe(df)
        st.caption("لو الأرقام هنا قديمة، معناها قوقل لسه ما حدث الرابط. انتظر 5 دقايق واضغط تحديث.")

    # --- الحسابات البنكية ---
    with st.expander("💳 أرقام الحسابات"):
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
    st.error("⚠️ جاري تحميل البيانات... لو طولت تأكد من الرابط.")

# زر التحديث
if st.button('🔄 تحديث البيانات الآن'):
    st.cache_data.clear()
    st.rerun()
