import json
import subprocess
import threading
import time

from dns.resolver import Resolver

from config import config
from helpers.logging import setup_logging


class NetworkCollector:
    def __init__(self, sites, count, dns_test_site, nameserver_list, shared_data):
        self.sites = sites
        self.count = count
        self.pingstats = []
        self.dnsstats = []
        self.dns_test_site = dns_test_site
        self.nameservers = nameserver_list
        self.shared_data = shared_data
        self.logger = setup_logging(config.logging.netprobe)

    def pingtest(self, count, site):
        # Run ping binary and process the output
        ping = subprocess.getoutput(
            f"ping -n -i 0.1 -c {count} {site} | grep 'rtt\\|loss'"
        )
        try:
            loss = ping.split(" ")[5].strip("%")
            latency = ping.split("/")[4]
            jitter = ping.split("/")[6].split(" ")[0]
            netdata = {"site": site, "latency": latency, "loss": loss, "jitter": jitter}
            self.logger.debug(netdata)
            self.pingstats.append(netdata)
        except Exception as e:
            self.logger.error(f"Error pinging {site}")
            self.logger.error(e)
            return False
        return True

    def dnstest(self, site, nameserver):
        # Run DNS tests
        my_resolver = Resolver()
        server = []  # Resolver needs a list
        server.append(nameserver.ip)
        try:
            my_resolver.nameservers = server
            my_resolver.timeout = 10
            answers = my_resolver.query(site, "A")
            dns_latency = round(answers.response.time * 1000, 2)
            dnsdata = {
                "nameserver": nameserver.name,
                "nameserver_ip": nameserver.ip,
                "latency": dns_latency,
            }
            self.logger.debug(dnsdata)
            self.dnsstats.append(dnsdata)
        except Exception as e:
            self.logger.error(f"Error performing DNS resolution on {nameserver.name}")
            self.logger.error(e)
            dnsdata = {
                "nameserver": nameserver.name,
                "nameserver_ip": nameserver.ip,
                "latency": 5000,
            }
            self.dnsstats.append(dnsdata)
        return True

    def write_results(self):
        self.shared_data["netprobe"] = {
            "stats": self.pingstats,
            "dns_stats": self.dnsstats,
        }
        self.pingstats = []
        self.dnsstats = []
        self.logger.debug("Netprobe stats written to shared object")


class SpeedtestCollector:
    def __init__(self, shared_data):
        self.speedstats = {}
        self.shared_data = shared_data
        self.logger = setup_logging(config.logging.speedtest)

    def speedtest(self):
        # run the speedtest-cli binary and process the output
        try:
            result = subprocess.getoutput("speedtest-cli --json")
            self.logger.debug(result)
            data = json.loads(result)
            speeddata = {"download": data["download"], "upload": data["upload"]}
            self.logger.debug(speeddata)
            self.speedstats = speeddata
        except Exception as e:
            self.logger.error("Error performing speedtest.")
            self.logger.error(e)
            speeddata = {"download": None, "upload": None}
            self.speedstats = speeddata
        return True

    def write_results(self):
        self.shared_data["speedtest"] = self.speedstats
        self.speedstats = {}
        self.logger.debug("Speedstats written to shared object")


def run_net_probe(collector, interval):
    # Spawn probe threads, write the results to shared object and wait for the configured interval
    while True:
        threads = []
        for site in collector.sites:
            t = threading.Thread(
                target=collector.pingtest, args=(collector.count, site)
            )
            threads.append(t)
            t.start()

        for nameserver in collector.nameservers:
            t = threading.Thread(
                target=collector.dnstest, args=(collector.dns_test_site, nameserver)
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        collector.write_results()
        time.sleep(interval)


def run_speed_probe(collector, interval):
    # Run speedtest, write the results to the shared object and wait for the configured interval
    while True:
        collector.speedtest()
        collector.write_results()

        time.sleep(interval)
