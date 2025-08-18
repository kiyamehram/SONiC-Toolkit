import requests
import re
import phonenumbers
from phonenumbers import carrier, timezone, geocoder
import argparse
import json
from datetime import datetime
import sys

class WhatsAppOSINT:
    def __init__(self, phone_number=None, username=None):
        self.phone_number = phone_number
        self.username = username
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.banner = """
        ██╗    ██╗██╗  ██╗ █████╗ ███████╗██████╗ ████████╗ ██████╗ 
        ██║    ██║██║  ██║██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗
        ██║ █╗ ██║███████║███████║███████╗██████╔╝   ██║   ██║   ██║
        ██║███╗██║██╔══██║██╔══██║╚════██║██╔═══╝    ██║   ██║   ██║
        ╚███╔███╔╝██║  ██║██║  ██║███████║██║        ██║   ╚██████╔╝
         ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝    ╚═════╝ 
        """

    def show_banner(self):
        print(self.banner.format(
            phone=self.phone_number or "Not provided", 
            username=self.username or "Not provided"
        ))

    def validate_phone_number(self):
        try:
            parsed_num = phonenumbers.parse(self.phone_number, None)
            if not phonenumbers.is_valid_number(parsed_num):
                return {"valid": False, "error": "Invalid phone number"}
            
            return {
                "valid": True,
                "international": phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                "national": phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.NATIONAL),
                "e164": phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.E164),
                "carrier": carrier.name_for_number(parsed_num, "en"),
                "timezone": timezone.time_zones_for_number(parsed_num),
                "region": geocoder.description_for_number(parsed_num, "en"),
                "country_code": parsed_num.country_code
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def check_whatsapp_status(self):
        if not self.phone_number:
            return {"error": "Phone number not provided"}
            
        try:
            url = f"https://web.whatsapp.com/send?phone={self.phone_number}"
            response = self.session.get(url, headers=self.headers, allow_redirects=True)
            
            if response.status_code == 200:
                if "window.location.href" in response.text:
                    return {"has_whatsapp": False, "message": "No WhatsApp account found"}
                else:
                    return {"has_whatsapp": True, "message": "WhatsApp account exists"}
            return {"error": "Failed to check WhatsApp status", "status_code": response.status_code}
        except Exception as e:
            return {"error": str(e)}

    def get_profile_info(self):
        if not self.phone_number:
            return {"error": "Phone number not provided"}
            
        try:
            profile_pic_url = f"https://web.whatsapp.com/pp?e=https%3A%2F%2Fweb.whatsapp.com%2Fprofile%3Fid%3D{self.phone_number}&t=1&u={self.phone_number}"
            
            return {
                "profile_picture": profile_pic_url,
                "warning": "Direct profile access may require authentication",
                "suggestions": [
                    "Use WhatsApp web to manually check the profile",
                    "Consider using official WhatsApp Business API",
                    "Check social media for linked accounts"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    def find_username_connections(self):
        if not self.username:
            return {"error": "Username not provided"}
            
        try:
            social_media = {
                "instagram": f"https://www.instagram.com/{self.username}",
                "facebook": f"https://www.facebook.com/{self.username}",
                "twitter": f"https://twitter.com/{self.username}",
                "linkedin": f"https://www.linkedin.com/in/{self.username}",
                "tiktok": f"https://www.tiktok.com/@{self.username}",
                "github": f"https://github.com/{self.username}",
                "youtube": f"https://youtube.com/{self.username}"
            }
            
            results = {}
            for platform, url in social_media.items():
                try:
                    response = self.session.head(url, headers=self.headers, timeout=5)
                    results[platform] = {
                        "url": url,
                        "exists": response.status_code == 200,
                        "status": response.status_code
                    }
                except:
                    results[platform] = {
                        "url": url,
                        "exists": False,
                        "error": "Connection failed"
                    }
            
            return results
        except Exception as e:
            return {"error": str(e)}

    def check_online_status(self):
        if not self.phone_number:
            return {"error": "Phone number not provided"}
            
        return {
            "warning": "Direct online status check requires WhatsApp client integration",
            "suggestions": [
                "Use WhatsApp web to manually check online status",
                "Last seen information is only available for contacts",
                "Consider using WhatsApp Web's developer tools to monitor presence"
            ]
        }

    def analyze_chat_export(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chat_data = f.read()
                
            message_count = len(re.findall(r'\d+/\d+/\d+, \d+:\d+ - .+?:', chat_data))
            participants = list(set(re.findall(r'\d+/\d+/\d+, \d+:\d+ - (.+?):', chat_data)))
            media_count = len(re.findall(r'<Media omitted>', chat_data))
            date_pattern = r'\d+/\d+/\d+'
            dates = re.findall(date_pattern, chat_data)
            
            if dates:
                first_date = min(dates)
                last_date = max(dates)
            
            return {
                "message_count": message_count,
                "participants": participants,
                "media_count": media_count,
                "time_period": {
                    "first_message": first_date,
                    "last_message": last_date
                },
                "analysis": {
                    "most_active_hour": self._analyze_activity_by_hour(chat_data),
                    "word_frequency": self._analyze_word_frequency(chat_data),
                    "most_active_participant": self._analyze_participant_activity(chat_data)
                }
            }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_activity_by_hour(self, chat_data):
        hour_pattern = r'\d+/\d+/\d+, (\d+):\d+'
        hours = re.findall(hour_pattern, chat_data)
        hour_counts = {str(h): hours.count(h) for h in range(24)}
        return dict(sorted(hour_counts.items(), key=lambda item: item[1], reverse=True)[:5])

    def _analyze_word_frequency(self, chat_data, top_n=10):
        messages = re.findall(r': (.+)', chat_data)
        words = ' '.join(messages).split()
        word_counts = {}
        
        for word in words:
            word_lower = word.lower()
            if len(word_lower) > 3 and word_lower.isalpha():
                word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
                
        return dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True)[:top_n])

    def _analyze_participant_activity(self, chat_data):
        participants = re.findall(r'\d+/\d+/\d+, \d+:\d+ - (.+?):', chat_data)
        participant_counts = {p: participants.count(p) for p in set(participants)}
        return dict(sorted(participant_counts.items(), key=lambda item: item[1], reverse=True))

    def save_to_file(self, data, filename="whatsapp_osint_results.json"):
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return {"success": True, "message": f"Results saved to {filename}"}
        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="WhatsApp OSINT Tool")
    parser.add_argument("-p", "--phone", help="Phone number to investigate (international format)")
    parser.add_argument("-u", "--username", help="Username to search for connections")
    parser.add_argument("-c", "--chat", help="Path to exported WhatsApp chat file")
    parser.add_argument("-o", "--output", help="Output file name (default: whatsapp_osint_results.json)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    if not any([args.phone, args.username, args.chat]):
        parser.print_help()
        return
    
    osint = WhatsAppOSINT(phone_number=args.phone, username=args.username)
    
    if args.verbose:
        osint.show_banner()
    
    results = {}
    
    if args.phone:
        if args.verbose:
            print(f"[*] Analyzing phone number: {args.phone}")
        
        results["phone_validation"] = osint.validate_phone_number()
        results["whatsapp_status"] = osint.check_whatsapp_status()
        results["profile_info"] = osint.get_profile_info()
        results["online_status"] = osint.check_online_status()
    
    if args.username:
        if args.verbose:
            print(f"[*] Searching for username: {args.username}")
        
        results["username_connections"] = osint.find_username_connections()
    
    if args.chat:
        if args.verbose:
            print(f"[*] Analyzing chat file: {args.chat}")
        
        results["chat_analysis"] = osint.analyze_chat_export(args.chat)
    
    print(json.dumps(results, indent=4))
    
    if args.output:
        save_result = osint.save_to_file(results, args.output)
        if args.verbose and save_result.get("success"):
            print(f"[+] Results saved to {args.output}")
    else:
        save_result = osint.save_to_file(results)
        if args.verbose and save_result.get("success"):
            print("[+] Results saved to whatsapp_osint_results.json")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"[!] An error occurred: {str(e)}")
        sys.exit(1)