import streamlit as st
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Ahi-AI Okul Sistemi", page_icon="🕌", layout="centered")

# --- BAŞLIK VE GİRİŞ ---
st.image("https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=800&auto=format&fit=crop&q=60", caption="Geleceğin Turizmcileri Burada Yetişiyor")
st.title("🕌 Ahi-AI: Değerler Eğitimi ve Mülakat")
st.info("Bu sistem, öğrenci adaylarını sadece notlarıyla değil; Ahilik değerleri, dürüstlük, sabır ve kriz yönetimi becerileriyle değerlendirir.")

# --- YAN MENÜ (GÜVENLİK) ---
with st.sidebar:
    st.header("🔑 Giriş Paneli")
    st.write("Sistemi kullanmak için anahtarınızı girin.")
    api_key = st.text_input("Google API Anahtarı:", type="password", help="AI Studio'dan aldığınız şifre.")
    st.divider()
    st.caption("Geliştirici: Ömer Hoca & Gemini")

# --- PROGRAM ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # En yeni ve hızlı modeli seçtik
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Senaryoyu hafızada tutmak için oturum kontrolü
        if "senaryo" not in st.session_state:
            st.session_state.senaryo = ""

        st.subheader("1. Aşama: Senaryo Üretimi")
        
        # BUTON 1: SENARYO ÜRET
        if st.button("🎲 Yeni Mülakat Başlat", type="primary"):
            with st.spinner("Usta senin için zorlu bir durum düşünüyor..."):
                prompt = """
                Sen Ahilik kültürüne hakim, tecrübeli bir otelcilik ustasısın.
                Turizm lisesi öğrencisi için; dürüstlüğünü, sabrını ve nezaketini zorlayacak
                kısa, çarpıcı ve gerçekçi bir otelcilik kriz senaryosu yaz.
                Sadece senaryoyu ver.
                """
                response = model.generate_content(prompt)
                st.session_state.senaryo = response.text
                st.rerun()

        # Eğer senaryo varsa ekranda göster
        if st.session_state.senaryo:
            st.success("📝 SENARYO:")
            st.markdown(f"**{st.session_state.senaryo}**")
            
            st.divider()
            
            st.subheader("2. Aşama: Öğrenci Cevabı")
            # ÖĞRENCİ CEVABI ALANI
            cevap = st.text_area("Bu durumda ne yapardınız?", height=150, placeholder="Cevabınızı buraya içtenlikle yazın...")
            
            # BUTON 2: DEĞERLENDİR
            if st.button("⚖️ Ahi Usta'ya Gönder ve Puanla"):
                if cevap:
                    with st.spinner("Cevabınız Ahilik terazisinde tartılıyor..."):
                        degerlendirme_prompt = f"""
                        Senaryo: {st.session_state.senaryo}
                        Öğrenci Cevabı: {cevap}
                        
                        Bu cevabı şu kriterlere göre değerlendir:
                        1. Ahilik ve Dürüstlük (Yalan var mı?)
                        2. Müşteri Memnuniyeti ve Nezaket
                        3. Pratik Zeka ve Çözüm
                        
                        Her birine 100 üzerinden puan ver.
                        Sonunda büyük harflerle "SONUÇ: KABUL" veya "SONUÇ: RET" yaz.
                        """
                        sonuc = model.generate_content(degerlendirme_prompt)
                        st.balloons() # Ekranda balonlar uçuşsun
                        st.markdown(sonuc.text)
                else:
                    st.warning("Lütfen boş kağıt vermeyin, bir cevap yazın.")

    except Exception as e:
        st.error(f"Anahtar hatası veya bağlantı sorunu: {e}")

else:
    st.warning("👈 Lütfen sol taraftan API Anahtarınızı girerek sistemi başlatın.")
