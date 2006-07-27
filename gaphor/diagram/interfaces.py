"""
This module describes the interfaces specific to the gaphor.diagram module.
These interfaces are:

 - IConnectable
   Use to define adapters for connecting 
 - IEditor
   Text editor interface

"""


from zope import interface

# Should be removed

class IDiagramItem(interface.Interface):
    """A diagram element"""
    subject = interface.Attribute("The model element connect to this view")    

class ICommentItem(IDiagramItem):
    """A view on a Comment item."""

class INamedItem(IDiagramItem):
    """A view on an attribute (part of a class, interface etc.)."""
    

class IClassItem(INamedItem):
    """The graphical view on a class."""
    

class IAttributeItem(INamedItem):
    """A view on an attribute (part of a class, interface etc.)."""

# until here..

class IEditor(interface.Interface):
    """Provide an interface for editing text. with the TextEditTool.
    """

    def is_editable(self, x, y):
        """Is this item editable in it's current state.
        x, y represent the cursors (x, y) position.
        """

    def get_text(self):
        """Get the text to be updated
        """

    def get_bounds(self):
        """Get the bounding box of the (current) text. The edit tool is not
        required to do anything with this information but it might help for
        some nicer displaying of the text widget.

        Returns: a gaphas.geometry.Rectangle
        """

    def update_text(self, text):
        """Update with the new text.
        """

    def key_pressed(self, pos, key):
        """Called every time a key is pressed. Allows for 'Enter' as escape
        character in single line editing.
        """

class IConnect(interface.Interface):
    """This interface is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Line, Element) an
    adapter could be written.
    """

    def connect(self, handle, x, y):
        """Connect a line's handle to element.
        x and y are translated to the element the handle is connecting to.

        Note that at the moment of the connect, handle.connected_to may point
        to some other item. The implementor should do the disconnect of
        the other element themselves.
        """

    def disconnect(self, handle):
        """Disconnect a line's handle from an element.
        """

    def full_disconnect(self, handle):
        """Disconnect a handle.connected_to from an element. This requires
        that the relationship is also removed at model level.
        """

    def glue(self, handle, x, y):
        """Determine if a handle can glue to a specific element.

        Returns a tuple (x, y) if the line and element may connect, None
        otherwise.
        """

# vim: sw=4:et:ai
