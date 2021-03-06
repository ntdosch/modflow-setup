"""
Test setup of temporal discretization (perioddata table attribute).

See documentation for pandas.date_range method for generating time discretization,
and the reference within on frequency strings.

https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.date_range.html
https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
"""
import copy
import numpy as np
import pandas as pd
import pytest
from mfsetup.tdis import get_parent_stress_periods
from .test_pleasant_mf6_inset import get_pleasant_mf6


@pytest.fixture(scope='function')
def pd0(shellmound_model):
    """Perioddata defined in shellmound.yml config file.
    3 groups:
    1) initial steady-state
    2) single transient period with start and end date
    3) frequency-defined periods with start and end date
    """
    m = shellmound_model #deepcopy(model)
    pd0 = m.perioddata.copy()
    return pd0


@pytest.fixture(scope='function')
def pd1(shellmound_model):
    """Perioddata defined with start_date_time, nper, perlen, nstp, and tsmult
    specified explicitly.
    """
    m = shellmound_model
    m.cfg['sto']['steady'] = {0: True,
                              1: False}

    # Explicit stress period setup
    nper = 11  # total number of MODFLOW periods (including initial steady-state)
    m.cfg['tdis']['perioddata'] = {}
    m.cfg['tdis']['options']['start_date_time'] = '2008-10-01'
    m.cfg['tdis']['perioddata']['perlen'] = [1] * nper
    m.cfg['tdis']['perioddata']['nstp'] = [5] * nper
    m.cfg['tdis']['perioddata']['tsmult'] = 1.5
    m._perioddata = None
    pd1 = m.perioddata.copy()
    return pd1


@pytest.fixture(scope='function')
def pd2(shellmound_model):
    """Perioddata defined with start_date_time, frequency and nper.
    """
    m = shellmound_model
    m.cfg['tdis']['options']['end_date_time'] = None
    m.cfg['tdis']['perioddata']['perlen'] = None
    m.cfg['tdis']['dimensions']['nper'] = 11
    m.cfg['tdis']['perioddata']['freq'] = 'D'
    m.cfg['tdis']['perioddata']['nstp'] = 5
    m.cfg['tdis']['perioddata']['tsmult'] = 1.5
    m._perioddata = None
    pd2 = m.perioddata.copy()
    return pd2


@pytest.fixture(scope='function')
def pd3(shellmound_model):
    """Perioddata defined with start_date_time, end_datetime, and nper
    """
    m = shellmound_model
    m.cfg['tdis']['perioddata']['end_date_time'] = '2008-10-11'
    m.cfg['tdis']['perioddata']['freq'] = None
    m._perioddata = None
    pd3 = m.perioddata.copy()
    return pd3


@pytest.fixture(scope='function')
def pd4(shellmound_model):
    """Perioddata defined with start_date_time, end_datetime, and freq.
    """
    m = shellmound_model
    m.cfg['tdis']['perioddata']['freq'] = 'D'
    m._perioddata = None
    pd4 = m.perioddata.copy()
    return pd4


@pytest.fixture(scope='function')
def pd5(shellmound_model):
    """Perioddata defined with end_datetime, freq and nper.
    """
    m = shellmound_model
    m.cfg['tdis']['options']['start_date_time'] = None
    m.cfg['tdis']['perioddata']['end_date_time'] = '2008-10-12'
    m._perioddata = None
    pd5 = m.perioddata.copy()
    return pd5


@pytest.fixture(scope='function')
def pd6(shellmound_model):
    """Perioddata defined with month-end frequency
    """
    m = shellmound_model
    # month end vs month start freq
    m.cfg['tdis']['perioddata']['freq'] = '6M'
    m.cfg['tdis']['options']['start_date_time'] = '2007-04-01'
    m.cfg['tdis']['perioddata']['end_date_time'] = '2015-10-01'
    m.cfg['tdis']['perioddata']['nstp'] = 15
    m._perioddata = None
    pd6 = m.perioddata.copy()
    return pd6


def test_pd0_freq_last_end_date_time(shellmound_model, pd0):
    """When perioddata are set-up based on start date, end date and freq,
    verify that the last end-date is the beginning of the next day (end of end-date)."""
    m = shellmound_model
    assert pd0 is not None
    assert pd0['end_datetime'].iloc[-1] == \
           pd.Timestamp(m.cfg['tdis']['perioddata']['group 3']['end_date_time']) + pd.Timedelta(1, unit='d')


