# Library of network utils abstracting from asyncio and socket internals. Designed for the simple pong game of the ENGF0002 (fall 2018) module.  

import asyncio
import argparse
import random, string, time


###################################
# Unified UDP sender and receiver #
###################################

class UdpPeer2PeerDaemon:
    
    def __init__(self, listen_port, send_port, listen_ip='127.0.0.1', send_ip='127.0.0.1'):
        self.listen_port = listen_port
        self.send_port = send_port
        self.listen_ip = listen_ip
        self.send_ip = send_ip
        self.created_tasks = []

    def process_incoming_messages(self, loop, packet_handle_function = None):
        print("Starting UDP server (on local port {})".format(self.listen_port))
        if packet_handle_function is None:
            packet_handle_function = self._only_print_incoming_packets
        listening_endpoint = loop.create_datagram_endpoint(
                lambda: FlexibleUdpServerProtocol(packet_handle_function,loop),
                local_addr=(self.listen_ip, self.listen_port))
        self.created_tasks.append(loop.create_task(listening_endpoint))
    
    async def _only_print_incoming_packets(self, data, addr):
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        await asyncio.sleep(0.2)
    
    def send(self, loop, packet_generator_function = None, sending_interval = 0):
        sending_endpoint = loop.create_datagram_endpoint(
                lambda: FlexibleUdpAsyncSenderProtocol(loop, packet_generator_function, sending_interval),
                remote_addr=(self.send_ip, self.send_port))
        self.created_tasks.append(loop.create_task(sending_endpoint))

    async def shutdown(self):
        await asyncio.gather(*self.created_tasks)
        

# Asyncio protocols used by the UdpPeer2PeerDaemon class.
# The implementation of these protocols is inspired by the UDP Echo Client and Server examples in the asyncio documentation (https://docs.python.org/3.6/library/asyncio-protocol.html)

''' Asyncio protocol followed by a UDP server applying the input packet_handle_function to each incoming data.
The packet_handle_function must be a function taking data (bytes extracted from the network) and addr (source IP and port of the received packets) as arguments. '''
class FlexibleUdpServerProtocol:
    def __init__(self, packet_handle_function, loop = None):
        self.handle_fun = packet_handle_function    # must be an async function that takes data and addr as arguments
        self.loop = loop

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        self.loop.create_task(self.handle_fun(data, addr))
        
''' Asyncio protocol for a UDP sender. The input packet_generator_function is an asynchronous generator (type async_generator) that generates data to send out. '''
class FlexibleUdpAsyncSenderProtocol:
    def __init__(self, loop, packet_generator_function, sending_interval):
        self.packet_gen = packet_generator_function
        self.loop = loop
        self.pace = sending_interval
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.loop.create_task(self.send_outgoing_data())

    async def send_outgoing_data(self):
        async for message in self.packet_gen:
            print('Sending: {}'.format(message))
            if message is None:
                continue
            self.transport.sendto(message)
            await asyncio.sleep(self.pace)
        print("Finished sending")

    def datagram_received(self, data, addr):
        print("Received:", data.decode())
        
    def error_received(self, exc):
        print('Error sending message:', exc)


#################################################
# Main -- to run and test above classes/methods #
#################################################

### Helper classes and functions ###

class RandomMessageGenerator:
    def generate(self):
        while True:
            new_msg = ''.join([random.choice(string.ascii_letters) for n in range(15)])
            yield new_msg

    async def async_generate_bytes(self, max_messages, pace):
        msgs = 0
        while msgs < max_messages:
            msg = ''.join([random.choice(string.ascii_letters) for n in range(15)])
            yield msg.encode()
            await asyncio.sleep(pace)
            msgs += 1

async def print_random_string(number_strings,pace):
    it=1
    async for msg in RandomMessageGenerator().async_generate_bytes(number_strings,pace):
        print("Iteration {}, random string {}".format(it,msg.decode()))
        it += 1
        if it > number_strings:
            break

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('receive_port', type=int, help='A required port number (int) to send packets to')
    parser.add_argument('send_port', type=int, help='A required port number (int) to receive packets from')
    parser.add_argument('message', type=str, help='A required message (string) to send')
    args = parser.parse_args()
    return (args.receive_port,args.send_port,args.message)

### Main ###

if __name__ == "__main__":
    (receive_port,send_port,message) = parse_arguments()
    loop = asyncio.get_event_loop()

    daemon = UdpPeer2PeerDaemon(receive_port,send_port)
    daemon.process_incoming_messages(loop=loop)
    daemon.send(loop=loop, packet_generator_function=RandomMessageGenerator().async_generate_bytes(5,1))

    try:
        loop.run_until_complete(
            asyncio.gather(
                print_random_string(3,4)
            )
        )
    except KeyboardInterrupt:
        pass

    loop.run_until_complete(daemon.shutdown())
    loop.close()



