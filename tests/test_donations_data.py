from tracker.data.donations import DONATION_MILESTONES, GREED_DONATION_MILESTONES


def test_donation_milestones_sorted_ascending():
    amounts = [m["amount"] for m in DONATION_MILESTONES]
    assert amounts == sorted(amounts), f"DONATION_MILESTONES not sorted: {amounts}"


def test_greed_milestones_sorted_ascending():
    amounts = [m["amount"] for m in GREED_DONATION_MILESTONES]
    assert amounts == sorted(amounts), f"GREED_DONATION_MILESTONES not sorted: {amounts}"


def test_donation_milestones_have_required_fields():
    required = {"amount", "achievement_id", "name"}
    for m in DONATION_MILESTONES + GREED_DONATION_MILESTONES:
        assert required.issubset(m.keys()), f"missing fields in {m}"
        assert isinstance(m["amount"], int) and m["amount"] > 0
        assert isinstance(m["achievement_id"], int) and 0 <= m["achievement_id"] < 642


def test_known_milestones_present():
    by_amount_greed = {m["amount"]: m for m in GREED_DONATION_MILESTONES}
    by_amount_normal = {m["amount"]: m for m in DONATION_MILESTONES}
    assert by_amount_greed[879]["name"] == "Lost holds Holy Mantle"
    assert by_amount_greed[879]["achievement_id"] == 250
    assert by_amount_greed[1000]["name"] == "Keeper"
    assert by_amount_greed[1000]["achievement_id"] == 251
    assert by_amount_normal[999]["name"] == "Stop Watch"
    assert by_amount_normal[999]["achievement_id"] == 138
