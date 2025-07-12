from twisted.internet import reactor, protocol
from twisted.protocols import basic
import logging

# Set up logging
logging.basicConfig(filename='honeypot.log', level=logging.INFO, format='%(asctime)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

class HoneypotProtocol(basic.LineReceiver):
    def connectionMade(self):
        client_ip = self.transport.getPeer().host
        logging.info(f"Connection from {client_ip}")
        self.sendLine(b"Welcome to the honeypot! Unauthorized access is prohibited.")

    def lineReceived(self, line):
        client_ip = self.transport.getPeer().host
        logging.info(f"Received from {client_ip}: {line.decode('utf-8')}")
        self.sendLine(b"Command received. This incident will be reported.")

    def connectionLost(self, reason):
        client_ip = self.transport.getPeer().host
        logging.info(f"Connection lost from {client_ip}")

class HoneypotFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return HoneypotProtocol()

if __name__ == "__main__":
    port = 2222  # Port to listen on
    reactor.listenTCP(port, HoneypotFactory())
    logging.info(f"Honeypot running on port {port}")
    reactor.run()

