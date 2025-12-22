import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Ahi-AI Okul Yönetimi",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TASARIM: AHİLİK TEMASI ---
st.markdown("""
<style>
    .stApp {background-color: #FDFBF7;}
    .main-header {font-family: 'Helvetica', sans-serif; color: #5D4037; text-align: center; font-size: 3rem; font-weight: 700; text-shadow: 2px 2px 4px #D7CCC8;}
    .sub-header {color: #8D6E63; text-align: center; font-size: 1.5rem; font-style: italic; margin-bottom: 30px;}
    .stButton>button {background-color: #5D4037; color: #FFECB3; border-radius: 12px; border: 2px solid #3E2723; width: 100%;}
    .stButton>button:hover {background-color: #3E2723; color: white; transform: scale(1.02);}
    .metric-card {background-color: #fff; padding: 20px; border-radius: 10px; border-left: 5px solid #5D4037; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center;}
</style>
""", unsafe_allow_html=True)

# --- FONKSİYONLAR ---
def get_google_sheet_client():
    try:
        if "GCP_JSON" in st.secrets:
            json_creds = json.loads(st.secrets["GCP_JSON"], strict=False)
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
            client = gspread.authorize(creds)
            return client
    except:
        return None

def verileri_getir():
    client = get_google_sheet_client()
    if client:
        try:
            sheet = client.open("Ahi-Okul-Kayitlari").sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def kaydet(ad, senaryo, cevap, puan, sonuc):
    client = get_google_sheet_client()
    if client:
        try:
            sheet = client.open("Ahi-Okul-Kayitlari").sheet1
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([tarih, ad, senaryo[:50]+"...", cevap, puan, sonuc])
            return True
        except:
            return False
    return False

# --- YAN MENÜ ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1542353457-4f1074e2a87c?w=600&auto=format&fit=crop&q=60")
    st.markdown("### 🔑 Ahi Kapısı")
    
    secim = st.radio("Gitmek İstediğiniz Yer:", ["Öğrenci Girişi", "Yönetici Paneli"])
    
    st.divider()
    
    # Yönetici Şifresi
    yonetici_aktif = False
    if secim == "Yönetici Paneli":
        sifre = st.text_input("Yönetici Şifresi:", type="password")
        if sifre == "ahi123": # BURADAKİ ŞİFREYİ KULLANACAKSIN
            yonetici_aktif = True
            st.success("Giriş Başarılı: Başöğretmen")
        elif sifre:
            st.error("Hatalı Şifre!")
    
    # API Kontrol
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash')

# --- EKRAN 1: YÖNETİCİ PANELİ (Grafikler) ---
if yonetici_aktif:
    st.markdown('<div class="main-header">📊 Yönetici ve İstatistik Odası</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Okulun genel durum raporu buradadır.</div>', unsafe_allow_html=True)
    
    df = verileri_getir()
    
    if not df.empty:
        # İstatistik Kartları
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><h3>Toplam Öğrenci</h3><h1>{len(df)}</h1></div>', unsafe_allow_html=True)
        
        kabul_sayisi = len(df[df['SONUÇ'] == 'KABUL'])
        ret_sayisi = len(df[df['SONUÇ'] == 'RET'])
        
        c2.markdown(f'<div class="metric-card"><h3>Kabul Edilen</h3><h1 style="color:green">{kabul_sayisi}</h1></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><h3>Elenen</h3><h1 style="color:red">{ret_sayisi}</h1></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Grafikler
        col_grafik, col_tablo = st.columns([1, 2])
        
        with col_grafik:
            st.markdown("### 📈 Başarı Oranı")
            chart_data = pd.DataFrame({
                'Durum': ['Kabul', 'Ret'],
                'Sayı': [kabul_sayisi, ret_sayisi]
            })
            st.bar_chart(chart_data.set_index('Durum'))
            
        with col_tablo:
            st.markdown("### 📋 Son Kayıtlar")
            st.dataframe(df.tail(10)) # Son 10 kişiyi göster
            
    else:
        st.info("Henüz hiç kayıt yok hocam. Öğrenciler mülakata girince burası dolacak.")

# --- EKRAN 2: ÖĞRENCİ MÜLAKAT (Eski Sistem) ---
else:
    st.markdown('<div class="main-header">🕌 Ahi-AI: Sanal Usta</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">"Hak ile sabır dileyip bize gelen bizdendir."</div>', unsafe_allow_html=True)
    
    if secim == "Yönetici Paneli" and not yonetici_aktif:
        st.warning("Lütfen sol taraftan şifrenizi giriniz.")
    else:
        ad_soyad = st.text_input("👤 Adınız Soyadınız:", placeholder="Örn: Yunus Emre")
        
        if ad_soyad:
            if "senaryo" not in st.session_state: st.session_state.senaryo = ""

            if st.button("🎲 Yeni Senaryo Çek"):
                with st.spinner("Usta düşünüyor..."):
                    prompt = "Sen Ahilik ustasısın. Otelcilik öğrencisine dürüstlük ve sabır testi için kısa bir kriz senaryosu yaz."
                    res = model.generate_content(prompt)
                    st.session_state.senaryo = res.text
                    st.rerun()

            if st.session_state.senaryo:
                st.info(st.session_state.senaryo)
                cevap = st.text_area("Cevabınız:", height=150)
                
                if st.button("⚖️ Usta'ya Gönder"):
                    if cevap:
                        with st.spinner("Değerlendiriliyor..."):
                            degerlendirme = f"Senaryo: {st.session_state.senaryo}\nCevap: {cevap}\nAhilik ustası gibi puanla (0-100), SONUÇ: KABUL veya RET yaz, ve kısa öğüt ver."
                            sonuc = model.generate_content(degerlendirme).text
                            st.write(sonuc)
                            
                            karar = "KABUL" if "KABUL" in sonuc else ("RET" if "RET" in sonuc else "BELİRSİZ")
                            kaydet(ad_soyad, st.session_state.senaryo, cevap, sonuc, karar)
                            st.success("Kaydedildi!")
                            if "KABUL" in karar: st.balloons()
