import requests
import re
import json
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import concurrent.futures
import sqlite3
from datetime import datetime
import argparse
import os
from fake_useragent import UserAgent
import sys

class PhoneIntel:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.ua.random})
        self.db_conn = sqlite3.connect('phone_intel.db')
        self._init_db()
        self.sources = self._load_sources()
        
    def _init_db(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            phone_number TEXT,
                            source TEXT,
                            data_type TEXT,
                            data_value TEXT,
                            timestamp TEXT
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS cache (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            phone_number TEXT UNIQUE,
                            data TEXT,
                            timestamp TEXT
                        )''')
        self.db_conn.commit()

    def _load_sources(self):
        try:
            with open('sources.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "haveibeenpwned": {
                    "url": "https://haveibeenpwned.com/unifiedsearch/{phone}",
                    "method": "GET",
                    "parser": "parse_haveibeenpwned",
                    "headers": {}
                },
                "truecaller": {
                    "url": "https://www.truecaller.com/search/in/{phone}",
                    "method": "GET",
                    "parser": "parse_truecaller",
                    "headers": {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5"
                    }
                },
                "syncme": {
                    "url": "https://sync.me/search/?number={phone}",
                    "method": "GET",
                    "parser": "parse_syncme",
                    "headers": {}
                },
                "numverify": {
                    "url": "http://apilayer.net/api/validate?access_key=YOUR_API_KEY&number={phone}",
                    "method": "GET",
                    "parser": "parse_numverify",
                    "headers": {}
                },
                "openCNAM": {
                    "url": "https://api.opencnam.com/v3/phone/{phone}?format=json",
                    "method": "GET",
                    "parser": "parse_opencnam",
                    "headers": {}
                }
            }

    def normalize_phone(self, phone_number, country='IR'):
        try:
            parsed = phonenumbers.parse(phone_number, country)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            print(f"[-] Error normalizing phone number: {e}")
            return None

    def get_basic_info(self, phone_number):
        try:
            parsed = phonenumbers.parse(phone_number)
            return {
                'carrier': carrier.name_for_number(parsed, 'en'),
                'region': geocoder.description_for_number(parsed, 'en'),
                'timezone': timezone.time_zones_for_number(parsed),
                'valid': phonenumbers.is_valid_number(parsed),
                'possible': phonenumbers.is_possible_number(parsed),
                'national_format': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
                'international_format': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            }
        except Exception as e:
            print(f"[-] Error getting basic info: {e}")
            return {'error': str(e)}

    def _check_cache(self, phone_number):
        cursor = self.db_conn.cursor()
        cursor.execute('''SELECT data FROM cache WHERE phone_number = ?''', (phone_number,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

    def _save_to_cache(self, phone_number, data):
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO cache (phone_number, data, timestamp)
                          VALUES (?, ?, ?)''',
                      (phone_number, json.dumps(data), datetime.now().isoformat()))
        self.db_conn.commit()

    def search_source(self, phone_number, source_name):
        cached = self._check_cache(f"{source_name}_{phone_number}")
        if cached:
            return cached
            
        source = self.sources.get(source_name)
        if not source:
            return {'error': 'Source not found'}
        
        url = source['url'].format(phone=phone_number)
        try:
            headers = {**self.session.headers, **source.get('headers', {})}
            
            if source['method'] == 'GET':
                response = self.session.get(url, headers=headers, timeout=15)
            else:
                response = self.session.post(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return {'error': f"HTTP {response.status_code}"}
            
            if hasattr(self, source['parser']):
                parser = getattr(self, source['parser'])
                results = parser(response.text)
                self._save_results(phone_number, source_name, results)
                self._save_to_cache(f"{source_name}_{phone_number}", results)
                return results
            return {'error': 'Parser not found'}
        except Exception as e:
            print(f"[-] Error searching {source_name}: {e}")
            return {'error': str(e)}

    def parse_haveibeenpwned(self, html):
        results = []
        try:
            data = json.loads(html)
            for breach in data.get('Breaches', []):
                results.append({
                    'type': 'breach',
                    'value': breach['Name'],
                    'date': breach['BreachDate'],
                    'details': breach['Description'],
                    'compromised_data': ', '.join(breach.get('DataClasses', []))
                })
        except Exception as e:
            print(f"[-] Error parsing haveibeenpwned: {e}")
        return results

    def parse_truecaller(self, html):
        results = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Name
        name_tag = soup.find('h1', class_='profile-name')
        if name_tag:
            results.append({'type': 'name', 'value': name_tag.text.strip()})
        
        # Email
        email_tag = soup.find('a', href=lambda x: x and 'mailto:' in x)
        if email_tag:
            results.append({'type': 'email', 'value': email_tag.text.strip()})
        
        # Address
        address_div = soup.find('div', class_='address')
        if address_div:
            results.append({'type': 'address', 'value': address_div.text.strip()})
        
        # Social media
        social_links = soup.find_all('a', class_='social-link')
        for link in social_links:
            if 'facebook' in link['href']:
                results.append({'type': 'facebook', 'value': link['href']})
            elif 'twitter' in link['href']:
                results.append({'type': 'twitter', 'value': link['href']})
        
        return results

    def parse_syncme(self, html):
        results = []
        soup = BeautifulSoup(html, 'html.parser')
        
        profile = soup.find('div', class_='profile-header')
        if profile:
            name = profile.find('h1')
            if name:
                results.append({'type': 'name', 'value': name.text.strip()})
            
            for detail in profile.find_all('div', class_='detail'):
                if 'email' in detail.text.lower():
                    email = detail.find('a')
                    if email:
                        results.append({'type': 'email', 'value': email.text.strip()})
                elif 'address' in detail.text.lower():
                    results.append({'type': 'address', 'value': detail.text.replace('Address:', '').strip()})
        
        info_section = soup.find('div', class_='profile-info')
        if info_section:
            for item in info_section.find_all('div', class_='info-item'):
                key = item.find('span', class_='key')
                value = item.find('span', class_='value')
                if key and value:
                    results.append({
                        'type': key.text.strip().lower(),
                        'value': value.text.strip()
                    })
        
        return results

    def parse_numverify(self, json_data):
        results = []
        try:
            data = json.loads(json_data)
            
            if data.get('valid'):
                results.append({
                    'type': 'carrier',
                    'value': data.get('carrier', '')
                })
                results.append({
                    'type': 'location',
                    'value': f"{data.get('location', '')}, {data.get('country_name', '')}"
                })
                results.append({
                    'type': 'line_type',
                    'value': data.get('line_type', '')
                })
                results.append({
                    'type': 'local_format',
                    'value': data.get('local_format', '')
                })
        except Exception as e:
            print(f"[-] Error parsing numverify: {e}")
        return results

    def parse_opencnam(self, json_data):
        results = []
        try:
            data = json.loads(json_data)
            if data.get('name'):
                results.append({
                    'type': 'name',
                    'value': data['name'],
                    'source': data.get('source', 'unknown')
                })
        except Exception as e:
            print(f"[-] Error parsing openCNAM: {e}")
        return results

    def _save_results(self, phone_number, source, results):
        cursor = self.db_conn.cursor()
        for result in results:
            cursor.execute('''INSERT INTO results 
                              (phone_number, source, data_type, data_value, timestamp)
                              VALUES (?, ?, ?, ?, ?)''',
                          (phone_number, source, result.get('type', 'unknown'), 
                           result.get('value', ''), datetime.now().isoformat()))
        self.db_conn.commit()

    def search_all_sources(self, phone_number, max_threads=10):
        normalized = self.normalize_phone(phone_number)
        if not normalized:
            return {'error': 'Invalid phone number'}
        
        basic_info = self.get_basic_info(normalized)
        results = {'basic_info': basic_info, 'sources': {}}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_source = {
                executor.submit(self.search_source, normalized, source): source
                for source in self.sources
            }
            
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    results['sources'][source] = future.result()
                except Exception as e:
                    results['sources'][source] = {'error': str(e)}
        
        return results

    def generate_report(self, phone_number, format='console'):
        cursor = self.db_conn.cursor()
        cursor.execute('''SELECT source, data_type, data_value 
                          FROM results WHERE phone_number = ?''', (phone_number,))
        rows = cursor.fetchall()
        
        if format == 'console':
            print(f"\n[+] Report for {phone_number}")
            print("="*70)
            for source, data_type, data_value in rows:
                print(f"{source.upper():<20} | {data_type:<15} | {data_value}")
            print("="*70)
        elif format == 'json':
            report = {
                'phone_number': phone_number,
                'results': [{
                    'source': source,
                    'type': data_type,
                    'value': data_value
                } for source, data_type, data_value in rows]
            }
            return json.dumps(report, indent=2, ensure_ascii=False)
        elif format == 'html':
            html = f"""
            <html>
            <head>
                <title>PhoneIntel Report for {phone_number}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                    th {{ background-color: #4CAF50; color: white; }}
                </style>
            </head>
            <body>
                <h1>PhoneIntel Report for {phone_number}</h1>
                <table>
                    <tr>
                        <th>Source</th>
                        <th>Type</th>
                        <th>Value</th>
                    </tr>
            """
            for source, data_type, data_value in rows:
                html += f"""
                    <tr>
                        <td>{source}</td>
                        <td>{data_type}</td>
                        <td>{data_value}</td>
                    </tr>
                """
            html += """
                </table>
                <p>Report generated on {}</p>
            </body>
            </html>
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return html

    def search_darkweb(self, phone_number):

        return {'warning': 'Dark web search requires API keys and paid services'}

def print_banner():
    print("""
  ____  _                      _____       _ _ 
 |  _ \| |__   ___  _ __   ___|_   _| __ (_) |
 | |_) | '_ \ / _ \| '_ \ / _ \ | || '_ \| | |
 |  __/| | | | (_) | | | |  __/ | || | | | | |
 |_|   |_| |_|\___/|_| |_|\___| |_||_| |_|_|_|

 PhoneIntel v1.0 - Advanced Phone Number OSINT Tool
    """)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description='PhoneIntel: Advanced phone number OSINT tool')
    parser.add_argument('phone_numbers', nargs='+', help='Phone numbers to search')
    parser.add_argument('--threads', type=int, default=5, help='Maximum threads (default: 5)')
    parser.add_argument('--output', choices=['console', 'json', 'html'], default='console', 
                       help='Output format (default: console)')
    parser.add_argument('--save', help='Save output to file')
    args = parser.parse_args()

    intel = PhoneIntel()
    
    for phone in args.phone_numbers:
        print(f"\n[*] Searching for {phone}...")
        results = intel.search_all_sources(phone, args.threads)
        
        if args.output == 'json':
            report = intel.generate_report(phone, 'json')
            print(report)
            if args.save:
                with open(args.save, 'w') as f:
                    f.write(report)
        elif args.output == 'html':
            report = intel.generate_report(phone, 'html')
            if args.save:
                with open(args.save, 'w') as f:
                    f.write(report)
                print(f"[+] Report saved to {args.save}")
            else:
                print(report)
        else:
            intel.generate_report(phone)
            if args.save:
                cursor = intel.db_conn.cursor()
                cursor.execute('''SELECT source, data_type, data_value 
                                FROM results WHERE phone_number = ?''', (phone,))
                rows = cursor.fetchall()
                with open(args.save, 'w') as f:
                    for source, data_type, data_value in rows:
                        f.write(f"{source.upper():<20} | {data_type:<15} | {data_value}\n")
                print(f"[+] Report saved to {args.save}")

if __name__ == '__main__':
    main()