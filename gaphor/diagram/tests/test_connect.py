"""
Test Item connections.
"""

import unittest
from zope import component
from gaphor import resource
from gaphor import UML
from gaphor.ui.mainwindow import MainWindow
from gaphor.diagram import CommentItem, CommentLineItem
from gaphor.diagram.actor import ActorItem
from gaphor.diagram.tool import ConnectHandleTool
from gaphor.diagram.interfaces import IConnect


class HandleToolTestCase(unittest.TestCase):

    def test_commentline(self):
        """Test CommentLineItem connecting to comment and Actor items.
        """
        diagram = UML.create(UML.Diagram)
        comment = diagram.create(CommentItem, subject=UML.create(UML.Comment))
        line = diagram.create(CommentLineItem)
        actor = diagram.create(ActorItem, subject=UML.create(UML.Actor))
        actor2 = diagram.create(ActorItem, subject=UML.create(UML.Actor))

        # Connect the comment item to the head of the line:

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.handles()[0]
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is comment
        assert handle._connect_constraint is not None
        assert not comment.subject.annotatedElement

        # Connecting two ends of the line to the same item is not allowed:

        handle = line.handles()[-1]
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is None
        assert not hasattr(handle,'_connect_constraint')
        assert not comment.subject.annotatedElement, comment.subject.annotatedElement

        print '# now connect the actor'

        adapter = component.queryMultiAdapter((actor, line), IConnect)

        handle = line.handles()[-1]
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is actor
        assert handle._connect_constraint is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Same thing with another actor
        # (should disconnect the already connected actor):

        handle = line.handles()[-1]
        adapter = component.queryMultiAdapter((actor2, line), IConnect)
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is actor2
        assert handle._connect_constraint is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor2.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Disconnect actor:

        adapter.disconnect(handle)

        assert handle.connected_to is None, handle.connected_to
        assert handle._connect_constraint is None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert not actor2.subject in comment.subject.annotatedElement, comment.subject.annotatedElement



