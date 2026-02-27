Tamamdır kanka, ismi PAIM (muhtemelen Personalized AI Investment Messenger veya benzeri bir açılımı vardır, havalı olmuş) olarak güncelledim ve İngilizce bir README hazırladım.

İşte projenin yeni kimliğiyle hazırlanan README.md:

🚀 PAIM: Personalized AI Investment Messenger
PAIM is a Python-based automation tool designed for investment brokering professionals. It bridges the gap between high-level executive databases and investment opportunities by generating bespoke, highly personalized outreach messages using Gemini 2.5 Flash.

🛠️ Core Features
Automated Personalization: Matches your C-Level lead list with available company investment data seamlessly.

AI-Driven Copywriting: Leverages Google’s Gemini 1.5 Flash to craft persuasive, professional, and context-aware messages in Turkish.

Financial Data Integration: Automatically injects critical KPIs like 2025/2027 revenue projections, EBITDA, and founder intentions into every pitch.

Scalable Outreach: Processes entire datasets in seconds and outputs formatted results into time-stamped logs for easy CRM integration.

📋 Prerequisites
Ensure you have Python 3.x installed along with the following dependencies:

Bash
pip install pandas google-generativeai openpyxl
The script expects two specific Excel files in the root directory:

C-Level Execs.xlsx: Containing lead names, sectors, and contact info.

Company Database.xlsx: Containing target company financials and industry details.

🚀 Getting Started
Obtain API Key: Get your credentials from the Google AI Studio.

Execution:

Bash
python paim.py
Authentication: Enter your API key when prompted (or set it as a GOOGLE_API_KEY environment variable).

Output: Review your generated pitches in the personalized_messages_YYYYMMDD_HHMMSS.txt file.

⚙️ Configuration
You can fine-tune the AI's behavior within the generate_personalized_message function:

Tone: Professional, persuasive, and sincere.

Constraint: Maximum 200 words per message.

Language: Turkish (Targeting the local investment ecosystem).

⚠️ Disclaimer
This tool is intended for communication assistance and does not constitute financial advice. Always verify the output before sending it to high-value clients.
