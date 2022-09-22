import streamlit as st
import soundfile as sf
import proc

MAXNUM = 4
ADDVAL = 25
per = 0

st.title('関係者用 補正処理ツール')
st.write('←サイドバーにファイルをアップロードし、`Process`ボタンを押してください。')

st.sidebar.write('### 1. 補正係数ファイルの指定')
coef_file = st.sidebar.file_uploader("Input wave file", type="wav", key='coef')

st.sidebar.write('### 2. 録音データファイルのアップロード')
data_file = st.sidebar.file_uploader("Input wave file", type="wav", key='data')

st.sidebar.write('### 3. 補正処理実行')
bin_data = None

def progress_bar(bar, percentage, val):
    bar.progress(val + ADDVAL)
    percentage.text(f'{val + ADDVAL} %')

    return val + ADDVAL


if coef_file is not None and data_file is not None:
    if st.sidebar.button('Process'):
        coef, fs_coef = sf.read(coef_file)
        data, fs_data = sf.read(data_file)
        if not proc.check_fs(fs_coef, fs_data):
            st.error('Please check Fs!!!')
        else:
            st.write('---')
            st.write('### Progress')
            percentage = st.empty()
            percentage.text('0 %')
            bar = st.progress(0)

            bin_data, fs = proc.conv_coef(coef, data, fs_coef)
            st.write('[1/3] _Calculation done!_')
            per = progress_bar(bar, percentage, per)
else:
    st.sidebar.button('Process', disabled=True)

if bin_data is not None:
    # Plot
    st.write('[2/3] _Plotting waveform ..._')
    duration = 15
    fig = proc.plot_waveform(bin_data[0:duration*fs, :], fs)
    st.plotly_chart(fig, use_container_width=True)
    per = progress_bar(bar, percentage, per)

    # Make output file
    outfilename = 'bin_' + data_file.name
    sf.write(outfilename, bin_data, fs, format='wav')
    per = progress_bar(bar, percentage, per)

    st.write('[3/3] _Generating audio file ..._')
    # href = proc.get_binary_file_downloader_html(outfilename, 'Audio file')
    # st.markdown(href, unsafe_allow_html=True)
    st.audio(outfilename)
    per = progress_bar(bar, percentage, per)

    st.success('ALL DONE!!')