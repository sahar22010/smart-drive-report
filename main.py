import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import random
from datetime import datetime
import smtplib
from email.message import EmailMessage
import traceback

# Page configuration
st.set_page_config(
    page_title="SmartDrive - Smart Driving Report",
    page_icon="🚗",
    layout="centered"
)

# Generate random driving metrics
def generate_metrics():
    return {
        "Smart Driving": random.randint(60, 100),
        "Smooth Turns": random.randint(40, 100),
        "Safe Stops": random.randint(50, 100),
        "Focus While Driving": random.randint(30, 100),
        "Speed Compliance": random.randint(70, 100),
        "Fuel Efficiency": random.randint(50, 100)
    }

# Create charts
def create_charts(metrics):
    try:
        # Pie chart
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(metrics.values(), labels=metrics.keys(), autopct='%1.1f%%',
                colors=['#08F7FE', '#FE53BB', '#F5D300', '#00ff00', '#9d4edd', '#ff6d00'])
        st.pyplot(fig1)

        # Bar chart
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        bars = ax2.bar(metrics.keys(), metrics.values(), 
                      color=['#08F7FE', '#FE53BB', '#F5D300', '#00ff00', '#9d4edd', '#ff6d00'])
        ax2.set_ylim(0, 110)
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height, f'{height}%', 
                    ha='center', va='bottom')
        st.pyplot(fig2)
    except Exception as e:
        st.error(f"Chart generation error: {str(e)}")

# Generate PDF report
def generate_pdf(metrics, tip):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(0, 15, "SmartDrive - Smart Driving Report", ln=True, align='C')

        pdf.set_font("Arial", '', 16)
        pdf.cell(0, 10, "Prototype - Simulated Data", ln=True, align='C')
        pdf.ln(15)

        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 10, "Results:", ln=True)

        pdf.set_font("Arial", '', 14)
        for key, value in metrics.items():
            pdf.cell(0, 10, f"{key}: {value}%", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Tip:", ln=True)
        pdf.set_font("Arial", '', 14)
        pdf.multi_cell(0, 10, tip)

        pdf.ln(10)
        pdf.set_font("Arial", 'I', 12)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

        return pdf.output(dest="S").encode("latin1")
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        return None

# Send the PDF report via email
def send_email(receiver_email, pdf_bytes):
    try:
        sender_email = "smartdrive.report@gmail.com"
        sender_password = "owjj okgp ljbl gztg"  # App password

        if not sender_email or sender_password == "your_app_password_here":
            raise ValueError("❗ Email settings not completed")

        msg = EmailMessage()
        msg['Subject'] = "SmartDrive Report"
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg.set_content("""
        Hello,

        Please find attached your smart driving report.
        Thank you for using SmartDrive! 🚗
        """)

        msg.add_attachment(
            pdf_bytes,
            maintype='application',
            subtype='pdf',
            filename="smartdrive_report.pdf"
        )

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Failed to send: {str(e)}")
        st.text(traceback.format_exc())
        return False

# Main Streamlit UI
def main():
    st.title("🚗 SmartDrive - Smart Driving Report")

    with st.form("report_form"):
        user_email = st.text_input("📧 Enter your email:")
        submitted = st.form_submit_button("🎯 Generate Report")

        if submitted:
            if not user_email:
                st.warning("⚠ Please enter a valid email address.")
            else:
                with st.spinner("Generating your report..."):
                    try:
                        metrics = generate_metrics()
                        weakest = min(metrics, key=metrics.get)
                        tip = f"Tip: Focus on improving {weakest} ({metrics[weakest]}%)"

                        st.subheader("📊 Results")
                        create_charts(metrics)

                        st.subheader("💡 Tip")
                        st.success(tip)

                        pdf_bytes = generate_pdf(metrics, tip)
                        if pdf_bytes:
                            st.download_button(
                                label="⬇ Download PDF",
                                data=pdf_bytes,
                                file_name="smartdrive_report.pdf",
                                mime="application/pdf"
                            )

                            if send_email(user_email, pdf_bytes):
                                st.success(f"✅ Report sent to: {user_email}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

if __name__== "__main__":
    main()
