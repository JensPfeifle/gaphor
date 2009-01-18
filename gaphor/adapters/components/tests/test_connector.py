"""
Test connector item connectors.
"""

from gaphor.tests import TestCase
from zope import component
from gaphor import UML
from gaphor.diagram import items

from gaphor.adapters.components.connectorconnect import _interfaces



class ComponentConnectTestCase(TestCase):
    """
    Test connection of connector item to a component.
    """
    def test_glue(self):
        """Test glueing connector to component
        """
        component = self.create(items.ComponentItem, UML.Component)
        line = self.create(items.ConnectorItem)

        glued = self.glue(line, line.head, component)
        self.assertTrue(glued)


    def test_connection(self):
        """Test connecting connector to a component
        """
        component = self.create(items.ComponentItem, UML.Component)
        line = self.create(items.ConnectorItem)

        self.connect(line, line.head, component)
        self.assertTrue(line.subject is None)
        self.assertTrue(line.end is None)


    def test_glue_both(self):
        """Test glueing connector to component when one is connected
        """
        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)
        line = self.create(items.ConnectorItem)

        self.connect(line, line.head, c1)
        glued = self.glue(line, line.tail, c2)
        self.assertFalse(glued)



class InterfaceConnectTestCase(TestCase):
    """
    Test connection with interface acting as assembly connector.
    """
    def test_non_folded_glue(self):
        """Test non-folded interface glueing
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        glued = self.glue(line, line.head, iface)
        self.assertFalse(glued)


    def test_folded_glue(self):
        """Test folded interface glueing
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_REQUIRED
        glued = self.glue(line, line.head, iface)
        self.assertTrue(glued)


    def test_glue_when_dependency_connected(self):
        """Test interface glueing, when dependency connected
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        dep = self.create(items.DependencyItem)
        line = self.create(items.ConnectorItem)

        self.connect(dep, dep.head, iface)

        iface.folded = iface.FOLDED_REQUIRED
        glued = self.glue(line, line.head, iface)
        self.assertFalse(glued)


    def test_glue_when_implementation_connected(self):
        """Test interface glueing, when implementation connected
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        impl = self.create(items.ImplementationItem)
        line = self.create(items.ConnectorItem)

        self.connect(impl, impl.head, iface)

        iface.folded = iface.FOLDED_REQUIRED
        glued = self.glue(line, line.head, iface)
        self.assertFalse(glued)


    def test_glue_when_connector_connected(self):
        """Test interface glueing, when connector connected
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        iface.folded = iface.FOLDED_REQUIRED

        line1 = self.create(items.ConnectorItem)
        line2 = self.create(items.ConnectorItem)

        self.connect(line1, line1.head, iface)
        self.assertEquals(iface.FOLDED_ASSEMBLY, iface.folded)

        glued = self.glue(line2, line2.head, iface)
        self.assertTrue(glued)


    def test_simple_connection(self):
        """Test simple connection to an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # test preconditions
        assert not pport.provided and not pport.required
        assert not rport.provided and not rport.required

        self.connect(line, line.head, iface, pport)
        # interface goes into assembly mode
        self.assertEquals(iface.FOLDED_ASSEMBLY, iface.folded)
        self.assertFalse(iface._name.is_visible())

        # no UML metamodel yet
        self.assertTrue(line.subject is None)
        self.assertTrue(line.end is None)

        # check port status
        self.assertTrue(pport.provided and not pport.required and pport.connectable)
        self.assertTrue(rport.required and not rport.provided and rport.connectable)
        p1 = iface.ports()[1]
        p2 = iface.ports()[3]
        self.assertTrue(not p1.required and not p1.provided and not p1.connectable)
        self.assertTrue(not p2.required and not p2.provided and not p2.connectable)


    def test_connection_angle_change(self):
        """Test angle after connection to an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[1]
        rport = iface.ports()[3]

        # test preconditions
        assert not pport.provided and not pport.required
        assert not rport.provided and not rport.required
        assert iface._angle == 0.0

        self.connect(line, line.head, iface, pport)
        self.assertEquals(rport.angle, iface._angle)


    def test_connection_of_two_connectors_one_side(self):
        """Test connection of two connectors to required port of an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        c1 = self.create(items.ConnectorItem)
        c2 = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # connect to the same interface
        self.connect(c1, c1.head, iface, pport)
        self.connect(c2, c2.head, iface, pport)

        # no UML metamodel yet
        self.assertTrue(c1.subject is None)
        self.assertTrue(c1.end is None)
        self.assertTrue(c2.subject is None)
        self.assertTrue(c2.end is None)

        # check port status
        self.assertTrue(pport.provided and not pport.required)
        self.assertTrue(rport.required and not rport.provided)
        p1 = iface.ports()[1]
        p2 = iface.ports()[3]
        self.assertTrue(not p1.required and not p1.provided)
        self.assertTrue(not p2.required and not p2.provided)


    def test_connection_of_two_connectors_two_sides(self):
        """Test connection of two connectors to required and provided ports of an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        c1 = self.create(items.ConnectorItem)
        c2 = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        self.connect(c1, c1.head, iface, pport)
        self.connect(c2, c2.head, iface, rport)

        # no UML metamodel yet
        self.assertTrue(c1.subject is None)
        self.assertTrue(c1.end is None)
        self.assertTrue(c2.subject is None)
        self.assertTrue(c2.end is None)

        # check port status
        self.assertTrue(pport.provided and not pport.required)
        self.assertTrue(rport.required and not rport.provided)
        p1 = iface.ports()[1]
        p2 = iface.ports()[3]
        self.assertTrue(not p1.required and not p1.provided)
        self.assertTrue(not p2.required and not p2.provided)


    def test_simple_disconnection(self):
        """Test disconnection of simple connection to an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[1]

        self.connect(line, line.head, iface, pport)

        # test preconditions
        assert pport.provided and not pport.required and pport.connectable

        self.disconnect(line, line.head)
        self.assertEquals(iface.FOLDED_PROVIDED, iface.folded)
        self.assertEquals(iface._angle, 0)
        self.assertTrue(iface._name.is_visible())

        self.assertFalse(any(p.provided for p in iface.ports()))
        self.assertFalse(any(p.required for p in iface.ports()))
        self.assertTrue(all(p.connectable for p in iface.ports()))



