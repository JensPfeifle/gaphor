from builtins import object
from gi.repository import Gtk
from gaphor.tests.testcase import TestCase
from gaphor.application import Application
from gaphor.ui.diagramtab import DiagramTab
from gaphor.ui.diagramtoolbox import DiagramToolbox, TOOLBOX_ACTIONS
from gaphor import UML


class WindowOwner(object):
    """
    Placeholder object for a MainWindow. Should provide just enough
    methods to make the tests work.
    """

    def remove_tab(self, other):
        pass


class DiagramToolboxTestCase(TestCase):

    services = ["element_factory", "properties", "element_dispatcher"]

    def setUp(self):
        TestCase.setUp(self)
        diagram = self.diagram
        tab = DiagramTab(WindowOwner())
        tab.diagram = diagram
        tab.construct()
        self.tab = tab

    def tearDown(self):
        TestCase.tearDown(self)

    def test_toolbox_actions_shortcut_unique(self):

        shortcuts = {}

        for category, items in TOOLBOX_ACTIONS:

            for action_name, label, stock_id, shortcut in items:

                try:

                    shortcuts[shortcut].append(action_name)

                except KeyError:

                    shortcuts[shortcut] = [action_name]

        for key, val in list(shortcuts.items()):

            if key is not None:

                self.assertEqual(len(val), 1, "Duplicate toolbox shortcut")

    def test_standalone_construct_with_diagram(self):
        pass  # is setUp()

    def _test_placement_action(self, action):
        self.tab.toolbox.action_group.get_action(action).activate()
        assert self.tab.view.tool
        # Ensure the factory is working
        self.tab.view.tool._factory()
        self.diagram.canvas.update()

    def test_placement_pointer(self):
        self.tab.toolbox.action_group.get_action("toolbox-pointer").activate()

    def test_placement_comment(self):
        self._test_placement_action("toolbox-comment")

    def test_placement_comment_line(self):
        self._test_placement_action("toolbox-comment-line")

    # Classes:

    def test_placement_class(self):
        self._test_placement_action("toolbox-class")

    def test_placement_interface(self):
        self._test_placement_action("toolbox-interface")

    def test_placement_package(self):
        self._test_placement_action("toolbox-package")

    def test_placement_association(self):
        self._test_placement_action("toolbox-association")

    def test_placement_dependency(self):
        self._test_placement_action("toolbox-dependency")

    def test_placement_generalization(self):
        self._test_placement_action("toolbox-generalization")

    def test_placement_implementation(self):
        self._test_placement_action("toolbox-implementation")

    # Components:

    def test_placement_component(self):
        self._test_placement_action("toolbox-component")

    def test_placement_node(self):
        self._test_placement_action("toolbox-node")

    def test_placement_artifact(self):
        self._test_placement_action("toolbox-artifact")

    # Actions:

    def test_placement_action(self):
        self._test_placement_action("toolbox-action")

    def test_placement_initial_node(self):
        self._test_placement_action("toolbox-initial-node")

    def test_placement_activity_final_node(self):
        self._test_placement_action("toolbox-activity-final-node")

    def test_placement_flow_final_node(self):
        self._test_placement_action("toolbox-flow-final-node")

    def test_placement_decision_node(self):
        self._test_placement_action("toolbox-decision-node")

    def test_placement_fork_node(self):
        self._test_placement_action("toolbox-fork-node")

    def test_placement_object_node(self):
        self._test_placement_action("toolbox-object-node")
        self.assertEqual(1, len(self.kindof(UML.ObjectNode)))

    def test_placement_partition(self):
        self._test_placement_action("toolbox-partition")
        self.assertEqual(0, len(self.kindof(UML.ActivityPartition)))

    def test_placement_flow(self):
        self._test_placement_action("toolbox-flow")

    # Use cases:

    def test_usecase(self):
        self._test_placement_action("toolbox-usecase")

    def test_actor(self):
        self._test_placement_action("toolbox-actor")

    def test_usecase_association(self):
        self._test_placement_action("toolbox-usecase-association")

    def test_include(self):
        self._test_placement_action("toolbox-include")

    def test_extend(self):
        self._test_placement_action("toolbox-extend")

    # Profiles:

    def test_profile(self):
        self._test_placement_action("toolbox-profile")

    def test_metaclass(self):
        self._test_placement_action("toolbox-metaclass")

    def test_stereotype(self):
        self._test_placement_action("toolbox-stereotype")

    def test_extension(self):
        self._test_placement_action("toolbox-extension")


# vim:sw=4:et:ai
