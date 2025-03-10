import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import requests
import base64
from encoded_credentials import get_credentials
import pandas as pd
import json
import os

#This allows me to read in start and end times for songs if any are chosen, and defaults the rest.
play_times_path = "Playlist.csv"
if os.path.exists(play_times_path):
    times = pd.read_csv(play_times_path)
    times['Start_second'] = times['Start_second'].fillna(0)
    times['Interval_second'] = times['Interval_second'].fillna(58)
else:
    times = pd.DataFrame(columns=[['Song','Start_Second','Interval_second']])

#I didn't want my credentials just out in the open, while I knew my friends wouldn't take them, this is just good practice even if not truly secure.
def deobfuscate_credentials():
    obfuscated_username, obfuscated_password = get_credentials()
    username = base64.b64decode(obfuscated_username.encode()).decode()
    password = base64.b64decode(obfuscated_password.encode()).decode()
    return username, password


class MusicSpotlight():
    #Initiates an authorization token, and also grabs current playback volume
    def __init__(self, sp):
        self.sp = sp
        self.volume = sp.current_playback()['device']['volume_percent']

    #Not used un the actual performance of the program, but was useful for testing
    def get_current_song(self):
        current_track = self.sp.current_playback()
        if current_track is None:
            return "No song is currently playing."
        track_name = current_track['item']['name']
        artists = ", ".join([artist['name'] for artist in current_track['item']['artists']])
        album_name = current_track['item']['album']['name']
        is_playing = current_track['is_playing']
        status = "Currently playing:" if is_playing else "Currently paused:"
        return f"{status} {track_name} by {artists} from the album '{album_name}'."
    
    #Spotify authorization tokens expire after an hour, this refreshes my token as needed to allow the application to run for longer.
    def refresh(self):
        decoded_username, decoded_password = deobfuscate_credentials()
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
        refresh_token = self.sp.auth_manager.get_cached_token()['refresh_token']
        CLIENT_ID = decoded_username
        CLIENT_SECRET = decoded_password
        REDIRECT_URI = 'http://localhost:8888/callback'
        query = "https://accounts.spotify.com/api/token"
        requests_body = {
                "grant_type": "refresh_token",
                "refresh_token":refresh_token,
                "client_id":CLIENT_ID,
                "client_secret": CLIENT_SECRET}
        r = requests.post(url = query, headers = headers, data = requests_body)
        return r.json()['access_token']
    
    def skip_to_next_track(self,sp):
        sp.next_track()

    #Basic method for seeking to a particular second in a song, used later
    @staticmethod
    def seek_to_position(sp, position_seconds):
        current_track = sp.current_playback()
        if current_track is None:
            return
        device_id = current_track['device']['id']
        position_ms = int(position_seconds * 1000)
        sp.seek_track(position_ms = position_ms, device_id = device_id)

    #I was experiencing lag with the seek_to_position method, where I would skip to the next track, and it would take about 200 milliseconds to actually execute the
    #seek, which led to songs with loud intro notes to blast them before skipping to the point I actually wanted which was annoying. I couldn't fix the latency so I
    #developed a fade out, which would fade the volume to 0 at the end of the current song, then skip, then set the volume back to the original after the "seek" function.
    #Can't hear the result of the latency if the volume is at 0.
    #Note worthy: Depending on location and internet speed, fade_volume can also be laggy, causing the fade out, which is intended to be 2 seconds, to be more like
    #4 or 5. If you want more precise control of start and end times, it may be better to comment out the fade and just set volume to 0, and back to target
    @staticmethod
    def fade_volume(sp, initial_volume, target_volume, fade_duration=2, num_steps=5):
        if initial_volume > 0:
            volume_step = (target_volume - initial_volume) / num_steps
            for i in range(num_steps):
                new_volume = max(0, initial_volume + (i * volume_step))
                sp.volume(int(new_volume))
                time.sleep(fade_duration / num_steps)
            sp.volume(target_volume)
        else:
            sp.volume(target_volume)

    #Ok, you're deep into this project at this point. I have to admit that this next block is the DUMBEST thing here, and yet I still feel like I should keep it.
    #My friends and I have an ongoing joke about Thunderstruck that originated back in college that meant we could never skip the song once it began playing.
    #I, as a practical joke, decided to take that a mile further and developed the thunderstruck exception which not only refuses to skip the song as it does the
    #others, but also refuses to ALLOW you to skip the song. For the duration of the song, it tracks how far into it you are, and should you change the song
    #it will revert back to thunderstruck and skip to the moment you were at before you pressed skip. It checks every 2.5 seconds. There is no way around this
    #without halting the entire program.
    def Thunderstruck_Exception(sp):
        track_uri = 'spotify:track:57bgtoPSgt236HzfBOd8kj'
        
        start_time = time.time()
        counter = 0
        for x in range(10000):
            current_track = sp.current_playback()
            device_id = current_track['device']['id']
            if current_track['item']['uri'] != track_uri:
                sp.start_playback(uris=[track_uri])
                time.sleep(0.1)
                sp.seek_track(position_ms = (int(counter*1000)), device_id = device_id)
                start_time = time.time()  # Reset timer 
            if time.time() - start_time > 290:
                break  # Exit loop after 290 seconds
            else:
                time.sleep(2.5)
                counter+=2.5

    #Originally this was planned to last an hour before I figured out how to refresh my access token, this block manages all the functions above.
    def skip_tracks(self):
  # 58 seconds
        access_token = self.sp.auth_manager.get_cached_token()['access_token']
        for x in range(61):          
            if (x) % 55 == 0:
                access_token = self.refresh()
         #sends request off to spotify
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://api.spotify.com/v1/me/player/queue", headers=headers)
            response.raise_for_status()
            
            response_json = response.json()
            queue_array = response_json.get('queue', [])
            song_titles = [item['name'] for item in queue_array]
            print(song_titles[0])
            #start position refers to the seek functionality, interval is used in the actual looping to tell the program how long we actually want the song to play
            #This allows for songs to end where we want them to instead of just 60 second increments, which minimizes downtime in playlist spotlights
            if song_titles[0] in list(times['Song']):
                start_position = times['Start_second'].loc[times['Song'] == song_titles[0]].iloc[0]
                interval = times['Interval_second'].loc[times['Song'] == song_titles[0]].iloc[0]
            else:
                start_position = 0
                interval = 58
            # Replace start_times with your actual data source
            if song_titles[0] == 'Thunderstruck':
                interval = 290
                start_position = 0
            time.sleep(3)
            
            #There are some odd numbers here like interval minus 4, all of that is to combat latency and allow for all api calls to resolve.
            current_volume = self.sp.current_playback()['device']['volume_percent']
            self.fade_volume(self.sp, current_volume, 0)
            self.skip_to_next_track(self.sp)
            self.seek_to_position(self.sp, start_position)
            self.fade_volume(self.sp, 0, current_volume)
            time.sleep(interval - 4)

    # Replace this with your own logic for getting the start position
if __name__ == "__main__":
    decoded_username, decoded_password = deobfuscate_credentials()
    CLIENT_ID = decoded_username
    CLIENT_SECRET = decoded_password
    REDIRECT_URI = 'http://localhost:8888/callback'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope='user-read-playback-state user-modify-playback-state'))
    
    MusicSpotlight(sp).skip_tracks()
