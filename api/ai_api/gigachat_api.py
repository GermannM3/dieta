import aiohttp
import json
import os
import time
from typing import Optional, List, Dict

class GigaChatAPI:
    def __init__(self):
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1"
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.client_id = "0ac3bc43-79fb-49cf-86bc-c9c806a8e3d6"
        self.auth_key = "MGFjM2JjNDMtNzlmYi00OWNmLTg2YmMtYzljODA2YThlM2Q2OmUyMGFlMDJjLTNmMjAtNGE4ZC1iMWE4LTRiMTA1YmI2OGMwZQ=="
        self.access_token = None
        self.token_expires_at = None
        
    async def get_access_token(self) -> Optional[str]:
        """Асинхронное получение токена доступа"""
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': '864e65ea-7a12-41ce-b398-0809f0f30fd0',
            'Authorization': f'Basic {self.auth_key}'
        }
        data = 'scope=GIGACHAT_API_PERS'
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.auth_url, headers=headers, data=data, ssl=False) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get('access_token')
                        self.token_expires_at = token_data.get('expires_at')
                        return self.access_token
                    else:
                        print(f"Ошибка получения токена: {response.status}, {await response.text()}")
                        return None
        except Exception as e:
            print(f"Ошибка при запросе токена: {e}")
            return None
    
    async def ensure_token(self) -> bool:
        """Проверка и обновление токена при необходимости"""
        current_time = int(time.time() * 1000)
        
        if not self.access_token or (self.token_expires_at and current_time >= self.token_expires_at):
            return await self.get_access_token() is not None
        return True
    
    async def chat_completion(self, messages: List[Dict], model: str = "GigaChat", temperature: float = 0.1) -> Optional[str]:
        """Асинхронная отправка запроса к GigaChat API"""
        if not await self.ensure_token():
            return None
            
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    ssl=False
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'choices' in data and len(data['choices']) > 0:
                            return data['choices'][0]['message']['content']
                    else:
                        print(f"Ошибка GigaChat API: {response.status}, {await response.text()}")
                        return None
                
        except Exception as e:
            print(f"Ошибка при запросе к GigaChat: {e}")
            return None
    
    async def simple_completion(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Простой асинхронный запрос к GigaChat"""
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
        messages.append({
            "role": "user", 
            "content": prompt
        })
        
        return await self.chat_completion(messages)

# Глобальный экземпляр
gigachat = GigaChatAPI()

# Функции-обертки для совместимости с существующим кодом
async def generate_text_gigachat(prompt: str, system_prompt: str = None) -> str:
    """Генерация текста через GigaChat"""
    try:
        result = await gigachat.simple_completion(prompt, system_prompt)
        return result if result else "Извините, не удалось получить ответ от GigaChat."
    except Exception as e:
        print(f"Ошибка в generate_text_gigachat: {e}")
        return "Произошла ошибка при обращении к GigaChat."

async def answer_to_text_prompt_gigachat(main_prompt: str, tg_id: int) -> str:
    """Ответ на текстовый промпт через GigaChat с контекстом"""
    from database.crud import get_context, add_to_context
    
    try:
        # Получаем контекст пользователя
        context = await get_context(tg_id=tg_id)
        
        # Формируем системный промпт
        system_prompt = """Ты - умный ассистент-диетолог. Отвечай на русском языке, будь дружелюбным и полезным. 
        Специализируйся на вопросах питания, здоровья и диетологии. Давай практические советы."""
        
        # Формируем сообщения с контекстом
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем предыдущий контекст
        for ctx in context[-10:]:  # Последние 10 сообщений
            messages.append({"role": "user", "content": ctx.get("user", "")})
            if ctx.get("assistant"):
                messages.append({"role": "assistant", "content": ctx["assistant"]})
        
        # Добавляем текущий запрос
        messages.append({"role": "user", "content": main_prompt})
        
        # Получаем ответ от GigaChat
        response = await gigachat.chat_completion(messages)
        
        if response:
            # Сохраняем в контекст
            await add_to_context(tg_id=tg_id, user_message=main_prompt, assistant_message=response)
            return response
        else:
            return "Извините, не удалось получить ответ от GigaChat."
            
    except Exception as e:
        print(f"Ошибка в answer_to_text_prompt_gigachat: {e}")
        return "Произошла ошибка при обработке запроса." 