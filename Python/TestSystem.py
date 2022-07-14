import time
import datetime
import psycopg2
import bcrypt

from threading import Thread, Lock


class Db:
    """Класс создания подключения с использованием Singltone"""

    __instance__ = None
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(cls)
        return cls.instance

    @staticmethod
    def get_connect():
        return psycopg2.connect(database="TestsSystem", user="", password="", host="localhost", port=5432)


class Profile:
    __slots__ = ["name", "lastname", "otch", "group", "login", "password", "age", "conn"]

    def __init__(self):
        self.conn = Db().get_connect()

    def get_profile(self, login):
        """Возвращает пароль из БД по введенному логину"""
        password = TestSystem().get_list_like("password", "profile", "login", login)
        return password

    def set_profile(self, name, lastname, group, login, password, email):
        """ полученные данные вносит в БД, проверяя существование группы"""
        curs = self.conn.cursor()
        password_hashed = bcrypt.hashpw(bytes(str(password), encoding="utf8"),
                                        bcrypt.gensalt()).decode('utf-8')

        id_group = TestSystem().get_list_like("id_group", "group", "name", group)

        if len(id_group) == 0:
            print("Такой группы нет! уточните номер группы и введите повторно данные")
            Auth().registration()
        else:
            curs.execute(f"""INSERT INTO "profile" ("name", "lastname", "id_group", "login", "password", "email") 
            VALUES ('{name}', '{lastname}', '{id_group[0][0]}', '{login}', '{password_hashed}', '{email}')""")
            self.conn.commit()


class Auth:
    """ Класс аутентификации Логин Регистрация и ЛогАут"""
    LOGIN = None
    is_auth = bool()

    def __init__(self):
        self.conn = Db.get_connect()
        self.login = None
        self.password = None

    def registration(self):
        self.login = input("login: ")

        if TestSystem().get_list_like("login", "profile", "login", self.login):
            print("Такой логин уже существует!")
            Auth().registration()

        password = input("password: ")
        name = input("name: ")
        lastname = input("lastname: ")
        group = input("group: ")
        email = input("email: ")
        Profile().set_profile(name, lastname, group, self.login, password, email)
        Auth.LOGIN = self.login
        Auth.is_auth = True

        return Auth.is_auth

    def log_in(self):
        print("Hello! Enter your:")
        self.login = input("login: ")
        self.password = input("password: ")
        prof = Profile().get_profile(self.login)
        Auth.LOGIN = self.login

        if len(prof) == 0:
            print("Такого пользователя не существует! пройдите регистрацию!")
            Auth().registration()
        else:
            tf = (bcrypt.checkpw(self.password.encode(), bytes(prof[0][0], encoding="utf8")))
            if tf is True:
                Auth.is_auth = True
                return Auth.is_auth
            else:
                print("Не верный пароль!")
                Auth().log_in()

    def logout(self):
        Auth.is_auth = False


class SaveResult:
    """ Сохранение результатов """

    def __init__(self):
        self.conn = Db().get_connect()
        self.login = Auth.LOGIN
        self.curs = self.conn.cursor()

    def save_result(self, test, d_time, result, timer):
        id_profile = TestSystem().get_list_like("id_profile", "profile", "login", self.login)
        self.curs.execute(f"""INSERT INTO "test_result" ("id_profile", "login", "dt_time", "test", "result", "tm_time") 
                VALUES ('{id_profile[0][0]}','{self.login}','{d_time}', '{test}', '{result}', '{timer}')""")
        self.conn.commit()


class Test:
    def __init__(self):
        self.conn = Db().get_connect()

    """ В классе реализуем методы работы с БД """

    def get_list_tests(self):
        """ получение списка тестов """
        curs = self.conn.cursor()
        curs.execute(""" SELECT "id_test", "theme" FROM "test" """)
        tests = curs.fetchall()
        return tests

    def get_questions(self, id_test):
        """ получение списков вопросов """
        curs = self.conn.cursor()
        curs.execute(f""" SELECT "id_question", "id_answer", "status" FROM "test_questions" 
                                WHERE "id_test" = {id_test} """)
        test = curs.fetchall()
        return test


