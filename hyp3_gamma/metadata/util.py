import shutil
from glob import glob
from pathlib import Path


def populate_example_data(product_dir: Path):
    product_files = glob(str(Path(__file__).parent.parent / 'tests' / 'data' / 'rtc*'))
    for f in product_files:
        shutil.copy(f, product_dir / f'{Path(f).name.replace("rtc", product_dir.name)}')
