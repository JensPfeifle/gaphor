"""ClassifierItem diagram item
"""

import itertools

from gaphas.util import text_extents, text_center, text_set_font
from gaphor import UML
from gaphor.i18n import _

from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.feature import FeatureItem

from gaphas.util import text_center
import font

class Compartment(list):
    """Specify a compartment in a class item.
    A compartment has a line on top and a list of FeatureItems.
    """

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.visible = True
        self.width = 0
        self.height = 0

    def save(self, save_func):
        #log.debug('Compartment.save: %s' % self)
        for item in self:
            save_func(None, item)

    def has_item(self, item):
        """Check if the compartment already contains an item with the
        same subject as item.
        """
        s = item.subject
        local_elements = [f.subject for f in self]
        return s and s in local_elements

    def get_size(self):
        """Get width, height of the compartment. pre_update should have
        been called so widthand height have been calculated.
        """
        return self.width, self.height

    def pre_update(self, context):
        """Pre update, determine width and height of the compartment.
        """
        self.width = self.height = 0
        cr = context.cairo
        for item in self:
            item.pre_update(context)
        if self:
            sizes = [f.get_size(True) for f in self]
            self.width = max(map(lambda p: p[0], sizes))
            self.height = sum(map(lambda p: p[1], sizes))
        margin = self.owner.style.compartment_margin
        self.width += margin[1] + margin[3]
        self.height += margin[0] + margin[2]

    def update(self, context):
        for item in self:
            item.update(context)


    def draw(self, context):
        cr = context.cairo
        margin = self.owner.style.compartment_margin
        cr.translate(margin[1], margin[0])
        for item in self:
            cr.save()
            try:
                cr.translate(0, item.height)
                item.draw(context)
            finally:
                cr.restore()


