import time
import pafy
import vlc

urls = ["https://www.youtube.com/watch?v=Xhh3_-JRnDc", "https://www.youtube.com/watch?v=wEGOxgfdRVc", "https://www.youtube.com/watch?v=IX5xMgqAkOk"]
video = pafy.new(urls[0])
best = video.getbest()
playurl = best.url

instance = vlc.Instance("--vout=dummy")
player = instance.media_player_new()
media = instance.media_new(playurl)
media.get_mrl()
player.set_media(media)
player.play()

while player.is_playing:
    query = input(">> ")

    if query == "p":
        player.pause()
    if query == "u":
        player.play()
    if query == "e":
        break

player.stop()