from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.topo import Topo
from mininet.node import Node
import time

r1_eth0 = 'r1-eth0'
r1_eth0_ip = '172.10.1.1'
r1_eth1 = 'r1-eth1'
r1_eth1_ip = '172.10.2.2'
r1_eth2 = 'r1-eth2'
r1_eth2_ip = '172.10.3.2'
r2_eth0 = 'r2-eth0'
r2_eth0_ip = '172.10.2.1'
r2_eth1 = 'r2-eth1'
r2_eth1_ip = '172.10.4.1'
r3_eth0 = 'r3-eth0'
r3_eth0_ip = '172.10.3.1'
r3_eth1 = 'r3-eth1'
r3_eth1_ip = '172.10.5.1'
r4_eth0 = 'r4-eth0'
r4_eth0_ip = '172.10.6.1'
r4_eth1 = 'r4-eth1'
r4_eth1_ip = '172.10.4.2'
r4_eth2 = 'r4-eth2'
r4_eth2_ip = '172.10.5.2'
h1_eth0 = 'h1-eth0'
h1_eth0_ip = '172.10.1.2'
h2_eth0 = 'h2-eth0'
h2_eth0_ip = '172.10.6.2'

class Router(Node): 
    def config(self, **params):
        super(Router, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')
        self.cmd('cd %s' % self.name)
        self.cmd('bird -l')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        self.cmd('birdc -l down')
        super(Router, self).terminate()

def getmaskedIP(ip: str):
    return '{}/{}'.format(ip, 24)

class MyTopo(Topo):
    def build(self, **_opts):
        r1 = self.addHost('R1', cls = Router, ip = getmaskedIP(r1_eth0_ip))
        r2 = self.addHost('R2', cls = Router, ip = getmaskedIP(r2_eth0_ip))
        r3 = self.addHost('R3', cls = Router, ip = getmaskedIP(r3_eth0_ip))
        r4 = self.addHost('R4', cls = Router, ip = getmaskedIP(r4_eth0_ip))
        h1 = self.addHost(name = 'H1', ip = getmaskedIP(h1_eth0_ip), defaultRoute = 'via {}'.format(r1_eth0_ip))
        h2 = self.addHost(name = 'H2', ip = getmaskedIP(h2_eth0_ip), defaultRoute = 'via {}'.format(r4_eth0_ip))
        self.addLink(h1, r1, intfName1 = h1_eth0, intfName2 = r1_eth0, params1 = {'ip': getmaskedIP(h1_eth0_ip)}, params2 = {'ip': getmaskedIP(r1_eth0_ip)})
        self.addLink(h2, r4, intfName1 = h2_eth0, intfName2 = r4_eth0, params1 = {'ip': getmaskedIP(h2_eth0_ip)}, params2 = {'ip': getmaskedIP(r4_eth0_ip)})
        self.addLink(r1, r2, intfName1 = r1_eth1, intfName2 = r2_eth0, params1 = {'ip': getmaskedIP(r1_eth1_ip)}, params2 = {'ip': getmaskedIP(r2_eth0_ip)})
        self.addLink(r1, r3, intfName1 = r1_eth2, intfName2 = r3_eth0, params1 = {'ip': getmaskedIP(r1_eth2_ip)}, params2 = {'ip': getmaskedIP(r3_eth0_ip)})
        self.addLink(r2, r4, intfName1 = r2_eth1, intfName2 = r4_eth1, params1 = {'ip': getmaskedIP(r2_eth1_ip)}, params2 = {'ip': getmaskedIP(r4_eth1_ip)})
        self.addLink(r3, r4, intfName1 = r3_eth1, intfName2 = r4_eth2, params1 = {'ip': getmaskedIP(r3_eth1_ip)}, params2 = {'ip': getmaskedIP(r4_eth2_ip)})

def init_router(mininet: Mininet):
    buff_size = '10kb'
    bw = '100mbit'
    delay = '30ms'
    routers = {'R1': [r1_eth0, r1_eth1, r1_eth2], 'R2': [r2_eth0, r2_eth1], 'R3': [r3_eth0, r3_eth1], 'R4': [r4_eth0, r4_eth1, r4_eth2]}
    
    for router, intf_list in routers.items():
        for intf in intf_list:
            mininet[router].cmd('tc qdisc add dev {} root handle 1: tbf rate {} buffer {} limit {}'.format(intf, bw, buff_size, buff_size))
            mininet[router].cmd('tc qdisc add dev {} parent 1:1 handle 10: netem delay {}'.format(intf, delay))

def exec():
    topo = MyTopo()
    mininet = Mininet(topo = topo)
    mininet.start()
    init_router(mininet)
    for router in ['R1', 'R2', 'R3', 'R4']:
        info('\n{}\'s Routing Table:\n'.format(router))
        info(mininet[router].cmd('route'))

    time.sleep(2)
    
    info('\nPinging all nodes and routers\n')
    info(mininet.pingAll())

    CLI(mininet)
    mininet.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    exec()