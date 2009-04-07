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

        for key, value in expected.items():
            msg = "Key %s doesn't match.\nExpected:\n%s\n\nActual:\n%s" % (key, pprint.pformat(value), pprint.pformat(from_json[key]))
            self.assertEqual(value, from_json[key], msg)
#        msg = "Unequal data structures!\nExpected:\n%s\n\nActual:\n%s" % (pprint.pformat(expected), pprint.pformat(from_json))
#        self.assertEqual(expected, from_json, msg)

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
        c = self.project.comments[0]
        expected = {u'attachments_count': 0,
                    u'author_id': 3396975,
                    u'body': u'This is the latest comment',
                    u'emailed_from': None,
                    u'id': 29503849,
                    u'post_id': 19364228,
                    u'posted_on': u'2009-01-28T21:37:02'}
        self.assertSerialization(c, expected)

    def test_milestone(self):
        m = self.project.milestones[0]
        expected = {u'completed': False,
                    u'created_on': u'2009-01-29T21:55:43',
                    u'creator_id': 3396975,
                    u'deadline': u'2011-12-31T00:00:00',
                    u'id': 8710156,
                    u'project_id': 2849305,
                    u'responsible_party_id': 3396975,
                    u'responsible_party_type': u'Person',
                    u'title': u'Future Milestone 3',
                    u'wants_notification': False,
                    u'is_previous': False,
                    u'is_upcoming': True,
                    u'is_late': False}
        self.assertSerialization(m, expected)

    def test_todolist(self):
        t = self.project.todo_lists[self.project.todo_lists.keys()[0]]
        expected = {u'complete': u'false',
                    u'completed_count': 0,
                    u'description': u'Bugs and errors that need to be fixed',
                    u'id': 5390843,
                    u'milestone_id': None,
                    u'name': u'Defect backlog',
                    u'position': 3,
                    u'private': False,
                    u'project_id': 2849305,
                    u'tracked': False,
                    u'uncompleted_count': 2,
                    u'is_complete': False,
                    u'is_sprint': False,
                    u'is_backlog': True}
        self.assertSerialization(t, expected)

    def test_project(self):
        p = self.project
        expected = self.generated_expected_project()
        self.assertSerialization(p, expected)

    def generated_expected_project(self, limit_relations=None):
        expected = {
            u'name': self.project.name,
            u'status': self.project.status,
            u'last_changed_on': '2009-02-03T15:03:14',
            u'messages': [ m.to_json(limit_relations) for m in self.project.messages[:limit_relations] ],
            u'comments': [ c.to_json(limit_relations) for c in self.project.comments[:limit_relations] ],
            u'milestones': [ m.to_json(limit_relations) for m in self.project.milestones[:limit_relations] ],
            u'late_milestones': [ m.to_json(limit_relations) for m in self.project.late_milestones[:limit_relations] ],
            u'previous_milestones': [ m.to_json(limit_relations) for m in self.project.previous_milestones[:limit_relations] ],
            u'backlogged_count': self.project.backlogged_count,
            u'sprints': [ s.to_json(limit_relations) for s in self.project.sprints[:limit_relations] ],
            u'current_sprint': self.project.current_sprint.to_json(limit_relations),
            u'upcoming_sprints': [ s.to_json(limit_relations) for s in self.project.upcoming_sprints[:limit_relations] ],
        }

        todo_list_keys = self.project.todo_lists.keys()
        todo_list_keys.sort()
        todo_list_keys = todo_list_keys[:limit_relations]

        expected[u'todo_lists'] = {}
        for k in todo_list_keys:
            expected[u'todo_lists'][k] = self.project.todo_lists[k].to_json(limit_relations)
        
        backlog_keys = self.project.backlogs.keys()
        backlog_keys.sort()
        backlog_keys = backlog_keys[:limit_relations]

        expected[u'backlogs'] = {}
        for k in backlog_keys:
            expected[u'backlogs'][k] = self.project.backlogs[k].to_json(limit_relations)

        return expected

if __name__ == "__main__":
    import unittest
    unittest.main()
