# Config loading and validation

import yaml
from pydantic import BaseModel, ValidationError


class PingModel(BaseModel):
    sites: list[str]


class NameServerModel(BaseModel):
    name: str
    ip: str


class DNSModel(BaseModel):
    testsite: str
    nameservers: list[NameServerModel]


class HealthWeightModel(BaseModel):
    loss: float
    latency: float
    jitter: float
    dns_latency: float


class HealthThresholdModel(BaseModel):
    loss: int
    latency: int
    jitter: int
    dns_latency: int


class HealthModel(BaseModel):
    weight: HealthWeightModel
    threshold: HealthThresholdModel


class SpeedModel(BaseModel):
    enabled: bool
    interval: int


class PresentationModel(BaseModel):
    port: int
    interface: str


class RedisModel(BaseModel):
    url: str
    port: int
    password: str


class ProbeModel(BaseModel):
    interval: int
    count: int


class ConfigModel(BaseModel):
    ping: PingModel
    dns: DNSModel
    health: HealthModel
    speed: SpeedModel
    presentation: PresentationModel
    redis: RedisModel
    probe: ProbeModel


def load_config(file_path: str) -> dict:
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        print(e)
    return {}


def validate_config(config_data: dict):
    try:
        config = ConfigModel(**config_data)
        return config
    except ValidationError as e:
        print("Configuration validation failed:", e)


config = validate_config(load_config("config.yml"))
