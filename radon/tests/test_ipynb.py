import json
import os

import pytest

import radon.cli as cli
from radon.cli.harvest import (
    SUPPORTS_IPYNB,
    CCHarvester,
    Harvester,
    MIHarvester,
    RawHarvester,
)
from radon.cli.tools import _is_python_file
from radon.tests.test_cli_harvest import MI_CONFIG, RAW_CONFIG

BASE_CONFIG_WITH_IPYNB = cli.Config(
    exclude="*.py", ignore=None, include_ipynb=True, ipynb_cells=False,
)

BASE_CONFIG_WITH_IPYNB_AND_CELLS = cli.Config(
    exclude="*.py", ignore=None, include_ipynb=True, ipynb_cells=True,
)

DIRNAME = os.path.dirname(__file__)


@pytest.mark.skipif(not SUPPORTS_IPYNB, reason="nbformat not installed")
def test_harvestor_yields_ipynb(log_mock):
    '''Test that Harvester will try ipynb files when configured'''
    target = os.path.join(DIRNAME, 'data', 'example.ipynb')
    harvester = Harvester([DIRNAME], BASE_CONFIG_WITH_IPYNB)
    filenames = list(harvester._iter_filenames())
    assert _is_python_file(target)
    assert len(filenames) == 1
    assert target in filenames


@pytest.mark.skipif(not SUPPORTS_IPYNB, reason="nbformat not installed")
def test_ipynb(log_mock):
    mi_cfg = cli.Config(**BASE_CONFIG_WITH_IPYNB.config_values)
    mi_cfg.config_values.update(MI_CONFIG.config_values)
    raw_cfg = cli.Config(**BASE_CONFIG_WITH_IPYNB.config_values)
    raw_cfg.config_values.update(RAW_CONFIG.config_values)
    cc_cfg = cli.Config(
        order=lambda block: block.name,
        no_assert=False,
        min='A',
        max='F',
        show_complexity=False,
        show_closures=False,
        average=True,
        total_average=False,
    )
    cc_cfg.config_values.update(BASE_CONFIG_WITH_IPYNB.config_values)

    mappings = {
        MIHarvester: mi_cfg,
        RawHarvester: raw_cfg,
        CCHarvester: cc_cfg,
    }
    target = 'data/'
    fnames = [
        os.path.join(DIRNAME, target),
    ]
    for h_class, cfg in mappings.items():
        for f in fnames:
            harvester = h_class([f], cfg)
            out = harvester.as_json()
            assert not any(['error' in out]), out


@pytest.mark.skipif(not SUPPORTS_IPYNB, reason="nbformat not installed")
def test_ipynb_with_cells(mocker, log_mock):
    mi_cfg = cli.Config(**BASE_CONFIG_WITH_IPYNB_AND_CELLS.config_values)
    mi_cfg.config_values.update(MI_CONFIG.config_values)
    raw_cfg = cli.Config(**BASE_CONFIG_WITH_IPYNB_AND_CELLS.config_values)
    raw_cfg.config_values.update(RAW_CONFIG.config_values)
    cc_cfg = cli.Config(
        order=lambda block: block.name,
        no_assert=False,
        min='A',
        max='F',
        show_complexity=False,
        show_closures=False,
        average=True,
        total_average=False,
    )
    cc_cfg.config_values.update(BASE_CONFIG_WITH_IPYNB_AND_CELLS.config_values)

    mappings = {
        MIHarvester: mi_cfg,
        RawHarvester: raw_cfg,
        CCHarvester: cc_cfg,
    }
    target = 'data/'
    fnames = [
        os.path.join(DIRNAME, target),
    ]
    for h_class, cfg in mappings.items():
        for f in fnames:
            harvester = h_class([f], cfg)
            out = harvester.as_json()
            assert not any(['error' in out]), out


@pytest.mark.skipif(not SUPPORTS_IPYNB, reason="nbformat not installed")
def test_raw_ipynb(log_mock):
    raw_cfg = cli.Config(**BASE_CONFIG_WITH_IPYNB.config_values)

    target = os.path.join(DIRNAME, 'data', 'example.ipynb')
    harvester = RawHarvester([DIRNAME], raw_cfg)
    out = json.loads(harvester.as_json())

    assert harvester.config.include_ipynb is True
    assert target in out

    for key, value in (
        ('loc', 63),
        ('lloc', 37),
        ('sloc', 37),
        ('comments', 3),
        ('multi', 10),
        ('blank', 14),
        ('single_comments', 2),
    ):
        assert out[target][key] == value


@pytest.mark.skipif(not SUPPORTS_IPYNB, reason="nbformat not installed")
def test_raw_ipynb_cells(log_mock):
    raw_cfg = cli.Config(**BASE_CONFIG_WITH_IPYNB_AND_CELLS.config_values)

    target = os.path.join(DIRNAME, 'data', 'example.ipynb')
    harvester = RawHarvester([DIRNAME], raw_cfg)
    out = json.loads(harvester.as_json())
    cell_target = target + ":[3]"

    assert target in out
    assert cell_target in out

    for key, value in (
        ('loc', 52),
        ('lloc', 27),
        ('sloc', 27),
        ('comments', 3),
        ('multi', 10),
        ('blank', 13),
        ('single_comments', 2),
    ):
        assert out[cell_target][key] == value
