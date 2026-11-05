import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse

def parse_uysm_catalog():
    base_url = 'http://www.uysm.ru/'
    print("Запускаем полное сканирование сайта uysm.ru...")
    
    try:
        # Делаем запрос к сайту
        response = requests.get(base_url)
        response.raise_for_status()
        # Принудительно ставим кодировку, чтобы кириллица читалась корректно
        response.encoding = 'windows-1251' 
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        catalog_data = []
        all_links = soup.find_all('a', href=True)
        
        # Слова-маркеры. Ссылки с таким текстом нам точно не нужны в каталоге
        exclude_words = [
            'главная', 'новости', 'контакты', 'о компании', 'фотогалерея', 
            'акции', 'договора', 'партнеры', 'отзывы', 'видео', 
            'задать вопрос', 'условия доставки', 'скидки', 'все отзывы', 'подробнее'
        ]
        
        for link in all_links:
            href = link['href']
            # Вытягиваем текст ссылки, убирая лишние пробелы и переносы
            text = link.get_text(strip=True).replace('\n', ' ').replace('\r', '')
            
            if not text:
                continue
                
            text_lower = text.lower()
            if any(word in text_lower for word in exclude_words):
                continue
                
            # Берем только внутренние ссылки сайта
            if href.startswith('/') or 'uysm.ru' in href or not href.startswith('http'):
                full_url = urllib.parse.urljoin(base_url, href)
                
                # Отсекаем мусор вроде коротких цифр (страницы пагинации) и email-адресов
                if len(text) > 4 and 'mailto:' not in href and '@' not in text:
                    catalog_data.append({
                        'Оборудование / Категория': text,
                        'Ссылка на старом сайте': full_url
                    })
        
        # Чистим дубликаты (одна и та же дробилка может дублироваться в разных блоках)
        seen = set()
        unique_catalog = []
        for item in catalog_data:
            if item['Оборудование / Категория'] not in seen:
                seen.add(item['Оборудование / Категория'])
                unique_catalog.append(item)
                
        if unique_catalog:
            df = pd.DataFrame(unique_catalog)
            # Сохраняем в новый файл, чтобы не путать со старым
            output_file = 'uysm_catalog_full.xlsx'
            df.to_excel(output_file, index=False)
            print(f"\nУспешно! Найдено {len(unique_catalog)} позиций оборудования и запчастей.")
            print(f"Данные сохранены в файл: {output_file}")
        else:
            print("Не удалось найти подходящие ссылки.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    parse_uysm_catalog()