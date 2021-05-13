import json
import musicbrainzngs
import pandas as pd
import urllib3

http = urllib3.PoolManager()

musicbrainzngs.set_useragent("test", 1, contact=None)

# set the artist name here
artist_name = 'The Dillinger Escape Plan'

# construct the url to retrieve the unique ID for this artist to retrieve the track listings below in JSON
url = 'http://musicbrainz.org/ws/2/artist/?query=artist:"' + artist_name + '"+&fmt=json'

# send the api request to musicbrainz
r = http.request(
    'GET',
    url
)
data = json.loads(r.data.decode('utf-8'))

# find the ID from the extracted json
mbid = data['artists'][0]['id']

# the lyrics site has a limit of a 100 results, the below loops through the pages to return all the songs

limit = 100
offset = 0
recordings = []
page = 0

# create a list to hold the track names
list = []

# use the function from the musicbrainz library to retrieve the track listings
# and loop through the pages based on the recording count
result = musicbrainzngs.browse_recordings(artist=mbid, limit=limit)
for recordinglist in result['recording-list']:
    list.append(recordinglist['title'])
page_recordings = result['recording-list']
recordings += page_recordings

if "recording-count" in result:
    count = result['recording-count']
while len(page_recordings) >= limit:
    offset += limit
    page += 1
    result = musicbrainzngs.browse_recordings(artist=mbid, limit=limit, offset=offset)
    page_recordings = result['recording-list']
    recordings += page_recordings
    for recording_list in result['recording-list']:
        # append the results to the list
        list.append(recording_list['title'])

# create a list to hold the word count for the tracks
list2 = []

# Loop through all the track names in the list and then pass those results to the lyrics API to return the lyrics
for tracks in list:
    # construct the url
    lyrics_url = "https://api.lyrics.ovh/v1/" + artist_name + "/" + tracks
    r = http.request(
        'GET',
        lyrics_url
    )
    # some songs do not have lyrics, in those cases the JSON format changes and the key switches
    # from 'lyrics' to 'error'. This except skips these results and continues the loop
    try:
        data2 = json.loads(r.data.decode('utf-8'))
        # retrieve the lyrics
        lyrics = data2['lyrics']
        # count the number of words
        word_list = lyrics.split()
        words = len(word_list)
        # add the number of words to list2
        list2.append(words)

    except:
        continue

# use a pandas data from to hold the words data and then use pandas
# aggregate functions to do the sums, max, min etc and print the result
df = pd.DataFrame(list2, columns=['track_length'])

# find the total number tracks
total_tracks = df.shape[0]

# Find the total number of words
total_track_lengths = df['track_length'].sum()

# divide the total number words by the number of tracks
Average_track_lengths = total_track_lengths / total_tracks

# Do the other aggregate functions
max_track_lengths = df['track_length'].max()
min_track_lengths = df['track_length'].min()
var_track_lengths = df['track_length'].var()
std_track_lengths = df['track_length'].std()

# print the results
print("For " + artist_name + " the average number of words is " + str(Average_track_lengths))
print("The maximum word length is " + str(max_track_lengths))
print("The minimum word length is " + str(min_track_lengths))
print("The variance is " + str(var_track_lengths))
print("The standard deviation is " + str(std_track_lengths))
