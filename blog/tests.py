from django.test import TestCase

from .utils import remove_non_alphanumeric

# Create your tests here.

class UtilsTests(TestCase):
    def test_remove_non_alphanumeric(self):
        input_string = "Hello python abs"
        expected_output = "Hello python abs"
        self.assertEqual(remove_non_alphanumeric(input_string), expected_output)
        
        input_string = "Hello, $!%world123"
        expected_output = "Hello world123"
        self.assertEqual(remove_non_alphanumeric(input_string), expected_output)

        input_string = "abc!@#123"
        expected_output = "abc123"
        self.assertEqual(remove_non_alphanumeric(input_string), expected_output)

        input_string = "python3.9.1"
        expected_output = "python391"
        self.assertEqual(remove_non_alphanumeric(input_string), expected_output)

        input_string = "a b c"
        expected_output = "a b c"
        self.assertEqual(remove_non_alphanumeric(input_string), expected_output)