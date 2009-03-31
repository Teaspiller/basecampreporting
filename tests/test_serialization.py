import os
import pprint
import unittest
import datetime

from basecampreporting.serialization import json, BasecampObjectEncoder
from basecampreporting.mocks import TestProject

class SerializationTestHelper(unittest.TestCase):
    def setUp(self):
        self.username = "FAKE"
        self.password = "FAKE"
        self.url = "http://FAKE.basecamphq.com/"
        self.project_id = 2849305

        base_path = os.path.dirname(os.path.abspath(__file__))
        self.fixtures_path = os.path.join(base_path, ".", "fixtures", "project.recorded.json")


        self.project = TestProject(self.url, self.project_id,
                               self.username, self.password, self.fixtures_path)

        self.project.bc.load_test_fixtures(self.fixtures_path)

    def assertSerialization(self, o, expected):
        as_json = o.to_json()
        from_json = json.loads(as_json)

        msg = "Unequal data structures!\nExpected:\n%s\n\nActual:\n%s" % (pprint.pformat(expected), pprint.pformat(from_json))
        self.assertEqual(expected, from_json, msg)

class SerializationTests(SerializationTestHelper):
    def test_message(self):
        m = self.project.messages[0]
        expected = {
            u"category": {u"type": u"PostCategory", u"id": 28605393, u"name": u"Assets"},
            u"attachments_count": 0,
            u"id": 19364228,
            u"posted_on": u'2009-01-28T14:30:18',
            u"title": u"This is the newest message"
        }
        self.assertSerialization(m, expected)

    def test_comment(self):
        pass

if __name__ == "__main__":
    import unittest
    unittest.main()
