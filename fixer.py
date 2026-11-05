import pandas as pd

def fix_and_convert():
    input_file = 'uysm_catalog_full.xlsx'
    output_file = 'uysm_catalog_clean.csv'
    
    print(f"Открываем файл {input_file}...")
    
    try:
        # Читаем проблемный Excel
        df = pd.read_excel(input_file)
        
        # Функция для исправления двойной кодировки
        def fix_encoding(text):
            if not isinstance(text, str):
                return text
            try:
                return text.encode('windows-1251').decode('utf-8')
            except:
                return text
                
        # Применяем исправление ко всем колонкам
        for col in df.columns:
            df[col] = df[col].apply(fix_encoding)
            
        # Исправляем сами названия колонок, если они тоже сбились
        df.columns = [fix_encoding(col) for col in df.columns]
        
        # Сохраняем в чистый CSV (кодировка utf-8-sig нужна, чтобы Excel тоже понимал этот CSV)
        df.to_csv(output_file, index=False, encoding='utf-8-sig', sep=';')
        
        print(f"Успех! Данные расшифрованы и сохранены в файл: {output_file}")
        print("Теперь этот файл можно легко загрузить в AI Studio.")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    fix_and_convert()