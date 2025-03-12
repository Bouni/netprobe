import threading
import time
from multiprocessing import Manager

from config import config
from helpers.logging import setup_logging
from metrics import setup_metrics_server
from probes import NetworkCollector, SpeedtestCollector, run_net_probe, run_speed_probe

logger = setup_logging(config.logging.main)

if __name__ == "__main__":
    with Manager() as manager:
        shared_data = manager.dict()
        # Setup collectors
        netprobe_collector = NetworkCollector(
            config.ping.sites,
            config.probe.count,
            config.dns.testsite,
            config.dns.nameservers,
            shared_data,
        )
        speed_collector = SpeedtestCollector(shared_data)

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
        threading.Thread(
            target=setup_metrics_server, args=(shared_data,), daemon=True
        ).start()

        # Keep the main thread alive
        while True:
            time.sleep(1)
