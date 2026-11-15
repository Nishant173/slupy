import unittest

from slupy.core.distributions import ExactDistribution, RandomDistribution


class TestDistribution(unittest.TestCase):

    def test_random_distribution(self):
        dist = RandomDistribution(
            distribution={
                "A": 55,
                "B": 30,
                "C": 15,
            },
        )
        self.assertEqual(
            dist.sample_size,
            100,
        )

        for _ in range(dist.sample_size * 25):
            self.assertTrue(
                dist.compute_category() in dist.distribution
            )

    def test_exact_distribution(self):
        dist = ExactDistribution(
            distribution={
                "A": 30,
                "B": 40,
                "C": 18.298,
                "D": 11.6,
                "E": 0.102,
            },
            shuffle=True,
        )
        self.assertEqual(
            dist.sample_size,
            100_000,
        )

        for _ in range(dist.sample_size * 25):
            self.assertTrue(
                dist.compute_category() in dist.distribution
            )

        counter = dist.get_category_counter_for_sample_size()
        self.assertEqual(
            sorted(list(counter.keys())),
            sorted(list(dist.distribution.keys())),
            msg="The keys from the counter object must be the same as the categories of the distribution",
        )

        self.assertEqual(
            counter["A"],
            30_000,
        )
        self.assertEqual(
            counter["B"],
            40_000,
        )
        self.assertEqual(
            counter["C"],
            18_298,
        )
        self.assertEqual(
            counter["D"],
            11_600,
        )
        self.assertEqual(
            counter["E"],
            102,
        )


