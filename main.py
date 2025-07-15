import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import random
import os
import numpy as np
from matplotlib.patches import Circle

# إعدادات الإيميل
SENDER_EMAIL = "smartdrive.report@gmail.com"
APP_PASSWORD = "owjj okgp ljbl gztg"  # استبدليه بكلمة مرور التطبيق الخاصة بك

def create_chart(values):
    categories_en = ['Speed', 'Focus', 'Calmness', 'Aggression', 'Distraction']
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    bars = ax1.bar(categories_en, values, color=colors)
    ax1.set_title('Driving Behavior Summary', fontsize=12)
    ax1.set_ylim([0, 150])

    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height}%',
                 ha='center', va='bottom', fontsize=10)

    overall_score = np.mean(values)
    color = '#2ca02c' if overall_score > 70 else '#ff7f0e' if overall_score > 40 else '#d62728'
    circle = Circle((0.5, 0.5), 0.4, fill=False, linewidth=10, color=color)
    ax2.add_patch(circle)
    ax2.text(0.5, 0.5, f'{overall_score:.0f}%',
             ha='center', va='center', fontsize=24, fontweight='bold')
    ax2.set_title('Overall Score', fontsize=12)
    ax2.axis('off')

    plt.tight_layout()
    chart_path = "chart.png"
    fig.savefig(chart_path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return chart_path, overall_score

def get_driving_tip_paragraph(score):
    if score > 80:
        return (
            "Your driving behavior is impressive! You're showing great awareness and control on the road. "
            "Maintaining this level of calmness and focus will help keep you and others safe. "
            "Continue driving attentively, stay patient with traffic, and avoid distractions. "
            "Excellent job — keep it up!"
        )
    elif score > 50:
        return (
            "Your driving performance is good, but there's room for improvement. Try to stay more focused, "
            "especially in busy traffic. Reducing distractions and avoiding sudden reactions can greatly enhance your control. "
            "Stay aware of your surroundings, and always aim for smoother decisions on the road."
        )
    else:
        return (
            "Your driving shows that you need to be more careful. It's important to reduce distractions and control your reactions. "
            "Try to stay calm, avoid aggressive moves, and focus entirely on the road. Improving your attention and behavior will make you a much safer and more confident driver."
        )

def get_tip_list():
    return [
        "Stay focused and avoid distractions like phones.",
        "Keep both hands on the wheel.",
        "Slow down in busy or unfamiliar areas.",
        "Be patient with other drivers.",
        "Avoid sudden lane changes or harsh braking.",
        "Always wear your seatbelt.",
        "Take breaks if you feel tired.",
    ]

def generate_pdf(chart_path, values, overall_score):
    pdf = FPDF()
    pdf.add_page()

    # الصفحة الأولى
    pdf.set_font("Helvetica", size=18)
    pdf.cell(0, 15, "SmartDrive Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, f"Speed: {values[0]} km/h", ln=True)
    pdf.cell(0, 10, f"Focus: {values[1]}%", ln=True)
    pdf.cell(0, 10, f"Calmness: {values[2]}%", ln=True)
    pdf.cell(0, 10, f"Aggression: {values[3]}%", ln=True)
    pdf.cell(0, 10, f"Distraction: {values[4]}%", ln=True)
    pdf.ln(10)

    pdf.image(chart_path, x=10, w=190)
    pdf.ln(10)

    # الصفحة الثانية
    pdf.add_page()
    pdf.set_font("Helvetica", size=18)
    pdf.set_text_color(0, 91, 187)  # لون أزرق
    pdf.multi_cell(0, 10, get_driving_tip_paragraph(overall_score))
    pdf.ln(8)

    pdf.set_font("Helvetica", size=14)
    pdf.set_text_color(0, 0, 0)  # لون أسود
    pdf.cell(0, 10, "Tips to Improve:", ln=True)

    pdf.set_font("Helvetica", size=13)
    for tip in get_tip_list():
        pdf.cell(5)
        pdf.cell(0, 10, f"- {tip}", ln=True)

    pdf.output("driving_report.pdf")

def send_email(to_email):
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = "SmartDrive Report"

    body = """
Hello,

Your SmartDrive report is attached to this email.
Wishing you safe and smart driving!

Best regards,
Sahar Jamal
"""
    message.attach(MIMEText(body, "plain"))

    with open("driving_report.pdf", "rb") as f:
        part = MIMEApplication(f.read(), Name="SmartDrive_Report.pdf")
        part['Content-Disposition'] = 'attachment; filename="SmartDrive_Report.pdf"'
        message.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(message)

def main():
    st.set_page_config(page_title="تقرير القيادة الذكية", layout="centered")

    st.title("🚗 تقرير القيادة الذكية / SmartDrive Report")

    st.markdown("""
    <p style='text-align: center;'>
    بواسطة: <b>سحر جمال</b> / By: <b>Sahar Jamal</b><br>
    <span style='color: gray; font-size: 14px;'>
    ملاحظة: هذا نموذج أولي يعتمد على بيانات عشوائية
    </span>
    </p>
    """, unsafe_allow_html=True)

    email = st.text_input("بريدك الإلكتروني / Your Email")

    if st.button("إرسال التقرير / Send Report"):
        if email:
            values = [
                random.randint(60, 140),
                random.randint(50, 100),
                random.randint(40, 100),
                random.randint(0, 100),
                random.randint(0, 100)
            ]
            chart_path, overall_score = create_chart(values)
            generate_pdf(chart_path, values, overall_score)
            send_email(email)
            st.success("✅ Report sent successfully!")
        else:
            st.error("⚠ Please enter a valid email.")

if __name__ == "__main__":
    main()