class TestSystem:
    "Класс взаимодействует с моделью и представлением. Включает всю бизнес логику системы."
    def __init__(self):
        self.conn = Db().get_connect()
        self.curs = self.conn.cursor()
    t_out = False

    def run(self):
        """Метод реализует запуск теста"""
        while not Auth.is_auth:
            Auth().log_in()
        else:
            print(f"{Auth.LOGIN}, Вы Вошли в систему Тестирования!", "\n",
                  "Для Начала теста выберете Тему и тест начнётся!", "\n",
                  "У Вас 5 минут на решение теста")
            TestView().render()

    def get_list(self, row, table, condition, elem):
        self.curs.execute(f""" SELECT "{row}" FROM "{table}" WHERE "{condition}" = {elem} """)
        list_ = self.curs.fetchall()
        return list_

    def get_list_like(self, row, table, condition, elem):
        self.curs.execute(f""" SELECT "{row}" FROM "{table}" WHERE "{condition}" LIKE '{elem}' """)
        list_ = self.curs.fetchall()
        return list_


class View:
    """ 'Абстрактный' класс для потомков """
    def render(self):
        pass


class QuestionView(View):
    """В классе перегружаем виртуальный метод  render от родителя"""

    lock = Lock()
    stop_thread = False

    def render(self, data=None):
        """Метод реализует отрисовку вопроса с вариантами ответа и строкой выбора варианта,
        выставление необходимого времени на тест"""

        stud_result = 0
        qustions = list()
        answers = list()
        answ_t_f = list()
        list_question = Test().get_questions(data)

        for qust1, qust2, qust3 in list_question:
            qustions.append(qust1)  # вопросы
            answers.append(qust2)  # ответы
            answ_t_f.append(qust3)  # тру/фолс

        quest = sorted(set(qustions))

        k_a = len(answers) / len(quest)
        # для определения количества ответов в вопросах(ответов в вопросах равное количество)
        k = 0
        # вывод вопроса по id
        for elem in quest:
            c = 1
            test1 = TestSystem().get_list("text_question", "questions", "id_question", elem)
            for t in test1:
                print("Вопрос: ", str(t).strip("( ) , ' "))

            # вывод и чтение ответов
            for i in range(k, int(k + k_a)):
                # ans1 = TestSystem().get_list_answer(q1[i])
                ans1 = TestSystem().get_list("text_answer", "answers", "id_answer", answers[i])
                print(f"{c}. ", str(ans1[0]).strip("(),'"))
                c += 1

            stud_answer = int(input("Enter yuor answer: "))
            if answ_t_f[stud_answer - 1 + k] is True:
                stud_result += 1
            k += int(k_a)
        s_r = list()
        s_r.append(f"{stud_result} from {len(quest)}")
        return s_r

    def t_render(self, data):
        """ Метод реализует проверку времени и выставление оценки """
        st_r = list()

        d_time = datetime.datetime.now()
        t_f_time = time.time()
        th = Thread(target=(st_r.append(QuestionView().render(data))))
        th.start()
        QuestionView.lock.acquire()
        QuestionView.stop_thread = True
        QuestionView.lock.release()

        test_time = time.time() - t_f_time
        if (test_time - 10.0) < 1e-2:
            print("Поздравляю! Ваш тест завершён!", "\n" "Ваша оценка: ", str(st_r).strip("[]'"))
            SaveResult().save_result(data, d_time, st_r[0][0], test_time)
        else:
            print("Вы не сдали тест, т.к затратили больше времени на выполнение", "\n",
                  f"Но Вы ответила на {st_r[0][0]} вопросов ")
            SaveResult().save_result(data, d_time, "FALSE", test_time)

        time.sleep(2)
        Auth().logout()


class TestView(View):
    def __init__(self):
        pass

    def render(self):
        for test in Test().get_list_tests():
            print(str(test).strip("( ) , ' ").replace(", '", ". "))
        QuestionView().t_render(input("Enter number of test: "))

    # """Метод реализует отрисовку экранной формы выбора билета """


TestSystem().run()
