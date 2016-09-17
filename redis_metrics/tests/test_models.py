"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from __future__ import unicode_literals
from datetime import datetime, timedelta
try:
    from unittest.mock import call, patch, Mock
except ImportError:
    from mock import call, patch, Mock

from django.test import TestCase
from django.test.utils import override_settings

from ..models import R, dedupe


TEST_SETTINGS = {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
    'SOCKET_TIMEOUT': None,
    'SOCKET_CONNECTION_POOL': None,
    'MIN_GRANULARITY': 'seconds',
    'MAX_GRANULARITY': 'yearly',
    'MONDAY_FIRST_DAY_OF_WEEK': False,
}


@override_settings(REDIS_METRICS=TEST_SETTINGS)
class TestR(TestCase):
    """Tests for the ``R`` class."""

    def setUp(self):
        # Patch the connection to redis, but keep a reference to the
        # created StrictRedis instance, so we can make assertions about how
        # it's called.
        self.redis_patcher = patch('redis_metrics.models.redis.StrictRedis')
        mock_StrictRedis = self.redis_patcher.start()
        self.redis = mock_StrictRedis.return_value
        self.r = R()

    def tearDown(self):
        self.redis = self.redis_patcher.stop()
        super(TestR, self).tearDown()

    def test_dedupe(self):
        """Test the redis_metrics.models.dedupe function."""
        self.assertEqual(
            list(dedupe(['a', 'a', 'b', 'c', 'b', 'c', 'c', 'c'])),
            ['a', 'b', 'c']
        )

    def test__init__(self):
        """Test creation of an R object with parameters."""
        with patch('redis_metrics.models.redis.StrictRedis') as mock_redis:
            kwargs = {
                'decode_responses': True,
                'categories_key': 'CAT',
                'metric_slugs_key': 'MSK',
                'gauge_slugs_key': 'GSK',
                'host': 'HOST',
                'port': 'PORT',
                'db': 'DB',
                'password': 'PASSWORD',
                'socket_timeout': 1,
                'connection_pool': 1
            }
            inst = R(**kwargs)
            self.assertEqual(inst.host, "HOST")
            self.assertEqual(inst.port, "PORT")
            self.assertEqual(inst.db, "DB")
            self.assertEqual(inst.password, 'PASSWORD')
            self.assertEqual(inst.socket_timeout, 1)
            self.assertEqual(inst.connection_pool, 1)
            self.assertEqual(inst._categories_key, "CAT")
            self.assertEqual(inst._metric_slugs_key, "MSK")
            self.assertEqual(inst._gauge_slugs_key, "GSK")
            mock_redis.assert_called_once_with(
                decode_responses=True,
                host='HOST',
                port='PORT',
                db='DB',
                password="PASSWORD",
                socket_timeout=1,
                connection_pool=1
            )

    def test__init__with_default_kwargs(self):
        """Test creation of an R object without parameters."""
        r_kwargs = {
            'decode_responses': True,
            'host': 'localhost',
            'db': 0,
            'port': 6379,
            'password': None,
            'connection_pool': None,
            'socket_timeout': None
        }
        with patch('redis_metrics.models.redis.StrictRedis') as mock_redis:
            inst = R()
            self.assertEqual(inst.host, 'localhost')
            self.assertEqual(inst.port, 6379)
            self.assertEqual(inst.db, 0)
            self.assertEqual(inst.password, None)
            self.assertEqual(inst.socket_timeout, None)
            self.assertEqual(inst.connection_pool, None)
            self.assertEqual(inst._categories_key, 'categories')
            self.assertEqual(inst._metric_slugs_key, "metric-slugs")
            self.assertEqual(inst._gauge_slugs_key, "gauge-slugs")
            mock_redis.assert_called_once_with(**r_kwargs)

    def test__date_range(self):
        """Tests ``R._date_range`` at various granularities *without* a
        ``since`` date."""
        # minutes, seconds and hours should be capped at 300, 480, and 720
        d = datetime(2014, 1, 1)
        self.assertEqual(len(list(self.r._date_range('seconds', d))), 300)
        self.assertEqual(len(list(self.r._date_range('minutes', d))), 480)
        self.assertEqual(len(list(self.r._date_range('hourly', d))), 720)

        # Everything else should have a timedelta of 7 days
        self.assertEqual(len(list(self.r._date_range('daily', None))), 8)
        self.assertEqual(len(list(self.r._date_range('weekly', None))), 8)
        self.assertEqual(len(list(self.r._date_range('monthly', None))), 8)
        self.assertEqual(len(list(self.r._date_range('yearly', None))), 8)

        # Test with a specified `to` argument.
        since = datetime(2014, 1, 1)
        to = datetime(2015, 1, 1)
        self.assertEqual(len(list(self.r._date_range('daily', since, to))), 366)
        self.assertEqual(len(list(self.r._date_range('weekly', since, to))), 366)
        self.assertEqual(len(list(self.r._date_range('monthly', since, to))), 366)
        self.assertEqual(len(list(self.r._date_range('yearly', since, to))), 366)

    def test__date_range_seconds(self):
        """Tests ``R._date_range`` at the "seconds" granularity."""
        since = datetime.utcnow() - timedelta(seconds=5)
        values = self.r._date_range('seconds', since)
        self.assertEqual(len(list(values)), 5)

    def test__date_range_minutes(self):
        """Tests ``R._date_range`` at the "minutes" granularity."""
        since = datetime.utcnow() - timedelta(minutes=5)
        values = self.r._date_range('minutes', since)
        self.assertEqual(len(list(values)), 5)

    def test__date_range_hourly(self):
        """Tests ``R._date_range`` at the "hourly" granularity."""
        since = datetime.utcnow() - timedelta(hours=5)
        values = self.r._date_range('hourly', since)
        self.assertEqual(len(list(values)), 5)

    def test__date_range_daily(self):
        """Tests ``R._date_range`` at the "daily" granularity."""
        since = datetime.utcnow() - timedelta(days=5)
        values = self.r._date_range('daily', since)
        self.assertEqual(len(list(values)), 6)  # 6 because we do days + 1

    def test__date_range_weekly(self):
        """Tests ``R._date_range`` at the "weekly" granularity."""
        since = datetime.utcnow() - timedelta(days=5)
        values = self.r._date_range('weekly', since)
        self.assertEqual(len(list(values)), 6)  # 6 because we do days + 1

    def test__date_range_monthly(self):
        """Tests ``R._date_range`` at the "monthly" granularity."""
        since = datetime.utcnow() - timedelta(days=5)
        values = self.r._date_range('montly', since)
        self.assertEqual(len(list(values)), 6)  # 6 because we do days + 1

    def test__date_range_yearly(self):
        """Tests ``R._date_range`` at the "yearly" granularity."""
        since = datetime.utcnow() - timedelta(days=5)
        values = self.r._date_range('yearly', since)
        self.assertEqual(len(list(values)), 6)  # 6 because we do days + 1

    def test_categories(self):
        """Verify that ``R.categories()`` calls redis SMEMBERS command."""
        self.r.categories()
        self.redis.smembers.assert_called_once_with("categories")

    def test__category_key(self):
        """Creates a redis key for a given category string."""
        self.assertEqual(
            self.r._category_key("Sample Category"),
            u"c:Sample Category"
        )

    def test__category_slugs(self):
        """Verify that this returns an empty list or a list of slugs."""
        # When there are no results from redis
        with patch('redis_metrics.models.redis.StrictRedis') as mock_redis:
            mock_redis.return_value.smembers.return_value = set([])
            r = R()
            result = r._category_slugs("Sample Category")
            self.assertEqual(len(result), 0)

        # When there are no results from redis
        with patch('redis_metrics.models.redis.StrictRedis') as mock_redis:
            mock_redis.return_value.smembers.return_value = set(["slug-a", "slug-b"])
            r = R()
            result = r._category_slugs("Sample Category")
            self.assertEqual(set(result), set(['slug-a', 'slug-b']))

    @patch.object(R, '_category_slugs')
    def test__categorize(self, mock_category_slugs):
        """Categorizing a slug should add the correct key/values to Redis,
        and it should store the Category in a redis set."""

        # Sample category and metric slug
        cat = "Sample Category"
        cat_key = "c:Sample Category"
        slug = "sample-slug"

        with patch('redis_metrics.models.redis.StrictRedis') as mock_redis:
            redis_instance = mock_redis.return_value
            r = R()

            r._categorize(slug, cat)
            calls = [call.sadd(cat_key, slug), call.sadd("categories", cat)]
            redis_instance.assert_has_calls(calls, any_order=True)

    def test__granularities(self):
        """Tests ``R._granularities with default test settings."""
        # With default settings, min/max granularity is "seconds" and "yearly"
        self.assertEqual(
            list(self.r._granularities()),
            ['seconds', 'minutes', 'hourly', 'daily', 'weekly', 'monthly', 'yearly']
        )

    def test__granularities_with_altered_min(self):
        """Tests ``R._granularities with an altered minimum value."""
        test_settings = TEST_SETTINGS.copy()
        test_settings['MIN_GRANULARITY'] = 'daily'
        with override_settings(REDIS_METRICS=test_settings):
            self.assertEqual(
                list(self.r._granularities()),
                ['daily', 'weekly', 'monthly', 'yearly']
            )

    def test__granularities_with_altered_max(self):
        """Tests ``R._granularities with an altered maximum value."""
        test_settings = TEST_SETTINGS.copy()
        test_settings['MAX_GRANULARITY'] = 'daily'
        with override_settings(REDIS_METRICS=test_settings):
            self.assertEqual(
                list(self.r._granularities()),
                ['seconds', 'minutes', 'hourly', 'daily']
            )

    def test_metric_key_patterns(self):
        # These two things should always be the same.
        from ..settings import GRANULARITIES
        self.assertEqual(
            sorted(self.r._metric_key_patterns().keys()),
            sorted(GRANULARITIES)
        )

    def test__build_keys(self):
        """Tests ``R._build_keys``. with default arguments."""
        with patch('redis_metrics.models.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2014, 7, 2, 12, 6, 34)
            expected_results = [
                "m:test-slug:s:2014-07-02-12-06-34",
                "m:test-slug:i:2014-07-02-12-06",
                "m:test-slug:h:2014-07-02-12",
                "m:test-slug:2014-07-02",
                "m:test-slug:w:2014-26",
                "m:test-slug:m:2014-07",
                "m:test-slug:y:2014",
            ]
            keys = self.r._build_keys('test-slug')
            self.assertEqual(keys, expected_results)

    def test__build_keys_seconds(self):
        """Tests ``R._build_keys``. with a *seconds* granularity."""
        d = datetime(2012, 4, 1, 11, 30, 59)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='seconds')
        self.assertEqual(keys, ['m:test-slug:s:2012-04-01-11-30-59'])

    def test__build_keys_minutes(self):
        """Tests ``R._build_keys``. with a *minutes* granularity."""
        d = datetime(2012, 4, 1, 11, 30)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='minutes')
        self.assertEqual(keys, ['m:test-slug:i:2012-04-01-11-30'])

    def test__build_keys_hourly(self):
        """Tests ``R._build_keys``. with a *hourly* granularity."""
        d = datetime(2012, 4, 1, 11, 30)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='hourly')
        self.assertEqual(keys, ['m:test-slug:h:2012-04-01-11'])

    def test__build_keys_daily(self):
        """Tests ``R._build_keys``. with a *daily* granularity."""
        d = datetime(2012, 4, 1)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='daily')
        self.assertEqual(keys, ['m:test-slug:2012-04-01'])

    def test__build_keys_weekly(self):
        """Tests ``R._build_keys``. with a *weekly* granularity."""
        d = datetime(2012, 4, 1)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='weekly')
        self.assertEqual(keys, ['m:test-slug:w:2012-14'])

    def test__build_keys_weekly_week_starts_monday(self):
        """Tests ``R._build_keys``. with a *weekly* granularity."""
        test_settings = TEST_SETTINGS.copy()
        test_settings['MONDAY_FIRST_DAY_OF_WEEK'] = True
        with override_settings(REDIS_METRICS=test_settings):
            d = datetime(2012, 4, 1)  # April Fools!
            keys = self.r._build_keys('test-slug', date=d, granularity='weekly')
            self.assertEqual(keys, ['m:test-slug:w:2012-13'])

    def test__build_keys_monthly(self):
        """Tests ``R._build_keys``. with a *monthly* granularity."""
        d = datetime(2012, 4, 1)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='monthly')
        self.assertEqual(keys, ['m:test-slug:m:2012-04'])

    def test__build_keys_yearly(self):
        """Tests ``R._build_keys``. with a *yearly* granularity."""
        d = datetime(2012, 4, 1)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='yearly')
        self.assertEqual(keys, ['m:test-slug:y:2012'])

    def test_metric_slugs(self):
        """Test that ``R.metric_slugs`` makes a call to Redis SMEMBERS."""
        self.r.metric_slugs()
        self.redis.assert_has_calls([call.smembers(self.r._metric_slugs_key)])

    @patch.object(R, '_category_slugs')
    def test_metric_slugs_by_category(self, mock_category_slugs):
        """Test that we get metric slugs organized by category."""
        # set up a mock return value for the category's redis set
        self.redis.smembers.return_value = ['Sample Category']
        # set up return value for mock call to _category_slugs
        mock_category_slugs.return_value = ['foo', 'bar']

        # Since this method all calls out to ``R.metric_slugs``, let's patch
        # that so it returns a list of all slugs, one of which will not be
        # categorized
        self.r.metric_slugs = Mock(return_value=['foo', 'bar', 'baz'])

        # Now, test the thing.
        result = self.r.metric_slugs_by_category()
        expected_result = {
            'Sample Category': ['foo', 'bar'],
            'Uncategorized': ['baz']
        }
        self.assertEqual(result, expected_result)
        self.redis.smembers.assert_called_once_with("categories")
        mock_category_slugs.assert_called_once_with("Sample Category")
        self.r.metric_slugs.assert_called_once_with()

    def test_delete_metric(self):
        """Verify that ``R.delete_metric`` deletes all keys and removes keys
        from the set of metric slugs."""

        # Make sure KEYS returns some data
        self.redis.keys.return_value = ["m:slug:0", "m:slug:1"]
        self.r.delete_metric('slug')  # call delete_metric

        # Verify that the metric data is removed as are the keys from the set
        self.redis.assert_has_calls([
            call.keys("m:slug:*"),
            call.delete("m:slug:0", "m:slug:1"),
            call.srem(self.r._metric_slugs_key, "slug")
        ])

    @patch.object(R, '_build_keys')
    def test_set_metric(self, mock_build_keys):
        """Test setting metrics using ``R.set_metric``."""
        # Define redis keys
        mock_build_keys.return_value = [
            'm:test-slug:s:2000-01-02-11-45-30',
            'm:test-slug:i:2000-01-02-11-45',
            'm:test-slug:h:2000-01-02-11',
            'm:test-slug:2000-01-02',
            'm:test-slug:m:2000-01',
            'm:test-slug:w:2000-01',
            'm:test-slug:y:2000'
        ]
        slug = 'test-slug'
        value = 42

        # get the metric keys so we can check for the appropriate calls
        self.r.set_metric(slug, value)

        # Verify that setting a metric adds the appropriate slugs to the keys
        # set and then incrememts each key
        self.redis.sadd.assert_called_once_with('metric-slugs', slug)
        self.redis.mset.assert_called_once_with({
            'm:test-slug:s:2000-01-02-11-45-30': 42,
            'm:test-slug:i:2000-01-02-11-45': 42,
            'm:test-slug:h:2000-01-02-11': 42,
            'm:test-slug:2000-01-02': 42,
            'm:test-slug:m:2000-01': 42,
            'm:test-slug:w:2000-01': 42,
            'm:test-slug:y:2000': 42,
        })

        # Expiration should not have gotten called
        self.assertFalse(self.redis.expire.called)

    @patch.object(R, '_build_keys')
    def test_set_metric_with_expiration(self, mock_build_keys):
        """Test setting metrics using ``R.set_metric`` with an expiration."""
        # Define redis keys
        mock_build_keys.return_value = [
            'm:test-slug:s:2000-01-02-11-45-30',
            'm:test-slug:i:2000-01-02-11-45',
            'm:test-slug:h:2000-01-02-11',
            'm:test-slug:2000-01-02',
            'm:test-slug:m:2000-01',
            'm:test-slug:w:2000-01',
            'm:test-slug:y:2000'
        ]
        slug = 'test-slug'
        value = 42

        # get the metric keys so we can check for the appropriate calls
        self.r.set_metric(slug, value, expire=500)

        # Verify that each key had an expiration set.
        self.redis.expire.assert_has_calls([
            call('m:test-slug:s:2000-01-02-11-45-30', 500),
            call('m:test-slug:i:2000-01-02-11-45', 500),
            call('m:test-slug:h:2000-01-02-11', 500),
            call('m:test-slug:2000-01-02', 500),
            call('m:test-slug:m:2000-01', 500),
            call('m:test-slug:w:2000-01', 500),
            call('m:test-slug:y:2000', 500),
        ])

    @patch.object(R, '_categorize')
    def test_set_metric_with_category(self, mock_categorize):
        """Test setting metrics using ``R.set_metric`` when a category
        is provided."""

        # get the metric keys so we can check for the appropriate calls
        self.r.set_metric('test-slug', 42, category='Test Category')
        mock_categorize.assert_called_once_with('test-slug', "Test Category")

    def test_metric(self):
        """Test setting metrics using ``R.metric``."""

        slug = 'test-metric'
        n = 1

        # get the keys used for the metric, so we can check for the appropriate
        # calls
        keys = self.r._build_keys(slug)
        second, minute, hour, day, week, month, year = keys
        self.r.metric(slug, num=n)

        # Verify that setting a metric adds the appropriate slugs to the keys
        # set and then incrememts each key
        self.redis.assert_has_calls([
            call.sadd(self.r._metric_slugs_key, slug),
            call.pipeline(),
            call.pipeline().incr(second, n),
            call.pipeline().incr(minute, n),
            call.pipeline().incr(hour, n),
            call.pipeline().incr(day, n),
            call.pipeline().incr(week, n),
            call.pipeline().incr(month, n),
            call.pipeline().incr(year, n),
        ])

        # Expiration should not have gotten called
        self.assertFalse(self.redis.expire.called)

    def test_metric_with_overridden_granularities(self):
        test_settings = TEST_SETTINGS.copy()
        test_settings['MIN_GRANULARITY'] = 'daily'
        test_settings['MAX_GRANULARITY'] = 'weekly'
        with override_settings(REDIS_METRICS=test_settings):
            slug = 'test-metric'
            n = 1

            # get the keys used for the metric, so we can check for the appropriate
            # calls
            daily, weekly = self.r._build_keys(slug)
            self.r.metric(slug, num=n)

            # Verify that setting a metric adds the appropriate slugs to the keys
            # set and then incrememts each key
            self.redis.assert_has_calls([
                call.sadd(self.r._metric_slugs_key, slug),
                call.pipeline(),
                call.pipeline().incr(daily, n),
                call.pipeline().incr(weekly, n),
            ])

            # Expiration should not have gotten called
            self.assertFalse(self.redis.expire.called)

    @patch.object(R, '_categorize')
    def test_metric_with_category(self, mock_categorize):
        """The ``metric`` method should call ``_categorize`` if passed a
        ``category`` argument."""
        category = "Some Category"
        slug = 'categorized-metric'
        n = 1

        # get the keys used for the metric, so we can check for calls
        keys = self.r._build_keys(slug)
        second, minute, hour, day, week, month, year = keys
        self.r.metric(slug, num=n, category=category)

        # Verify that setting a metric adds the appropriate slugs to the keys
        # set and then incrememts each key
        self.redis.assert_has_calls([
            call.sadd(self.r._metric_slugs_key, slug),
            call.pipeline(),
            call.pipeline().incr(second, n),
            call.pipeline().incr(minute, n),
            call.pipeline().incr(hour, n),
            call.pipeline().incr(day, n),
            call.pipeline().incr(week, n),
            call.pipeline().incr(month, n),
            call.pipeline().incr(year, n),
        ])

        # Make sure this gets categorized.
        mock_categorize.assert_called_once_with(slug, category)

        # Expiration should not have gotten called
        self.assertFalse(self.redis.expire.called)

    @patch.object(R, '_categorize')
    def test_metric_with_expiration(self, mock_categorize):
        """The ``metric`` method should call the redis ``expire`` method if
        passed an ``expire`` argument."""

        slug = 'categorized-metric'
        n = 1

        # get the keys used for the metric, so we can check for calls
        keys = self.r._build_keys(slug)
        self.r.metric(slug, num=n, expire=3600)

        # Verify that setting a metric adds the appropriate slugs to the keys
        # set and then incrememts each key
        call_list = [call.sadd(self.r._metric_slugs_key, slug), call.pipeline()]
        for k in keys:
            call_list.append(call.pipeline().incr(k, n))
            call_list.append(call.pipeline().expire(k, 3600))

        self.redis.assert_has_calls(call_list)

        # Make sure nothing was categorized.
        self.assertFalse(mock_categorize.called)

    def test_get_metric(self):
        """Tests getting a single metric; ``R.get_metric``."""
        slug = 'test-metric'
        self.r.get_metric(slug)

        # Verify that we GET the keys from redis
        sec, min, hour, day, week, month, year = self.r._build_keys(slug)
        self.redis.assert_has_calls([
            call.get(sec),
            call.get(min),
            call.get(hour),
            call.get(day),
            call.get(week),
            call.get(month),
            call.get(year),
        ])

    def test_get_metric_with_overridden_granularities(self):
        test_settings = TEST_SETTINGS.copy()
        test_settings['MIN_GRANULARITY'] = 'daily'
        test_settings['MAX_GRANULARITY'] = 'weekly'
        with override_settings(REDIS_METRICS=test_settings):
            slug = 'test-metric'
            self.r.get_metric(slug)

            # Verify that we GET the keys from redis
            day, week = self.r._build_keys(slug)
            self.redis.assert_has_calls([
                call.get(day),
                call.get(week),
            ])

    def test_get_metrics(self):
        # Set a return value for mget, so all of the method gets exercised.
        prev_return = self.redis.mget.return_value
        self.redis.mget.return_value = ['1', '2']

        # Slugs for metrics we want
        slugs = ['metric-1', 'metric-2']

        # Build the various keys for each metric
        keys_list = []
        for s in slugs:
            keys_list.append(self.r._build_keys(s))

        # construct the calls to redis.mget
        calls = [call(*keys) for keys in keys_list]

        # Test our method
        self.r.get_metrics(slugs)
        self.assertEqual(self.redis.mget.call_args_list, calls)
        self.assertTrue(self.redis.mget.called)  # mget was called...
        self.assertEqual(self.redis.mget.call_count, 2)  # ...twice

        # Reset mget's previous return value
        self.redis.mget.return_value = prev_return

    def test_get_metrics_with_overridden_granularities(self):
        test_settings = TEST_SETTINGS.copy()
        test_settings['MIN_GRANULARITY'] = 'daily'
        test_settings['MAX_GRANULARITY'] = 'weekly'
        with override_settings(REDIS_METRICS=test_settings):
            # Set a return value for mget, so all of the method gets exercised.
            prev_return = self.redis.mget.return_value
            self.redis.mget.return_value = ['1', '2']

            # Slugs for metrics we want
            slugs = ['metric-1', 'metric-2']

            # Build the various keys for each metric
            keys_list = []
            for s in slugs:
                keys_list.append(self.r._build_keys(s))

            # construct the calls to redis.mget
            calls = [call(*keys) for keys in keys_list]

            # Test our method
            self.r.get_metrics(slugs)
            self.assertEqual(self.redis.mget.call_args_list, calls)
            self.assertTrue(self.redis.mget.called)  # mget was called...
            self.assertEqual(self.redis.mget.call_count, 2)  # ...twice

            # Reset mget's previous return value
            self.redis.mget.return_value = prev_return

    def test_get_category_metrics(self):
        """returns metrics for a given category"""
        r = R()
        # Mock methods called by `get_category_metrics`
        r._category_slugs = Mock(return_value=['some-slug'])
        r.get_metrics = Mock(return_value="RESULT")
        results = r.get_category_metrics("Sample Category")
        self.assertEqual(results, 'RESULT')
        r._category_slugs.assert_called_once_with("Sample Category")
        r.get_metrics.assert_called_once_with(['some-slug'])

    def test_delete_category(self):
        r_kwargs = {
            'decode_responses': True,
            'host': 'localhost',
            'db': 0,
            'port': 6379,
            'password': None,
            'connection_pool': None,
            'socket_timeout': None
        }
        with patch("redis_metrics.models.redis.StrictRedis") as mock_redis:
            r = R()
            r.delete_category("Foo")
            mock_redis.assert_has_calls([
                call(**r_kwargs),
                call().delete('c:Foo'),
                call().srem("categories", "Foo")
            ])

    @patch.object(R, "delete_category")
    def test_reset_category_with_no_metrics(self, mock_delete_category):
        """Calling ``reset_category`` with an empty list of metrics should
        just delete the category."""
        with patch("redis_metrics.models.redis.StrictRedis"):
            r = R()
            r.reset_category("Stuff", [])
            mock_delete_category.assert_called_once_with("Stuff")

    def test_reset_category(self):
        r_kwargs = {
            'decode_responses': True,
            'host': 'localhost',
            'db': 0,
            'port': 6379,
            'password': None,
            'connection_pool': None,
            'socket_timeout': None
        }
        with patch("redis_metrics.models.redis.StrictRedis") as mock_redis:
            r = R()
            r.reset_category("Stuff", ['foo', 'bar'])
            mock_redis.assert_has_calls([
                call(**r_kwargs),
                call().sadd('c:Stuff', 'foo', 'bar'),
                call().sadd('categories', 'Stuff'),
            ])

    def _metric_history_keys(self, slugs, since=None, to=None,
                             granularity='daily'):
        """generates the same list of keys used in ``get_metric_history``.
        These can then be used to test for calls to redis. Note: This is
        duplicate code from ``get_metric_history`` :-/ """
        if type(slugs) != list:
            slugs = [slugs]
        keys = []
        for slug in slugs:
            for date in self.r._date_range(granularity, since, to):
                keys += self.r._build_keys(slug, date, granularity)
        keys = list(dedupe(keys))
        return keys

    def _test_get_metric_history(self, slugs, since=None, to=None,
                                 granularity=None):
        """actual test code for ``R.get_metric_history``."""
        keys = self._metric_history_keys(slugs, since, to, granularity)
        self.r.get_metric_history(
            slugs, since=since, to=to, granularity=granularity)
        self.redis.assert_has_calls([call.mget(keys)])

    def test_get_metric_history_hourly(self):
        """Tests ``R.get_metric_history`` with hourly granularity."""
        self._test_get_metric_history('test-slug', granularity='hourly')

        # with specified to/since dates
        self._test_get_metric_history(
            'test-slug',
            since=datetime(2014, 1, 1),
            to=datetime(2016, 1, 1),
            granularity='hourly'
        )

    def test_get_metric_history_daily(self):
        """Tests ``R.get_metric_history`` with daily granularity."""
        self._test_get_metric_history('test-slug', granularity='daily')

        # with specified to/since dates
        self._test_get_metric_history(
            'test-slug',
            since=datetime(2014, 1, 1),
            to=datetime(2016, 1, 1),
            granularity='daily'
        )

    def test_get_metric_history_weekly(self):
        """Tests ``R.get_metric_history`` with weekly granularity."""
        self._test_get_metric_history('test-slug', granularity='weekly')

        # with specified to/since dates
        self._test_get_metric_history(
            'test-slug',
            since=datetime(2014, 1, 1),
            to=datetime(2016, 1, 1),
            granularity='weekly'
        )

    def test_get_metric_history_monthly(self):
        """Tests ``R.get_metric_history`` with monthly granularity."""
        self._test_get_metric_history('test-slug', granularity='monthly')

        # with specified to/since dates
        self._test_get_metric_history(
            'test-slug',
            since=datetime(2014, 1, 1),
            to=datetime(2016, 1, 1),
            granularity='monthly'
        )

    def test_get_metric_history_yearly(self):
        """Tests ``R.get_metric_history`` with yearly granularity."""
        self._test_get_metric_history('test-slug', granularity='yearly')

        # with specified to/since dates
        self._test_get_metric_history(
            'test-slug',
            since=datetime(2014, 1, 1),
            to=datetime(2016, 1, 1),
            granularity='yearly'
        )

    def test_get_metric_multiple_history_hourly(self):
        self._test_get_metric_history(['foo', 'bar'], granularity='hourly')

        # with specified to/since dates
        self._test_get_metric_history(
            ['foo', 'bar'],
            since=datetime(2015, 1, 1),
            to=datetime(2015, 2, 1),
            granularity='hourly'
        )

    def test_get_metric_multiple_history_daily(self):
        self._test_get_metric_history(['foo', 'bar'], granularity='daily')

        # with specified to/since dates
        self._test_get_metric_history(
            ['foo', 'bar'],
            since=datetime(2015, 1, 1),
            to=datetime(2015, 2, 1),
            granularity='daily'
        )

    def test_get_metric_multiple_history_weekly(self):
        self._test_get_metric_history(['foo', 'bar'], granularity='weekly')

        # with specified to/since dates
        self._test_get_metric_history(
            ['foo', 'bar'],
            since=datetime(2015, 1, 1),
            to=datetime(2015, 2, 1),
            granularity='weekly'
        )

    def test_get_metric_multiple_history_monthly(self):
        self._test_get_metric_history(['foo', 'bar'], granularity='monthly')

        # with specified to/since dates
        self._test_get_metric_history(
            ['foo', 'bar'],
            since=datetime(2015, 1, 1),
            to=datetime(2015, 12, 1),
            granularity='monthly'
        )

    def test_get_metric_multiple_history_yearly(self):
        self._test_get_metric_history(['foo', 'bar'], granularity='yearly')

        # with specified to/since dates
        self._test_get_metric_history(
            ['foo', 'bar'],
            since=datetime(2015, 1, 1),
            to=datetime(2016, 1, 1),
            granularity='yearly'
        )

    @patch.object(R, '_date_range')
    def test_get_metric_history_replaces_none_with_zero(self, mock_date_range):
        """Ensure that None-values get replaced with Zeros in
        ``R.get_metric_history``."""

        # Mock the _date_range method so we can specify it's return values.
        mock_date_range.return_value = [
            datetime(2000, 1, 1),
            datetime(2000, 1, 2),
            datetime(2000, 1, 3),
            datetime(2000, 1, 4),
        ]

        # Temporarily change the return value for mget
        mget_return = self.redis.mget.return_value
        self.redis.mget.return_value = ['1', '2', None, '3']

        # Note: we're not providing a since parameter here, since we've
        # mocked the R._date_range method.
        results = self.r.get_metric_history("foo", granularity="daily")

        # Format the range of dates that for which we should get results
        expected = [
            ('m:foo:2000-01-01', '1'),
            ('m:foo:2000-01-02', '2'),
            ('m:foo:2000-01-03', 0),
            ('m:foo:2000-01-04', '3'),
        ]
        self.assertEqual(results, expected)

        # Reset mget's previous return value
        self.redis.mget.return_value = mget_return

    @patch.object(R, 'get_metric_history')
    def test_get_metric_history_as_columns(self, mock_metric_hist):
        # set up some sample (yearly) metrics
        mock_metric_hist.return_value = [
            ("m:bar:y:2012", '1'),
            ('m:bar:y:2013', '2'),
            ('m:foo:y:2012', '3'),
            ('m:foo:y:2013', '4'),
        ]
        expected_results = [
            ('Period', 'foo', 'bar'),
            ('y:2012', '3', '1'),
            ('y:2013', '4', '2'),
        ]
        with patch('redis_metrics.models.redis.StrictRedis'):
            r = R()
            kwargs = {
                'slugs': ['foo', 'bar'],
                'since': None,
                'granularity': 'yearly',
            }
            results = r.get_metric_history_as_columns(**kwargs)
            self.assertEqual(results, expected_results)

    def _test_get_metric_history_as_columns(self, slugs, granularity):
        """Test that R.get_metric_history_as_columns makes calls to the
        following functions:

        * ``R.r.mget``
        * ``R.get_metric_history``
        * ``templatetags.metric_slug``
        * ``templatetags.strip_metric_prefix``

        """
        keys = self._metric_history_keys(slugs, granularity=granularity)
        self.r.get_metric_history_as_columns(slugs, granularity=granularity)

        # Verifies the correct call to redis
        self.redis.assert_has_calls([call.mget(keys)])

        # Verify that the method gets called correctly
        with patch('redis_metrics.models.R') as mock_r:
            r = mock_r.return_value  # Get an instance of our Mocked R class
            r.get_metric_history_as_columns(slugs, granularity=granularity)
            mock_r.assert_has_calls([
                call().get_metric_history_as_columns(
                    slugs, granularity=granularity
                )
            ])

    def test_get_metric_history_as_columns_hourly(self):
        self._test_get_metric_history_as_columns(['foo', 'bar'], 'hourly')

    def test_get_metric_history_as_columns_daily(self):
        self._test_get_metric_history_as_columns(['foo', 'bar'], 'daily')

    def test_get_metric_history_as_columns_weekly(self):
        self._test_get_metric_history_as_columns(['foo', 'bar'], 'weekly')

    def test_get_metric_history_as_columns_monthly(self):
        self._test_get_metric_history_as_columns(['foo', 'bar'], 'monthly')

    def test_get_metric_history_as_columns_yearly(self):
        self._test_get_metric_history_as_columns(['foo', 'bar'], 'yearly')

    @patch.object(R, 'get_metric_history')
    def test_get_metric_history_chart_data(self, mock_metric_hist):
        # set up some sample (yearly) metrics
        mock_metric_hist.return_value = [
            ("m:bar:y:2012", '1'),
            ('m:bar:y:2013', '2'),
            ('m:foo:y:2012', '3'),
            ('m:foo:y:2013', '4'),
        ]
        expected_results = {
            'periods': ['y:2012', 'y:2013'],
            'data': [
                {'slug': 'bar', 'values': ['1', '2']},
                {'slug': 'foo', 'values': ['3', '4']},
            ]
        }
        with patch('redis_metrics.models.redis.StrictRedis'):
            r = R()
            kwargs = {
                'slugs': ['foo', 'bar'],
                'since': None,
                'granularity': 'yearly',
            }
            results = r.get_metric_history_chart_data(**kwargs)
            self.assertEqual(results, expected_results)

    def test_gauge_slugs(self):
        """Tests that ``R.gauge_slugs`` calls the SMEMBERS command."""
        self.r.gauge_slugs()
        self.redis.assert_has_calls([call.smembers(self.r._gauge_slugs_key)])

    def test__gauge_key(self):
        """Tests that ``R._gauge_key`` correctly generates gauge keys."""
        key = self.r._gauge_key('test-gauge')
        self.assertEqual(key, 'g:test-gauge')

    def test_gauge(self):
        """Tests setting a gauge with ``R.gauge``. Verifies that the gauge slug
        is added to the set of gauge slugs and that the value gets set."""
        self.r.gauge('test-gauge', 9000)
        self.redis.assert_has_calls([
            call.sadd(self.r._gauge_slugs_key, 'test-gauge'),
            call.set('g:test-gauge', 9000),
        ])

    def test_get_gauge(self):
        """Tests retrieving a gague with ``R.get_gauge``. Verifies that the
        Redis GET command is called with the correct key."""
        self.r.get_gauge('test-gauge')
        self.redis.assert_has_calls([call.get('g:test-gauge')])

    def test_delete_gauge(self):
        """Tests deltion of a gauge."""
        self.r.delete_gauge("test-gauge")
        self.redis.assert_has_calls([
            call.delete('g:test-gauge'),
            call.srem(self.r._gauge_slugs_key, "test-gauge"),
        ])
