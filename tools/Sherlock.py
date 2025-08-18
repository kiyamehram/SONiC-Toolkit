import requests
import json
import time
import concurrent.futures
from bs4 import BeautifulSoup
import argparse
import os
import re
from datetime import datetime
from urllib.parse import urlparse
import sqlite3
import pandas as pd
from fake_useragent import UserAgent
from torrequest import TorRequest
import dns.resolver
import socket
import sys
from colorama import Fore, Style, init

init(autoreset=True)

class SherlockPro:
    def __init__(self):
        self.ua = UserAgent()
        self.db_conn = sqlite3.connect('sherlock_pro.db')
        self._init_db()
        self.platforms = self._load_platforms()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.ua.random})
        self.tor = TorRequest(password='sherlockpro')
        self._print_banner()
        
    def _print_banner(self):
        banner = f"""
{Fore.RED}
  /^^ ^^                            /^^                 /^^          
/^^    /^^/^^                       /^^                 /^^          
 /^^      /^^        /^^    /^ /^^^ /^^   /^^       /^^^/^^  /^^     
   /^^    /^ /^    /^   /^^  /^^    /^^ /^^  /^^  /^^   /^^ /^^      
      /^^ /^^  /^^/^^^^^ /^^ /^^    /^^/^^    /^^/^^    /^/^^        
/^^    /^^/^   /^^/^         /^^    /^^ /^^  /^^  /^^   /^^ /^^      
  /^^ ^^  /^^  /^^  /^^^^   /^^^   /^^^   /^^       /^^^/^^  /^^     
                                                                     
      /^               /^^                                           
     /^ ^^             /^^ /^                                        
    /^  /^^     /^^^^  /^^                                           
   /^^   /^^   /^^     /^^/^^                                        
  /^^^^^^ /^^    /^^^  /^^/^^                                        
 /^^       /^^     /^^ /^^/^^                                        
/^^         /^^/^^ /^^/^^^/^^   
{Style.RESET_ALL}
"""
        print(banner)
        
    def _init_db(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT,
                            platform TEXT,
                            url TEXT,
                            status TEXT,
                            found INTEGER,
                            timestamp TEXT,
                            metadata TEXT,
                            response_time REAL
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS platform_data (
                            platform TEXT PRIMARY KEY,
                            check_url TEXT,
                            regex_pattern TEXT,
                            error_msg TEXT,
                            last_updated TEXT,
                            headers TEXT,
                            requires_javascript BOOLEAN,
                            is_rate_limited BOOLEAN
                        )''')
        self.db_conn.commit()

    def _load_platforms(self):
        try:
            with open('custom_platforms.json', 'r', encoding='utf-8') as f:
                platforms = json.load(f)
                print(f"{Fore.GREEN}[+] Loaded {len(platforms)} custom platforms{Style.RESET_ALL}")
                return platforms
        except FileNotFoundError:
            print(f"{Fore.YELLOW}[!] Custom platforms file not found, loading defaults{Style.RESET_ALL}")
            default_platforms = {
                "instagram": {
                    "check_url": "https://www.instagram.com/{}/",
                    "regex_pattern": r'"username":"{}"',
                    "error_msg": "page_not_found",
                    "headers": {
                        "Accept-Language": "en-US,en;q=0.9"
                    },
                    "requires_javascript": False,
                    "is_rate_limited": True
                },
                "twitter": {
                    "check_url": "https://twitter.com/{}",
                    "regex_pattern": r'@{}',
                    "error_msg": "page doesn't exist",
                    "headers": {
                        "Accept": "text/html,application/xhtml+xml"
                    },
                    "requires_javascript": True,
                    "is_rate_limited": True
                },
                "github": {
                    "check_url": "https://github.com/{}",
                    "regex_pattern": r'class="vcard-username" itemprop="additionalName">{}<',
                    "error_msg": "Not Found",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "facebook": {
                    "check_url": "https://www.facebook.com/{}",
                    "regex_pattern": r'content="https://www.facebook.com/{}"',
                    "error_msg": "Sorry, this page isn't available",
                    "headers": {
                        "Accept": "text/html,application/xhtml+xml"
                    },
                    "requires_javascript": True,
                    "is_rate_limited": True
                },
                "linkedin": {
                    "check_url": "https://www.linkedin.com/in/{}",
                    "regex_pattern": r'<title>{} | LinkedIn</title>',
                    "error_msg": "This profile is not available",
                    "headers": {
                        "Accept-Language": "en-US,en;q=0.9"
                    },
                    "requires_javascript": True,
                    "is_rate_limited": True
                },
                "reddit": {
                    "check_url": "https://www.reddit.com/user/{}",
                    "regex_pattern": r'<title>u/{}',
                    "error_msg": "Sorry, nobody on Reddit goes by that name",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "youtube": {
                    "check_url": "https://www.youtube.com/{}",
                    "regex_pattern": r'"channelId":"{}"',
                    "error_msg": "This channel does not exist",
                    "headers": {
                        "Accept-Language": "en-US,en;q=0.9"
                    },
                    "requires_javascript": True,
                    "is_rate_limited": True
                },
                "tiktok": {
                    "check_url": "https://www.tiktok.com/@{}",
                    "regex_pattern": r'<title>@{}',
                    "error_msg": "Couldn't find this account",
                    "headers": {
                        "Accept": "text/html,application/xhtml+xml"
                    },
                    "requires_javascript": True,
                    "is_rate_limited": True
                },
                "pinterest": {
                    "check_url": "https://www.pinterest.com/{}/",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Sorry, we couldn't find that page",
                    "requires_javascript": True,
                    "is_rate_limited": False
                },
                "telegram": {
                    "check_url": "https://t.me/{}",
                    "regex_pattern": r'<meta property="og:title" content="{}"',
                    "error_msg": "<title>Telegram: Contact",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "spotify": {
                    "check_url": "https://open.spotify.com/user/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Couldn't find that user",
                    "requires_javascript": True,
                    "is_rate_limited": False
                },
                "twitch": {
                    "check_url": "https://www.twitch.tv/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Sorry. Unless you've got a time machine, that content is unavailable.",
                    "requires_javascript": True,
                    "is_rate_limited": True
                },
                "vimeo": {
                    "check_url": "https://vimeo.com/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Sorry, we couldn't find that page",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "medium": {
                    "check_url": "https://medium.com/@{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "404",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "quora": {
                    "check_url": "https://www.quora.com/profile/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Oops! The page you were looking for doesn't exist.",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "flickr": {
                    "check_url": "https://www.flickr.com/people/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Oops! You've taken a wrong turn.",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "dribbble": {
                    "check_url": "https://dribbble.com/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Whoops, that page is gone.",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "behance": {
                    "check_url": "https://www.behance.net/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Oops! We can't find that page.",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "deviantart": {
                    "check_url": "https://{}.deviantart.com",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "The page you requested was not found",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "soundcloud": {
                    "check_url": "https://soundcloud.com/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Oops! We couldn't find that page.",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "imgur": {
                    "check_url": "https://imgur.com/user/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "imgur: 404 error",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "slideshare": {
                    "check_url": "https://www.slideshare.net/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Page not found",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "stackoverflow": {
                    "check_url": "https://stackoverflow.com/users/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Page Not Found",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "gitlab": {
                    "check_url": "https://gitlab.com/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "The page could not be found",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "bitbucket": {
                    "check_url": "https://bitbucket.org/{}/",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "This account does not exist",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "hackernews": {
                    "check_url": "https://news.ycombinator.com/user?id={}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "No such user.",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "producthunt": {
                    "check_url": "https://www.producthunt.com/@{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Page not found",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "wikipedia": {
                    "check_url": "https://en.wikipedia.org/wiki/User:{}",
                    "regex_pattern": r'<title>User:{}',
                    "error_msg": "User does not exist",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "keybase": {
                    "check_url": "https://keybase.io/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Not found",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "codepen": {
                    "check_url": "https://codepen.io/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Sorry, we couldn't find what you're looking for.",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "replit": {
                    "check_url": "https://replit.com/@{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Page not found",
                    "requires_javascript": False,
                    "is_rate_limited": False
                },
                "kaggle": {
                    "check_url": "https://www.kaggle.com/{}",
                    "regex_pattern": r'<title>{}',
                    "error_msg": "Page not found",
                    "requires_javascript": False,
                    "is_rate_limited": False
                }
            }
            return default_platforms

    def check_username(self, username, platform, use_tor=False, retry=0):
        try:
            if retry > 2:
                return {
                    'status': 'error',
                    'message': 'Max retries exceeded',
                    'platform': platform,
                    'username': username
                }

            platform_data = self.platforms.get(platform, {})
            if not platform_data:
                return {'status': 'error', 'message': 'Platform not configured'}
            
            url = platform_data['check_url'].format(username)
            
            # Set custom headers if specified
            headers = {'User-Agent': self.ua.random}
            if platform_data.get('headers'):
                headers.update(platform_data['headers'])
            
            result = {
                'username': username,
                'platform': platform,
                'url': url,
                'http_status': None,
                'found': False,
                'metadata': {},
                'response_time': None
            }
            
            start_time = time.time()
            
            try:
                if use_tor:
                    resp = self.tor.get(url, headers=headers, timeout=15)
                else:
                    resp = self.session.get(url, headers=headers, timeout=15)
                
                result['response_time'] = time.time() - start_time
                result['http_status'] = resp.status_code
                
                if resp.status_code == 404:
                    result['status'] = 'not_found'
                elif resp.status_code == 200:
                    if re.search(platform_data['regex_pattern'].format(re.escape(username)), resp.text, re.IGNORECASE):
                        result['found'] = True
                        result['status'] = 'found'
                    elif platform_data.get('error_msg') and platform_data['error_msg'].lower() in resp.text.lower():
                        result['status'] = 'not_found'
                    else:
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        if self._advanced_checks(soup, username, platform):
                            result['found'] = True
                            result['status'] = 'found'
                        else:
                            result['status'] = 'unknown'
                            
                    result['metadata'] = self._extract_metadata(resp.text, platform)
                elif resp.status_code == 429:
                    if platform_data.get('is_rate_limited', False):
                        wait_time = (retry + 1) * 5
                        print(f"{Fore.YELLOW}[!] Rate limited on {platform}. Waiting {wait_time} seconds...{Style.RESET_ALL}")
                        time.sleep(wait_time)
                        return self.check_username(username, platform, use_tor, retry + 1)
                    else:
                        result['status'] = 'error'
                        result['message'] = f"HTTP {resp.status_code} (Rate Limited)"
                else:
                    result['status'] = 'error'
                    result['message'] = f"HTTP {resp.status_code}"
                
                self._save_result(result)
                return result
                
            except requests.exceptions.Timeout:
                result['status'] = 'error'
                result['message'] = 'Request timeout'
                return result
            except requests.exceptions.SSLError:
                result['status'] = 'error'
                result['message'] = 'SSL Error'
                return result
            except requests.exceptions.ConnectionError:
                result['status'] = 'error'
                result['message'] = 'Connection error'
                return result
            except requests.exceptions.TooManyRedirects:
                result['status'] = 'error'
                result['message'] = 'Too many redirects'
                return result
            except Exception as e:
                result['status'] = 'error'
                result['message'] = str(e)
                return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'platform': platform,
                'username': username
            }

    def _advanced_checks(self, soup, username, platform):
        platform_checks = {
            'instagram': lambda: soup.find('meta', property='og:title') and 
                               username.lower() in soup.find('meta', property='og:title').get('content', '').lower(),
            'twitter': lambda: soup.find('div', class_='profile-card') is not None,
            'github': lambda: 'avatar' in str(soup) and 'user-profile' in str(soup),
            'facebook': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'linkedin': lambda: f"{username} | LinkedIn" in soup.find('title').text if soup.find('title') else False,
            'reddit': lambda: f"u/{username}" in soup.find('title').text if soup.find('title') else False,
            'youtube': lambda: f"@{username}" in soup.find('title').text if soup.find('title') else False,
            'tiktok': lambda: f"@{username}" in soup.find('title').text if soup.find('title') else False,
            'pinterest': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'telegram': lambda: username.lower() in soup.find('meta', property='og:title').get('content', '').lower() if soup.find('meta', property='og:title') else False,
            'spotify': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'twitch': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'vimeo': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'medium': lambda: f"@{username}" in soup.find('title').text if soup.find('title') else False,
            'quora': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'flickr': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'dribbble': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'behance': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'deviantart': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'soundcloud': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'imgur': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'slideshare': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'stackoverflow': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'gitlab': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'bitbucket': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'hackernews': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'producthunt': lambda: f"@{username}" in soup.find('title').text if soup.find('title') else False,
            'wikipedia': lambda: f"User:{username}" in soup.find('title').text if soup.find('title') else False,
            'keybase': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'codepen': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'replit': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False,
            'kaggle': lambda: username.lower() in soup.find('title').text.lower() if soup.find('title') else False
        }
        
        check_func = platform_checks.get(platform, lambda: False)
        return check_func()

    def _extract_metadata(self, html, platform):
        metadata = {}
        soup = BeautifulSoup(html, 'html.parser')
        
        if platform == 'instagram':
            meta_tag = soup.find('meta', property='og:description')
            if meta_tag:
                metadata['description'] = meta_tag.get('content', '')
            metadata['image'] = soup.find('meta', property='og:image').get('content', '') if soup.find('meta', property='og:image') else ''
        
        elif platform == 'twitter':
            card = soup.find('div', class_='profile-card')
            if card:
                metadata['name'] = card.find('h1').text if card.find('h1') else ''
                metadata['bio'] = card.find('p', class_='bio').text if card.find('p', class_='bio') else ''
        
        elif platform == 'github':
            profile = soup.find('div', class_='h-card')
            if profile:
                metadata['name'] = profile.find('span', class_='p-name').text if profile.find('span', class_='p-name') else ''
                metadata['bio'] = profile.find('div', class_='p-note').text.strip() if profile.find('div', class_='p-note') else ''
                metadata['location'] = profile.find('span', class_='p-label').text if profile.find('span', class_='p-label') else ''
        
        elif platform == 'facebook':
            profile = soup.find('div', id='intro_container_id')
            if profile:
                metadata['name'] = soup.find('title').text if soup.find('title') else ''
        
        elif platform == 'linkedin':
            profile = soup.find('section', class_='top-card-layout')
            if profile:
                metadata['name'] = profile.find('h1').text.strip() if profile.find('h1') else ''
                metadata['headline'] = profile.find('h2').text.strip() if profile.find('h2') else ''
        
        
        return metadata

    def _save_result(self, result):
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO results 
                          (username, platform, url, status, found, timestamp, metadata, response_time)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (result['username'], result['platform'], result['url'],
                       result['status'], int(result.get('found', False)), 
                       datetime.now().isoformat(), json.dumps(result.get('metadata', {})),
                       result.get('response_time', 0)))
        self.db_conn.commit()

    def multi_check(self, usernames, platforms=None, max_threads=20, use_tor=False, verbose=False):
        if not platforms:
            platforms = self.platforms.keys()
        
        results = []
        total = len(usernames) * len(platforms)
        completed = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for username in usernames:
                for platform in platforms:
                    futures.append(executor.submit(
                        self.check_username, username, platform, use_tor
                    ))
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if verbose:
                        status = result.get('status', 'error')
                        if status == 'found':
                            color = Fore.GREEN
                            symbol = '✓'
                        elif status == 'not_found':
                            color = Fore.RED
                            symbol = '✗'
                        else:
                            color = Fore.YELLOW
                            symbol = '?'
                        
                        print(f"{color}[{symbol}] {result['platform']:15} {result['username']:20} {status:10} {result.get('message', '')}{Style.RESET_ALL}")
                    
                    sys.stdout.write(f"\r[+] Progress: {completed}/{total} ({completed/total*100:.1f}%)")
                    sys.stdout.flush()
                
                except Exception as e:
                    print(f"\n{Fore.RED}[!] Error processing result: {e}{Style.RESET_ALL}")
        
        print()  
        return results

    def dns_lookup(self, username, domains):
        found = []
        for domain in domains:
            try:
                subdomain = f"{username}.{domain}"
                answers = dns.resolver.resolve(subdomain, 'A')
                if answers:
                    found.append({
                        'domain': domain,
                        'subdomain': subdomain,
                        'ip': [str(r) for r in answers]
                    })
            except dns.resolver.NXDOMAIN:
                continue
            except dns.resolver.NoAnswer:
                continue
            except dns.resolver.Timeout:
                print(f"{Fore.YELLOW}[!] DNS lookup timeout for {subdomain}{Style.RESET_ALL}")
                continue
            except Exception as e:
                print(f"{Fore.YELLOW}[!] DNS lookup error for {subdomain}: {e}{Style.RESET_ALL}")
                continue
        return found

    def generate_report(self, username, output_format='html'):
        cursor = self.db_conn.cursor()
        cursor.execute('''SELECT platform, url, status, found, timestamp, metadata, response_time
                          FROM results WHERE username = ? ORDER BY found DESC, platform ASC''', (username,))
        rows = cursor.fetchall()
        
        if output_format == 'html':
            report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Sherlock Pro+ Report for {username}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .found {{ color: green; }}
        .not-found {{ color: red; }}
        .error {{ color: orange; }}
        .metadata {{ max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    </style>
</head>
<body>
    <h1>Sherlock Pro+ Report for {username}</h1>
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <table>
        <tr>
            <th>Platform</th>
            <th>Status</th>
            <th>URL</th>
            <th>Response Time</th>
            <th>Metadata</th>
        </tr>
"""
            
            for platform, url, status, found, timestamp, metadata_json, response_time in rows:
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                except:
                    metadata = {}
                
                status_class = 'found' if found else 'not-found'
                if status == 'error':
                    status_class = 'error'
                
                metadata_str = ', '.join(f"{k}: {v}" for k, v in metadata.items() if v)
                
                report += f"""
        <tr>
            <td>{platform}</td>
            <td class="{status_class}">{status}</td>
            <td><a href="{url}" target="_blank">{url}</a></td>
            <td>{response_time:.2f}s</td>
            <td class="metadata" title="{metadata_str}">{metadata_str}</td>
        </tr>
"""
            
            report += """
    </table>
    <footer style="margin-top: 30px; font-size: 0.8em; color: #666;">
        Generated by Sherlock Pro+ - Advanced Username Tracking Tool
    </footer>
</body>
</html>
"""
            return report
        
        elif output_format == 'json':
            results = []
            for platform, url, status, found, timestamp, metadata_json, response_time in rows:
                results.append({
                    'platform': platform,
                    'url': url,
                    'status': status,
                    'found': bool(found),
                    'timestamp': timestamp,
                    'response_time': response_time,
                    'metadata': json.loads(metadata_json) if metadata_json else {}
                })
            return json.dumps(results, indent=2)
        
        elif output_format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['Platform', 'URL', 'Status', 'Found', 'Timestamp', 'Response Time', 'Metadata'])
            
            for platform, url, status, found, timestamp, metadata_json, response_time in rows:
                writer.writerow([
                    platform,
                    url,
                    status,
                    'Yes' if found else 'No',
                    timestamp,
                    f"{response_time:.2f}s",
                    json.dumps(json.loads(metadata_json) if metadata_json else {})
                ])
            
            return output.getvalue()
        
        else:
            return "Unsupported output format"

    def update_platforms(self):
        try:
            print(f"{Fore.CYAN}[*] Checking for platform updates...{Style.RESET_ALL}")
            

            updated_platforms = self._load_platforms()
            changes = 0
            
            for platform, data in updated_platforms.items():
                if platform not in self.platforms:
                    print(f"{Fore.GREEN}[+] Added new platform: {platform}{Style.RESET_ALL}")
                    changes += 1
                else:
                    if json.dumps(self.platforms[platform], sort_keys=True) != json.dumps(data, sort_keys=True):
                        print(f"{Fore.YELLOW}[~] Updated platform: {platform}{Style.RESET_ALL}")
                        changes += 1
            
            if changes > 0:
                self.platforms = updated_platforms
                print(f"{Fore.GREEN}[+] Updated {changes} platforms{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}[*] No platform updates found{Style.RESET_ALL}")
            
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to update platforms: {e}{Style.RESET_ALL}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Sherlock Pro+: Advanced username tracking tool')
    parser.add_argument('usernames', nargs='+', help='Usernames to search')
    parser.add_argument('--platforms', nargs='+', help='Specific platforms to check')
    parser.add_argument('--output', help='Output file (html, json, csv)')
    parser.add_argument('--tor', action='store_true', help='Use Tor for anonymity')
    parser.add_argument('--threads', type=int, default=20, help='Maximum threads (default: 20)')
    parser.add_argument('--update', action='store_true', help='Update platform data before searching')
    parser.add_argument('--dns', nargs='+', help='Check for DNS subdomains with these domains')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output during search')
    args = parser.parse_args()

    sherlock = SherlockPro()
    
    if args.update:
        sherlock.update_platforms()
    
    if args.dns:
        print(f"\n{Fore.CYAN}[*] Performing DNS lookups...{Style.RESET_ALL}")
        for username in args.usernames:
            dns_results = sherlock.dns_lookup(username, args.dns)
            if dns_results:
                print(f"\n{Fore.GREEN}[+] DNS results for {username}:{Style.RESET_ALL}")
                for result in dns_results:
                    print(f"  - {result['subdomain']}: {', '.join(result['ip'])}")
            else:
                print(f"{Fore.RED}[-] No DNS results for {username}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}[*] Searching for {len(args.usernames)} username(s) across {len(sherlock.platforms)} platforms...{Style.RESET_ALL}")
    
    start_time = time.time()
    results = sherlock.multi_check(args.usernames, args.platforms, args.threads, args.tor, args.verbose)
    elapsed = time.time() - start_time
    
    found = sum(1 for r in results if r.get('found'))
    errors = sum(1 for r in results if r.get('status') == 'error')
    
    print(f"\n{Fore.CYAN}[+] Search completed in {elapsed:.2f} seconds{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Found {found} positive results{Style.RESET_ALL}")
    if errors > 0:
        print(f"{Fore.YELLOW}[!] Encountered {errors} errors{Style.RESET_ALL}")
    
    if args.output:
        output_format = 'html'
        if args.output.endswith('.json'):
            output_format = 'json'
        elif args.output.endswith('.csv'):
            output_format = 'csv'
        
        report = sherlock.generate_report(args.usernames[0], output_format)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"{Fore.GREEN}[*] Results saved to {args.output}{Style.RESET_ALL}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Critical error: {e}{Style.RESET_ALL}")
        sys.exit(1)