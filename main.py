import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import random
import numpy as np
from matplotlib.patches import Circle
import sqlite3
from datetime import datetime

# إعدادات الإيميل - استبدلها ببياناتك
SENDER_EMAIL = "smartdrive.report@gmail.com"
APP_PASSWORD = "owjj okgp ljbl gztg"

# ------ تسجيل الزوار ------
def init_db():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  visit_time TIMESTAMP,
                  visitor_ip TEXT,
                  user_agent TEXT,
                  email TEXT)''')
    conn.commit()
    conn.close()

def log_visit(email=None):
    try:
        conn = sqlite3.connect('visitors.db')
        c = conn.cursor()
        visit_time = datetime.now()
        c.execute("INSERT INTO visitors (visit_time, email) VALUES (?, ?)",
                 (visit_time, email))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging visit: {e}")

init_db()

# ------ واجهة التطبيق ------
st.set_page_config(page_title="SmartDrive Report", layout="centered")

# Header Section
st.markdown("""
<h1 style='text-align: center; color: #2E86C1; margin-bottom: 5px;'>
🚗 SmartDrive – AI-Powered Driving Behavior Report
</h1>
<p style='text-align: center; font-size: 18px; color: #5D6D7E; margin-top: 5px;'>
Know your drive. Improve it.
</p>
""", unsafe_allow_html=True)

# Info Box
st.markdown("""
<div style='border: 2px solid #2E86C1; padding: 15px; border-radius: 8px; 
            background-color: #F4F6F7; color: #154360; font-size: 16px;
            margin-bottom: 25px;'>
<b>SmartDrive</b> combines data science and AI to give you smart insights into your driving behavior. 
Save time, drive smarter, and become a better driver.<br><br>

This is just the beginning. In the future, I aim to develop this project into a real system that can 
be applied nationwide using surveillance cameras to monitor driving and prevent dangerous behavior — 
starting from this prototype based on random data. The goal is to protect lives and improve road 
safety across all communities.
</div>
""", unsafe_allow_html=True)

# ------ الوظائف الأساسية ------
def create_chart(values):
    categories = ['Speed', 'Focus', 'Calmness', 'Aggression', 'Distraction']
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # الرسم البياني
    bars = ax1.bar(categories, values, color=colors)
    ax1.set_title('Driving Performance', fontsize=14, pad=20)
    ax1.set_ylim([0, 150])
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height}%',
                 ha='center', va='bottom', fontsize=10)
    
    # دائرة الأداء
    overall_score = np.mean(values)
    color = '#2ca02c' if overall_score > 70 else '#ff7f0e' if overall_score > 40 else '#d62728'
    circle = Circle((0.5, 0.5), 0.4, fill=False, linewidth=10, color=color)
    ax2.add_patch(circle)
    ax2.text(0.5, 0.5, f'{overall_score:.0f}%', 
             ha='center', va='center', fontsize=24, fontweight='bold')
    ax2.set_title('Overall Score', fontsize=14, pad=20)
    ax2.axis('off')
    
    plt.tight_layout()
    chart_path = "chart.png"
    fig.savefig(chart_path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return chart_path, overall_score

def generate_tip(score):
    if score > 80:
        return (
            "EXCELLENT DRIVING!\n\n"
            "• You're in the top 10% of drivers!\n"
            "• Maintain your perfect focus\n"
            "• Keep this safe driving pattern\n"
            "• Take breaks every 2 hours\n\n"
            "Advice: Share your skills with others!"
        )
    elif score > 50:
        return (
            "GOOD PERFORMANCE\n\n"
            "• Slightly reduce distractions\n"
            "• Improve smooth acceleration\n"
            "• Check mirrors more frequently\n"
            "• Anticipate other drivers' moves\n\n"
            "Advice: Small tweaks will make you excellent!"
        )
    else:
        return (
            "NEEDS IMPROVEMENT\n\n"
            "• Reduce aggressive maneuvers\n"
            "• Eliminate phone usage\n"
            "• Maintain steady speed\n"
            "• Increase following distance\n\n"
            "Advice: Consider a defensive driving course."
        )

def create_pdf(chart_path, values, overall_score):
    pdf = FPDF()
    
    # الصفحة الأولى
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 15, 'SMART DRIVE REPORT', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 8, f'Speed: {values[0]} km/h', 0, 1)
    pdf.cell(0, 8, f'Focus: {values[1]}%', 0, 1)
    pdf.cell(0, 8, f'Calmness: {values[2]}%', 0, 1)
    pdf.cell(0, 8, f'Aggression: {values[3]}%', 0, 1)
    pdf.cell(0, 8, f'Distraction: {values[4]}%', 0, 1)
    pdf.ln(15)
    
    pdf.image(chart_path, x=10, w=190)
    pdf.ln(15)
    
    # الصفحة الثانية
    pdf.add_page()
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, 'PERSONALIZED DRIVING TIPS', 0, 1)
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 8, generate_tip(overall_score))
    
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, 'Report generated by Sahar Jamal', 0, 0, 'C')
    
    pdf.output("driving_report.pdf")
    return True

def send_email(to_email):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = "Your SmartDrive Report is Ready!"
    
    body = """
Hello Driver,

Your personalized SmartDrive report is attached.

This includes:
- Your driving performance scores
- Detailed analysis
- Custom improvement tips

Drive safely!
- Sahar Jamal
"""
    msg.attach(MIMEText(body, 'plain'))
    
    with open("driving_report.pdf", "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename="driving_report.pdf")
        msg.attach(attach)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

# ------ إحصاءات الزوار ------
def show_stats():
    try:
        conn = sqlite3.connect('visitors.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM visitors")
        total_visits = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM visitors WHERE email IS NOT NULL")
        reports_sent = c.fetchone()[0]
        conn.close()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Project Stats")
        st.sidebar.markdown(f"📊 Total Visits: *{total_visits}*")
        st.sidebar.markdown(f"📨 Reports Sent: *{reports_sent}*")
        st.sidebar.markdown("""
        <small>Developed by <b>Sahar Jamal</b><br>
        AI-powered road safety solution</small>
        """, unsafe_allow_html=True)
    except:
        pass

# ------ الواجهة الرئيسية ------
email = st.text_input("Your Email Address")

if st.button("Generate My Report"):
    if "@" in email and "." in email:
        # توليد بيانات عشوائية
        values = [
            random.randint(60, 140),  # Speed
            random.randint(50, 100),  # Focus
            random.randint(40, 100),  # Calmness
            random.randint(0, 100),   # Aggression
            random.randint(0, 100)    # Distraction
        ]
        
        chart_path, score = create_chart(values)
        if create_pdf(chart_path, values, score):
            send_email(email)
            log_visit(email)  # تسجيل الزيارة مع الإيميل
            st.success("✅ Report sent successfully! Check your email.")
        else:
            st.error("❌ Failed to generate report")
    else:
        st.warning("⚠ Please enter a valid email address")

# تسجيل الزيارة بدون إيميل (عند فتح الصفحة فقط)
log_visit()

# عرض الإحصاءات
show_stats()

# Footer
st.markdown("""
<p style='text-align:center; font-size: 14px; color: #7F8C8D; margin-top: 50px;'>
By: <b>Sahar Jamal</b> | Prototype for demonstration purposes
</p>
""", unsafe_allow_html=True)

