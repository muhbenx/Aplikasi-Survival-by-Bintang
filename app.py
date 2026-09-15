import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
from PIL import Image
from google import genai
import os

# 1. SETTING HALAMAN
st.set_page_config(
    page_title="Offline Survival Suite & AI Assistant",
    page_icon="🏕️",
    layout="wide"
)

# 2. INJEKSI PWA OFFLINE
pwa_code = """
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    const swCode = `
      const CACHE_NAME = 'survival-app-v3';
      self.addEventListener('install', event => {
        event.waitUntil(
          caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(['/']);
          })
        );
      });
      self.addEventListener('fetch', event => {
        event.respondWith(
          caches.match(event.request).then(response => {
            return response || fetch(event.request);
          })
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

st.title("🏕️ Offline Survival Suite & AI Assistant")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📸 AI Object Counter", 
    "🗺️ GPS & Peta Visual", 
    "🧭 Kompas & SOS", 
    "🔊 Peluit Darurat", 
    "📖 Panduan Survival"
])

# --- TAB 1: AI OBJECT COUNTER ---
with tab1:
    st.header("📸 Hitung Barang Bawaan (AI Counter)")
    st.write("Foto/upload barang logistik kamu untuk dihitung otomatis menggunakan Gemini AI.")
    
    api_key = st.text_input("Masukkan Google AI Studio API Key:", type="password")
    
    target_object = st.text_input(
        "Ingin menghitung barang tertentu saja? (Opsional)", 
        placeholder="Contoh: Mie instan, Botol air, Kaleng (Kosongkan jika ingin hitung semua)"
    )
    
    uploaded_file = st.file_uploader("Upload Foto Logistics/Barang", type=["jpg", "jpeg", "png"])
    
    if uploaded_file and api_key:
        image = Image.open(uploaded_file)
        st.image(image, caption="Foto Barang", use_container_width=True)
        
        if st.button("Hitung Barang"):
            with st.spinner("Menganalisis foto..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    if target_object.strip():
                        prompt = f"Tolong hitung secara spesifik jumlah '{target_object}' yang ada di dalam foto ini. Sebutkan jumlah totalnya dan beri rincian singkat."
                    else:
                        prompt = "Tolong hitung dan sebutkan rincian jumlah seluruh barang/logistik survival yang ada di foto ini secara detail."
                        
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[image, prompt]
                    )
                    st.success("Hasil Analisis:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Gagal memproses gambar: {e}")

# --- TAB 2: GPS & PETA VISUAL ---
with tab2:
    st.header("🗺️ Peta Visual & Lokasi GPS")
    
    st.subheader("1. Lokasi Live Satelit HP")
    gps_html = """
    <div style="background-color: #222; padding: 15px; border-radius: 8px; color: white;">
        <button onclick="getLocation()" style="padding: 10px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">Dapatkan Koordinat & Altitudo</button>
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
    st.info("Peta ini merender data visual online. Buka/zoom area gunung sebelum berangkat agar tersimpan di cache HP.")
    
    default_lat, default_lon = -6.8951, 107.6339
    m = folium.Map(location=[default_lat, default_lon], zoom_start=12)
    folium.Marker([default_lat, default_lon], popup="Pos Survival", tooltip="Lokasi Awal").add_to(m)
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
