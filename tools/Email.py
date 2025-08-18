import email
import pytesseract
from PIL import Image
import io
import imaplib
from tkinter import Tk, Label, Entry, Button, messagebox, StringVar, END, Text
from tkinter.ttk import Progressbar, Combobox
import threading
import time
from datetime import datetime

class EmailOCRApp:
    def __init__(self, master):
        self.master = master
        master.title("Email OCR Processor")
        master.geometry("500x400")
        
        self.email_var = StringVar()
        self.password_var = StringVar()
        self.server_var = StringVar(value="imap.gmail.com")
        self.limit_var = StringVar(value="5")
        
        Label(master, text="Email Address:").pack(pady=(10,0))
        Entry(master, textvariable=self.email_var, width=40).pack()
        
        Label(master, text="Password:").pack(pady=(10,0))
        Entry(master, textvariable=self.password_var, show="*", width=40).pack()
        
        Label(master, text="IMAP Server:").pack(pady=(10,0))
        Entry(master, textvariable=self.server_var, width=40).pack()
        
        Label(master, text="Number of Emails to Process:").pack(pady=(10,0))
        Entry(master, textvariable=self.limit_var, width=40).pack()
        
        self.progress = Progressbar(master, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)
        
        Button(master, text="Process Emails", command=self.start_processing).pack(pady=10)
        
        self.result_text = Text(master, height=10, width=60)
        self.result_text.pack(pady=10)
        
    def start_processing(self):
        email = self.email_var.get()
        password = self.password_var.get()
        server = self.server_var.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Email and password are required!")
            return
            
        try:
            limit = int(self.limit_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for email limit")
            return
            
        self.progress["value"] = 0
        self.result_text.delete(1.0, END)
        self.result_text.insert(END, "Processing emails...\n")
        
        processing_thread = threading.Thread(
            target=self.process_emails_thread,
            args=(email, password, server, limit)
        )
        processing_thread.start()
        
def process_emails_thread(self, email, password, server, limit):
    try:
        if self.is_processing:
            self.master.after(0, self.show_error, "Another process is already running!")
            return
            
        self.is_processing = True
        self.master.after(0, lambda: self.progress.config(mode='indeterminate'))
        self.master.after(0, self.progress.start)
        
        processor = EmailOCRProcessor(email, password, server)
        
        def progress_callback(current, total):
            progress = (current / total) * 100
            self.master.after(0, self.update_progress, progress)
            
        emails_data = processor.process_emails(limit, progress_callback)
        processor.close_connection()
        
        self.master.after(0, self.display_results, emails_data)
        
    except imaplib.IMAP4.error as e:
        error_msg = f"IMAP Error: {str(e)}"
        self.master.after(0, self.show_error, error_msg)
    except pytesseract.TesseractNotFoundError:
        self.master.after(0, self.show_error, "Tesseract OCR is not installed or not in system PATH")
    except Exception as e:
        self.master.after(0, self.show_error, f"Unexpected error: {str(e)}")
    finally:
        self.is_processing = False
        self.master.after(0, lambda: self.progress.config(mode='determinate'))
        self.master.after(0, self.progress.stop)

def update_progress(self, value):
    self.progress["value"] = value
    self.master.update_idletasks()

def display_results(self, emails_data):
    self.result_text.delete(1.0, END)
    
    if not emails_data:
        self.result_text.insert(END, "No emails found or processed.\n")
        return
        
    for i, email_data in enumerate(emails_data):
        self.result_text.insert(END, f"\n Email {i+1}:\n")
        self.result_text.insert(END, f" Subject: {email_data['subject']}\n")
        self.result_text.insert(END, f" From: {email_data['from']}\n")
        self.result_text.insert(END, f" Date: {email_data.get('date', 'N/A')}\n")
        
        if email_data['text']:
            self.result_text.insert(END, "\n Text Content:\n")
            self.result_text.insert(END, email_data['text'][:500] + ("..." if len(email_data['text']) > 500 else "") + "\n")
            
        for j, img_text in enumerate(email_data['images_text']):
            self.result_text.insert(END, f"\n Extracted Text from Image {j+1}:\n")
            self.result_text.insert(END, img_text[:300] + ("..." if len(img_text) > 300 else "") + "\n")
            
        self.result_text.insert(END, "\n" + "═"*50 + "\n")
    
    self.progress["value"] = 100
    self.master.after(0, lambda: messagebox.showinfo(
        "Success", 
        f"Successfully processed {len(emails_data)} emails"
    ))
    
    save = messagebox.askyesno("Save Results", "Would you like to save the results to a file?")
    if save:
        self.save_results_to_file(emails_data)

def save_results_to_file(self, emails_data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"email_ocr_results_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for i, email_data in enumerate(emails_data):
                f.write(f"\nEmail {i+1}:\n")
                f.write(f"Subject: {email_data['subject']}\n")
                f.write(f"From: {email_data['from']}\n")
                
                if email_data['text']:
                    f.write("\nText Content:\n")
                    f.write(email_data['text'] + "\n")
                    
                for j, img_text in enumerate(email_data['images_text']):
                    f.write(f"\nExtracted Text from Image {j+1}:\n")
                    f.write(img_text + "\n")
                
                f.write("\n" + "="*50 + "\n")
                
        messagebox.showinfo("Success", f"Results saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save results: {str(e)}")
        self.progress["value"] = 100
        messagebox.showinfo("Success", "Email processing completed!")
        
    def show_error(self, error_msg):
        self.result_text.insert(END, f"\nError: {error_msg}\n")
        self.progress["value"] = 0
        messagebox.showerror("Error", error_msg)


class EmailOCRProcessor:
    def __init__(self, email_account, password, server='imap.gmail.com'):
        self.email_account = email_account
        self.password = password
        self.server = server
        
    def connect_to_mailbox(self):
        self.mail = imaplib.IMAP4_SSL(self.server)
        self.mail.login(self.email_account, self.password)
        self.mail.select('inbox')
    
    def process_emails(self, limit=10):
        self.connect_to_mailbox()
        
        typ, data = self.mail.search(None, 'ALL')
        email_ids = data[0].split()
        
        results = []
        for i, email_id in enumerate(email_ids[:limit]):
            typ, msg_data = self.mail.fetch(email_id, '(RFC822)')
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            email_info = {
                'subject': self.decode_header(email_message['subject']),
                'from': self.decode_header(email_message['from']),
                'text': '',
                'images_text': []
            }
            
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    try:
                        email_info['text'] += part.get_payload(decode=True).decode('utf-8', errors='replace')
                    except:
                        pass
                
                if 'image' in content_type and 'attachment' in content_disposition:
                    try:
                        image_data = part.get_payload(decode=True)
                        image = Image.open(io.BytesIO(image_data))
                        
                        extracted_text = pytesseract.image_to_string(image, lang='fas+eng')
                        email_info['images_text'].append(extracted_text)
                    except Exception as e:
                        email_info['images_text'].append(f"Error processing image: {str(e)}")
            
            results.append(email_info)
        
        return results
    
    def decode_header(self, header):
        if header is None:
            return ""
            
        decoded = []
        for part, charset in email.header.decode_header(header):
            if isinstance(part, bytes):
                try:
                    decoded.append(part.decode(charset if charset else 'utf-8', errors='replace'))
                except:
                    decoded.append(part.decode('utf-8', errors='replace'))
            else:
                decoded.append(str(part))
                
        return ' '.join(decoded)
    
    def close_connection(self):
        try:
            self.mail.close()
            self.mail.logout()
        except:
            pass

def main():
    print("""

███████╗███╗░░░███╗░█████╗░██╗██╗░░░░░  ░██████╗██╗██╗░░░░░███████╗███╗░░██╗░█████╗░███████╗
██╔════╝████╗░████║██╔══██╗██║██║░░░░░  ██╔════╝██║██║░░░░░██╔════╝████╗░██║██╔══██╗██╔════╝
█████╗░░██╔████╔██║███████║██║██║░░░░░  ╚█████╗░██║██║░░░░░█████╗░░██╔██╗██║██║░░╚═╝█████╗░░
██╔══╝░░██║╚██╔╝██║██╔══██║██║██║░░░░░  ░╚═══██╗██║██║░░░░░██╔══╝░░██║╚████║██║░░██╗██╔══╝░░
███████╗██║░╚═╝░██║██║░░██║██║███████╗  ██████╔╝██║███████╗███████╗██║░╚███║╚█████╔╝███████╗
╚══════╝╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝╚══════╝  ╚═════╝░╚═╝╚══════╝╚══════╝╚═╝░░╚══╝░╚════╝░╚══════╝
    """)
if __name__ == '__main__':
    root = Tk()
    app = EmailOCRApp(root)
    
    
    root.mainloop()
        self.is_processing = False
