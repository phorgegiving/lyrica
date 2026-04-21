# Syllable
dynamic kinetic typography project
Syllable - это мультимедийный Python-инструмент, который превращает прослушивание музыки в визуальный экспириенс. Проект автоматически захватывает играющий трек, анализирует его структуру и генерирует адаптивные субтитры, которые подстраиваются под настроение музыки в реальном времени.

# Основные фишки:
Zero-API Listening: Захват метаданных напрямую из системы (Windows SDK), не требующий Spotify Premium или иных подписок. Работает со многими плеерами.

Neural Alignment: Послоговая синхронизация текста с аудиопотоком с помощью нейросети WhisperX.

Adaptive Design System: Визуальный стиль (верстка, анимация, цвета) меняется динамически:

Smart Caching: Система локального хранения данных (текст, аудио, тайминги) для мгновенного повторного запуска. (потенциально будет хранение на сервере)

# Технологический стек
Core: Python 3.10+

Audio ML: WhisperX (AI alignment), Librosa (Beat detection).

Data Mining: yt-dlp (YouTube Search), LyricsGenius (Genius API).

System: winsdk (Windows Media Control).

Frontend: HTML5 / CSS3 (Animations) / JavaScript

# Запуск:

git clone https://github.com/your-username/syllable.git

cd syllable

в requirements.txt есть несколько опциональных пакетов. стоить выбрать подходящие перед установкой
(по дефолту-пресеты для слабых пк) НЕ ЗАБУДЬ ПЕРЕЙТИ В .\venv\Scripts\Activate.ps1

pip install -r requirements.txt

создайте файл .env в корневой папке проекта, вставьте туда:

GENIUS_ACCESS_TOKEN=your_token_here

python main.py