class AssemblyConnectorTestCase(TestCase):
    """
    Test assembly connector. It is assumed that interface and component
    connection tests defined above are working correctly.
    """
    def create_interfaces(self, *args):
        """
        Generate interfaces with names sepecified by arguments.

        :Paramters:
         args
            List of interface names.
        """
        for name in args:
            interface = self.element_factory.create(UML.Interface)
            interface.name = name
            yield interface


    def provide(self, component, interface):
        """
        Change component's data so it implements interfaces.
        """
        impl = self.element_factory.create(UML.Implementation)
        component.implementation = impl
        impl.contract = interface


    def require(self, component, interface):
        """
        Change component's data so it requires interface.
        """
        usage = self.element_factory.create(UML.Usage)
        component.clientDependency = usage
        usage.supplier = interface


    def test_connection(self):
        """Test basic assembly connection
        """
        conn1 = self.create(items.ConnectorItem)
        conn2 = self.create(items.ConnectorItem)

        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)

        iface = self.create(items.InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # first component provides interface
        # and the second one requires it
        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)

        # connect component
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        # make an assembly
        self.connect(conn1, conn1.tail, iface, pport)
        self.connect(conn2, conn2.tail, iface, rport)

        # test UML data model
        self.assertTrue(conn1.subject is conn2.subject,
            '%s is not %s' % (conn1.subject, conn2.subject))
        assembly = conn1.subject
        self.assertTrue(isinstance(assembly, UML.Connector))
        self.assertEquals('assembly', assembly.kind)

        # there should be two connector ends
        self.assertEquals(2, len(assembly.end))
        # interface is on both ends
        end1 = conn1.end
        end2 = conn2.end
        self.assertTrue(end1 in assembly.end)
        self.assertTrue(end2 in assembly.end)
        self.assertEquals(end1.role, iface.subject)
        self.assertEquals(end2.role, iface.subject)
        # connector ends point to components 
        p1 = end1.partWithPort
        p2 = end2.partWithPort
        self.assertEquals(p1, c1.subject.ownedPort)
        self.assertEquals(p2, c2.subject.ownedPort)


#   def test_interfaces_gathering(self):
#       """Test interfaces gathering
#       """
#       c1 = self.c1
#       c2 = self.c2
#       c3 = self.create(items.ComponentItem, UML.Component)

#       i1, = self._create_interfaces('A')

#       self._provide(c1.subject, i1)
#       self._require(c2.subject, i1)
#       self._provide(c3.subject, i1)

