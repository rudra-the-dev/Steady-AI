from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Cards</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #f5f1e8;
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
        }

        .cards-wrapper {
            position: relative;
            overflow: hidden;
        }

        .cards-container {
            display: flex;
            gap: 20px;
            transition: transform 0.3s ease-out;
        }

        .card {
            background: #f9f6f0;
            border-radius: 16px;
            padding: 40px 30px;
            min-height: 280px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            position: relative;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border-color: #e8e3d8;
        }

        .card:active {
            transform: translateY(-2px);
        }

        .icon {
            font-size: 48px;
            margin-bottom: 30px;
        }

        .card-title {
            font-size: 24px;
            font-weight: 500;
            color: #4a4a4a;
            line-height: 1.4;
            margin-top: auto;
        }

        @media (min-width: 769px) {
            .cards-container {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
            }

            .card {
                flex: none;
                width: 100%;
            }

            .dots {
                display: none;
            }
        }

        @media (max-width: 768px) {
            body {
                padding: 20px 0;
            }

            .cards-wrapper {
                padding: 0 20px;
            }

            .cards-container {
                gap: 20px;
                padding: 0;
            }

            .card {
                flex: 0 0 calc(100vw - 40px);
                scroll-snap-align: center;
            }

            .dots {
                display: flex;
                justify-content: center;
                gap: 8px;
                margin-top: 20px;
            }

            .dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: #d4cfc4;
                transition: all 0.3s ease;
                cursor: pointer;
            }

            .dot.active {
                background-color: #8b7f6f;
                width: 24px;
                border-radius: 4px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="cards-wrapper">
            <div class="cards-container" id="cardsContainer">
                <div class="card" onclick="handleCardClick(0)">
                    <div class="icon">🎓✨</div>
                    <h2 class="card-title">The joy of lifelong learning</h2>
                </div>
                <div class="card" onclick="handleCardClick(1)">
                    <div class="icon">🎀✨</div>
                    <h2 class="card-title">Tapping into your curiosity</h2>
                </div>
                <div class="card" onclick="handleCardClick(2)">
                    <div class="icon">☂️</div>
                    <h2 class="card-title">Exploring the wonders of the internet</h2>
                </div>
            </div>
            <div class="dots" id="dots">
                <div class="dot active" onclick="goToSlide(0)"></div>
                <div class="dot" onclick="goToSlide(1)"></div>
                <div class="dot" onclick="goToSlide(2)"></div>
            </div>
        </div>
    </div>

    <script>
        let currentSlide = 0;
        const totalSlides = 3;
        let startX = 0;
        let currentX = 0;
        let isDragging = false;

        const cardsContainer = document.getElementById('cardsContainer');
        const dots = document.querySelectorAll('.dot');

        function updateDots() {
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentSlide);
            });
        }

        function goToSlide(index) {
            if (window.innerWidth <= 768) {
                currentSlide = index;
                const cardWidth = cardsContainer.querySelector('.card').offsetWidth;
                const gap = 20;
                const offset = -(currentSlide * (cardWidth + gap));
                cardsContainer.style.transform = `translateX(${offset}px)`;
                updateDots();
            }
        }

        function handleCardClick(index) {
            alert(`You clicked: ${['The joy of lifelong learning', 'Tapping into your curiosity', 'Exploring the wonders of the internet'][index]}`);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
