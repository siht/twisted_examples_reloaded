import encodings.idna
import sys
sys.path += '.'

import async_finger

from twisted.application import service



def main(): # quitamos la construcción de los factories aquí y los centralizamos en un service
    global application
    application = service.Application("finger", uid=1, gid=1)
    options = {
        "file": "/etc/users",
        "templates": "/usr/share/finger/templates",
        "ircnick": "fingerbot",
        "ircserver": "localhost",
        "pbport": 8889,
        "ssl": "ssl=0",
    }

    ser = async_finger.makeService(options)

    ser.setServiceParent(service.IServiceCollection(application))


if __name__ == 'builtins': # cuando twistd llama a un tac el archivo se llama "builtins"
    main()
