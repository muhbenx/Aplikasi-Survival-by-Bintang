import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
from PIL import Image
from google import genai

# 1. SETTING HALAMAN
st.set_page_config(
    page_title="Offline Survival Suite & AI Assistant",
    page_icon="📦",
    layout="wide"
)

# 2. INJEKSI PWA OFFLINE
pwa_code = """
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    const swCode = `
      const CACHE_NAME = 'survival-app-v6';
      self.addEventListener('install', event => {
        event.waitUntil(
          caches.open(CACHE_NAME).then(cache => cache.addAll(['/']))
        );
      });
      self.addEventListener('fetch', event => {
        event.respondWith(
          caches.match(event.request).then(response => response || fetch(event.request))
        );
      });
    `;
    const blob = new Blob([swCode], {type: 'application/javascript'});
    const swUrl = URL.createObjectURL(blob);
    navigator.serviceWorker.register(swUrl);
  });
}
</script>
"""
components.html(pwa_code, height=0)

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.title("⚙ Config")
    api_key = st.text_input("Gemini API Key:", type="password", placeholder="Paste API Key di sini...")
    st.caption("Powered by Gemini 2.5 Flash Vision AI")

# --- TAB NAVIGATION ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 AI Object Counter", 
    "🗺️ GPS & Peta Visual", 
    "🧭 Kompas & SOS", 
    "🔊 Peluit Darurat", 
    "📖 Panduan Survival"
])

# --- TAB 1: AI OBJECT COUNTER ---
with tab1:
    st.title("📦 AI Object Counter")
    st.caption("Automated Visual Inventory & Overlapping Object Detector")
    
    st.subheader("🎯 Mode Perhitungan")
    mode = st.radio(
        "Pilih Mode:",
        ["Hitung Objek Spesifik (Sesuai Foto Sampel)", "Hitung TOTAL SEMUA Objek dalam Wadah"],
        label_visibility="collapsed"
    )
    
    foto_sampel = None
    foto_wadah = None
    
    if "Spesifik" in mode:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**1. Sampel Objek**")
            foto_sampel = st.file_uploader("Upload foto sampel", type=["jpg", "jpeg", "png"], key="sampel")
            if foto_sampel:
                st.image(Image.open(foto_sampel), use_container_width=True)
                
        with col2:
            st.write("**2. Isi Wadah / Box**")
            foto_wadah = st.file_uploader("Upload foto wadah terisi", type=["jpg", "jpeg", "png"], key="wadah_spesifik")
            if foto_wadah:
                st.image(Image.open(foto_wadah), use_container_width=True)
    else:
        st.write("**Foto Isi Wadah / Box / Kumpulan Barang**")
        foto_wadah = st.file_uploader("Upload foto wadah/kumpulan barang", type=["jpg", "jpeg", "png"], key="wadah_total")
        if foto_wadah:
            st.image(Image.open(foto_wadah), use_container_width=True)
            
    st.write("")
    if st.button("✨ Mulai Perhitungan AI", use_container_width=True):
        if not api_key:
            st.error("Masukkan Gemini API Key terlebih dahulu di Sidebar Config!")
        elif not foto_wadah:
            st.error("Upload foto barang/wadah terlebih dahulu!")
        elif "Spesifik" in mode and not foto_sampel:
            st.error("Untuk mode Objek Spesifik, kamu harus mengunggah Foto Sampel!")
        else:
            with st.spinner("Menganalisis objek dengan AI..."):
                try:
                    client = genai.Client(api_key=api_key)
                    img_wadah = Image.open(foto_wadah)
                    
                    if "Spesifik" in mode and foto_sampel:
                        img_sampel = Image.open(foto_sampel)
                        prompt = (
                            "Gambar pertama adalah contoh sampel objek target. "
                            "Gambar kedua adalah kumpulan objek/wadah. "
                            "Tolong hitung secara akurat berapa jumlah total objek pada gambar kedua yang SAMA JENISNYA dengan objek sampel di gambar pertama. "
                            "Sebutkan jumlah angka pastinya dan beri rincian analisisnya."
                        )
                        contents = [img_sampel, img_wadah, prompt]
                    else:
                        prompt = (
                            "Tolong hitung total seluruh barang/objek yang ada di dalam foto ini secara presisi. "
                            "Sebutkan total angka keseluruhannya dan buatkan daftar rincian barang yang terdeteksi."
                        )
                        contents = [img_wadah, prompt]
                        
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents
                    )
                    st.success("Hasil Perhitungan AI:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Gagal memproses perhitungan: {e}")

