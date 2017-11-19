from __future__ import division

import sys
from PyQt5.QtMultimedia import QAudioInput, QAudioFormat, QAudioDeviceInfo, QAudio
from PyQt5.QtCore import *
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import queue
import audioop

class ResponseHandler(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.queue = queue.Queue()
        self.stopped = False
        self.shouldClear = False

    answerChanged = pyqtSignal('QString')

    def clear(self):
        self.shouldClear = True

    def run(self):
        while not self.stopped:
            responses = self.queue.get()
            if self.shouldClear:
                self.queue.queue.clear()
                # self.answerChanged.emit('')
                self.shouldClear = False
                continue
            for response in responses:
                if not self.shouldClear:
                    self.handleResponse(response)
                break

    def addRespnses(self, responses):
        self.queue.put(responses)

    def handleResponse(self, response):
        if not response.results:
            return
        print(response)
        result = response.results[0]
        if not result.alternatives:
            return
        # print(result)
        self.answerChanged.emit(result.alternatives[0].transcript)


class AnswerRecognizer(QObject):
    def __init__(self, rate, language):
        QObject.__init__(self)
        self.rate = rate
        self.requests = []
        self.client = speech.SpeechClient()
        self.config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=rate,
            language_code=language)
        self.streamingConfig = types.StreamingRecognitionConfig(
            config=self.config,
            interim_results=False)
        self.resonseHandlerThread = QThread()
        self.resonseHandler = ResponseHandler()
        self.resonseHandler.moveToThread(self.resonseHandlerThread)
        def answerChanged(answer):
            self.bestText = answer
            self.answerChanged.emit(answer)
        self.resonseHandler.answerChanged.connect(answerChanged)
        self.resonseHandlerThread.started.connect(self.resonseHandler.run)
        self.resonseHandlerThread.start()
        self.reset()

        self.ioDevice = QBuffer(parent=self)
        self.ioDevice.open(QIODevice.ReadWrite)
        self.audioFormat = QAudioFormat()
        self.audioFormat.setSampleRate(self.rate)
        self.audioFormat.setChannelCount(1)
        self.audioFormat.setByteOrder(QAudioFormat.LittleEndian)
        self.audioFormat.setSampleSize(16)
        self.audioFormat.setCodec("audio/pcm")
        self.audioFormat.setSampleType(QAudioFormat.SignedInt)
        deviceInfo = QAudioDeviceInfo.defaultInputDevice()
        print(deviceInfo.deviceName())
        if not deviceInfo.isFormatSupported(self.audioFormat):
            print("not supported format")
        self.audioInput = QAudioInput(self.audioFormat, parent=self)
        self.audioInput.setNotifyInterval(500)
        self.audioInput.notify.connect(self.stream)
        self.audioInput.start(self.ioDevice)



    def reset(self):
        self.requests.clear()
        self.resonseHandler.clear()
        self.stopped = True
        self.silenceLen = 0
        self.bestText = ""

    answerChanged = pyqtSignal('QString')
    answerFinalize = pyqtSignal()
    loudnessChanged = pyqtSignal('float')

    def stream(self):
        self.loudnessChanged.emit(0)
        self.ioDevice.seek(0)
        data = self.ioDevice.readAll().data()
        self.ioDevice.seek(0)
        if self.stopped:
            return

        if len(data) > 0:
            rms = audioop.rms(data, 2)
            print("rms:", rms)
            self.loudnessChanged.emit(rms/32767)
            print("rms threshold:", int(32767 * 0.35))
            print("data len:", len(data))
            if rms < int(32767 * 0.35):
                self.silenceLen += len(data)
            else:
                self.silenceLen = 0
            print("silence len:", self.silenceLen)
            if self.silenceLen >= self.rate * 2 * 3:
                if self.bestText == "":
                    self.startRecognition()
                    # return
                else:
                    self.stopRecognition()
                    self.finalizeAnswer()
                    return

            self.requests.append((types.StreamingRecognizeRequest(audio_content=data)))
            try:
                responses = self.client.streaming_recognize(self.streamingConfig, self.requests)
                self.resonseHandler.addRespnses(responses)
            except Exception as e:
                print(e)
                self.stopRecognition()
                self.finalizeAnswer()
                return

    @pyqtSlot()
    def startRecognition(self):
        print("start rec")
        self.reset()
        self.answerChanged.emit("")
        self.stopped = False

    @pyqtSlot()
    def stopRecognition(self):
        print("stop")
        self.reset()

    @pyqtSlot()
    def finalizeAnswer(self):
        print("finalize")
        self.resonseHandler.clear()
        self.answerFinalize.emit()

    def close(self):
        print("close")
        self.stopRecognition()
        self.audioInput.stop()
        self.ioDevice.close()


