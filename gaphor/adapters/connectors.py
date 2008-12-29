"""
Connector adapters.

To register connectors implemented in this module, it is imported in
gaphor.adapter package.
"""

from zope import interface, component

from gaphas import geometry
from gaphor import UML
from gaphor.core import inject
from gaphor.diagram.interfaces import IConnect
from gaphor.diagram import items


class disconnect_handle(object):
    """
    Helper for handle disconnection. Those objects are used, in stead of bound
    methods, since the pickle persister can't handle bound methods.
    """

    def __init__(self, adapter, handle):
        self.adapter = adapter
        self.handle = handle

    def __call__(self):
        self.adapter.disconnect(self.handle)


class AbstractConnect(object):
    """
    Connection adapter for Gaphor diagram items.

    Line item ``line`` connects with a handle to a connectable item ``element``.

    Attributes:

    - line: connecting item
    - element: connectable item
    - _canvas: canvas reference
    """
    interface.implements(IConnect)

    element_factory = inject('element_factory')

    def __init__(self, element, line):
        self.element = element
        self.line = line


    def glue(self, handle, port):
        """
        Determine if items can be connected.

        The method contains a hack for folded interfaces, see
        `gaphor.diagram.classes.interface` module documentation for
        connection to folded interface rules.

        Returns `True` by default.
        """
        iface = self.element
        if isinstance(iface, items.InterfaceItem) and iface.folded:
            canvas = iface.canvas
            count = len(canvas.get_connected_items(iface))
            return count == 0 and isinstance(self.line, (items.DependencyItem, items.ImplementationItem))
        return True


    def connect(self, handle, port):
        """
        Connect to an element. Note that at this point the line may
        be connected to some other, or the same element by means of the
        handle.connected_to property. Also the connection at UML level
        still exists.
        
        Returns `True` if a connection is established.
        """
        return True


    def disconnect(self, handle):
        """
        Disconnect UML model level connections.
        """
        pass



class CommentLineElementConnect(AbstractConnect):
    """
    Connect a comment line to any element item.
    """
    component.adapts(items.ElementItem, items.CommentLineItem)

    def glue(self, handle, port):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        element = self.element
        connected_to = opposite.connected_to
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            #print 'Subjects none or match:', connected_to.subject, element.subject
            return None

        # One end should be connected to a CommentItem:
        cls = items.CommentItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        return super(CommentLineElementConnect, self).glue(handle, port)

    def connect(self, handle, port):
        if super(CommentLineElementConnect, self).connect(handle, port):
            opposite = self.line.opposite(handle)
            if opposite.connected_to:
                if isinstance(opposite.connected_to.subject, UML.Comment):
                    opposite.connected_to.subject.annotatedElement = self.element.subject
                else:
                    self.element.subject.annotatedElement = opposite.connected_to.subject

    def disconnect(self, handle):
        opposite = self.line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            if isinstance(opposite.connected_to.subject, UML.Comment):
                del opposite.connected_to.subject.annotatedElement[handle.connected_to.subject]
            elif opposite.connected_to.subject:
                del handle.connected_to.subject.annotatedElement[opposite.connected_to.subject]
        super(CommentLineElementConnect, self).disconnect(handle)

component.provideAdapter(CommentLineElementConnect)


class CommentLineLineConnect(AbstractConnect):
    """
    Connect a comment line to any diagram line.
    """
    component.adapts(items.DiagramLine, items.CommentLineItem)

    def glue(self, handle, port):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        element = self.element
        connected_to = opposite.connected_to

        # do not connect to the same item nor connect to other comment line
        if connected_to is element or isinstance(element, items.CommentLineItem):
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        # One end should be connected to a CommentItem:
        cls = items.CommentItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        return super(CommentLineLineConnect, self).glue(handle, port)

    def connect(self, handle, port):
        if super(CommentLineLineConnect, self).connect(handle, port):
            opposite = self.line.opposite(handle)
            if opposite.connected_to and self.element.subject:
                if isinstance(opposite.connected_to.subject, UML.Comment):
                    opposite.connected_to.subject.annotatedElement = self.element.subject
                else:
                    self.element.subject.annotatedElement = opposite.connected_to.subject

    def disconnect(self, handle):
        opposite = self.line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            if isinstance(handle.connected_to.subject, UML.Comment):
                del handle.connected_to.subject.annotatedElement[opposite.connected_to.subject]
            elif opposite.connected_to.subject:
                del opposite.connected_to.subject.annotatedElement[handle.connected_to.subject]
        super(CommentLineLineConnect, self).disconnect(handle)

