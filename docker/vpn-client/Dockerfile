# WireGuard VPN client for a Fed-BioMed node
#
# Adapted from Fed-BioMed (Apache-2.0):
# https://github.com/fedbiomed/fedbiomed/blob/v6.4.1/envs/vpn/docker/base/build_files/Dockerfile

# temporary builder image for wireguard tools
# - may need update for properly compiling boringtun
# - built on the same suite as the runtime image so its binaries stay compatible
FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y git build-essential curl

# install boringtun userspace implementation of wireguard
#
# - match versions of debian & boringtun : up to date 0.5.2 compiles ok for bullseye, but could not have it working
#   Continue with 0.4.0
# - glitch: debian's apt-get cargo is too old vs boringtun's cargo packages dependencies, need to install
#   up to date rust/cargo
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && . /root/.cargo/env && \
    cargo install --locked --bin boringtun --version ~0.4.0 boringtun

# install needed wireguard-tools
RUN apt-get install -y wireguard-tools

# runtime image: only needs wireguard and network tools, no Python
FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends iproute2 iputils-ping bash vim net-tools procps && \
    rm -rf /var/lib/apt/lists/*

# get wireguard from builder image
COPY --from=builder /root/.cargo/bin/boringtun /usr/bin/
COPY --from=builder /usr/bin/wg* /usr/bin/

COPY entrypoint.bash entrypoint_functions.bash /
RUN chmod +x /entrypoint.bash

ENTRYPOINT ["/entrypoint.bash"]
