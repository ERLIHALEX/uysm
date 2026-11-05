import csv
import os
import re
import random

# Настройки путей
CSV_FILE = 'uysm_catalog_clean.csv'
PRODUCT_TEMPLATE = 'product_template.html'
CATALOG_TEMPLATE = 'catalog_template.html'
OUTPUT_DIR = 'products'
CATALOG_OUTPUT = 'catalog_generated.html'

# Ключевые слова для определения запчастей (чтобы отключать 3D и Видео)
PARTS_KEYWORDS = ['плита', 'конус', 'ролик', 'бронз', 'запчаст', 'подпятник', 'пружин', 'сетка', 'лента', 'втулка']

def is_spare_part(title):
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in PARTS_KEYWORDS)

def generate_sku():
    # Генерируем случайный артикул для реалистичности
    return f"1049{random.randint(10000, 99999)}"

def main():
    # 1. Создаем папку для товаров, если её нет
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. Читаем шаблоны
    with open(PRODUCT_TEMPLATE, 'r', encoding='utf-8') as f:
        prod_template_html = f.read()

    with open(CATALOG_TEMPLATE, 'r', encoding='utf-8') as f:
        cat_template_html = f.read()

    generated_cards = []
    
    print("🚀 Запуск генератора статических страниц ЮУСМ...")

    # 3. Читаем CSV базу
    # Используем utf-8-sig на случай BOM от Excel
    with open(CSV_FILE, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader, None) # Пропускаем заголовок

        for index, row in enumerate(reader):
            if not row or len(row) < 1:
                continue
            
            title = row[0].strip()
            if not title:
                continue

            # Определяем категорию и логику рендеринга
            is_part = is_spare_part(title)
            category_name = "Запчасти и комплектующие" if is_part else "Дробильно-сортировочное оборудование"
            category_slug = "zapchasti" if is_part else "drobilki"
            
            sku = generate_sku()
            file_name = f"item_{index}.html"
            file_path = os.path.join(OUTPUT_DIR, file_name)

            # --- РЕНДЕРИНГ КАРТОЧКИ ТОВАРА ---
            html = prod_template_html
            html = html.replace('{{TITLE}}', title)
            html = html.replace('{{SKU}}', sku)
            html = html.replace('{{CATEGORY}}', category_name)

            # Умный рендеринг (Макросы препроцессора)
            if is_part:
                # Вырезаем блоки 3D и Видео
                html = re.sub(r'<!-- IF_EQUIPMENT -->.*?<!-- ENDIF_EQUIPMENT -->', '', html, flags=re.DOTALL)
                # Делаем вкладку чертежа активной, так как 3D удалено
                html = html.replace('data-target="tab-blueprint"', 'data-target="tab-blueprint" class="tab-btn active"')
                html = html.replace('id="tab-blueprint" class="tab-pane"', 'id="tab-blueprint" class="tab-pane active"')
            else:
                # Оставляем блоки, просто удаляем сами комментарии-маркеры
                html = html.replace('<!-- IF_EQUIPMENT -->', '').replace('<!-- ENDIF_EQUIPMENT -->', '')

            # Корректируем пути (так как файлы теперь в папке products/)
            # Возвращаем ссылки на корень
            html = html.replace('href="catalog.html"', 'href="../catalog_generated.html"')
            html = html.replace('href="index.html"', 'href="../index.html"')
            html = html.replace('href="blueprint.html"', 'href="../blueprint.html"')
            html = html.replace('href="lines.html"', 'href="../lines.html"')
            html = html.replace('href="tour.html"', 'href="../tour.html"')
            html = html.replace('href="photo-order.html"', 'href="../photo-order.html"')
            html = html.replace('href="troubleshooting.html"', 'href="../troubleshooting.html"')
            html = html.replace('href="compare.html"', 'href="../compare.html"')
            html = html.replace('href="bim.html"', 'href="../bim.html"')
            html = html.replace('href="cabinet.html"', 'href="../cabinet.html"')
            html = html.replace('href="map.html"', 'href="../map.html"')
            html = html.replace('href="contacts.html"', 'href="../contacts.html"')

            # Сохраняем готовый HTML файл товара
            with open(file_path, 'w', encoding='utf-8') as out_f:
                out_f.write(html)

            # --- ГЕНЕРАЦИЯ КАРТОЧКИ ДЛЯ КАТАЛОГА ---
            price_badge = "В наличии" if random.random() > 0.3 else "Под заказ"
            card_html = f"""
            <div class="product-card" data-category="{category_slug}">
                <div class="product-image">{'Чертеж' if is_part else 'Фото агрегата'}</div>
                <div class="product-info">
                    <div class="product-category">{category_name}</div>
                    <div class="product-title">{title}</div>
                    <div class="product-footer">
                        <span class="product-price">{price_badge}</span>
                        <a href="{OUTPUT_DIR}/{file_name}" class="btn-small">Подробнее</a>
                    </div>
                </div>
            </div>
            """
            generated_cards.append(card_html)

    # 4. Собираем финальный каталог
    final_catalog_html = cat_template_html.replace('<!-- PRODUCTS_GRID_START -->', '\n'.join(generated_cards))
    
    with open(CATALOG_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(final_catalog_html)

    print(f"✅ Успешно сгенерировано {len(generated_cards)} страниц товаров в папке '{OUTPUT_DIR}/'!")
    print(f"✅ Каталог обновлен и сохранен как '{CATALOG_OUTPUT}'.")

if __name__ == "__main__":
    main()