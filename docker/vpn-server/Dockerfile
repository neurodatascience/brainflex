# WireGuard VPN server for Fed-BioMed nodes and researchers
#
# Adapted from Fed-BioMed (Apache-2.0):
# https://github.com/fedbiomed/fedbiomed/blob/v6.4.1/envs/vpn/docker/vpnserver/build_files/Dockerfile
#
# Built on top of the VPN client image (`docker/vpn-client`, passed as the
# `vpn-client` build context), which provides wireguard and the entrypoint functions

FROM vpn-client

# python3 and python3-tabulate are needed by configure_peer.py
# iptables is needed to restrict traffic between VPN peers
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-tabulate iptables && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /fedbiomed

# wireguard server
EXPOSE 51820/udp

COPY vpn vpn/
COPY configure_peer /usr/local/bin/
COPY entrypoint.bash /
RUN chmod +x /entrypoint.bash /usr/local/bin/configure_peer

ENTRYPOINT ["/entrypoint.bash"]
