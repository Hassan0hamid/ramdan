import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="الحقيبة الرمضانية - هندسة وعمارة",
    page_icon="🌙",
    layout="centered"
)

# --- 2. تنسيق CSS ---
st.markdown("""
<style>
    /* اتجاه الصفحة */
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3 { font-family: 'Tajawal', sans-serif; color: #1f77b4; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
    
    /* تنسيق التوقيع */
    .footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #eee;
        font-size: 12px;
        color: #888;
        font-family: 'Tajawal', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. دالة لرسم الكروت ---
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
# الرابط الخاص بك
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpVaFIFaIybxYXbO6ECjCzUFVRiVERCTKy6D-hFRPyKkzwzwDgJamRCuDBHfKCsg85m5vM9fBbVf1U/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        
        # تنظيف العناوين
        df.columns = df.columns.str.strip()
        
        # توحيد الهمزات في المستويات
        if 'المستوى' in df.columns:
            df['المستوى'] = df['المستوى'].astype(str).str.strip()
            df['المستوى'] = df['المستوى'].str.replace(r'[أإآ]ل', 'ال', regex=True) 
            df['المستوى'] = df['المستوى'].str.replace('الاول', 'الأول')
            df['المستوى'] = df['المستوى'].str.replace('ألاول', 'الأول')

        # تنظيف الأرقام
        df['المبلغ'] = df['المبلغ'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['المبلغ'] = pd.to_numeric(df['المبلغ'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data(sheet_url)

# --- 5. العرض الرئيسي ---
try:
    st.image("poster.jpeg", use_container_width=True) 
except:
    pass

if not df.empty:
    st.title("🌙 وسابقوا..")
    st.markdown("<h5 style='text-align: center; color: gray;'>منافسة الخير - كلية الهندسة والعمارة</h5>", unsafe_allow_html=True)
    
    # الحسابات
    TARGET_AMOUNT = 38000000
    BAG_COST = 190000
    
    total_collected = df['المبلغ'].sum()
    bags_collected = int(total_collected / BAG_COST)
    progress = total_collected / TARGET_AMOUNT

    # عرض الكروت
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
    
    levels_order = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس"]
    tabs = st.tabs(levels_order)
    
    for i, level_name in enumerate(levels_order):
        with tabs[i]:
            # تنظيف ومطابقة الاسم للبحث
            search_name = level_name.replace("أ", "ا").replace("إ", "ا")
            
            # فلترة مرنة
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
                
                # الرسم البياني
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
                
                leader = level_df.iloc[-1]
                if leader['المبلغ'] > 0:
                    st.success(f"🥇 المتصدر: {leader['القسم']} ({leader['المبلغ']:,})")
            else:
                st.info(f"لا توجد بيانات مسجلة لـ {level_name} حتى الآن.")

    st.divider()

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
         
    # --- التوقيع (Footer) ---
    st.markdown("""
    <div class="footer">
    تم التطوير بواسطة: حسن حامد ❤️<br>
    بالتوفيق لكل الدفعات
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("⚠️ جاري تحميل البيانات...")

# زر التحديث
if st.button('🔄 تحديث البيانات الآن'):
    st.cache_data.clear()
    st.rerun()
