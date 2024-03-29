import logging
import os
from collections import Counter
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from rich import print as rprint

nr = InitNornir(config_file="config.yaml")

CLEAR = "clear"
os.system(CLEAR)
ip_list = []

def get_ip(task):
    """
    Extract IP addresses from all interfaces and add them to the list called `ip_list`.
    """
    response = task.run(
        task=send_command, command="show interfaces", severity_level=logging.DEBUG
    )
    task.host["facts"] = response.scrapli_response.genie_parse_output()
    interfaces = task.host["facts"]
    for intf in interfaces:
        try:
            ip_key = interfaces[intf]["ipv4"]
            for ip in ip_key:
                ip_addr = ip_key[ip]["ip"]
                ip_list.append(ip_addr)
        except KeyError:
            pass

def locate_ip(task):
    """
    Retrieve details about all interfaces.
    This task aims to locate the network interface and device that has been assigned a duplicate IP address.
    """
    response = task.run(
        task=send_command, command="show interfaces", severity_level=logging.DEBUG
    )
    task.host["facts"] = response.scrapli_response.genie_parse_output()
    interfaces = task.host["facts"]
    for intf in interfaces:
        try:
            ip_key = interfaces[intf]["ipv4"]
            for ip in ip_key:
                ip_addr = ip_key[ip]["ip"]
                if ip_addr in targets:
                    rprint(f"[yellow]{task.host} {intf} - {ip_addr}[/yellow]")
        except KeyError:
            pass

nr.run(task=get_ip)
targets = [k for k, v in Counter(ip_list).items() if v > 1]
if targets:
    rprint("[red]ALERT: DUPLICATES IP DETECTED![/red]")
    rprint(targets)
    rprint("\n[cyan]Searching IP addresses in topology...[/cyan]")
    nr.run(task=locate_ip)
else:
    rprint("[green]SCAN FINISHED - NO DUPLICATES IP DETECTED[/green]")
