import sys
import dbm

def perform(args):
    domain_db = dbm.open(args.domain_db, 'c', 0o600)
    if args.get:
        print(domain_db[args.get])
    elif args.put:
        domain_db[args.put[0]] = args.put[1]
    elif args.delete:
        del domain_db[args.delete]
    elif args.unload:
        for k in list(domain_db.keys()):
            print('%s\t%s' % (k, domain_db[k]))
        # Should work according to documentation, but doesn't
        # for k, v in DOMAIN_DB.iteritems():
        #     print k, '\t', v
    elif args.load:
        for line in sys.stdin:
            k, v = line.rstrip('\r\n').split('\t', 1)
            domain_db[k] = v
    domain_db.close()

# vim: tabstop=8 softtabstop=0 expandtab shiftwidth=4
