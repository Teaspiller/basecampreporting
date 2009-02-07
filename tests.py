import unittest
from project import Project

from basecamp import Basecamp

class TestBasecamp(Basecamp):
    pass

class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.username = "apitest"
        self.password = "apitest"
        self.url = "http://apitesting.basecamphq.com/"
        self.project_id = 2849305

        self.project = Project(self.url, self.project_id,
                               self.username, self.password, basecamp=TestBasecamp)
        
    def test_latest_message(self):
        self.assertEqual("This is the newest message",
                         self.project.messages[0].title)

    def test_latest_comment(self):
        self.assertEqual("This is the latest comment",
                         self.project.comments[0].body)

    def test_late_milestones(self):
        self.assertEqual(3, len(self.project.late_milestones))

    def test_upcoming_milestones(self):
        self.assertEqual(3, len(self.project.upcoming_milestones))

    def test_previous_milestones(self):
        self.assertEqual(6, len(self.project.previous_milestones))

    def test_backlogs(self):
        self.assertEqual(2, len(self.project.backlogs))

        self.assertEqual(3, self.project.backlogs['Product backlog'].uncompleted_count)
        self.assertEqual(2, self.project.backlogs['Defect backlog'].uncompleted_count)
        self.assertEqual(5, self.project.backlogged_count)

    def test_sprints(self):
        expected = [0, 1, 2]
        actual = [sprint.sprint_number for sprint in self.project.sprints]
        self.assertEqual(expected, actual)
        
        self.assertEqual(1, self.project.current_sprint.sprint_number)
        self.assertEqual("Sprint 1", self.project.current_sprint.name)
        self.assertEqual(1, len(self.project.upcoming_sprints))

    def test_project_title(self):
        self.assertEqual("API Testing Project", self.project.name)
        
def main():
    unittest.main()

if __name__ == "__main__":
    main()
