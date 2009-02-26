
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.application import Application
from gaphor.services.elementdispatcher import ElementDispatcher


class ElementDispatcherTestCase(TestCase):

    def setUp(self):
        super(ElementDispatcherTestCase, self).setUp()
        self.events = []
        self.dispatcher = ElementDispatcher()
        self.dispatcher.init(Application)

    def tearDown(self):
        self.dispatcher.shutdown()
        super(ElementDispatcherTestCase, self).tearDown()

    def _handler(self, event):
        self.events.append(event)


    def test_register_handler(self):
        dispatcher = self.dispatcher
        element = UML.Class()
        dispatcher.register_handler(self._handler, element, 'ownedOperation.parameter.name')
        assert len(dispatcher._handlers) == 1
        assert dispatcher._handlers.keys()[0] == (element, UML.Class.ownedOperation)

        # Add some properties:

        element.ownedOperation = UML.Operation()
        p = element.ownedOperation[0].formalParameter = UML.Parameter()
        p.name = 'func'
        dispatcher.register_handler(self._handler, element, 'ownedOperation.parameter.name')
        assert len(dispatcher._handlers) == 3


    def test_register_handler_2(self):
        dispatcher = self.dispatcher
        element = UML.Class()

        # Add some properties:

        element.ownedOperation = UML.Operation()
        p = element.ownedOperation[0].formalParameter = UML.Parameter()
        dispatcher.register_handler(self._handler, element, 'ownedOperation.parameter.name')

        assert len(self.events) == 0, len(self.events)
        dispatcher.register_handler(self._handler, element, 'ownedOperation.parameter.name')

        p.name = 'func'
        assert len(self.events) == 1, len(self.events)


    def test_unregister_handler(self):

        # First some setup:
        dispatcher = self.dispatcher
        element = UML.Class()
        o = element.ownedOperation = UML.Operation()
        p = element.ownedOperation[0].formalParameter = UML.Parameter()
        p.name = 'func'
        dispatcher.register_handler(self._handler, element, 'ownedOperation.parameter.name')
        assert len(dispatcher._handlers) == 3
        assert dispatcher._handlers[element, UML.Class.ownedOperation]
        assert dispatcher._handlers[o, UML.Operation.parameter]
        assert dispatcher._handlers[p, UML.Parameter.name]

        dispatcher.unregister_handler(self._handler)

        assert len(dispatcher._handlers) == 0, dispatcher._handlers
        assert len(dispatcher._reverse) == 0, dispatcher._reverse
        #assert dispatcher._handlers.keys()[0] == (element, UML.Class.ownedOperation)
        # Should not fail here too:
        dispatcher.unregister_handler(self._handler)


    def test_notification(self):
        """
        Test notifications with Class object.
        """
        dispatcher = self.dispatcher
        element = UML.Class()
        o = element.ownedOperation = UML.Operation()
        p = element.ownedOperation[0].formalParameter = UML.Parameter()
        p.name = 'func'
        dispatcher.register_handler(self._handler, element, 'ownedOperation.parameter.name')
        assert len(dispatcher._handlers) == 3
        assert not self.events

        element.ownedOperation = UML.Operation()
        assert len(self.events) == 1, self.events
        assert len(dispatcher._handlers) == 4
        
        p.name = 'othername'
        assert len(self.events) == 2, self.events

        del element.ownedOperation[o]
        assert len(dispatcher._handlers) == 2


    def test_notification_2(self):
        """
        Test notifications with Transition object.
        """
        dispatcher = self.dispatcher
        element = UML.Transition()
        g = element.guard = UML.Constraint()
        s = g.specification = UML.LiteralSpecification()
        dispatcher.register_handler(self._handler, element, 'guard.specification<LiteralSpecification>.value')
        assert len(dispatcher._handlers) == 3
        assert not self.events
        assert (element.guard, UML.Constraint.specification) in dispatcher._handlers.keys(), dispatcher._handlers.keys()

        s.value = 'x'
        assert len(self.events) == 1, self.events

        element.guard = UML.Constraint()
        assert len(self.events) == 2, self.events
        assert len(dispatcher._handlers) == 2, len(dispatcher._handlers)
        assert (element.guard, UML.Constraint.specification) in dispatcher._handlers.keys()
        element.guard.specification = UML.LiteralSpecification()
        assert len(self.events) == 3, self.events
        assert len(dispatcher._handlers) == 3, len(dispatcher._handlers)


    def test_notification_of_change(self):
        """
        Test notifications with Transition object.
        """
        dispatcher = self.dispatcher
        element = UML.Transition()
        g = element.guard = UML.Constraint()
        s = g.specification = UML.LiteralSpecification()
        dispatcher.register_handler(self._handler, element, 'guard.specification<LiteralSpecification>.value')
        assert len(dispatcher._handlers) == 3
        assert not self.events

        s.value = 'x'
        assert len(self.events) == 1, self.events

        element.guard = UML.Constraint()
        assert len(self.events) == 2, self.events
        

    def test_notification_with_composition(self):
        """
        Test unregister with composition. Use Class.ownedOperation.precondition.
        """
        dispatcher = self.dispatcher
        element = UML.Class()
        o = element.ownedOperation = UML.Operation()
        p = element.ownedOperation[0].precondition = UML.Constraint()
        p.name = 'func'
        dispatcher.register_handler(self._handler, element, 'ownedOperation.precondition.name')
        assert len(dispatcher._handlers) == 3
        assert not self.events

        del element.ownedOperation[o]
        assert len(dispatcher._handlers) == 1


    def test_notification_with_incompatible_elements(self):
        """
        Test unregister with composition. Use Class.ownedOperation.precondition.
        """
        dispatcher = self.dispatcher
        element = UML.Transition()
        g = element.guard = UML.Constraint()
        s = g.specification = UML.LiteralSpecification()
        dispatcher.register_handler(self._handler, element, 'guard.specification<LiteralSpecification>.value')
        assert len(dispatcher._handlers) == 3
        assert not self.events
        assert (element.guard, UML.Constraint.specification) in dispatcher._handlers.keys(), dispatcher._handlers.keys()

        s.value = 'x'
        assert len(self.events) == 1, self.events

        element.guard.specification = UML.ValueSpecification()
        assert len(self.events) == 2, self.events

        s.value = 'a'
        assert len(self.events) == 2, self.events


