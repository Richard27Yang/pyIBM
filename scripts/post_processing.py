# script: $pyIBM/scripts/post_processing.py
# Olivier Mesnard (mesnardo@gwu.edu)
# BarbaGroup (lorenabarba.com)

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0,'./src')
from case import *
from mesh import *
from body import *
from solver import *
from variable import *
from operations import *

def plot_pressure(p, body=None):
	'''Plot pressure field on the mesh.'''

	p.read()
	
	plt.figure(num=None)
	plt.grid(False)
	plt.xlabel(r'$x$', fontsize=20)
	plt.xlabel(r'$y$', fontsize=20)

	nc = 100
	pmin, pmax = p.field.min(), p.field.max()
	pmin, pmax = -0.5, 0.5
	if pmin == pmax:
		pmin, pmax = -0.5, 0.5
	levels = np.linspace(pmin, pmax, nc)
	
	cont = plt.contourf(Mesh.x, Mesh.y, p.field.reshape(Mesh.Ny, Mesh.Nx),\
						levels, extend='both', cmap=cm.jet)
	cbar = plt.colorbar(cont)
	cbar.set_label('pressure')

	if Mesh.is_body:
		plt.plot(np.append(body.x,body.x[0]), np.append(body.y, body.y[0]), 'k', ls='-', lw=1)

	plt.xlim(Mesh.xmin, Mesh.xmax)
	plt.ylim(Mesh.ymin, Mesh.ymax)

	plt.title('pressure - '+str(Solver.ite))
	plt.savefig(Case.path+'/images/'+'pressure'+str('%04d'%(Solver.ite,))+'.png')
	
	plt.clf()
	plt.close()

def plot_velocity(u, v, body=None):
	'''Plot velocity field on the mesh.'''
	
	u.read()
	v.read()
	
	plt.figure(num=None)
	plt.grid(False)
	plt.xlabel(r'$x$', fontsize=20)
	plt.xlabel(r'$y$', fontsize=20)

	nc = 100
	magn = np.sqrt(u.field**2+v.field**2)
	umin, umax = magn.min(), magn.max()
	umin, umax = 0., 1.
	levels = np.linspace(umin, umax, nc)

	cont = plt.contourf(Mesh.x, Mesh.y, magn.reshape(Mesh.Nx, Mesh.Ny),\
						levels, extend='both', cmap=cm.jet)
	cbar = plt.colorbar(cont)
	cbar.set_label('velocity')

	plt.streamplot(Mesh.x, Mesh.y,\
				   u.field.reshape(Mesh.Ny, Mesh.Nx),\
				   v.field.reshape(Mesh.Ny, Mesh.Nx))

	if Mesh.is_body:
		plt.plot(np.append(body.x,body.x[0]), np.append(body.y, body.y[0]), 'k', ls='-', lw=1)

	plt.xlim(Mesh.xmin, Mesh.xmax)
	plt.ylim(Mesh.ymin, Mesh.ymax)

	plt.title('velocity - '+str(Solver.ite))
	plt.savefig(Case.path+'/images/'+'velocity'+str('%04d'%(Solver.ite,))+'.png')
	
	plt.clf()
	plt.close()


def plot_vorticity(u, v, body=None):
	'''Plot vorticity field on the mesh.'''
	
	u.read()
	v.read()
	w = grad(v,'x') - grad(u,'y')

	plt.figure(num=None)
	plt.grid(False)
	plt.xlabel(r'$x$', fontsize=20)
	plt.xlabel(r'$y$', fontsize=20)

	nc = 100
	wmin, wmax = w.min(), w.max()
	wmin, wmax = -1.0, 1.0
	if wmin == wmax:
		wmin, wmax = -1.0, 1.0
	levels = np.linspace(wmin, wmax, nc)
	
	cont = plt.contourf(Mesh.x, Mesh.y, w.reshape(Mesh.Ny, Mesh.Nx),\
						levels, extend='both', cmap=cm.jet)
	cbar = plt.colorbar(cont)
	cbar.set_label('vorticity')

	if Mesh.is_body:
		plt.plot(np.append(body.x,body.x[0]), np.append(body.y, body.y[0]), 'k', ls='-', lw=1)

	plt.xlim(Mesh.xmin, Mesh.xmax)
	plt.ylim(Mesh.ymin, Mesh.ymax)

	plt.title('vorticity - '+str(Solver.ite))
	plt.savefig(Case.path+'/images/'+'vorticity'+str('%04d'%(Solver.ite,))+'.png')
	
	plt.clf()
	plt.close()


def main(arg):
	'''Plot either pressure, velocity or vorticity,
	at every time saved in the case folder.
	'''
	Case(arg[1])

	mesh = Mesh()

	body = Body() if Mesh.is_body else None

	Solver()

	if len(arg) > 2:
		variables = arg[2::]
		if 'all' in arg:
			variables = ['pressure', 'velocity', 'vorticity']
	else:
		variables = ['pressure', 'velocity', 'vorticity']

	print variables	

	if 'pressure' in variables:
		p = Variable('p', skip_assemble=True)
	if 'velocity' in variables or 'vorticity' in variables:
		u = Variable('u', skip_assemble=True)
		v = Variable('v', skip_assemble=True)
		if 'vorticity' in variables:
			u.assemble_matrix('gradienty', scheme='central', direction='y')
			v.assemble_matrix('gradientx', scheme='central', direction='x')

	if not os.path.isdir(Case.path+'/images'):
		os.system('mkdir '+Case.path+'/images')

	for ite in xrange(Solver.start, Solver.start+Solver.nt, Solver.write_every):
		
		Solver.ite += Solver.write_every

		print 'Iteration ', Solver.ite

		if 'pressure' in variables:
			plot_pressure(p, body)
		if 'velocity' in variables:
			plot_velocity(u, v, body)
		if 'vorticity' in variables:
			plot_vorticity(u, v, body)
		

if __name__ == '__main__':
	print '\n\t----- pyIBM - POST-PROCESSING -----\n'
	main(sys.argv)
	print '\n\t----- pyIBM - END -----\n'
