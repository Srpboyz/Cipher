from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path
from functools import singledispatchmethod
import json
import sys
import os

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenuBar, QMenu

if TYPE_CHECKING:
    from ..window import Window

__all__ = ("Menubar",)


class Menubar(QMenuBar):
    """The window menubar

    Parameters
    ----------
    window: :class:`Window`
        The window
    """

    def __init__(self, window: Window) -> None:
        super().__init__()
        self.setObjectName("Menubar")
        self._window = window
        self._menus: set[QAction] = set()
        self.createFileMenu()
        self.createEditMenu()
        self.createViewMenu()

        self.window.shortcut.fileChanged.connect(self.updateShortcuts)
        self.updateShortcuts()

    @property
    def window(self) -> Window:
        return self._window

    @singledispatchmethod
    def addMenu(self, name: str) -> QMenu:
        menu = super().addMenu(name)
        self._menus.add(menu)
        return menu

    @addMenu.register
    def _(self, menu: QMenu) -> QAction:
        self._menus.add(menu)
        return super().addMenu(menu)

    def removeMenu(self, menu: QMenu) -> None:
        self.removeAction(menu.menuAction())
        self._menus.discard(menu)

    def createFileMenu(self) -> None:
        """Create the file menu box"""
        fileMenu = self.addMenu("File")

        saveFile = fileMenu.addAction("Save File")
        saveFile.triggered.connect(
            lambda: (
                self._window.currentFile.saveFile() if self._window.currentFile else ...
            )
        )

        saveAs = fileMenu.addAction("Save File As")
        saveAs.triggered.connect(
            lambda: (
                self._window.currentFile.saveAs() if self._window.currentFile else ...
            )
        )

        fileMenu.addSeparator()

        newFile = fileMenu.addAction("New File")
        newFile.triggered.connect(self._window.fileManager.createFile)

        newFolder = fileMenu.addAction("New Folder")
        newFolder.triggered.connect(self._window.fileManager.createFolder)

        fileMenu.addSeparator()

        openFile = fileMenu.addAction("Open File")
        openFile.triggered.connect(self._window.fileManager.openFile)

        openFile = fileMenu.addAction("Open File Path")
        openFile.triggered.connect(self._window.fileManager.openFilePath)

        reopen = fileMenu.addAction("Reopen Closed Tab")
        reopen.triggered.connect(self._window.tabView.reopenTab)

        openFolder = fileMenu.addAction("Open Folder")
        openFolder.triggered.connect(self._window.fileManager.openFolder)

        openFolderTreeView = fileMenu.addAction("Open Folder in Tree View")
        openFolderTreeView.triggered.connect(self.window.fileManager.openFolderTreeView)

        closeFolder = fileMenu.addAction("Close Folder")
        closeFolder.triggered.connect(self._window.fileManager.closeFolder)

    def createEditMenu(self) -> None:
        """Creates the edit menu box"""
        editMenu = self.addMenu("Edit")

        copy = editMenu.addAction("Copy")
        copy.triggered.connect(
            lambda: self._window.currentFile.copy() if self._window.currentFile else ...
        )

        cut = editMenu.addAction("Cut")
        cut.triggered.connect(
            lambda: self._window.currentFile.cut() if self._window.currentFile else ...
        )

        paste = editMenu.addAction("Paste")
        paste.triggered.connect(
            lambda: (
                self._window.currentFile.paste() if self._window.currentFile else ...
            )
        )

        find = editMenu.addAction("Find")
        find.triggered.connect(
            lambda: self._window.currentFile.find() if self._window.currentFile else ...
        )
        editMenu.addSeparator()

        styles = editMenu.addAction("Styles")
        styles.triggered.connect(
            lambda: self._window.tabView.createTab(
                Path(os.path.join(self.window.localAppData, "styles", "styles.qss"))
            )
        )

        shortcut = editMenu.addAction("Shortcuts")
        shortcut.triggered.connect(
            lambda: self._window.tabView.createTab(
                Path(os.path.join(self.window.localAppData, "shortcuts.json"))
            )
        )

        globalSettings = editMenu.addAction("Global Settings")
        globalSettings.triggered.connect(self.editGlobalSettings)

        workspaceSettings = editMenu.addAction("Workspace Settings")
        workspaceSettings.triggered.connect(self.editWorkspaceSettings)

        editRunFile = editMenu.addAction("Run Settings")
        editRunFile.triggered.connect(self.editRunFile)

    def editGlobalSettings(self) -> None:
        """Opens the global settings as a tab to edit"""
        self._window.tabView.createTab(
            Path(os.path.join(self.window.localAppData, "settings.cipher"))
        )

    def editWorkspaceSettings(self) -> None:
        """Opens the workspace settings as a tab to edit.
        If a workspace isn't opened, the global settings will open instead"""
        if not self._window.currentFolder:
            return self.editGlobalSettings()
        self._window.tabView.createTab(
            Path(os.path.join(self.window.currentFolder, ".cipher", "settings.cipher"))
        )

    def editRunFile(self) -> None:
        """Opens the run.bat or run.sh to edit"""
        if not self._window.currentFolder:
            return
        if sys.platform == "win32":
            path = Path(os.path.join(self.window.currentFolder, ".cipher", "run.bat"))
        else:
            path = Path(os.path.join(self.window.currentFolder, ".cipher", "run.sh"))
        self._window.tabView.createTab(path)

    def createViewMenu(self) -> None:
        """Creates the view menu box"""
        view = self.addMenu("View")

        view.addAction("Fullscreen").triggered.connect(
            lambda: (
                self.window.showFullScreen()
                if not self.window.isFullScreen()
                else self.window.showMaximized()
            )
        )
        view.addAction("Explorer").triggered.connect(self.explorer)
        view.addAction("Logs").triggered.connect(self.logs)
        view.addAction("Close Editor").triggered.connect(
            self._window.tabView.closeCurrentTab
        )

    def explorer(self) -> None:
        """Opens or closes the :class:`sidebar.Explorer`"""
        widget = self._window.hsplit.widget(0)
        visible = not widget.isVisible()
        widget.setVisible(visible)
        widget.setFocus() if visible else ...

    def logs(self) -> None:
        outputView = self.window.outputView
        if not outputView.isHidden() and outputView.currentWidget() == self.window.logs:
            return outputView.hide()
        outputView.show()
        outputView.setCurrentWidget(self.window.logs)

    def updateShortcuts(self) -> None:
        """Updates the shortcuts when `shortcuts.json` updates"""
        with open(os.path.join(self.window.localAppData, "shortcuts.json")) as f:
            shortcuts = json.load(f)
        for menu in self._menus:
            for action in menu.actions():
                if not (name := action.text()):
                    continue
                action.setShortcut(shortcuts.get(name, ""))
