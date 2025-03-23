import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import re
import os
from datetime import datetime

# Function to classify records as encrypted or non-encrypted
def classify_encryption(df):
    # Create a new column to indicate if a record is encrypted
    df['is_encrypted'] = df.apply(
        lambda row: 1 if ('*' in str(row['Name']) or 
                          '*' in str(row['Email']) or 
                          '-' in str(row['Age']) or 
                          '-' in str(row['Salary'])) 
        else 0, axis=1
    )
    return df

# Function to create visualizations
def create_visualizations(df):
    # Count of encrypted vs non-encrypted records
    plt.figure(figsize=(10, 6))
    counts = df['is_encrypted'].value_counts()
    labels = ['Non-Encrypted', 'Encrypted'] if 0 in counts.index else ['Encrypted', 'Non-Encrypted']
    colors = ['#5cb85c', '#d9534f']
    
    plt.pie(counts, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.axis('equal')
    plt.title('Distribution of Encrypted vs Non-Encrypted Records')
    plt.tight_layout()
    plt.savefig('encryption_distribution.png')
    
    # Salary distribution based on encryption status
    plt.figure(figsize=(10, 6))
    
    # For non-encrypted records, use actual salary
    non_encrypted = df[df['is_encrypted'] == 0]
    
    # For encrypted records, use the average of salary range
    encrypted = df[df['is_encrypted'] == 1].copy()
    
    # Convert salary ranges to average values for visualization purposes
    def extract_avg_salary(salary_range):
        if isinstance(salary_range, str) and '-' in salary_range:
            min_val, max_val = salary_range.split('-')
            return (float(min_val) + float(max_val)) / 2
        return salary_range
    
    encrypted['Salary_Avg'] = encrypted['Salary'].apply(extract_avg_salary)
    
    # Plot
    if len(non_encrypted) > 0:
        sns.histplot(non_encrypted['Salary'], color='#5cb85c', label='Non-Encrypted', alpha=0.7, kde=True)
    
    if len(encrypted) > 0:
        sns.histplot(encrypted['Salary_Avg'], color='#d9534f', label='Encrypted', alpha=0.7, kde=True)
    
    plt.title('Salary Distribution by Encryption Status')
    plt.xlabel('Salary')
    plt.ylabel('Count')
    plt.legend()
    plt.tight_layout()
    plt.savefig('salary_distribution.png')
    
    # Age distribution
    plt.figure(figsize=(10, 6))
    
    # For non-encrypted records, use actual age
    
    # For encrypted records, use the average of age range
    def extract_avg_age(age_range):
        if isinstance(age_range, str) and '-' in age_range:
            min_val, max_val = age_range.split('-')
            return (float(min_val) + float(max_val)) / 2
        return age_range
    
    if len(encrypted) > 0:
        encrypted['Age_Avg'] = encrypted['Age'].apply(extract_avg_age)
    
    # Plot
    if len(non_encrypted) > 0:
        sns.histplot(non_encrypted['Age'], color='#5cb85c', label='Non-Encrypted', alpha=0.7, kde=True)
    
    if len(encrypted) > 0:
        sns.histplot(encrypted['Age_Avg'], color='#d9534f', label='Encrypted', alpha=0.7, kde=True)
    
    plt.title('Age Distribution by Encryption Status')
    plt.xlabel('Age')
    plt.ylabel('Count')
    plt.legend()
    plt.tight_layout()
    plt.savefig('age_distribution.png')

# Function to create a PDF report
def create_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    
    # Set up fonts
    pdf.set_font('Arial', 'B', 16)
    
    # Title
    pdf.cell(190, 10, 'CSV Encryption Classification Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Date of analysis
    pdf.set_font('Arial', '', 10)
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(190, 10, f'Report generated on: {today}', 0, 1, 'R')
    pdf.ln(5)
    
    # Summary statistics
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(190, 10, 'Summary Statistics:', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    total_records = len(df)
    encrypted_records = df['is_encrypted'].sum()
    non_encrypted_records = total_records - encrypted_records
    
    pdf.cell(190, 10, f'Total Records: {total_records}', 0, 1)
    pdf.cell(190, 10, f'Encrypted Records: {encrypted_records} ({encrypted_records/total_records*100:.1f}%)', 0, 1)
    pdf.cell(190, 10, f'Non-Encrypted Records: {non_encrypted_records} ({non_encrypted_records/total_records*100:.1f}%)', 0, 1)
    pdf.ln(10)
    
    # Add visualizations
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(190, 10, 'Visual Analysis:', 0, 1)
    pdf.ln(5)
    
    # Add the pie chart
    pdf.image('encryption_distribution.png', x=10, y=None, w=190)
    pdf.ln(5)
    
    # Add the salary distribution
    pdf.image('salary_distribution.png', x=10, y=None, w=190)
    pdf.ln(5)
    
    # Add the age distribution
    pdf.image('age_distribution.png', x=10, y=None, w=190)
    pdf.ln(10)
    
    # Sample records
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(190, 10, 'Sample Records:', 0, 1)
    pdf.ln(5)
    
    # Add sample of both encrypted and non-encrypted records
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(20, 10, 'ID', 1, 0, 'C')
    pdf.cell(40, 10, 'Name', 1, 0, 'C')
    pdf.cell(20, 10, 'Age', 1, 0, 'C')
    pdf.cell(60, 10, 'Email', 1, 0, 'C')
    pdf.cell(30, 10, 'Salary', 1, 0, 'C')
    pdf.cell(20, 10, 'Encrypted', 1, 1, 'C')
    
    pdf.set_font('Arial', '', 8)
    
    # Sample of non-encrypted records
    non_encrypted_sample = df[df['is_encrypted'] == 0].head(3)
    for _, row in non_encrypted_sample.iterrows():
        pdf.cell(20, 10, str(row['ID']), 1, 0, 'C')
        pdf.cell(40, 10, str(row['Name']), 1, 0, 'L')
        pdf.cell(20, 10, str(row['Age']), 1, 0, 'C')
        pdf.cell(60, 10, str(row['Email']), 1, 0, 'L')
        pdf.cell(30, 10, str(row['Salary']), 1, 0, 'R')
        pdf.cell(20, 10, 'No', 1, 1, 'C')
    
    # Sample of encrypted records
    encrypted_sample = df[df['is_encrypted'] == 1].head(3)
    for _, row in encrypted_sample.iterrows():
        pdf.cell(20, 10, str(row['ID']), 1, 0, 'C')
        pdf.cell(40, 10, str(row['Name']), 1, 0, 'L')
        pdf.cell(20, 10, str(row['Age']), 1, 0, 'C')
        pdf.cell(60, 10, str(row['Email']), 1, 0, 'L')
        pdf.cell(30, 10, str(row['Salary']), 1, 0, 'R')
        pdf.cell(20, 10, 'Yes', 1, 1, 'C')
    
    # Conclusion
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(190, 10, 'Conclusion:', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(190, 10, 'This report shows the analysis of encrypted versus non-encrypted records in the dataset. The classification is based on the presence of asterisks (*) in Name and Email fields, and range values (using hyphens) in Age and Salary fields. The classification model successfully identified encrypted records and provided visual representations of the data distribution.')
    
    # Save the PDF
    pdf.output('encryption_classification_report.pdf')

# Main function to run the entire process
def main(csv_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Classify records
    df = classify_encryption(df)
    
    # Create visualizations
    create_visualizations(df)
    
    # Create PDF report
    create_pdf_report(df)
    
    # Save the classified data
    df.to_csv('classified_data.csv', index=False)
    
    print(f"Classification complete. Found {df['is_encrypted'].sum()} encrypted records out of {len(df)} total records.")
    print("Visualizations and PDF report have been generated.")

if __name__ == "__main__":
    # Replace with your CSV file path
    csv_file_path = "result.csv"
    main(csv_file_path)
