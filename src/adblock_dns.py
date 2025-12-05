# adblock_dns.py
import argparse
import socket
from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, QTYPE, A
import os
from hosts_store import load_blacklist, log_block

UPSTREAM = ('1.1.1.1', 53)   # cloudflare; puedes usar 8.8.8.8
BLACKLIST = None

class AdblockResolver(BaseResolver):
    def __init__(self):
        self.blacklist = load_blacklist()
    def resolve(self, request, handler):
        qname = str(request.q.qname).rstrip('.').lower()
        qtype = QTYPE[request.q.qtype]
        client = handler.client_address[0] if handler and hasattr(handler, 'client_address') else 'unknown'
        # exact match or subdomain block: check domain and its parent domains
        parts = qname.split('.')
        check = ['.'.join(parts[i:]) for i in range(len(parts))]
        for d in check:
            if d in self.blacklist:
                # return A 0.0.0.0
                reply = request.reply()
                reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=300))
                log_block(client, qname, qtype)
                return reply
        # not blocked -> forward to upstream (use system resolver via socket)
        # Simple forwarder
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(request.pack(), UPSTREAM)
            resp, _ = sock.recvfrom(4096)
            from dnslib import DNSRecord
            return DNSRecord.parse(resp)
        except Exception as e:
            # fallback: empty reply
            reply = request.reply()
            return reply
        finally:
            sock.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=53)
    args = parser.parse_args()
    resolver = AdblockResolver()
    server = DNSServer(resolver, port=args.port, address='0.0.0.0')
    print("Starting DNS server on port", args.port)
    server.start_thread()
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
