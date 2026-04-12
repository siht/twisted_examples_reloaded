
import sys

from twisted.internet import defer, task


async def main(reactor):
    await defer.Deferred()


task.react(lambda *a: defer.ensureDeferred(main(*a)), sys.argv[1:])
                  