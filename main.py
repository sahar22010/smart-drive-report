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

# Email settings (replace with your actual credentials)
SENDER_EMAIL = "smartdrive.report@gmail.com"
APP_PASSWORD = "‏owjj okgp ljbl gztg" 

def create_chart(values):
    categories = ['Speed', 'Focus', 'Calmness', 'Aggression', 'Distraction']
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Bar chart
    bars = ax1.bar(categories, values, color=colors)
    ax1.set_title('Driving Performance', fontsize=14, pad=20)
    ax1.set_ylim([0, 150])
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height}%',
                 ha='center', va='bottom', fontsize=10)
    
    # Score circle
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
            "• Maintain your high focus levels\n"
            "• Keep safe following distance\n"
            "• Take breaks every 2 hours\n"
            "• Stay aware of surroundings\n\n"
            "You're setting a great example for safe driving!"
        )
    elif score > 50:
        return (
            "GOOD DRIVING\n\n"
            "• Reduce minor distractions\n"
            "• Practice smooth acceleration\n"
            "• Check mirrors frequently\n"
            "• Anticipate other drivers' actions\n\n"
            "With small improvements, you'll reach excellent level!"
        )
    else:
        return (
            "NEEDS IMPROVEMENT\n\n"
            "• Reduce aggressive maneuvers\n"
            "• Minimize phone usage\n"
            "• Maintain steady speed\n"
            "• Increase following distance\n\n"
            "Consider taking a defensive driving course."
        )

def create_pdf(chart_path, values, overall_score):
    pdf = FPDF()
    
    # Page 1 - Summary
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
    
    # Page 2 - Tips
    pdf.add_page()
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, 'PERSONALIZED DRIVING TIPS', 0, 1)
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 14)  # Larger font for readability
    pdf.multi_cell(0, 8, generate_tip(overall_score))
    
    pdf.output("report.pdf")
    return True

def send_email(to_email):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = "Your SmartDrive Report"
    
    body = """
Hi there,

Your personalized driving report is attached.

This includes:
- Your driving performance scores
- Detailed analysis
- Personalized improvement tips

Drive safe!
The SmartDrive Team
"""
    msg.attach(MIMEText(body, 'plain'))
    
    with open("report.pdf", "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename="report.pdf")
        msg.attach(attach)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

def main():
    st.set_page_config(page_title="SmartDrive", layout="centered")
    st.title("🚗 SmartDrive Analytics")
    
    st.markdown("""
    <p style='text-align:center;'>
    Get your personalized driving report<br>
    <span style='color:gray; font-size:14px;'>
    Prototype version - uses simulated data
    </span>
    </p>
    """, unsafe_allow_html=True)
    
    email = st.text_input("Your Email Address")
    
    if st.button("Generate Report"):
        if "@" in email and "." in email:
            values = [
                random.randint(60, 140),
                random.randint(50, 100),
                random.randint(40, 100),
                random.randint(0, 100),
                random.randint(0, 100)
            ]
            
            chart_path, score = create_chart(values)
            if create_pdf(chart_path, values, score):
                send_email(email)
                st.success("✅ Report sent! Check your email.")
            else:
                st.error("Failed to generate report")
        else:
            st.warning("Please enter a valid email")


if __name__ == "__main__":
    main()
