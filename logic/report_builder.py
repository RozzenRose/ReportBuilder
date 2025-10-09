import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from logic.plot_builder import get_purchases_plot, get_income_plot, get_pie
from logic.math_functions import pie_prices, sort_data
from rabbitmq.to_aggregator import send_to_aggregator
import io


# Путь к шрифту DejaVuSans (по умолчанию на Manjaro)
font_path = "/usr/share/fonts/TTF/DejaVuSans.ttf"
# Регистрируем шрифт
pdfmetrics.registerFont(TTFont("CyrillicFont", font_path))


async def get_report(raw_data):
    # Отправляем данные на обработку в CurrencyAggregator
    data = await send_to_aggregator(raw_data)

    # Сортируем данные
    purchases, incomes = await sort_data(data)

    # Создаем PDF
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=A4)

    # Добавляем заголовок текст
    c.setFont("CyrillicFont", 22)
    c.drawString(50, 800, "Финансовый отчет")

    # Вставляем график с расходами
    c.drawImage(ImageReader(await get_purchases_plot(purchases)), 30, 450, width=540, height=320)
    plt.tight_layout()
    c.setFont("CyrillicFont", 8)
    y_string = 430
    for i in range(len(purchases)):
        c.drawString(50, y_string, f"{purchases[i][0]} - "
                                           f"{round(purchases[i][1])} {purchases[i][2]}")
        y_string -= 15

    c.showPage()  # Создаем новую страницу

    # Вставляем график с доходами
    c.drawImage(ImageReader(await get_income_plot(incomes)), 30, 450, width=540, height=320)
    plt.tight_layout()
    c.setFont("CyrillicFont", 8)
    y_string = 430
    for i in range(len(incomes)):
        c.drawString(50, y_string, f"{incomes[i][0]} - "
                                           f"{round(incomes[i][1])} {incomes[i][2]}")
        y_string -= 15

    c.showPage() # Создаем новую страницу

    c.setFont("CyrillicFont", 16)
    c.drawString(50, 800, "Категории расходов")

    # Вставляем круговую диаграмму
    c.drawImage(ImageReader(await get_pie(data)), 50, 440, width=480, height=350)
    plt.tight_layout()

    # Вставляем подпись по категориям под диаграмму
    pie_data = await pie_prices(data)
    sum_pri = sum([item[1] for item in pie_data])
    c.setFont("CyrillicFont", 8)
    y_string = 450
    for i in range(len(pie_data)):
        cat = pie_data[i][0]
        pri = pie_data[i][1]
        c.drawString(50, y_string, f'{cat} - {round(pri)} - {round((pri/sum_pri)*100, 2)}%')
        y_string -= 15

    # Сохраняем PDF
    c.showPage()
    c.save()

    # Отправляем данные
    pdf_buf.seek(0)
    pdf_bytes = pdf_buf.getvalue()
    return pdf_bytes
