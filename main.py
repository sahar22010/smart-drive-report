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
APP_PASSWORD = "owjj okgp ljbl gztg"  # يجب تغييرها في الإنتاج الحقيقي

# دالة لإنشاء الرسم البياني
def create_chart(values):
    categories_ar = ['السرعة', 'التركيز', 'الهدوء', 'العدوانية', 'التشتت']
    categories_en = ['Speed', 'Focus', 'Calmness', 'Aggression', 'Distraction']
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # الرسم البياني
    bars = ax1.bar(categories_ar, values, color=colors)
    ax1.set_title('ملخص سلوك القيادة / Driving Behavior Summary', fontsize=12)
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
    ax2.set_title('النسبة الكلية / Overall Score', fontsize=12)
    ax2.axis('off')
    
    plt.tight_layout()
    chart_path = "chart.png"
    fig.savefig(chart_path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return chart_path, overall_score

# دالة النصائح
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

# دالة إنشاء PDF
def generate_pdf(chart_path, values, overall_score):
    pdf = FPDF()
    
    # إضافة الخطوط
    pdf.add_font('NotoArabic', '', 'NotoKufiArabic-Regular.ttf', uni=True)
    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
    
    # الصفحة الرئيسية
    pdf.add_page()
    
    # العنوان
    pdf.set_font('NotoArabic', '', 16)
    pdf.cell(0, 10, 'تقرير القيادة الذكية', 0, 1, 'C')
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, 'SmartDrive Report', 0, 1, 'C')
    pdf.ln(10)
    
    # البيانات
    pdf.set_font('NotoArabic', '', 12)
    pdf.cell(0, 10, f'السرعة: {values[0]} كم/ساعة', 0, 1)
    pdf.cell(0, 10, f'التركيز: {values[1]}%', 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Speed: {values[0]} km/h', 0, 1)
    pdf.cell(0, 10, f'Focus: {values[1]}%', 0, 1)
    pdf.ln(10)
    
    # الصورة
    pdf.image(chart_path, x=10, w=190)
    pdf.ln(10)
    
    # النصائح
    tip_ar, tip_en = generate_driving_tip(overall_score)
    pdf.set_font('NotoArabic', '', 12)
    pdf.multi_cell(0, 8, tip_ar)
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, tip_en)
    pdf.ln(10)
    
    # الملاحظة
    pdf.set_text_color(128, 128, 128)
    pdf.set_font('NotoArabic', '', 10)
    pdf.cell(0, 10, 'هذا نموذج أولي يعتمد على بيانات عشوائية', 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.
