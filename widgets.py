from PyQt4 import QtGui, QtCore
from collections import deque
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Label(QtGui.QLabel):
	""" A drag & droppable label  """
	def __init__(self, title, parent):
		super(Label, self).__init__(title, parent)
		self.standard_color = 'rgb(154, 205, 50)'
		self.setStyleSheet("background-color: %s; border: 1px solid;" % self.standard_color)
		self.setAlignment(QtCore.Qt.AlignCenter)
		self.setFixedWidth(100)
		self.rank = int(title)

	def mouseMoveEvent(self, e):
		mimeData = QtCore.QMimeData()
		drag = QtGui.QDrag(self)
		drag.setMimeData(mimeData)
		drag.setHotSpot(self.rect().topLeft())
		dropAction = drag.start(QtCore.Qt.MoveAction)
	

class CoefficientWidget(QtGui.QFrame):
	""" A QFrame for displaying a coefficient and enabling/disabling it """
	def __init__(self, parent, max_deque_len):
		super(CoefficientWidget, self).__init__(parent=parent)
		self.max_deque_len = max_deque_len
		self.values = deque([1], self.max_deque_len)
		self.cb = QtGui.QCheckBox('', self)
		self.cb.stateChanged.connect(parent.toggle_coefficient)
		self.label = QtGui.QLabel(' '*50, self)
		self.label.move(20, 0)
	
	def reset_values(self):
		self.values = deque([1], self.max_deque_len)


class MplCanvas(FigureCanvas):
	""" A canvas for a matplotlib figure """
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		self.fig = Figure(figsize=(width, height), dpi=dpi)
		#self.fig.set_facecolor('None')
		self.ax = self.fig.add_subplot(111)
		self.ax.set_alpha(0.1)
		self.ax.hold(False)

		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding,
										 QtGui.QSizePolicy.Expanding)
		

