from tkinter import *

import numpy as np

from scipy.ndimage import rotate
from scipy.spatial.transform import Rotation

class Transform (Frame) :

    def __init__(self, master):

        super().__init__(master, padx=5, pady=1)

        self.rotation = 0
        self.mirror = False

        self.rotation_entry = Entry(self, width=8, justify=CENTER)
        self.rotation_scale = Scale(self, from_=-180, to=180, orient=HORIZONTAL, showvalue=False, command=lambda r: self.set_rotation(r, self.rotation_scale))
        self.mirror_check = Checkbutton(self, text='Mirror', command=lambda: self.set_mirror(self.mirror_check.var.get(), self.mirror_check))

        self.rotation_entry.bind('<KeyRelease>', lambda *a: self.set_rotation(self.rotation_entry.get(), self.rotation_entry))
        self.rotation_entry.insert(0, self.rotation)
        self.mirror_check.var = IntVar(value=self.mirror)
        self.mirror_check.config(var=self.mirror_check.var)

        self.rotation_entry.pack(side=LEFT)
        self.rotation_scale.pack(side=LEFT, fill=BOTH, expand=True)
        self.mirror_check.pack(side=RIGHT)

    def set_rotation(self, rotation, caller=None):

        try:

            assert -180 <= float(rotation) <= +180

        except Exception as e:

            self.rotation_entry.delete(0, END)
            self.rotation_entry.insert(0, self.rotation)

            self.rotation_scale.set(self.rotation)

            return

        if not caller is self.rotation_entry:

            self.rotation_entry.delete(0, END)
            self.rotation_entry.insert(0, rotation)

        if not caller is self.rotation_scale:

            c = self.rotation_scale['command']
            self.rotation_scale['command'] = ''

            self.rotation_scale.set(float(rotation))

            self.rotation_scale['command'] = c

        self.rotation = float(rotation)

        if hasattr(self, 'on_rotation'):
            self.on_rotation(self.rotation)

    def set_mirror(self, mirror, caller=None):

        if not caller is self.mirror_check:
            self.mirror_check.var.set(bool(mirror))

        self.mirror = bool(mirror)

        if hasattr(self, 'on_mirror'):
            self.on_mirror(self.mirror)

    def set_from_matrix(self, matrix):

        matrix /= np.sqrt(np.power(matrix, 2).sum(axis=0))

        if np.argmax(np.power(matrix[0], 2)):
            m = True if np.sign(matrix[0,1]) != np.sign(matrix[1,0]) else False
        else:
            m = True if np.sign(matrix[0,0]) == np.sign(matrix[1,1]) else False

        matrix = m if m else matrix.dot(np.diag([-1, 1]))

        matrix3d = np.eye(3); matrix3d[:2,:2] = matrix
        r = Rotation.from_matrix(matrix3d).as_euler('xyz', degrees=True)[2]

        self.set_rotation(r)
        self.set_mirror(m)

    def transform_data(self, data):

        if self.mirror:
            data = data[:,::-1]

        data = rotate(data, self.rotation, order=0, cval=np.nan)

        return data

    def transform_points(self, points, shape_in, shape_out=None):

        if not len(points):
            return points

        shape_out = shape_out if not shape_out is None else shape_in

        t = np.deg2rad(-self.rotation)
        m = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])

        points = np.array(points) + .5 - np.array(shape_in[::-1]) / 2
        points[:,0] *= -1 if self.mirror else 1
        points = m.dot(points.T).T
        points = points - .5 + np.array(shape_out[::-1]) / 2

        return points
