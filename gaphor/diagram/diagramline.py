"""
Basic functionality for canvas line based items on a diagram.
"""

import itertools

import gaphas
from gaphas.util import text_extents
from diagramitem import DiagramItem
#from gaphor.diagram import LineItemMeta

class LineItem(gaphas.Line, DiagramItem):
    """Base class for diagram lines.
    """

#    __metaclass__ = LineItemMeta

    def __init__(self, id = None):
        gaphas.Line.__init__(self)
        DiagramItem.__init__(self, id)
        self.fuzzyness = 2
        self._stereotype_pos = (0, 0)
        self._stereotype_width = 0
        self._stereotype_height = 0

    head = property(lambda self: self._handles[0])
    tail = property(lambda self: self._handles[-1])

    def update(self, context):
        super(LineItem, self).update(context)
        cr = context.cairo

        # update stereotype
        self.update_stereotype()

        sw, sh = text_extents(cr, self._stereotype)

        handles = self._handles
        middle = len(handles)/2
        p1 = handles[middle-1].pos
        p2 = handles[middle].pos

        x = p1[0] > p2[0] and sw + 2 or -2
        x = (p1[0] + p2[0]) / 2.0 - x
        y = p1[1] > p2[1] and -sh or 0
        y = (p1[1] + p2[1]) / 2.0 - y

        self._stereotype_pos = (x, y)
        self._stereotype_width = sw
        self._stereotype_height = sh

    def draw(self, context):
        super(LineItem, self).draw(context)
        cr = context.cairo
        if self._stereotype:
            cr.move_to(*self._stereotype_pos)
            cr.show_text(self._stereotype)


class DiagramLine(LineItem):
    """
    Gaphor lines. This line is serializable and has a popup
    menu.

    TODO: put serializability and popup in separate adapters.
    """

    popup_menu = LineItem.popup_menu + (
        'separator', 
        'AddSegment',
        'DeleteSegment',
        'Orthogonal',
        'OrthogonalAlignment',
        'separator',
        'EditDelete'
    )

    def do_set_property (self, pspec, value):
        pass

    def do_get_property(self, pspec):
        pass

    def save (self, save_func):
        LineItem.save(self, save_func)
        for prop in ('affine', 'color', 'orthogonal', 'horizontal'):
            save_func(prop, self.get_property(prop))
        points = [ ]
        for h in self.handles:
            pos = h.get_pos_i ()
            points.append (pos)
        save_func('points', points)
        c = self.handles[0].connected_to
        if c:
            save_func('head-connection', c, reference=True)
        c = self.handles[-1].connected_to
        if c:
            save_func('tail-connection', c, reference=True)

    def load (self, name, value):
        if name == 'points':
            points = eval(value)
            self.set_property('head_pos', points[0])
            self.set_property('tail_pos', points[1])
            for p in points[2:]:
                self.set_property ('add_point', p)
        elif name in ('head_connection', 'head-connection'):
            self._load_head_connection = value
        elif name in ('tail_connection', 'tail-connection'):
            self._load_tail_connection = value
        else:
            LineItem.load(self, name, value)

    def postload(self):
        if hasattr(self, '_load_head_connection'):
            self._load_head_connection.connect_handle(self.handles[0])
            del self._load_head_connection
        if hasattr(self, '_load_tail_connection'):
            self._load_tail_connection.connect_handle(self.handles[-1])
            del self._load_tail_connection
        LineItem.postload(self)



class FreeLine(LineItem):
    """
    TODO: get rid of this one.

    A line with disabled last handle. This allows to create diagram items,
    which have one or more additional lines.

    Last handle is usually attached to a point of diagram item. This point
    is called main point.
    """
    def __init__(self, id = None, mpt = None):
        LineItem.__init__(self, id)

        # expose first handle
        self._handle = self.handles[0]

        # disable last handle, it should be in main point
        h = self.handles[-1]
        h.props.movable = False
        h.props.connectable = False
        h.props.visible = False

        self._main_point = mpt

        if self._main_point is None:
            self._main_point = 0, 0


    def on_update(self, affine):
        self.handles[-1].set_pos_i(*self._main_point)
        self._handle.set_pos_i(*self._handle.get_pos_i()) # really strange, but we have to do this

        LineItem.on_update(self, affine)

# vim:sw=4:et
