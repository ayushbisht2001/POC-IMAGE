from PySide2.QtWidgets import QWidget, QLabel, QMainWindow,  QApplication, QStackedLayout, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout
from PySide2.QtGui import QPixmap
from PySide2.QtCore import QSize, Qt
import numpy as np
import sys
from pathlib import Path
import io
from PIL import Image, ImageCms
from PIL.ImageQt import ImageQt

def load_image(path):
    if Path(path).is_file():
        return ImageQt(path)



def convert_to_srgb(file_path):
        '''Convert PIL image to sRGB color space (if possible)'''
        img = Image.open(file_path)
        icc = img.info.get('icc_profile', '')
        if icc:
            io_handle = io.BytesIO(icc)     # virtual file
            src_profile = ImageCms.ImageCmsProfile(io_handle)
            dst_profile = ImageCms.createProfile('sRGB')
            img_conv = ImageCms.profileToProfile(img, src_profile, dst_profile)
            icc_conv = img_conv.info.get('icc_profile','')
        if icc != icc_conv:
            # ICC profile was changed -> save converted file
            img_conv.save(file_path,
                        format = 'JPEG',
                        quality = 50,
                        icc_profile = icc_conv)


class Paginator(QWidget):
    
    def __init__(self, parent,total, page_size, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.total_images = total
        self.page_size = page_size
        self.page_count = total//page_size + (1 and total%page_size) 
        
        self.current_index = 0

        self.paginator_box = QFrame(self)
        self.paginator_box.setObjectName("paginator_box")
        self.paginator_box.setLayout(QHBoxLayout())
        self._render_btns()

    
    def _render_btns(self):
        
        for count in range(self.page_count):
            btn = QPushButton(f"{count}")
            btn.setMaximumSize(QSize(30, 15))
            btn.clicked.connect(lambda int = int, count = count : self.set_current_index(count) )
            self.paginator_box.layout().addWidget(btn)
         
    
    
    def set_current_index(self, index):

        self.current_index = index
        self.parent.update_page()
      






class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Gallery")
        self.resize(1326, 720)
        self.container = QFrame(self)
        self.container.setLayout(QVBoxLayout())
        self.image_container = QWidget()
        self.image_container.setLayout(QGridLayout())
        self.image_container.setObjectName("image_container")
        self.paginator = Paginator(self, 1000, 100)
        self.paginator.setFixedSize(QSize(1326, 40))
        self.paginator.setStyleSheet("""
        QFrame#paginator_box{
        background-color : grey; border : 2px solid black; border-radius : 8px;
        
        }
        """)
        self.container.layout().addWidget(self.paginator)
        self.container.layout().addWidget(self.image_container)
        self.image_container.setFixedSize( 1326 ,680)
        self.image_container.setStyleSheet("""
            QWidget#image_container{
                background : #ECF2FF;
            }
        """)
        self._render_images()
        self.setCentralWidget(self.container)
        self.image_list = [  [ None  for col in range(10) ] for row in range(10)  ]

    def _render_images(self):
        
        for row in range(10):
            for col in range(10):
                img = None
                try:
                    img_path = self.paginator.current_index*self.paginator.page_size
                    img = self.image_list[row][col]
                    if not img:
                        raise ValueError
                except Exception as e:
                    img = QLabel()
                    
                rv = np.random.choice(np.arange(0, 2), p=[0.5, 0.5])
                img_pm = QPixmap(f"sample{rv}.jpg")
                img.setPixmap(img_pm.scaled(100, 100, Qt.KeepAspectRatio))
                self.image_container.layout().addWidget(img, row, col )
            # print(img_path, end=" , ")           

    def update_page(self):
        self._render_images()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


