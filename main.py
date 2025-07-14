import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import random
import os

# -------- إعدادات الإيميل --------
SENDER_EMAIL = "smartdrive.report@gmail.com"
APP_PASSWORD = "owjj okgp ljbl gztg"

# -------- توليد رسم بياني --------
def create_chart():
    categories = ['Speed', 'Focus', 'Calmness', 'Aggression', 'Distraction']
    values = [random.randint(60, 140), random.randint(50, 100), random.randint(40, 100), random.randint(0, 100), random.randint(0, 100)]
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']

    fig, ax = plt.subplots()
    ax.bar(categories, values, color=colors)
    ax.set_title('Driving Behavior Summary')
    ax.set_ylim([0, 150])
    chart_path = "chart.png"
    fig.savefig(chart_path)
    plt.close(fig)
    return chart_path, values

# -------- توليد PDF التقرير --------
def generate_pdf(values, style="Energetic", tip="Take short breaks to stay focused."):
    chart_path, _ = create_chart()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="🚗 Smart Driving Report - July 2025", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Speed: {values[0]} km/h", ln=True)
    pdf.cell(200, 10, txt=f"Focus: {values[1]}%", ln=True)
    pdf.cell(200, 10, txt=f"Calmness: {values[2]}%", ln=True)
    pdf.cell(200, 10, txt=f"Aggression: {values[3]}%", ln=True)
    pdf.cell(200, 10, txt=f"Distraction: {values[4]}%", ln=True)
    pdf.cell(200, 10, txt=f"Style: {style}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Tip: {tip}")
    pdf.ln(5)
    pdf.image(chart_path, x=30, w=150)
    pdf.ln(5)
    pdf.cell(200, 10, txt="By: Sahar Jamal", ln=True, align='C')
    pdf.cell(200, 10, txt="Note: This is a prototype based on random data.", ln=True, align='C')
    pdf.output("driving_report.pdf")

# -------- إرسال الإيميل مع المرفق --------
def send_email(to_email):
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = "🚗 Your SmartDrive Report is Here!"

    body = """
Hey there!

Here's your personalized driving report. Hope you enjoy the insights 🚗✨

Stay safe & drive smart,
– Sahar Jamal
    """
    message.attach(MIMEText(body, "plain"))

    with open("driving_report.pdf", "rb") as f:
        part = MIMEApplication(f.read(), Name="Driving_Report.pdf")
        part['Content-Disposition'] = 'attachment; filename="Driving_Report.pdf"'
        message.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(message)

# -------- واجهة Streamlit --------
st.set_page_config(page_title="SmartDrive Report", layout="centered")
st.title("🚗 SmartDrive Report")
st.markdown("<p style='text-align: center;'>By: <b>Sahar Jamal</b><br>This is a prototype based on random data</p>", unsafe_allow_html=True)
st.markdown("Enter your email below to get your colorful smart driving report 🎨📩")

email = st.text_input("Your Email")

if st.button("Send My Report"):
    if email:
        chart_path, values = create_chart()
        generate_pdf(values)
        send_email(email)
        st.success("✅ Sent! Check your email for the report.")
    else:
        st.error("⚠ Please enter a valid email.")

# -------------------------- ملاحظة --------------------------
st.markdown(
    "<p style='text-align: center; font-size: 12px; color: gray;'>"
    "This is a preliminary project based on random data."
    "</p>",
    unsafe_allow_html=True
)
