import sys
from PySide6.QtCore import (
    QUrl, QTimer, Slot
    )
from PySide6.QtWidgets import *
from PySide6.QtMultimedia import (QAudio, QAudioOutput, QMediaFormat,
                                  QMediaPlayer)
from PySide6.QtMultimediaWidgets import QVideoWidget

from utils import io_utils

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._proj_tree = io_utils.ProjectTree('../projects')

        # -- File management widgets --
        self._project_browser = QComboBox()
        self._project_browser.addItems([project.get_name() for project in\
            self._proj_tree.get_projects()])

        self._project_browser.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self._project_browser.currentIndexChanged.connect(self._project_selection_change)

        self._file_browser = QListWidget()
        self._update_file_browser(0)
        self._file_browser.currentRowChanged.connect(self._file_selection_change)

        # -- Multimedia widgets --
        self._audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)
        self._video_widget = QVideoWidget()
        self._player.setVideoOutput(self._video_widget)
        # --

        # -- Layout widgets --
        self._window_main = QWidget()
        self._groupbox_files = QGroupBox("Projects and Files")
        self._sp_files = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        #self._sp_files.setHorizontalStretch(1)
        self._groupbox_files.setSizePolicy(self._sp_files)

        self._window_cutting = QWidget()
        self._sp_cutting = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        #self._sp_cutting.setHorizontalStretch(5)
        self._window_cutting.setSizePolicy(self._sp_cutting)

        self._window_scripts = QWidget()

        self._layout_outer = QHBoxLayout(self._window_main)
        self._layout_files = QVBoxLayout(self._groupbox_files)
        self._layout_cutting = QVBoxLayout(self._window_cutting)
        self._layout_scripts = QHBoxLayout(self._window_scripts)

        self._layout_outer.setContentsMargins(5, 5, 5, 5)
        self._layout_files.setContentsMargins(5, 5, 5, 5)
        self._layout_cutting.setContentsMargins(5, 5, 5, 5)
        self._layout_scripts.setContentsMargins(5, 5, 5, 5)
        
        self._groupbox_files.setLayout(self._layout_files)

        self._layout_outer.addWidget(self._groupbox_files)
        self._layout_outer.addWidget(self._window_cutting)

        self._layout_files.addWidget(self._project_browser)
        self._layout_files.addWidget(self._file_browser)

        self._layout_cutting.addWidget(self._video_widget)
        self._layout_cutting.addWidget(self._window_scripts)

        self.setCentralWidget(self._window_main)
        # --

        #self._player.play()

    def _project_selection_change(self, index):
        self._update_file_browser(index)

    def _update_file_browser(self, index):
        self._file_browser.clear()
        self._proj_tree.update_tree()
        selected_project = self._proj_tree.get_projects()[index]
        file_list = selected_project.get_media('video/mp4/raw').get_file_names()
        self._file_browser.addItems(file_list)

    def _file_selection_change(self, index):
        if index < 0:
            self._player.stop()
        else:
            project_index = self._project_browser.currentIndex()
            video_media = self._proj_tree.get_projects()[project_index].get_media('video/mp4/raw')
            video_path = video_media.get_file_paths()[index]
            self._player.setSource(QUrl.fromLocalFile(video_path))
            self._player.play()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    available_geometry = main_win.screen().availableGeometry()
    main_win.resize(available_geometry.width() / 1.5,
                    available_geometry.height() / 1.5)
    main_win.show()
    sys.exit(app.exec())