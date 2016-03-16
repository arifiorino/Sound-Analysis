import numpy, matplotlib, struct, wave, scipy.fftpack#, math
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

filename='Goldie.wav'

def avg(a):
    try:
        return sum(a)/len(a)
    except ZeroDivisionError:
        return 0
def dft(x, m=1500):
    N=len(x)
    w=(2*math.pi)/N
    c=[]
    for k in range(0,m):
        if k%100==0:
            print(k,'/',m)
        c.append(math.sqrt(sum(math.pow([x[n]*math.cos(w*k*n) for n in range(N)]),2)+math.pow(sum([x[n]*math.sin(w*k*n) for n in range(N)]),2)))
    return c
def smooth(x,window_len=5,window='hanning'):
    #return x
    if x.ndim != 1:
            raise ValueError
    if x.size < window_len:
            raise ValueError
    if window_len<3:
            return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError
    s=numpy.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
    if window == 'flat': #moving average
            w=numpy.ones(window_len,'d')
    else:  
            w=eval('numpy.'+window+'(window_len)')
    y=numpy.convolve(w/w.sum(),s,mode='same')
    return y[window_len:-window_len+1]
def secToTime(sec):
    m=0
    while sec>=60:
        m+=1
        sec-=60
    if sec<10:
        return str(int(m))+':0'+str(int(sec))
    return str(int(m))+':'+str(int(sec))

waveFile = wave.open('Music/'+filename, 'r')
fileLength = waveFile.getnframes()
fileFramerate=waveFile.getframerate()
dataBytes=waveFile.readframes(waveFile.getnframes())
data=[struct.unpack('HH', dataBytes[i:i+4]) for i in range(0,len(dataBytes),4)]
fftStartI=0
fftFramerate=int(fileFramerate/25)
gWidth=200
gHeight=15000000

FFMpegWriter = animation.writers['ffmpeg']
writer = FFMpegWriter(fps=25)

fig = plt.figure()
fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
left, = plt.plot([], [], 'r')
right, = plt.plot([], [], 'b')

plt.xlim(0, gWidth)
plt.ylim(0, gHeight)
plt.axis('off')

totalLen=secToTime(fileLength/fileFramerate)
with writer.saving(fig, 'Final/'+filename[:-4]+'.mp4', 200):
    while fftStartI<=len(data)-fftFramerate:
        lData=list(smooth(abs(scipy.fftpack.fft(numpy.asarray([data[i][0] for i in range(fftStartI,fftStartI+fftFramerate)])))))[2:]
        rData=list(smooth(abs(scipy.fftpack.fft(numpy.asarray([data[i][1] for i in range(fftStartI,fftStartI+fftFramerate)])))))[2:]
        fftStartI+=fftFramerate
        if int(fftStartI/fftFramerate)%200==0:
            print(secToTime(fftStartI/fileFramerate), '/', totalLen, '('+str(round(fftStartI/fileLength*100,2))+'%)')
        left.set_data(list(range(gWidth)),lData[:gWidth])
        right.set_data(list(range(gWidth)),rData[:gWidth])
        writer.grab_frame()
print('Done.')
