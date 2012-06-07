class Status(object):

    OFFLINE = (1, 'offline')
    ONLINE = (2, 'online')
    AWAY = (3, 'away')

    @classmethod
    def all(cls):
        return (
            cls.OFFLINE,
            cls.ONLINE,
            cls.AWAY,
        )
