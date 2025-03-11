# Netprobe Service

import time
import json
from helpers.network_helper import NetworkCollector
from helpers.redis_helper import RedisConnect
from config import config
from datetime import datetime
from helpers.logging_helper import setup_logging

if __name__ == "__main__":
    collector = NetworkCollector(
        config.ping.sites,
        config.probe.count,
        config.dns.testsite,
        config.dns.nameservers,
    )

    # Logging Config

    logger = setup_logging("logs/netprobe.log")

    while True:
        try:
            stats = collector.collect()
            current_time = datetime.now()

        except Exception as e:
            print("Error testing network")
            logger.error("Error testing network")
            logger.error(e)
            continue

        # Connect to Redis

        try:
            cache = RedisConnect()

            # Save Data to Redis

            cache_interval = (
                config.probe.interval + 15
            )  # Set the redis cache TTL slightly longer than the probe interval

            cache.redis_write("netprobe", json.dumps(stats), cache_interval)

            # logger.info(f"Stats successfully written to Redis from device ID for Netprobe")

        except Exception as e:
            logger.error("Could not connect to Redis")
            logger.error(e)

        time.sleep(config.probe.interval)
