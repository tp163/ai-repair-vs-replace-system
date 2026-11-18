"""Tests for device identification, typo tolerance, and fuzzy matching."""
import pytest
from src.dataset import load_phones
from src.device_match import match_device, build_confirmation, analysis_allowed


@pytest.fixture
def catalogue():
    return load_phones()


def test_exact_match(catalogue):
    res = match_device("Apple", "iPhone 13", catalogue)
    assert res["match_status"] == "exact"
    assert res["was_corrected"] is False
    assert len(res["options"]) >= 1
    assert res["options"][0]["phone"]["brand"] == "Apple"
    assert res["options"][0]["phone"]["model"] == "iPhone 13"


def test_typo_iponw_matches_iphone_13(catalogue):
    # Common user typo: "iponw 13" -> "Apple iPhone 13"
    res = match_device("apple", "iponw 13", catalogue)
    assert res["match_status"] == "fuzzy_match"
    assert res["was_corrected"] is True
    assert res["canonical_name"] == "Apple iPhone 13"
    assert res["canonical_brand"] == "Apple"
    assert res["canonical_model"] == "iPhone 13"
    assert len(res["options"]) >= 1
    assert res["confidence"] >= 0.75

    conf = build_confirmation(res, None, user_confirmed=True)
    assert conf["confirmed"] is True
    assert conf["unverified"] is False
    assert conf["matched_id"] == "iphone-13-128"
    assert analysis_allowed(conf) is True


def test_typo_galxy_matches_galaxy_a51(catalogue):
    # Common user typo: "galxy a51" -> "Samsung Galaxy A51"
    res = match_device("samsung", "galxy a51", catalogue)
    assert res["match_status"] == "fuzzy_match"
    assert res["was_corrected"] is True
    assert res["canonical_name"] == "Samsung Galaxy A51"
    assert len(res["options"]) >= 1


def test_typo_redmi_not_matches_redmi_note_13(catalogue):
    # Common user typo: "redmi not 13" -> "Xiaomi Redmi Note 13"
    res = match_device("xiaomi", "redmi not 13", catalogue)
    assert res["match_status"] == "fuzzy_match"
    assert res["was_corrected"] is True
    assert "Redmi Note 13" in res["canonical_name"]


def test_typo_pixl_matches_pixel_8a(catalogue):
    # Common user typo: "pixl 8a" -> "Google Pixel 8a"
    res = match_device("google", "pixl 8a", catalogue)
    assert res["match_status"] == "fuzzy_match"
    assert res["was_corrected"] is True
    assert res["canonical_name"] == "Google Pixel 8a"


def test_different_number_does_not_falsely_match(catalogue):
    # "iPhone 12" must NOT match "iPhone 13"
    res = match_device("apple", "iphone 12", catalogue)
    assert res["match_status"] == "not_found"
    assert res["was_corrected"] is False
    assert len(res["options"]) == 0

    conf = build_confirmation(res, None, user_confirmed=False, manual_ok=True)
    assert conf["unverified"] is True
    assert conf["matched_id"] is None


def test_unsupported_devices_fail_closed(catalogue):
    # Unsupported devices must NOT be forcibly matched
    for brand, model in [("oneplus", "9 pro"), ("nokia", "3310"), ("motorola", "g84")]:
        res = match_device(brand, model, catalogue)
        assert res["match_status"] == "not_found"
        assert res["was_corrected"] is False
        assert len(res["options"]) == 0
