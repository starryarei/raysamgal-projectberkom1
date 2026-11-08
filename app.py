import os
import streamlit as st


# Kalkulator Emisi (buat dipindahin ke Streamlit)
# Menghitung emisi, rata-rata, dan emisi minimum kendaraan


st.set_page_config(page_title="Kalkulator Emisi", layout="centered")

# backgroundnya dijadiin warna hijau
st.markdown("""
<style>
.stApp { background-color: #f4faf5; }
h1, h2, h3 { color: #1b5e20; }
div.stButton > button {
    background-color: #2e7d32;
    color: white;
    border: none;
    border-radius: 6px;
}
div.stButton > button:hover {
    background-color: #1b5e20;
    color: white;
}
</style>
""", unsafe_allow_html=True)



# Fungsi menghitung emisi

def emisitotal(sumber, jarak, konsumsi_energi, efisiensi_BBM, faktorlistrik, faktorBBM, persen):
    if sumber == "Listrik":
        emisi = jarak * konsumsi_energi * faktorlistrik
    elif sumber == "BBM":
        emisi = (jarak / efisiensi_BBM) * faktorBBM
    else:
        emisi = (persen / 100) * jarak * konsumsi_energi * faktorlistrik + (1 - (persen / 100)) * (jarak / efisiensi_BBM) * faktorBBM
    return emisi



# historynya disimpan di session_state biar gak hilang
# pas halaman direfresh Streamlit

if "riwayat_jenis" not in st.session_state:
    st.session_state.riwayat_jenis = []
    st.session_state.riwayat_emisi = []
    st.session_state.riwayat_satuan = []

riwayat_jenis = st.session_state.riwayat_jenis
riwayat_emisi = st.session_state.riwayat_emisi
riwayat_satuan = st.session_state.riwayat_satuan


# Header

st.title("Kalkulator Emisi")
st.write("Hitung emisi, rata-rata, dan emisi minimum kendaraan untuk perjalanan tertentu.")


# Input

st.header("Input Perjalanan")

jenis = st.selectbox("Jenis kendaraan", ["Mobil", "Motor", "Truk"])
sumber = st.selectbox("Jenis sumber energi", ["Listrik", "BBM", "Hybrid"])

persen = 0
if sumber == "Hybrid":
    persen = st.slider("Persentase penggunaan listrik (%)", 0, 100, 50)

# Hybrid dan listrik hanya menghitung CO2
if sumber == "Hybrid" or sumber == "Listrik":
    jenis_emisi = "CO2"
    st.info("Kendaraan hybrid dan listrik hanya menghitung emisi CO2")
else:
    jenis_emisi = st.selectbox("Jenis emisi", ["CO2", "CO", "NOx"])

# Opsi BBM hanya untuk mobil (motor = bensin, truk = solar)
jenis_bbm = ""
if (sumber == "BBM" or sumber == "Hybrid") and jenis == "Mobil":
    jenis_bbm = st.selectbox("Jenis bahan bakar", ["Bensin", "Solar"])

jarak = st.number_input("Jarak yang ditempuh (km)", min_value=1, value=10, step=1)


# Tombol hitung

if st.button("Hitung emisi"):
    konsumsi_energi = 0
    faktorlistrik = 0
    efisiensi_BBM = 0
    faktorBBM = 0

    # Faktor listrik
    if sumber == "Listrik" or sumber == "Hybrid":
        if jenis == "Mobil":
            konsumsi_energi = 0.12
        elif jenis == "Motor":
            konsumsi_energi = 0.04
        else:
            konsumsi_energi = 1.50
        faktorlistrik = 0.85

    # Faktor BBM
    if sumber == "BBM" or sumber == "Hybrid":
        if jenis == "Mobil":
            efisiensi_BBM = 14
        elif jenis == "Motor":
            efisiensi_BBM = 50
        else:
            efisiensi_BBM = 3

        if jenis_emisi == "CO2":
            if jenis == "Mobil":
                if jenis_bbm == "Bensin":
                    faktorBBM = 2.4
                else:
                    faktorBBM = 2.7
            elif jenis == "Motor":
                faktorBBM = 2.4
            else:
                faktorBBM = 2.7
            satuan = "kg CO2"

        elif jenis_emisi == "CO":
            if jenis == "Mobil":
                if jenis_bbm == "Bensin":
                    faktorBBM = 0.003
                else:
                    faktorBBM = 0.0007
            elif jenis == "Motor":
                faktorBBM = 0.014
            else:
                faktorBBM = 0.010
            satuan = "kg CO"

        else:
            if jenis == "Mobil":
                if jenis_bbm == "Bensin":
                    faktorBBM = 0.00025
                else:
                    faktorBBM = 0.0015
            elif jenis == "Motor":
                faktorBBM = 0.0002
            else:
                faktorBBM = 0.014
            satuan = "kg NOx"

        if jenis_emisi != "CO2":
            faktorlistrik = 0
    else:
        satuan = "kg CO2"

    emisi = emisitotal(sumber, jarak, konsumsi_energi, efisiensi_BBM, faktorlistrik, faktorBBM, persen)

    riwayat_jenis.append(jenis)
    riwayat_emisi.append(emisi)
    riwayat_satuan.append(satuan)

    st.success("Emisi yang dihasilkan " + jenis + " adalah " + format(emisi, ".2f") + " " + satuan)

    # Status emisi (g/km)
    emisi_per_km = (emisi / jarak) * 1000
    if satuan == "kg CO2":
        batas = 150
    elif satuan == "kg CO":
        batas = 0.8
    else:
        batas = 0.05

    if emisi_per_km > batas:
        st.warning("Emisi tergolong tinggi.")
    else:
        st.success("Emisi tergolong rendah.")


