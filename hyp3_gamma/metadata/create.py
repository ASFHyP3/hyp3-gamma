from datetime import datetime
from pathlib import Path
from typing import List

from hyp3_gamma.metadata import insar, rtc


def create_metadata_file_set_rtc(
    product_dir: Path,
    granule_name: str,
    dem_name: str,
    processing_date: datetime,
    looks: int,
    plugin_name: str,
    plugin_version: str,
    processor_name: str,
    processor_version: str,
) -> List[Path]:
    payload = rtc.marshal_metadata(
        product_dir=product_dir,
        granule_name=granule_name,
        dem_name=dem_name,
        processing_date=processing_date,
        looks=looks,
        plugin_name=plugin_name,
        plugin_version=plugin_version,
        processor_name=processor_name,
        processor_version=processor_version,
    )
    writer = rtc.RtcMetadataWriter(payload)

    return writer.create_metadata_file_set()


def create_metadata_file_set_insar(
    product_dir: Path,
    reference_granule_name: str,
    secondary_granule_name: str,
    processing_date: datetime,
    looks: str,
    dem_name: str,
    water_mask_applied: bool,
    plugin_name: str,
    plugin_version: str,
    processor_name: str,
    processor_version: str,
    ref_point_coords: dict,
    phase_filter_parameter: float,
) -> List[Path]:
    payload = insar.marshal_metadata(
        product_dir=product_dir,
        reference_granule_name=reference_granule_name,
        secondary_granule_name=secondary_granule_name,
        processing_date=processing_date,
        looks=looks,
        dem_name=dem_name,
        water_mask_applied=water_mask_applied,
        plugin_name=plugin_name,
        plugin_version=plugin_version,
        processor_name=processor_name,
        processor_version=processor_version,
        ref_point_coords=ref_point_coords,
        phase_filter_parameter=phase_filter_parameter,
    )
    writer = insar.InSarMetadataWriter(payload)
    return writer.create_metadata_file_set()
