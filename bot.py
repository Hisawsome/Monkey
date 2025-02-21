import aiohttp
import asyncio
import json
import os
from datetime import datetime
from colorama import init, Fore, Style
from fake_useragent import UserAgent
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

console = Console()

def display_logo():
    logo_text = Text(" MonkeyRush ", style="bold yellow", justify="center")
    footer_text = Text("by Ridi  |  Telegram: @Ridihimself", style="cyan", justify="center")
    panel = Panel(
        logo_text, 
        title="🚀 LOGO 🚀", 
        subtitle=footer_text, 
        border_style="red",
        width=90  
    )
    console.print(panel)

display_logo()
print("\n")
init(autoreset=True)

def get_user_agent():
    return "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36 Telegram-Android/11.2.2 (Xiaomi M1908C3JGG; Android 12; SDK 31; AVERAGE)"

clk = int(input(Fore.CYAN + Style.BRIGHT + "Your Taping !? ..: " + Fore.YELLOW))

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def send_telegram_message(message):
    # Set your Telegram bot token and chat ID either as environment variables or directly here.
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id")
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {"chat_id": telegram_chat_id, "text": message}
    async with aiohttp.ClientSession() as session:
         async with session.post(url, json=payload) as response:
             return await response.json()

async def read_tokens():
    file_path = "data.txt"
    if not os.path.exists(file_path):
        print(Fore.RED + f"[{get_time()}] [Error] data.txt file not found!")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            tokens = [line.strip() for line in file.readlines() if line.strip()]
            if not tokens:
                print(Fore.YELLOW + f"[{get_time()}] [Warning] data.txt is empty!")
                return []
            return tokens
    except Exception as e:
        print(Fore.RED + f"[{get_time()}] [Error] Failed to read tokens: {e}")
        return []

async def fetch_user_data(session, token, account_number):
    url = "https://api.monkeyrush.fun/api/v1/user"

    headers = {
        'User-Agent': get_user_agent(),
        'Accept': "application/json, text/plain, */*",
        'Authorization': f"Bearer {token}",
        'Origin': "https://clicker.monkeyrush.fun",
        'Referer': "https://clicker.monkeyrush.fun/"
    }

    try:
        async with session.get(url, headers=headers) as response:
            data = await response.text()
            json_data = json.loads(data)
            username = json_data.get("username", "No Name")
            print(Fore.GREEN + f"[{get_time()}] [Account {account_number}] [Success] Username: {username}")
    except json.JSONDecodeError:
        print(Fore.RED + f"[{get_time()}] [Account {account_number}] [Error] Failed to parse JSON!")
    except Exception as e:
        print(Fore.RED + f"[{get_time()}] [Account {account_number}] [Error] Request failed: {e}")

async def take_reward(session, token, account_number):
    url = "https://api.monkeyrush.fun/api/v1/game/take-reward"
    payload = {"type": "daily"}

    headers = {
        'User-Agent': get_user_agent(),
        'Accept': "application/json, text/plain, */*",
        'Content-Type': "application/json",
        'Authorization': f"Bearer {token}",
        'Origin': "https://clicker.monkeyrush.fun",
        'Referer': "https://clicker.monkeyrush.fun/"
    }

    try:
        async with session.post(url, json=payload, headers=headers) as response:
            status_code = response.status
            if status_code == 200:
                success_message = f"[{get_time()}] [Account {account_number}] [Success] Reward claimed successfully!"
                print(Fore.GREEN + success_message)
                await send_telegram_message(f"Account {account_number}: Reward claimed successfully!")
            else:
                info_message = f"[{get_time()}] [Account {account_number}] [Info] Daily reward already claimed."
                print(Fore.YELLOW + info_message)
    except Exception as e:
        error_message = f"[{get_time()}] [Account {account_number}] [Error] Failed to claim reward: {e}"
        print(Fore.RED + error_message)
        await send_telegram_message(f"Account {account_number}: Error claiming reward: {e}")

async def send_request(session, token, account_number):
    url = "https://api.monkeyrush.fun/api/v1/game/tap"
    payload = {"score": clk}

    headers = {
        'User-Agent': get_user_agent(),
        'Accept': "application/json, text/plain, */*",
        'Content-Type': "application/json",
        'Authorization': f"Bearer {token}",
        'Origin': "https://clicker.monkeyrush.fun",
        'Referer': "https://clicker.monkeyrush.fun/"
    }

    try:
        async with session.post(url, json=payload, headers=headers) as response:
            result = await response.text()
            data = json.loads(result)
            score = data.get("score", "N/A")
            energy = data.get("energy", "N/A")
            print(Fore.CYAN + f"[{get_time()}] [Acc {account_number}] [Info] Score: {score} | Energy: {energy}")
            if energy <= clk:
                print(Fore.RED + f"[{get_time()}] [Acc {account_number}] [Info] Waiting for 5 minutes due to low energy.")
                await asyncio.sleep(300)
    except json.JSONDecodeError:
        print(Fore.RED + f"[{get_time()}] [Account {account_number}] [Error] Failed to parse JSON response!")
    except Exception as e:
        print(Fore.RED + f"[{get_time()}] [Account {account_number}] [Error] Request failed: {e}")

async def handle_account(token, account_number):
    async with aiohttp.ClientSession() as session:
        await fetch_user_data(session, token, account_number)
        await take_reward(session, token, account_number)

        while True:
            await send_request(session, token, account_number)
            await asyncio.sleep(10)

async def main():
    tokens = await read_tokens()
    if not tokens:
        return

    tasks = [handle_account(token, i + 1) for i, token in enumerate(tokens)]
    await asyncio.gather(*tasks)

asyncio.run(main())
