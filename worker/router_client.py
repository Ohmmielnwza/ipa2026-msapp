"""Part 11: SSH to a router and return structured interface records."""

import os
from netmiko import ConnectHandler
from ntc_templates.parse import parse_output


def get_interfaces(ip, username, password, ssh_port=22, device_type="cisco_ios"):
    if os.getenv("ROUTER_MODE", "ssh") == "demo":
        # Explicit lab fixture; this branch does NOT connect to a router.
        output = (
            "Interface              IP-Address      OK? Method Status                Protocol\n"  # noqa: E501
            f"GigabitEthernet1        {ip:<15} YES manual up                    up\n"
            "GigabitEthernet2        unassigned      YES unset  administratively down down\n"  # noqa: E501
            "GigabitEthernet3        unassigned      YES unset  administratively down down\n"  # noqa: E501
            "GigabitEthernet4        unassigned      YES unset  administratively down down\n"  # noqa: E501
        )
        return parse_output(
            platform="cisco_ios", command="show ip interface brief", data=output
        )
    with ConnectHandler(
        device_type=device_type,
        host=ip,
        port=int(ssh_port),
        username=username,
        password=password,
        conn_timeout=10,
        auth_timeout=10,
        banner_timeout=15,
    ) as connection:
        result = connection.send_command(
            "show ip interface brief", use_textfsm=True, read_timeout=30
        )
    if not isinstance(result, list) or not result:
        raise ValueError("TextFSM returned no structured interface records")
    return result
