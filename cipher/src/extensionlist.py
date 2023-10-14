from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QMessageBox

if TYPE_CHECKING:
    from .window import MainWindow


__all__ = ("ExtensionItem", "ExtensionList")


class ExtensionItem(QListWidgetItem):
    __slots__ = ("name", "path")

    def __init__(self, name: str, icon: str, path: Path, enabled: bool = False) -> None:
        super().__init__()
        self.name = name
        self.path = path

        self.setIcon(QIcon(icon))
        self.setText(f"{name} (Loading)" if enabled else f"{name} (Disabled)")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class ExtensionList(QListWidget):
    """The list view of all :class:`Extension`

    Parameters
    ----------
    window: :class:`MainWindow`

    Attributes
    ----------

    """

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.setObjectName("ExtensionList")
        self._window = window
        self.setMaximumWidth(self.screen().size().width() // 2)
        self.itemClicked.connect(lambda item: window.tabView.createTab(item.path))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.createContextMenu()
        self.customContextMenuRequested.connect(
            lambda pos: self.menu.exec(self.viewport().mapToGlobal(pos))
        )

    @property
    def window(self) -> MainWindow:
        return self._window

    def createContextMenu(self):
        self.menu = QMenu(self._window)
        self.menu.setObjectName("ExtensionContextMenu")
        enabledisable = self.menu.addAction("Enable/Disable")
        enabledisable.triggered.connect(self.enabledisable)

    def selectedItems(self) -> List[ExtensionItem]:
        return super().selectedItems()

    def enabledisable(self) -> None:
        index = self.selectedItems()
        if not index:
            return
        index = index[0]
        with open(index.path) as f:
            data = json.load(f)
        with open(index.path, "w") as f:
            data["enabled"] = not data["enabled"]
            json.dump(data, f, indent=4)

        if data["enabled"]:
            index.setText(f"{index.name} (Reload Required)")
            box = QMessageBox(self)
            box.setWindowTitle("Extension")
            box.setText(
                "You need to reload the window to reload the extension. Continue?"
            )
            box.exec()
        else:
            self.window.removeExtension(index.name)
            index.setText(f"{index.name} (Disabled)")
