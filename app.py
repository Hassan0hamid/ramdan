import streamlit as st
import pandas as pd
import plotly.express as px

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="الحقيبة الرمضانية - هندسة وعمارة",
    page_icon="🌙",
    layout="centered"
)

# --- تنسيق CSS (عربي + ألوان الهوية) ---
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3 { font-family: 'Tajawal', sans-serif; color: #1f77b4; text-align: center; }
    .metric-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #ddd; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- 🖼️ صورة البوستر ---
# (ارفع صورة البوستر في نفس المكان في GitHub وسميها poster.jpeg)
try:
    st.image("poster.jpeg", use_container_width=True) 
except:
    st.warning("صورة البوستر ما موجودة، تأكد من رفعها باسم poster.jpeg")

# --- 📥 تحميل البيانات ---
# ⚠️ استبدل الرابط ده بالرابط حقك (ما تنسى علامات التنصيص "")
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpVaFIFaIybxYXbO6ECjCzUFVRiVERCTKy6D-hFRPyKkzwzwDgJamRCuDBHfKCsg85m5vM9fBbVf1U/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df
    except:
        return pd.DataFrame() # لو في خطأ يرجع داتا فاضية

df = load_data(sheet_url)

if not df.empty:
    # --- 📊 الإحصائيات العامة ---
    st.title("🌙 وسابقوا..")
    st.markdown("<h4 style='text-align: center; color: gray;'>حملة الحقيبة الرمضانية - كليتي الهندسة والعمارة</h4>", unsafe_allow_html=True)
    
    TARGET_AMOUNT = 38000000  # 38 مليون
    BAG_COST = 190000         # تكلفة الحقيبة
    TARGET_BAGS = 200         # 200 حقيبة

    total_collected = df['المبلغ'].sum()
    bags_collected = int(total_collected / BAG_COST)
    progress = total_collected / TARGET_AMOUNT

    # عرض العدادات
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 المجموع الكلي", f"{total_collected:,.0f} ج.س")
    with col2:
        st.metric("🎒 حقائب تم تأمينها", f"{bags_collected} من {TARGET_BAGS}")
    with col3:
        st.metric("📉 نسبة الإنجاز", f"{progress*100:.1f}%")

    st.progress(min(progress, 1.0))
    
    st.divider()

    # --- 🔥 ساحة التنافس (حسب المستويات) ---
    st.subheader("🏆 منافسات الدفعات والأقسام")
    st.info("الهدف لكل قسم: 3 حقائب رمضانية (570,000 ج.س) 🎯")

    # تبويبات للمستويات
    tabs = st.tabs(["المستوى الأول", "المستوى الثاني", "المستوى الثالث", "المستوى الرابع", "المستوى الخامس"])
    
    levels_map = {
        "المستوى الأول": tabs[0], "المستوى الثاني": tabs[1], 
        "المستوى الثالث": tabs[2], "المستوى الرابع": tabs[3], "المستوى الخامس": tabs[4]
    }

    # اللوجيك لكل تاب
    for level_name, tab in levels_map.items():
        with tab:
            # فلترة البيانات حسب المستوى
            level_df = df[df['المستوى'] == level_name]
            
            if not level_df.empty:
                # تجميع المبالغ للأقسام في هذا المستوى
                dept_group = level_df.groupby('القسم')['المبلغ'].sum().reset_index()
                dept_group = dept_group.sort_values(by='المبلغ', ascending=True)

                # رسم بياني
                fig = px.bar(
                    dept_group, x='المبلغ', y='القسم', orientation='h',
                    text='المبلغ', color='المبلغ', color_continuous_scale='Blues'
                )
                
                # خط الهدف (3 حقائب)
                fig.add_vline(x=570000, line_dash="dash", line_color="green", annotation_text="هدف الـ 3 حقائب")
                
                fig.update_layout(xaxis_title="المساهمة (ج.س)", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)')
                fig.update_traces(texttemplate='%{text:.2s}')
                st.plotly_chart(fig, use_container_width=True)
                
                # المتصدر
                leader = dept_group.iloc[-1]
                if leader['المبلغ'] >= 570000:
                     st.success(f"🥇 المتصدر حالياً: {leader['القسم']} (تجاوزوا هدف الـ 3 حقائب!)")
                else:
                     st.write(f"🥇 المتصدر حالياً: {leader['القسم']}")

            else:
                st.write("لا توجد بيانات مسجلة لهذا المستوى حتى الآن.")

    st.divider()

    # --- 💳 طرق المساهمة ---
    with st.expander("💳 اضغط هنا لعرض حسابات التبرع", expanded=False):
        st.markdown("""
        **بنك الخرطوم (بنكك):** `4195521` - زبيدة فؤاد عثمان
        **بنك فيصل (فوري):** `52092340` - محمد جلال الدين الشيخ
        **بنك أمدرمان الوطني (أوكاش):** `643344` - محمد جلال الدين الشيخ
        
        📲 **تأكد من إرسال الإشعار على الرقم:** `0112551093`
        """)

else:
    st.error("⚠️ الرجاء التأكد من رابط ملف Google Sheet ووضعه داخل علامات تنصيص.")

# زر تحديث
if st.button('🔄 تحديث القائمة'):
    st.cache_data.clear()
    st.rerun()
