
import unittest
from gaphor import resource
from gaphor.ui.mainwindow import MainWindow
from gaphor.diagram.tool import PlacementTool
from gaphor.diagram import placementactions
from gaphor import UML
from gaphas.canvas import Context
from gaphas.view import ToolContext

Event = Context


class PlacementToolTestCase(unittest.TestCase):

    main_window = resource(MainWindow)
    main_window.construct()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def do_test_placement(self, action):
        diagram = UML.create(UML.Diagram)
        self.main_window.show_diagram(diagram)
        #action = CommentPlacementAction()
        action.init(self.main_window)
        tool = PlacementTool(item_factory=action.item_factory, action_id=action.id)
        # what's a good way to test the events?
        view = self.main_window.get_current_diagram_view()
        assert view, 'View should be available here'
        tool.on_button_press(ToolContext(view=view), Event(x=10, y=10))

    def test_comment_placement(self):
        self.do_test_placement(placementactions.CommentPlacementAction())

    def test_actor_placement(self):
        self.do_test_placement(placementactions.ActorPlacementAction())

    def test_comment_line_placement(self):
        self.do_test_placement(placementactions.CommentLinePlacementAction())

    def test_use_case_placement(self):
        self.do_test_placement(placementactions.UseCasePlacementAction())


# vim:sw=4:et:ai
