"""
"""

import gtk
import gaphas

class DiagramView(gaphas.View):
    """Displays a diagram (canvas) in a widget.

    See also: DiagramTab
    """

    TARGET_STRING = 0
    TARGET_ELEMENT_ID = 1
    DND_TARGETS = [
        ('gaphor/element-id', 0, TARGET_ELEMENT_ID)]

    __gtype_name__ = 'GaphorDiagramView'

    def __init__(self, diagram=None):
        super(DiagramView, self).__init__(diagram and diagram.canvas)
        self.diagram = diagram
        self.canvas = diagram.canvas

        # Drop
        self.drag_dest_set (gtk.DEST_DEFAULT_ALL, DiagramView.DND_TARGETS,
                            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK)

#    def set_tool(self, tool):
#        print 'setting tool', tool
#        resource('MainWindow').get_action_pool().executeself.tool.grab(tool)
#        pass

# vim: sw=4:et
