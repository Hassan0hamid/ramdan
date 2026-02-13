import streamlit as st
import pandas as pd
import plotly.express as px

# --- إعدادات الصفحة ---
st.set_page_config(page_title="تحدي الخير - رمضان", layout="centered")

# --- دالة لجلب البيانات من قوقل شيت ---
# بنعمل cache عشان ما يحمل من الشيت كل ثانية، بس كل ما شخص يدخل
@st.cache_data(ttl=60) 
def load_data(sheet_url):
    # قراءة ملف الـ CSV مباشرة من الرابط
    df = pd.read_csv(sheet_url)
    return df

# --- 🔴 هام: خت الرابط حقك هنا مكان الرابط ده ---
sheet_url = https://docs.google.com/spreadsheets/d/e/2PACX-1vQpVaFIFaIybxYXbO6ECjCzUFVRiVERCTKy6D-hFRPyKkzwzwDgJamRCuDBHfKCsg85m5vM9fBbVf1U/pubhtml "رابط_الـ_CSV_بتاعك_من_الخطوة_الأولى" 

try:
    # تحميل البيانات
    df = load_data(sheet_url)

    # --- العنوان والهدف ---
    st.title("🌙 سباق الخير - حملة إفطار رمضان")
    st.markdown("### المنافسة بين الدفع والأقسام 🔥")

    # حساب الإجماليات
    target_amount = 5000000  # مثلاً الهدف 5 مليون (عدلها براحتك)
    total_collected = df['المبلغ'].sum()
    progress = total_collected / target_amount

    # عرض العداد الكبير
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="إجمالي التبرعات", value=f"{total_collected:,.0f} SDG")
    with col2:
        st.metric(label="المتبقي للهدف", value=f"{target_amount - total_collected:,.0f} SDG")

    # شريط التقدم
    st.progress(min(progress, 1.0))
    st.caption(f"تم جمع {progress*100:.1f}% من الهدف الكلي")

    st.markdown("---")

    # --- معالجة البيانات للمنافسة (تجميع حسب القسم) ---
    # بنجمع قروش كل قسم مع بعض
    competitors = df.groupby('القسم')['المبلغ'].sum().reset_index()
    # ترتيبهم من الأكثر للأقل
    competitors = competitors.sort_values(by='المبلغ', ascending=False)

    # --- الرسم البياني (السباق) ---
    st.subheader("📊 مؤشر المنافسة")
    fig = px.bar(
        competitors, 
        x='المبلغ', 
        y='القسم', 
        orientation='h', # شريط أفقي عشان الأسماء تكون واضحة
        text='المبلغ', 
        color='القسم',
        title="ترتيب الأقسام حسب المساهمة"
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # --- لوحة الصدارة (Leaderboard Table) ---
    st.subheader("🏆 لوحة المتصدرين")
    
    # تنسيق الجدول
    st.dataframe(
        competitors,
        use_container_width=True,
        hide_index=True,
        column_config={
            "القسم": "الدفعة / القسم",
            "المبلغ": st.column_config.ProgressColumn(
                "حجم المساهمة",
                format="%d SDG",
                min_value=0,
                max_value=int(competitors['المبلغ'].max())
            )
        }
    )

except Exception as e:
    st.error("⚠️ في مشكلة في رابط الشيت. تأكد إنك عملت 'Publish to Web' واخترت CSV.")
    st.write(e)

# زر تحديث يدوي
if st.button('تحديث البيانات 🔄'):
    st.cache_data.clear()
    st.rerun()
