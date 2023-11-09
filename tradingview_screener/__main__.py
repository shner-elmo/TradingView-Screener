from __future__ import annotations

import os
import json
import time
from typing import Optional

import typer
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


app = typer.Typer()


@app.command()
def login(username: Optional[str] = None, password: Optional[str] = None):
    # TODO: add support for multiple browsers (browser: str = 'chrome')
    username = username or os.environ.get('TRADINGVIEW_USERNAME')
    password = password or os.environ.get('TRADINGVIEW_PASSWORD')

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.set_capability('cloud:options', {'goog:loggingPrefs': {'performance': 'ALL'}})

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)
    driver.get('https://www.tradingview.com/accounts/signin/')

    if username and password:
        driver.find_element(By.XPATH, "//button[@name='Email']").click()
        time.sleep(2)
        driver.find_element(By.XPATH, "//input[@id='id_username']").send_keys(username)
        driver.find_element(By.XPATH, "//input[@id='id_password']").send_keys(password)
        driver.find_element(By.XPATH, "//*[text()='Remember me']").click()
        time.sleep(0.2)
        driver.find_element(By.XPATH, "//*[text()='Sign in']").click()
    else:
        print('Waiting for you to login manually ...')
        input('Please press enter when you are finished.')

        print('Resuming script ...')

    driver.get('https://www.tradingview.com/screener/')

    time.sleep(10)
    request = next(
        x for x in driver.requests if x.url == 'https://scanner.tradingview.com/america/scan'
    )

    if request.headers.get('sessionid'):
        print('sessionid found')
    else:
        print('sessionid not found')

    cookies = dict(x.split('=', maxsplit=1) for x in request.headers['Cookie'].split('; '))
    default_headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'text/plain, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-usenewauth': 'true',
    }
    headers = {k: request.headers.get(k, v) for k, v in default_headers.items()}

    with open('output.json', 'w', encoding='utf8') as f:
        json.dump({'headers': headers, 'cookies': cookies}, f, indent=4)

    driver.close()


if __name__ == '__main__':
    app()
