from ext.event import *
from ext.extension import *
from pypresence import Presence, exceptions as exec
from PyQt6.QtWidgets import QWidget
from pathlib import Path
from typing import Optional
import time
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
format = logging.Formatter("%(levelname)s:%(asctime)s:%(message)s")
fileHandler = logging.FileHandler(f"{os.path.dirname(__file__)}\\logs.log")
fileHandler.setFormatter(format)
logger.addHandler(fileHandler)


class RPC(Extension):
    def __init__(self, **kwargs) -> None:
        self._loop = kwargs.get("loop")
        self.rpc: Presence = Presence("1044002439906476063", loop=self._loop)
        self.rpc.connect()
        self.time: float = time.time()

    def update(self, folder: Optional[Path], widget: QWidget) -> None:
        if not widget:
            return
        name = widget.objectName()
        folder = folder.name if folder else None
        try:
            self.rpc.update(
                state=f"Workspace: {folder}",
                details=f"Editing {name}",
                start=self.time,
                large_image="editor",
                large_text="Cipher",
                small_text=name,
            )
        except exec.InvalidID:
            self.rpc.close()
            self.rpc = Presence("1044002439906476063", loop=self._loop)
            self.rpc.connect()
            self.rpc.update(
                state=f"Workspace: {folder}",
                details=f"Editing {name}",
                start=self.time,
                large_image="editor",
                large_text="Cipher",
            )

    @event()
    def onReady(self, folder: Optional[Path], widget: QWidget) -> None:
        self.update(folder, widget)

    @event()
    def widgetChanged(self, folder: Optional[Path], widget: QWidget) -> None:
        self.update(folder, widget)

    @event()
    def onClose(self) -> None:
        self.rpc.clear()

    @onReady.error
    def onReadyError(self, error: Exception, *args, **kwargs) -> None:
        if isinstance(error, AttributeError):
            return
        logger.error(f"RPC updateError - {error.__class__}: {error}")
        try:
            self.rpc.clear()
        except RuntimeError:
            pass

    @widgetChanged.error
    def widgetChangedError(self, error: Exception, *args, **kwargs) -> None:
        if isinstance(error, AttributeError):
            return
        if isinstance(error, exec.InvalidID):
            self.rpc.close()
            return self.rpc.connect()
        logger.error(f"RPC updateError - {error.__class__}: {error}")
        try:
            self.rpc.clear()
        except RuntimeError:
            pass

    @onClose.error
    def onCloseError(self, error: Exception, *args, **kwargs) -> None:
        logger.error(f"RPC updateError - {error.__class__}: {error}")
