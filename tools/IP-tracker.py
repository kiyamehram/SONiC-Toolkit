import requests
import json
from datetime import datetime
import argparse
import sys

BANNER = """
\033[1;31m
### ######     #######                                           
 #  #     #       #    #####    ##    ####  #    # ###### #####  
 #  #     #       #    #    #  #  #  #    # #   #  #      #    # 
 #  ######        #    #    # #    # #      ####   #####  #    # 
 #  #             #    #####  ###### #      #  #   #      #####  
 #  #             #    #   #  #    # #    # #   #  #      #   #  
### #             #    #    # #    #  ####  #    # ###### #    # 
\033[1;34m
"""

def display_banner():
    print(BANNER)
    print(f"\033[1;36m[*] Script started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    print("\033[1;33m[*] GitHub: https://github.com/kiyamehram \033[0m")
    print("\033[1;33m[*] Author: NoneR00tk1t \033[0m\n")

def get_ip_info(ip=None):
    try:
        if not ip:
            print("\033[1;32m[*] Getting your public IP address...\033[0m")
            ip = requests.get('https://api.ipify.org', timeout=5).text
            print(f"\033[1;32m[*] Tracking YOUR IP: {ip}\033[0m")
        else:
            print(f"\033[1;32m[*] Tracking TARGET IP: {ip}\033[0m")
        
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=10)
        data = res.json()
        
        if data['status'] == 'fail':
            print("\033[1;31m[!] IP Tracking Failed!\033[0m")
            print(f"\033[1;31m[!] Reason: {data.get('message', 'Unknown error')}\033[0m")
            return

        print("\n\033[1;35m[+] Geolocation Information:\033[0m")
        print(f"  \033[1;34mCountry:\033[0m {data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})")
        print(f"  \033[1;34mRegion:\033[0m {data.get('regionName', 'N/A')} ({data.get('region', 'N/A')})")
        print(f"  \033[1;34mCity:\033[0m {data.get('city', 'N/A')}")
        print(f"  \033[1;34mZIP Code:\033[0m {data.get('zip', 'N/A')}")
        print(f"  \033[1;34mTimezone:\033[0m {data.get('timezone', 'N/A')}")
        print(f"  \033[1;34mISP:\033[0m {data.get('isp', 'N/A')}")
        print(f"  \033[1;34mOrganization:\033[0m {data.get('org', 'N/A')}")
        print(f"  \033[1;34mAS Number/Name:\033[0m {data.get('as', 'N/A')}")
        print(f"  \033[1;34mCoordinates:\033[0m {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
        print(f"  \033[1;34mGoogle Maps:\033[0m https://maps.google.com/?q={data.get('lat', '')},{data.get('lon', '')}")
        
        if data.get('mobile', False):
            print("  \033[1;34mMobile:\033[0m Yes")
        if data.get('proxy', False):
            print("  \033[1;34mProxy/VPN:\033[0m Yes")
        if data.get('hosting', False):
            print("  \033[1;34mHosting/Datacenter:\033[0m Yes")
        
        print(f"\n\033[1;35m[+] Reverse DNS:\033[0m {data.get('reverse', 'N/A')}")
        
        # Log the results
        log_entry = {
            'timestamp': str(datetime.now()),
            'ip': ip,
            'country': data.get('country'),
            'city': data.get('city'),
            'isp': data.get('isp'),
            'coordinates': f"{data.get('lat')},{data.get('lon')}",
            'asn': data.get('as')
        }
        
        try:
            with open("/var/log/ip_tracker.log", "a") as log:
                log.write(json.dumps(log_entry) + "\n")
            print("\033[1;32m[*] Information logged to /var/log/ip_tracker.log\033[0m")
        except Exception as e:
            print(f"\033[1;33m[!] Warning: Could not write to log file: {str(e)}\033[0m")
            
    except requests.exceptions.RequestException as e:
        print(f"\033[1;31m[!] Network Error: {str(e)}\033[0m")
    except Exception as e:
        print(f"\033[1;31m[!] Unexpected Error: {str(e)}\033[0m")

if __name__ == "__main__":
    display_banner()
    
    parser = argparse.ArgumentParser(description="Advanced IP Tracker for Kali Linux")
    parser.add_argument("-t", "--target", help="Target IP Address")
    parser.add_argument("-v", "--version", action="version", version="IP Tracker 2.0")
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n\033[1;33m[*] Example: ./ip_tracker.py -t 8.8.8.8\033[0m")
        print("\033[1;33m[*] Running without arguments will track your own IP\033[0m\n")
        if input("\033[1;36mDo you want to track your own IP? (y/n): \033[0m").lower() == 'y':
            get_ip_info()
    else:
        args = parser.parse_args()
        get_ip_info(args.target)