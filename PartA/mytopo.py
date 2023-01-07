from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.examples.linuxrouter import LinuxRouter
from mininet.log import setLogLevel, info

class mytopo(Topo):
    def build(self, **_opts):
        r1 = self.addHost('R1', cls = LinuxRouter, ip = '172.10.1.1/24')
        r2 = self.addHost('R2', cls = LinuxRouter, ip = '172.10.2.1/24')
        r3 = self.addHost('R3', cls = LinuxRouter, ip = '172.10.3.1/24')
        r4 = self.addHost('R4', cls = LinuxRouter, ip = '172.10.6.1/24')
        h1 = self.addHost(name = 'H1', ip = '172.10.1.2/24', defaultRoute = 'via 172.10.1.1')
        h2 = self.addHost(name = 'H2', ip = '172.10.6.2/24', defaultRoute = 'via 172.10.6.1')

        self.addLink(h1, r1, intfName1 = 'h1_eth0', intfName2 = 'r1_eth0', params1 = {'ip': '172.10.1.2/24'}, params2 = {'ip': '172.10.1.1/24'})
        self.addLink(h2, r4, intfName1 = 'h2_eth0', intfName2 = 'r4_eth0', params1 = {'ip': '172.10.6.2/24'}, params2 = {'ip': '172.10.6.1/24'})
        self.addLink(r1, r2, intfName1 = 'r1_eth1', intfName2 = 'r2_eth0', params1 = {'ip': '172.10.2.2/24'}, params2 = {'ip': '172.10.2.1/24'})
        self.addLink(r1, r3, intfName1 = 'r1_eth2', intfName2 = 'r3_eth0', params1 = {'ip': '172.10.3.2/24'}, params2 = {'ip': '172.10.3.1/24'})
        self.addLink(r2, r4, intfName1 = 'r2_eth1', intfName2 = 'r4_eth1', params1 = {'ip': '172.10.4.1/24'}, params2 = {'ip': '172.10.4.2/24'})
        self.addLink(r3, r4, intfName1 = 'r3_eth1', intfName2 = 'r4_eth2', params1 = {'ip': '172.10.5.1/24'}, params2 = {'ip': '172.10.5.2/24'})

def add_static_routes(net: Mininet):
    net['R1'].cmd("ip route add 172.10.4.0/24 via 172.10.2.1 dev r1_eth1")
    net['R1'].cmd("ip route add 172.10.5.0/24 via 172.10.3.1 dev r1_eth2")
    #net['R1'].cmd("ip route add 172.10.6.0/24 via 172.10.2.1 dev r1_eth1")
    net['R1'].cmd("ip route add 172.10.6.0/24 via 172.10.3.1 dev r1_eth2")
    net['R1'].cmd("sysctl net.ipv4.ip_forward=1")

    net['R2'].cmd("ip route add 172.10.3.0/24 via 172.10.2.2 dev r2_eth0")
    net['R2'].cmd("ip route add 172.10.5.0/24 via 172.10.4.2 dev r2_eth1")
    net['R2'].cmd("ip route add 172.10.1.0/24 via 172.10.2.2 dev r2_eth0")
    net['R2'].cmd("ip route add 172.10.6.0/24 via 172.10.4.2 dev r2_eth1")
    net['R2'].cmd("sysctl net.ipv4.ip_forward=1")

    net['R3'].cmd("ip route add 172.10.2.0/24 via 172.10.3.2 dev r3_eth0")
    net['R3'].cmd("ip route add 172.10.4.0/24 via 172.10.5.2 dev r3_eth1")
    net['R3'].cmd("ip route add 172.10.6.0/24 via 172.10.5.2 dev r3_eth1")
    net['R3'].cmd("ip route add 172.10.1.0/24 via 172.10.3.2 dev r3_eth0")
    net['R3'].cmd("sysctl net.ipv4.ip_forward=1")

    net['R4'].cmd("ip route add 172.10.2.0/24 via 172.10.4.1 dev r4_eth1")
    net['R4'].cmd("ip route add 172.10.3.0/24 via 172.10.5.1 dev r4_eth2")
    net['R4'].cmd("ip route add 172.10.1.0/24 via 172.10.5.1 dev r4_eth2")
    #net['R4'].cmd("ip route add 172.10.1.0/24 via 172.10.4.1 dev r4_eth1")
    net['R4'].cmd("sysctl net.ipv4.ip_forward=1")


def exec():
    topo = mytopo()
    mininet = Mininet(topo = topo)
    mininet.start()

    add_static_routes(mininet)
    
    for router in ['R1', 'R2', 'R3', 'R4']:
        info('\n{}\'s Routing Table:\n'.format(router))
        info(mininet[router].cmd('route'))
    
    info('\nPinging all nodes and routers\n')
    info(mininet.pingAll())

    CLI(mininet)
    mininet.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    exec()