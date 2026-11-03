# WireGuard VPN client for a Fed-BioMed node
#
# Adapted from Fed-BioMed (Apache-2.0):
# https://github.com/fedbiomed/fedbiomed/blob/v6.4.1/envs/vpn/docker/base/build_files/Dockerfile

# temporary builder image for boringtun (userspace implementation of wireguard)
FROM rust:1.99.1-slim-bookworm@sha256:24707e70a4f1e23d9a7b25202ec43126d28a52294b96aad5c670df1fd1f1d400 AS builder

RUN cargo install --locked --bin boringtun --version =0.4.0 boringtun

# runtime image: wireguard and network tools
FROM debian:bookworm-slim@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3

RUN apt-get update && \
    apt-get install -y --no-install-recommends wireguard-tools iproute2 iputils-ping bash vim net-tools procps && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/cargo/bin/boringtun /usr/bin/

COPY entrypoint.bash entrypoint_functions.bash /
RUN chmod +x /entrypoint.bash

ENTRYPOINT ["/entrypoint.bash"]
