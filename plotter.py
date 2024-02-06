import dmvis
import matplotlib
import matplotlib.animation as animation
from matplotlib import pyplot as plt


vis = dmvis.DMVisualisation()

# simulation = animation.FuncAnimation(plt.gcf(), vis.mpl_func_animation_cb, blit=False, interval=20, repeat=False)

# plt.show()
vis.show()
plt.show()
