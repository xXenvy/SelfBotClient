from __future__ import annotations

from typing import Coroutine, TYPE_CHECKING, Optional

from asyncio import Task
import threading
from time import sleep

if TYPE_CHECKING:
    from .client import Client


class Tasks:
    """
    :class:`Tasks` Allows you to run several methods simultaneously with tasks.

    :param client: Client object to obtain main program loop
    """

    def __init__(self, client: Client) -> None:
        self._client: Client = client
        self._loop = client.loop
        self._tasks: list[Task] = []

    def add_task(self, func: Coroutine, name: str) -> None:
        """
        The add_task function adds a task to the list of tasks.

        :param func: Asynchronous function to execute
        :param name: Give the task a unique name
        """

        task: Task = self._loop.create_task(func, name=name)
        self._tasks.append(task)

    def remove_task(self, name: str) -> None:
        """
        The remove_task function removes a task from the list of tasks.

        :param name: Specify the name of the task to be removed
        """

        for task in self._tasks:
            if task.get_name() == name:
                self._tasks.remove(task)

    def get_task(self, name: str) -> Optional[Task]:
        """
        The get_task function returns a task object from the list of tasks.

        :param name: Specify the name of the task to be returned
        """

        for task in self._tasks:
            if task.get_name() == name:
                return task
        return None

    def run_until_complete(self) -> None:
        """
        The run_until_complete function is used to run a task until it's complete.
        This function will also wait for the main loop to finish before executing any of its tasks.
        """

        if self._loop.is_running():
            if self._client.logger._status:
                self._client.logger.debug("The main loop is already up and running. I'm waiting for it to finish.")

        while self._loop.is_running():
            sleep(1)

        for _ in self._tasks:
            self._loop.run_until_complete(_)

        self._tasks: list[Task] = []

    def run(self) -> None:
        """
        The run function is a wrapper for the run_until_complete function.
        It starts a new thread and runs the run_until_complete function in that thread
        without waiting for all tasks to be completed
        """

        _thread = threading.Thread(name=f"{self}", target=self.run_until_complete)
        _thread.start()

    def __repr__(self) -> str:
        return f"<Thread={len(self._tasks)}>"
