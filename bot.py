from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, urllib.parse, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Stork:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "chrome-extension://knnliglhgkmlblppdejchidfihjnockl",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Stork - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "tokens.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account
    
    def generate_payload(self, refresh_token):
        payload = {
            "grant_type": "refresh_token",
            "client_id": "5msns4n49hmg3dftp2tp1t2iuh",
            "refresh_token": refresh_token
        }
        return urllib.parse.urlencode(payload)

    def print_message(self, account, proxy, color, message):
        proxy_value = proxy.get("http") if isinstance(proxy, dict) else proxy
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy_value}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def refresh_token(self, refresh_token: str, proxy=None, retries=5):
        url = "https://stork-prod-apps.auth.ap-northeast-1.amazoncognito.com/oauth2/token"
        data = self.generate_payload(refresh_token)
        headers = {
            **self.headers,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['access_token']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(refresh_token, proxy, Fore.RED, f"GET Access Token Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def user_info(self, refresh_token: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://app-api.jp.stork-oracle.network/v1/me"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[refresh_token]}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            await self.get_new_token(refresh_token, use_proxy)
                            headers["Authorization"] = f"Bearer {self.access_tokens[refresh_token]}"
                            continue

                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(refresh_token, proxy, Fore.RED, f"GET User Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def turn_on_verification(self, refresh_token: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://app-api.jp.stork-oracle.network/v1/stork_signed_prices"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[refresh_token]}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            await self.get_new_token(refresh_token, use_proxy)
                            headers["Authorization"] = f"Bearer {self.access_tokens[refresh_token]}"
                            continue
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(refresh_token, proxy, Fore.RED, f"GET Message Hash Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def validate_verfication(self, refresh_token: str, msg_hash: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://app-api.jp.stork-oracle.network/v1/stork_signed_prices/validations"
        data = json.dumps({"msg_hash":msg_hash, "valid":True})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[refresh_token]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        if response.status == 401:
                            await self.get_new_token(refresh_token, use_proxy)
                            headers["Authorization"] = f"Bearer {self.access_tokens[refresh_token]}"
                            continue
                        
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(refresh_token, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def get_new_token(self, refresh_token: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(refresh_token) if use_proxy else None
        access_token = None
        while access_token is None:
            access_token = await self.refresh_token(refresh_token, proxy)
            if not access_token:
                proxy = self.rotate_proxy_for_account(refresh_token) if use_proxy else None
                await asyncio.sleep(5)
                continue

            self.access_tokens[refresh_token] = access_token
            self.print_message(refresh_token, proxy, Fore.GREEN, "GET Access Token Success")
            return self.access_tokens[refresh_token]

    async def process_user_earning(self, refresh_token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(refresh_token) if use_proxy else None

            user = await self.user_info(refresh_token, use_proxy, proxy)
            if user:
                verified_msg = user.get("stats", {}).get("stork_signed_prices_valid_count", 0)
                invalid_msg = user.get("stats", {}).get("stork_signed_prices_invalid_count", 0)

                self.print_message(refresh_token, proxy, Fore.GREEN,
                    f"Verified Messages:"
                    f"{Fore.WHITE + Style.BRIGHT} {verified_msg} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Invalid Messages: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{invalid_msg}{Style.RESET_ALL}"
                )

            await asyncio.sleep(5 * 60)
            
    async def process_send_ping(self, refresh_token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(refresh_token) if use_proxy else None

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Try to GET Hash Message...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )

            verify = await self.turn_on_verification(refresh_token, use_proxy, proxy)
            if verify:
                for key in verify:
                    if "USD" in key:
                        msg_hash = verify[key].get("timestamped_signature", {}).get("msg_hash")
                        self.print_message(refresh_token, proxy, Fore.GREEN, f"Message Hash: {Fore.BLUE+Style.BRIGHT}{self.mask_account(msg_hash)}{Style.RESET_ALL}")

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )

                ping = await self.validate_verfication(refresh_token, msg_hash, use_proxy, proxy)
                if ping:
                    self.print_message(refresh_token, proxy, Fore.GREEN, "PING Success")

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 60 Seconds For Next Ping...{Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(1 * 60)
        
    async def process_accounts(self, refresh_token: str, use_proxy: bool):
        self.access_tokens[refresh_token] = await self.get_new_token(refresh_token, use_proxy)
        if self.access_tokens[refresh_token]:
            tasks = []
            tasks.append(asyncio.create_task(self.process_user_earning(refresh_token, use_proxy)))
            tasks.append(asyncio.create_task(self.process_send_ping(refresh_token, use_proxy)))
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice = 2

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for refresh_token in tokens:
                    if refresh_token:
                        tasks.append(asyncio.create_task(self.process_accounts(refresh_token, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Stork()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Stork - BOT{Style.RESET_ALL}                                       "                              
        )
