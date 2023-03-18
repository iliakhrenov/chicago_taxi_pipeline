from dagster import Definitions, load_assets_from_modules

from . import assets
from . import chicago_taxi

defs = Definitions(assets=load_assets_from_modules([assets, chicago_taxi]))
