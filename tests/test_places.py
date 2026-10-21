"""The bundled place list (GeoNames cities15000, CC BY 4.0) and its search."""

from jyotish.places import ATTRIBUTION, places, search


def test_reference_birthplace_is_found_with_coordinates_and_timezone():
    [p] = search("rewari", 1)
    assert p["label"] == "Rewāri, Haryana, India" and p["timezone"] == "Asia/Kolkata"
    assert abs(p["lat"] - 28.1989) < 0.01 and abs(p["lon"] - 76.6170) < 0.01        # the reference chart's place
    assert search("Rewāri", 1) == search("REWARI", 1) == search("rewari, har", 1)     # accents, case, "name, state"


def test_old_names_ranking_and_narrowing():
    assert search("bombay", 1)[0]["label"] == "Mumbai, Maharashtra, India"
    assert search("calcutta", 1)[0]["label"] == "Kolkata, West Bengal, India"
    london = search("london", 3)
    assert london[0]["label"] == "London, England, United Kingdom" and london[0]["timezone"] == "Europe/London"
    assert search("paris, united states", 1)[0]["country_code"] == "US"
    assert search("r") == [] and len(search("san", 20)) == 20


def test_every_place_has_coordinates_in_range_and_a_timezone():
    ps = places()
    assert len(ps) > 30_000
    assert all(-90 <= p["lat"] <= 90 and -180 <= p["lon"] <= 180 and "/" in p["timezone"] or p["timezone"] == "UTC"
               for p in ps)
    assert "GeoNames" in ATTRIBUTION and "CC BY 4.0" in ATTRIBUTION
