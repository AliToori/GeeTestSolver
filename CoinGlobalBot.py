#!/usr/bin/env python3
"""
    *******************************************************************************************
    CoinGlobalBot: CoinGlobal Geetest Captcha Solver
    Developer: Ali Toori, Full-Stack Python Developer
    Founder: https://boteaz.com/
    *******************************************************************************************
"""
import os
import pickle
import re
import json
import random
import logging.config
import time
import zipfile
import base64
from time import sleep
import pandas as pd
import numpy as np
import io

import cv2
import pyfiglet
import concurrent.futures
from pathlib import Path
from datetime import datetime
from multiprocessing import freeze_support

import requests
import pyautogui
from PIL import Image
from selenium import webdriver

from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service


class CoinGlobalBot:
    def __init__(self):
        self.PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))
        self.file_settings = str(self.PROJECT_ROOT / 'BotRes/Settings.json')
        self.directory_downloads = str(self.PROJECT_ROOT / 'BotRes/Downloads/')
        self.url_coin_global = "https://frontend-pkr.coin-global.io/#/pages/login/register"
        self.user_agents = self.get_user_agents()
        self.settings = self.get_settings()
        self.LOGGER = self.get_logger()
        self.logged_in = False
        driver = None

    # Get self.LOGGER
    @staticmethod
    def get_logger():
        """
        Get logger file handler
        :return: LOGGER
        """
        logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            'formatters': {
                'colored': {
                    '()': 'colorlog.ColoredFormatter',  # colored output
                    # --> %(log_color)s is very important, that's what colors the line
                    'format': '[%(asctime)s,%(lineno)s] %(log_color)s[%(message)s]',
                    'log_colors': {
                        'DEBUG': 'green',
                        'INFO': 'cyan',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'bold_red',
                    },
                },
                'simple': {
                    'format': '[%(asctime)s,%(lineno)s] [%(message)s]',
                },
            },
            "handlers": {
                "console": {
                    "class": "colorlog.StreamHandler",
                    "level": "INFO",
                    "formatter": "colored",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    'encoding': 'utf-8',
                    "filename": "CoinGlobalBot.log",
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 1
                },
            },
            "root": {"level": "INFO",
                     "handlers": ["console", "file"]
                     }
        })
        return logging.getLogger()

    @staticmethod
    def enable_cmd_colors():
        # Enables Windows New ANSI Support for Colored Printing on CMD
        from sys import platform
        if platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    @staticmethod
    def banner():
        pyfiglet.print_figlet(text='____________ CoinGlobalBot\n', colors='RED')
        print('CoinGlobalBot GeeTest Captcha Solver Bot\n'
              'YouTube: youtube.com/@AliToori\n'
              '************************************************************************')

    def get_settings(self):
        """
        Creates default or loads existing settings file.
        :return: settings
        """
        if os.path.isfile(self.file_settings):
            with open(self.file_settings, 'r') as f:
                settings = json.load(f)
            return settings
        settings = {"Settings": {
            "NumberOfInstancesToRun": 1
        }}
        with open(self.file_settings, 'w') as f:
            json.dump(settings, f, indent=4)
        with open(self.file_settings, 'r') as f:
            settings = json.load(f)
        return settings

    # Get random user agent
    def get_user_agents(self):
        file_uagents = str(self.PROJECT_ROOT / 'BotRes/user_agents.txt')
        with open(file_uagents) as f:
            content = f.readlines()
        return [x.strip() for x in content]

    # Loads web driver with configurations
    def get_driver(self, proxy=True, headless=False):
        driver_bin = str(self.PROJECT_ROOT / "BotRes/bin/chromedriver.exe")
        service = Service(executable_path=driver_bin)
        # mobile_emulation = {"deviceName": "iPhone X"}
        mobile_emulation = {"deviceName": "Nest Hub Max"}
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # options.add_experimental_option("mobileEmulation", mobile_emulation)
        prefs = {"directory_upgrade": True,
                 "credentials_enable_service": False,
                 "profile.password_manager_enabled": False,
                 "profile.default_content_settings.popups": False,
                 # "profile.managed_default_content_settings.images": 2,
                 f"download.default_directory": f"{self.directory_downloads}",
                 "profile.default_content_setting_values.geolocation": 2
                 }
        options.add_experimental_option("prefs", prefs)
        options.add_argument(F'--user-agent={random.choice(self.user_agents)}')
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    @staticmethod
    def wait_until_visible(driver, css_selector=None, element_id=None, name=None, class_name=None, tag_name=None, duration=10000, frequency=0.01):
        if css_selector:
            WebDriverWait(driver, duration, frequency).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        elif element_id:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, element_id)))
        elif name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.NAME, name)))
        elif class_name:
            WebDriverWait(driver, duration, frequency).until(
                EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
        elif tag_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))

    # Solve GeeTest Puzzle using Pillow and OpenCV
    def solve_geetest(self, slider_slice_path, image_path):
        self.LOGGER.info(f'Solving GeeTest captcha')
        # Process background image
        img = Image.open(image_path)
        img1 = np.array(img.convert('RGB'))
        img_blur = cv2.GaussianBlur(img1, (3, 3), 0)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        img_canny = cv2.Canny(img_gray, 250, 250)
        img_edges = Image.fromarray(img_canny)
        remaining = img_edges.crop((61, 0, img.width, 192))
        remaining.save('background_img.png')

        # Process slider_slice image
        slider_slice = Image.open(slider_slice_path)
        slider_slice_img1 = np.array(slider_slice.convert('RGB'))
        slider_slice_img_blur = cv2.GaussianBlur(slider_slice_img1, (3, 3), 0)
        slider_slice_img_gray = cv2.cvtColor(slider_slice_img_blur, cv2.COLOR_BGR2GRAY)
        slider_slice_img_canny = cv2.Canny(slider_slice_img_gray, 250, 250)
        slider_slice_img_edges = Image.fromarray(slider_slice_img_canny)
        slider_slice = slider_slice_img_edges.crop((0, 0, 59, 192))
        bbox = slider_slice.getbbox()
        slider_slice = slider_slice.crop(bbox)
        slider_slice.save('slider_slice_img.png')

        img_rgb = np.stack((remaining,) * 3, axis=-1)
        template = np.stack((slider_slice,) * 3, axis=-1)
        w, h = template.shape[:-1]

        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        for i in range(10, 1, -1):
            threshold = i / 10
            loc = np.where(res >= threshold)
            if len(loc[0]) > 0:
                break
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        # Get and convert numpy int64 to int
        offset = loc[1][0].item()
        self.LOGGER.info(f'GeeTest captcha has been solved successfully!')
        return offset

    # Login to the CoinGlobal
    def login_coin_global(self, driver, email, password):
        self.LOGGER.info(f'Signing-in to CoinGlobal account: {email}')
        self.LOGGER.info(f'Requesting CoinGlobal: {str(self.url_coin_global)} Account: {email}')
        driver.get(self.url_coin_global)
        self.LOGGER.info('Filling credentials')

        # Wait for Email registration button
        self.wait_until_visible(driver=driver, css_selector='[class="regTypec"]', duration=5)
        actions = ActionChains(driver)

        # sleep(1)
        # Open inspect elements
        # self.LOGGER.info('Opening inspector')
        # actions.send_keys(Keys.CONTROL, Keys.SHIFT, 'c').perform()
        sleep(1)
        # # Toggle device to mobile mode
        # self.LOGGER.info('Toggling device mode to mobile')
        # actions.send_keys(Keys.CONTROL, Keys.SHIFT, 'm').perform()
        # sleep(1)

        # Open inspect elements
        sleep(1)
        pyautogui.hotkey('ctrl', 'shift', 'C')
        sleep(3)
        # Toggle device to mobile mode
        pyautogui.hotkey('ctrl', 'shift', 'M')
        sleep(1)


        # try:
        # Enter email
        # self.wait_until_visible(driver=driver, css_selector='input[class="uni-input-input"]')
        email_input = driver.find_elements(By.CSS_SELECTOR, 'input[class="uni-input-input"]')[1]
        email_input.send_keys(email)
        sleep(1)
        email_input.click()

        # Click get code text
        self.wait_until_visible(driver=driver, css_selector='[class="code_text"]', duration=5)
        driver.find_element(By.CSS_SELECTOR, '[class="code_text"]').click()

        # Wait for captcha img
        # self.wait_until_visible(driver=driver, css_selector='[class="verify-img-panel"] div', duration=10)
        self.LOGGER.info(f'Captcha found')

        # Save captcha image to local file
        # captcha_img_url = driver.find_element(By.CSS_SELECTOR, '[class="verify-img-panel"] div').get_attribute('style').split('"')[1]
        captcha_img_encoded = driver.find_element(By.CSS_SELECTOR, '[class="verify-img-panel"] img').get_attribute('src')
        # self.LOGGER.info(f'Captcha Img URL: {captcha_img_encoded}')
        # Decode and save the encoded captcha image
        # Get time to save captcha image by
        time_stamp = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
        captcha_img_path = os.path.join(f'captcha_{time_stamp}.png')
        with open(captcha_img_path, "wb") as file:
            file.write(base64.urlsafe_b64decode(captcha_img_encoded.replace('data:image/png;base64,', '')))

        # Save the slider image to local file
        slider_img_encoded = driver.find_element(By.CSS_SELECTOR, '[class="verify-sub-block"] img').get_attribute('src')
        # self.LOGGER.info(f'Slider Img URL: {slider_img_encoded}')
        # Decode and save the encoded captcha image
        # Get time to save captcha image by
        time_stamp = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
        slider_img_path = os.path.join(f'slider_{time_stamp}.png')
        with open(slider_img_path, "wb") as file:
            file.write(base64.b64decode(slider_img_encoded.replace('data:image/png;base64,', '')))

        sleep(1)
        # captcha_offset = self.solve_geetest(slider_slice_path=slider_img_path, image_path=captcha_img_path)
        captcha_offset = 80

        # Move the puzzle with the captcha offset
        # scrollBar = driver.find_element(By.CSS_SELECTOR, 'div.bs-slide-thumb')
        print(f'Moving the puzzle to {captcha_offset}')
        # self.wait_until_visible(driver=driver, css_selector='[class="verify-move-block"]', duration=10)
        slider = driver.find_element(By.CSS_SELECTOR, '[class="verify-move-block"]')
        # actions.drag_and_drop_by_offset(source=slider, xoffset=captcha_offset, yoffset=0)
        sleep(1)
        location = slider.location
        size = slider.size
        print(f'Slider location: {location}, Size: {size}')
        x = slider.location["x"] + 220
        y = slider.location["y"] + 150
        captcha_offset += x
        # captcha_offset += 100
        print(f'Slider position, x:{x}, y:{y}')
        pyautogui.moveTo(x=x, y=y)
        sleep(1)
        pyautogui.dragTo(x=captcha_offset, y=y, button='left')
        print(f'Puzzle moved to {captcha_offset}')
        sleep(3)
        try:
            # Wait for captcha solving confirmation
            # Click get code text
            self.wait_until_visible(driver=driver, css_selector='[class="code_text"]', duration=10)
            code_text = driver.find_elements(By.CSS_SELECTOR, '[class="code_text"]')[1].text
            if 'S' in code_text:
                self.LOGGER.info("Login successful")
            else:
                self.LOGGER.info("Login failed")
        except:
            print("Captcha error")

        sleep(5000)
        # Enter Password
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(password)

        # Click Login
        driver.find_element(By.CSS_SELECTOR, '[class="sc-a4a6801b-0 dPXqEb"]').click()
        self.LOGGER.info(f'Login clicked')

        # except:
        #     pass
        try:
            self.wait_until_visible(driver=driver, css_selector='.avatar-img ', duration=10)
            self.LOGGER.info('Successful sign-in')
        except:
            pass

    # Main method to handle all the functions
    def main(self):
        freeze_support()
        self.enable_cmd_colors()
        self.banner()
        self.LOGGER.info(f'CoinGlobalBot launched')
        email = self.settings["Settings"]["Email"]
        password = self.settings["Settings"]["Password"]
        driver = self.get_driver()
        self.login_coin_global(driver=driver, email=email, password=password)
        # captcha_offset = self.solve_geetest(slider_slice_path='slider_slice.png', image_path='captcha.png')
        # print(captcha_offset)


if __name__ == '__main__':
    CoinGlobalBot().main()
