from youtubesearchpython import VideosSearch

videosSearch = VideosSearch('Circles - Official Audio', limit = 10)
results = videosSearch.result()["result"]

for result in results:
    print(result["title"])