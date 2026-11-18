import os
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from app.database import Base
from app.models import Calculation, Division, User
from app.schemas import CalculationCreate, CalculationRead, CalculationType


@pytest.fixture
def postgres_engine():
    database_url = os.environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL integration tests")

    schema = f"test_calculation_{uuid4().hex}"
    engine = create_engine(
        database_url, execution_options={"schema_translate_map": {None: schema}}
    )
    try:
        assert engine.dialect.name == "postgresql"
        with engine.begin() as connection:
            connection.execute(CreateSchema(schema))
            Base.metadata.create_all(connection)
        try:
            yield engine
        finally:
            with engine.begin() as connection:
                connection.execute(DropSchema(schema, cascade=True))
    finally:
        engine.dispose()


def test_calculation_round_trip(postgres_engine):
    with Session(postgres_engine) as session:
        user = User(username="calculator", email="calculator@example.com")
        session.add(user)
        session.flush()
        user_id = user.id
        data = CalculationCreate(a=12.5, b=2, type="Divide")
        calculation = Calculation.from_create(data, user_id=user_id)
        session.add(calculation)
        session.flush()
        calculation_id = calculation.id
        session.commit()

    with Session(postgres_engine) as session:
        stored = session.scalar(select(Calculation).where(Calculation.a == 12.5))
        assert isinstance(stored, Division)
        assert stored.id == calculation_id
        assert stored.inputs == [12.5, 2]
        assert stored.user.username == "calculator"
        assert stored.result is None
        assert CalculationRead.model_validate(stored).model_dump() == {
            "id": calculation_id,
            "user_id": user_id,
            "a": 12.5,
            "b": 2,
            "type": CalculationType.DIVISION,
            "result": 6.25,
        }


@pytest.mark.parametrize(
    ("operation", "b"), [("Power", 2), ("Divide", 0)]
)
def test_invalid_calculation_leaves_database_empty(postgres_engine, operation, b):
    with Session(postgres_engine) as session:
        user = User(username="calculator", email="calculator@example.com")
        session.add(user)
        session.commit()

        with pytest.raises(ValidationError):
            data = CalculationCreate(a=12, b=b, type=operation)
            session.add(Calculation.from_create(data, user_id=user.id))
            session.commit()

        assert session.scalar(select(func.count()).select_from(Calculation)) == 0


def test_postgres_rejects_unknown_owner(postgres_engine):
    data = CalculationCreate(a=1, b=2, type="Add")
    with Session(postgres_engine) as session:
        session.add(Calculation.from_create(data, user_id=uuid4()))
        with pytest.raises(IntegrityError) as error:
            session.commit()
        assert error.value.orig.pgcode == "23503"
        session.rollback()
        assert session.scalar(select(func.count()).select_from(Calculation)) == 0
