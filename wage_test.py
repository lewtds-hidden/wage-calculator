from datetime import datetime
from wage import parse_time, evening_hours, overtime, overtime_pay


def test_parse_time():
    assert parse_time("6.3.2014","5:00","10:00") == \
        (datetime(2014, 3, 6, 5, 0), datetime(2014, 3, 6, 10, 0))
    assert parse_time("6.3.2014","15:00","2:00") == \
        (datetime(2014, 3, 6, 15, 0), datetime(2014, 3, 7, 2, 0))
    assert parse_time("6.3.2014","15:00","0:0") == \
        (datetime(2014, 3, 6, 15, 0), datetime(2014, 3, 7, 0, 0))
    assert parse_time("06.03.2014","15:00","17:00") == \
        (datetime(2014, 3, 6, 15, 0), datetime(2014, 3, 6, 17, 0))
    assert parse_time("06.03.2014","15:00","17:12") == \
        (datetime(2014, 3, 6, 15, 0), datetime(2014, 3, 6, 17, 12))


def test_evening_hours():
    # not evening
    assert evening_hours(datetime(2014, 3, 6, 7, 0), \
                        datetime(2014, 3, 6, 8, 0)) == 0
    assert evening_hours(datetime(2014, 3, 6, 7, 0), \
                        datetime(2014, 3, 6, 18, 0)) == 0
    assert evening_hours(datetime(2014, 3, 6, 6, 0), \
                        datetime(2014, 3, 6, 18, 0)) == 0
    # evening
    assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                        datetime(2014, 3, 6, 19, 0)) == 1
    # crossing day boundary
    assert evening_hours(datetime(2014, 3, 6, 23, 0), \
                        datetime(2014, 3, 7, 1, 0)) == 2
    assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                        datetime(2014, 3, 7, 1, 0)) == 7
    assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                        datetime(2014, 3, 7, 6, 0)) == 12
    # not whole hours
    assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                        datetime(2014, 3, 7, 1, 15)) == 7.25
    assert evening_hours(datetime(2014, 3, 6, 18, 15), \
                        datetime(2014, 3, 7, 1, 15)) == 7
    # passing 6:00
    assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                        datetime(2014, 3, 7, 6, 15)) == 12
    # before 18:00
    assert evening_hours(datetime(2014, 3, 6, 15, 0), \
                        datetime(2014, 3, 7, 6, 0)) == 12


def test_overtime():
    assert list(overtime(0, [8, 2, 2])) == [0, 0, 0, 0]
    assert list(overtime(6, [8, 2, 2])) == [6, 0, 0, 0]
    assert list(overtime(8, [8, 2, 2])) == [8, 0, 0, 0]
    assert list(overtime(9, [8, 2, 2])) == [8, 1, 0, 0]
    assert list(overtime(10, [8, 2, 2])) == [8, 2, 0, 0]
    assert list(overtime(11, [8, 2, 2])) == [8, 2, 1, 0]
    assert list(overtime(12, [8, 2, 2])) == [8, 2, 2, 0]
    assert list(overtime(17, [8, 2, 2])) == [8, 2, 2, 5]

def test_overtime_pay():
    BASE_RATE = 3.75
    OVERTIME_STOPS = [8, 2, 2]
    OVERTIME_RATES = [p * BASE_RATE for p in [0, 0.25, 0.5, 1]]
    assert overtime_pay(8, OVERTIME_STOPS, OVERTIME_RATES) == 0
    assert overtime_pay(9, OVERTIME_STOPS, OVERTIME_RATES) == 0.9375
    assert overtime_pay(10, OVERTIME_STOPS, OVERTIME_RATES) == 1.875
    assert overtime_pay(11, OVERTIME_STOPS, OVERTIME_RATES) == 3.75
    assert overtime_pay(12, OVERTIME_STOPS, OVERTIME_RATES) == 5.625
    assert overtime_pay(13, OVERTIME_STOPS, OVERTIME_RATES) == 9.375


def test_totalpay():
    assert total_pay(datetime(2014, 3, 6, 7, 0),
                     datetime(2014, 3, 6, 10, 0)) == 11.25

    # night shift
    assert total_pay(datetime(2014, 3, 6, 18, 0),
                     datetime(2014, 3, 6, 19, 0)) == 4.9