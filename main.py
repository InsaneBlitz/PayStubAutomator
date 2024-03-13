import os
import sys
import fitz  # PyMuPDF for handling PDF files
import re  # Regular expression module for email pattern matching
import smtplib
from email.message import EmailMessage
import json
from google.cloud import secretmanager

# Placeholder module to handle file paths. Users should replace 'filepath' with their own path handling solution.
from filepath import FilePath

def resource_path(relative_path):
    """
    Converts a relative resource path to an absolute path, accommodating different execution environments.
    
    Parameters:
    - relative_path (str): The relative path to the resource.
    
    Returns:
    - str: The absolute path to the resource.
    """
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, relative_path)

def getSecret(project_id, secret_id, service_account):
    """
    Retrieves secret values from Google Cloud Secret Manager.
    
    Parameters:
    - project_id (str): Google Cloud project ID.
    - secret_id (str): The ID of the secret to retrieve.
    - service_account (str): Path to the service account JSON file.
    
    Returns:
    - dict: Secret values in key-value pairs, or None if an error occurs.
    """
    try:
        client = secretmanager.SecretManagerServiceClient.from_service_account_json(service_account)
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": secret_name})
        secret_values = json.loads(response.payload.data.decode("UTF-8"))
        return secret_values
    except Exception as e:
        print(f"Error occurred while retrieving secret values: {str(e)}")
        return None

def send_email(sender_email, sender_password, receiver_email, pay_stub_path, body=''):
    """
    Sends an email with a pay stub PDF attached.
    
    Parameters:
    - sender_email (str): The email address of the sender.
    - sender_password (str): The password for the sender's email account.
    - receiver_email (str): The email address of the receiver.
    - pay_stub_path (str): The file path of the pay stub PDF to attach.
    - body (str, optional): The body text of the email. Defaults to an empty string.
    """
    sent_folder_path = 'Sent'
    if not os.path.exists(sent_folder_path):
        os.makedirs(sent_folder_path)
    
    msg = EmailMessage()
    msg['Subject'] = 'Pay Stub'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(body)

    with open(pay_stub_path, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=os.path.basename(pay_stub_path))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)
    move_to_sent_folder(pay_stub_path)

def move_to_sent_folder(pay_stub_path):
    """
    Moves the pay stub PDF to the 'Sent' folder after sending the email.
    
    Parameters:
    - pay_stub_path (str): The file path of the pay stub PDF.
    """
    sent_folder_path = 'Sent'
    original_name = os.path.basename(pay_stub_path)
    base, ext = os.path.splitext(original_name)
    date_part, name_part = base.split(' - ', 1)
    sent_file_path = os.path.join(sent_folder_path, original_name)
    counter = 1
    while os.path.exists(sent_file_path):
        unique_name = f"{date_part} - {name_part} - {counter}{ext}"
        sent_file_path = os.path.join(sent_folder_path, unique_name)
        counter += 1
    os.rename(pay_stub_path, sent_file_path)

def process_pay_stubs(pdf_path, period_end_date, sender_email, sender_password, email_body):
    """
    Processes the pay stubs from a PDF, extracting individual stubs and emailing them.
    
    Parameters:
    - pdf_path (str): Path to the source PDF containing pay stubs.
    - period_end_date (str): The end date of the pay period for filename generation.
    - sender_email (str): The email address of the sender.
    - sender_password (str): The password for the sender's email account.
    - email_body (str): Additional message body for the email.
    """
    if not os.path.exists('Failed to Send'):
        os.makedirs('Failed to Send')

    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        email_match = re.search(r'([\w\.-]+)@[domain]\.com', text)  # Replace [domain] with your domain
        if email_match:
            email = email_match.group(0)
            email_identifier = email_match.group(1)
            output_pdf_path = f"{period_end_date} - {email_identifier}.pdf"
            stub_pdf = fitz.open()
            stub_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
            stub_pdf.save(output_pdf_path)
            stub_pdf.close()
            
            try:
                send_email(sender_email, sender_password, email, output_pdf_path, email_body)
                print(f"Sent pay stub to {email}")
            except Exception as e:
                print(f"Failed to send pay stub to {email}: {e}")
                move_to_failed_send_folder(output_pdf_path)
        else:
            print(f"No email found on page {page_num + 1}.")
    doc.close()

def move_to_failed_send_folder(output_pdf_path):
    """
    Moves a pay stub PDF to the 'Failed to Send' folder.
    
    Parameters:
    - output_pdf_path (str): The file path of the pay stub PDF.
    """
    os.rename(output_pdf_path, os.path.join('Failed to Send', output_pdf_path))

def main():
    """
    Main function to handle user inputs and process pay stubs.
    """
    # Placeholder values for project_id and secret_id. Replace these with your actual project ID and secret ID.
    PROJECT_ID = 'your-google-cloud-project-id'
    SECRET_ID = 'your-secret-id'

    service_Account = FilePath('path-to-your-service-account-file.json')

    pdf_file_name = input("Please enter the file name of the PDF: ")
    pdf_path = resource_path(pdf_file_name)

    secretValues = getSecret(PROJECT_ID, SECRET_ID, service_Account)
    if secretValues is not None:
        sender_email = secretValues['email']
        password = secretValues['email_password']
        period_end_date = input("Please enter the Period End Date (MM/DD/YYYY): ")
        formatted_date = period_end_date.replace('/', '-')
        email_body = input("Please enter any additional message for the email body (optional): ")
        
        process_pay_stubs(pdf_path, formatted_date, sender_email, password, email_body)
        print("Paystubs sent. Please review the 'Failed to Send' folder for any issues.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    print("Paystub Processing Script")
    main()
