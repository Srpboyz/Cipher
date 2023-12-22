from __future__ import annotations
from typing import Any, TYPE_CHECKING

from PyQt6.QtCore import QObject, pyqtSignal
from .event import Event

if TYPE_CHECKING:
    from cipher import Window

__all__ = ("Extension",)


class AsyncMixin(type):
    async def __call__(cls, *args, **kwargs):
        self = cls.__new__(cls, *args, **kwargs)
        await self.__init__(*args, **kwargs)
        return self


class ExtensionMeta(type):
    __events__: list[Event]

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        events = []
        for base in reversed(self.__mro__):
            for value in base.__dict__.values():
                if isinstance(value, Event):
                    events.append(value)
        self.__events__ = events
        return self


class ExtensionCore(type(QObject), ExtensionMeta, AsyncMixin):
    ...


class Extension(QObject, metaclass=ExtensionCore):
    __events__: list[Event] = []
    ready = pyqtSignal()

    def __new__(cls, *args, **kwargs):
        self = super(Extension, cls).__new__(cls)
        for event in self.__events__:
            event._instance = self

        return self

    def __init__(self, window: Window) -> None:
        super().__init__(parent=window)
        self.window = window
        self.isReady = False

    def prepare(self) -> None:
        self.isReady = True
        self.ready.emit()

    def unload(self) -> Any:
        ...
