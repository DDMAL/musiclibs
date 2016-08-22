from misirlou.helpers.manifest_utils.errors import ErrorMap, ManifestError
from misirlou.tests.mis_test import MisirlouTestSetup


class ErrorMapTestCase(MisirlouTestSetup):
    def setUp(self):
        self.er = ErrorMap()

    def test_get_error(self):
        # Assert that you can get a tuple.
        no_error1 = self.er['NO_ERROR']
        self.assertEqual(no_error1, ManifestError(0, "NO_ERROR", "No errors reported."))

        # Assert that you can get the same tuple through str or int.
        no_error2 = self.er[0]
        self.assertEqual(no_error1, no_error2)

        # Assert that non int or str is type error.
        with self.assertRaises(TypeError):
            bad_call = self.er[3.14]

        # Assert that bad key raises KeyError.
        with self.assertRaises(KeyError):
            bad_call = self.er['ASJHDAISH']

    def test_iterate_errors(self):
        for errs in self.er.values():
            self.assertTrue(isinstance(errs[0], int))
            self.assertTrue(errs[1].isupper())
            self.assertTrue(isinstance(errs[2], str))
            pass
