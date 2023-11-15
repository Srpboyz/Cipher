from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from .splitter import VSplitter
from .extensionlist import ExtensionList
from .git import Git
from .search import GlobalSearch

if TYPE_CHECKING:
    from .window import Window

__all__ = ("Sidebar",)


class Sidebar(QFrame):
    def __init__(self, window: Window) -> None:
        super().__init__(window)
        self.setObjectName("Sidebar")
        self._window = window
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(5, 10, 5, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter
        )
        self.createFolder()
        self.createExtensionList()
        self.createSearch()
        self.createGitList()
        self.createSettings()
        self.setLayout(self._layout)

    @property
    def window(self) -> Window:
        return self._window

    def createFolder(self) -> None:
        folder = QLabel()
        folder.setPixmap(
            QPixmap(f"{self.window.localAppData}/icons/folder.svg").scaled(29, 29)
        )
        folder.setContentsMargins(3, 0, 0, 4)
        folder.enterEvent = lambda _: self.setCursor(Qt.CursorShape.PointingHandCursor)
        folder.leaveEvent = lambda _: self.setCursor(Qt.CursorShape.ArrowCursor)
        folder.mousePressEvent = self.folderMousePressEvent
        self._layout.addWidget(folder)

    def folderMousePressEvent(self, _: QMouseEvent) -> None:
        if isinstance(self._window.hsplit.widget(0), VSplitter):
            return self._window.fileSplitter.setVisible(
                not self._window.fileSplitter.isVisible()
            )
        self._window.hsplit.replaceWidget(0, self._window.fileSplitter)
        self._window.fileSplitter.setVisible(True)

    def createExtensionList(self) -> None:
        extensions = QLabel()
        extensions.setPixmap(
            QPixmap(f"{self.window.localAppData}/icons/extensions.svg").scaled(29, 29)
        )
        extensions.setContentsMargins(2, 0, 0, 0)
        extensions.enterEvent = lambda _: self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        extensions.leaveEvent = lambda _: self.setCursor(Qt.CursorShape.ArrowCursor)
        extensions.mousePressEvent = self.extensionListMousePressEvent
        self._layout.addWidget(extensions)

    def extensionListMousePressEvent(self, _: QMouseEvent) -> None:
        if isinstance(self._window.hsplit.widget(0), ExtensionList):
            return self._window.extensionList.setVisible(
                not self._window.extensionList.isVisible()
            )
        self._window.hsplit.replaceWidget(0, self._window.extensionList)
        self._window.extensionList.setVisible(True)

    def createSearch(self) -> None:
        search = QLabel()
        search.setPixmap(
            QPixmap(f"{self.window.localAppData}/icons/search.svg").scaled(26, 26)
        )
        search.setContentsMargins(4, 5, 0, 0)
        search.enterEvent = lambda _: self.setCursor(Qt.CursorShape.PointingHandCursor)
        search.leaveEvent = lambda _: self.setCursor(Qt.CursorShape.ArrowCursor)
        search.mousePressEvent = self.searchMousePressEvent
        self._layout.addWidget(search)

    def searchMousePressEvent(self, _: QMouseEvent) -> None:
        if isinstance(self._window.hsplit.widget(0), GlobalSearch):
            return self._window.search.setVisible(not self._window.search.isVisible())
        self._window.hsplit.replaceWidget(0, self._window.search)
        self._window.search.textBox.selectAll()
        self._window.search.textBox.setFocus()
        self._window.search.setVisible(True)

    def createGitList(self) -> None:
        git = QLabel()
        git.setPixmap(
            QPixmap(f"{self.window.localAppData}/icons/git.svg").scaled(32, 32)
        )
        git.setContentsMargins(1, 4, 0, 0)
        git.enterEvent = lambda _: self.setCursor(Qt.CursorShape.PointingHandCursor)
        git.leaveEvent = lambda _: self.setCursor(Qt.CursorShape.ArrowCursor)
        git.mousePressEvent = self.gitMousePressEvent
        self._layout.addWidget(git)

    def gitMousePressEvent(self, _: QMouseEvent) -> None:
        if isinstance(self._window.hsplit.widget(0), Git):
            return self._window.git.setVisible(not self._window.git.isVisible())
        self._window.hsplit.replaceWidget(0, self._window.git)
        self._window.git.setVisible(True)

    def createSettings(self) -> None:
        settings = QLabel()
        settings.setPixmap(
            QPixmap(f"{self.window.localAppData}/icons/settings.svg").scaled(31, 31)
        )
        settings.setContentsMargins(2, 5, 0, 0)
        settings.enterEvent = lambda _: self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        settings.leaveEvent = lambda _: self.setCursor(Qt.CursorShape.ArrowCursor)
        settings.mousePressEvent = self.settingsMousePressEvent
        self._layout.addWidget(settings)

    def settingsMousePressEvent(self, _: QMouseEvent = None) -> None:
        path = self._window.fileManager.settingsPath
        if not path.exists():
            return
        self._window.tabView.createTab(path)
