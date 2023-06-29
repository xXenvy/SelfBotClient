from __future__ import annotations

from .enums import PresenceStatus, PresencePlatform, ActivityType
from .errors import InvalidStatusType


class ActivityBuilder:

    def __init__(self,
                 activity_name: str,
                 activity_type: ActivityType,
                 activity_details: str = "",
                 user_status: PresenceStatus = PresenceStatus.ONLINE,
                 user_platform: PresencePlatform = PresencePlatform.DESKTOP,
                 ):

        self.activity_name: str = activity_name
        self.activity_details: str = activity_details

        if isinstance(activity_type, ActivityType):
            self.activity_type: int = activity_type.value
        else:
            raise InvalidStatusType(ActivityType, type(activity_type))

        if isinstance(user_status, PresenceStatus):
            self.user_status: str = user_status.value
        else:
            raise InvalidStatusType(PresenceStatus, type(user_status))

        if isinstance(user_platform, PresencePlatform):
            self.user_platform: str = user_platform.value
        else:
            raise InvalidStatusType(PresencePlatform, type(user_platform))

    def __repr__(self):
        return f"<Activity(name={self.activity_name}, type={self.activity_type}, status={self.user_status})>"

