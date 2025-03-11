# Netprobe Service

import time
import json
from helpers.network_helper import Netprobe_Speedtest
from helpers.redis_helper import RedisConnect
from config import config
from datetime import datetime
from helpers.logging_helper import setup_logging

if __name__ == "__main__":
    # Global Variables
    collector = Netprobe_Speedtest()

    # Logging Config

    logger = setup_logging("logs/speedtest.log")

    if config.speed.enabled:
        while True:
            try:
                stats = collector.collect()
                current_time = datetime.now()

            except Exception as e:
                print("Error running speedtest")
                logger.error("Error running speedtest")
                logger.error(e)
                time.sleep(config.speed.interval)  # Pause before retrying
                continue

            # Connect to Redis

            try:
                cache = RedisConnect()

                # Save Data to Redis

                cache_interval = (
                    config.speed.interval * 2
                )  # Set the redis cache 2x longer than the speedtest interval

                cache.redis_write("speedtest", json.dumps(stats), cache_interval)

                logger.info("Stats successfully written to Redis for Speed Test")

            except Exception as e:
                logger.error("Could not connect to Redis")
                logger.error(e)

            time.sleep(config.speed.interval)

    else:
        logger.info("Speedtest disabled in config!")
        exit()
