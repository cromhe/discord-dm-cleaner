import requests
import time
import json
import sys
from colorama import Fore, init

init(autoreset=True)

# setup headers
def get_headers(token):
    return {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

def load_cfg():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except:
        print(Fore.RED + "err: missing config.json")
        sys.exit()

def main():
    cfg = load_cfg()
    token = cfg.get("token")
    delay = cfg.get("delay", 1.5)

    if not token or token == "paste_ur_token_here":
        print(Fore.RED + "bro forgot the token in config.json")
        return

    # get user id first (to know which msg is urs)
    me_req = requests.get("https://discord.com/api/v9/users/@me", headers=get_headers(token))
    if me_req.status_code != 200:
        print(Fore.RED + "invalid token or locked acc")
        return
    
    my_id = me_req.json()['id']
    print(Fore.GREEN + f"logged in as: {me_req.json()['username']} ({my_id})")

    # input dm channel id
    channel_id = input(Fore.YELLOW + "paste dm/channel id to clean: ").strip()

    print(Fore.CYAN + "fetching msgs... (might take a while)")

    # fetch & delete loop
    total_deleted = 0
    has_more = True
    last_msg_id = None

    while has_more:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100"
        if last_msg_id:
            url += f"&before={last_msg_id}"

        r = requests.get(url, headers=get_headers(token))
        
        if r.status_code != 200:
            print(Fore.RED + f"cant fetch msgs: {r.status_code}")
            break

        msgs = r.json()
        if not msgs:
            has_more = False
            break

        for msg in msgs:
            last_msg_id = msg['id']
            
            # only delete my msgs
            if msg['author']['id'] == my_id:
                del_url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{msg['id']}"
                del_req = requests.delete(del_url, headers=get_headers(token))
                
                if del_req.status_code == 204:
                    print(Fore.GREEN + f"[+] deleted msg: {msg['id']}")
                    total_deleted += 1
                elif del_req.status_code == 429:
                    print(Fore.RED + "[!] rate limited, sleeping 5s...")
                    time.sleep(5)
                else:
                    print(Fore.RED + f"[-] fail to delete: {del_req.status_code}")
                
                # sleep to be safe
                time.sleep(delay)
            else:
                # skip other ppl msgs
                pass

    print(Fore.GREEN + f"done. total deleted: {total_deleted}")

if __name__ == "__main__":
    main()