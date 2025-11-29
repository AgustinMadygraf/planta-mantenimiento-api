import unittest

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from src.interface_adapters.gateways.sqlalchemy.models import Base, PlantModel
from src.interface_adapters.gateways.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork


class SqlAlchemyUnitOfWorkTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False, class_=Session)

    def tearDown(self) -> None:
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_commit_persists_changes(self) -> None:
        uow = SqlAlchemyUnitOfWork(self.session_factory)

        with uow as active:
            active.session.add(PlantModel(name="Temporal", location="", status="operativa"))
            active.commit()

        with Session(self.engine) as check_session:
            count = check_session.scalar(select(func.count()).select_from(PlantModel))
            self.assertEqual(count, 1)

    def test_rollback_discards_changes_on_exception(self) -> None:
        uow = SqlAlchemyUnitOfWork(self.session_factory)

        with self.assertRaises(RuntimeError):
            with uow as active:
                active.session.add(PlantModel(name="Temporal", location="", status="operativa"))
                raise RuntimeError("Force rollback")

        with Session(self.engine) as check_session:
            count = check_session.scalar(select(func.count()).select_from(PlantModel))
            self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
