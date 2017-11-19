import sys
from gtts import gTTS as gtts
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QBuffer, QIODevice
import io

class QuestionPlayer(object):
    def __init__(self):
        self.mplayer = QMediaPlayer()
        self.buffer = QBuffer()

    def audioCallabck(self, status, startCallback, endCallback):
        if status == QMediaPlayer.BufferedMedia:
            startCallback()
        elif status == QMediaPlayer.EndOfMedia:
            endCallback()
            self.buffer.close()



    def playQuestionAudio(self, question_text, startCallback, endCallback):
        tts = gtts(text=question_text, lang='ru', slow=False)
        file = io.BytesIO()
        tts.write_to_fp(file)
        self.buffer.setData(file.getvalue())
        file.close()
        self.buffer.open(QIODevice.ReadOnly)
        if self.mplayer.receivers(self.mplayer.mediaStatusChanged) > 0:
            self.mplayer.mediaStatusChanged.disconnect()
        self.mplayer.mediaStatusChanged.connect(lambda status: self.audioCallabck(status, startCallback, endCallback))
        self.mplayer.setMedia(QMediaContent(), self.buffer)
        self.mplayer.setVolume(100)
        self.mplayer.play()


