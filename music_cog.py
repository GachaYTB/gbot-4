import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
sendytlink = False

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False


        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnected_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" & item, download=False)["entries"][0]
            except Exception:
                return False
        return {'source': info['formats'[0],['url']], 'title': info['title']}
    
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.music_queuepop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, a):
        
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc == None:
                    await a.send('Could not connect to the voice channel')
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

        else:
            self.is_playing = False
    
    @commands.event
    async def on_message(msg, self):
        global sendytlink
        if msg.content == 'g4:play':
            await msg.channel.send('Please send your youtube link.')
            sendytlink = True
        elif msg.content == 'g4:pause':
            if self.is_playing:
                self.is_playing = False
                self.is_paused = True
                self.vc.pause()
            elif self.is_paused:
                self.is_playing = True
                self.is_paused = False
                self.vc.resume()
        elif msg.content == 'g4:resume':
            if self.is_paused:
                self.is_playing = True
                self.is_paused = False
                self.vc.resume()
        elif msg.content == 'g4:skip':
            if self.vc != None and self.vc:
                self.vc.stop()
                await self.play_music(msg.channel)
        elif msg.content == 'g4:queue':
            retval = ""

            for i in range(0, len(self.music_queue)):
                if i > 4: break
                retval += self.music_queue[i][0]['title'] + '\n'

            if retval != "":
                await msg.channel.send(retval)
            else:
                await msg.channel.send('No music in the queue.')
        elif msg.content == 'g4:leave':
            self.is_playing = False
            self.is_paused = False
            await self.vc.disconnect()
        elif sendytlink == True:
            query = " ".join(msg.content)

            voice_channel = msg.author.voice.channel
            if voice_channel is None:
                await msg.channel.send('Please connect in a voice channel.')
            elif self.is_paused:
                self.vc.resume()
            else:
                song = self.search_yt(query)
                if type(song) == type(True):
                    await msg.channel.send('Could not download the song. Incorrect format, Please try another keyword.')
                else:
                    await msg.channel.send('Song added to the queue.')
                    self.music_queue.append([song, voice_channel])

                    if self.is_playing == False:
                        await self.play_music(msg.channel)