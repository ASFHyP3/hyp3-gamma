from hyp3_gamma import __main__ as main


def test_earlier_granule_first():
    a = 'S1A_EW_GRDM_1SSH_20141112T235735_20141112T235835_003255_003C39_913F'
    b = 'S1A_EW_GRDM_1SSH_20141112T235835_20141112T235935_003255_003C39_D8E7'
    c = 'S1A_IW_SLC__1SDV_20200701T170703_20200701T170730_033264_03DA9B_CAB2'

    assert main.earlier_granule_first(a, a) == (a, a)

    assert main.earlier_granule_first(a, c) == (a, c)
    assert main.earlier_granule_first(c, a) == (a, c)

    assert main.earlier_granule_first(a, b) == (a, b)
    assert main.earlier_granule_first(b, a) == (a, b)
