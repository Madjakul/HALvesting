# test_preprocessing.py

import logging
from datetime import datetime

import pytest
from lxml import etree

from halvesting.utils.data.preprocessing import extract_year, format_hal


@pytest.fixture
def sample_xml():
    # Sample XML data for testing format_hal
    xml_str = """
    <text>
        <listbibl>
            <biblfull>
                <idno type="halId">hal-id-1</idno>
                <editionstmt>
                    <edition>
                        <ref subtype="author" target="file1.pdf"/>
                        <date type="whenProduced">2023-01-01</date>
                    </edition>
                </editionstmt>
                <profiledesc>
                    <langusage>
                        <language ident="en"/>
                    </langusage>
                    <textclass>
                        <classcode scheme="halDomain" n="CS"/>
                    </textclass>
                </profiledesc>
            </biblfull>
        </listbibl>
    </text>
    """
    return etree.fromstring(xml_str)


def test_extract_year():
    # Test extract_year function
    assert extract_year("2023-01-01") == "2023"
    assert extract_year("2023-01") == "2023"
    assert extract_year("2023") == "2023"
    assert extract_year("invalid-date") == "1"


def test_format_hal(sample_xml, monkeypatch, caplog):
    # Mocking datetime.now() to have a consistent timestamp for testing
    def mock_datetime_now():
        return datetime(2023, 1, 1)

    monkeypatch.setattr("datetime.datetime.now", mock_datetime_now)

    # Capture logs to check if warnings are logged
    caplog.set_level(logging.WARNING)

    # Test format_hal function
    result = format_hal(sample_xml)

    assert len(result) == 1
    assert result[0]["halid"] == "id-1"
    assert result[0]["lang"] == "en"
    assert result[0]["domain"] == ["CS"]
    assert result[0]["timestamp"] == "2023/01/01 00:00:00"
    assert result[0]["year"] == "2023"
    assert result[0]["url"] == "file1.pdf"

    # Check if warning is logged for invalid date format
    assert "Error parsing date: invalid-date" in caplog.text
