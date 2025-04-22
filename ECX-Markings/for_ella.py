try:
    num = int(input("Enter your age:"))
    value = 0
    print(num,"!")
    print("Now let's get it divided by 2")
    print("That will give us", num/2)
    print("How about if we divide it by 0?")
    print(num/value)
except ValueError:
    print("That's not an age, Dear!")
except TypeError:
    print("Type with words, not letters.")
except ZeroDivisionError:
    print("Unfortunately we can't divide by 0")

import requests

TOKEN = '7717980436:AAEAtRJaoPa8QPkJRFTe9Vm_JWtmw3o87us'
url = f'https://api.telegram.org/bot{TOKEN}/getMe'

response = requests.get(url)
print(response.json())

# NAME: OLANIYAN ENIOLA

# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# import requests
# from bs4 import BeautifulSoup
# import time
# import sys
#
#
# SPOTIPY_CLIENT_ID = "b087b554661a4d1ca974841f7733dcd7"
# SPOTIPY_CLIENT_SECRET = "16abfd4eeb874acebf47d544501b0325"
# SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"
# SCOPE = "playlist-modify-public"
#
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     client_id=SPOTIPY_CLIENT_ID,
#     client_secret=SPOTIPY_CLIENT_SECRET,
#     redirect_uri=SPOTIPY_REDIRECT_URI,
#     scope=SCOPE
# ))
#
# # Get user ID
# try:
#     user_id = sp.current_user()["id"]
# except Exception as err:
#     print("Error retrieving current user from Spotify:", err)
#     sys.exit(1)
#
#
# def get_top_10_songs(artist_name):
#     """
#     Fetch top 10 songs of an artist from Spotify using exact matching.
#     If exact matching fails, prompts user to choose from similar artists.
#     """
#     results = sp.search(q=f"artist:{artist_name}", type="artist", limit=5)
#     artist = None
#
#     for item in results["artists"]["items"]:
#         if item["name"].lower() == artist_name.lower():
#             artist = item
#             break
#
#     if not artist:
#         print(f"Exact match for artist '{artist_name}' not found.")
#         similar_artists = results["artists"]["items"]
#         if not similar_artists:
#             print("No similar artists found.")
#             return []
#         print("Did you mean one of these?")
#         for i, item in enumerate(similar_artists):
#             print(f" {i+1}. {item['name']}")
#         choice = input("Enter the number of the artist you'd like to select or press enter to cancel: ").strip()
#         if choice.isdigit():
#             idx = int(choice) - 1
#             if 0 <= idx < len(similar_artists):
#                 artist = similar_artists[idx]
#             else:
#                 print("Invalid selection. Cancelling operation.")
#                 return []
#         else:
#             print("Cancelling operation.")
#             return []
#
#     artist_id = artist["id"]
#     top_tracks = sp.artist_top_tracks(artist_id)["tracks"]
#     return [(track["name"], track["id"]) for track in top_tracks[:10]]
#
#
# def get_billboard_top_100(date):
#     """
#     Scrape Billboard Hot 100 for a given date (YYYY-MM-DD format).
#     Returns a list of tuples (song, artist) if successful.
#     """
#     url = f"https://www.billboard.com/charts/hot-100/{date}/"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#                       "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#     }
#     try:
#         response = requests.get(url, headers=headers)
#     except Exception as err:
#         print("Error fetching Billboard data:", err)
#         return []
#
#     if response.status_code != 200:
#         print(f"Failed to retrieve Billboard data. Status code: {response.status_code}")
#         return []
#
#     soup = BeautifulSoup(response.text, "html.parser")
#
#     songs = [song.get_text(strip=True) for song in soup.select("h3.c-title.a-no-trucate")]
#     artists = [artist.get_text(strip=True) for artist in soup.select("span.c-label.a-no-trucate")]
#
#     if len(songs) != len(artists):
#         print("⚠️ Mismatch in songs and artists count. Billboard's structure may have changed.")
#         return []
#
#     return list(zip(songs, artists))
#
#
# def search_song_on_spotify(song, artist):
#     """
#     Search for a song on Spotify by given song and artist names.
#     Returns track ID if found.
#     """
#     query = f"track:{song} artist:{artist}"
#     result = sp.search(q=query, type="track", limit=1)
#     tracks = result.get("tracks", {}).get("items", [])
#     return tracks[0]["id"] if tracks else None
#
#
# def create_playlist(name, track_ids):
#     """
#     Create a Spotify playlist and add the provided track IDs.
#     """
#     try:
#         playlist = sp.user_playlist_create(user=user_id, name=name, public=True)
#         sp.playlist_add_items(playlist_id=playlist["id"], items=track_ids)
#         print(f"Playlist '{name}' created successfully!")
#     except Exception as err:
#         print("Error while creating playlist:", err)
#
#
# def run_program():
#     """
#     Main loop to prompt the user for creating either a Billboard or
#     Top 10 artist playlist.
#     """
#     while True:
#         choice = input("\nEnter 'billboard' for Billboard playlist, type an artist name for Top 10 songs, or 'exit' to quit: ").strip().lower()
#         if choice == "exit":
#             print("Exiting program.")
#             break
#
#         if choice == "billboard":
#             date = input("Input date in this format YYYY-MM-DD: ").strip()
#             songs = get_billboard_top_100(date)
#             if not songs:
#                 print(f"No songs found on Billboard Hot 100 for the date {date}.")
#                 continue
#
#             print(f"\nFound {len(songs)} songs from Billboard Hot 100 on {date}:")
#             track_ids = []
#             for song, artist in songs:
#                 track_id = search_song_on_spotify(song, artist)
#                 if track_id:
#                     track_ids.append(track_id)
#                     print(f"Found: '{song}' by {artist}")
#                 else:
#                     print(f"Not found on Spotify: '{song}' by {artist}")
#                 time.sleep(1)
#
#             if not track_ids:
#                 print("No valid tracks were found on Spotify.")
#                 continue
#
#             print("\nCreating playlist with the logged songs...")
#             create_playlist(f"Billboard Hot 100 - {date}", track_ids)
#
#         else:
#             artist_name = choice
#             songs = get_top_10_songs(artist_name)
#             if not songs:
#                 print(f"No songs found for artist '{artist_name}'.")
#                 continue
#
#             print(f"\nTop 10 songs by {artist_name}:")
#             track_ids = []
#             for song_name, track_id in songs:
#                 print(f" {song_name}")
#                 track_ids.append(track_id)
#
#             print("\nCreating playlist with these songs...")
#             create_playlist(f"Top 10 - {artist_name}", track_ids)
#
#
# if __name__ == "__main__":
#     run_program()
