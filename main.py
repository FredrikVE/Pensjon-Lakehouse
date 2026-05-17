#Pensjon-Lakehouse/main.py
from pensjon.di.dependencies import Dependencies
from pensjon.lakehouse.config import LakehouseConfig
from pensjon.lakehouse.pipeline import PensjonLakehousePipeline

if __name__ == "__main__":
    pipeline = PensjonLakehousePipeline(
        deps=Dependencies(),
        config=LakehouseConfig(),
    )

    pipeline.run()