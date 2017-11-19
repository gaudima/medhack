import re


class Server:
    class Person:
        identifier = 0

        def __init__(self, name, age):
            self.name = name
            self.age = age
            self.id = self.identifier
            self.identifier += 1

    class Doctor(Person):
        all_doctors = []
        number = 0

        def __init__(self, name, age, key_words, category, questions):
            super().__init__(name, age)
            self.keyWords = key_words
            self.category = category
            self.questions = questions
            self.all_doctors += [self]
            self.number += 1

        @staticmethod
        def detect(symptoms):
            best_doctor = -1
            index = -1
            for i in range(len(symptoms)):
                if symptoms[i] > best_doctor:
                    best_doctor = symptoms[i]
                    index = i
            if index == -1:
                return None
            return Server.Doctor.all_doctors[index]

        def say(self):
            return 'Большое спасибо за обращение в нашу систему. По вашей проблеме вам поможет ' + self.category + \
                   ', доктор ' + self.name

        def get_questions(self):
            return self.questions

    class Client(Person):
        def __init__(self, name, age):
            super().__init__(name, age)
            self.history = []

        def create_history(self, req, doctor, questions, answers):
            temp = Server.History(doctor, req, Server.Dialog(questions, answers))
            self.history.append(temp)
            return temp

        def getHistory(self):
            return self.history

    class History:
        def __init__(self, doc, req, dia):
            self.doctor = doc
            self.request = req
            self.dialog = dia

        def print(self):
            return

    class Dialog:
        def __init__(self, questions, answers):
            self.questions = questions
            self.answers = answers

    c_q = ['У вас повышенное давление?', 'Случаются ли у вас боли в груди?',
           'Принимали ли вы какие-нибудь препараты для купирования боли?', 'Какую боль вы ощущаете?',
           'У вас есть хронические болезни сердца?']
    g_q = ['Какой у вас стул?', 'Есть ли боли в животе?', 'Случались ли за последнее время вздутия живота?',
           'Была ли за последнее время рвота?', 'Была ли за последнее время изжога?']
    e_q = ['Есть ли у Вас сухость во рту?', 'Испытываете ли жажду воды?', 'Замечаете ли Вы снижение памяти?',
           'Успытываете ли Вы повышенную потливость', 'Успытываете ли Вы дрожь в руках?']
    l_q = ['Хорошо ли вы слышите?', 'Больно ли Вам глотать?', 'Есть ли у Вас насморк?']

    c_k = ['сердцебиени', 'кардиолог', 'сердце', 'сердечн', 'недостаточност', "давлени", "повышенн", "пониженн",
           "высок",
           "низк"]
    g_k = ['живот', 'понос', "диабет", "эндокринолог",
           "щитовидная", "железа", "тошнит", "сахарный", "ожирение", 'жир']
    e_k = ['отек', 'сон|cна', 'устал', 'диабет', 'дрож', 'сухость|сух', 'кож']
    l_k = ['кашель|кашл', 'мокрот', 'кровохаркань', 'харка' 'уши|ух', 'горл', 'нос', 'сопл' 'заложен', 'одышк', 'удушь']

    common_questions = ['Как долго вы болеете?']

    cardiolog = Doctor("I.V. Smirnov", 45, c_k, 'Кардиолог', c_q)
    gastroenterolog = Doctor("А. Чехов", 42, g_k, 'Гастроэнтеролог', g_q)
    endokrinolog = Doctor("И. Курагин", 40, e_k, 'Эндокринолог', e_q)
    lor = Doctor("Н. Носов", 35, l_k, 'ЛОР', l_q)

    AllKeyWords = [x.keyWords for x in Doctor.all_doctors]

    clients = [{'name': 'Joe', 'age': 15,
                'history': [{'doctor': '', 'request': '', 'dialogs': [{'question': '', 'answer': ''}]}]
                }]

    @staticmethod
    def find_keywords(input_array, keywords_array):
        # разбиваем строку на отдельные слова
        found = []
        count = [0] * len(keywords_array)

        # перебираем каждое слово
        for input_array_i in input_array:
            # смотрим совпадение с нашими ключевыми словами
            for i in range(len(keywords_array)):
                for keyWord in keywords_array[i]:
                    # if keyWord == input_array_i:
                    #     # добавляем в массив найденных, если совпали
                    #     found.append(input_array_i)
                    #     count[i] += 1
                    if re.match(keyWord, input_array_i):
                        count[i] += 1
        return count

    @staticmethod
    def filter_diseases(input_arr, diseases):
        result = []
        for elem in input_arr:
            if elem in diseases:
                result.append(elem)
        return result

    @staticmethod
    def demo(self):
        seek = self.Client("Max Krutov", 14)

        # inputStr = "школа болит ангина живот нога боль в груди сердцебиение"
        inputStr = "гормоны высокие, сердце колит"

        foundKeyWords = self.find_keywords(inputStr.split(" "), self.AllKeyWords)
        res_doctor = self.Doctor.detect(foundKeyWords)
        if (res_doctor == None):
            print("error in detect()")
        else:
            print(res_doctor.category)
            questions = res_doctor.get_questions()
            print(questions)
            answers = []  # from dimon
            print(seek.create_history(inputStr, res_doctor, questions, answers))

    @staticmethod
    def _main(input_str):
        input_arr = input_str.split(" ")
        foundKeyWords = Server.find_keywords(input_arr, Server.AllKeyWords)