class ElementDispatcherAsServiceTestCase(TestCase):

    services = TestCase.services + ['element_dispatcher']

    def setUp(self):
        super(ElementDispatcherAsServiceTestCase, self).setUp()
        self.events = []
        self.dispatcher = Application.get_service('element_dispatcher')

    def tearDown(self):
        super(ElementDispatcherAsServiceTestCase, self).tearDown()

    def _handler(self, event):
        self.events.append(event)

    def test_notification(self):
        """
        Test notifications with Class object.
        """
        dispatcher = self.dispatcher
        element = UML.Class()
        o = element.ownedOperation = UML.Operation()
        p = element.ownedOperation[0].formalParameter = UML.Parameter()
        p.name = 'func'
        dispatcher.register_handler(self._handler, element, 'ownedOperation.parameter.name')
        assert len(dispatcher._handlers) == 3
        assert not self.events

        element.ownedOperation = UML.Operation()
        assert len(self.events) == 1, self.events
        assert len(dispatcher._handlers) == 4
        
        p.name = 'othername'
        assert len(self.events) == 2, self.events

        del element.ownedOperation[o]
        assert len(dispatcher._handlers) == 2


    def test_association_notification(self):
        """
        Test notifications with Class object.
        
        Tricky case where no events are fired.
        """
        dispatcher = self.dispatcher
        element = UML.Association()
        p1 = element.memberEnd = UML.Property()
        p2 = element.memberEnd = UML.Property()

        assert len(element.memberEnd) == 2
        print element.memberEnd
        dispatcher.register_handler(self._handler, element, 'memberEnd.name')
        assert len(dispatcher._handlers) == 3, len(dispatcher._handlers)
        assert not self.events

        p1.name = 'foo'
        assert len(self.events) == 1, (self.events, dispatcher._handlers)
        assert len(dispatcher._handlers) == 3
        
        p1.name = 'othername'
        assert len(self.events) == 2, self.events


    def test_association_notification_complex(self):
        """
        Test notifications with Class object.
        
        Tricky case where no events are fired.
        """
        dispatcher = self.dispatcher
        element = UML.Association()
        p1 = element.memberEnd = UML.Property()
        p2 = element.memberEnd = UML.Property()
        p1.lowerValue = UML.LiteralSpecification()
        p1.upperValue = UML.LiteralSpecification()
        p2.lowerValue = UML.LiteralSpecification()
        p2.upperValue = UML.LiteralSpecification()

        assert len(element.memberEnd) == 2
        print element.memberEnd

        base = 'memberEnd<Property>.'
        dispatcher.register_handler(self._handler, element, base + 'name')
        dispatcher.register_handler(self._handler, element, base + 'aggregation')
        dispatcher.register_handler(self._handler, element, base + 'classifier')
        dispatcher.register_handler(self._handler, element, base + 'lowerValue<LiteralSpecification>.value')
        dispatcher.register_handler(self._handler, element, base + 'upperValue<LiteralSpecification>.value')

        assert len(dispatcher._handlers) == 15, len(dispatcher._handlers)
        assert not self.events

        p1.name = 'foo'
        assert len(self.events) == 1, (self.events, dispatcher._handlers)
        assert len(dispatcher._handlers) == 15
        
        p1.name = 'othername'
        assert len(self.events) == 2, self.events


# vim: sw=4:et:ai