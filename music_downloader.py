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
from utils import download_file


options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36")
WINDOW_SIZE = "920,800"
options.add_argument("--headless")
options.add_argument("--window-size=%s" % WINDOW_SIZE)
options.add_argument("--mute-audio")

spotify_downloader_website = 'https://www.soundloaders.com/spotify-downloader/'




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
        print("="* 100)
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
        print(self.dir)
        driver = webdriver.Chrome(self.driver_path, chrome_options=self.options)
        return driver


    @staticmethod
    def check_exists_by_xpath(driver, xpath):
        try:
            driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False
        return True


    def download_song(self, url):

        try:
            driver = self._connect_driver()
            driver.get(self.spotify_downloader_website)
            time.sleep(2)
            search_bar = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/div[1]/div[1]/form/input')
            search_bar.clear()
            search_bar.send_keys(url)
            search_bar.send_keys(Keys.ENTER)
            time.sleep(2)
            download_button = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/div[1]/div[1]/div/div/div[2]/button')
            download_button.click()
            time.sleep(3)

            download_window = '//*[@id="__next"]/main/div/div[1]/div[1]/div[2]/div/div'
            try:
                element = WebDriverWait(driver, 5*60).until_not( EC.presence_of_element_located((By.XPATH, download_window)))
                time.sleep(2)
            finally:
                driver.quit()
        except:
            print(f'Error with {url}')


    def download_playlist(self, url):
        self._create_dir(url)
        prefs = {
            "download.default_directory" : self.dir,
            "savefile.default_directory": self.dir,}
        self.options.add_experimental_option("prefs", prefs)
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.process_playlist(url)
        playlist_csv = pd.read_csv(os.path.join( self.dir, 'summary_file.csv'))
        playlist_csv['status'] = 'To Be Completed'

        Parallel(n_jobs=15)(delayed(self.download_song)(url) 
                        for url in playlist_csv['url'] )
