from dataclasses import dataclass


@dataclass
class Position:
    market: str
    volume: float
    avg_price: float

    @property
    def total_value(self) -> float:
        return self.volume * self.avg_price

class PositionManager:
    def __init__(self):
        self.positions: dict[str, Position] = {}

    def get_position(self, market: str) -> Position | None:
        return self.positions.get(market)

    def get_volume(self, market: str) -> float:
        position = self.get_position(market)
        return position.volume if position else 0.0

    def get_position_value(self, market: str) -> float:
        position = self.get_position(market)
        return position.total_value if position else 0.0

    def apply_buy(self, market: str, price: float, volume: float) -> None:
        position = self.get_position(market)

        if position is None:
            self.positions[market] = Position(
                market=market,
                volume=volume,
                avg_price=price,
            )
            return

        total_cost = position.avg_price * position.volume + price * volume
        total_volume = position.volume + volume
        position.avg_price = total_cost / total_volume
        position.volume = total_volume

    def apply_sell(self, market: str, volume: float) -> None:
        position = self.get_position(market)

        if position is None:
            raise ValueError("보유 포지션이 없습니다.")

        if volume > position.volume:
            raise ValueError("보유 수량보다 많이 매도할 수 없습니다.")

        position.volume -= volume

        if position.volume == 0:
            del self.positions[market]