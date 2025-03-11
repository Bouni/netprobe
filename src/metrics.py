import time

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily

from config import config
from helpers.logging import setup_logging
from helpers.redis import RedisConnect

# Logging setup
logger = setup_logging(config.logging.metrics)


class CustomCollector:
    def __init__(self):
        self.cache = RedisConnect()

    def collect(self):
        logger.info("Starting metric collection")
        start_time = time.time()

        # Read data from Redis
        stats_netprobe = self._fetch_redis_data("netprobe")
        stats_speedtest = self._fetch_redis_data("speedtest")

        if not stats_netprobe:
            logger.warning("No netprobe data found in Redis")
            return

        # Create Prometheus metrics
        yield from self._collect_network_metrics(stats_netprobe)
        yield from self._collect_dns_metrics(stats_netprobe)
        yield from self._collect_speedtest_metrics(stats_speedtest)
        yield from self._calculate_health_score(stats_netprobe)

        logger.info(f"Metric collection completed in {time.time() - start_time:.2f}s")

    def _fetch_redis_data(self, key):
        """Retrieve and parse JSON data from Redis."""
        try:
            raw_data = self.cache.redis_read(key)
            return raw_data
        except Exception as e:
            logger.error(f"Failed to read {key} from Redis: {e}")
            return None

    def _collect_network_metrics(self, stats_netprobe):
        """Collect network latency, loss, and jitter metrics."""
        g = GaugeMetricFamily(
            "Network_Stats",
            "Network statistics (latency, loss, jitter)",
            labels=["type", "target"],
        )

        total_latency = total_loss = total_jitter = 0
        for item in stats_netprobe["stats"]:
            latency, loss, jitter = map(
                float, (item["latency"], item["loss"], item["jitter"])
            )
            g.add_metric(["latency", item["site"]], latency)
            g.add_metric(["loss", item["site"]], loss)
            g.add_metric(["jitter", item["site"]], jitter)
            total_latency += latency
            total_loss += loss
            total_jitter += jitter

        # Average calculations
        count = len(stats_netprobe["stats"])
        g.add_metric(["latency", "all"], total_latency / count)
        g.add_metric(["loss", "all"], total_loss / count)
        g.add_metric(["jitter", "all"], total_jitter / count)

        yield g

    def _collect_dns_metrics(self, stats_netprobe):
        """Collect DNS response time metrics."""
        h = GaugeMetricFamily("DNS_Stats", "DNS performance metrics", labels=["server"])

        for item in stats_netprobe["dns_stats"]:
            h.add_metric([item["nameserver"]], float(item["latency"]))

        yield h

    def _collect_speedtest_metrics(self, stats_speedtest):
        """Collect internet speed test metrics."""
        if not stats_speedtest:
            logger.warning("No speedtest data found in Redis")
            return

        s = GaugeMetricFamily(
            "Speed_Stats", "Speedtest.net performance", labels=["direction"]
        )

        for key, value in stats_speedtest.items():
            if value is not None:
                s.add_metric([key], float(value))

        yield s

    def _calculate_health_score(self, stats_netprobe):
        """Calculate an overall internet health score."""
        health_config = config.health

        def compute_score(value, threshold):
            return min(value / threshold, 1)

        # Fetch and compute scores
        avg_loss = compute_score(
            sum(float(item["loss"]) for item in stats_netprobe["stats"])
            / len(stats_netprobe["stats"]),
            health_config.threshold.loss,
        )
        avg_latency = compute_score(
            sum(float(item["latency"]) for item in stats_netprobe["stats"])
            / len(stats_netprobe["stats"]),
            health_config.threshold.latency,
        )
        avg_jitter = compute_score(
            sum(float(item["jitter"]) for item in stats_netprobe["stats"])
            / len(stats_netprobe["stats"]),
            health_config.threshold.jitter,
        )

        # Assume My_DNS_Server is present; adjust if necessary
        dns_latency = next(
            (
                float(item["latency"])
                for item in stats_netprobe["dns_stats"]
                if item["nameserver"] == "My_DNS_Server"
            ),
            1000,
        )
        dns_latency_score = compute_score(dns_latency, health_config.threshold.latency)

        # Weighted health score calculation
        score = 1 - (
            health_config.weight.loss * avg_loss
            + health_config.weight.latency * avg_latency
            + health_config.weight.jitter * avg_jitter
            + health_config.weight.latency * dns_latency_score
        )

        i = GaugeMetricFamily("Health_Stats", "Overall internet health score")
        i.add_metric(["health"], score)

        yield i


def setup_metrics_server():
    """Start the Prometheus metrics server with a singleton collector."""
    logger.info("Starting Prometheus metrics server...")

    REGISTRY.register(CustomCollector())

    start_http_server(config.metrics.port, addr=config.metrics.interface)
    logger.info(
        f"Prometheus metrics server running on {config.metrics.interface}:{config.metrics.port}"
    )
