import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# --- SAYFA AYARLARI (GÖRSEL MAKYAJ) ---
st.set_page_config(page_title="Ahi-AI Okul Yönetimi", page_icon="🕌", layout="wide")

# --- CSS İLE ÖZEL TASARIM ---
st.markdown("""
<style>
    .main-header {font-size: 3rem; color: #8B4513; text-align: center; font-weight: bold;}
    .sub-header {font-size: 1.5rem; color: #A0522D; text-align: center; margin-bottom: 20px;}
    .stButton>button {background-color: #8B4513; color: white; border-radius: 10px; width: 100%;}
    .success-box {padding: 20px; background-color: #f0f9ff; border-left: 5px solid #0099ff; border-radius: 5px;}
    .report-card {background-color: #fcfcfc; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

# --- FONKSİYONLAR ---
def get_google_sheet_client():
    try:
        # Secrets'tan JSON verisini al ve oku
        json_creds = json.loads(st.secrets["GCP_JSON"])
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Veritabanı Bağlantı Hatası: {e}")
        return None

def kaydet(ad, senaryo, cevap, puan, sonuc):
    client = get_google_sheet_client()
    if client:
        try:
            # Tablo adının doğru olduğundan emin ol: "Ahi-Okul-Kayitlari"
            sheet = client.open("Ahi-Okul-Kayitlari").sheet1
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Satır ekle
            sheet.append_row([tarih, ad, senaryo[:100]+"...", cevap, puan, sonuc])
            return True
        except Exception as e:
            st.error(f"Kayıt Hatası: {e}")
            return False
    return False

# --- YAN MENÜ ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=800&auto=format&fit=crop&q=60")
    st.markdown("### 🔑 Ahi-AI Paneli")
    st.info("Bu sistem, Ahilik değerlerini modern otelcilik eğitimiyle birleştirir.")
    
    st.divider()
    
    # Kullanıcıdan Ad Soyad İste (Kayıt için gerekli)
    ad_soyad = st.text_input("Öğrenci Adı Soyadı:", placeholder="Örn: Ahmet Yılmaz")
    
    # API Anahtarı Kontrolü
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash')
        api_durum = True
    else:
        st.error("API Anahtarı Bulunamadı!")
        api_durum = False

# --- ANA EKRAN ---
st.markdown('<div class="main-header">🕌 Ahi-AI: Sanal Usta</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">"Eline, beline, diline sahip ol."</div>', unsafe_allow_html=True)

if api_durum and ad_soyad:
    
    if "senaryo" not in st.session_state:
        st.session_state.senaryo = ""

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 1. Adım: Kriz Anı")
        if st.button("🎲 Senaryo Çek", type="primary"):
            with st.spinner("Usta düşünüyor..."):
                prompt = """
                Sen Ahilik geleneğine sahip bir otelcilik ustasısın.
                Öğrenciyi zorlayacak, dürüstlük ve sabır gerektiren,
                kısa ve gerçekçi bir otelcilik senaryosu yaz.
                Sadece olayı anlat.
                """
                res = model.generate_content(prompt)
                st.session_state.senaryo = res.text
                st.rerun()

    with col2:
        if st.session_state.senaryo:
            st.info(f"📋 **SENARYO:**\n\n{st.session_state.senaryo}")
            
            cevap = st.text_area("Bu durumda ne yaparsın?", height=150, placeholder="Cevabınızı buraya yazın...")
            
            if st.button("⚖️ Değerlendir ve Kaydet"):
                if cevap:
                    with st.spinner("Ahi Usta değerlendiriyor ve deftere işliyor..."):
                        # Yapay Zeka Değerlendirmesi
                        degerlendirme_prompt = f"""
                        Senaryo: {st.session_state.senaryo}
                        Cevap: {cevap}
                        
                        Lütfen şu formatta yanıt ver:
                        PUAN: [0-100 arası bir sayı ver]
                        SONUÇ: [KABUL veya RET yaz]
                        YORUM: [Detaylı yorumunu yaz]
                        """
                        sonuc_raw = model.generate_content(degerlendirme_prompt).text
                        
                        # Sonucu ekrana yaz
                        st.markdown('<div class="report-card">', unsafe_allow_html=True)
                        st.markdown(sonuc_raw)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Kayıt İşlemi (Basit parsing)
                        puan_ozet = "Detaylar Rapor'da"
                        karar_ozet = "BELİRSİZ"
                        if "KABUL" in sonuc_raw: karar_ozet = "KABUL"
                        elif "RET" in sonuc_raw: karar_ozet = "RET"
                        
                        if kaydet(ad_soyad, st.session_state.senaryo, cevap, sonuc_raw, karar_ozet):
                            st.success(f"✅ Sonuçlar '{ad_soyad}' adına başarıyla kaydedildi!")
                            st.balloons()
                        else:
                            st.warning("Değerlendirme yapıldı ama sisteme kaydedilemedi. (Ayarları kontrol edin)")

                else:
                    st.warning("Lütfen bir cevap yazın.")
else:
    if not ad_soyad:
        st.warning("👈 Lütfen sol menüden Adınızı Soyadınızı girerek sisteme giriş yapın.")