class ClassifierItem(NamedItem):
    """This item visualizes a Class instance.

    A ClassifierItem is a superclass for (all) Classifier like objects,
    such as Class, Interface, Component and Actor.

    ClassifierItem controls the stereotype, namespace and owning package.

    A classifier has three drawing style (ClassifierItem.drawing_style):
     - The comparttment view, as often used by Classes
     - A compartment view, but with a little stereotype icon in the right corner
     - One big icon, as used by Actors and sometimes interfaces.

    To support this behavior a few helper methods are defined which can be
    called/overridden:
     - update_compartment_icon (box-style with small icon (see ComponentItem))
     - update_icon (does nothing by default, an impl. should be provided by
                    subclasses (see ActorItem))
    """

    # Do not use preset drawing style
    DRAW_NONE = 0
    # Draw the famous box style
    DRAW_COMPARTMENT = 1
    # Draw compartment with little icon in upper right corner
    DRAW_COMPARTMENT_ICON = 2
    # Draw as icon
    DRAW_ICON = 3

    __style__ = {
        'icon-size': (20, 20),
        'compartment-margin': (5, 5, 5, 5), # (top, right, bottom, left)
        }
    # Default size for small icons
    ICON_WIDTH    = 15
    ICON_HEIGHT   = 25
    ICON_MARGIN_X = 10
    ICON_MARGIN_Y = 10
    NAME_COMPARTMENT_HEIGHT = 35

    def __init__(self, id = None, width = 100, height = 50):
        NamedItem.__init__(self, id, width, height)
        self._compartments = []
        self._from = None # (from ...) text
        self._drawing_style = ClassifierItem.DRAW_NONE

    def save(self, save_func):
        # Store the show- properties *before* the width/height properties,
        # otherwise the classes will unintentionally grow due to "visible"
        # attributes or operations.
        self.save_property(save_func, 'drawing-style')
        NamedItem.save(self, save_func)

    def postload(self):
        NamedItem.postload(self)
        self.on_subject_notify__isAbstract(self.subject)

    def set_drawing_style(self, style):
        """Set the drawing style for this classifier: DRAW_COMPARTMENT,
        DRAW_COMPARTMENT_ICON or DRAW_ICON.
        """
        if style != self._drawing_style:
            #self.preserve_property('drawing-style')
            self._drawing_style = style
            self.request_update()

        if self._drawing_style == self.DRAW_COMPARTMENT:
            self.draw       = self.draw_compartment
            self.pre_update = self.pre_update_compartment
            self.update     = self.update_compartment

        elif self._drawing_style == self.DRAW_COMPARTMENT_ICON:
            self.draw       = self.draw_compartment_icon
            self.pre_update = self.pre_update_compartment_icon
            self.update     = self.update_compartment_icon

        elif self._drawing_style == self.DRAW_ICON:
            self.draw       = self.draw_icon
            self.pre_update = self.pre_update_icon
            self.update     = self.update_icon


    drawing_style = property(lambda self: self._drawing_style, set_drawing_style)


    def create_compartment(self, name):
        """Create a new compartment. Compartments contain data such as
        attributes and operations.

        It is common to create compartments during the construction of the
        diagram item. Their visibility can be toggled by Compartment.visible.
        """
        c = Compartment(name, self)
        self._compartments.append(c)
        return c

    compartments = property(lambda s: s._compartments)

    def sync_uml_elements(self, elements, compartment, creator=None):
        """This method synchronized a list of elements with the items
        in a compartment. A creator-function should be passed which is used
        for creating new compartment items.

        @elements: the list of attributes or operations in the model
        @compartment: our local representation
        @creator: factory method for creating new attr. or oper.'s
        """
        # extract the UML elements from the compartment
        local_elements = [f.subject for f in compartment]

        # map local element with compartment element
        mapping = dict(zip(local_elements, compartment))

        to_add = [el for el in elements if el not in local_elements]

        #print 'sync_elems:', elements, local_elements, to_add

        # Remove no longer present elements:
        for el in [el for el in local_elements if el not in elements]:
            self.remove(mapping[el])

        # sync local elements with elements
        del compartment[:]

        for el in elements:
            if el in to_add:
                #print 'sync_elems: creating', el
                creator(el)
            else:
                compartment.append(mapping[el])

        #log.debug('elements order in model: %s' % [f.name for f in elements])
        #log.debug('elements order in diagram: %s' % [f.subject.name for f in compartment])
        assert tuple([f.subject for f in compartment]) == tuple(elements)

        self.request_update()


    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        NamedItem.on_subject_notify(self, pspec,
                                    ('namespace', 'namespace.name',
                                     'isAbstract') + notifiers)
        # Create already existing attributes and operations:
        if self.subject:
            self.on_subject_notify__namespace(self.subject)
            self.on_subject_notify__isAbstract(self.subject)
        self.request_update()

    def on_subject_notify__namespace(self, subject, pspec=None):
        """Add a line '(from ...)' to the class item if subject's namespace
        is not the same as the namespace of this diagram.
        """
        if self.subject and self.subject.namespace and self.canvas and \
           self.canvas.diagram.namespace is not self.subject.namespace:
            self._from = _('(from %s)') % self.subject.namespace.name
        else:
           self._from = None

        self.request_update()

    def on_subject_notify__namespace_name(self, subject, pspec=None):
        """Change the '(from ...)' line if the namespace's name changes.
        """
        self.on_subject_notify__namespace(subject, pspec)

    def on_subject_notify__isAbstract(self, subject, pspec=None):
        self.request_update()

    def pre_update_compartment(self, context):
        for comp in self._compartments:
            comp.pre_update(context)

        cr = context.cairo
        s_w = s_h = 0
        if self.stereotype:
            s_w, s_h = text_extents(cr, self.stereotype)
        n_w, n_h = text_extents(cr, self.subject.name)
        f_w, f_h = 0, 0
        if self.subject.namespace:
            f_w, f_h = text_extents(cr, self._from, font=font.FONT_SMALL)

        sizes = [comp.get_size() for comp in self._compartments]

        self.min_width = max(s_w, n_w, f_w)
        self.min_height = self.NAME_COMPARTMENT_HEIGHT

        if sizes:
            w = max(map(lambda p: p[0], sizes))

            h = sum(map(lambda p: p[1], sizes))
            self.min_width = max(self.min_width, w)
            self.min_height += h
        super(ClassifierItem, self).pre_update(context)

    def pre_update_compartment_icon(self, context):
        self.pre_update_compartment(context)

    def pre_update_icon(self, context):
        super(ClassifierItem, self).pre_update(context)

    def update_compartment(self, context):
        """Update state for box-style presentation.
        """
        pass

    def update_compartment_icon(self, context):
        """Update state for box-style w/ small icon.
        """
        pass

    def update_icon(self, context):
        """
        """
        pass

    def get_icon_pos(self):
        """Get icon position.
        """
        return self.width - self.ICON_MARGIN_X - self.ICON_WIDTH, \
            self.ICON_MARGIN_Y


    def draw_compartment(self, context):
        if not self.subject: return
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()
        y = 0

        if self._drawing_style == self.DRAW_COMPARTMENT_ICON:
            width = self.width - self.ICON_WIDTH
        else:
            width = self.width

        # draw stereotype
        y += 10
        if self.stereotype:
            text_set_font(cr, font.FONT)
            text_center(cr, width / 2, y, self.stereotype)

        # draw name
        y += 10
        text_set_font(cr, font.FONT_NAME)
        text_center(cr, width / 2, y, self.subject.name)

        y += 10
        # draw 'from ... '
        if self._from:
            text_set_font(cr, font.FONT_SMALL)
            text_center(cr, width / 2, y, self._from)

        y += 5
        cr.translate(0, y)

        # draw compartments
        for comp in self._compartments:
            cr.save()
            cr.move_to(0, 0)
            cr.line_to(self.width, 0)
            cr.stroke()
            try:
                comp.draw(context)
            finally:
                cr.restore()
            cr.translate(0, comp.height)


# vim:sw=4:et
