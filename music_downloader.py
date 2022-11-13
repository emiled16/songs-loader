import os
import time

import pandas as pd
import spotipy
from joblib import Parallel, delayed
from requests import get
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from spotipy.oauth2 import SpotifyOAuth


options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36")
WINDOW_SIZE = "920,800"
options.add_argument("--headless")
options.add_argument("--window-size=%s" % WINDOW_SIZE)
options.add_argument("--mute-audio")

spotify_downloader_website = 'https://spotify-downloader.com/'

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


class MusicDownloader:
    def __init__(self, output_dir_name, cred, scope, spotify_downloader_website, 
                        driver_path, options=options):

        self.output_dir_name = output_dir_name
        self.client_ID = cred.client_ID
        self.client_SECRET = cred.client_SECRET
        self.redirect_url = cred.redirect_url
        self.scope = scope

        self.sp = self._connect_spotify_api()

        # webdriver
        self.driver_path = driver_path
        self.options = options
        self.spotify_downloader_website = spotify_downloader_website

        self.main_path = os.getcwd()


    def _connect_spotify_api(self):
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.client_ID, client_secret= self.client_SECRET, 
                redirect_uri=self.redirect_url, scope=self.scope)
                )
        return sp

    def process_playlist(self, url):
        artists = []
        names = []
        urls = []
        results = self.sp.playlist(url)
        # print(results.keys())
        playlist = results['tracks']['items']

        for song in playlist:
            track = song['track']
            artist = track['artists'][0]['name']
            name = track['name']
            url = track['external_urls']['spotify']

            artists.append(artist)
            names.append(name)
            urls.append(url)

            print(artist, " – ", name, " – ", url)

        summary = pd.DataFrame(
            {
                "name": names,
                "artist": artists,
                "url": urls,
                })
        if self.dir: 
            summary.to_csv(os.path.join(self.dir, 'summary_file.csv'), index=False)
        return summary

    def _create_dir(self, url):
        results = self.sp.playlist(url)

        path = os.path.join(self.main_path, self.output_dir_name)
        # Check whether the specified path exists or not
        isExist = os.path.exists(path)
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(path)
        self.dir = path

    def _connect_driver(self):
        driver = webdriver.Chrome(self.driver_path, chrome_options=self.options)
        return driver

    def download_song(self, url):
        try:
            driver = self._connect_driver()
            driver.get(self.spotify_downloader_website)
            time.sleep(2)  
            search_bar = driver.find_element(By.XPATH, '//*[@id="link"]')
            search_bar.clear()
            search_bar.send_keys(url)
            time.sleep(1)
            submit_button = driver.find_element(By.XPATH, '//*[@id="submit"]')
            submit_button.click()
            delay = 30 # seconds
            try:
                myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="result"]/article/footer/button')))
            except TimeoutException:
                pass

            download_button = driver.find_element(By.XPATH, '//*[@id="result"]/article/footer/button')
            download_button.click()
            while 'save' not in driver.find_element(By.XPATH, '//*[@id="result"]/article/footer/button').text.lower()  :
                time.sleep(2)
            time.sleep(1)    
            download_button.click()
            verification_button = driver.find_element(By.XPATH,  '//*[@id="startVerification"]')
            time.sleep(0.5)
            verification_button.click()
            time.sleep(20)

            p = driver.current_window_handle
            chwd = driver.window_handles
            for w in chwd:
                #switch focus to child window
                if(w!=p):
                    driver.switch_to.window(w)
            time.sleep(5)   
            if check_exists_by_xpath(driver, '//*[@id="cmpbox"]'):
                driver.find_element(By.XPATH, '//*[@id="cmpwelcomebtnyes"]/a').click()
            time.sleep(20)

            try:
                verify_button = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]')
            except:
                verify_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]')
            verify_button.click()

            time.sleep(60)
            driver.quit()
        except:
            print('Error:', url)


    def download_playlist(self, url):
        self._create_dir(url)
        prefs = {"download.default_directory" : self.dir}
        self.options.add_experimental_option("prefs", prefs)
        self.process_playlist(url)
        playlist_csv = pd.read_csv(os.path.join( self.dir, 'summary_file.csv'))
        playlist_csv['status'] = 'To Be Completed'

        Parallel(n_jobs=8)(delayed(self.download_song)(url) 
                        for url in playlist_csv['url'] )
