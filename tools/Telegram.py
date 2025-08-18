import requests
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.tl.functions.users import GetFullUserRequest
import json
import time
from datetime import datetime
import os
import re
import sys

class TelegramOSINT:
    def __init__(self):
        self.api_id = None
        self.api_hash = None
        self.client = None
        self.session_name = "telegram_osint"
        self.results = {}
        
    def get_api_credentials(self):
        print("\nPlease enter your Telegram API credentials (get them from my.telegram.org)")
        self.api_id = input("Enter your API ID: ").strip()
        self.api_hash = input("Enter your API Hash: ").strip()
        
        if not self.api_id.isdigit():
            print("Error: API ID must be a number")
            return False
        if not re.match(r'^[a-f0-9]{32}$', self.api_hash, re.IGNORECASE):
            print("Error: API Hash should be 32 characters long hexadecimal")
            return False
            
        return True
    
    def connect(self):
        try:
            if not self.api_id or not self.api_hash:
                if not self.get_api_credentials():
                    return False
                    
            self.client = TelegramClient(self.session_name, int(self.api_id), self.api_hash)
            self.client.start()
            
            if not self.client.is_connected():
                print("Failed to establish connection")
                return False
                
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False
    
    def get_user_info(self, username):
        try:
            if not username.startswith('@'):
                username = '@' + username
                
            user = self.client.get_entity(username)
            return {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'verified': user.verified,
                'bot': user.bot,
                'scam': user.scam,
                'access_hash': user.access_hash if hasattr(user, 'access_hash') else None,
                'premium': user.premium if hasattr(user, 'premium') else None
            }
        except ValueError:
            return "Error: User not found. Check the username."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_full_user_info(self, username):
        try:
            if not username.startswith('@'):
                username = '@' + username
                
            user = self.client.get_entity(username)
            full_info = self.client(GetFullUserRequest(user))
            
            result = {
                'basic_info': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'premium': user.premium if hasattr(user, 'premium') else None
                },
                'full_info': {
                    'about': full_info.about,
                    'common_chats_count': full_info.common_chats_count if hasattr(full_info, 'common_chats_count') else None,
                    'blocked': full_info.blocked,
                    'phone_calls_available': full_info.phone_calls_available if hasattr(full_info, 'phone_calls_available') else None,
                    'phone_calls_private': full_info.phone_calls_private if hasattr(full_info, 'phone_calls_private') else None,
                    'profile_photo': str(full_info.profile_photo) if full_info.profile_photo else None,
                    'notify_settings': str(full_info.notify_settings)
                }
            }
            
            if hasattr(user, 'status'):
                result['basic_info']['status'] = str(user.status)
            
            return result
        except ValueError:
            return "Error: User not found. Check the username."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def search_public_messages(self, username, limit=100):
        try:
            if not username.startswith('@'):
                username = '@' + username
                
            user = self.client.get_entity(username)
            messages = []
            counter = 0
            
            for dialog in self.client.iter_dialogs():
                if counter >= limit:
                    break
                    
                if dialog.is_channel or dialog.is_group:
                    try:
                        for message in self.client.iter_messages(dialog.id, from_user=user.id, limit=5):  # Limit per chat
                            if counter >= limit:
                                break
                                
                            messages.append({
                                'date': message.date.strftime("%Y-%m-%d %H:%M:%S"),
                                'chat_id': dialog.id,
                                'chat_title': dialog.title,
                                'message': message.text,
                                'media': bool(message.media)
                            })
                            counter += 1
                    except Exception as e:
                        continue
            
            return messages
        except ValueError:
            return "Error: User not found. Check the username."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_channel_info(self, channel_username):
        try:
            if not channel_username.startswith('@'):
                channel_username = '@' + channel_username
                
            channel = self.client.get_entity(channel_username)
            full_info = self.client(GetFullUserRequest(channel))
            
            participants = []
            try:
                for user in self.client.iter_participants(channel, limit=10):
                    participants.append({
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    })
            except Exception as e:
                participants = f"Cannot fetch participants: {str(e)}"
            
            return {
                'id': channel.id,
                'title': channel.title,
                'username': channel.username,
                'description': channel.about if hasattr(channel, 'about') else None,
                'participants_count': channel.participants_count if hasattr(channel, 'participants_count') else None,
                'date_created': channel.date.strftime("%Y-%m-%d") if hasattr(channel, 'date') else 'Unknown',
                'verified': channel.verified if hasattr(channel, 'verified') else None,
                'scam': channel.scam if hasattr(channel, 'scam') else None,
                'participants_sample': participants
            }
        except ValueError:
            return "Error: Channel not found. Check the username."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def find_related_channels(self, username):
        try:
            if not username.startswith('@'):
                username = '@' + username
                
            user = self.client.get_entity(username)
            channels = []
            
            for dialog in self.client.iter_dialogs(limit=50):  
                if dialog.is_channel:
                    try:
                        participants = self.client.get_participants(dialog.id, limit=100)  # Limit participants check
                        for participant in participants:
                            if participant.id == user.id and hasattr(participant, 'admin_rights') and participant.admin_rights:
                                channels.append({
                                    'id': dialog.id,
                                    'title': dialog.title,
                                    'username': dialog.entity.username if hasattr(dialog.entity, 'username') else None
                                })
                                break
                    except Exception as e:
                        continue
            
            return channels
        except ValueError:
            return "Error: User not found. Check the username."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def save_results(self, data, filename):
        try:
            if not filename:
                filename = "telegram_osint_results"
                
            filename = re.sub(r'[\\/*?:"<>|]', "", filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return f"Results saved to {filename}"
        except Exception as e:
            return f"Error saving file: {str(e)}"

def display_menu():
    print("""
    ████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗
    ╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
       ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║
       ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║
       ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
       ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
    
    """)

def main():
    display_menu()
    
    tool = TelegramOSINT()
    
    if not tool.connect():
        print("\nFailed to connect to Telegram. Please check your API credentials and internet connection.")
        return
    
    results = {}
    
    while True:
        print("\nOptions:")
        print("1. Get basic user info")
        print("2. Get full user info")
        print("3. Search user's public messages")
        print("4. Get channel info")
        print("5. Find channels where user is admin")
        print("6. Save current results to file")
        print("7. Exit")
        
        choice = input("\nSelect an option (1-7): ").strip()
        
        if choice == '1':
            username = input("Enter Telegram username (with or without @): ").strip()
            user_info = tool.get_user_info(username)
            print("\nUser Information:")
            if isinstance(user_info, dict):
                for k, v in user_info.items():
                    print(f"{k:>15}: {v}")
                results['Basic User Info'] = user_info
            else:
                print(user_info)
                
        elif choice == '2':
            username = input("Enter Telegram username (with or without @): ").strip()
            full_info = tool.get_full_user_info(username)
            print("\nFull User Information:")
            if isinstance(full_info, dict):
                print("Basic Info:")
                for k, v in full_info['basic_info'].items():
                    print(f"{k:>15}: {v}")
                print("\nExtended Info:")
                for k, v in full_info['full_info'].items():
                    print(f"{k:>15}: {v}")
                results['Full User Info'] = full_info
            else:
                print(full_info)
                
        elif choice == '3':
            username = input("Enter Telegram username (with or without @): ").strip()
            try:
                limit = int(input("Max messages to search (default 20, max 100): ") or 20)
                limit = min(limit, 100)  
            except ValueError:
                print("Invalid number. Using default 20.")
                limit = 20
                
            messages = tool.search_public_messages(username, limit)
            print(f"\nFound {len(messages) if isinstance(messages, list) else 0} public messages:")
            if isinstance(messages, list):
                for msg in messages[:5]:  
                    print(f"\n[{msg['date']}] {msg['chat_title']}:")
                    print(msg['message'][:200] + ("..." if len(msg['message']) > 200 else ""))
                results['Public Messages'] = messages
            else:
                print(messages)
                
        elif choice == '4':
            channel = input("Enter channel username (with or without @): ").strip()
            channel_info = tool.get_channel_info(channel)
            print("\nChannel Information:")
            if isinstance(channel_info, dict):
                for k, v in channel_info.items():
                    if k == 'participants_sample' and isinstance(v, list):
                        print("\nParticipants sample:")
                        for p in v[:5]:
                            name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
                            print(f"- @{p.get('username', 'no_username')} ({name})")
                    else:
                        print(f"{k:>20}: {v}")
                results['Channel Info'] = channel_info
            else:
                print(channel_info)
                
        elif choice == '5':
            username = input("Enter Telegram username (with or without @): ").strip()
            channels = tool.find_related_channels(username)
            print(f"\nFound {len(channels) if isinstance(channels, list) else 0} channels where user is admin:")
            if isinstance(channels, list):
                for chan in channels[:10]:  
                    print(f"- {chan.get('title', 'No title')} (@{chan.get('username', 'no_username')})")
                results['Admin Channels'] = channels
            else:
                print(channels)
                
        elif choice == '6':
            if results:
                filename = input("Enter filename (without extension, leave blank for default): ").strip()
                save_result = tool.save_results(results, filename)
                print(save_result)
            else:
                print("No results to save.")
                
        elif choice == '7':
            if results:
                save = input("Save results before exiting? (y/n): ").lower().strip()
                if save == 'y':
                    filename = input("Enter filename (without extension, leave blank for default): ").strip()
                    save_result = tool.save_results(results, filename)
                    print(save_result)
            print("\nExiting...")
            if tool.client and tool.client.is_connected():
                tool.client.disconnect()
            sys.exit(0)
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)