import os
import socket
import smtplib
from requests import get
from fuzzywuzzy import fuzz
from googlesearch import search
from bs4 import BeautifulSoup
import colorama

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
                print(stdOutput("error") + f"Error sending email: {e}")
                break

        server.quit()
        print(stdOutput("info") + "Finished sending emails.")

    except smtplib.SMTPAuthenticationError as e:
        print(stdOutput("error") + f"Authentication error: {e}")
    except Exception as e:
        print(stdOutput("error") + f"Unexpected error: {e}")

def search_links(query):
    results = 100
    print(f"[~] Searching for '{query}'")

    for url in search(query, stop=results):
        print(f'\n[+] Url detected: {url}')
        try:
            text = get(url, timeout=1).text
        except:
            continue
        soup = BeautifulSoup(text, "html.parser")
        links_detected = []
        try:
            print(f'[?] Title: {soup.title.text.strip()}')
        except:
            print(f'[?] Title: null')
        try:
            for link in soup.findAll('a'):
                href = link.get('href')
                if href and href.startswith('http') and href not in links_detected:
                    if query.lower() in href.lower() or fuzz.ratio(link.text, href) >= 60:
                        print(f'--- Relevant link found: {href}')
                        links_detected.append(href)
        except:
            continue
        if not links_detected:
            print('--- No data found')

def help_menu():
    return """
/email-bomber
↪ sends bulk emails.
↪ usage: /email-bomber <server> <your_email> <your_password> <target_email> <subject> <message> <count>

/apk-file
↪ builds an apk (not implemented in this version).

/search-links
↪ performs a google search and finds relevant links.
↪ usage: /search-links <query>

/exit
↪ exits the program.
"""

def main():
    clearDirec()
    display_kanki()
    print(stdOutput("warning") + "Type '/help' to see available commands." + colors.reset)

    while True:
        try:
            command = input(f"{colors.blue}kiya{colors.red}@{colors.green}NET{colors.reset}: ").strip()
            if command.lower() == '/help':
                print(help_menu())
            elif command.lower().startswith('/email-bomber'):
                args = command.split()[1:]
                if len(args) < 7:
                    print(stdOutput("error") + "Usage: /email-bomber <server> <your_email> <your_password> <target_email> <subject> <message> <count>")
                    continue
                server, email, pwd, target, subject, message, count = args[:7]
                try:
                    count = int(count)
                    email_bomber(server, email, pwd, target, subject, message, count)
                except ValueError:
                    print(stdOutput("error") + "Count must be an integer.")
            elif command.lower().startswith('/search-links'):
                parts = command.split(' ', 1)
                if len(parts) == 2:
                    search_links(parts[1])
                else:
                    print(stdOutput("error") + "Usage: /search-links <query>")
            elif command.lower() == '/exit':
                print(stdOutput("info") + "Exiting.")
                break
            else:
                print(stdOutput("error") + "Unknown command.")
        except Exception as e:
            print(stdOutput("error") + f"Error: {e}")

if __name__ == "__main__":
    main()
