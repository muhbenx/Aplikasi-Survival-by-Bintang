import streamlit as st
import streamlit.components.v1 as components

# 1. SETTING HALAMAN
st.set_page_config(
    page_title="Survival Suite Offline",
    page_icon="🏕️",
    layout="wide"
)

# 2. INJEKSI SERVICE WORKER (Bikin App Bisa Dibuka 100% Offline dari Cache HP)
pwa_code = """
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    const swCode = `
      const CACHE_NAME = 'survival-app-v1';
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
    navigator.serviceWorker.register(swUrl).then(function(reg) {
      console.log('Offline Cache Ready!');
    });
  });
}
</script>
"""
components.html(pwa_code, height=0)

# 3. TAMPILAN UTAMA APLIKASI
st.title("🏕️ Offline Survival Suite")
st.caption("Aplikasi Darurat Field Survival - Standalone Offline")

tab1, tab2, tab3, tab4 = st.tabs(["📍 GPS & Altitudo", "🧭 Kompas & SOS", "🔊 Peluit Darurat", "📖 Panduan Survival"])

# TAB 1: GPS & ALTITUDO
with tab1:
    st.header("GPS & Ketinggian (Satelit)")
    st.info("Fitur ini menggunakan sensor GPS bawaan HP. Tidak butuh internet.")
    
    gps_html = """
    <div style="text-align: center; padding: 20px; border: 2px solid #4CAF50; border-radius: 10px;">
        <button onclick="getLocation()" style="padding: 10px 20px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">Dapatkan Lokasi Saya</button>
        <h3 id="lat">Latitude: -</h3>
        <h3 id="lon">Longitude: -</h3>
        <h3 id="alt">Altitudo (Ketinggian): -</h3>
        <p id="acc">Akurasi: -</p>
    </div>

    <script>
    function getLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError, {enableHighAccuracy: true});
      } else { 
        alert("GPS tidak didukung oleh browser ini.");
      }
    }

    function showPosition(position) {
      document.getElementById("lat").innerHTML = "Latitude: " + position.coords.latitude;
      document.getElementById("lon").innerHTML = "Longitude: " + position.coords.longitude;
      document.getElementById("alt").innerHTML = "Altitudo: " + (position.coords.altitude ? position.coords.altitude.toFixed(1) + " mdpl" : "Data satelit tidak tersedia");
      document.getElementById("acc").innerHTML = "Akurasi: ± " + position.coords.accuracy.toFixed(1) + " meter";
    }

    function showError(error) {
      alert("Gagal mengambil GPS: " + error.message);
    }
    </script>
    """
    components.html(gps_html, height=250)

# TAB 2: KOMPAS & SOS
with tab2:
    st.header("Sinyal Pesan SOS Darurat")
    st.write("Salin teks di bawah ini untuk dikirimkan via SMS biasa ke tim SAR / Kontak Darurat:")
    st.code("SOS! Saya membutuhkan bantuan darurat di lokasi saya. Harap lacak sinyal ini.", language="text")

# TAB 3: PELUIT AUDIO
with tab3:
    st.header("Peluit SOS Audio High-Frequency")
    st.write("Menggunakan frekuensi audio khusus HP untuk menarik perhatian.")
    
    whistle_html = """
    <div style="text-align: center; padding: 20px;">
        <button onclick="playSOS()" style="padding: 15px 30px; font-size: 18px; background-color: #f44336; color: white; border: none; border-radius: 8px; cursor: pointer;">🔊 Bunyikan Peluit SOS</button>
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
        // Pola Morse SOS (... --- ...)
        let now = 0;
        [100, 100, 100].forEach(d => { tone(3000, 0.1, now); now += 200; });
        now += 300;
        [300, 300, 300].forEach(d => { tone(3000, 0.3, now); now += 400; });
        now += 300;
        [100, 100, 100].forEach(d => { tone(3000, 0.1, now); now += 200; });
    }
    </script>
    """
    components.html(whistle_html, height=120)

# TAB 4: BUKU PANDUAN
with tab4:
    st.header("📖 Buku Panduan Survival Lapangan")
    with st.expander("💧 Cara Menjernihkan Air"):
        st.write("1. Endapkan lumpur.\n2. Saring memakai kain/kaos bersih.\n3. Rebus hingga mendidih minimal 1 menit.")
    with st.expander("🔥 Cara Membuat Api Tanpa Korek"):
        st.write("1. Gunakan teknik gesekan kayu kering.\n2. Manfaatkan pemantik busi/batu api.\n3. Fokuskan sinar matahari dengan kaca pembesar/lensa HP.")
    with st.expander("⛺ Pertolongan Pertama Hipotermia"):
        st.write("1. Ganti pakaian basah dengan baju kering.\n2. Bungkus dengan *emergency blanket*.\n3. Beri minuman hangat manis jika sadar.")
