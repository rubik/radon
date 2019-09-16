import os
import json

import radon.cli as cli
from radon.cli.harvest import MIHarvester, RawHarvester, CCHarvester

from radon.tests.test_cli_harvest import (
        BASE_CONFIG, CC_CONFIG, RAW_CONFIG, MI_CONFIG,
)

DIRNAME = os.path.dirname(__file__)


def test_ipynb(log_mock):
    mi_cfg = cli.Config(
        **BASE_CONFIG.config_values,
    )
    mi_cfg.config_values.update(MI_CONFIG.config_values)
    mi_cfg.config_values['include_ipynb'] = True

    raw_cfg = cli.Config(
        **BASE_CONFIG.config_values,
    )
    raw_cfg.config_values.update(RAW_CONFIG.config_values)
    raw_cfg.config_values['include_ipynb'] = True

    cc_cfg = cli.Config(
        **BASE_CONFIG.config_values,
    )
    cc_cfg.config_values.update(CC_CONFIG.config_values)
    cc_cfg.config_values['include_ipynb'] = True

    mappings = {
        MIHarvester: mi_cfg,
        RawHarvester: raw_cfg,
        CCHarvester: cc_cfg,
    }
    target = 'data/'
    fnames = [os.path.join(DIRNAME, target),]
    for h_class, cfg in mappings.items():
        for f in fnames:
            harvester = h_class([f], cfg)
            out = harvester.as_json()
            assert not any(['error' in out])


def test_ipynb_with_cells(mocker, log_mock):
    mi_cfg = cli.Config(
        **BASE_CONFIG.config_values,
    )
    mi_cfg.config_values.update(MI_CONFIG.config_values)
    mi_cfg.config_values['include_ipynb'] = True
    mi_cfg.config_values['ipynb_cells'] = True

    raw_cfg = cli.Config(
        **BASE_CONFIG.config_values,
    )
    raw_cfg.config_values.update(RAW_CONFIG.config_values)
    raw_cfg.config_values['include_ipynb'] = True
    raw_cfg.config_values['ipynb_cells'] = True

    cc_cfg = cli.Config(
        **BASE_CONFIG.config_values,
    )
    cc_cfg.config_values.update(CC_CONFIG.config_values)
    cc_cfg.config_values['include_ipynb'] = True
    cc_cfg.config_values['ipynb_cells'] = True

    mappings = {
        MIHarvester: mi_cfg,
        RawHarvester: raw_cfg,
        CCHarvester: cc_cfg,
    }
    target = 'data/'
    fnames = [os.path.join(DIRNAME, target),]
    for h_class, cfg in mappings.items():
        for f in fnames:
            harvester = h_class([f], cfg)
            out = harvester.as_json()
            assert not any(['error' in out])


def test_raw_ipynb(log_mock):
    raw_cfg = cli.Config(
        **BASE_CONFIG.config_values,
    )
    raw_cfg.config_values.update(RAW_CONFIG.config_values)
    raw_cfg.config_values['include_ipynb'] = True
    raw_cfg.config_values['ipynb_cells'] = False

    target = os.path.join(DIRNAME, 'data/example.ipynb')
    harvester = RawHarvester([target], raw_cfg)
    out = json.loads(harvester.as_json())
    assert target in out
    assert out[target]['loc'] == 63
    assert out[target]['lloc'] == 37
    assert out[target]['sloc'] == 37
    assert out[target]['comments'] == 3
    assert out[target]['multi'] == 10
    assert out[target]['blank'] == 14
    assert out[target]['single_comments'] == 2


def test_raw_ipynb_cells(log_mock):
    raw_cfg = cli.Config(
        **BASE_CONFIG.config_values,
    )
    raw_cfg.config_values.update(RAW_CONFIG.config_values)
    raw_cfg.config_values['include_ipynb'] = True
    raw_cfg.config_values['ipynb_cells'] = True

    target = os.path.join(DIRNAME, 'data/example.ipynb')
    harvester = RawHarvester([target], raw_cfg)
    out = json.loads(harvester.as_json())
    cell_target = target + ":[3]"
    assert target in out
    assert cell_target in out
    assert out[cell_target]['loc'] == 52
    assert out[cell_target]['lloc'] == 27
    assert out[cell_target]['sloc'] == 27
    assert out[cell_target]['comments'] == 3
    assert out[cell_target]['multi'] == 10
    assert out[cell_target]['blank'] == 13
    assert out[cell_target]['single_comments'] == 2