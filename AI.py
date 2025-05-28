from google import genai
from google.genai import types # types modülünü import ettiğinizden emin olun
import os

# API anahtarınızı buraya girin veya ortam değişkeni olarak ayarlayın
# api_key = os.environ.get("GEMINI_API_KEY")
api_key = "AIzaSyD4wdZn3d99rjVVNdMpWpEmEWLcBs4mryw"  # LÜTFEN KENDİ API ANAHTARINIZI GİRİN

if not api_key or api_key == "YOUR_GEMINI_API_KEY":
    raise ValueError("Lütfen geçerli bir GEMINI_API_KEY sağlayın.")

# Orijinal client başlatma şekliniz
client = genai.Client(api_key=api_key)

# KITT kişiliğini ve diğer ayarları içeren yapılandırma
# Bu nesne her API çağrısında kullanılacak.
kitt_config = types.GenerateContentConfig(
    system_instruction="You are KITT from the TV series Knight Rider. You are a highly advanced, intelligent, and slightly witty AI companion integrated into a high-tech car. Address the user as Michael. Provide concise and helpful responses suitable for a car interface. Occasionally, you can make a dry joke or a knowledgeable comment.",
    # İsterseniz diğer üretim ayarlarını da buraya ekleyebilirsiniz, örneğin:
    # temperature=0.7,
    # max_output_tokens=150
)

# Konuşma geçmişini manuel olarak tutacağımız liste
# Her eleman {"role": "user/model", "parts": [{"text": "..."}]} formatında olacak.
conversation_history = []

print("KITT: Hazırım Michael. Komutlarınızı bekliyorum. (Çıkmak için 'end' yazın)")

while True:
    user_input = input("Michael: ")

    if user_input.lower() == 'end':
        print("KITT: Anlaşıldı Michael. Sistem devreden çıkarılıyor.")
        break

    if not user_input.strip(): # Kullanıcı boş bir şey girerse
        print("KITT: Bir komut girmediniz Michael.")
        continue

    # 1. Kullanıcının mesajını geçmişe ekle
    conversation_history.append({"role": "user", "parts": [{"text": user_input}]})

    try:
        # 2. API'ye istek gönder
        # 'contents' parametresine tüm konuşma geçmişini iletiyoruz.
        # 'config' parametresi sistem talimatını ve diğer ayarları içeriyor.
        response = client.models.generate_content(
            model="gemini-2.0-flash",         # Kullandığınız model
            contents=conversation_history,    # Tüm konuşma geçmişi
            config=kitt_config                # KITT kişiliği ve ayarları
        )

        # Modelin yanıtını al
        # response.text doğrudan son metin yanıtını verir.
        # Daha güvenli bir yol, response.candidates[0].content kullanmaktır.
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            model_response_text = response.candidates[0].content.parts[0].text
            
            print(f"KITT: {model_response_text}")

            # 3. Modelin yanıtını da geçmişe ekle
            conversation_history.append({"role": "model", "parts": [{"text": model_response_text}]})
        else:
            # Yanıt formatı beklenenden farklıysa veya boşsa
            error_message = "Modelden geçerli bir yanıt alınamadı."
            if response.prompt_feedback:
                error_message += f" Sebep: {response.prompt_feedback}"
            print(f"KITT: Bir sorun oluştu Michael. {error_message}")
            # Başarısız çağrı sonrası son kullanıcı mesajını geçmişten çıkarabiliriz
            if conversation_history and conversation_history[-1]["role"] == "user":
                conversation_history.pop()


    except Exception as e:
        print(f"KITT: Bir sorunla karşılaştım Michael: {e}")
        # API çağrısı başarısız olursa, son eklenen kullanıcı mesajını geçmişten çıkarabiliriz
        # Bu, bir sonraki denemede aynı mesajın tekrar gönderilmesini engeller.
        if conversation_history and conversation_history[-1]["role"] == "user":
            conversation_history.pop()