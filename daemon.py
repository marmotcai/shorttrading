import sys, os, time, atexit, signal

class Daemon:
    def __init__(self, pidfile):
        self.pidfile = pidfile

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)
        os.chdir('/')
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open('/tmp/test.txt', 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def delpid(self):
        os.remove(self.pidfile)
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid + '\n')

    def start(self):

        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            message = "pidfile {0} already exist." + \
                      "Daemon already running?\n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)

        self.daemonize()
        self.run()

    def stop(self):

        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile {0} does not exist." + \
                      "Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))
            return
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err.args))
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()


PID_FILE = '/tmp/testDaemon.pid'


class TestDaemon(Daemon):

    def run(self):
        while True:
            sys.stdout.write('%s:hello world\n' % (time.ctime(),))
            sys.stdout.flush()
            time.sleep(1)

if __name__ == '__main__':

    daemon = TestDaemon(PID_FILE)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print("Starting daemon...")
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print("Stopping daemon...")
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print("Restarting daemon...")
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(2)

    else:
        print("usage: {0} start|stop|restart".format(sys.argv[0]))
        sys.exit(2)