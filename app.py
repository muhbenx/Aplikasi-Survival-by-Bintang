import subprocess, sys
def install(package): subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try: import folium, streamlit_folium, streamlit_js_eval
except ImportError: install("folium"); install("streamlit-folium"); install("streamlit-js-eval")

import time
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from google import genai
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# Config Halaman Utama
st.set_page_config(
    page_title="Multi-Tool AI & Survival App",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- FUNGSI KOMPRES SUPER CEPAT (MAX 600px) ---
def compress_image_fast(uploaded_file, max_size=600):
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((max_size, max_size))
    return img

# --- FUNGSI CALL GEMINI CEPAT ---
def call_gemini_fast(client, contents):
    models_to_try = ["gemini-1.5-flash", "gemini-3.6-flash"]
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            return response
        except Exception:
            continue
    raise Exception("Koneksi ke AI sibuk. Silakan coba klik tombol sekali lagi.")

# --- SIDEBAR NAVIGASI MENU ---
with st.sidebar:
    st.title("🛠️ Multi-Tool Navigation")
    menu_pilihan = st.radio(
        "Pilih Fitur / Menu:",
        ["📦 AI Object Counter", "🧭 Offline Survival Locator"]
    )
    st.divider()

# ==============================================================================
# MENU 1: AI OBJECT COUNTER
# ==============================================================================
if menu_pilihan == "📦 AI Object Counter":
    st.title("📦 AI Object Counter")
    st.caption("Automated Visual Inventory & Overlapping Object Detector")

    with st.sidebar:
        st.header("⚙️ Config AI")
        api_key = st.text_input("Gemini API Key:", type="password", placeholder="Paste API Key di sini...")
        st.caption("Powered by Gemini Vision AI")

    st.subheader("🎯 Mode Perhitungan")
    mode_hitung = st.radio(
        "Pilih metode analisis AI:",
        ["Hitung Objek Spesifik (Sesuai Foto Sampel)", "Hitung TOTAL SEMUA Objek dalam Wadah"],
        label_visibility="collapsed"
    )

    file_sample = None
    file_box = None

    if mode_hitung == "Hitung Objek Spesifik (Sesuai Foto Sampel)":
        col1, col2 = st.columns(2)
        with col1:
            st.write("**1. Sampel Objek**")
            file_sample = st.file_uploader("Upload foto sampel", type=["jpg", "jpeg", "png"], key="sample")
            if file_sample:
                st.image(file_sample, use_container_width=True)

        with col2:
            st.write("**2. Isi Wadah / Box**")
            file_box = st.file_uploader("Upload foto wadah terisi", type=["jpg", "jpeg", "png"], key="box")
            if file_box:
                st.image(file_box, use_container_width=True)
    else:
        st.write("**Upload Foto Isi Wadah / Box**")
        file_box = st.file_uploader("Upload foto wadah yang ingin dihitung seluruh isinya", type=["jpg", "jpeg", "png"], key="box_single")
        if file_box:
            st.image(file_box, use_container_width=True)

    if st.button("🚀 Mulai Perhitungan AI", use_container_width=True, type="primary"):
        if not api_key or not file_box:
            st.error("Lengkapi API Key dan Foto Wadah terlebih dahulu!")
        elif mode_hitung == "Hitung Objek Spesifik (Sesuai Foto Sampel)" and not file_sample:
            st.warning("Upload foto sampel barangnya dulu ya!")
        else:
            with st.spinner("⚡ Menghitung objek secara kilat..."):
                try:
                    client = genai.Client(api_key=api_key)
                    img_box_compressed = compress_image_fast(file_box)
                    
                    if mode_hitung == "Hitung Objek Spesifik (Sesuai Foto Sampel)":
                        img_sample_compressed = compress_image_fast(file_sample)
                        contents_input = [img_sample_compressed, img_box_compressed]
                        prompt = "Hitung jumlah objek di foto kedua yang persis/sejenis dengan foto sampel pertama. Berikan output: 1. Total Terdeteksi (Pcs), 2. Catatan singkat posisi/tumpukan."
                    else:
                        contents_input = [img_box_compressed]
                        prompt = "Hitung total semua barang/objek dalam foto ini. Berikan output: 1. Rincian per jenis barang, 2. TOTAL KESELURUHAN BARANG (Pcs)."

                    contents_input.append(prompt)
                    response = call_gemini_fast(client, contents_input)
                    
                    st.balloons()
                    with st.container(border=True):
                        st.subheader("📊 Hasil Analisis AI")
                        st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# ==============================================================================
# MENU 2: ALL-IN-ONE OFFLINE SURVIVAL LOCATOR & SUITE
# ==============================================================================
elif menu_pilihan == "🧭 Offline Survival Locator":
    st.title("🧭 Offline Survival Suite")
    st.caption("Deteksi GPS, Altitudo, Kompas Digital, Sinyal SOS Audio/Layar, & Buku Panduan Survival (Full Offline)")

    st.info("💡 **Tips Survival:** GPS HP bekerja via satelit ruang angkasa tanpa sinyal seluler. Matikan paket data & hemat baterai saat tersesat!")

    tab_gps, tab_tools, tab_guide = st.tabs(["📡 GPS, Peta & Altitudo", "🚨 Tools SOS & Kompas", "📖 Panduan Survival"])

    # ---------------- TAB 1: GPS & PETA ----------------
    with tab_gps:
        st.subheader("📡 Status Koordinat GPS & Ketinggian")
        location = get_geolocation()

        if location:
            lat = location['coords']['latitude']
            lon = location['coords']['longitude']
            accuracy = location['coords']['accuracy']
            
            # Ambil data altitudo dari GPS satelit (jika tersedia)
            altitude = location['coords'].get('altitude', None)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latitude", f"{lat:.5f}")
            with col2:
                st.metric("Longitude", f"{lon:.5f}")
            with col3:
                st.metric("Ketinggian", f"{altitude:.0f} mdpl" if altitude is not None else "N/A")
            
            st.caption(f"Akurasi Sinyal GPS: ±{accuracy:.1f} meter")

            st.divider()
            st.subheader("🗺️ Peta Posisi Kamu")
            m = folium.Map(location=[lat, lon], zoom_start=16)
            folium.Marker(
                [lat, lon],
                popup="LOKASI KAMU SAAT INI",
                tooltip="Posisi Terdeteksi GPS",
                icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
            ).add_to(m)

            st_folium(m, width=700, height=400)

            st.divider()
            st.subheader("🆘 Pesan Bantuan SOS (SMS/Radio)")
            alt_text = f" Ketinggian: {altitude:.0f}m." if altitude else ""
            pesan_sos = f"SOS! Saya tersesat di koordinat: https://maps.google.com/?q={lat},{lon} ({lat:.6f}, {lon:.6f}).{alt_text} Butuh pertolongan secepatnya!"
            st.text_area("Salin pesan ini untuk dikirim via SMS biasa ke Tim SAR/Keluarga:", value=pesan_sos, height=90)

        else:
            st.warning("⚠️ Mengambil sinyal GPS... Izinkan akses lokasi di browser kamu.")

    # ---------------- TAB 2: TOOLS SOS & KOMPAS ----------------
    with tab_tools:
        st.subheader("🧭 Kompas Digital Live")
        st.caption("Gerakkan HP kamu untuk mendeteksi arah mata angin (membutuhkan sensor Magnetometer HP)")
        
        compass_html = """
        <div style="text-align: center; font-family: sans-serif; padding: 10px; background: #1a1a2e; color: #fff; border-radius: 12px;">
            <h2 id="heading" style="color: #4eacc5; margin-bottom: 5px;">0° --</h2>
            <div id="compass" style="width: 150px; height: 150px; border: 4px solid #4eacc5; border-radius: 50%; margin: 10px auto; position: relative; transition: transform 0.2s ease-out;">
                <div style="position: absolute; top: 5px; left: 50%; transform: translateX(-50%); font-weight: bold; color: #ff4b4b;">N</div>
            </div>
            <button onclick="startCompass()" style="padding: 8px 16px; background: #4eacc5; border: none; color: white; border-radius: 6px; cursor: pointer; font-weight: bold;">Aktifkan Sensor Kompas</button>
        </div>

        <script>
        function startCompass() {
            if (window.DeviceOrientationEvent) {
                window.addEventListener('deviceorientation', function(e) {
                    let alpha = e.alpha || e.webkitCompassHeading;
                    if (alpha !== null) {
                        let heading = Math.round(alpha);
                        let dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
                        let dir = dirs[Math.round(heading / 45) % 8];
                        document.getElementById('heading').innerText = heading + "° " + dir;
                        document.getElementById('compass').style.transform = "rotate(" + (-heading) + "deg)";
                    }
                }, true);
            } else {
                alert("Sensor kompas tidak didukung di perangkat/browser ini.");
            }
        }
        </script>
        """
        components.html(compass_html, height=280)

        st.divider()
        st.subheader("🚨 Sinyal Darurat Audio SOS")
        st.caption("Bunyikan suara peluit frekuensi tinggi (2000Hz) untuk menarik perhatian Tim SAR di sekitar.")

        sound_sos_html = """
        <div style="text-align: center; padding: 10px; background: #222; border-radius: 12px; color: white;">
            <button onclick="playWhistle()" style="padding: 12px 24px; background: #ff4b4b; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-right: 10px;">🔊 Bunyikan Peluit SOS</button>
            <button onclick="stopWhistle()" style="padding: 12px 24px; background: #555; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">⏹️ Matikan</button>
        </div>

        <script>
        let audioCtx, osc;
        function playWhistle() {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (osc) osc.stop();
            osc = audioCtx.createOscillator();
            osc.type = 'sine';
            osc.frequency.value = 2000;
            osc.connect(audioCtx.destination);
            osc.start();
        }
        function stopWhistle() {
            if (osc) { osc.stop(); osc = null; }
        }
        </script>
        """
        components.html(sound_sos_html, height=100)

    # ---------------- TAB 3: PANDUAN SURVIVAL ----------------
    with tab_guide:
        st.subheader("📖 Buku Panduan Survival Darurat (Offline)")
        
        with st.expander("🐍 Pertolongan Pertama: Gigitan Ular & Serangga Beracun", expanded=True):
            st.markdown("""
            1. **Jangan Panik & Minimalkan Gerakan:** Semakin banyak bergerak, semakin cepat racun menyebar via pembuluh getah bening.
            2. **Imobilisasi Area Gigitan:** Ambil dua bilah kayu tebal, pasang di bagian atas & bawah sendi luka, lalu ikat longgar dengan kain (seperti membidai patah tulang).
            3. **JANGAN Diisap / Dipotong:** Jangan pernah mengisap darah atau menoreh luka dengan pisau.
            4. **Posisikan Lebih Rendah dari Jantung:** Biarkan area yang tergigit berada di posisi yang lebih rendah dari posisi dada.
            """)

        with st.expander("💧 Cara Menemukan & Memurnikan Air Minum"):
            st.markdown("""
            1. **Cari Sumber Air:** Ikuti arah gravitasi ke lembah/jurang, amati kumpulan serangga/burung, atau cari lekukan batu.
            2. **Air Embun Pagi:** Sapukan kain/kaos bersih ke dedaunan di pagi hari, lalu peras kain tersebut ke dalam wadah.
            3. **Penyaringan Sederhana:** Gunakan botol bekas dipotong, isi berturut-turut dari bawah ke atas: *kain - arang kayu - pasir halus - kerikil kecil*.
            4. **Wajib Rebus:** Rebus air sampai mendidih setidaknya selama **3-5 menit** untuk membunuh bakteri & parasit.
            """)

        with st.expander("⛺ Panduan Membuat Tempat Berlindung (Shelter) Darurat"):
            st.markdown("""
            1. **Pilih Lokasi:** Hindari dasar lembah kering (risiko banjir bandang) dan bawah pohon lapuk/kelapa (risiko dahan jatuh).
            2. **Tipe Lean-To (Sandar Pohon):** Rebahkan satu dahan kayu tebal berukuran 2-3 meter ke batang pohon, susun ranting-ranting rapat di sampingnya membentuk atap.
            3. **Isolasi Lapisan Bawah:** Lapisi tanah tempat tidur kamu dengan daun kering/pakis setebal minimal 15-20 cm agar suhu dingin tanah tidak menyedot panas tubuh (*hipotermia*).
            """)

        with st.expander("🆘 Kode Sinyal Darurat Darat-ke-Udara (Helikopter/SAR)"):
            st.markdown("""
            Buat simbol besar di area terbuka (lapangan/puncak) menggunakan batu, kayu, atau pakaian berwarna kontras:
            * **`V`** : Butuh Bantuan (*Require Assistance*)
            * **`X`** : Butuh Bantuan Medis (*Require Medical Assistance*)
            * **`Y`** : Ya / Benar (*Yes*)
            * **`N`** : Tidak / Tidak BISA (*No*)
            """)