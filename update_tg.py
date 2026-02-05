import feedparser
import json
import os

# Ссылка на ваш канал через RSS-мост (этот сервис превращает ТГ в понятный код)
TG_RSS = "https://rsshub.app/telegram/channel/TPereslavl"

def update():
    print("Запуск сбора новостей...")
    feed = feedparser.parse(TG_RSS)
    news_list = []
    
    # Проверяем, есть ли новости в ленте
    if not feed.entries:
        print("Лента пуста или сервис временно недоступен")
        return

    for entry in feed.entries[:12]: # Берем 12 последних постов
        # Убираем лишние HTML теги из текста
        description = entry.description.replace('<br>', '\n').split('<img')[0] 
        
        news_list.append({
            "title": entry.title[:80] + "..." if len(entry.title) > 80 else entry.title,
            "link": entry.link,
            "description": description[:200] + "...",
            "date": entry.published
        })
    
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)
    print(f"Успешно сохранено {len(news_list)} новостей в news.json")

if __name__ == "__main__":
    update()
