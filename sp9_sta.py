import scipy.io
import numpy as np
import matplotlib.pylab as plt
import plotly.express as px
import scipy.signal
#import plotly.graph_objects as go
import pandas as ps

def mov_wav(x):
    x[0] = x[0]
    x[1] = x[1]
    for i in range(2, len(x) - 3):
        x[i] = (x[i - 2] + x[i - 1] + x[i] + x[i + 1] + x[i + 2]) / 5
    return x


def main():
    mat = scipy.io.loadmat("src\\02.mat")
    data = mat["simultan_data"]
    vic = np.array(data[32])
    vec = np.array(data[0:32])
    mat, data = None, None
    N = len(vic)
    id = 0
    idx = list()
    v = list()
    mn = list()
    avvic = mov_wav(list(vic))

    # todo: threshold atlepesek:= idx
    for i in range(len(avvic[1:N])):
        if ((avvic[i - 1]) < 0) & (avvic[i] > 0):
            id = i
            idx.append(id)
    idx = np.array(idx)

    # todo: no. of spikes:
    print(len(idx), "db spike")  # 760 + 3

    def spkwd(chn, tau):
        '''
        spike-ok listáját adja meg\\
        bemenet: egy csatorna jele, amelyiken ablakozom a jelet
        időintervallumokat ment ki indexek szerint
        az első és utolsó spike felesleges\\
        kimenet: v tömbbel tér vissza, benne feszültségértékekkel
        '''
        v = list()
        for i in range(len(idx)):
            v.append(chn[idx[i] - tau: idx[i] + tau])
        v.pop(0)
        v.pop(-1)
        v.pop(653)
        # v = np.array(v)
        return v

    # todo: Fs = 20 kHz, time axis:= t
    Tm = N / 20000
    t = np.linspace(0, Tm, N)

    # todo: VIC plotolasa - simitott jellel egyutt
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t[122400:152400], vic[122400:152400], "r")
    # ax.plot(t[122400:152400], avvic[122400:152400])
    ax.set_title("Raw IC signal")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("potential (mV)")
    fig.show()
    fig.savefig("raw_ic_signal.png", dpi=300)

    # todo: IC spike-ok listaja: 760x20k
    ic_sps = spkwd(vic, 1000)
    t = np.linspace(-.5, .5, 2000)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t, ic_sps[1])
    f = open("ic_sps.txt", "w")
    for i in range(1, len(ic_sps)):
        f.write(str(ic_sps[i]) + ", ")
        if len(ic_sps[i]) == 2000: ax.plot(t, ic_sps[i])
    f.close()
    fig.show()
    fig.savefig("collected_ic_spikes-100ms.png", dpi=300)  # 758 pcs

    # todo: atlagos IC spike: 1x1000 shape
    v = spkwd(vic, 500)
    v = np.array(v)  # v-t fajlba: ablakozott spike-ok
    mn = v.mean(axis=0)

    # todo: atlagos EC spike:
    spec = list()
    mnspec = list()  # ez lesz a (voltage) mean of spikes EC
    for i in range(len(vec)):
        spec.append(spkwd(vec[i], 200))  # 10 ms idoablak vec jelen
        mnspec.append(np.array(spec[i]).mean(axis=0))

    # todo: VIC raw signal
    red = px.colors.qualitative.Plotly[1]
    t_vic = np.linspace(-25, 25, 1000)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t_vic, mn, "r")
    ax.set_title("Average spike at the soma")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("potential (mV)")
    fig.show()
    fig.savefig("av_sp_at_soma_50ms.png", dpi=300)

    t = np.linspace(-15, 15, 600)  # --> tau = 300
    vi30 = np.array(spkwd(vic, 300)).mean(axis=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t, vi30, "r")
    ax.set_title("Average spike at the soma (30 ms)")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("potential (mV)")
    fig.show()
    fig.savefig("av_sp_at_soma_30ms.png", dpi=300)

    t = np.linspace(-10, 10, 400)
    vi20 = np.array(spkwd(vic, 200)).mean(axis=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t, vi20, "r")
    ax.set_title("Average spike at the soma (20 ms)")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("potential (mV)")
    fig.show()
    fig.savefig("av_sp_at_soma_20ms.png", dpi=300)

    # todo: VEC mean 20 ms plot
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, mnspec[0])
    for i in range(1, len(mnspec)):
        ax.plot(t, mnspec[i])
    ax.set_title("Average EC spikes")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("potential (mV)")
    fig.show()
    fig.savefig("av_sp_EC_20ms.png", dpi=300)

    # todo: VEC heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(mnspec, cmap='Spectral')
    plt.tight_layout()
    plt.show()
    fig.savefig("VEC_heatmap.png", dpi=300)

