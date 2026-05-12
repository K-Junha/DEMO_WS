from pydantic import BaseModel
from typing import Optional


class Weights(BaseModel):
    tg: float
    cte: float
    dielectric: float
    dielectric_const: float


class GlobalTarget(BaseModel):
    tg: float
    cte: float
    dielectric: float
    dielectric_const: float
    weights: Weights


class Timing(BaseModel):
    device_activation_interval_ms: int
    experiment_running_ms: int
    experiment_complete_ms: int
    experiment_gap_ms: int


class RandomRangeItem(BaseModel):
    min: float
    max: float


class RandomRange(BaseModel):
    tg: RandomRangeItem
    cte: RandomRangeItem
    dielectric: RandomRangeItem
    dielectric_const: RandomRangeItem


class Device(BaseModel):
    id: str
    name: str
    model: str
    protocol: str
    ip: str
    port: int
    connected: bool
    measures: Optional[list[str]] = None


class Props4(BaseModel):
    tg: float
    cte: float
    dielectric: float
    dielectric_const: float


class FurnaceStep(BaseModel):
    step: int
    target_temp: float
    measured_temp: float
    hold_time: str
    heating_rate: float


class SampleExperiment(BaseModel):
    scale: Optional[dict] = None
    mixer: Optional[dict] = None
    furnace: Optional[dict] = None
    annealing: Optional[dict] = None
    press: Optional[dict] = None


class Sample(BaseModel):
    id: str
    composition: str
    predicted: Props4
    measurement: Props4
    next_composition: str
    experiment: SampleExperiment


class AppConfig(BaseModel):
    timing: Timing
    global_target: GlobalTarget
    auto_tune_enabled: bool
    random_range: RandomRange
    devices: list[Device]
    samples: list[Sample]
