from gevent.backdoor import BackdoorServer
import gevent


def start_console():
    def run_console():
        server = BackdoorServer(('127.0.0.1', 5005),
                                banner="Hello from gevent backdoor!",
                                locals={
                                    '_process': "process"
                                })

        server.serve_forever()

    return gevent.spawn(run_console)
