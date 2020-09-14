import cv2 as cv
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image


class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super().__init__(**kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

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


class CamApp(App):
    def build(self):
        self.capture = cv.VideoCapture(0)
        self.my_camera = KivyCamera(capture=self.capture, fps=30)
        return self.my_camera

    def on_stop(self):
        self.capture.release()


if __name__ == '__main__':
    CamApp().run()
