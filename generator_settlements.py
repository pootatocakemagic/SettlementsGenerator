from settlement_generators.FortressGenerator import FortressGenerator as Fortress
from settlement_generators.CapitalGenerator import CapitalGenerator as Capital
from settlement_generators.CityGenerator import CityGenerator as City
from settlement_generators.TownGenerator import TownGenerator as Town
from settlement_generators.VillageGenerator import VillageGenerator as Village
from settlement_generators.TradingPostGenerator import TradingPostGenerator as TradingPost


if __name__ == "__main__":
    trading_post = TradingPost()
    print(trading_post.total_info)