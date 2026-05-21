from src.game.abilities.fire_blast import FireBlastStrategy
from src.game.abilities.freeze_ray import FreezeRayStrategy
from src.game.abilities.thunder_chain import ThunderChainStrategy
from src.game.abilities.tidal_wave import TidalWaveStrategy


_singletons = {
    FireBlastStrategy.name: FireBlastStrategy(),
    FreezeRayStrategy.name: FreezeRayStrategy(),
    ThunderChainStrategy.name: ThunderChainStrategy(),
    TidalWaveStrategy.name: TidalWaveStrategy(),
}


def get(name):
    """Yetenek adina karsilik gelen Strategy instance'ini dondurur."""
    strategy = _singletons.get(name)
    if strategy is None:
        raise ValueError(
            f"Bilinmeyen yetenek: {name}. "
            f"Mevcut: {sorted(_singletons.keys())}"
        )
    return strategy


def register(strategy):
    """Yeni Strategy ekle (OCP: engine'e dokunmadan yeni yetenek)."""
    _singletons[strategy.name] = strategy


def all_names():
    return list(_singletons.keys())
