"""                 Программа выполняет сверку по фотографии, есть ли человек в Базе.
            Позволяет сохранить фотографию человека и создать профиль с сохранением в базе данных SQL,
                            фотография при этом сохраняется в формате PICKLE.
                        Иcпользуется движок OpenCV и библиотека face_recognition.
                        Виртуальная часть воспроизведена с помощью библиеотки Qt.
                        Фотографии профиля хранятся в отдельной папке(базе), т.к
                                процесс поиска займёт меньше времени"""

import pickle
import cv2
import os
import Camera
import tableM
import face_recognition
import model

from threading import Thread
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5 import QtCore

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 890)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
cap.set(cv2.CAP_PROP_FPS, 60)

status = str()

NAME = str()
SURNAME = str()
GROUP = str()
PHOTO = str()


class Thread1(QThread):
    """Поток для воспроизведения видео в форме"""
    changePixmap = pyqtSignal(QImage)

    def __init__(self, *args, **kwargs):
        super().__init__()

    def run(self):
        while cap.isOpened():
            # print("CAM is open")
            ret1, image = cap.read()
            faces = cv2.CascadeClassifier("faces.xml")
            result = faces.detectMultiScale(image, scaleFactor=1.2, minNeighbors=6)
            for (x, y, w, h) in result:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 200), thickness=3)
                if ret1:
                    im1 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    height1, width1, channel1 = im1.shape
                    step1 = channel1 * width1
                    qImg1 = QImage(im1.data, width1, height1, step1, QImage.Format_RGB888)
                    p = qImg1.scaled(880, 530, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)


class SaveNew:
    """класс является "командным пунком" для потока сохранения и
    вывода информации о пользователе"""

    def __init__(self, name, surname, group):
        self.name = name
        self.surname = surname
        self.group = group

    def save_photo(self):
        """функция объявления и вызова потока для сохранения фотографии"""

        th = Thread3(1, self.name, self.surname, self.group)
        th.start()

    @staticmethod
    def show_profile():
        """Функция вызывает поток для выводы и обработки информации о пльзователе"""

        th = Thread4(1)
        th.start()
        th.join()


class Thread4(Thread):
    """Класс выполняет отдельным потоком поиск пользователя"""

    changePixmap = pyqtSignal(QImage)

    def __init__(self, limit):
        super().__init__()
        self._limit = limit

    def run(self):
        """Выполняется поиск пользователя по фото снятым камерой и фото из базы данных"""

        dir_images = os.listdir("Faces")
        for i in range(self._limit):
            if cap.isOpened():
                """Если камера работает - выполняется"""

                ret1, image = cap.read()  # читаем данные с камеры
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # пререводим фото в ч/б
                encodings = face_recognition.face_encodings(rgb)  # кодируем в вектор лицо
                questions = model.Profile.query.all()
                ph = str()

                flag = False  # устанавливаем флаг для поиска фото(чтобы остановить поиск при нахождении совпадения)
                for encoding in encodings:
                    for image in dir_images:
                        if flag is True:
                            continue
                        else:
                            name = image.split("_")
                            im = cv2.imread(f"Faces/{image}")
                            rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                            encod_image = face_recognition.face_encodings(rgb)
                            """matches - функция сравнения фото(лиц), возвращает True False"""
                            matches = face_recognition.compare_faces(encod_image, encoding)
                        while True in matches:
                            Camera.NAME = name[2]
                            Camera.SURNAME = name[1]
                            Camera.GROUP = name[3].split(".")[0]
                            Camera.PHOTO = image
                            Camera.status = "OK!"
                            flag = True
                            break
                    else:
                        if flag is False:
                            Camera.status = "NO PROFILE"
                            Camera.NAME = "NO NAME"
                            Camera.SURNAME = ""
                            Camera.GROUP = ""
                            Camera.PHOTO = "P_P_P_P.jpeg"
                            break


class Thread3(Thread):
    """Класс для работы с базой данных на сервере - сохряняет данные пользователя и фото в формате PICKLE"""

    def __init__(self, limit, name, surname, group):
        super().__init__()
        self._limit = limit
        self.name = name
        self.surname = surname
        self.group = group

    @staticmethod
    def save_Db(name: str, surname: str, group: str, encodings):
        """функция Записывает в Базу данных сервера (имя, фамия, группа, фото в коде PICKLE"""

        from model import db, Profile
        # NewUser = Profile(name=f"{name}", surname=f"{surname}", group=f"{group}",
        #                   photo=f"{pickle.dumps(encodings, pickle.DEFAULT_PROTOCOL)}")
        NewUser = Profile(name=f"{name}", surname=f"{surname}", group=f"{group}",
                          photo=str(encodings))
        db.session.add(NewUser)
        db.session.commit()

    def run(self):
        """сохранение фотографии(лица) для профиля с названием (Photo_Фамилия_Имя_Группа.jpeg)"""

        for i in range(self._limit):
            if cap.isOpened():
                print("Thread 3")
                ret1, image = cap.read()
                faces = cv2.CascadeClassifier("faces.xml")
                result = faces.detectMultiScale(image, scaleFactor=1.3, minNeighbors=6)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                encod_image = face_recognition.face_encodings(rgb)
                if ret1:
                    for k in range(len(result)):
                        for (x, y, w, h) in result:
                            print(f"Writing: {self.name}")
                            Camera.status = f"Запись имени: {self.name}"
                            cv2.imwrite(f"Faces/Photo_{self.surname}_{self.name}_{self.group}.jpeg",
                                        image[y - 40:y + h + 40, x:x + w])
                            Thread3.save_Db(name=self.name, surname=self.surname, group=self.group,
                                            encodings=encod_image)
                            Camera.status = "Save Ok"
                else:
                    Camera.status = "Error Save"


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = tableM.Ui_Form()
        self.ui.setupUi(self)

        self.ui.pushButton_3.clicked.connect(self.status)
        self.ui.pushButton_4.clicked.connect(self.info)
        self.ui.pushButton_4.clicked.connect(self.status)

        self.th1 = Thread1(self)
        self.th1.changePixmap.connect(self.setImage)
        self.th1.start()

    @QtCore.pyqtSlot(QImage)
    def setImage(self, qImg1):
        self.ui.label.setPixmap(QPixmap.fromImage(qImg1))
        self.ui.label_8.setPixmap(QPixmap.fromImage(qImg1))

    @QtCore.pyqtSlot()
    def status(self):
        pass
        # self.ui.label_15.setText(Camera.status)
        # self.ui.label_13.setText(Camera.status)

    def info(self):
        id_t = str()
        questions = model.Profile.query.all()
        for data in questions:
            if data.surname == f'{Camera.SURNAME}':
                id_t = data.id

        self.ui.label_5.setText(Camera.NAME)
        self.ui.label_6.setText(Camera.SURNAME)
        self.ui.label_7.setText(Camera.GROUP)

        self.ui.label_15.setText(str(f"id: {id_t}"))
        self.ui.label_13.setText(str(f"id: {id_t}"))

        self.ui.label_16.setPixmap(QPixmap(f"Faces/{Camera.PHOTO}"))
        self.ui.label_16.setScaledContents(True)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    ui = tableM.Ui_Form
    sys.exit(app.exec_())

