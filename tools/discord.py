
import discord
import asyncio
import aiohttp
import json
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

class DiscordOSINT:
    def __init__(self):
        self.token = None
        self.session = None
        self.client = None
        self.banner = f"""
{Fore.BLUE}
██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗     
██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗   
██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║    
██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║    
██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝     
╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝      
{Style.RESET_ALL}
{Fore.YELLOW}Version: 1.0 | Author: NoneR00tk1t{Style.RESET_ALL}
"""

    def display_banner(self):
        print(self.banner)

    async def auto_detect_token(self):
        try:
            paths = [
                os.path.join(os.getenv('APPDATA'), 'discord', 'Local Storage', 'leveldb'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Discord', 'Local Storage', 'leveldb'),
                os.path.expanduser('~/.config/discord/Local Storage/leveldb')
            ]
            
            for path in paths:
                if os.path.exists(path):
                    for file in os.listdir(path):
                        if file.endswith(('.ldb', '.log')):
                            try:
                                with open(os.path.join(path, file), 'r', errors='ignore') as f:
                                    content = f.read()
                                    token_pos = content.find('token":"')
                                    if token_pos != -1:
                                        self.token = content[token_pos+8:].split('"')[0]
                                        return True
                            except:
                                continue
            return False
        except Exception as e:
            print(f"{Fore.RED}Token detection error: {e}{Style.RESET_ALL}")
            return False

    async def initialize_session(self):
        self.session = aiohttp.ClientSession()
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True
        self.client = discord.Client(intents=intents)
        
        try:
            await self.client.login(self.token)
        except discord.LoginFailure:
            print(f"{Fore.RED}Invalid token! Please check your token.{Style.RESET_ALL}")
            return False
        return True

    async def get_user_info(self, user_id):
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            async with self.session.get(f'https://discord.com/api/v9/users/{user_id}', headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        'username': f"{data['username']}#{data['discriminator']}",
                        'id': data['id'],
                        'avatar_url': f"https://cdn.discordapp.com/avatars/{data['id']}/{data['avatar']}.png" if data.get('avatar') else None,
                        'account_created': datetime.fromtimestamp(((int(data['id']) >> 22) + 1420070400000) / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                        'bot': data.get('bot', False),
                        'public_flags': data.get('public_flags', 0),
                        'banner_url': f"https://cdn.discordapp.com/banners/{data['id']}/{data['banner']}.png" if data.get('banner') else None,
                        'accent_color': data.get('accent_color')
                    }
                return {'error': f'API request failed with status {resp.status}'}
        except Exception as e:
            return {'error': str(e)}

    async def get_guild_info(self, guild_id):
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            async with self.session.get(f'https://discord.com/api/v9/guilds/{guild_id}', headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        'server_name': data['name'],
                        'server_id': data['id'],
                        'owner_id': data['owner_id'],
                        'member_count': data.get('approximate_member_count', 'Unknown'),
                        'icon_url': f"https://cdn.discordapp.com/icons/{data['id']}/{data['icon']}.png" if data.get('icon') else None,
                        'features': data.get('features', []),
                        'premium_tier': data.get('premium_tier', 0),
                        'verification_level': data.get('verification_level', 0)
                    }
                return {'error': f'API request failed with status {resp.status}'}
        except Exception as e:
            return {'error': str(e)}

    async def search_messages(self, query, limit=5):
        results = []
        for guild in self.client.guilds:
            for channel in guild.text_channels:
                try:
                    async for message in channel.history(limit=limit):
                        if query.lower() in message.content.lower():
                            results.append({
                                'server': guild.name,
                                'channel': channel.name,
                                'author': str(message.author),
                                'content': message.content,
                                'timestamp': message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                                'attachments': [a.url for a in message.attachments]
                            })
                except discord.Forbidden:
                    continue
                except Exception as e:
                    print(f"{Fore.YELLOW}Error searching in {guild.name}/{channel.name}: {e}{Style.RESET_ALL}")
                    continue
        return results

    async def run(self):
        self.display_banner()
        
        print(f"{Fore.CYAN}Attempting automatic Discord token detection...{Style.RESET_ALL}")
        if not await self.auto_detect_token():
            print(f"{Fore.YELLOW}Token not found automatically.{Style.RESET_ALL}")
            self.token = input(f"{Fore.GREEN}Enter your Discord token: {Style.RESET_ALL}").strip('"\' ')
        
        if not await self.initialize_session():
            return
            
        while True:
            print(f"\n{Fore.MAGENTA}╔════════════════════════════════╗")
            print(f"{Fore.MAGENTA}║{Fore.CYAN}      Discord OSINT Tool      {Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}╠════════════════════════════════╣")
            print(f"{Fore.MAGENTA}║{Fore.CYAN} 1. Investigate User         {Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}║{Fore.CYAN} 2. Investigate Server       {Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}║{Fore.CYAN} 3. Search Messages          {Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}║{Fore.CYAN} 0. Exit                     {Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}╚════════════════════════════════╝{Style.RESET_ALL}")
            
            choice = input(f"{Fore.YELLOW}Select option: {Style.RESET_ALL}")
            
            if choice == '1':
                user_id = input(f"{Fore.GREEN}Enter target user ID: {Style.RESET_ALL}")
                print(f"{Fore.CYAN}Gathering user information...{Style.RESET_ALL}")
                result = await self.get_user_info(user_id)
                print(f"\n{Fore.GREEN}Results:{Style.RESET_ALL}")
                print(json.dumps(result, indent=2))
            elif choice == '2':
                guild_id = input(f"{Fore.GREEN}Enter target server ID: {Style.RESET_ALL}")
                print(f"{Fore.CYAN}Gathering server information...{Style.RESET_ALL}")
                result = await self.get_guild_info(guild_id)
                print(f"\n{Fore.GREEN}Results:{Style.RESET_ALL}")
                print(json.dumps(result, indent=2))
            elif choice == '3':
                query = input(f"{Fore.GREEN}Enter search query: {Style.RESET_ALL}")
                print(f"{Fore.CYAN}Searching messages...{Style.RESET_ALL}")
                result = await self.search_messages(query)
                print(f"\n{Fore.GREEN}Search Results:{Style.RESET_ALL}")
                print(json.dumps(result, indent=2))
            elif choice == '0':
                print(f"{Fore.RED}Exiting...{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
            
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        
        await self.session.close()
        if self.client.is_ready():
            await self.client.close()

if __name__ == "__main__":
    tool = DiscordOSINT()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(tool.run())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Operation cancelled by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
    finally:
        loop.close()
