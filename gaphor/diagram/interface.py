"""
Interface item.
"""

import itertools
from math import pi
from gaphas.item import NW, SE
from gaphor import UML
from gaphor.diagram.dependency import DependencyItem
from gaphor.diagram.implementation import ImplementationItem
from gaphor.diagram.klass import ClassItem
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.rotatable import SimpleRotation
from gaphor.diagram.style import ALIGN_TOP, ALIGN_BOTTOM, ALIGN_CENTER

class InterfaceItem(ClassItem, SimpleRotation):
    """
    This item represents an interface drawn as a dot. The class-like
    representation is provided by ClassItem. These representations can be
    switched by using the Fold and Unfold actions.

    TODO (see also DependencyItem): when a Usage dependency is connected to
          the interface, draw a line, but not all the way to the connecting
          handle. Stop drawing the line 'x' points earlier. 
    """

    __uml__        = UML.Interface
    __stereotype__ = {'interface': lambda self: self.drawing_style != self.DRAW_ICON}
    __style__ = {
        'icon-size': (20, 20),
        'icon-size-provided': (20, 20),
        'icon-size-required': (28, 28),
        'name-outside': False,
        }

    UNFOLDED_STYLE = {
        'name-align': (ALIGN_CENTER, ALIGN_TOP),
        'name-outside': False,
        }

    FOLDED_STYLE = {
        'name-align': (ALIGN_CENTER, ALIGN_BOTTOM),
        'name-outside': True,
        }

    RADIUS_PROVIDED = 10
    RADIUS_REQUIRED = 14

    def __init__(self, id=None):
        ClassItem.__init__(self, id)
        SimpleRotation.__init__(self)
        self._draw_required = False
        self._draw_provided = False

    def set_drawing_style(self, style):
        """
        In addition to setting the drawing style, the handles are
        make non-movable if the icon (folded) style is used.
        """
        ClassItem.set_drawing_style(self, style)
        # TODO: adjust offsets so the center point is the same
        if self._drawing_style == self.DRAW_ICON:
            self.style.update(self.FOLDED_STYLE)
            self.request_update()
        else:
            self.style.update(self.UNFOLDED_STYLE)
            self.request_update()

    drawing_style = property(lambda self: self._drawing_style, set_drawing_style)

    def get_popup_menu(self):
        if self.drawing_style == self.DRAW_ICON:
            return NamedItem.popup_menu + ('separator', 'Rotate', 'Unfold',)
        else:
            return ClassItem.get_popup_menu(self)

    def is_folded(self):
        """
        Returns True if the interface is drawn as a circle/dot.
        Unfolded means it's drawn like a classifier.
        """
        return self.drawing_style == self.DRAW_ICON

    def pre_update_icon(self, context):
        """
        Figure out if this interface represents a required, provided,
        assembled (wired) or dotted (minimal) look.
        """
        for h in self._handles: h.movable = False
        self.style.name_outside = True

        h_nw = self._handles[NW]
        cx, cy = h_nw.x + self.width/2, h_nw.y + self.height/2
        self._draw_required = self._draw_provided = False
        for item, handle in self.canvas.get_connected_items(self):
            if gives_required(handle):
                self._draw_required = True
            elif gives_provided(handle):
                self._draw_provided = True
        radius = self.RADIUS_PROVIDED
        self.style.icon_size = self.style.icon_size_provided
        if self._draw_required:
            radius = self.RADIUS_REQUIRED
            self.style.icon_size = self.style.icon_size_required
        self.min_width, self.min_height = self.style.icon_size
        self.width, self.height = self.style.icon_size

        #h_nw.x, h_nw.y = cx - radius, cy - radius
        h_se = self._handles[SE]
        #h_se.x, h_se.y = cx + radius, cy + radius
        super(InterfaceItem, self).pre_update(context)

    def draw_icon(self, context):
        cr = context.cairo
        h_nw = self._handles[NW]
        cx, cy = h_nw.x + self.width/2, h_nw.y + self.height/2
        if self._draw_required:
            cr.move_to(cx, cy + self.RADIUS_REQUIRED)
            cr.arc_negative(cx, cy, self.RADIUS_REQUIRED, pi/2, pi*1.5)
            cr.stroke()
        if self._draw_provided or not self._draw_required:
            cr.move_to(cx + self.RADIUS_PROVIDED, cy)
            cr.arc(cx, cy, self.RADIUS_PROVIDED, 0, pi*2)
            cr.stroke()
        super(InterfaceItem, self).draw(context)

    def rotate(self, step = 1):
        """
        Update connected handle positions after rotation.
        """
        SimpleRotation.rotate(self, step)
        self.update_handle_pos()



def gives_provided(handle):
    """
    Check if an item connected to an interface changes semantics of this
    interface to be provided.

    handle - handle of an item
    """
    return isinstance(handle.owner, ImplementationItem)


def gives_required(handle):
    """Check if an item connected to an interface changes semantics of this
    interface to be required.

    handle - handle of an item
    TODO: check subject.clientDependency and subject.supplierDependency
    """
    item = handle.owner
    # check for dependency item, interfaces is required if
    # - connecting handle is head one
    # - is in auto dependency
    # - if is not in auto dependency then its UML type is Usage
    return isinstance(item, DependencyItem) and item.handles[0] == handle \
        and (not item.auto_dependency and item.dependency_type is UML.Usage
            or item.auto_dependency)


# vim:sw=4:et
