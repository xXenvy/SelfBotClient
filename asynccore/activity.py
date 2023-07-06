from __future__ import annotations

from .enums import ActivityPlatform, ActivityStatus, ActivityType
from .errors import InvalidStatusType


class ActivityBuilder:
    """
    ActivityBuilder allows you to configure the activity.
    The finished object should be specified in the **activity** argument in the :class:`asynccore.client.Client` class.


    :param activity_name: Set the name of the activity
    :param activity_type: Set the activity type
    :param activity_details: Display the name of the game you are playing
    :param user_status: Set the user status
    :param user_platform: Set the platform that the user is using
    """

    def __init__(self,
                 activity_name: str,
                 activity_type: ActivityType,
                 activity_details: str = "",
                 user_status: ActivityStatus = ActivityStatus.ONLINE,
                 user_platform: ActivityPlatform = ActivityPlatform.DESKTOP,
                 ):
        self.activity_name: str = activity_name
        self.activity_details: str = activity_details

        if isinstance(activity_type, ActivityType):
            self.activity_type: int = activity_type.value
        else:
            raise InvalidStatusType(ActivityType, type(activity_type))

        if isinstance(user_status, ActivityStatus):
            self.user_status: str = user_status.value
        else:
            raise InvalidStatusType(ActivityStatus, type(user_status))

        if isinstance(user_platform, ActivityPlatform):
            self.user_platform: str = user_platform.value
        else:
            raise InvalidStatusType(ActivityPlatform, type(user_platform))

    def __repr__(self):
        return f"<Activity(name={self.activity_name}, type={self.activity_type}, status={self.user_status})>"
