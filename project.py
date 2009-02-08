import datetime
import re

try:
    import cElementTree as ElementTree
except ImportError:
    from elementtree import ElementTree

from basecamp import Basecamp

class BasecampObject(object):
    '''Common class of Basecamp objects'''
    def parse_datetime(self, value):
        year = int(value[0:4])
        month = int(value[5:7])
        day = int(value[8:10])
        hour = int(value[11:13])
        minute = int(value[14:16])
        second = int(value[17:19])
        return datetime.datetime(year=year, month=month, day=day,
                                 hour=hour, minute=minute, second=second)

    def parse_date(self, value):
        year = int(value[0:4])
        month = int(value[5:7])
        day = int(value[8:10])
        return datetime.date(year=year, month=month, day=day)

class Project(BasecampObject):
    '''Represents a project in Basecamp.'''
    def __init__(self, url, id, username, password, basecamp=Basecamp):
        self.bc = basecamp(url, username, password)
        self.id = id
        self.cache = dict(messages = [], comments = [],
                          milestones = [], todo_lists = {})
        self._name = ''
        self._status = ''
        self._last_changed_on = ''

    def _get_project_info(self):
        project_xml = self.bc._request("/projects/%s.xml" % self.id)
        node = ElementTree.fromstring(project_xml)
        self._name = node.findtext("name")
        self._status = node.findtext("status")
        self._last_changed_on = node.findtext("last-changed-on")

    @property
    def name(self):
        if not self._name: self._get_project_info()
        return self._name

    @property
    def status(self):
        if not self._status: self._get_project_info()
        return self._status

    @property
    def last_changed_on(self):
        if not self._last_changed_on: self.get_project_info()
        return self.parse_datetime(self._last_changed_on)

    @property
    def messages(self):
        if self.cache['messages']: return self.cache['messages']
        message_xml = self.bc.message_archive(self.id)
        messages = []
        for post in ElementTree.fromstring(message_xml).findall("post"):
            messages.append(Message(post))
        self.cache['messages'] = messages
        return self.cache['messages']

    @property
    def comments(self):
        '''Looks through the last 3 messages and returns those comments.'''
        if self.cache['comments']: return self.cache['comments']
        comments = []
        for message in self.messages[0:3]:
            comment_xml = self.bc.comments(message.id)
            for comment_node in ElementTree.fromstring(comment_xml).findall("comment"):
                comments.append(Comment(comment_node))
        comments.sort()
        comments.reverse()
        self.cache['comments'] = comments
        return self.cache['comments']

    @property
    def milestones(self):
        '''Array of all milestones'''
        if self.cache['milestones']: return self.cache['milestones']
        milestone_xml = self.bc.list_milestones(self.id)
        milestones = []
        for node in ElementTree.fromstring(milestone_xml).findall("milestone"):
            milestones.append(Milestone(node))

        milestones.sort()
        milestones.reverse()
        self.cache['milestones'] = milestones
        return self.cache['milestones']

    @property
    def late_milestones(self):
        '''Array of all late milestones'''
        return [m for m in self.milestones if m.is_late]

    @property
    def upcoming_milestones(self):
        return [m for m in self.milestones if m.is_upcoming]

    @property
    def previous_milestones(self):
        return [m for m in self.milestones if m.is_previous]

    @property
    def todo_lists(self):
        if self.cache['todo_lists']: return self.cache['todo_lists']
        todo_lists_xml = self.bc.todo_lists(self.id)
        todo_lists = {}
        for node in ElementTree.fromstring(todo_lists_xml).findall("todo-list"):
            the_list = ToDoList(node)
            todo_lists[the_list.name] = the_list
        self.cache['todo_lists'] = todo_lists
        return self.cache['todo_lists']

    @property
    def backlogs(self):
        backlogs = {}
        lists = [tdlist for tdlist in self.todo_lists.values() if tdlist.is_backlog]
        for alist in lists:
            backlogs[alist.name] = alist
            
        return backlogs

    @property
    def backlogged_count(self):
        backlogged = 0
        for alist in self.backlogs.values(): backlogged += alist.uncompleted_count
        return backlogged

    @property
    def sprints(self):
        sprints = [tdlist for tdlist in self.todo_lists.values() if tdlist.is_sprint]
        sprints.sort()
        return sprints

    @property
    def current_sprint(self):
        unfinished_sprints = [ tdlist for tdlist in self.sprints if not tdlist.is_complete ]
        unfinished_sprints.sort()
        try:
            return unfinished_sprints[0]
        except IndexError:
            return None

    @property
    def upcoming_sprints(self):
        return [ sprint for sprint in self.sprints if not sprint.is_complete and sprint.sprint_number > self.current_sprint.sprint_number ]

class ToDoList(BasecampObject):
    '''Represents a ToDo list in Basecamp'''
    def __init__(self, node):
        self.id = int(node.findtext("id"))
        self.name = node.findtext("name")
        self.project_id = int(node.findtext("project-id"))
        self._complete = node.findtext("complete")
        self.completed_count = int(node.findtext("completed-count"))
        self.uncompleted_count = int(node.findtext("uncompleted-count"))

    @property
    def is_complete(self):
        if self._complete.lower() in ['true', 'yes', 'y', 't', 1]: return True
        return False

    @property
    def is_sprint(self):
        if 'sprint' in self.name.lower(): return True
        return False

    @property
    def is_backlog(self):
        if 'backlog' in self.name.lower(): return True
        return False

    sprint_number_pattern = re.compile('(Sprint|sprint) (?P<sprint_number>[\d+])')
    @property
    def sprint_number(self):
        result = self.sprint_number_pattern.search(self.name)
        return int(result.group('sprint_number'))

    def __cmp__(self, other):
        if self.is_sprint and other.is_sprint:
            return cmp(self.sprint_number, other.sprint_number)
        return cmp(self.name, other.name)

class Milestone(BasecampObject):
    '''Represents a milestone in Basecamp'''
    def __init__(self, node):
        self.id = int(node.findtext("id"))
        self.title = node.findtext("title")
        self._deadline = node.findtext("deadline")
        self._completed = node.findtext("completed")

    def __cmp__(self, other):
        return cmp(self.deadline, other.deadline)

    @property
    def is_previous(self):
        if self.deadline < datetime.date.today(): return True

    @property
    def is_upcoming(self):
        if self.deadline >= datetime.date.today(): return True

    @property
    def is_late(self):
        if self.completed: return False
        if self.deadline < datetime.date.today(): return True

    @property
    def completed(self):
        if self._completed.lower() in ["true", "1", "yes"]:
            return True
        return False

    @property
    def deadline(self):
        return self.parse_date(self._deadline)

class Comment(BasecampObject):
    '''Represents a comment on a message in Basecamp'''
    def __init__(self, node):
        self.id = int(node.findtext("id"))
        self.body = node.findtext("body")
        self._posted_on = node.findtext("posted-on")
        self.author_id = id(node.findtext("author-id"))

    @property
    def posted_on(self):
        return self.parse_datetime(self._posted_on)

    def __cmp__(self, other):
        value = cmp(self.posted_on, other.posted_on)
        return value

class Message(BasecampObject):
    '''Represents a Message in Basecamp'''
    def __init__(self, message_element):
        self.id = int(message_element.findtext("id"))
        self.title = message_element.findtext("title")
        self._posted_on = message_element.findtext("posted-on")

    @property
    def posted_on(self):
        return self.parse_datetime(self._posted_on)

if __name__ == "__main__":
    from tests import *
    main()