# --- TAB 2: GPS & PETA VISUAL ---
with tab2:
    st.header("🗺️ Peta Visual & Lokasi GPS")
    
    # Inisialisasi Session State untuk simpan lokasi pengguna
    if 'user_lat' not in st.session_state:
        st.session_state['user_lat'] = -6.8951
    if 'user_lon' not in st.session_state:
        st.session_state['user_lon'] = 107.6339
    if 'location_fetched' not in st.session_state:
        st.session_state['location_fetched'] = False

    st.subheader("1. Lokasi Live Satelit HP")
    
    # Input manual koordinat jika pengguna ingin menyesuaikan langsung
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        custom_lat = st.number_input("Latitude", value=st.session_state['user_lat'], format="%.6f")
    with col_input2:
        custom_lon = st.number_input("Longitude", value=st.session_state['user_lon'], format="%.6f")

    st.session_state['user_lat'] = custom_lat
    st.session_state['user_lon'] = custom_lon

    gps_html = """
    <div style="background-color: #222; padding: 15px; border-radius: 8px; color: white;">
        <button onclick="getLocation()" style="padding: 10px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">📍 Dapatkan Koordinat & Altitudo Presisi</button>
        <p id="lat" style="margin-top:10px;">Latitude: -</p>
        <p id="lon">Longitude: -</p>
        <p id="alt">Altitudo: -</p>
    </div>
    <script>
    function getLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(pos) {
          document.getElementById("lat").innerHTML = "Latitude: " + pos.coords.latitude;
          document.getElementById("lon").innerHTML = "Longitude: " + pos.coords.longitude;
          document.getElementById("alt").innerHTML = "Altitudo: " + (pos.coords.altitude ? pos.coords.altitude.toFixed(1) + " mdpl" : "Satelit tidak mendeteksi altitudo");
        }, function(err) { alert("Akses GPS ditolak/gagal: " + err.message); }, {enableHighAccuracy: true});
      }
    }
    </script>
    """
    components.html(gps_html, height=160)
    
    st.subheader("2. Peta Topografi / Visual (Folium)")
    st.info("Salin nilai Latitude & Longitude dari tombol di atas ke kolom input angka jika ingin memindahkan fokus peta secara tepat ke posisimu.")
    
    # Peta merender berdasarkan titik latitude & longitude aktif
    m = folium.Map(location=[st.session_state['user_lat'], st.session_state['user_lon']], zoom_start=15)
    folium.Marker(
        [st.session_state['user_lat'], st.session_state['user_lon']], 
        popup="Posisi Kamu", 
        tooltip="Lokasi Terdeteksi",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    
    st_folium(m, width=700, height=400)

# --- TAB 3: KOMPAS & SOS ---
with tab3:
    st.header("🧭 Kompas & Teks Darurat SOS")
    st.write("Teks darurat untuk dikirim lewat SMS biasa:")
    st.code("SOS! Saya membutuhkan bantuan darurat di lokasi gunung. Harap lacak sinyal koordinat saya.", language="text")

# --- TAB 4: PELUIT AUDIO ---
with tab4:
    st.header("🔊 Peluit SOS Audio High-Frequency")
    whistle_html = """
    <div style="text-align: center; padding: 10px;">
        <button onclick="playSOS()" style="padding: 15px 25px; font-size: 16px; background-color: #f44336; color: white; border: none; border-radius: 8px; cursor: pointer;">🔊 Bunyikan Peluit SOS (Morse)</button>
    </div>
    <script>
    function playSOS() {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function tone(freq, duration, delay) {
            setTimeout(() => {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.value = freq;
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + duration);
            }, delay);
        }
        let now = 0;
        [100, 100, 100].forEach(d => { tone(3000, 0.1, now); now += 200; });
        now += 300;
        [300, 300, 300].forEach(d => { tone(3000, 0.3, now); now += 400; });
        now += 300;
        [100, 100, 100].forEach(d => { tone(3000, 0.1, now); now += 200; });
    }
    </script>
    """
    components.html(whistle_html, height=100)

# --- TAB 5: PANDUAN SURVIVAL ---
with tab5:
    st.header("📖 Buku Panduan Survival Lapangan")
    with st.expander("💧 Cara Menjernihkan Air"):
        st.write("1. Endapkan lumpur.\n2. Saring memakai kain/kaos bersih.\n3. Rebus hingga mendidih minimal 1 menit.")
    with st.expander("🔥 Cara Membuat Api Tanpa Korek"):
        st.write("1. Gunakan teknik gesekan kayu kering.\n2. Manfaatkan pemantik busi/batu api.\n3. Fokuskan sinar matahari dengan kaca pembesar/lensa HP.")
    with st.expander("⛺ Pertolongan Pertama Hipotermia"):
        st.write("1. Ganti pakaian basah dengan baju kering.\n2. Bungkus dengan emergency blanket.\n3. Beri minuman hangat manis jika sadar.")