# Hasil

if len(riwayat_emisi) > 0:
    st.header("Hasil Kalkulator")

    # Cek apakah semua satuan sama
    satuan_sama = True
    for i in range(len(riwayat_satuan)):
        if riwayat_satuan[i] != riwayat_satuan[0]:
            satuan_sama = False

    if satuan_sama == False:
        st.warning("Jenis emisi berbeda. Total dan rata-rata tidak dapat dibandingkan.")
        for i in range(len(riwayat_emisi)):
            st.write("Perjalanan " + str(i + 1) + ": " + format(riwayat_emisi[i], ".2f") + " " + riwayat_satuan[i])

    else:
        total_emisi = sum(riwayat_emisi)
        rata2_emisi = total_emisi / len(riwayat_emisi)

        if len(riwayat_emisi) == 1:
            st.write("Emisi yang dihasilkan " + riwayat_jenis[0] + " adalah " + format(riwayat_emisi[0], ".2f") + " " + riwayat_satuan[0])
        else:
            output = st.radio("Jenis output", ["Total emisi", "Rata-rata emisi", "Emisi minimum"])

            if output == "Total emisi":
                st.write("Emisi total yang dihasilkan adalah " + format(total_emisi, ".2f") + " " + riwayat_satuan[0])

                # Hitung kontribusi tiap kendaraan
                kontribusi = {"Mobil": 0, "Motor": 0, "Truk": 0}
                for i in range(len(riwayat_jenis)):
                    kontribusi[riwayat_jenis[i]] += riwayat_emisi[i]

                persenkendaraan = [
                    (kontribusi["Mobil"] / total_emisi) * 100,
                    (kontribusi["Motor"] / total_emisi) * 100,
                    (kontribusi["Truk"] / total_emisi) * 100
                ]
                jeniskendaraan2 = ["Mobil", "Motor", "Truk"]

                # Urutkan dari terendah ke tertinggi
                for i in range(3):
                    for j in range(3 - i - 1):
                        if persenkendaraan[j] > persenkendaraan[j + 1]:
                            sementara = persenkendaraan[j]
                            persenkendaraan[j] = persenkendaraan[j + 1]
                            persenkendaraan[j + 1] = sementara

                            nama = jeniskendaraan2[j]
                            jeniskendaraan2[j] = jeniskendaraan2[j + 1]
                            jeniskendaraan2[j + 1] = nama

                st.write("Persen kontribusi terendah hingga tertinggi:")
                for i in range(3):
                    st.write(jeniskendaraan2[i] + ": " + format(persenkendaraan[i], ".2f") + "%")

            elif output == "Rata-rata emisi":
                st.write("Emisi rata-rata yang dihasilkan adalah " + format(rata2_emisi, ".2f") + " " + riwayat_satuan[0])

            else:
                # Salin list biar history asli gak berubah urutannya
                emisi_urut = list(riwayat_emisi)
                jenis_urut = list(riwayat_jenis)
                n = len(emisi_urut)

                for i in range(n):
                    for j in range(n - i - 1):
                        if emisi_urut[j] > emisi_urut[j + 1]:
                            sementara = emisi_urut[j]
                            emisi_urut[j] = emisi_urut[j + 1]
                            emisi_urut[j + 1] = sementara

                            nama = jenis_urut[j]
                            jenis_urut[j] = jenis_urut[j + 1]
                            jenis_urut[j + 1] = nama

                st.write("Emisi terendah ke tertinggi:")
                for i in range(n):
                    st.write(jenis_urut[i] + ": " + format(emisi_urut[i], ".2f") + " " + riwayat_satuan[0])

                st.write("Emisi minimum dihasilkan oleh " + jenis_urut[0] + " dengan nilai " + format(emisi_urut[0], ".2f") + " " + riwayat_satuan[0])

    if st.button("Hapus semua perjalanan"):
        st.session_state.riwayat_jenis = []
        st.session_state.riwayat_emisi = []
        st.session_state.riwayat_satuan = []
        st.rerun()


# Tim kita mantaap 

st.divider()
st.subheader("Tim Pengembang")
if os.path.exists("foto_kelompok.png"):
    st.image("foto_kelompok.png", use_container_width=True)
st.write("Sammy, Rayya, Galuh")
