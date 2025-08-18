import os
import requests
from bs4 import BeautifulSoup
import re
import socket
import whois
import dns.resolver
import json
import time
from datetime import datetime

class DoxingTool:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_ip_info(self, ip_address):
        try:
            response = self.session.get(f"http://ip-api.com/json/{ip_address}")
            data = response.json()
            if data['status'] == 'success':
                return {
                    'Country': data['country'],
                    'Region': data['regionName'],
                    'City': data['city'],
                    'ZIP': data['zip'],
                    'ISP': data['isp'],
                    'Org': data['org'],
                    'AS': data['as'],
                    'Latitude': data['lat'],
                    'Longitude': data['lon']
                }
        except Exception as e:
            return f"Error: {str(e)}"
    
    def whois_lookup(self, domain):
        try:
            w = whois.whois(domain)
            return dict(w)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def dns_lookup(self, domain, record_type='A'):
        try:
            answers = dns.resolver.resolve(domain, record_type)
            return [str(rdata) for rdata in answers]
        except Exception as e:
            return f"Error: {str(e)}"
    
    def reverse_whois(self, email):
        return "Reverse WHOIS requires paid API access"
    
    def username_search(self, username):
        sites = {
            'GitHub': f'https://github.com/{username}',
            'Twitter': f'https://twitter.com/{username}',
            'Instagram': f'https://instagram.com/{username}',
            'Reddit': f'https://reddit.com/user/{username}',
            'YouTube': f'https://youtube.com/user/{username}'
        }
        
        results = {}
        for site, url in sites.items():
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    results[site] = url
            except:
                pass
        
        return results
    
    def email_search(self, email):
        return "Email search requires paid API access"
    
    def phone_lookup(self, phone_number):
        return "Phone lookup requires paid API access"
    
    def social_media_profiles(self, name):
        return "Social media search requires paid API access"
    
    def save_results(self, data, filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return f"Results saved to {filename}"

def main():
    print("""
    ██████╗  ██████╗ ██╗  ██╗██╗███╗   ██╗ ██████╗ 
    ██╔══██╗██╔═══██╗╚██╗██╔╝██║████╗  ██║██╔════╝ 
    ██║  ██║██║   ██║ ╚███╔╝ ██║██╔██╗ ██║██║  ███╗
    ██║  ██║██║   ██║ ██╔██╗ ██║██║╚██╗██║██║   ██║
    ██████╔╝╚██████╔╝██╔╝ ██╗██║██║ ╚████║╚██████╔╝
    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    

    """)
    
    tool = DoxingTool()
    results = {}
    
    while True:
        print("\nOptions:")
        print("1. IP Lookup")
        print("2. WHOIS Lookup")
        print("3. DNS Lookup")
        print("4. Username Search")
        print("5. Exit")
        
        choice = input("Select an option (1-5): ")
        
        if choice == '1':
            ip = input("Enter IP address: ")
            ip_info = tool.get_ip_info(ip)
            print("\nIP Information:")
            for k, v in ip_info.items():
                print(f"{k}: {v}")
            results['IP Lookup'] = ip_info
            
        elif choice == '2':
            domain = input("Enter domain: ")
            whois_data = tool.whois_lookup(domain)
            print("\nWHOIS Information:")
            for k, v in whois_data.items():
                print(f"{k}: {v}")
            results['WHOIS Lookup'] = whois_data
            
        elif choice == '3':
            domain = input("Enter domain: ")
            record_type = input("Record type (A, MX, NS, etc.): ")
            dns_data = tool.dns_lookup(domain, record_type)
            print("\nDNS Information:")
            print(dns_data)
            results['DNS Lookup'] = dns_data
            
        elif choice == '4':
            username = input("Enter username: ")
            profiles = tool.username_search(username)
            print("\nFound profiles:")
            for site, url in profiles.items():
                print(f"{site}: {url}")
            results['Username Search'] = profiles
            
        elif choice == '5':
            if results:
                save = input("Save results? (y/n): ").lower()
                if save == 'y':
                    filename = input("Enter filename (without extension): ")
                    tool.save_results(results, filename)
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()