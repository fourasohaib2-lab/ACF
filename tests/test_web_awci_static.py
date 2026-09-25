"""acf-awci-web serves the built front on / and keeps the API first."""

from fastapi.testclient import TestClient

from acf.web.awci_app import create_awci_app


def test_serves_index_and_keeps_api(tmp_path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html><title>AWCI</title>")
    c = TestClient(create_awci_app(data_dir=tmp_path, web_dist=dist))
    assert "AWCI" in c.get("/").text
    assert c.get("/api/v1/awci/registry").status_code == 200


def test_no_dist_no_static_mount(tmp_path) -> None:
    c = TestClient(create_awci_app(data_dir=tmp_path, web_dist=tmp_path / "absent"))
    assert c.get("/").status_code == 404


def test_e2e_server_prepares_a_complete_and_a_partial_run(tmp_path) -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "awci"))
    import e2e_server
    from acf.web.awci_wms import WmsRelay

    domains = e2e_server.prepare(tmp_path)
    app = create_awci_app(data_dir=tmp_path, domains_file=domains, web_dist=tmp_path / "none")
    app.state.awci_wms = WmsRelay(e2e_server.OfflineWmsFetcher(), tmp_path / "cache")
    c = TestClient(app)
    assert c.get("/api/v1/awci/runs", params={"domain": "fixture"}).json()[0]["status"] == "complete"
    wet = c.get("/api/v1/awci/runs", params={"domain": "fixture_wet"}).json()[0]
    assert wet["status"] == "partial" and wet["missing_steps"] == [6]
    tile = {"bbox": "0,4000000,500000,4500000", "width": 256, "height": 256}
    assert c.get("/api/v1/awci/wms", params=tile | {"layer": "mtg_fd:ir105_hrfi"}).status_code == 200
    assert c.get("/api/v1/awci/wms", params=tile | {"layer": "msg_fes:rgb_ash"}).status_code == 502
