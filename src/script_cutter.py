import sys
from PySide6.QtCore import (
    Slot, QUrl, Qt, QStringListModel
    )
from PySide6.QtWidgets import *
from PySide6.QtMultimedia import (QAudio, QAudioOutput, QMediaFormat,
                                  QMediaPlayer)
from PySide6.QtMultimediaWidgets import QVideoWidget

from utils import io_utils
import numpy as np

# holds current script in various forms, script can be queried and edited
class ScriptModel:
    def __init__(self):
        self._script_tble = None
        self._script_html = ''

    def _script_tble_to_html(self):
        self._script_html = ''

        # empty scripts have no text
        if self._script_tble.ndim < 2:
            return

        for word in self._script_tble[1:,0]:
            self._script_html += word + ' '

        self._script_html.rstrip()

    def _get_array_index_from_cursor(self):
        pass

    def load_script(self, path):
        self._script_tble = np.loadtxt(path, delimiter=',', dtype=str)
        self._script_tble_to_html()

    def get_script_html(self):
        return self._script_html

    def mark_word_at_cursor(self, curser_pos):
        pass

    def mark_selection(self, curser_pos_1, cursor_pos_2):
        pass


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #set focus to receive keypress events
        self.setFocusPolicy(Qt.StrongFocus)

        # -- Models --
        self._proj_tree = io_utils.ProjectTree('../projects')

        self._projects_model = QStringListModel()
        proj_names = [proj.get_name() for proj in self._proj_tree.get_projects()]
        self._projects_model.setStringList(proj_names)

        self._files_model = QStringListModel()

        self._script_model = ScriptModel()
        # --
        
        # -- File management --
        self._project_browser = QComboBox()
        self._project_browser.setModel(self._projects_model)
        self._project_browser.currentIndexChanged.connect(self._project_selection_change)

        self._file_browser = QListView()
        self._file_browser.setModel(self._files_model)
        self._file_browser.selectionModel().currentRowChanged.connect(self._file_selection_change)

        # initialize listview
        self._project_selection_change(0)
        # --

        # -- Multimedia --
        self._audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)
        self._video_widget = QVideoWidget()
        self._player.setVideoOutput(self._video_widget)
        self._sp_video = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self._video_widget.setSizePolicy(self._sp_video)
        # --

        # -- Script edit widgets --
        #self._script_navigator = QTextBrowser()
        self._script_editor = QTextEdit()

        #self._script_navigator.setPlainText("Hello this is an example text.")
        self._script_editor.setReadOnly(True)
        #self._script_editor.setHtml('Hello this is an <span style="background-color:rgba(255,200,0,0.4)">example</span> text.')
        #self._script_editor.setHtml('Hello this is an example text.')
        self._script_editor.setCursor(Qt.ArrowCursor)
        self._script_editor.viewport().setCursor(Qt.ArrowCursor)
        self._sp_editor = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self._script_editor.setSizePolicy(self._sp_editor)
        self._script_editor.cursorPositionChanged.connect(self._script_cursor_change)
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
        self._sp_scripts = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self._window_scripts.setSizePolicy(self._sp_scripts)

        self._layout_outer = QHBoxLayout(self._window_main)
        self._layout_files = QVBoxLayout(self._groupbox_files)
        self._layout_cutting = QVBoxLayout(self._window_cutting)
        #self._layout_scripts = QHBoxLayout(self._window_scripts)

        self._layout_outer.setContentsMargins(5, 5, 5, 5)
        self._layout_files.setContentsMargins(5, 5, 5, 5)
        self._layout_cutting.setContentsMargins(5, 5, 5, 5)
        #self._layout_scripts.setContentsMargins(5, 5, 5, 5)
        
        self._groupbox_files.setLayout(self._layout_files)

        self._layout_outer.addWidget(self._groupbox_files)
        self._layout_outer.addWidget(self._window_cutting)

        self._layout_files.addWidget(self._project_browser)
        self._layout_files.addWidget(self._file_browser)

        self._layout_cutting.addWidget(self._video_widget)
        self._layout_cutting.addWidget(self._script_editor)
        #self._layout_cutting.addWidget(self._window_scripts)

        #self._layout_scripts.addWidget(self._script_navigator)
        #self._layout_scripts.addWidget(self._script_editor)

        self.setCentralWidget(self._window_main)
        # --

    #@Slot(int)
    def _project_selection_change(self, index):
        #self._update_file_browser(index)
        selected_project = self._proj_tree.get_projects()[index]
        file_list = selected_project.get_media('video/mp4/raw').get_file_names()
        self._files_model.setStringList(file_list)

    #@Slot(int)
    def _file_selection_change(self, q_index):
        index = q_index.row()

        if index < 0:
            self._player.stop()
        else:
            project_index = self._project_browser.currentIndex()
            video_media = self._proj_tree.get_projects()[project_index].get_media('video/mp4/raw')
            video_path = video_media.get_file_paths()[index]
            self._player.setSource(QUrl.fromLocalFile(video_path))

            script_media = self._proj_tree.get_projects()[project_index].get_media('script/full/csv')
            script_path = script_media.get_file_paths()[index]
            self._script_model.load_script(script_path)

            self._script_editor.setHtml(self._script_model.get_script_html())

            #workaround to get video player widget to show first frame of video
            self._player.play()
            self._player.pause()

    def _script_cursor_change(self):
        anchor = self._script_editor.textCursor().anchor()
        position = self._script_editor.textCursor().position()

        #print(anchor, position)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self._player.playbackState() == QMediaPlayer.PlayingState:
                self._player.pause()
            else:
                self._player.play()

        if event.key() == Qt.Key_Left:
            self._player.setPosition(self._player.position() - 1000)
        if event.key() == Qt.Key_Right:
            self._player.setPosition(self._player.position() + 1000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    available_geometry = main_win.screen().availableGeometry()
    main_win.resize(available_geometry.width() / 1.5,
                    available_geometry.height() / 1.5)
    main_win.show()
    sys.exit(app.exec())