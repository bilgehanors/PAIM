#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from google import genai
from google.genai import types
from datetime import datetime
import sys
import os
import time

def load_data():
    """Excel dosyalarını yükle"""
    print("📂 Veri dosyaları yükleniyor...")
    
    execs = pd.read_excel("C-Level Execs.xlsx")
    companies = pd.read_excel("Company Database.xlsx")
    
    print(f"✅ {len(execs)} müşteri bulundu")
    print(f"✅ {len(companies)} şirket verisi bulundu\n")
    
    return execs, companies

def configure_api(api_key):
    """Google GenAI API'sini yapılandır"""
    print("🔑 API yapılandırılıyor...")
    client = genai.Client(api_key=api_key)
    print("✅ Gemini 2.5 Flash modeli yüklendi\n")
    
    return client

def find_best_company(client, customer_name, customer_sector, companies, usage_counts=None):
    """
    AI kullanarak müşteriye en uygun şirketi bul.
    Uygun şirket yoksa None döner.
    usage_counts: dict — hangi şirket kaç kez önerildi
    """
    if usage_counts is None:
        usage_counts = {}
    
    founders_col = "Founders' Intention"
    company_list = "\n".join([
        f"- {row['Stock Code']}: {row['Industry']} (2025 Revenue: {row['2025 Turnover (Euro)']}, "
        f"2027 Projected: {row['2027 Expected Turnover (Euro)']}, EBITDA: {row['EBITDA (%)']}, "
        f"Employees: {row['Number of Employees']}, Founders' Intent: {row[founders_col]})"
        for _, row in companies.iterrows()
    ])
    
    # Daha önce kullanılan şirketleri bildir
    used_info = ""
    if usage_counts:
        used_lines = [f"  - {code}: already recommended to {count} client(s)" 
                      for code, count in sorted(usage_counts.items(), key=lambda x: -x[1])]
        used_info = "\n\nAlready Recommended Companies (AVOID if possible):\n" + "\n".join(used_lines)
    
    prompt = f"""You are an expert investment advisor. Your task is to find the BEST matching company for a client based on strategic relevance.

Client: {customer_name}
Client's Industry: {customer_sector}

Available Companies:
{company_list}{used_info}

Rules:
1. Pick the ONE company that has the strongest strategic, financial, or synergistic connection to the client's industry.
2. Think about: supply chain synergies, technology adoption potential, market adjacency, investment value, cross-industry opportunities.
3. STRONGLY PREFER companies that have NOT been recommended yet or have been recommended fewer times. Only reuse a company if there is truly no better alternative.
4. If NO company has a meaningful connection to the client's industry, respond with exactly: NONE
5. Respond with ONLY the Stock Code of the best match (e.g. "MSFT") or "NONE". Nothing else."""

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemma-3-27b-it',
                contents=prompt,
                config=types.GenerateContentConfig(
                    http_options=types.HttpOptions(timeout=30000)
                )
            )
            result = response.text.strip().upper()
            
            # Validate that the result is an actual stock code
            valid_codes = companies['Stock Code'].str.upper().tolist()
            if result in valid_codes:
                match = companies[companies['Stock Code'].str.upper() == result].iloc[0]
                return match
            elif result == "NONE":
                return None
            else:
                # Try to extract a stock code from the response
                for code in valid_codes:
                    if code in result:
                        return companies[companies['Stock Code'].str.upper() == code].iloc[0]
                return None
        except Exception as e:
            error_str = str(e)
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                wait_time = 60
                print(f"\n⏳ Rate limit! {wait_time}s bekleniyor... (deneme {attempt+1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"\n⚠️  Eşleştirme hatası: {error_str[:50]}")
                return None
    print(f"\n⚠️  {max_retries} deneme sonrası başarısız.")
    return None


def generate_personalized_message(client, customer_name, sector, company_name, company_sector, 
                                  turnover, expected_turnover, ebitda, employees, founders_intention):
    """
    Müşteri için özel mesaj oluştur
    """
    
    prompt = f"""You are a representative of a highly successful investment brokerage firm.
Using the information below, write a highly PERSONALIZED message to the client in ENGLISH. The message must sound exactly like a real human wrote it. Keep the tone mostly formal but slightly casual. Include one or two very minor grammatical quirks or conversational phrasing so it feels completely natural and not AI-generated.

*Client Information:*
•⁠  ⁠Name: {customer_name}
•⁠  ⁠Industry: {sector}

*Investment Opportunity (The Company):*
•⁠  ⁠Company Name: {company_name}
•⁠  ⁠Sector: {company_sector}
•⁠  ⁠2025 Revenue (Euro): {turnover}
•⁠  ⁠2027 Projected Revenue (Euro): {expected_turnover}
•⁠  ⁠EBITDA: {ebitda}
•⁠  ⁠Headcount: {employees}
•⁠  ⁠Founders' Intent: {founders_intention}

*Instructions:*
1.⁠ ⁠Accurately use the client's name and industry.
2.⁠ ⁠Emphasize the target company's growth potential and financial strength.
3.⁠ ⁠Draw a logical, meaningful connection between the client's business and the target company.
4.⁠ ⁠Clearly explain the concrete advantages of this investment opportunity.
5.⁠ ⁠Maintain a warm, professional, and highly persuasive tone.
6.⁠ ⁠Keep the total length under 200 words.
7.⁠ ⁠Output ONLY the message body. NEVER include a subject line (no "Subject:" header). Do NOT include any titles or introductory labels.
8.⁠ ⁠Sign off with "Best regards," followed by "Alex Hartman" on the next line and "Senior Advisor, Meridian Capital Partners" on the line after. NEVER use placeholders like [Your Name] or [Company Name].
9.⁠ ⁠Do NOT wrap the output in markdown formatting or code blocks."""

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemma-3-27b-it',
                contents=prompt,
                config=types.GenerateContentConfig(
                    http_options=types.HttpOptions(timeout=30000)
                )
            )
            text = response.text.strip()
            # Post-process: remove any Subject: lines the model might still add
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                if line.strip().lower().startswith('subject:'):
                    continue
                cleaned_lines.append(line)
            text = '\n'.join(cleaned_lines).strip()
            return text
        except Exception as e:
            error_str = str(e)
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                wait_time = 60
                print(f"\n⏳ Rate limit! {wait_time}s bekleniyor... (deneme {attempt+1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"\n⚠️  API Hatası: {error_str[:50]}")
                return "❌ API'den cevap alınamadı. Lütfen daha sonra deneyiniz."
    return "❌ Rate limit aşıldı, birçok deneme sonrası başarısız."

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
    client = configure_api(api_key)
    
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
        
        skipped = 0
        usage_counts = {}  # Hangi şirket kaç kez önerildi
        
        for idx, (_, customer) in enumerate(execs.iterrows(), 1):
            customer_name = customer['Name']
            customer_sector = customer['Sector']
            
            # AI ile en uygun şirketi bul
            print(f"[{idx}/{len(execs)}] {customer_name} ({customer_sector}) → Eşleştiriliyor...", end=" ")
            company = find_best_company(client, customer_name, customer_sector, companies, usage_counts)
            
            if company is None:
                print("❌ Uygun şirket bulunamadı, atlanıyor.")
                skipped += 1
                continue
            
            company_name = company['Stock Code']
            company_sector = company['Industry']
            turnover = company['2025 Turnover (Euro)']
            expected_turnover = company['2027 Expected Turnover (Euro)']
            ebitda = company['EBITDA (%)']
            employees = company['Number of Employees']
            founders_intention = company["Founders' Intention"]
            
            # Kullanım sayacını güncelle
            usage_counts[company_name] = usage_counts.get(company_name, 0) + 1
            
            print(f"✅ ← {company_name} ({company_sector})")
            
            # Mesaj oluştur
            message = generate_personalized_message(
                client,
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
    if skipped > 0:
        print(f"⏭️  {skipped} müşteri uygun şirket bulunamadığı için atlandı")
    print(f"💾 Dosya kaydedildi: {output_filename}")

if __name__ == "__main__":
    main()
