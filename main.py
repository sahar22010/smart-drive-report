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
import requests

# Email settings
SENDER_EMAIL = "smartdrive.report@gmail.com"
APP_PASSWORD = "owjj okgp ljbl gztg"  # Replace with your actual password

def download_font():
    font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoKufiArabic/NotoKufiArabic-Regular.ttf"
    font_path = "NotoKufiArabic-Regular.ttf"
    
    if not os.path.exists(font_path):
        try:
            response = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(response.content)
            st.success("تم تحميل الخط العربي بنجاح")
        except Exception as e:
            st.error(f"فشل تحميل الخط العربي: {str(e)}")
            return False
    return True

def create_chart(values):
    categories_ar = ['السرعة', 'التركيز', 'الهدوء', 'العدوانية', 'التشتت']
    categories_en = ['Speed', 'Focus', 'Calmness', 'Aggression', 'Distraction']
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    bars = ax1.bar(categories_ar, values, color=colors)
    ax1.set_title('ملخص سلوك القيادة / Driving Behavior Summary', fontsize=12)
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
    ax2.set_title('النسبة الكلية / Overall Score', fontsize=12)
    ax2.axis('off')
    
    plt.tight_layout()
    chart_path = "chart.png"
    fig.savefig(chart_path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return chart_path, overall_score

def generate_driving_tip(score):
    tips_ar = {
        'high': "أحسنت! أداؤك في القيادة ممتاز. حافظ على هذه المستويات العالية من التركيز والهدوء.",
        'medium': "أداؤك جيد ولكن هناك مجال للتحسين. حاول زيادة مستوى تركيزك وتقليل التشتت.",
        'low': "هناك حاجة لتحسين أدائك في القيادة. ركز أكثر على الطريق وحاول تقليل العدوانية."
    }
    
    tips_en = {
        'high': "Excellent! Your driving performance is outstanding. Maintain these high levels.",
        'medium': "Good performance but there's room for improvement. Try to increase your focus.",
        'low': "Your driving performance needs improvement. Focus more on the road."
    }
    
    if score > 80:
        return tips_ar['high'], tips_en['high']
    elif score > 50:
        return tips_ar['medium'], tips_en['medium']
    else:
        return tips_ar['low'], tips_en['low']

def generate_pdf(chart_path, values, overall_score):
    pdf = FPDF()
    
    # Add fonts
    font_added = False
    try:
        pdf.add_font('NotoArabic', '', 'NotoKufiArabic-Regular.ttf', uni=True)
        font_added = True
    except:
        st.warning("Using fallback font for Arabic text")
    
    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
    
    # Add page
    pdf.add_page()
    
    # Title
    if font_added:
        pdf.set_font('NotoArabic', '', 16)
        pdf.cell(0, 10, 'تقرير القيادة الذكية', 0, 1, 'C')
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, 'SmartDrive Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Data
    if font_added:
        pdf.set_font('NotoArabic', '', 12)
        pdf.cell(0, 10, f'السرعة: {values[0]} كم/ساعة', 0, 1)
        pdf.cell(0, 10, f'التركيز: {values[1]}%', 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Speed: {values[0]} km/h', 0, 1)
    pdf.cell(0, 10, f'Focus: {values[1]}%', 0, 1)
    pdf.ln(10)
    
    # Chart image
    pdf.image(chart_path, x=10, w=190)
    pdf.ln(10)
    
    # Tips
    tip_ar, tip_en = generate_driving_tip(overall_score)
    if font_added:
        pdf.set_font('NotoArabic', '', 12)
        pdf.multi_cell(0, 8, tip_ar)
        pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, tip_en)
    pdf.ln(10)
    
    # Footer note
    pdf.set_text_color(128, 128, 128)
    if font_added:
        pdf.set_font('NotoArabic', '', 10)
        pdf.cell(0, 10, 'هذا نموذج أولي يعتمد على بيانات عشوائية', 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, 'This is a prototype using random data', 0, 1, 'C')
    
    pdf.output("driving_report.pdf")

def send_email(to_email):
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = "تقرير القيادة الذكية / SmartDrive Report"
    
    body = """
مرحباً / Hello,

تقرير القيادة الذكية الخاص بك مرفق بهذه الرسالة. 
Your SmartDrive report is attached to this email.

مع تحياتي / Best regards,
سحر جمال / Sahar Jamal
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
    
    # Download Arabic font if not exists
    if not download_font():
        st.warning("قد لا تظهر النصوص العربية بشكل صحيح بدون الخط المطلوب")
    
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
            
            st.success("✅ تم الإرسال بنجاح! / Sent successfully!")
        else:
            st.error("⚠ يرجى إدخال بريد صحيح / Please enter a valid email")

if __name__== "__main__":
    main()
