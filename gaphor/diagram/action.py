'''
ActionItem diagram item
'''

import math
import gobject
import pango
import diacanvas
from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.align import ITEM_ALIGN_C

def make_arc(radius, edges, q=1):
    """Create a tupple of edges points, which represent a 90 degrees
    arc in the first quadrant
    """
    points = []
    sin = math.sin
    cos = math.cos
    pi2 = (math.pi/2)
    for i in xrange(edges + 1):
        n = (pi2 * i) / edges + pi2*q
        points.append((cos(n) * radius, sin(n) * radius))
    return points

def alter_arc(arc, offsetx=0, offsety=0):
    return [(x+offsetx, y+offsety) for x, y in arc]

class ActionItem(NamedItem):
    __uml__   = UML.Action
    n_align = ITEM_ALIGN_C

    RADIUS = 15
    arc_1 = make_arc(radius=RADIUS, edges=10, q=0)
    arc_2 = make_arc(radius=RADIUS, edges=10, q=1)
    arc_3 = make_arc(radius=RADIUS, edges=10, q=2)
    arc_4 = make_arc(radius=RADIUS, edges=10, q=3)

    def draw_border(self):
        r = self.RADIUS
        h = self.height - r
        w = self.width - r
        line = alter_arc(self.arc_1, offsetx=w, offsety=h) + \
               alter_arc(self.arc_2, offsetx=r, offsety=h) + \
               alter_arc(self.arc_3, offsetx=r, offsety=r) + \
               alter_arc(self.arc_4, offsetx=w, offsety=r)
        self._border.line(line)
        self._border.set_cyclic(True)


# vim:sw=4:et
