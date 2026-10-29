import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "t.db")
import app as appmod
from automation import process_request


def test_password_reset_auto_resolves():
    r = process_request("I forgot my password", "cannot login")
    assert r["intent"] == "password_reset" and r["status"] == "auto_resolved" and r["auto_reply"]


def test_security_goes_to_soc_p1():
    r = process_request("Suspicious phishing email received")
    assert r["team"] == "Security SOC" and r["priority"] == "P1" and r["status"] == "assigned"


def test_urgent_bumps_priority():
    assert process_request("Application crashes on billing page, urgent")["priority"] == "P1"


def test_unknown_goes_to_service_desk():
    assert process_request("What is the cafeteria menu today")["team"] == "Service Desk"


def test_api_flow():
    appmod.init_db()
    c = appmod.app.test_client()
    assert c.post("/api/requests", json={}).status_code == 400
    rid = c.post("/api/requests", json={"title": "Keyboard is not working"}).get_json()["id"]
    assert c.patch(f"/api/requests/{rid}", json={"status": "resolved"}).get_json()["status"] == "resolved"
    assert c.get("/api/stats").get_json()["total"] == 1
