from numpy import ceil, floor, arange, abs, log2, argmin, min, zeros
from scipy.fftpack import fft, ifft
import plotly.graph_objects as go
import base64, os

def conv_coef(coef, data, fs):
    dat = zeros((data.shape[0], 2))
    dat[:, 0] = fftfilt(coef[:, 0], data[:, 0])
    dat[:, 1] = fftfilt(coef[:, 1], data[:, 1])

    return dat, fs


def check_fs(fs1, fs2):
    return fs1 == fs2


def nextpow2(x):
    """Return the first integer N such that 2**N >= abs(x)"""

    return ceil(log2(abs(x)))


def fftfilt(b, x, *n):
    """Filter the signal x with the FIR filter described by the
    coefficients in b using the overlap-add method. If the FFT
    length n is not specified, it and the overlap-add block length
    are selected so as to minimize the computational cost of
    the filtering operation."""

    N_x = len(x)
    N_b = len(b)

    # Determine the FFT length to use:
    if len(n):

        # Use the specified FFT length (rounded up to the nearest
        # power of 2), provided that it is no less than the filter
        # length:
        n = n[0]
        if n != int(n) or n <= 0:
            raise ValueError('n must be a nonnegative integer')
        if n < N_b:
            n = N_b
        N_fft = 2**nextpow2(n)
    else:

        if N_x > N_b:

            # When the filter length is smaller than the signal,
            # choose the FFT length and block size that minimize the
            # FLOPS cost. Since the cost for a length-N FFT is
            # (N/2)*log2(N) and the filtering operation of each block
            # involves 2 FFT operations and N multiplications, the
            # cost of the overlap-add method for 1 length-N block is
            # N*(1+log2(N)). For the sake of efficiency, only FFT
            # lengths that are powers of 2 are considered:
            N = 2**arange(ceil(log2(N_b)), floor(log2(N_x)))
            cost = ceil(N_x/(N-N_b+1))*N*(log2(N)+1)
            N_fft = N[argmin(cost)]

        else:

            # When the filter length is at least as long as the signal,
            # filter the signal using a single block:
            N_fft = 2**nextpow2(N_b+N_x-1)

    N_fft = int(N_fft)

    # Compute the block length:
    L = int(N_fft - N_b + 1)

    # Compute the transform of the filter:
    H = fft(b, N_fft)

    y = zeros(N_x,float)
    i = 0
    while i <= N_x:
        il = min([i+L,N_x])
        k = min([i+N_fft,N_x])
        yt = ifft(fft(x[i:il],N_fft)*H,N_fft) # Overlap..
        y[i:k] = y[i:k] + yt[:k-i]            # and add
        i += L

    return y


def plot_waveform(data, fs):
    x_t = arange(0, len(data)/fs+1, 1/fs)
    fig = go.Figure(data=[
        go.Scatter(x=x_t, y=data[:, 0], name='L ch'),
        go.Scatter(x=x_t, y=data[:, 1], name='R ch'),
    ])

    return fig


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'

    return href
