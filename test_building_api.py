#!/usr/bin/env python3
# unit tests for Complex in complex.py
from building_api import HeightsLimitsProc
import unittest

""" Test set also requires two original test files """

class TestBuildingAPI(unittest.TestCase):

    def test_read_in_heights(self):
        """ Tests read-in of features on height plataeus
            (We expect 3 features from the given files)
        """
        tmp_class = HeightsLimitsProc('limits.json', 'heights.json')
        expected = 3
        computed = len(tmp_class.heights)
        success = expected == computed
        msg = "Expected {} features, read in only {}".format(expected, computed)
        assert success, msg

    def test_read_in_limits(self):
        """ Tests read-in of features on limits, though currently
            this model computes only 1 buildinglimit extent to N elevation zones
        """
        tmp_class = HeightsLimitsProc('limits.json', 'heights.json')
        expected = 1
        computed = len(tmp_class.limits)
        success = expected == computed
        msg = "Expected {} features, read in only {}".format(expected, computed)
        assert success, msg

    def test_valid_yes(self):
        """ Asserts a known-good validate() call
        """
        tmp_class = HeightsLimitsProc('limits.json', 'heights.json')
        tmp_class.unionize()
        expected = True
        computed = tmp_class.validate()
        success = (expected == computed)
        msg = "Given limits & heights did NOT validate. Feature geometry error"
        assert success, msg

    def test_valid_no(self):
        """ Tests for false validate() return by deliberately breaking heights
            feature coverage overlap of limits
        """
        tmp_class = HeightsLimitsProc('limits.json', 'heights.json')
        tmp_class.heights.pop() # destroy heights features integrity
        tmp_class.unionize()
        expected = False
        computed = tmp_class.validate()
        success = (expected == computed)
        msg = "Validate() on limits + _broken_ heights features should be FALSE."
        assert success, msg

    def test_valid_no_slight(self):
        """ Tests a false validate() return by deliberately altering dimensions
            on known-good geofeatures. Moves one coord pair to inside of the
            building limits, breaking coverage slightly.
            mess around here:
        """
        tmp_class = HeightsLimitsProc('limits.json', 'heights.json')

        # Alter one coordinate, ruining coverage integrity
        tmp_class.heights[0]['geometry']['coordinates'][0][0] =\
                                        [10.7205381014655, 59.94392858334589]
        tmp_class.unionize()
        expected = False
        computed = tmp_class.validate()
        success = (expected == computed)
        msg = "Validate() on _altered_ heights features should trigger FALSE."
        assert success, msg

if __name__ == '__main__':
    unittest.main()
