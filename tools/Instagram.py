import requests
import json
import re
from datetime import datetime
import argparse
import os
from bs4 import BeautifulSoup
import sys
from time import sleep

class InstagramOSINT:
    def __init__(self, username=None, email=None, phone=None):
        self.username = username
        self.email = email
        self.phone = phone
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-IG-App-ID': '936619743392459',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'DNT': '1'
        }
        self.session.headers.update(self.headers)
        
    def _make_request(self, url, method='GET', data=None, retries=3):
        for attempt in range(retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=10)
                else:
                    response = self.session.post(url, data=data, timeout=10)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    sleep_time = (attempt + 1) * 5
                    print(f"Rate limited. Waiting {sleep_time} seconds before retry...")
                    sleep(sleep_time)
                    continue
                else:
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                sleep(5)
                continue
        return None

    def get_user_info(self):
        if not self.username:
            return {"error": "Username not provided"}
            
        url = f"https://www.instagram.com/{self.username}/?__a=1"
        response = self._make_request(url)
        
        if response:
            try:
                data = response.json()
                user = data.get('graphql', {}).get('user', {})
                
                return {
                    'username': user.get('username'),
                    'full_name': user.get('full_name'),
                    'biography': user.get('biography'),
                    'external_url': user.get('external_url'),
                    'is_private': user.get('is_private'),
                    'is_verified': user.get('is_verified'),
                    'profile_pic_url': user.get('profile_pic_url_hd'),
                    'followers': user.get('edge_followed_by', {}).get('count'),
                    'following': user.get('edge_follow', {}).get('count'),
                    'posts': user.get('edge_owner_to_timeline_media', {}).get('count'),
                    'joined_recently': user.get('is_joined_recently'),
                    'business_account': user.get('is_business_account'),
                    'business_category': user.get('business_category_name'),
                    'highlight_reel_count': user.get('highlight_reel_count', 0),
                    'has_guides': user.get('has_guides', False),
                    'has_ar_effects': user.get('has_ar_effects', False),
                    'has_clips': user.get('has_clips', False),
                    'has_channel': user.get('has_channel', False)
                }
            except json.JSONDecodeError:
                return {"error": "Failed to parse user information - profile may be private"}
        return {"error": "Failed to fetch user information"}

    def check_username_availability(self):
        if not self.username:
            return {"error": "Username not provided"}
            
        url = "https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/"
        payload = {
            "email": "temp@example.com",
            "username": self.username,
            "first_name": "test",
            "opt_into_one_tap": False
        }
        
        response = self._make_request(url, method='POST', data=payload)
        if response:
            try:
                data = response.json()
                if data.get("username_suggestions"):
                    return {"available": False, "suggestions": data.get("username_suggestions")}
                return {"available": True}
            except json.JSONDecodeError:
                return {"error": "Failed to parse response"}
        return {"error": "Failed to check username availability"}

    def find_related_accounts(self):
        if not self.username:
            return {"error": "Username not provided"}
            
        url = f"https://www.instagram.com/web/search/topsearch/?context=blended&query={self.username}"
        response = self._make_request(url)
        
        if response:
            try:
                data = response.json()
                return {
                    'related_accounts': [{
                        'username': user['user']['username'],
                        'full_name': user['user']['full_name'],
                        'verified': user['user']['is_verified'],
                        'profile_pic': user['user']['profile_pic_url'],
                        'follower_count': user['user']['byline'],
                        'mutual_followers': user['user']['mutual_followers_count'] if 'mutual_followers_count' in user['user'] else None
                    } for user in data.get('users', [])[:10]]  
                }
            except (json.JSONDecodeError, KeyError):
                return {"error": "Failed to parse related accounts data"}
        return {"error": "Failed to fetch related accounts"}

    def search_by_email(self):
        if not self.email:
            return {"error": "Email not provided"}
            
        url = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/"
        payload = {"email_or_username": self.email}
        response = self._make_request(url, method='POST', data=payload)
        
        if response:
            try:
                data = response.json()
                if data.get("title") == "Account Found":
                    return {
                        "found": True, 
                        "message": "Account exists with this email",
                        "user_info": {
                            "username": data.get("username", "hidden"),
                            "profile_pic": data.get("profile_pic_url", None)
                        }
                    }
                return {"found": False, "message": "No account found with this email"}
            except json.JSONDecodeError:
                return {"error": "Failed to parse email search response"}
        return {"error": "Failed to search by email"}

    def search_by_phone(self):
        if not self.phone:
            return {"error": "Phone not provided"}
            
        url = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/"
        payload = {"email_or_username": self.phone}
        response = self._make_request(url, method='POST', data=payload)
        
        if response:
            try:
                data = response.json()
                if data.get("title") == "Account Found":
                    return {
                        "found": True, 
                        "message": "Account exists with this phone",
                        "user_info": {
                            "username": data.get("username", "hidden"),
                            "profile_pic": data.get("profile_pic_url", None)
                        }
                    }
                return {"found": False, "message": "No account found with this phone"}
            except json.JSONDecodeError:
                return {"error": "Failed to parse phone search response"}
        return {"error": "Failed to search by phone"}

    def extract_metadata_from_url(self, post_url):
        if not post_url.startswith(('http://', 'https://')):
            post_url = f'https://www.instagram.com/p/{post_url}/'
            
        response = self._make_request(post_url)
        if response:
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                script_tag = soup.find('script', text=re.compile('window\._sharedData'))
                if script_tag:
                    json_data = json.loads(script_tag.string.split(' = ')[1].rstrip(';'))
                    post_data = json_data.get('entry_data', {}).get('PostPage', [{}])[0].get('graphql', {}).get('shortcode_media', {})
                    
                    caption = post_data.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', '')
                    hashtags = re.findall(r'#(\w+)', caption)
                    mentions = re.findall(r'@(\w+)', caption)
                    
                    return {
                        'post_id': post_data.get('id'),
                        'shortcode': post_data.get('shortcode'),
                        'caption': caption,
                        'hashtags': hashtags,
                        'mentions': mentions,
                        'likes': post_data.get('edge_media_preview_like', {}).get('count'),
                        'comments': post_data.get('edge_media_to_comment', {}).get('count'),
                        'timestamp': datetime.fromtimestamp(post_data.get('taken_at_timestamp')).isoformat(),
                        'location': post_data.get('location'),
                        'owner': {
                            'username': post_data.get('owner', {}).get('username'),
                            'profile_pic': post_data.get('owner', {}).get('profile_pic_url'),
                            'id': post_data.get('owner', {}).get('id')
                        },
                        'is_video': post_data.get('is_video'),
                        'video_views': post_data.get('video_view_count'),
                        'dimensions': post_data.get('dimensions'),
                        'display_url': post_data.get('display_url'),
                        'accessibility_caption': post_data.get('accessibility_caption'),
                        'tags': post_data.get('tags', []),
                        'sponsor_tags': [user['sponsor'] for user in post_data.get('edge_media_to_sponsor_user', {}).get('edges', [])]
                    }
                return {"error": "Failed to extract post metadata - script tag not found"}
            except (json.JSONDecodeError, AttributeError) as e:
                return {"error": f"Failed to parse post metadata: {str(e)}"}
        return {"error": "Failed to fetch post data"}

    def save_to_file(self, data, filename="instagram_osint_results.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return {"success": True, "message": f"Results saved to {filename}"}
        except (IOError, TypeError) as e:
            return {"error": f"Failed to save results: {str(e)}"}

def print_banner():
    banner = """
██████╗ ███████╗██████╗ ███████╗ ██████╗ █████╗ ███╗   ██╗███████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗████╗  ██║██╔════╝
██║  ██║█████╗  ██████╔╝███████╗██║     ███████║██╔██╗ ██║█████╗  
██║  ██║██╔══╝  ██╔══██╗╚════██║██║     ██╔══██║██║╚██╗██║██╔══╝  
██████╔╝███████╗██║  ██║███████║╚██████╗██║  ██║██║ ╚████║███████╗
╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝
                                                                  
Instagram OSINT Tool v2.0 | Developed by [NoneR00tk1t]
"""
    print(banner)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Instagram OSINT Tool", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-u", "--username", help="Instagram username to investigate")
    parser.add_argument("-e", "--email", help="Email to search for Instagram account")
    parser.add_argument("-p", "--phone", help="Phone number to search for Instagram account")
    parser.add_argument("-purl", "--post_url", help="Instagram post URL or shortcode to extract metadata")
    parser.add_argument("-o", "--output", help="Output file name (default: instagram_osint_results.json)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if not any([args.username, args.email, args.phone, args.post_url]):
        parser.print_help()
        print("\nExamples:")
        print("  python instagram_osint.py -u target_username")
        print("  python instagram_osint.py -e example@email.com -o results.json")
        print("  python instagram_osint.py -purl BsOGulcndjW")
        return
    
    osint = InstagramOSINT(username=args.username, email=args.email, phone=args.phone)
    results = {}
    
    if args.username:
        if args.verbose:
            print(f"[*] Gathering information for username: {args.username}")
        results['user_info'] = osint.get_user_info()
        results['username_availability'] = osint.check_username_availability()
        results['related_accounts'] = osint.find_related_accounts()
    
    if args.email:
        if args.verbose:
            print(f"[*] Searching for account with email: {args.email}")
        results['email_search'] = osint.search_by_email()
    
    if args.phone:
        if args.verbose:
            print(f"[*] Searching for account with phone: {args.phone}")
        results['phone_search'] = osint.search_by_phone()
    
    if args.post_url:
        if args.verbose:
            print(f"[*] Extracting metadata from post: {args.post_url}")
        results['post_metadata'] = osint.extract_metadata_from_url(args.post_url)
    
    print("\nResults:")
    print(json.dumps(results, indent=4, ensure_ascii=False))
    
    output_file = args.output if args.output else "instagram_osint_results.json"
    save_result = osint.save_to_file(results, output_file)
    
    if save_result.get("success"):
        print(f"\n[+] Results saved to {output_file}")
    else:
        print(f"\n[-] Error saving results: {save_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()