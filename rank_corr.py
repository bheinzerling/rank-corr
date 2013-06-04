import sys
import time
from PyQt4 import QtGui, QtCore
import numpy as np
from widgets import Label, CoefficientWidget, MplCanvas
from rank_correlation_measures import tau, rho, AP

class MainWindow(QtGui.QWidget):

	def __init__(self):
		super(MainWindow, self).__init__()
		self.initUI()
	
	def initUI(self):
		self.row_height =35 
		self.grid_y = 50
		self.max_deque_len = 46 
		self.coefficients = ['tau', 'rho', 'AP'] 
		self.coefficient_names = ["Kendall's tau", "Spearman's rho", "Average Precision"]
		self.coefficient_colors = ['blue', 'red', 'aquamarine']

		self.init_ranked_list()

		# put labels displaying coefficient data under the ranked list
		y = lambda i: self.grid_y + len(self.labels) * self.row_height + i * 25
		self.label_conc = QtGui.QLabel('', self)
		self.label_disc = QtGui.QLabel('', self)
		self.label_conc.move(35, y(0))
		self.label_disc.move(35, y(1))
		self.label_conc.setFixedWidth(100)
		self.label_disc.setFixedWidth(100)
		for i, coefficient in enumerate(self.coefficients):
			setattr(self, coefficient, CoefficientWidget(self, self.max_deque_len))
			c = getattr(self, coefficient)
			c.move(15, y(i+2))

		# MplCanvas in a frame with vbox layout for automatic resizing
		self.mpl_canvas = MplCanvas(self)
		self.canvas_frame = QtGui.QFrame(parent=self)
		self.resize_frame()
		self.vbox = QtGui.QVBoxLayout()
		self.vbox.addWidget(self.mpl_canvas)
		self.canvas_frame.setLayout(self.vbox)
		self.canvas_frame.show()

		# reset and inverse buttons
		self.reset = QtGui.QPushButton('Reset', self)
		self.reset.clicked.connect(self.reset_labels)
		self.reset.move(8, 10)
		self.inverse = QtGui.QPushButton('Invert', self)
		self.inverse.clicked.connect(self.invert_labels)
		self.inverse.move(self.reset.rect().width() + 5,  10)
		
		# checkbox to toggle display of plot and coefficients
		self.cb_draw = QtGui.QCheckBox('Plot', self)
		self.cb_draw.move(self.inverse.pos().x() + self.inverse.rect().width() + 5, 10)
		self.cb_draw.stateChanged.connect(self.toggle_draw)
		self.toggle_draw()

		self.update_coefficients(True)

		self.setAcceptDrops(True)
		self.setWindowTitle('Rank Correlation Demo')
		self.setGeometry(100, 100, 1000, 600)
		self.show()

	def init_ranked_list(self):
		# create labels and display them in a 1-column grid
		self.labels = [Label(str(i), self) for i in range(10)]
		for i in range(len(self.labels)):
			y = self.grid_y + i * self.row_height
			rank_label = QtGui.QLabel('%i' % i, self)
			rank_label.move(20, y)
		self.createGrid()

	def toggle_coefficient(self):
		self.draw_plot()

	def toggle_draw(self):
		# hide or show canvas and coefficients
		for coefficient in self.coefficients:
			c = getattr(self, coefficient)
			c.reset_values()
			c.cb.setChecked(False)
		toggle_visibility = lambda w: w.show() if self.cb_draw.isChecked() else w.hide()
		for w in ['canvas_frame', 'label_conc', 'label_disc'] + self.coefficients:
			toggle_visibility(getattr(self, w))
		self.mpl_canvas.ax.cla()
		self.draw_plot()

	def reset_labels(self):
		# restore original ordering
		self.labels.sort(key=lambda x: x.rank)
		self.createGrid()
		self.update_coefficients(True)
	
	def invert_labels(self):
		# invert current ordering
		#self.labels.sort(key=lambda x: x.rank, inverse=True)
		for i in range(len(self.labels)):
			for j in range(i+1, len(self.labels)):
				self.labels[i], self.labels[j] = self.labels[j], self.labels[i]
				self.createGrid()
				if self.cb_draw.isChecked():
					self.update_coefficients(True)
					self.draw_plot()
				time.sleep(0.1)
				self.repaint()

	def update_coefficients(self, drop=False):
		values1 = list(range(len(self.labels)))
		values2 = [l.rank for l in self.labels]
		concordant_pairs, discordant_pairs = tau(values1, values2, True)
		self.label_conc.setText('Conc. pairs: %i' % concordant_pairs)
		self.label_disc.setText('Disc. pairs: %i' % discordant_pairs)
		for coefficient in self.coefficients:
			c = getattr(self, coefficient)
			current_value = globals()[coefficient](values1, values2)
			c.label.setText('%s: %.4f  ' % (coefficient, current_value))
			if drop:
				c.values.append(current_value)
		if drop:
			self.draw_plot()

	def resize_frame(self):
		self.canvas_frame.setGeometry(200, 0, self.rect().width()-200, self.rect().height()-0)

	def createGrid(self):
		# display list in a 1-column grid and color labels according to distance from their ideal position
		for i, label in enumerate(self.labels):
			label.move(50, self.grid_y + i * self.row_height)
			if i == label.rank:
				color = label.standard_color
			else:
				red_value = abs(label.rank - i) * 255 / len(self.labels)
				color = 'rgb(255, %s, 0)' % str(255 - red_value)
			label.setStyleSheet("background-color: %s; border: 1px solid;" % color)

	def reorderLabels(self, drop=False):
		self.labels.sort(key=lambda x: x.pos().y())
		self.update_coefficients(drop)
		self.createGrid()

	def draw_plot(self):
		x_vals = range(self.max_deque_len)
		y_vals = None
		# to decide where to place the legend, keep track of the last few y values
		last_y_vals_sum = 0
		test_x = int(self.max_deque_len * 0.6)
		self.mpl_canvas.ax.hold(True)
		self.mpl_canvas.ax.cla()
		for i, coefficient in enumerate(self.coefficients):
			c = getattr(self, coefficient)
			color = self.coefficient_colors[i]
			label = self.coefficient_names[i]
			if c.cb.isChecked():
				y_vals = [c.values[i] if i < len(c.values) else None for i in x_vals]
				self.mpl_canvas.ax.plot(x_vals, y_vals, 'o-', color=color, label=label)
				last_y_vals_sum += sum([v for v in y_vals[test_x:] if v != None])
		self.mpl_canvas.ax.hold(False)
		if y_vals:
			# use last few y values to decide whether to place the legend in the upper or lower part
			loc = 'upper right' if last_y_vals_sum < 0 else 'lower right'
			self.mpl_canvas.ax.legend(loc=loc)
		self.mpl_canvas.ax.set_ylim([-1., 1.])
		self.mpl_canvas.ax.set_xlim([-0.5, self.max_deque_len + 2])
		self.mpl_canvas.ax.spines['bottom'].set_position('center')
		self.mpl_canvas.ax.spines['top'].set_color('none')
		self.mpl_canvas.ax.yaxis.set_ticks((np.linspace(-1, 1, 9)))
		self.mpl_canvas.ax.xaxis.set_ticks([])
		self.mpl_canvas.ax.xaxis.set_ticklabels([])
		self.mpl_canvas.ax.grid(True)
		self.mpl_canvas.draw()

	def dragEnterEvent(self, e):
		e.accept()
	
	def dragMoveEvent(self,e):
		snap = 5 # vertical snap distance in px
		position = e.pos()
		e.source().move(position)
		# only reorder labels if the dragged label is within snap distance
		y_relative_to_gridrow = (self.grid_y + e.source().pos().y()) % self.row_height
		if (y_relative_to_gridrow <= snap) or (y_relative_to_gridrow >= self.row_height - snap):
			self.reorderLabels()

	def dropEvent(self, e):
		position = e.pos()
		e.source().move(position)
		# in case of a drop, reorder the labels and update the plot
		self.reorderLabels(True)

	def resizeEvent(self, e):
		super(MainWindow, self).resizeEvent(e)
		self.resize_frame()


def main():
	app = QtGui.QApplication(sys.argv)
	mw = MainWindow()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
