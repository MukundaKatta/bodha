"""Tests for Bodha."""
from src.core import Bodha
def test_init(): assert Bodha().get_stats()["ops"] == 0
def test_op(): c = Bodha(); c.process(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Bodha(); [c.process() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Bodha(); c.process(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Bodha(); r = c.process(); assert r["service"] == "bodha"
