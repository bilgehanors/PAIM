#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import google.generativeai as genai
from datetime import datetime
import sys
import os

def load_data():
    """Excel dosyalarını yükle"""
    print("📂 Veri dosyaları yükleniyor...")
    
    execs = pd.read_excel("C-Level Execs.xlsx")
    companies = pd.read_excel("Company Database.xlsx")
    
    print(f"✅ {len(execs)} müşteri bulundu")
    print(f"✅ {len(companies)} şirket verisi bulundu\n")
    
    return execs, companies

def configure_api(api_key):
    """Google Generative AI API'sini yapılandır"""
    print("🔑 API yapılandırılıyor...")
    genai.configure(api_key=api_key)
    
    # Model seçimi
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("✅ Gemini 2.5 Flash modeli yüklendi\n")
    
    return model

def generate_personalized_message(model, customer_name, sector, company_name, company_sector, 
                                  turnover, expected_turnover, ebitda, employees, founders_intention):
    """
    Müşteri için özel mesaj oluştur
    """
    
    prompt = f"""Sen başarılı bir investment brokering şirketinin temsilcisisin.
Aşağıdaki bilgileri kullanarak, müşteri için TÜRKÇE ve çok KIŞISEL bir mesaj yaz:

**Müşteri Bilgileri:**
- Ad: {customer_name}
- Sektörü: {sector}

**Yatırım Fırsatı (Şirket):**
- Şirket Adı: {company_name}
- Sektör: {company_sector}
- 2025 Ciro (Euro): {turnover}
- 2027 Beklenen Ciro (Euro): {expected_turnover}
- EBITDA: {ebitda}
- Çalışan Sayısı: {employees}
- Kurucuların Niyeti: {founders_intention}

**Talimatta:**
1. Müşterinin adını ve sektörünü doğru bir şekilde kullan
2. Şirketin büyüme potansiyelini ve finansal gücünü vurgula
3. Müşteri ile şirket arasında anlamlı bir bağlantı kur
4. Yatırım fırsatının avantajlarını açıkla
5. Samimi, profesyonel ve ikna edici bir ton kullan
6. Maksimum 200 kelime olsun
7. Sadece mesajı yaz, başlık yok

Mesajı şimdi yaz:"""

    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(
            timeout=30.0
        ))
        return response.text.strip()
    except Exception as e:
        print(f"\n⚠️  API Hatası (Müşteri atlıyor): {str(e)[:50]}")
        return "❌ API'den cevap alınamadı. Lütfen daha sonra deneyiniz."

def main():
    # API KEY kontrolü (ortam değişkeninden oku veya input iste)
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("⚠️  GOOGLE_API_KEY ortam değişkeni bulunamadı.")
        print("📝 Lütfen API Key'ini gir:")
        api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API Key gerekli!")
        sys.exit(1)
    
    print(f"✅ API Key alındı ({api_key[:10]}...)\n")
    
    # Veri yükleme
    execs, companies = load_data()
    
    # API yapılandırma
    model = configure_api(api_key)
    
    # Çıktı dosyası
    output_filename = f"personalized_messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    print(f"💬 Özel mesajlar oluşturuluyor ({len(execs)} müşteri için)...\n")
    print("=" * 80)
    
    messages_generated = 0
    
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write("=" * 80 + "\n")
        outfile.write(f"KİŞİSELLEŞTİRİLMİŞ YATIRIMI MESAJLARI\n")
        outfile.write(f"Oluşturma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        outfile.write("=" * 80 + "\n\n")
        
        for idx, (_, customer) in enumerate(execs.iterrows(), 1):
            customer_name = customer['Name']
            customer_sector = customer['Sector']
            
            # Rastgele bir şirket seç (her müşteri için farklı)
            company = companies.iloc[idx % len(companies)]
            company_name = company['Stock Code']
            company_sector = company['Industry']
            turnover = company['2025 Turnover (Euro)']
            expected_turnover = company['2027 Expected Turnover (Euro)']
            ebitda = company['EBITDA (%)']
            employees = company['Number of Employees']
            founders_intention = company["Founders' Intention"]
            
            print(f"[{idx}/{len(execs)}] {customer_name} ({customer_sector}) ← {company_name} ({company_sector})")
            
            # Mesaj oluştur
            message = generate_personalized_message(
                model,
                customer_name,
                customer_sector,
                company_name,
                company_sector,
                turnover,
                expected_turnover,
                ebitda,
                employees,
                founders_intention
            )
            
            # Dosyaya yaz
            outfile.write(f"--- MÜŞTERI {idx} ---\n")
            outfile.write(f"Ad: {customer_name}\n")
            outfile.write(f"Sektörü: {customer_sector}\n")
            outfile.write(f"İletişim: {customer['Contact Number']}\n")
            outfile.write(f"Durum: {customer['Status']}\n")
            outfile.write(f"\n[YÖNELDİĞİ ŞİRKET: {company_name} - {company_sector}]\n")
            outfile.write(f"2025 Ciro: {turnover}\n")
            outfile.write(f"Beklenen 2027 Ciro: {expected_turnover}\n")
            outfile.write(f"EBITDA: {ebitda}\n")
            outfile.write(f"Çalışan Sayısı: {employees}\n\n")
            outfile.write(f"📧 KİŞİSEL MESAJ:\n")
            outfile.write(message + "\n\n")
            outfile.write("-" * 80 + "\n\n")
            
            messages_generated += 1
    
    print("=" * 80)
    print(f"\n✅ Tamamlandı!")
    print(f"📄 {messages_generated} adet özel mesaj oluşturuldu")
    print(f"💾 Dosya kaydedildi: {output_filename}")

if __name__ == "__main__":
    main()
