from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models import Addition, Calculation, Division, Multiplication, Subtraction
from app.schemas import CalculationCreate


@pytest.mark.parametrize(
    ("operation", "model_type", "expected"),
    [
        ("Add", Addition, 15),
        ("Sub", Subtraction, 9),
        ("Multiply", Multiplication, 36),
        ("Divide", Division, 4),
    ],
)
def test_factory_creates_each_operation(operation, model_type, expected):
    data = CalculationCreate(a=12, b=3, type=operation)
    calculation = Calculation.from_create(data, user_id=uuid4())

    assert isinstance(calculation, model_type)
    assert (calculation.a, calculation.b) == (12, 3)
    assert calculation.get_result() == expected


@pytest.mark.parametrize(
    "data",
    [
        {"a": 1, "b": 2, "type": "Power"},
        {"a": 1, "b": -0.0, "type": "Divide"},
        {"a": "invalid", "b": 2, "type": "Add"},
        {"a": True, "b": 2, "type": "Add"},
        {"a": 1, "b": float("inf"), "type": "Add"},
        {"a": float("nan"), "b": 2, "type": "Add"},
        {"a": 1, "type": "Add"},
    ],
)
def test_create_rejects_invalid_data(data):
    with pytest.raises(ValidationError):
        CalculationCreate.model_validate(data)


def test_factory_rejects_overflow():
    data = CalculationCreate(a=1e308, b=10, type="Multiply")
    with pytest.raises(ValueError, match="result must be finite"):
        Calculation.from_create(data, user_id=uuid4())
