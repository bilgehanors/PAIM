#!/bin/bash
# ============================================
#   WhatsApp Mesaj Gönderici - Kurulum Scripti
#   Arkadaşın bunu çalıştırması yeterli!
# ============================================

echo "============================================"
echo "  📲 WhatsApp Sender - Kurulum Başlıyor"
echo "============================================"
echo ""

# 1. Python kontrolü
if command -v python3 &> /dev/null; then
    echo "✅ Python3 zaten yüklü: $(python3 --version)"
else
    echo "❌ Python3 bulunamadı!"
    echo ""
    
    # macOS mı Linux mu?
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "📥 macOS tespit edildi."
        echo "Python'u yüklemek için şu komutu çalıştır:"
        echo ""
        echo "   xcode-select --install"
        echo ""
        echo "Veya https://www.python.org/downloads/ adresinden indir."
    else
        echo "📥 Linux tespit edildi. Python yükleniyor..."
        sudo apt update && sudo apt install -y python3 python3-pip
    fi
    
    echo ""
    echo "Python yüklendikten sonra bu scripti tekrar çalıştır!"
    exit 1
fi

# 2. pip kontrolü
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 zaten yüklü"
else
    echo "📥 pip3 yükleniyor..."
    python3 -m ensurepip --upgrade 2>/dev/null || {
        echo "pip yüklenemiyor, manuel yükleme gerekli:"
        echo "   python3 -m ensurepip --upgrade"
        exit 1
    }
fi

echo ""
echo "📦 Gerekli paketler yükleniyor..."
echo ""

# 3. Gerekli paketleri yükle
pip3 install pywhatkit pyautogui pyperclip

echo ""
echo "============================================"
echo "  ✅ Kurulum Tamamlandı!"
echo "============================================"
echo ""
echo "Şimdi şu komutu çalıştır:"
echo ""
echo "   python3 whatsapp_sender.py"
echo ""
echo "⚠️  ÖNEMLİ: Tarayıcıda web.whatsapp.com açık"
echo "   ve giriş yapılmış olmalı!"
echo "============================================"
