from typing import Any, Callable
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject, QRunnable, QThread


__all__ = ("Thread", "Runnable")


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, func: Callable[..., Any], *args, **kwargs) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        try:
            self.func(*self.args, **self.kwargs)
        except Exception:
            pass
        self.finished.emit()


class Thread(QThread):
    def __init__(self, func: Callable[..., Any], *args, **kwargs) -> None:
        QThread.__init__(self)
        self.worker = Worker(func, *args, **kwargs)
        self.worker.moveToThread(self)
        self.started.connect(self.worker.run)


class Runnable(QRunnable):
    def __init__(self, func: Callable[..., Any], *args, **kwargs) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self) -> None:
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            pass
