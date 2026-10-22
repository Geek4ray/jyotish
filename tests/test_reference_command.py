"""`jyotish reference` prints the worked example (SPEC, "The first engineering milestone"): its Life
areas are the true-time chart's, the engine result SPEC records (career moderate, top three career,
marriage, longevity), not the positions-only chart's, whose KP votes are not applicable for want of
cusps (review 2026-10-23, F16)."""

import re

from jyotish.cli import main


def test_reference_prints_the_worked_examples_tiers(capsys):
    main(["reference"])
    out = capsys.readouterr().out
    areas = out[out.index("Life areas (Layer 5"):]
    areas = areas[:areas.index("Transits on")]
    assert re.search(r"^  career\s+moderate\s", areas, re.M) and not re.search(r"^  career\s+strong", areas, re.M)
    assert re.search(r"^  health\s+weak / mixed", areas, re.M) and re.search(r"^  mother_home\s+weak / mixed", areas, re.M)
    assert "Top: career, marriage, longevity." in areas
    assert "stability 1.00/1.00/1.00" in areas                       # the true-time chart carries the sampler's numbers
    assert "Driver (v2): Venus" in areas
    assert "The Life areas above, and the stability and timing below, are computed from the birth data at the true time" in out
    # The positions and the fires are still the app's printed chart.
    assert "Sun      27°47'55\" Aquarius" in out and "yoga.ruchaka               sun    Mars H10" in out
