import os
import pytest
from aptsec.parsers.nmap import parse_nmap_xml

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "nmap_sample.xml")


def test_parse_returns_list_of_dicts():
    results = parse_nmap_xml(FIXTURE)
    assert isinstance(results, list)
    assert len(results) > 0


def test_open_ports_only():
    results = parse_nmap_xml(FIXTURE)
    states = [r["state"] for r in results]
    assert all(s == "open" for s in states)


def test_fields_present():
    results = parse_nmap_xml(FIXTURE)
    first = results[0]
    for field in ("host", "port", "protocol", "service", "state"):
        assert field in first


def test_ssh_port_parsed():
    results = parse_nmap_xml(FIXTURE)
    ssh = next((r for r in results if r["port"] == 22), None)
    assert ssh is not None
    assert ssh["service"] == "ssh"
    assert ssh["host"] == "10.0.0.1"


def test_closed_port_excluded():
    results = parse_nmap_xml(FIXTURE)
    ports = [r["port"] for r in results]
    assert 80 not in ports


def test_invalid_file_raises():
    with pytest.raises(Exception):
        parse_nmap_xml("/nonexistent/file.xml")