def test_pd1_explicit_perioddata_setup(pd1, shellmound_model):
    """Test perioddata setup with start_date_time, nper, perlen, nstp, and tsmult
    specified explicitly.
    """
    m = shellmound_model
    assert pd1['start_datetime'][0] == pd1['start_datetime'][1] == pd1['end_datetime'][0]
    assert pd1['end_datetime'][1] == pd.Timestamp(m.cfg['tdis']['options']['start_date_time']) + \
           pd.Timedelta(m.cfg['tdis']['perioddata']['perlen'][1], unit=m.time_units)
    assert pd1['nstp'][0] == 1
    assert pd1['tsmult'][0] == 1


@pytest.mark.skip("still need to fix this; workaround in the meantime is just to specify an extra period")
def test_pd2_start_date_freq_nper(pd1, pd2):
    """Since perlen wasn't explicitly specified,
    pd2 will have the 11 periods at freq 'D' (like pd1)
    but with a steady-state first stress period of length 1
    in other words, perlen discretization with freq
    only applies to transient stress periods
    """
    assert pd2.iloc[:-1].equals(pd1)


def test_pd3_start_end_dates_nper(pd1, pd3):
    assert pd3.equals(pd1)


def test_pd4_start_end_dates_freq(pd1, pd4):
    assert pd4.equals(pd1)


@pytest.mark.skip("still need to fix this")
def test_pd5_end_date_freq_nper(pd1, pd5):
    assert pd5.iloc[:-1].equals(pd1)


@pytest.mark.skip(reason='incomplete')
def test_pd6(pd0, pd6):
    pd0_g1_3 = pd.concat([pd0.iloc[:1], pd0.iloc[2:]])
    for c in pd0_g1_3[['perlen', 'start_datetime', 'end_datetime']]:
        assert np.array_equal(pd6[c].values, pd0_g1_3[c].values)


def test_pd_date_range():
    """Test that pandas date range is producing the results we expect.
    """
    dates = pd.date_range('2007-04-01', '2015-10-01', periods=None, freq='6MS')
    assert len(dates) == 18
    assert dates[-1] == pd.Timestamp('2015-10-01')


@pytest.mark.parametrize('copy_periods, nper', (('all', 'm.nper'),  # copy all stress periods
                                                ('all', 13),  # copy all stress periods up to 13
                                                ([0], 'm.nper'),  # repeat parent stress period 0
                                                ([2], 'm.nper'),  # repeat parent stress period 2
                                                ([1, 2], 'm.nper')  # include parent stress periods 1 and 2, repeating 2
                                                ))
def test_get_parent_stress_periods(copy_periods, nper, basic_model_instance, request):
    m = basic_model_instance
    if nper == 'm.nper':
        nper = m.nper
    test_name = request.node.name.split('[')[1].strip(']')
    if m.name == 'pfl' and copy_periods not in ('all', [0]):
        return
    expected = {'pfl_nwt-all-m.nper': [0, 0],  # one parent model stress period, 'all' input
                'pfl_nwt-all-13': [0] * nper,  # one parent model stress period, 'all' input
                'pfl_nwt-copy_periods2-m.nper': [0, 0],  # one parent model stress period, input=[0]
                'pleasant_nwt-all-m.nper': list(range(nper)),  # many parent model stress periods, input='all'
                'pleasant_nwt-all-13': list(range(nper)),  # many parent model stress periods, input='all'
                'pleasant_nwt-copy_periods2-m.nper': [0]*nper,  # many parent model stress periods, input=[0]
                'pleasant_nwt-copy_periods3-m.nper': [2] * nper,   # many parent model stress periods, input=[2]
                'pleasant_nwt-copy_periods4-m.nper': [1] + [2] * (nper-1),    # many parent model stress periods, input=[1, 2]
                'get_pleasant_mf6-all-m.nper': list(range(nper)),
                'get_pleasant_mf6-all-13': list(range(nper)),
                'get_pleasant_mf6-copy_periods2-m.nper': [0]*nper,
                'get_pleasant_mf6-copy_periods3-m.nper': [2] * nper,
                'get_pleasant_mf6-copy_periods4-m.nper': [1] + [2] * (nper-1),
                }

    # test getting list of parent stress periods corresponding to inset stress periods
    result = get_parent_stress_periods(m.parent, nper=nper,
                                       parent_stress_periods=copy_periods)
    assert result == expected[test_name]
    assert len(result) == nper
    assert not any(set(result).difference(set(range(m.parent.nper))))

    # test adding parent stress periods to perioddata table
    m.cfg['parent']['copy_stress_periods'] = copy_periods
    if m.version != 'mf6':
        m.cfg['dis']['nper'] = nper
        for var in ['perlen', 'nstp', 'tsmult', 'steady']:
            del m.cfg['dis'][var]
    m._set_parent()
    m._set_perioddata()
    assert np.array_equal(m.perioddata['parent_sp'], np.array(expected[test_name]))
