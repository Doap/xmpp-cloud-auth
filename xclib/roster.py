import hashlib
import logging
import traceback
import threading
import sys
from xclib.roster_thread import roster_thread
from xclib.utf8 import utf8
from xclib.check import assertEqual

class roster(roster_thread):
    def jidsplit(self, jid):
        '''Split jid into lhs@rhs'''
        (node, at, dom) = jid.partition('@')
        if at == '':
            return (node, self.domain)
        else:
            return (node, dom)

    def roster_cloud(self):
        '''Query roster JSON from cloud'''
        success, code, message, text = self.verbose_cloud_request({
            'operation': 'sharedroster',
            'username':  self.username,
            'domain':    self.authDomain
        })
        if success:
            if code is not None and code != requests.codes.ok:
                return code, None
            else:
                sr = None
                try:
                    sr = message['data']['sharedRoster']
                    return sr, text
                except Exception as e:
                    logging.warn('Weird response: ' + str(e))
                    return message, text
        else:
            return False, None

    def try_roster(self, async=True):
        '''Maybe update roster'''
        if (self.ctx.ejabberdctl_path is not None):
            try:
                response, text = self.roster_cloud()
                if response is not None and response != False:
                    texthash = hashlib.sha256(text.encode('utf-8')).hexdigest()
                    userhash = utf8('RH:' + self.username + ':' + self.domain)
                    # Response changed or first response for that user?
                    if not userhash in self.ctx.shared_roster_db or self.ctx.shared_roster_db[userhash] != texthash:
                        self.ctx.shared_roster_db[userhash] = texthash
                        t = threading.Thread(target=self.roster_background_thread,
                            args=[response])
                        t.start()
                        if not async:
                            t.join() # For automated testing only
                        else:
                            # Try to do most before the user is actually logged in.
                            # Thanks to improved caching, this should rarely be noticeable
                            # and reduce the 'full names only visible on second login'
                            # problem experienced especially in Gajim (maybe a race condition?)
                            t.join(1.0)
                        return True
            except Exception as err:
                (etype, value, tb) = sys.exc_info()
                traceback.print_exception(etype, value, tb)
                logging.warn('roster_groups thread: %s:\n%s'
                             % (str(err), ''.join(traceback.format_tb(tb))))
                return False
        return True
