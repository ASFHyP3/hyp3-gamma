from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape


def get_environment():
    env = Environment(
        loader=PackageLoader('hyp3_metadata', 'GAMMA'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    return env


def render_template(template: str, payload: dict):
    env = get_environment()
    template = env.get_template(template)
    rendered = template.render(payload)
    return rendered


def get_dem_resolution(dem_name):
    data = {
        'NED13': '1/3 arc seconds (about 10 meters)',
        'NED1': '1 arc second (about 30 meters)',
        'NED2': '2 arc seconds (about 60 meters)',
        'SRTMGL1': '1 arc second (about 30 meters)',
        'SRTMGL3': '3 arc seconds (about 90 meters)',
    }
    return data[dem_name]


def create_rtc_gamma_readme(readme_filename: Path, granule_name: str, resolution: float, gamma_flag: bool,
                            power_flag: bool, filter_applied: bool, looks: int, projection: str, dem_name: str,
                            plugin_version: str, gamma_version: str, processing_date: datetime):
    payload = locals()
    payload['dem_resolution'] = get_dem_resolution(dem_name)
    content = render_template('RTC/README_RTC_GAMMA.txt', payload)
    with open(readme_filename, 'w') as f:
        f.write(content)