component.provideAdapter(CommentLineLineConnect)


class RelationshipConnect(AbstractConnect):
    """
    Base class for relationship connections, such as associations,
    dependencies and implementations.

    This class introduces a new method: relationship() which is used to
    find an existing relationship in the model that does not yet exist
    on the canvas.
    """

    element_factory = inject('element_factory')

    # relationships can sometimes by unary, i.e. association, flow
    # override in deriving class to allow unary relationship
    CAN_BE_UNARY = False

    def glue(self, handle, port):
        """
        In addition to the normal check, both relationship ends may not be
        connected to the same element. Same goes for subjects.
        """
        if not self.CAN_BE_UNARY:
            opposite = self.line.opposite(handle)
            line = self.line
            element = self.element
            connected_to = opposite.connected_to

            # Element can not be a parent for itself.
            if connected_to is element:
                return None

            # Same goes for subjects:
            if connected_to and \
                    (not (connected_to.subject or element.subject)) \
                     and connected_to.subject is element.subject:
                return None

        return super(RelationshipConnect, self).glue(handle, port)


    def relationship(self, required_type, head, tail):
        """
        Find an existing relationship in the model that meets the
        required type and is connected to the same model element the head
        and tail of the line are conncted to.

        type - the type of relationship we're looking for
        head - tuple (association name on line, association name on element)
        tail - tuple (association name on line, association name on element)
        """
        line = self.line
        element = self.element

        head_subject = line.head.connected_to.subject
        tail_subject = line.tail.connected_to.subject

        edge_head_name = head[0]
        node_head_name = head[1]
        edge_tail_name = tail[0]
        node_tail_name = tail[1]

        # First check if the right subject is already connected:
        if line.subject \
           and getattr(line.subject, edge_head_name) is head_subject \
           and getattr(line.subject, edge_tail_name) is tail_subject:
            return line.subject

        # This is the type of the relationship we're looking for
        #required_type = getattr(type(tail_subject), node_tail_name).type

        # Try to find a relationship, that is already created, but not
        # yet displayed in the diagram.
        for gen in getattr(tail_subject, node_tail_name):
            if not isinstance(gen, required_type):
                continue
                
            gen_head = getattr(gen, edge_head_name)
            try:
                if not head_subject in gen_head:
                    continue
            except TypeError:
                if not gen_head is head_subject:
                    continue

            # check for this entry on line.canvas
            for item in gen.presentation:
                # Allow line to be returned. Avoids strange
                # behaviour during loading
                if item.canvas is line.canvas and item is not line:
                    break
            else:
                return gen
        return None

    def relationship_or_new(self, type, head, tail):
        """
        Like relation(), but create a new instance of none was found.
        """
        relation = self.relationship(type, head, tail)
        if not relation:
            line = self.line
            relation = self.element_factory.create(type)
            setattr(relation, head[0], line.head.connected_to.subject)
            setattr(relation, tail[0], line.tail.connected_to.subject)
        return relation

    def connect_connected_items(self, connected_items=None):
        """
        Cause items connected to ``line`` to reconnect, allowing them to
        establish or destroy relationships at model level.
        """
        line = self.line
        canvas = line.canvas
        solver = canvas.solver

        # First make sure coordinates match
        solver.solve()
        for item, handle in connected_items or line.canvas.get_connected_items(line):
            adapter = component.queryMultiAdapter((line, item), IConnect)
            assert adapter
            adapter.connect(handle)
        
    def disconnect_connected_items(self):
        """
        Cause items connected to @line to be disconnected.
        This is nessesary if the subject of the @line is to be removed.

        Returns a list of (item, handle) pairs that were connected (this
        list can be used to connect items again with connect_connected_items()).
        """
        line = self.line
        canvas = line.canvas
        solver = canvas.solver

        # First make sure coordinates match
        solver.solve()
        connected_items = list(line.canvas.get_connected_items(line))
        for item, handle in connected_items:
            adapter = component.queryMultiAdapter((line, item), IConnect)
            assert adapter
            adapter.disconnect(handle)
        return connected_items

    def connect_subject(self, handle):
        """
        Establish the relationship at model level.
        """
        raise NotImplemented, 'Implement connect_subject() in a subclass'

    def disconnect_subject(self, handle):
        """
        Disconnect the diagram item from its model element. If there are
        no more presentations(diagram items) connected to the model element,
        unlink() it too.
        """
        line = self.line
        old = line.subject
        del line.subject
        if old and len(old.presentation) == 0:
            old.unlink()

    def connect(self, handle, port):
        """
        Connect the items to each other. The model level relationship
        is created by create_subject()
        """
        if super(RelationshipConnect, self).connect(handle, port):
            opposite = self.line.opposite(handle)
            if opposite.connected_to:
                self.connect_subject(handle)
                line = self.line
                if line.subject:
                    self.connect_connected_items()
            return True


    def disconnect(self, handle):
        """
        Disconnect model element.
        """
        line = self.line
        opposite = line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            old = line.subject
             
            connected_items = self.disconnect_connected_items()
            
            self.disconnect_subject(handle)
            if old:
                self.connect_connected_items(connected_items)

        super(RelationshipConnect, self).disconnect(handle)


