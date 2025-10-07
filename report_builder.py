import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from plot_builder import get_purchases_plot, get_income_plot, get_pie
from math_functions import pie_prices
import io



async def get_report(data):
    # Путь к шрифту DejaVuSans (по умолчанию на Manjaro)
    font_path = "/usr/share/fonts/TTF/DejaVuSans.ttf"

    # Регистрируем шрифт
    pdfmetrics.registerFont(TTFont("CyrillicFont", font_path))


    # Создаем PDF
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=A4)

    # Добавляем заголовок текст
    c.setFont("CyrillicFont", 22)
    c.drawString(50, 800, "Финансовый отчет")

    # Вставляем график с расходами
    c.drawImage(ImageReader(await get_purchases_plot(data['purchases'])), 30, 450, width=540, height=320)
    plt.tight_layout()
    c.setFont("CyrillicFont", 8)
    y_string = 430
    for i in range(len(data['purchases'])):
        c.drawString(50, y_string, f"{data['purchases'][i]['name']} - "
                                           f"{data['purchases'][i]['price']}")
        y_string -= 15
    c.showPage()  # Создаем новую страницу

    # Вставляем график с доходами
    c.drawImage(ImageReader(await get_income_plot(data['incomes'])), 30, 450, width=540, height=320)
    plt.tight_layout()
    c.setFont("CyrillicFont", 8)
    y_string = 430
    for i in range(len(data['incomes'])):
        c.drawString(50, y_string, f"{data['incomes'][i]['description']} - "
                                           f"{data['incomes'][i]['quantity']}")
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
        c.drawString(50, y_string, f'{cat} - {pri} - {round((pri/sum_pri)*100, 2)}%')
        y_string -= 15

    # Сохраняем PDF
    c.showPage()
    c.save()

    pdf_buf.seek(0)
    pdf_bytes = pdf_buf.getvalue()
    return pdf_bytes
