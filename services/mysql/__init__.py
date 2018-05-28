from angler.services.mysql.database import MySqlDatabase


def factory(name, conf):
    mysql = MySqlDatabase(
        name,
        conf['url'],
    )
    return mysql

