"""This file is automatically read when running tests"""
import pytest


@pytest.fixture(autouse=True)
def aws_credentials(monkeypatch):
    """Set dummy AWS credentials for tests purposes"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_ACCOUNT_ID", "testing")
