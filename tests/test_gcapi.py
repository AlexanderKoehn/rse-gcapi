import pytest
from click.testing import CliRunner
from jsonschema import ValidationError

from gcapi import Client, cli
from gcapi.gcapi import LazyDict


def test_lazy_dict():
    ld = LazyDict(lambda: {1: 2})
    assert len(ld) == 1

    ld = LazyDict(lambda: {1: 2})
    assert ld[1] == 2


def test_no_auth_exception():
    with pytest.raises(RuntimeError):
        Client()


def test_headers():
    token = "foo"
    c = Client(token=token)
    assert c.headers["Authorization"] == f"TOKEN {token}"
    assert c.headers["Accept"] == "application/json"


def test_http_base_url():
    with pytest.raises(RuntimeError):
        Client(token="foo", base_url="http://example.com")


def test_custom_base_url():
    c = Client(token="foo")
    assert c._base_url.startswith("https://grand-challenge.org")

    c = Client(token="foo", base_url="https://example.com")
    assert c._base_url.startswith("https://example.com")


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "gcapi.cli.main" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


@pytest.mark.parametrize(
    "datetime_string,valid",
    (
        ("teststring", False),
        (1, False),
        ({}, False),
        ("2019-13-11T13:55:00.123456Z", False),
        ("2019-12-11T25:55:00.123456Z", False),
        ("2019-12-11T13:60:00.123456Z", False),
        ("2019-12-11T13:55:00.123456Z", True),
        ("2019-12-11T13:55:00Z", True),
    ),
)
def test_datetime_string_format_validation(datetime_string, valid):
    landmark_annotation = {
        "id": "4d5721f8-485d-4a17-8507-e06a8f897dd3",
        "grader": 7,
        "created": datetime_string,
        "singlelandmarkannotation_set": [
            {
                "id": "69ea96c2-9a96-4080-9b2c-0b9d0417dda1",
                "image": "70ec13fd-7fcf-4c84-bcd0-5fa3ac34a6b0",
                "landmarks": [
                    [249.029700179422, 194.950491966439],
                    [308.910901038675, 210.158411188267],
                    [270.891081357472, 353.683160558702],
                ],
            },
            {
                "id": "8055d041-d78d-4fa6-94af-1e57e80e11d8",
                "image": "46ba46f4-7fcd-418d-a43f-f668b286daeb",
                "landmarks": [
                    [759.567661360211, 495.505389057573],
                    [911.79182925945, 646.176269350096],
                    [672.582428997143, 726.948261175343],
                ],
            },
        ],
    }
    c = Client(verify=False, token="foo")
    if valid:
        assert (
            c.retina_landmark_annotations._verify_against_schema(
                landmark_annotation
            )
            is None
        )
    else:
        with pytest.raises(ValidationError):
            c.retina_landmark_annotations._verify_against_schema(
                landmark_annotation
            )