class ImplementationConnect(RelationshipConnect):
    """
    Connect Interface and a BehavioredClassifier using an Implementation.
    """
    component.adapts(items.NamedItem, items.ImplementationItem)

    def glue(self, handle, port):
        line = self.line
        element = self.element

        # Element at the head should be an Interface
        if handle is line.head and \
           not isinstance(element.subject, UML.Interface):
            return None

        # Element at the tail should be a BehavioredClassifier
        if handle is line.tail and \
           not isinstance(element.subject, UML.BehavioredClassifier):
            return None

        return super(ImplementationConnect, self).glue(handle, port)


    def connect_subject(self, handle):
        """
        Perform implementation relationship connection.
        """
        relation = self.relationship_or_new(UML.Implementation,
                    ('contract', None),
                    ('implementatingClassifier', 'implementation'))
        self.line.subject = relation


component.provideAdapter(ImplementationConnect)


class IncludeConnect(RelationshipConnect):
    """
    Connect Usecases with a Include relationship.
    """
    component.adapts(items.UseCaseItem, items.IncludeItem)

    def glue(self, handle, port):
        line = self.line
        element = self.element

        if not (element.subject and isinstance(element.subject, UML.UseCase)):
            return None

        return super(IncludeConnect, self).glue(handle, port)

    def connect_subject(self, handle):
        relation = self.relationship_or_new(UML.Include,
                    ('addition', None),
                    ('includingCase', 'include'))
        self.line.subject = relation

component.provideAdapter(IncludeConnect)


class ExtendConnect(RelationshipConnect):
    """
    Connect Usecases with a Extend relationship.
    """
    component.adapts(items.UseCaseItem, items.ExtendItem)

    def glue(self, handle, port):
        line = self.line
        element = self.element
        
        if not (element.subject and isinstance(element.subject, UML.UseCase)):
            return None

        return super(ExtendConnect, self).glue(handle, port)

    def connect_subject(self, handle):
        relation = self.relationship_or_new(UML.Extend,
                    ('extendedCase', None),
                    ('extension', 'extend'))
        self.line.subject = relation

component.provideAdapter(ExtendConnect)


