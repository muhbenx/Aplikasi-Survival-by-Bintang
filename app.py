import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from google import genai

# 1. SETTING HALAMAN
st.set_page_config(
    page_title="Offline Survival Suite & AI Assistant",
    page_icon="📦",
    layout="wide"
)

# 2. INJEKSI PWA FULL OFFLINE (SERVICE WORKER & MANIFEST)
pwa_code = """
<script>
// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    const swCode = `
      const CACHE_NAME = 'survival-pwa-v12';
      const urlsToCache = [
        '/',
        'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
        'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
        'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
      ];

      self.addEventListener('install', event => {
        event.waitUntil(
          caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(urlsToCache);
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

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.title("⚙ Config")
    api_key = st.text_input("Gemini API Key:", type="password", placeholder="Paste API Key di sini...")
    st.caption("Powered by Gemini 3.6 Flash Vision AI")
    st.info("💡 **Mode Offline:** Peta GPS, Peluit SOS, dan Buku Panduan tetap bekerja tanpa internet!")

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
    st.caption("Automated Visual Inventory & Overlapping Object Detector (Membutuhkan Koneksi Internet)")
    
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
            with st.spinner("Menganalisis objek dengan AI secara presisi..."):
                try:
                    client = genai.Client(api_key=api_key)
                    img_wadah = Image.open(foto_wadah)
                    
                    if "Spesifik" in mode and foto_sampel:
                        img_sampel = Image.open(foto_sampel)
                        prompt = (
                            "Gambar pertama adalah contoh sampel objek target. "
                            "Gambar kedua adalah foto wadah/tempat penyimpanan. "
                            "Instruksi Khusus:\n"
                            "1. FOKUS UTAMA: Hitung HANYA objek di DALAM WADAH pada gambar kedua yang SAMA JENISNYA dengan gambar pertama. Perhatikan posisi penumpukan/tumpang tindih dengan sangat teliti agar hitungan tepat.\n"
                            "2. Berikan jumlah total angka yang pasti untuk barang DI DALAM WADAH.\n"
                            "3. OPSIONAL: Jika ada objek serupa di luar wadah, sebutkan secara terpisah di bagian 'Catatan Tambahan (Luar Wadah)'."
                        )
                        contents = [img_sampel, img_wadah, prompt]
                    else:
                        prompt = (
                            "Tolong analisis dan hitung objek dalam foto ini secara sangat teliti dengan aturan ketat berikut:\n\n"
                            "1. **FOKUS UTAMA (Barang di DALAM Wadah/Box):**\n"
                            "   - Hitung seluruh barang (seperti pulpen, spidol, pensil, dll.) yang secara fisik berada DI DALAM wadah putih.\n"
                            "   - Hitung dari kiri ke kanan secara cermat, perhatikan bagian ujung atau klip pulpen agar tidak ada yang terhitung ganda atau terlewat.\n"
                            "   - Berikan **JUMLAH TOTAL UTAMA** untuk isi wadah.\n\n"
                            "2. **OPSIONAL (Barang di LUAR Wadah):**\n"
                            "   - Buat bagian terpisah berjudul '📌 Catatan Tambahan (Objek Luar Wadah)' jika ada objek lain di luar wadah (misalnya meteran gulung, meja, dll.). Jangan gabungkan jumlah objek luar ini ke dalam Total Utama Wadah."
                        )
                        contents = [img_wadah, prompt]
                        
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=contents
                    )
                    st.success("Hasil Perhitungan AI:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Gagal memproses perhitungan: {e}")

# --- TAB 2: GPS & PETA VISUAL (SUPPORT LIVE TRACKING & OFFLINE) ---
with tab2:
    st.header("🗺️ Peta Live GPS (Direct Tracking)")
    st.caption("Peta terhubung langsung dengan GPS HP secara real-time. Tetap mendeteksi koordinat meskipun offline.")
    
    leaflet_direct_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            #map { height: 450px; width: 100%; border-radius: 10px; }
            .info-box { background: #222; color: #fff; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-family: sans-serif; font-size: 14px; }
            button { background: #ff4b4b; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }
        </style>
    </head>
    <body style="margin: 0; background-color: transparent;">
        <div class="info-box">
            <button onclick="locateMe()">📍 Kunci Titik Lokasi Saya</button>
            <span id="gps-status" style="margin-left: 10px;">Mencari sinyal GPS HP...</span>
        </div>
        <div id="map"></div>

        <script>
            var map = L.map('map').setView([0, 0], 2);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);

            var marker, circle;

            function onLocationFound(e) {
                var radius = e.accuracy / 2;

                if (marker) {
                    map.removeLayer(marker);
                    map.removeLayer(circle);
                }

                marker = L.marker(e.latlng).addTo(map)
                    .bindPopup("<b>Posisi Kamu Sekarang</b><br>Akurasi sekitar " + Math.round(radius) + " meter.").openPopup();

                circle = L.circle(e.latlng, radius).addTo(map);

                document.getElementById('gps-status').innerHTML = 
                    "<b>Lat:</b> " + e.latlng.lat.toFixed(6) + " | <b>Lon:</b> " + e.latlng.lng.toFixed(6) + " (Akurasi: " + Math.round(radius) + "m)";
            }

            function onLocationError(e) {
                document.getElementById('gps-status').innerHTML = "<span style='color: #ff6b6b;'>Gagal mendapat lokasi: " + e.message + " (Pastikan GPS HP aktif)</span>";
            }

            function locateMe() {
                document.getElementById('gps-status').innerText = "Menghubungkan ke satelit GPS...";
                map.locate({setView: true, maxZoom: 17, watch: true, enableHighAccuracy: true});
            }

            map.on('locationfound', onLocationFound);
            map.on('locationerror', onLocationError);

            locateMe();
        </script>
    </body>
    </html>
    """
    components.html(leaflet_direct_html, height=520)

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
