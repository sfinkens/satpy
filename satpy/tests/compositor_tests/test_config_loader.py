#!/usr/bin/env python
# Copyright (c) 2018-2025 Satpy developers
#
# This file is part of satpy.
#
# satpy is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# satpy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# satpy.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for compositor config handling."""

from typing import Optional

import pytest

import satpy
from satpy.composites.config_loader import load_compositor_configs_for_sensors


def test_bad_sensor_yaml_configs(tmp_path):
    """Test composite YAML file with no sensor isn't loaded.

    But the bad YAML also shouldn't crash composite configuration loading.

    """
    comp_dir = tmp_path / "composites"
    comp_dir.mkdir()
    comp_yaml = comp_dir / "fake_sensor.yaml"
    with satpy.config.set(config_path=[tmp_path]):
        _create_fake_composite_config(comp_yaml)

        # no sensor_name in YAML, quietly ignored
        comps, _ = load_compositor_configs_for_sensors(["fake_sensor"])
        assert "fake_sensor" in comps
        assert "fake_composite" not in comps["fake_sensor"]


def _create_fake_composite_config(yaml_filename: str, extra_content: Optional[dict]=None):
    import yaml

    from satpy.composites.aux_data import StaticImageCompositor
    content = {
        "composites": {
            "fake_composite": {
                "compositor": StaticImageCompositor,
                "url": "http://example.com/image.png",
            }
        }
    }
    if extra_content:
        content.update(extra_content)
    with open(yaml_filename, "w") as comp_file:
        yaml.dump(content, comp_file)


# 8< v1.0
class TestUserConfigWithDeprecatedSensorNameProperty:
    """Test loading user config with deprecated sensor_name property."""

    @pytest.fixture
    def user_comp_dir(self, tmp_path):
        """Get directory with user composites."""
        return tmp_path / "etc" / "composites"

    @pytest.fixture
    def user_config_file(self, user_comp_dir):
        """Write user config with old sensor_name property."""
        filename = user_comp_dir / "myinstrument.yaml"
        user_comp_dir.mkdir(parents=True)
        _create_fake_composite_config(filename, {"sensor_name": "myinstrument"})

    def test_finding_user_config(self, user_comp_dir, user_config_file):
        """Test loading user config with deprecated sensor_name property."""
        with satpy.config.set(config_path=[str(user_comp_dir.parent)]):
            with pytest.warns(DeprecationWarning, match="Use 'instrument' instead."):
                comps, _ = load_compositor_configs_for_sensors(["MyInstrument"])
            assert "MyInstrument" in comps
# >8 v1.0
