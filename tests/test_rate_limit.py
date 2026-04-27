from unittest import TestCase

from app.api.rate_limit import RateLimiter


class RateLimiterTest(TestCase):
    def test_allows_requests_within_limit(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        self.assertTrue(limiter.allow("token"))
        self.assertTrue(limiter.allow("token"))

    def test_blocks_requests_over_limit(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)

        self.assertTrue(limiter.allow("token"))
        self.assertFalse(limiter.allow("token"))

    def test_uses_separate_buckets_per_key(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)

        self.assertTrue(limiter.allow("token-a"))
        self.assertTrue(limiter.allow("token-b"))
