from dagster import Definitions, load_assets_from_modules

from . import assets_ingest, assets_marts, assets_checks, assets_analysis, assets_uplift, assets_reporting

all_assets = load_assets_from_modules([assets_ingest, assets_marts, assets_checks, assets_analysis, assets_uplift, assets_reporting])

defs = Definitions(
    assets=all_assets,
)
