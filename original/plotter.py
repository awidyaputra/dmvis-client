# Uncomment the next two lines if you want to save the animation
import matplotlib
#matplotlib.use("Agg")

import numpy
from matplotlib.pylab import *
from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.animation as animation
import pandas as pd
import requests

urlreceiver = r'http://localhost/unitydb/index.php/db/receiver_sils'


# Sent for figure
font = {'size'   : 9}
matplotlib.rc('font', **font)

# Setup figure and subplots
f0 = figure(num = 0, figsize = (18, 8))#, dpi = 100)
f0.suptitle("Uji Otonom", fontsize=12)
ax01 = subplot2grid((2, 4), (0, 0))
ax012 = ax01.twinx()
ax02 = subplot2grid((2, 4), (0, 1))
ax03 = subplot2grid((2, 4), (1, 0), colspan=2, rowspan=1)
ax04 = ax03.twinx()
ax05 = subplot2grid((2, 4), (0, 2), colspan=2, rowspan=2)
# tight_layout()
subplots_adjust(wspace=0.5, hspace=0.3)

# Set titles of subplots
ax01.set_title('TTC and DTC vs Time')
ax02.set_title('Distance vs Time')
ax03.set_title('Velocity, state, and Command vs Time')
ax05.set_title('Bird Eye View')

# set y-limits
ax01.set_ylim(0,50)
ax012.set_ylim(0,50)
ax02.set_ylim(0,70)
ax03.set_ylim(-6,8)
ax04.set_ylim(-6,8)
# ax05.set_ylim(-600,-520)
# ax05.set_ylim(1455,1465)
# ax05.set_ylim(1455,1465)
ax05.set_ylim(-1,100)

# sex x-limits
ax01.set_xlim(0,10.0)
ax012.set_xlim(0,10.0)
ax02.set_xlim(0,10.0)
ax03.set_xlim(0,10.0)
ax04.set_xlim(0,10.0)
# ax05.set_xlim(-600,-200)
# ax05.set_xlim(-600,-520)
ax05.set_xlim(-25,25)

# Turn on grids
ax01.grid(True)
ax02.grid(True)
ax03.grid(True)
ax05.grid(True)

# set label names
ax01.set_xlabel("t")
ax01.set_ylabel("TTC")
ax012.set_ylabel("DTC")
ax02.set_xlabel("t")
ax02.set_ylabel("m")
ax03.set_xlabel("t")
ax03.set_ylabel("m/s")
ax04.set_ylabel("MC level")
ax05.set_xlabel("x")
ax05.set_ylabel("y")

ax05.axvspan(-1.2,1.3, facecolor='gray', alpha=0.5)

# Data Placeholders

ystate=zeros(0)

yd=zeros(0)
ysd=zeros(0)

yr=zeros(0)
ys=zeros(0)
ydbw=zeros(0)

t=zeros(0)
tdbw=zeros(0)

xt=zeros(0)
yt=zeros(0)
xo=zeros(0)
yo=zeros(0)

yyre=zeros(0)
yxre=zeros(0)

yytp=zeros(0)
yxtp=zeros(0)

yttc = zeros(0)
ydtc = zeros(0)

# wpt = pd.read_csv('waypoints.txt', names=['x','y','v'])

# set plots
p011, = ax01.plot(t,yttc,'c-', label="TTC")
p012, = ax012.plot(t,ydtc,'-', label="DTC")

p021, = ax02.plot(t,yd,'y-', label="distance")
p022, = ax02.plot(t,ysd,'g-', label="safe distance")

p031, = ax03.plot(t,yr,'b-', label="reference speed")
p032, = ax03.plot(t,ys,'r-', label="actual speed")

p041, = ax04.plot(tdbw,ydbw,'m-.', label="dbw command")
p042, = ax04.plot(t,ystate,'k.-', label="state")

# p050, = ax05.plot(wpt['x'], wpt['y'],'k:', label="waypoints")

# ori
# p051, = ax05.plot(yt,xt,'gs', label="Tram")
# p052, = ax05.plot(yo,xo,'b^', label="Obstacle")

# p053, = ax05.plot(yyre,yxre,'g-', label="RE")
# p054, = ax05.plot(yytp,yxtp,'b.', label="TP")

p051, = ax05.plot(xt,yt,'gs', label="Tram")
p052, = ax05.plot(xo,yo,'b^', label="Obstacle")

p053, = ax05.plot(yxre,yyre,'g-', label="RE")
p054, = ax05.plot(yxtp,yytp,'b.', label="TP")


# set lagends
ax01.legend([p011,p012], [p011.get_label(), p012.get_label()])
ax02.legend([p021, p022], [p021.get_label(), p022.get_label()])
ax03.legend([p031,p032, p041], [p031.get_label(), p032.get_label(), p041.get_label()])

# Data Update
xmin = 0
xmax = 10.0
x = 0

