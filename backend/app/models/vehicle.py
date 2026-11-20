from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    brand: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    license_plate: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    fuel_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    average_consumption: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)

    driver: Mapped["Driver"] = relationship(back_populates="vehicles")
