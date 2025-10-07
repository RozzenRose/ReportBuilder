import matplotlib.pyplot as plt
import io
from math_functions import pie_prices


async def get_purchases_plot(data):
    #Распакум данные
    plot_data = []
    plot_data.extend([(item['price'], item['created_at']) for item in data])
    # Создаем график
    plt.subplots(figsize=(10.5, 5))
    plt.plot([item[1] for item in plot_data],[item[0] for item in plot_data], marker="o")
    plt.title("Расходы")
    plt.xticks(rotation=45)
    plt.ylabel("Сумма")
    plt.tight_layout()

    # Сохраняем график в память как PNG
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf


async def get_income_plot(data):
    #Распакум данные
    plot_data = []
    plot_data.extend([(item['quantity'], item['created_at']) for item in data])
    # Создаем график
    plt.subplots(figsize=(11, 5))
    plt.plot([item[1] for item in plot_data],[item[0] for item in plot_data], marker="o")
    plt.title("Доходы")
    plt.xticks(rotation=45)
    plt.ylabel("Сумма")
    plt.tight_layout()

    # Сохраняем график в память как PNG
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf


async def get_pie(data):
    # Функция подсчета расходов по категориям, вернет что-то типо {'Имя категории': Сумма расходов}
    answer = await pie_prices(data)

    # Построение круговой диаграммы
    plt.pie([item[1] for item in answer], labels=[item[0] for item in answer], startangle=90)

    # Соотношение сторон — чтобы круг был ровным
    plt.axis('equal')
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf

