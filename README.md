# songs-loader

This repository contains some code to load music from `https://spotify-downloader.com/` using a spotify playlist url.

Below are the steps required to make the code work:

1- Create a virtual environment and activate it:
```
python3 -m venv venv && source venv/bin/activate
```
2- Install the required packages using  the `requirements.txt` file
```
pip install -r requirements.txt
```

3- Create an app on https://developers.spotify.com/ and write your new ID and SECRET in a `.env` file as follows:

```
client_ID='client_ID'
client_SECRET='client_SECRET'   
redirect_url='http://localhost:9000'
```

4- You can now run the code as follows:
```
python main.py 'OUTPUT_DIR_NAME' 'SPOTIFY_PLAYLIST_URL'

```


# Attention:
- We recommend using a VPN.

- The code may break since the website is always updating.
- you need to install the right chromedriver for your OS. You can find it [here](https://chromedriver.chromium.org/downloads)