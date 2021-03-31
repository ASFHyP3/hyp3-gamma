import shutil
from glob import glob
from pathlib import Path

from hyp3_metadata import data

SUPPORTED_DEMS = ['EU_DEM_V11', 'GIMP', 'IFSAR', 'NED13', 'NED1', 'NED2', 'REMA', 'SRTMGL1', 'SRTMGL3', 'GLO-30']


def populate_example_data(product_dir: Path):
    product_files = glob(str(Path(data.__file__).parent / 'rtc*'))
    for f in product_files:
        shutil.copy(f, product_dir / f'{Path(f).name.replace("rtc", product_dir.name)}')