def updateData(self):
	global ystate

	global yd
	global ysd

	global yr
	global ys
	global ydbw

	global t
	global x

	global yxre
	global yyre

	global yxtp
	global yytp

	global xt
	global yt

	global xo
	global yo

	global start
	global yttc
	global ydtc

	global tdbw
	# global x

	rreceive = requests.post(urlreceiver)
	receiveText = rreceive.text.replace("%5E","\n")
	if receiveText!="":
		if (len(receiveText.split("BATAS"))>0):
			#print("masuk")
			DecisionMakingPlot = receiveText.split("BATAS")[0]
			ObstacleLocationPlot = receiveText.split("BATAS")[1]
			RailwayEstimatorPlot = receiveText.split("BATAS")[2]
			TrajectoryPredictionPlot = receiveText.split("BATAS")[3]
			DBWcommand = receiveText.split("BATAS")[4]

			print("RECEIVE DecisionMakingPlot:")
			print(DecisionMakingPlot)
			print("RECEIVE ObstacleLocationPlot:")
			print(ObstacleLocationPlot)
			print("RECEIVE RailwayEstimatorPlot:")
			print(RailwayEstimatorPlot)
			print("RECEIVE TrajectoryPredictionPlot:")
			print(TrajectoryPredictionPlot)
			print("RECEIVE DBWcommand:")
			print(DBWcommand)

		# else:
		# 	DecisionMakingPlot = receiveText.split("BATAS")[0]
		# 	ObstacleLocationPlot = receiveText.split("BATAS")[1]
		# 	RailwayEstimatorPlot = receiveText.split("BATAS")[2]
		# 	TrajectoryPredictionPlot = receiveText.split("BATAS")[3]

		# 	print("RECEIVE DecisionMakingPlot:")
		# 	print(DecisionMakingPlot)
		# 	print("RECEIVE ObstacleLocationPlot:")
		# 	print(ObstacleLocationPlot)
		# 	print("RECEIVE RailwayEstimatorPlot:")
		# 	print(RailwayEstimatorPlot)
		# 	print("RECEIVE TrajectoryPredictionPlot:")
		# 	print(TrajectoryPredictionPlot)
		# 	print("RECEIVE DBWcommand:")



			xt=zeros(0)
			yt=zeros(0)
			if DecisionMakingPlot:
				time = float(DecisionMakingPlot.split(",")[0])
				xtram = float(DecisionMakingPlot.split(",")[1])
				ytram = float(DecisionMakingPlot.split(",")[2])
				speed = float(DecisionMakingPlot.split(",")[3])
				distance = float(DecisionMakingPlot.split(",")[4])
				dtc = float(DecisionMakingPlot.split(",")[5])
				ttc = float(DecisionMakingPlot.split(",")[6])
				state = int(DecisionMakingPlot.split(",")[7])
				vref = float(DecisionMakingPlot.split(",")[8])
				safe_d = float(DecisionMakingPlot.split(",")[9])

				ystate=append(ystate,state)
				yd=append(yd,distance)
				ysd=append(ysd,safe_d)
				yr=append(yr,vref)
				ys=append(ys,speed)
				yttc=append(yttc,ttc)
				ydtc=append(ydtc,dtc)
				yt=append(yt,ytram)
				xt=append(xt,xtram)
				
				x = time
				t=append(t,x)
				# print("time ",type(x) ,t)
				
			yo=zeros(0)
			xo=zeros(0) 
			if ObstacleLocationPlot:
				obstacleCount = len(ObstacleLocationPlot.split("\n"))
				for i in range (0,obstacleCount):
					yo=append(yo,float(ObstacleLocationPlot.split("\n")[i].split(",")[1]))
					xo=append(xo,float(ObstacleLocationPlot.split("\n")[i].split(",")[0]))
			yxre=zeros(0)
			yyre=zeros(0)
   
			if RailwayEstimatorPlot:
				obstacleCount = len(RailwayEstimatorPlot.split("\n"))
				for i in range (0,obstacleCount):
					yxre=append(yxre,float(RailwayEstimatorPlot.split("\n")[i].split(",")[0]))
					yyre=append(yyre,float(RailwayEstimatorPlot.split("\n")[i].split(",")[1]))

			yxtp=zeros(0)
			yytp=zeros(0)
			if TrajectoryPredictionPlot:
				obstacleCount = len(TrajectoryPredictionPlot.split("\n"))
				for i in range (0,obstacleCount):
					yxtp=append(yxtp,float(TrajectoryPredictionPlot.split("\n")[i].split(",")[0]))
					yytp=append(yytp,float(TrajectoryPredictionPlot.split("\n")[i].split(",")[1]))

			if DBWcommand:
				dbw = DBWcommand.split(",")[1]
				tdbw=append(tdbw,float(DBWcommand.split(",")[0]))
				ydbw=append(ydbw,int(dbw))


			p011.set_data(t,yttc)
			p012.set_data(t,ydtc)

			#p012.set_data(t,ydbw)

			p021.set_data(t,yd)
			p022.set_data(t,ysd)

			p031.set_data(t,yr)
			p032.set_data(t,ys)

			p041.set_data(tdbw,ydbw)
			p042.set_data(t,ystate)

			p051.set_data(yt,xt)
			p052.set_data(yo,xo)

			p053.set_data(yyre,yxre)
			p054.set_data(yytp,yxtp)

			if x >= xmax-1.00:
				p011.axes.set_xlim(x-xmax+1.0,x+1.0)
				p021.axes.set_xlim(x-xmax+1.0,x+1.0)
				p032.axes.set_xlim(x-xmax+1.0,x+1.0)
				p041.axes.set_xlim(x-xmax+1.0,x+1.0)
				# p050.axes.set_xlim(xtram-30-2.0,xtram-2.0)
				# p051.axes.set_xlim(xtram-30-2.0,xtram-2.0)
				# p052.axes.set_xlim(xtram-30-2.0,xtram-2.0)

			return p011, p012, p021,p022, p031,p032, p041,p053, p051, p052, p054

# interval: draw new frame every 'interval' ms
# frames: number of frames to draw
simulation = animation.FuncAnimation(plt.gcf(), updateData, blit=False, interval=20, repeat=False)
# simulation = animation.FuncAnimation(f0, updateData, blit=False, frames=200, interval=20, repeat=False)

# Uncomment the next line if you want to save the animation
# simulation.save(filename='sim.mp4',dpi=300)

plt.show()
