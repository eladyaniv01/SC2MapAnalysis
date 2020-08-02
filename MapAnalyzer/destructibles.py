"""
https://github.com/DrInfy/sharpy-sc2/blob/develop/sharpy/managers/unit_value.py
"""
from sc2 import UnitTypeId

buildings_2x2 = {
        UnitTypeId.SUPPLYDEPOT,
        UnitTypeId.PYLON,
        UnitTypeId.DARKSHRINE,
        UnitTypeId.PHOTONCANNON,
        UnitTypeId.SHIELDBATTERY,
        UnitTypeId.TECHLAB,
        UnitTypeId.STARPORTTECHLAB,
        UnitTypeId.FACTORYTECHLAB,
        UnitTypeId.BARRACKSTECHLAB,
        UnitTypeId.REACTOR,
        UnitTypeId.STARPORTREACTOR,
        UnitTypeId.FACTORYREACTOR,
        UnitTypeId.BARRACKSREACTOR,
        UnitTypeId.MISSILETURRET,
        UnitTypeId.SPORECRAWLER,
        UnitTypeId.SPIRE,
        UnitTypeId.GREATERSPIRE,
        UnitTypeId.SPINECRAWLER,
}

buildings_3x3 = {
        UnitTypeId.GATEWAY,
        UnitTypeId.WARPGATE,
        UnitTypeId.CYBERNETICSCORE,
        UnitTypeId.FORGE,
        UnitTypeId.ROBOTICSFACILITY,
        UnitTypeId.ROBOTICSBAY,
        UnitTypeId.TEMPLARARCHIVE,
        UnitTypeId.TWILIGHTCOUNCIL,
        UnitTypeId.TEMPLARARCHIVE,
        UnitTypeId.STARGATE,
        UnitTypeId.FLEETBEACON,
        UnitTypeId.ASSIMILATOR,
        UnitTypeId.ASSIMILATORRICH,
        UnitTypeId.SPAWNINGPOOL,
        UnitTypeId.ROACHWARREN,
        UnitTypeId.HYDRALISKDEN,
        UnitTypeId.BANELINGNEST,
        UnitTypeId.EVOLUTIONCHAMBER,
        UnitTypeId.NYDUSNETWORK,
        UnitTypeId.NYDUSCANAL,
        UnitTypeId.EXTRACTOR,
        UnitTypeId.EXTRACTORRICH,
        UnitTypeId.INFESTATIONPIT,
        UnitTypeId.ULTRALISKCAVERN,
        UnitTypeId.BARRACKS,
        UnitTypeId.ENGINEERINGBAY,
        UnitTypeId.FACTORY,
        UnitTypeId.GHOSTACADEMY,
        UnitTypeId.STARPORT,
        UnitTypeId.FUSIONREACTOR,
        UnitTypeId.BUNKER,
        UnitTypeId.ARMORY,
        UnitTypeId.REFINERY,
        UnitTypeId.REFINERYRICH,
}

buildings_5x5 = {
        UnitTypeId.NEXUS,
        UnitTypeId.HATCHERY,
        UnitTypeId.HIVE,
        UnitTypeId.LAIR,
        UnitTypeId.COMMANDCENTER,
        UnitTypeId.ORBITALCOMMAND,
        UnitTypeId.PLANETARYFORTRESS,
}

BUILDING_IDS = buildings_5x5.union(buildings_3x3).union(buildings_2x2)
