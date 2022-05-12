from pytube import YouTube

url = 'https://www.youtube.com/watch?v=wEGOxgfdRVc'
yt = YouTube(url)

print(f"{yt.metadata[0].get('Artist')} // {yt.metadata[0].get('Song')} // {yt.metadata[0].get('Album')}")