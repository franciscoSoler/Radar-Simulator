import numpy
import pylab
import tkinter

pylab.ion()
# Functions definitions:
x = numpy.arange(0.0,3.0,0.01)
y = numpy.sin(2*numpy.pi*x)
Y = numpy.vstack((y,y/2,y/3,y/4))

#Usual plot depending on a parameter n:
def graphic_plot(n):
    if n < 0: n = 0
    if n > len(Y): n = len(Y)-1
    fig = pylab.figure(figsize=(8,5))
    ax = fig.add_subplot(111)
    ax.plot(x,Y[n,:],'x',markersize=2)
    ax.set_xlabel('x title')
    ax.set_ylabel('y title')
    ax.set_xlim(0.0,3.0)
    ax.set_ylim(-1.0,1.0)
    ax.grid(True)
    pylab.show()


def increase(n):
   return n+1

def decrease(n):
    return n-1

n=0
master = tkinter.Tk()
left_button  = tkinter.Button(master,text="<",command=decrease(n))
left_button.pack(side="left")
right_button = tkinter.Button(master,text=">",command=increase(n))
right_button.pack(side="left")
master.mainloop()