'''
    mnspec = np.array(mnspec)
    icsd = tyinv @ mnspec
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(icsd, cmap='Spectral')
    plt.tight_layout()
    plt.show()
    fig.savefig("csd_heatmap.png", dpi=300)


    f = open("ablakozott_spike-ok_1x1000_alak.txt", "w")
    MTX = mn

    for l in range(len(MTX)):  # végig megy a mtx sorain
        for e in range(len(MTX[l])):  # a sor elemein
            if e != len(MTX[l]) - 1:  # ha NEM az utolsó elem, akkor tesz vesszőt utána
                f.write(str(MTX[l][e]) + ',')
            else:
                f.write(str(MTX[l][e]))  # amúgy nem
        f.write("\n")  # a mtx minden új sora új sorba kerül
    f.close()

    f = open("EC_average_20ms_32x400_alak.txt", "w")
    MTX = list(mnspec)

    for l in range(len(MTX)):  # végig megy a mtx sorain
        for e in range(len(MTX[l])):  # a sor elemein
            if e != len(MTX[l]) - 1:  # ha NEM az utolsó elem, akkor tesz vesszőt utána
                f.write(str(MTX[l][e]) + ',')
            else:
                f.write(str(MTX[l][e]))  # amúgy nem
        f.write("\n")  # a mtx minden új sora új sorba kerül
    f.close()


    f = open("raw_IC_jel_1500ms_1x30000.txt", "w")
    MTX = vic[122400:152400]

    for l in range(len(MTX)):  # végig megy a mtx sorain
        for e in range(len(MTX[l])):  # a sor elemein
            if e != len(MTX[l]) - 1:  # ha NEM az utolsó elem, akkor tesz vesszőt utána
                f.write(str(MTX[l][e]) + ',')
            else:
                f.write(str(MTX[l][e]))  # amúgy nem
        f.write("\n")  # a mtx minden új sora új sorba kerül
    f.close()

    f = open("1db_IC_jel_30ms_1x600.txt", "w")
    MTX = vi30

    for l in range(len(MTX)):  # végig megy a mtx sorain
        for e in range(len(MTX[l])):  # a sor elemein
            if e != len(MTX[l]) - 1:  # ha NEM az utolsó elem, akkor tesz vesszőt utána
                f.write(str(MTX[l][e]) + ',')
            else:
                f.write(str(MTX[l][e]))  # amúgy nem
        f.write("\n")  # a mtx minden új sora új sorba kerül
    f.close()

    f = open("1db_IC_jel_20ms_1x400.txt", "w")
    MTX = vi20

    for l in range(len(MTX)):  # végig megy a mtx sorain
        for e in range(len(MTX[l])):  # a sor elemein
            if e != len(MTX[l]) - 1:  # ha NEM az utolsó elem, akkor tesz vesszőt utána
                f.write(str(MTX[l][e]) + ',')
            else:
                f.write(str(MTX[l][e]))  # amúgy nem
        f.write("\n")  # a mtx minden új sora új sorba kerül
    f.close()

    f = open("csd_20ms_32x400.txt", "w")
    MTX = icsd

    for l in range(len(MTX)):  # végig megy a mtx sorain
        for e in range(len(MTX[l])):  # a sor elemein
            if e != len(MTX[l]) - 1:  # ha NEM az utolsó elem, akkor tesz vesszőt utána
                f.write(str(MTX[l][e]) + ',')
            else:
                f.write(str(MTX[l][e]))  # amúgy nem
        f.write("\n")  # a mtx minden új sora új sorba kerül
    f.close()
    #todo: vic[122400:152400], vi30, vi20, icsd

'''

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

    '''
        fig = go.Figure()
        fig.add_trace(go.Scatter(name="VIC", x=t_vic, y=vic[122400:152400], mode="lines")) #, color = red))
        fig.show()
        fig.write_html("VIC_raw.html")


        #VEC plotting
        fig = go.Figure()
        fig.add_trace(go.Scatter(name="VEC(Ch 1)", x=taxms, y=mnspec[0], mode="lines"))
        for i in range(1, len(mnspec)):
            fig.add_trace(go.Scatter(name=f"VEC(Ch {i + 1})", x=taxms, y=mnspec[i],
                                     mode="lines"))
        fig.show()
        fig.write_html("VEC_mean.html")
    '''
