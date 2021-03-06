from PyQt5.QtCore import *
from .tts import QuestionPlayer
from .stt import AnswerRecognizer
from Server import Server
import time

class DialogModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent=parent)
        self.isQuestionRole = Qt.UserRole + 1
        self.textRole = Qt.UserRole + 2
        self.model = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.model)

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return None
        if role == self.isQuestionRole:
            return self.model[index.row()]["isQuestion"]
        elif role == self.textRole:
            return self.model[index.row()]["text"]

    def roleNames(self):
        roles = QAbstractListModel.roleNames(self)
        roles[self.isQuestionRole] = b"isQuestion"
        roles[self.textRole] = b"text"
        return roles

    def clear(self):
        self.beginResetModel()
        self.model.clear()
        print(self.model)
        self.endResetModel()

    def addQuestion(self, question):
        self.beginInsertRows(QModelIndex(), len(self.model), len(self.model))
        self.model.append({"isQuestion": True, "text": question})
        self.endInsertRows()

    def addResponse(self, response):
        self.beginInsertRows(QModelIndex(), len(self.model), len(self.model))
        self.model.append({"isQuestion": False, "text": response})
        self.endInsertRows()

    def modifyResponse(self, text):
        if len(self.model) > 0 and not self.model[-1]["isQuestion"]:
            self.model[-1]["text"] = text
            self.dataChanged.emit(self.index(len(self.model) - 1), self.index(len(self.model) - 1))

class DialogStrategy(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.doctor = None
        self.client = None
        self.questions = Server.common_questions

    def init(self, client):
        self.client = client

    def determineNextQuestion(self, previousQuestionId = -1, previousAnswer = ""):
        if previousQuestionId == -1:
            return 0, "Что вас беспокоит?"
        elif previousQuestionId == 0:
            keywords = Server.find_keywords(previousAnswer.lower().split(" "), Server.AllKeyWords)
            self.doctor = Server.Doctor.detect(keywords)
            if self.doctor:
                self.questions.extend(self.doctor.get_questions())
        if previousQuestionId < len(self.questions):
            return previousQuestionId + 1, self.questions[previousQuestionId]
        else:
            if self.doctor is None:
                return -2, "Большое спасибо за ваше обращение!"
            return -2, self.doctor.say()
    def getQuestionsHistory(self):
        return self.questions

class Dialog(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.questionPlayer = QuestionPlayer()
        self.answerRecognizer = AnswerRecognizer(16000, "ru-RU")
        self.server = Server()
        self.answerRecognizerThread = QThread()
        self.answerRecognizer.moveToThread(self.answerRecognizerThread)

        def quitThread():
            print("quit thread")
            self.close()
            self.answerRecognizerThread.terminate()

        parent.aboutToQuit.connect(quitThread)
        self.answerRecognizer.answerChanged.connect(lambda answer: self.handleAnswer(answer))
        self.answerRecognizer.answerFinalize.connect(lambda: self.finalizeAnswer())
        self.answerRecognizer.loudnessChanged.connect(lambda loudness: self.setMicLoudness(loudness))
        self.answerRecognizerThread.start()
        self.dialogStrategy = DialogStrategy(parent=self)
        self._model = DialogModel()
        self._inProcess = False
        self._micLoudness = 0
        self.lastQuestionId = -1
        self.patient = None
        self.lastAnswer = ""
        self.userAnswers = []

    micLoudnessChanged = pyqtSignal()
    @pyqtProperty('float', notify=micLoudnessChanged)
    def micLoudness(self):
        return self._micLoudness

    def setMicLoudness(self, loudness):
        self._micLoudness = loudness
        self.micLoudnessChanged.emit()

    modelChanged = pyqtSignal()
    @pyqtProperty('QVariant', notify=modelChanged)
    def model(self):
        return self._model

    inProcessChanged = pyqtSignal()
    @pyqtProperty(bool, notify=inProcessChanged)
    def inProcess(self):
        return self._inProcess

    @pyqtSlot('QString')
    def handleAnswer(self, answer):
        self._model.modifyResponse(answer)
        self.lastAnswer = answer

    @pyqtSlot()
    def finalizeAnswer(self):
        self.userAnswers.append(self.lastAnswer)
        self.nextAction()

    @pyqtSlot()
    def startDialog(self):
        self._inProcess = True
        self.inProcessChanged.emit()
        self.patient = Server.Client("Василий Пупкин", 30)
        self.dialogStrategy.init(self.patient)
        self.nextAction()

    @pyqtSlot()
    def nextAction(self):
        question = self.dialogStrategy.determineNextQuestion(self.lastQuestionId, self.lastAnswer)
        self.lastQuestionId = question[0]
        def finishCallback():
            if question[0] == -2:
                print(self.patient.create_history(self.userAnswers[0],
                                                  self.dialogStrategy.doctor,
                                                  self.dialogStrategy.getQuestionsHistory(),
                                                  self.userAnswers[1:]))
                return
            self.recognizeAnswer()
        self.questionPlayer.playQuestionAudio(question[1], lambda: self._model.addQuestion(question[1]), finishCallback)


    @pyqtSlot()
    def stopDialog(self):
        self._inProcess = False
        self.inProcessChanged.emit()
        self._model.clear()

    @pyqtSlot()
    def modifyAnswer(self, answer):
        self._model.modifyResponse(answer)

    @pyqtSlot()
    def recognizeAnswer(self):
        self._model.addResponse("")
        self.answerRecognizer.startRecognition()

    @pyqtSlot()
    def close(self):
        self.answerRecognizer.close()
