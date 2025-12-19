import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Ahi-AI Okul Yönetimi",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TASARIM: AHİLİK TEMASI (CSS) ---
st.markdown("""
<style>
    /* Genel Arka Plan */
    .stApp {
        background-color: #FDFBF7;
    }
    
    /* Başlık Stili */
    .main-header {
        font-family: 'Helvetica', sans-serif;
        color: #5D4037; /* Koyu Kahve */
        text-align: center;
        font-size: 3.5rem;
        font-weight: 700;
        padding-top: 20px;
        text-shadow: 2px 2px 4px #D7CCC8;
    }
    
    /* Alt Başlık */
    .sub-header {
        color: #8D6E63;
        text-align: center;
        font-size: 1.5rem;
        font-style: italic;
        margin-bottom: 40px;
    }
    
    /* Buton Tasarımı */
    .stButton>button {
        background-color: #5D4037;
        color: #FFECB3;
        border-radius: 12px;
        border: 2px solid #3E2723;
        padding: 10px 24px;
        font-size: 18px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #3E2723;
        color: #FFFFFF;
        border-color: #FFD54F;
        transform: scale(1.02);
    }
    
    /* Sonuç Kartı Tasarımı */
    .result-card {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 15px;
        border-left: 10px solid #5D4037;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    
    /* Senaryo Kutusu */
    .scenario-box {
        background-color: #EFEBE9;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #D7CCC8;
        color: #3E2723;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- FONKSİYONLAR ---
def get_google_sheet_client():
    try:
        # strict=False ekleyerek küçük hataları görmezden gel
        if "GCP_JSON" in st.secrets:
            json_creds = json.loads(st.secrets["GCP_JSON"], strict=False)
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
            client = gspread.authorize(creds)
            return client
        else:
            return None # JSON yoksa sessizce geç (Sadece AI çalışsın)
    except Exception as e:
        st.error(f"Veritabanı Hatası: {e}")
        return None

def kaydet(ad, senaryo, cevap, puan, sonuc):
    client = get_google_sheet_client()
    if client:
        try:
            sheet = client.open("Ahi-Okul-Kayitlari").sheet1
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([tarih, ad, senaryo[:100]+"...", cevap, puan, sonuc])
            return True
        except:
            return False
    return False

# --- YAN MENÜ ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1542353457-4f1074e2a87c?w=600&auto=format&fit=crop&q=60", caption="Geleceğin Ustaları")
    st.markdown("### 🔑 Giriş Kapısı")
    st.info("Burası edep, ahlak ve sanatın buluştuğu dijital meydandır.")
    
    st.divider()
    ad_soyad = st.text_input("👤 Adınız Soyadınız:", placeholder="Örn: Yunus Emre")
    
    # API Kontrol
    api_durum = False
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash')
        api_durum = True

# --- ANA EKRAN ---
st.markdown('<div class="main-header">🕌 Ahi-AI: Sanal Usta</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">"Hak ile sabır dileyip bize gelen bizdendir."</div>', unsafe_allow_html=True)

if not api_durum:
    st.error("⚠️ Sistem anahtarı (API Key) bulunamadı. Lütfen ayarlardan ekleyin.")
elif not ad_soyad:
    st.warning("👈 Lütfen sol taraftan isminizi girerek divana buyurun.")
else:
    # Oturum Yönetimi
    if "senaryo" not in st.session_state:
        st.session_state.senaryo = ""

    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        st.markdown("### 📜 1. İmtihan: Kriz Anı")
        st.write("Usta sana zorlu bir müşteri veya durum verecek.")
        
        if st.button("🎲 Yeni Senaryo Çek"):
            with st.spinner("Usta düşünüyor..."):
                prompt = """
                Sen Ahilik kültürüne hakim, bilge bir otelcilik ustasısın.
                Öğrencinin ahlakını, sabrını ve dürüstlüğünü test edecek
                kısa, vurucu ve gerçekçi bir otel/hizmet senaryosu yaz.
                Sadece olayı anlat.
                """
                res = model.generate_content(prompt)
                st.session_state.senaryo = res.text
                st.rerun()
        
        if st.session_state.senaryo:
            st.markdown(f'<div class="scenario-box">{st.session_state.senaryo}</div>', unsafe_allow_html=True)

    with col2:
        if st.session_state.senaryo:
            st.markdown("### ✍️ 2. Cevap: Senin Kararın")
            cevap = st.text_area("Bu durumda ne yaparsın?", height=200, placeholder="Dürüstçe ve edeple cevabını yaz...")
            
            if st.button("⚖️ Usta'ya Arz Et"):
                if cevap:
                    with st.spinner("Terazi tartılıyor, defter yazılıyor..."):
                        # 1. AI Değerlendirmesi
                        degerlendirme_prompt = f"""
                        Senaryo: {st.session_state.senaryo}
                        Öğrenci Cevabı: {cevap}
                        
                        Lütfen bir Ahi Ustası ağzıyla değerlendir.
                        1. Puan (0-100)
                        2. Karar (KABUL veya RET)
                        3. Kısa ve hikmetli bir öğüt/yorum.
                        
                        Yanıtı şu formatta ver:
                        **PUAN:** [Sayı]
                        **KARAR:** [KABUL/RET]
                        **ÖĞÜT:** [Yorumun]
                        """
                        sonuc_text = model.generate_content(degerlendirme_prompt).text
                        
                        # 2. Sonucu Göster (Özel Kart Tasarımı)
                        st.markdown(f"""
                        <div class="result-card">
                            {sonuc_text.replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 3. Kayıt (Basit parsing)
                        karar_kisa = "KABUL" if "KABUL" in sonuc_text else ("RET" if "RET" in sonuc_text else "BELİRSİZ")
                        if kaydet(ad_soyad, st.session_state.senaryo, cevap, sonuc_text, karar_kisa):
                            st.success(f"✅ Sonuçlar '{ad_soyad}' kütüğüne işlendi.")
                            if "KABUL" in karar_kisa:
                                st.balloons()
                            else:
                                st.snow() # Ret yerse kar yağsın (soğuk duş etkisi)
                        else:
                            st.warning("Sonuç gösterildi ancak deftere (Excel) yazılamadı.")
                else:
                    st.warning("Boş kağıt verme evlat, bir şeyler yaz.")
