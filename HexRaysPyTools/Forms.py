import idaapi
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore


class MyChoose(idaapi.Choose2):
    def __init__(self, items, title, cols, icon=-1):
        idaapi.Choose2.__init__(self, title, cols, flags=idaapi.Choose2.CH_MODAL, icon=icon)
        self.items = items

    def OnClose(self):
        pass

    def OnGetLine(self, n):
        return self.items[n]

    def OnGetSize(self):
        return len(self.items)


class StructureBuilder(idaapi.PluginForm):
    def __init__(self, structure_model):
        super(StructureBuilder, self).__init__()
        self.structure_model = structure_model
        self.parent = None

    def OnCreate(self, form):
        self.parent = self.FormToPySideWidget(form)
        self.init_ui()

    def init_ui(self):
        self.parent.setStyleSheet(
            "QTableView {background-color: transparent;}"
            "QHeaderView::section {background-color: transparent; border: 1px solid;}"
            "QPushButton {width: 50px; height: 20px;}"
            # "QPushButton::pressed {background-color: #ccccff}"
        )
        self.parent.resize(400, 600)
        self.parent.setWindowTitle('Structure Builder')

        btn_finalize = QtGui.QPushButton("&Finalize")
        btn_disable = QtGui.QPushButton("&Disable")
        btn_enable = QtGui.QPushButton("&Enable")
        btn_origin = QtGui.QPushButton("&Origin")
        btn_array = QtGui.QPushButton("&Array")
        btn_pack = QtGui.QPushButton("&Pack")
        btn_remove = QtGui.QPushButton("&Remove")
        btn_clear = QtGui.QPushButton("Clear")  # Clear button doesn't have shortcut because it can fuck up all work
        btn_recognize = QtGui.QPushButton("Recognize Shape")
        btn_scan_list = QtGui.QPushButton("Scanned Variables")
        btn_recognize.setStyleSheet("QPushButton {width: 100px; height: 20px;}")
        btn_scan_list.setStyleSheet("QPushButton {width: 100px; height: 20px;}")

        btn_finalize.setShortcut("f")
        btn_disable.setShortcut("d")
        btn_enable.setShortcut("e")
        btn_origin.setShortcut("o")
        btn_array.setShortcut("a")
        btn_pack.setShortcut("p")
        btn_remove.setShortcut("r")

        struct_view = QtGui.QTableView()
        struct_view.setModel(self.structure_model)

        struct_view.verticalHeader().setVisible(False)
        struct_view.horizontalHeader().setStretchLastSection(True)
        struct_view.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        grid_box = QtGui.QGridLayout()
        grid_box.setSpacing(0)
        grid_box.addWidget(btn_finalize, 0, 0)
        grid_box.addWidget(btn_disable, 0, 1)
        grid_box.addWidget(btn_enable, 0, 2)
        grid_box.addWidget(btn_origin, 0, 3)
        grid_box.addItem(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding), 0, 4)
        grid_box.addWidget(btn_scan_list, 0, 5, 1, 6)
        grid_box.addWidget(btn_array, 1, 0)
        grid_box.addWidget(btn_pack, 1, 1)
        grid_box.addWidget(btn_remove, 1, 2)
        grid_box.addWidget(btn_clear, 1, 3)
        grid_box.addItem(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding), 1, 4)
        grid_box.addWidget(btn_recognize, 1, 5, 1, 6)

        vertical_box = QtGui.QVBoxLayout()
        vertical_box.addWidget(struct_view)
        vertical_box.addLayout(grid_box)
        self.parent.setLayout(vertical_box)

        btn_finalize.clicked.connect(lambda: self.structure_model.finalize())
        btn_disable.clicked.connect(lambda: self.structure_model.disable_rows(struct_view.selectedIndexes()))
        btn_enable.clicked.connect(lambda: self.structure_model.enable_rows(struct_view.selectedIndexes()))
        btn_origin.clicked.connect(lambda: self.structure_model.set_origin(struct_view.selectedIndexes()))
        btn_array.clicked.connect(lambda: self.structure_model.make_array(struct_view.selectedIndexes()))
        btn_pack.clicked.connect(lambda: self.structure_model.pack_substructure(struct_view.selectedIndexes()))
        btn_remove.clicked.connect(lambda: self.structure_model.remove_items(struct_view.selectedIndexes()))
        btn_clear.clicked.connect(lambda: self.structure_model.clear())
        btn_recognize.clicked.connect(lambda: self.structure_model.recognize_shape(struct_view.selectedIndexes()))
        struct_view.activated[QtCore.QModelIndex].connect(self.structure_model.show_virtual_methods)
        self.structure_model.dataChanged.connect(struct_view.clearSelection)

    def OnClose(self, form):
        pass

    def Show(self, caption=None, options=0):
        return idaapi.PluginForm.Show(self, caption, options=0)


class StructureGraphViewer(idaapi.GraphViewer):
    def __init__(self, title, graph):
        idaapi.GraphViewer.__init__(self, title)
        self.graph = graph

    def OnRefresh(self):
        self.Clear()
        nodes_id = {}
        for node in self.graph.get_nodes():
            nodes_id[node] = self.AddNode(node)
        for first, second in self.graph.get_edges():
            self.AddEdge(nodes_id[first], nodes_id[second])
        return True

    def OnGetText(self, node_id):
        return self.graph.local_types[self[node_id]].name_and_color

    def OnHint(self, node_id):
        try:
            ordinal = self[node_id]
            return self.graph.local_types[ordinal].hint
        except KeyError:
            return

    def OnDblClick(self, node_id):
        self.graph.change_selected([self[node_id]])
        self.Refresh()
