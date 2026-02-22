from lxml import etree


def parse_nmap_xml(filepath: str) -> list[dict]:
    """Parse an Nmap XML file and return a list of open port dicts.

    Only IPv4 hosts are processed; IPv6-only hosts are skipped.
    Each returned dict has keys: host, port, protocol, service, state.
    """
    try:
        tree = etree.parse(filepath)
    except (OSError, etree.XMLSyntaxError) as e:
        raise ValueError(f"Failed to parse nmap XML: {e}") from e

    root = tree.getroot()
    if root.tag != "nmaprun":
        raise ValueError(f"Not an nmap XML file: root element is <{root.tag}>")

    results = []
    for host in tree.findall(".//host"):
        addr_el = host.find("address[@addrtype='ipv4']")
        if addr_el is None:
            continue
        ip = addr_el.get("addr", "")

        for port_el in host.findall(".//port"):
            state_el = port_el.find("state")
            if state_el is None or state_el.get("state") != "open":
                continue

            portid = port_el.get("portid")
            if portid is None:
                continue

            service_el = port_el.find("service")
            service_name = service_el.get("name", "") if service_el is not None else ""

            results.append({
                "host": ip,
                "port": int(portid),
                "protocol": port_el.get("protocol", "tcp"),
                "service": service_name,
                "state": "open",
            })

    return results
