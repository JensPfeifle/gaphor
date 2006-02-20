'''
Dependency -- 
'''
# vim:sw=4:et

from __future__ import generators

import math
import gobject
import pango
import diacanvas

from gaphor import resource
from gaphor import UML
from gaphor.diagram.relationship import DiagramLine

STEREOTYPE_OPEN = '\xc2\xab' # '<<'
STEREOTYPE_CLOSE = '\xc2\xbb' # '>>'

class IncludeItem(DiagramLine):
    """A UseCase Include dependency.
    """

    __uml__ = UML.Include
    __relationship__ = 'addition', None, 'includingCase', 'include'

    FONT = 'sans 10'

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

        font = pango.FontDescription(self.FONT)
        self._stereotype = diacanvas.shape.Text()
        self._stereotype.set_font_description(font)
        self._stereotype.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._stereotype.set_markup(False)
        self._stereotype.set_text(STEREOTYPE_OPEN + 'include' + STEREOTYPE_CLOSE)
        self.set(head_fill_color=0, head_a=0.0, head_b=15.0, head_c=6.0, head_d=6.0)
        self.set(dash=(7.0, 5.0), has_head=1)

    def save(self, save_func):
        DiagramLine.save(self, save_func)

    def load(self, name, value):
        DiagramLine.load(self, name, value)

    def update_label(self, p1, p2):
        w, h = self._stereotype.to_pango_layout(True).get_pixel_size()

        x = p1[0] > p2[0] and w + 2 or -2
        x = (p1[0] + p2[0]) / 2.0 - x
        y = p1[1] <= p2[1] and h or 0
        y = (p1[1] + p2[1]) / 2.0 - y

        self._stereotype.set_pos((x, y))

        return x, y, w, h

    def on_update (self, affine):
        DiagramLine.on_update(self, affine)
        handles = self.handles
        middle = len(handles)/2
        b1 = self.update_label(handles[middle-1].get_pos_i(),
                                 handles[middle].get_pos_i())

        b2 = self.bounds
        self.set_bounds((min(b1[0], b2[0]), min(b1[1], b2[1]),
                         max(b1[2] + b1[0], b2[2]), max(b1[3] + b1[1], b2[3])))

    def on_shape_iter(self):
        for s in DiagramLine.on_shape_iter(self):
            yield s
        yield self._stereotype

    #
    # Gaphor Connection Protocol
    #

    def allow_connect_handle(self, handle, connecting_to):
        """See DiagramLine.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.UseCase)
        except AttributeError:
            return 0

    def confirm_connect_handle (self, handle):
        """See DiagramLine.confirm_connect_handle().

        In case of an Implementation, the head should be connected to an
        Interface and the tail to a BehavioredClassifier.

        TODO: Should Class also inherit from BehavioredClassifier?
        """
        #print 'confirm_connect_handle', handle, self.subject
        c1 = self.handles[0].connected_to

        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.relationship
            if not relation:
                relation = resource(UML.ElementFactory).create(UML.Include)
                relation.addition = s1
                relation.includingCase = s2
            self.subject = relation

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See DiagramLine.confirm_disconnect_handle().
        """
        #print 'confirm_disconnect_handle', handle
        self.set_subject(None)
