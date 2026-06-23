from analytics import Analytics, Event
import pytest
from datetime import datetime, timedelta

def test_capture_event():
    analytics = Analytics()
    analytics.capture_event('page_view')
    assert len(analytics.events) == 1
    assert analytics.events[0].type == 'page_view'

def test_get_daily_active_users():
    analytics = Analytics()
    analytics.capture_event('page_view')
    analytics.capture_event('click')
    analytics.capture_event('conversion')
    daily_users = analytics.get_daily_active_users()
    assert len(daily_users) == 1
    assert daily_users[list(daily_users.keys())[0]] == 3

def test_get_conversion_rates():
    analytics = Analytics()
    analytics.capture_event('page_view')
    analytics.capture_event('click')
    analytics.capture_event('conversion')
    conversion_rates = analytics.get_conversion_rates()
    assert len(conversion_rates) == 1
    assert conversion_rates[list(conversion_rates.keys())[0]] == 1

def test_get_dashboard_data():
    analytics = Analytics()
    analytics.capture_event('page_view')
    analytics.capture_event('click')
    analytics.capture_event('conversion')
    dashboard_data = analytics.get_dashboard_data()
    assert 'daily_active_users' in dashboard_data
    assert 'conversion_rates' in dashboard_data

def test_get_dashboard_data_empty():
    analytics = Analytics()
    dashboard_data = analytics.get_dashboard_data()
    assert dashboard_data == {'daily_active_users': {}, 'conversion_rates': {}}

def test_capture_event_edge_case():
    analytics = Analytics()
    analytics.capture_event('invalid_event')
    assert len(analytics.events) == 1
    assert analytics.events[0].type == 'invalid_event'
