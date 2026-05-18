import sys
from pensjon.lakehouse.pipeline import PensjonLakehousePipeline

if __name__ == "__main__":
    use_testdata = "--testdata" in sys.argv
    pipeline = PensjonLakehousePipeline(use_testdata=use_testdata)
    pipeline.run()
