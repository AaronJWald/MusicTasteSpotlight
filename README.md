# MusicTasteSpotlight
## A Python tool that allows for smarter Spotify playback through the use of automated transitions, custom start times, and pre-defined intervals.

This project utilizes Spotify's API to control the playback of a user's queue or playlist to fit their liking. The script retrieves the next song in the queue and searches a Dataframe for the what time the song should begin and end. It sends these parameters through Spotify's API to ensure playback fits the user's expectation. It also handles authroization and refresh tokens to allow the app to function as long as desired. Since this app relies on sending many API requests it requires an internet connection to function, and performs better with faster internet.

You will need to enable Spotify for Developers (Free) and create an app in order to obtain a Client and Secret ID. These are required for proper authorization.

## Features:
 ### Automated Playback Handling
 - Reads user data from a local csv to determine what portion of the song should play.
 - Contains functionality to default to the first 60 seconds in case no time intervals are selected.

 ### Token Refreshing
 - Handles authorization and refreshing of access tokens through Spotify's API to ensure no downtime in application function.

 ### Audio Control
 - Gradual fade-in/out effects to smoothen transitions between songs.
 - Mitigates latency issues when seeking within a song.


## Installation and configuration
 ### Clone this repository
 ```
 git clone https://github.com/AaronJWald/MusicTasteSpotlight.git
 cd Music-Spotlight
 ```
 ### Install Dependencies
 ```
 pip install -r requirements.txt
 ```
 ### Enable Spotify for Developers and create an app
 - This allows you to obtain a client and secret id.
 - Define at least one redirect uri, I use http://localhost:3000

 ### Configure encoded_credentials
 - Input client and secret id where prompted
 ### Start Spotify on your chosen device and play a song
 ### Run Music_Taste_spotlight.py
 - This will begin the default playback of skipping songs every 60 seconds.
 - Choosing songs in the existing excel will play them with the given parameters
 - I am currently out of the country, when I return I will upload the file that allows for the creation of DataFrames based on Spotify playlist URI


