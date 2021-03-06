"""
Derived module from filehandler.py to handle vtk files.
"""
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as a3
import vtk
import pygem.filehandler as fh


class VtkHandler(fh.FileHandler):
	"""
	Vtk file handler class

	:cvar string infile: name of the input file to be processed.
	:cvar string outfile: name of the output file where to write in.
	:cvar string extension: extension of the input/output files. It is equal to '.vtk'.
	"""
	def __init__(self):
		super(VtkHandler, self).__init__()
		self.extension = '.vtk'


	def parse(self, filename):
		"""
		Method to parse the file `filename`. It returns a matrix with all the coordinates.

		:param string filename: name of the input file.

		:return: mesh_points: it is a `n_points`-by-3 matrix containing the coordinates of
			the points of the mesh
		:rtype: numpy.ndarray

		.. todo::

			- specify when it works
		"""
		self._check_filename_type(filename)
		self._check_extension(filename)

		self.infile = filename

		reader = vtk.vtkDataSetReader()
		reader.SetFileName(self.infile)
		reader.ReadAllVectorsOn()
		reader.ReadAllScalarsOn()
		reader.Update()
		data = reader.GetOutput()

		n_points = data.GetNumberOfPoints()
		mesh_points = np.zeros([n_points, 3])

		for i in range(n_points):
			mesh_points[i][0], mesh_points[i][1], mesh_points[i][2] = data.GetPoint(i)

		return mesh_points


	def write(self, mesh_points, filename):
		"""
		Writes a vtk file, called filename, copying all the structures from self.filename but
		the coordinates. mesh_points is a matrix that contains the new coordinates to
		write in the vtk file.

		:param numpy.ndarray mesh_points: it is a `n_points`-by-3 matrix containing
			the coordinates of the points of the mesh
		:param string filename: name of the output file.

		.. todo:: DOCS
		"""
		self._check_filename_type(filename)
		self._check_extension(filename)
		self._check_infile_instantiation(self.infile)

		self.outfile = filename

		reader = vtk.vtkDataSetReader()
		reader.SetFileName(self.infile)
		reader.ReadAllVectorsOn()
		reader.ReadAllScalarsOn()
		reader.Update()
		data = reader.GetOutput()

		points = vtk.vtkPoints()

		for i in range(data.GetNumberOfPoints()):
			points.InsertNextPoint(mesh_points[i, :])

		data.SetPoints(points)

		writer = vtk.vtkDataSetWriter()
		writer.SetFileName(self.outfile)

		if vtk.VTK_MAJOR_VERSION <= 5:
			writer.SetInput(data)
		else:
			writer.SetInputData(data)

		writer.Write()


	def plot(self, plot_file=None, save_fig=False):
		"""
		Method to plot a vtk file. If `plot_file` is not given it plots `self.infile`.

		:param string plot_file: the vtk filename you want to plot.
		:param bool save_fig: a flag to save the figure in png or not. If True the
			plot is not shown.
		"""
		if plot_file is None:
			plot_file = self.infile
		else:
			self._check_filename_type(plot_file)

		# Read the source file.
		reader = vtk.vtkUnstructuredGridReader()
		reader.SetFileName(plot_file)
		reader.Update()

		data = reader.GetOutput()
		points = data.GetPoints()
		ncells = data.GetCells().GetNumberOfCells()

		# for each cell it contains the indeces of the points that define the cell
		cells = np.zeros((ncells, 3))

		for i in range(0, ncells):
			for j in range(0, 3):
				cells[i][j] = data.GetCell(i).GetPointId(j)

		figure = plt.figure()
		axes = a3.Axes3D(figure)
		vtx = np.zeros((ncells, 3, 3))
		for i in range(0, ncells):
			for j in range(0, 3):
				vtx[i][j][0], vtx[i][j][1], vtx[i][j][2] = points.GetPoint(int(cells[i][j]))
			tri = a3.art3d.Poly3DCollection([vtx[i]])
			tri.set_color('b')
			tri.set_edgecolor('k')
			axes.add_collection3d(tri)

		scale = vtx.flatten(-1)
		axes.auto_scale_xyz(scale, scale, scale)

		# Show the plot to the screen
		if not save_fig:
			plt.show()
		else:
			figure.savefig(plot_file.split('.')[0] + '.png')


	def show(self, show_file=None):
		"""
		Method to show a vtk file. If `show_file` is not given it shows `self.infile`.

		:param string show_file: the vtk filename you want to show.
		"""
		if show_file is None:
			show_file = self.infile
		else:
			self._check_filename_type(show_file)

		# Read the source file.
		reader = vtk.vtkUnstructuredGridReader()
		reader.SetFileName(show_file)
		reader.Update() # Needed because of GetScalarRange
		output = reader.GetOutput()
		scalar_range = output.GetScalarRange()

		# Create the mapper that corresponds the objects of the vtk file
		# into graphics elements
		mapper = vtk.vtkDataSetMapper()
		if vtk.VTK_MAJOR_VERSION <= 5:
			mapper.SetInput(output)
		else:
			mapper.SetInputData(output)
		mapper.SetScalarRange(scalar_range)

		# Create the Actor
		actor = vtk.vtkActor()
		actor.SetMapper(mapper)

		# Create the Renderer
		renderer = vtk.vtkRenderer()
		renderer.AddActor(actor)
		# Set background color (white is 1, 1, 1)
		renderer.SetBackground(20, 20, 20)

		# Create the RendererWindow
		renderer_window = vtk.vtkRenderWindow()
		renderer_window.AddRenderer(renderer)

		# Create the RendererWindowInteractor and display the vtk_file
		interactor = vtk.vtkRenderWindowInteractor()
		interactor.SetRenderWindow(renderer_window)
		interactor.Initialize()
		interactor.Start()

