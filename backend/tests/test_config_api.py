import yaml


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_config_returns_200(client):
    r = client.get("/api/config")
    assert r.status_code == 200


def test_config_shape(client):
    r = client.get("/api/config")
    data = r.json()
    assert "timing" in data
    assert "global_target" in data
    assert "devices" in data
    assert "samples" in data
    assert "auto_tune_enabled" in data


def test_config_timing_fields(client):
    r = client.get("/api/config")
    t = r.json()["timing"]
    assert t["device_activation_interval_ms"] == 2000
    assert t["experiment_running_ms"] == 2000
    assert t["experiment_complete_ms"] == 1000
    assert t["experiment_gap_ms"] == 500


def test_config_devices_count(client):
    r = client.get("/api/config")
    devices = r.json()["devices"]
    assert len(devices) == 9


def test_config_samples_count(client):
    r = client.get("/api/config")
    samples = r.json()["samples"]
    assert len(samples) == 20


def test_config_global_target(client):
    r = client.get("/api/config")
    gt = r.json()["global_target"]
    assert gt["tg"] == 520.0
    assert gt["cte"] == 8.5
    assert gt["dielectric"] == 6.2
    assert gt["dielectric_const"] == 3.5
    assert "weights" in gt


def test_config_etag(client):
    r1 = client.get("/api/config")
    etag = r1.headers.get("etag")
    assert etag is not None
    r2 = client.get("/api/config", headers={"if-none-match": etag})
    assert r2.status_code == 304


def test_yaml_parses_cleanly():
    import yaml
    with open(r"C:\JUNHA\11.code\project\demoday\config\demo_data.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data is not None
    assert "samples" in data
