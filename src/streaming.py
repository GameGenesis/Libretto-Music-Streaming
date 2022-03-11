import time
import pafy
import vlc

url = "https://www.youtube.com/watch?v=Xhh3_-JRnDc"
video = pafy.new(url)
best = video.getbest()
playurl = best.url

instance = vlc.Instance("--vout=dummy")
player = instance.media_player_new()
media = instance.media_new(playurl)
media.get_mrl()
player.set_media(media)
player.play()

while player.is_playing:
    time.sleep(0.1)