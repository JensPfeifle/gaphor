"""
Style classes and constants.
"""

# padding
PADDING_TOP, PADDING_RIGHT, PADDING_BOTTOM, PADDING_LEFT = range(4)

# horizontal align
ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT = range(3)

# vertical align
ALIGN_TOP, ALIGN_MIDDLE, ALIGN_BOTTOM = range(3)


class Style(object):
    """
    Item style information. Style information is provided through object's
    attributes, i.e.::

        class InitialNodeItem
            __style__ = {
                'name-align': ('center', 'top'),
            }

    is translated to::

        >>> print style.name_align
        ('center', 'top')
    """
    def add(self, name, value):
        """
        Add style variable.

        Variable name can contain hyphens, which is converted to
        underscode, i.e. 'name-align' -> 'name_align'.

        @param name:  style variable name
        @param value: style variable value
        """
        name = name.replace('-', '_')
        setattr(self, name, value)


    def items(self):
        """
        Return iterator of (name, value) style information items.
        """
        return self.__dict__.iteritems()


def get_min_size(width, height, padding):
    """
    Get minimum size of an object using padding information.

    @param width: object width
    @param height: object height
    @param padding: padding information as a tuple
        (top, right, bottom, left)
    """
    return width + padding[PADDING_LEFT] + padding[PADDING_RIGHT], \
        height + padding[PADDING_TOP] + padding[PADDING_BOTTOM]


def get_text_point(extents, width, height, align, padding, outside):
    """
    Calculate position of the text relative to containing box defined by
    tuple (0, 0, width, height).  Text is aligned using align and padding
    information. It can be also placed outside the box if @C{outside}
    parameter is set to @C{True}.

    @param extents: text extents like width, height, etc.
    @param width:   width of the containing box
    @param height:  height of the containing box
    @param align:   text align information (center, top, etc.)
    @param padding: text padding
    @param outside: should text be put outside containing box
    """
    #x_bear, y_bear, w, h, x_adv, y_adv = extents
    w, h = extents

    halign, valign = align

    if outside:
        if halign == ALIGN_LEFT:
            x = -w - padding[PADDING_LEFT]
        elif halign == ALIGN_CENTER:
            x = (width - w) / 2
        elif halign == ALIGN_RIGHT:
            x = width + padding[PADDING_RIGHT]
        else:
            assert False

        if valign == ALIGN_TOP:
            y = -padding[PADDING_TOP]
        elif valign == ALIGN_MIDDLE:
            y = (height + h) / 2
        elif valign == ALIGN_BOTTOM:
            y = height + h + padding[PADDING_BOTTOM]
        else:
            assert False

    else:
        if halign == ALIGN_LEFT:
            x = padding[PADDING_LEFT]
        elif halign == ALIGN_CENTER:
            x = (width - w) / 2
        elif halign == ALIGN_RIGHT:
            x = width - w - padding[PADDING_RIGHT]
        else:
            assert False

        if valign == ALIGN_TOP:
            y = h + padding[PADDING_TOP]
        elif valign == ALIGN_MIDDLE:
            y = (height + h) / 2
        elif valign == ALIGN_BOTTOM:
            y = height - padding[PADDING_BOTTOM]
        else:
            assert False
    return x, y


# vim:sw=4:et