#       ifaces = _interfaces([c1, c3], [c2])
#       self.assertEquals(1, len(ifaces), 'interfaces %s' % ifaces)
#       self.assertTrue(i1 in ifaces, 'interfaces %s' % ifaces)




#   def test_groupped_connector_disconnection(self):
#       """Test groupped assembly connectors disconnection
#       """
#       self.connect(self.line, self.line.head, self.c1)

#       i1, = self._create_interfaces('A')
#       self._provide(self.c1.subject, i1)
#       self._require(self.c2.subject, i1)

#       connected = self.connect(self.line, self.line.tail, self.c2)
#       assert connected

#       assembly = self.create(items.ConnectorItem)
#       c3 = self.create(items.ComponentItem, UML.Component)
#       self._provide(c3.subject, i1)
#       self.connect(assembly, assembly.head, c3)

#       connected = self.connect(assembly, assembly.tail, self.line, self.line._provided_port)
#       assert connected

#       self.disconnect(assembly, assembly.tail)
#       
#       self.assertEquals(1, len(self.kindof(UML.Connector)))
#       self.assertEquals([self.line.subject], self.kindof(UML.Connector))
#       self.assertEquals(2, len(self.kindof(UML.ConnectorEnd)))
#       self.assertEquals(2, len(self.kindof(UML.Port)))


#   def test_component_intersection(self):
#       """Test component intersection of provided and required interfaces"""

#       i1, i2 = self._create_interfaces('A', 'B')

#       query = (self.c1, self.line)
#       adapter = component.queryMultiAdapter(query, IConnect)

#       # no provided/required interfaces
#       interfaces = adapter._get_interfaces(self.c1, self.c2)
#       self.assertEquals([], interfaces)

#       # c1 provides i1
#       self._provide(self.c1.subject, i1)
#       interfaces = adapter._get_interfaces(self.c1, self.c2)
#       self.assertEquals([], interfaces)

#       # c1 provides i1 and c2 requires i1
#       self._require(self.c2.subject, i1)
#       interfaces = adapter._get_interfaces(self.c1, self.c2)
#       self.assertEquals([i1], interfaces)

#       # c1 provides i1 and i2, c2 requires i1 only 
#       self._provide(self.c1.subject, i2)
#       interfaces = adapter._get_interfaces(self.c1, self.c2)
#       self.assertEquals([i1], interfaces)

#       # both components require and provide interfaces i1 and i2
#       self._require(self.c2.subject, i2)
#       interfaces = adapter._get_interfaces(self.c1, self.c2)
#       self.assertEquals([i1, i2], interfaces)


#   def test_components_connection(self):
#       """Test components connection
#       """
#       self.connect(self.line, self.line.head, self.c1)

#       i1, = self._create_interfaces('A')
#       self._provide(self.c1.subject, i1)
#       self._require(self.c2.subject, i1)

#       self.assertFalse(self.line.is_assembly)

#       connected = self.connect(self.line, self.line.tail, self.c2)
#       self.assertTrue(connected)

#       # test UML data model
#       # is connector really connector?
#       self.assertTrue(isinstance(self.line.subject, UML.Connector))
#       connector = self.line.subject
#       # there should be two connector ends
#       self.assertEquals(2, len(connector.end))
#       # interface i1 is on both ends
#       end1 = connector.end[0]
#       end2 = connector.end[1]
#       self.assertEquals(i1, end1.role)
#       self.assertEquals(i1, end2.role)
#       # connector ends identify components 
#       p1 = end1.partWithPort
#       p2 = end2.partWithPort
#       self.assertEquals(p1, self.c1.subject.ownedPort)
#       self.assertEquals(p2, self.c2.subject.ownedPort)
#       # it is assembly connector
#       self.assertEquals('assembly', connector.kind)
#       self.assertTrue(self.line.is_assembly)


#   def test_disconnection(self):
#       """Test assembly connector disconnection
#       """
#       self.connect(self.line, self.line.head, self.c1)

#       i1, = self._create_interfaces('A')
#       self._provide(self.c1.subject, i1)
#       self._require(self.c2.subject, i1)

#       connected = self.connect(self.line, self.line.tail, self.c2)
#       assert connected

#       self.disconnect(self.line, self.line.head)
#       
#       self.assertEquals(0, len(self.kindof(UML.Connector)))
#       self.assertEquals(0, len(self.kindof(UML.ConnectorEnd)))
#       self.assertEquals(0, len(self.kindof(UML.Port)))


# vim:sw=4:et:ai
