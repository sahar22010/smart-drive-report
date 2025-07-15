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

def generate_driving_tip(score):
    if score > 80:
        return (
            "Excellent job! Your driving shows great focus, calmness, and awareness. "
            "Keep up the good habits! Staying alert and relaxed helps prevent accidents "
            "and ensures a smooth experience. Great drivers are not just fast—they are smart and safe.",
        )
    elif score > 50:
        return (
            "You're doing okay, but there's room to grow. Maybe you're distracted sometimes or get stressed. "
            "Try to slow down a bit, breathe, and refocus when driving. Little changes can make a big difference. "
            "Safe driving is about attention and attitude."
        )
    else:
        return (
            "Your score shows that your driving could be risky. Maybe there’s aggression, high speed, or low focus. "
            "Please reflect on your driving behavior. Staying calm, focused, and in control can help protect you "
            "and others. Every smart change counts toward a safer journey."
        )

def generate_pdf(chart_path, values, overall_score):
    pdf = FPDF()

    # Add page 1
    pdf.add_page()
    pdf.set_font('Helvetica', '', 16)
    pdf.cell(0, 10, 'SmartDrive Report', 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, f'Speed: {values[0]} km/h', 0, 1)
    pdf.cell(0, 10, f'Focus: {values[1]}%', 0, 1)
    pdf.cell(0, 10, f'Calmness: {values[2]}%', 0, 1)
    pdf.cell(0, 10, f'Aggression: {values[3]}%', 0, 1)
    pdf.cell(0, 10, f'Distraction: {values[4]}%', 0, 1)
    pdf.ln(10)

    pdf.image(chart_path, x=10, w=190)

    # Add page 2 (tips)
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 144, 255)  # DodgerBlue
    pdf.cell(0, 10, "Your Driving Tip", 0, 1, 'L')
    pdf.ln(5)

    tip = generate_driving_tip(overall_score)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 12)
    pdf.multi_cell(0, 10, tip)

    pdf.output("driving_report.pdf")

def send_email(to_email):
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = "SmartDrive Report"

    body = """
Hello,

Your SmartDrive report is attached to this email.

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
    ملاحظة: هذا نموذج أولي يعتمد على بيانات عشوائية / This is a prototype using random data
    </span>
    </p>
    """, unsafe_allow_html=True)

    email = st.text_input("بريدك الإلكتروني / Your Email")

    if st.button("إرسال التقرير / Send Report"):
        if email:
            values = [
                random.randint(60, 140),  # Speed
                random.randint(50, 100),  # Focus
                random.randint(40, 100),  # Calmness
                random.randint(0, 100),   # Aggression
                random.randint(0, 100)    # Distraction
            ]

            chart_path, overall_score = create_chart(values)
            generate_pdf(chart_path, values, overall_score)
            send_email(email)

            st.success("✅ تم الإرسال بنجاح! / Sent successfully!")
        else:
            st.error("⚠ يرجى إدخال بريد صحيح / Please enter a valid email")


if __name__ == "__main__":
    main()
