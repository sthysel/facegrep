import cv2 as cv
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image

 
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.button import MDRectangleFlatButton

from datetime import datetime

class KivyCamera(Image):
    def __init__(self, capture, **kwargs):
        super().__init__(**kwargs)
        self.capture = capture

    def update(self, dt):
        face_cascade = cv.CascadeClassifier(
            "haarcascades/haarcascade_frontalface_default.xml")

        ret, frame = self.capture.read()
        if ret:
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            for (x, y, w, h) in faces:
                cv.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (255, 0, 0),
                    2,
                )

            # convert frame to texture
            buf1 = cv.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]),
                colorfmt='bgr',
            )
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture = image_texture


class ScreenShotButton(MDRectangleFlatButton):
    def __init__(self, text='Screen Shot'):
        super().__init__(text=text)

    def update(self, dt):
        self.size[0] = self.parent.size[0] - 10
        self.pos[0] = 5
        self.pos[1] = 5


class CamApp(MDApp):
    def build(self):
        self.parent = BoxLayout(orientation='vertical')

        self.capture = cv.VideoCapture(0)
        self.my_camera = KivyCamera(capture=self.capture)
        self.parent.add_widget(self.my_camera)
        
        # Button Setup
        self.shot_btn = ScreenShotButton()
        self.shot_btn.bind(on_release=self.screen_shot)
        self.parent.add_widget(self.shot_btn)

        # Setup Update
        fps = 30
        Clock.schedule_interval(self.update, 1.0 / fps)
        return self.parent

    def update ( self, dt ):
        self.my_camera.update(dt)
        self.shot_btn.update(dt)


    def screen_shot(self, obj):
        # Finds the number to add after name.
        name = "face"
        datename = datetime.now().strftime('%H_%M_%S_%d_%m_%Y.log')
        # saves file
        self.my_camera.export_to_png(name + datename + ".png")


    def on_stop(self):
        self.capture.release()



if __name__ == '__main__':
    CamApp().run()
