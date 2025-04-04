
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# بيانات الدخول الثابتة (يمكن تعديلها لاحقًا)
USERNAME = "admin"
PASSWORD = "1234"

# التحقق من تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("تسجيل الدخول")
    username_input = st.text_input("اسم المستخدم")
    password_input = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username_input == USERNAME and password_input == PASSWORD:
            st.session_state.logged_in = True
            st.success("تم تسجيل الدخول بنجاح")
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
    st.stop()

# بعد تسجيل الدخول يبدأ النظام المحاسبي
st.set_page_config(page_title="المحاسب الذكي", layout="centered")
st.title("المحاسب الذكي")

st.markdown("### إدخال قيد محاسبي")

# إنشاء نموذج لإدخال القيد
with st.form(key='entry_form'):
    date = st.date_input("تاريخ المعاملة", datetime.today())
    description = st.text_input("الوصف")
    amount = st.number_input("المبلغ", min_value=0.0, step=0.01)
    type = st.selectbox("نوع المعاملة", ["إيراد", "مصروف", "أصل", "خصم", "التزام"])
    submitted = st.form_submit_button("إضافة")

# تحميل البيانات القديمة أو إنشاء ملف جديد
if "entries" not in st.session_state:
    st.session_state.entries = pd.DataFrame(columns=["التاريخ", "الوصف", "المبلغ", "النوع"])

# إضافة المعاملة الجديدة إلى الجدول
if submitted:
    new_entry = pd.DataFrame({
        "التاريخ": [date.strftime("%Y-%m-%d")],
        "الوصف": [description],
        "المبلغ": [amount],
        "النوع": [type]
    })
    st.session_state.entries = pd.concat([st.session_state.entries, new_entry], ignore_index=True)
    st.success("تمت إضافة القيد بنجاح!")

# عرض الجدول مع الفلاتر
st.markdown("### المعاملات المسجلة")
if not st.session_state.entries.empty:
    df = st.session_state.entries.copy()

    # فلترة حسب النوع والتاريخ
    st.markdown("#### فلترة المعاملات")
    filter_type = st.multiselect("اختر نوع المعاملة", options=df["النوع"].unique(), default=list(df["النوع"].unique()))
    min_date = pd.to_datetime(df["التاريخ"]).min()
    max_date = pd.to_datetime(df["التاريخ"]).max()
    date_range = st.date_input("نطاق التاريخ", [min_date, max_date])

    df["التاريخ"] = pd.to_datetime(df["التاريخ"])
    filtered_df = df[
        (df["النوع"].isin(filter_type)) &
        (df["التاريخ"] >= pd.to_datetime(date_range[0])) &
        (df["التاريخ"] <= pd.to_datetime(date_range[1]))
    ]

    st.dataframe(filtered_df, use_container_width=True)

    # زر تحميل البيانات
    st.markdown("### تحميل البيانات")
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='المعاملات')
        output.seek(0)
        return output

    excel_data = convert_df_to_excel(filtered_df)
    st.download_button(
        label="تحميل كملف Excel",
        data=excel_data,
        file_name="المعاملات.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # تحليل البيانات
    st.markdown("### تحليل المعاملات")
    summary = filtered_df.groupby("النوع")["المبلغ"].sum().reset_index()
    st.bar_chart(summary.set_index("النوع"))

    # حساب الربح أو الخسارة
    revenue = summary[summary["النوع"] == "إيراد"]["المبلغ"].sum()
    expense = summary[summary["النوع"] == "مصروف"]["المبلغ"].sum()
    net = revenue - expense

    st.markdown("### صافي الربح / الخسارة")
    if net > 0:
        st.success(f"صافي الربح: {net:.2f} ريال")
    elif net < 0:
        st.error(f"صافي الخسارة: {-net:.2f} ريال")
    else:
        st.info("لا يوجد ربح أو خسارة حالياً.")
else:
    st.info("لا توجد معاملات حالياً.")
