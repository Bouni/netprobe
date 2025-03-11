import threading
import time

from config import config
from metrics import setup_metrics_server
from probes import NetworkCollector, SpeedtestCollector, run_net_probe, run_speed_probe
from helpers.logging import setup_logging

logger = setup_logging(config.logging.main)

if __name__ == "__main__":
    # Setup collectors
    netprobe_collector = NetworkCollector(
        config.ping.sites,
        config.probe.count,
        config.dns.testsite,
        config.dns.nameservers,
    )
    speed_collector = SpeedtestCollector()

    # Start netprobe thread
    threading.Thread(
        target=run_net_probe,
        args=(netprobe_collector, config.probe.interval),
        daemon=True,
    ).start()

    # Start speedtest thread if enabled
    if config.speed.enabled:
        threading.Thread(
            target=run_speed_probe,
            args=(speed_collector, config.speed.interval),
            daemon=True,
        ).start()
    else:
        logger.info("Speedtest is disabled in the config.")

    # Start metrics server
    threading.Thread(target=setup_metrics_server, daemon=True).start()

    # Keep the main thread alive
    while True:
        time.sleep(1)
