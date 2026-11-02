#!/bin/bash

# Functions for the VPN client container launch script
#
# Adapted from Fed-BioMed (Apache-2.0):
# https://github.com/fedbiomed/fedbiomed/blob/v6.4.1/envs/vpn/docker/node/build_files/entrypoint_functions.bash

# minimal checks on VPN environment variables
check_vpn_environ() {
    # check requires VPN variables are set
    local required_vpn_vars=${1:-'VPN_IP VPN_SUBNET_PREFIX VPN_SERVER_ENDPOINT VPN_SERVER_ALLOWED_IPS VPN_SERVER_PUBLIC_KEY VPN_SERVER_PSK'}
    local vars_error=false

    for var in $required_vpn_vars
    do
        value=$(eval "echo \$$var")
        if [ -z "$value" ]
        then
            vars_error=true
            echo "CRITICAL: required VPN variable $var is not set"
        else
            [ "$var" = 'VPN_SERVER_PSK' ] && value='_HIDDEN_VALUE_'
            echo "info: set $var='$value'"
        fi
    done
    if "$vars_error"
    then
        echo "CRITICAL: missing some required VPN variables, terminating"
        echo "CRITICAL: did you put the config.env file from the VPN administrator in ${CONFIG_DIR}?"
        exit 1
    fi
}

# initialize some environment variables
init_misc_environ() {

    #catch all errors in pipes
    set -o pipefail
}

# check wireguard interface exists
check_wg_interface() {

    if ! $(ifconfig wg0 >/dev/null 2>&1)
    then
        echo "CRITICAL: no wireguard interface wg0, cannot continue"
        exit 1
    fi
}

# launch wireguard VPN
# - uses boringtun (userspace) so that the container does not need to load or
#   remove kernel modules on the host
start_wireguard(){

    if ! WG_SUDO=1 boringtun wg0
    then
        echo "CRITICAL: could not start wireguard"
        exit 1
    fi
    echo "info: started wireguard, using boringtun"
}

# stop wireguard vpn
stop_wireguard() {

    # check wireguard interface still exists (may be destroyed by some errors)
    check_wg_interface

    echo "info: stopping wireguard"
    if ! pkill boringtun
    then
        echo "CRITICAL: could not stop wireguard boringtun"
        exit 1
    fi
}

save_wg_config() {

    # check wireguard interface still exists (may be destroyed by some errors)
    check_wg_interface

    # save configuration
    ( umask 0077 && wg showconf wg0 | tee $CONFIG_DIR/wireguard/wg0.conf >/dev/null )
    if [ "$?" -ne 0 ]
    then
        echo "CRITICAL: could not save wireguard config to ${CONFIG_DIR}/wireguard/wg0.conf"
        exit 1
    fi
    # give saved files the same owner as the mounted config directory (host user)
    chown -R --reference=$CONFIG_DIR $CONFIG_DIR/wireguard
    echo "info: saved wireguard config to ${CONFIG_DIR}/wireguard/wg0.conf"
}

# configure wireguard VPN
configure_wireguard() {

    mkdir -p $CONFIG_DIR/wireguard
    if [ "$?" -ne 0 ]
    then
        echo "CRITICAL: could not create config directory ${CONFIG_DIR}/wireguard"
        exit 1
    fi

    # need wireguard interface to continue
    check_wg_interface

    if [ -s "$CONFIG_DIR/wireguard/wg0.conf" ]
    then
        echo "info: loading wireguard config from existing file ${CONFIG_DIR}/wireguard/wg0.conf"
        wg setconf wg0 $CONFIG_DIR/wireguard/wg0.conf
        if [ "$?" -ne 0 ]
        then
            echo "CRITICAL: could not set wireguard config from file ${CONFIG_DIR}/wireguard/wg0.conf"
            exit 1
        fi
    else
        echo "info: generating new wireguard config"
        wg set wg0 private-key <(wg genkey)
        if [ "$?" -ne 0 ]
        then
            echo "CRITICAL: could not generate new wireguard config"
            exit 1
        fi

        save_wg_config
    fi

    # VPN client setup
    if [ -n "$VPN_SERVER_PUBLIC_KEY" ]
    then
        if [ "x$VPN_SERVER_PUBLIC_KEY" != x$(wg show wg0 peers | grep "$VPN_SERVER_PUBLIC_KEY") ]
        then
            # interface may not exist in case of fatal error in previous step
            check_wg_interface

            wg set wg0 peer "$VPN_SERVER_PUBLIC_KEY" allowed-ips "$VPN_SERVER_ALLOWED_IPS" endpoint "$VPN_SERVER_ENDPOINT" preshared-key <(echo "$VPN_SERVER_PSK") persistent-keepalive 25
            if [ "$?" -ne 0 ]
            then
                echo "CRITICAL: could not add peer to wireguard interface"
                exit 1
            fi

            save_wg_config
        fi
    fi

    # not needed anymore, remove if present (privacy provision)
    unset VPN_SERVER_PSK

    # check interface still exists
    check_wg_interface

    # add address and route
    ip -4 address add "$VPN_IP/$VPN_SUBNET_PREFIX" dev wg0
    if [ "$?" -ne 0 ]
    then
        echo "CRITICAL: could not set IP address and route for wireguard interface"
        exit 1
    fi

    # activate and set mtu
    ip link set mtu 1420 up dev wg0
    if [ "$?" -ne 0 ]
    then
        echo "CRITICAL: could not activate wireguard interface"
        exit 1
    fi

    echo "info: wireguard interface ready"
}

# called when stopping the container
finish () {

    echo "info: preparing to stop container"
    save_wg_config
    stop_wireguard
    echo "info: ready to stop container"

    exit 0
}
