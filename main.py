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

# إعدادات الإيميل (يجب تغييرها لتناسب احتياجاتك)
SENDER_EMAIL = "smartdrive.report@gmail.com"
APP_PASSWORD = "your_app_password_here"  # استبدل بكلمة المرور الفعلية

# دالة لإنشاء الرسم البياني مع دائرة الأداء
def create_chart(values):
    # إعداد الأسماء باللغتين
    categories_ar = ['السرعة', 'التركيز', 'الهدوء', 'العدوانية', 'التشتت']
    categories_en = ['Speed', 'Focus', 'Calmness', 'Aggression', 'Distraction']
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
    
    # إنشاء الشكل مع قسمين (رسم بياني + دائرة)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # الرسم البياني بالأعمدة
    bars = ax1.bar(categories_ar, values, color=colors)
    ax1.set_title('ملخص سلوك القيادة / Driving Behavior Summary', fontsize=12)
    ax1.set_ylim([0, 150])
    
    # إضافة القيم على الأعمدة
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height}%',
                 ha='center', va='bottom', fontsize=10)
    
    # دائرة الأداء الكلي
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
    return chart_path

# دالة لإنشاء نصيحة القيادة
def generate_driving_tip(score):
    tips_ar = {
        'high': "أحسنت! أداؤك في القيادة ممتاز. حافظ على هذه المستويات العالية من التركيز والهدوء. تذكر أن القيادة الآمنة تتطلب الوعي المستمر بمحيطك وتوقع الأخطاء من الآخرين. خذ فترات راحة قصيرة كل ساعتين لتجديد نشاطك.",
        'medium': "أداؤك جيد ولكن هناك مجال للتحسين. حاول زيادة مستوى تركيزك وتقليل التشتت. القيادة الدفاعية هي مفتاح السلامة على الطريق. انتبه جيدًا للمشاة والمركبات الأخرى، وحافظ على مسافة آمنة.",
        'low': "هناك حاجة لتحسين أدائك في القيادة. ركز أكثر على الطريق وحاول تقليل العدوانية في قيادتك. تذكر أن القيادة بسرعة عالية أو بعدوانية تزيد من مخاطر الحوادث بشكل كبير."
    }
    
    tips_en = {
        'high': "Excellent! Your driving performance is outstanding. Maintain these high levels of focus and calmness. Remember that safe driving requires constant awareness of your surroundings and anticipating others' mistakes. Take short breaks every 2 hours to refresh.",
        'medium': "Good performance but there's room for improvement. Try to increase your focus and reduce distractions. Defensive driving is the key to road safety. Pay attention to pedestrians and other vehicles, and maintain a safe distance.",
        'low': "Your driving performance needs improvement. Focus more on the road and try to reduce aggression. Remember that high-speed or aggressive driving significantly increases accident risks."
    }
    
    if score > 80:
        return tips_ar['high'], tips_en['high']
    elif score > 50:
        return tips_ar['medium'], tips_en['medium']
    else:
        return tips_ar['low'], tips_en['low']

# دالة لإنشاء ملف PDF
def generate_pdf(chart_path, values):
    overall_score = np.mean(values)
    tip_ar, tip_en = generate_driving_tip(overall_score)
    
    pdf = FPDF()
    pdf.add_page()
    
    # الصفحة العربية
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'تقرير القيادة الذكية - SmartDrive Report', 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'السرعة / Speed: {values[0]} كم/ساعة / km/h', 0, 1)
    pdf.cell(0, 10, f'التركيز / Focus: {values[1]}%', 0, 1)
    pdf.cell(0, 10, f'الهدوء / Calmness: {values[2]}%', 0, 1)
    pdf.cell(0, 10, f'العدوانية / Aggression: {values[3]}%', 0, 1)
    pdf.cell(0, 10, f'التشتت / Distraction: {values[4]}%', 0, 1)
    pdf.ln(10)
    
    pdf.image(chart_path, x=10, w=190)
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'نصيحة القيادة / Driving Tip:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, tip_ar)
    pdf.ln(5)
    pdf.multi_cell(0, 8, tip_en)
    pdf.ln(10)
    
    # إضافة ملاحظة أن البيانات عشوائية
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, 'ملاحظة: هذا نموذج أولي يعتمد على بيانات عشوائية لتطبيق الفكرة.', 0, 1, 'C')
    pdf.cell(0, 10, 'Note: This is a prototype using random data for demonstration purposes.', 0, 1, 'C')
    
    pdf.output("driving_report.pdf")

# دالة إرسال الإيميل
def send_email(to_email):
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = "تقرير القيادة الذكية / SmartDrive Report"
    
    body = """
مرحباً / Hello,

تقرير القيادة الذكية الخاص بك مرفق بهذه الرسالة. 
Your SmartDrive report is attached to this email.

هذا نموذج أولي يعتمد على بيانات عشوائية لتطبيق الفكرة.
This is a prototype using random data for demonstration purposes.

مع تحياتي / Best regards,
سحر جمال / Sahar Jamal
"""
    message.attach(MIMEText(body, "plain"))
    
    with open("driving_report.pdf", "rb") as f:
        part = MIMEApplication(f.read(), Name="SmartDrive_Report.pdf")
        part['Content-Disposition'] = 'attachment; filename="SmartDrive_Report.pdf"'
        message.attach(part)
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("smartdrive.report@gmail.com","owjj okgp ljbl gztg")
        server.send_message(message)

# واجهة Streamlit
def main():
    st.set_page_config(page_title="تقرير القيادة الذكية / SmartDrive Report", layout="centered")
    
    # عنوان الصفحة باللغتين
    st.title("🚗 تقرير القيادة الذكية / SmartDrive Report")
    
    # معلومات التطبيق مع التنبيه أن البيانات عشوائية
    st.markdown("""
    <p style='text-align: center;'>
    بواسطة: <b>سحر جمال</b> / By: <b>Sahar Jamal</b><br>
    <span style='color: red; font-size: 14px;'>
    ملاحظة: هذا نموذج أولي يعتمد على بيانات عشوائية لتطبيق الفكرة.<br>
    Note: This is a prototype using random data for demonstration purposes.
    </span>
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    أدخل بريدك الإلكتروني للحصول على تقرير القيادة الذكي<br>
    Enter your email to receive your smart driving report
    """, unsafe_allow_html=True)
    
    # حقل الإدخال
    email = st.text_input("بريدك الإلكتروني / Your Email")
    
    # زر الإرسال
    if st.button("إرسال التقرير / Send Report"):
        if email:
            # توليد بيانات عشوائية
            values = [
                random.randint(60, 140),  # السرعة/Speed
                random.randint(50, 100),   # التركيز/Focus
                random.randint(40, 100),   # الهدوء/Calmness
                random.randint(0, 100),    # العدوانية/Aggression
                random.randint(0, 100)     # التشتت/Distraction
            ]
            
            # إنشاء التقرير وإرساله
            chart_path = create_chart(values)
            generate_pdf(chart_path, values)
            send_email(email)
            
            st.success("✅ تم إرسال التقرير بنجاح! يرجى التحقق من بريدك الإلكتروني. / Report sent successfully! Please check your email.")
        else:
            st.error("⚠ يرجى إدخال بريد إلكتروني صالح. / Please enter a valid email address.")

if __name__ == "__main__":
    main()
