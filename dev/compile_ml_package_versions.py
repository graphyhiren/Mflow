"""
Compiles ml-package-versions.yml into ml_package_versions.py
"""
import yaml
import json
from pathlib import Path


def extract_field(d, keys):
    for key in keys:
        if key in d:
            d = d[key]
        else:
            return None
    return d


def generate_ml_package_versions_py():
    with Path("mlflow", "ml-package-versions.yml").open() as f:
        config = {}
        for name, cfg in yaml.load(f, Loader=yaml.SafeLoader).items():
            # Extract required fields
            pip_release = extract_field(cfg, ("package_info", "pip_release"))
            min_version = extract_field(cfg, ("autologging", "minimum"))
            max_version = extract_field(cfg, ("autologging", "maximum"))
            if (pip_release, min_version, max_version).count(None) > 0:
                continue

            config[name] = {
                "package_info": {
                    "pip_release": pip_release,
                },
                "autologging": {
                    "minimum": min_version,
                    "maximum": max_version,
                },
            }

        this_file = Path(__file__).resolve().relative_to(Path.cwd())
        dst = Path("mlflow", "ml_package_versions.py")
        config = json.dumps(config, indent=4)
        Path(dst).write_text(
            f"""\
# This file was auto-generated by {this_file}. Please do not edit it manually.

_ML_PACKAGE_VERSIONS = {config}
"""
        )


def main():
    generate_ml_package_versions_py()


if __name__ == "__main__":
    main()
