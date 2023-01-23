from music_downloader import MusicDownloader
from utils import Credentials
import typer

app = typer.Typer()


DRIVER_PATH = './chromedriver'
SCOPE = "user-read-recently-played"
SPOTIFY_DOWNLOADER_WEBSITE =  'https://www.soundloaders.com/spotify-downloader/'



@app.command()
def hello(
    output_dir_name: str,
    playlist_url: str,
    ):
    output_dir_name = output_dir_name if output_dir_name else 'downloads'
    
    cred = Credentials()
    downloader = MusicDownloader(
        output_dir_name=output_dir_name, 
        cred=cred, 
        scope=SCOPE,
        spotify_downloader_website=SPOTIFY_DOWNLOADER_WEBSITE,
        driver_path=DRIVER_PATH
        )

    downloader.download_playlist(playlist_url)

    print('='*50)
    print('DONE')


if __name__ == "__main__":
    app()