class MessageLifelineConnect(AbstractConnect):
    """
    Connect lifeline with a message.

    A message can connect to both the lifeline's head (the rectangle)
    or the lifetime line. In case it's added to the head, the message
    is considered to be part of a communication diagram. If the message is
    added to a lifetime line, it's considered a sequence diagram.

    """

    component.adapts(items.LifelineItem, items.MessageItem)

    element_factory = inject('element_factory')

    def connect_lifelines(self, line, send, received):
        """
        Always create a new Message with two EventOccurence instances.
        """
        def get_subject():
            if not line.subject:
                message = self.element_factory.create(UML.Message)
                message.name = 'call()'
                line.subject = message
            return line.subject

        if send:
            message = get_subject()
            if not message.sendEvent:
                event = self.element_factory.create(UML.EventOccurrence)
                event.sendMessage = message
                event.covered = send.subject

        if received:
            message = get_subject()
            if not message.receiveEvent:
                event = self.element_factory.create(UML.EventOccurrence)
                event.receiveMessage = message
                event.covered = received.subject


    def disconnect_lifelines(self, line):
        """
        Disconnect lifeline and set appropriate kind of message item. If
        there are no lifelines connected on both ends, then remove the message
        from the data model.
        """
        send = line.head.connected_to
        received = line.tail.connected_to

        if send:
            event = line.subject.receiveEvent
            if event:
                event.unlink()

        if received:
            event = line.subject.sendEvent
            if event:
                event.unlink()

        if not send and not received:
            # Both ends are disconnected:
            message = line.subject
            del line.subject
            if not message.presentation:
                message.unlink()
            for message in list(line._messages):
                line.remove_message(message, False)
                message.unlink()

            for message in list(line._inverted_messages):
                line.remove_message(message, True)
                message.unlink()


    def _glue_lifetime(self, handle):
        """
        Glue ``handle`` to lifeline's lifetime.

        The position returned is in line coordinates.
        """
        lifetime = self.element.lifetime
        top = lifetime.top.pos
        bottom = lifetime.bottom.pos

        pos = self._matrix_l2e.transform_point(*handle.pos)
        d, pos = geometry.distance_line_point(top, bottom, pos)

        return self._matrix_e2l.transform_point(*pos)


    def glue(self, handle, port):
        """
        Glue to lifeline's head or lifetime. If lifeline's lifetime is
        visible then disallow connection to lifeline's head.
        """
        element = self.element
        lifetime = element.lifetime
        line = self.line
        opposite = line.opposite(handle)

        pos = None
        if opposite.connected_to:
            opposite_is_visible = opposite.connected_to.lifetime.is_visible

            if lifetime.is_visible and opposite_is_visible:
                # glue lifetimes if both are visible
                pos = self._glue_lifetime(handle)
            elif not lifetime.is_visible and not opposite_is_visible:
                # glue heads if both lifetimes are invisible
                pos = AbstractConnect.glue(self, handle)

        elif lifetime.is_visible:
            pos = self._glue_lifetime(handle)

        else:
            pos = AbstractConnect.glue(self, handle)
        return pos
        

    def _get_segment(self, handle):
        """
        Return handles of one of lifeline head's side or lifetime handles.
        """
        element = self.element
        if element.lifetime.is_visible:
            return element.handles()[-2:] # return lifeline's lifetime handles
        else:
            return super(MessageLifelineConnect, self)._get_segment(handle)
        assert False


    def connect(self, handle, port):
        if not AbstractConnect.connect(self, handle, port):
            return

        line = self.line
        send = line.head.connected_to
        received = line.tail.connected_to
        self.connect_lifelines(line, send, received)

        lifetime = self.element.lifetime
        # if no lifetime then disallow making lifetime visible
        if not lifetime.is_visible:
            lifetime.bottom.movable = False
        # todo: move code above to LifetimeItem class
        lifetime._messages_count += 1


    def disconnect(self, handle):
        line = self.line
        send = line.head.connected_to
        received = line.tail.connected_to

        # if a message is delete message, then disconnection causes
        # lifeline to be no longer destroyed (note that there can be
        # only one delete message connected to lifeline)
        if received and line.subject.messageSort == 'deleteMessage':
            received.lifetime.is_destroyed = False
            received.request_update()

        AbstractConnect.disconnect(self, handle)
        self.disconnect_lifelines(line)

        lifetime = self.element.lifetime
        lifetime._messages_count -= 1
        # if there are no messages connected then allow to make lifetime visible
        # todo: move code below to LifetimeItem class
        if lifetime._messages_count < 1:
            lifetime.bottom.movable = True


component.provideAdapter(MessageLifelineConnect)


# vim:sw=4:et:ai
