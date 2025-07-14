import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import random
from datetime import datetime
import smtplib
from email.message import EmailMessage

# -------------------------- العنوان --------------------------
st.set_page_config(page_title="Smart Drive Report", layout="centered")
st.title("🚗 Smart Drive Report Generator")

# -------------------------- إدخال الإيميل --------------------------
user_email = st.text_input("Enter your email to receive your driving report:")

# -------------------------- توليد بيانات عشوائية --------------------------
if st.button("Generate Report"):
    if user_email:
        st.success("Generating your smart driving report...")

        # بيانات عشوائية للسواقة
        speed = random.randint(60, 140)
        focus = random.randint(50, 100)
        calmness = random.randint(40, 100)
        aggression = 100 - calmness
        distraction = 100 - focus

        # رسم بياني
        fig, ax = plt.subplots()
        categories = ['Speed', 'Focus', 'Calmness', 'Aggression', 'Distraction']
        values = [speed, focus, calmness, aggression, distraction]
        bar_colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
        ax.bar(categories, values, color=bar_colors)
        ax.set_ylim([0, 150])
        ax.set_title('Driving Behavior Overview')
        st.pyplot(fig)

        # -------------------------- نصيحة حسب النسب --------------------------
        advice = ""
        if aggression > 70:
            advice += "- Try to stay calm while driving. High aggression affects safety.\n"
        if distraction > 50:
            advice += "- Reduce distractions. Focus is key to safe driving.\n"
        if speed > 120:
            advice += "- You're driving too fast! Consider slowing down.\n"
        if not advice:
            advice = "Great job! Keep driving safely and mindfully."

        st.info("Advice:\n" + advice)

        # -------------------------- توليد PDF --------------------------
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Smart Drive Report", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Speed: {speed} km/h", ln=True)
            pdf.cell(200, 10, txt=f"Focus: {focus}%", ln=True)
            pdf.cell(200, 10, txt=f"Calmness: {calmness}%", ln=True)
            pdf.cell(200, 10, txt=f"Aggression: {aggression}%", ln=True)
            pdf.cell(200, 10, txt=f"Distraction: {distraction}%", ln=True)
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt="Advice:\n" + advice)
            pdf.output("/mnt/data/drive_report.pdf")

            with open("/mnt/data/drive_report.pdf", "rb") as file:
                file_data = file.read()

            # -------------------------- إرسال إيميل --------------------------
            email = EmailMessage()
            email['Subject'] = 'Your Smart Drive Report'
            email['From'] = 'smartdrive.report.bot@gmail.com'
            email['To'] = user_email
            email.set_content("Attached is your smart driving behavior report. Stay safe! 🚗")
            email.add_attachment(file_data, maintype='application', subtype='pdf', filename="drive_report.pdf")

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('smartdrive.report.bot@gmail.com', 'your-app-password')
                smtp.send_message(email)

            st.success("📩 Report sent successfully to your email!")

        except Exception as e:
            st.error(f"PDF generation error: {e}")

    else:
        st.warning("Please enter a valid email address.")

# -------------------------- التوقيع --------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 16px;'>🚗💡 By <b>Sahar Jamal</b></p>",
    unsafe_allow_html=True
)
