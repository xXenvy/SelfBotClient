from __future__ import annotations
from typing import Coroutine, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client

from asyncio import Task
from threading import Thread
from time import sleep


class Threads:

    def __init__(self, client: Client):
        self._client: Client = client
        self._loop = client.loop
        self._tasks: list[Task] = []

    def add_task(self, func: Coroutine, name: str) -> None:
        task: Task = self._loop.create_task(func, name=name)
        self._tasks.append(task)

    def run_until_complete(self):
        if self._loop.is_running():
            if self._client.logger._status:
                self._client.logger.debug("The main loop is already up and running. I'm waiting for it to finish.")

        while self._loop.is_running():
            sleep(1)

        for _ in self._tasks:
            self._loop.run_until_complete(_)

    def run(self):
        _thread = Thread(name=f"{self}", target=self.run_until_complete)
        _thread.start()

    def __repr__(self):
        return f"<Threads={len(self._tasks)}>"
