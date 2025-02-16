document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("pongCanvas");
    const ctx = canvas.getContext("2d");

    const paddleWidth = 10, paddleHeight = 60;
    let paddle1Y = (canvas.height - paddleHeight) / 2;
    let paddle2Y = (canvas.height - paddleHeight) / 2;
    let ballX = canvas.width / 2, ballY = canvas.height / 2;
    let ballSpeedX = 4, ballSpeedY = 3;

    function draw() {
        ctx.fillStyle = "black";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "white";
        ctx.fillRect(10, paddle1Y, paddleWidth, paddleHeight);
        ctx.fillRect(canvas.width - 20, paddle2Y, paddleWidth, paddleHeight);

        ctx.beginPath();
        ctx.arc(ballX, ballY, 8, 0, Math.PI * 2);
        ctx.fill();

        ballX += ballSpeedX;
        ballY += ballSpeedY;

        if (ballY <= 0 || ballY >= canvas.height) {
            ballSpeedY = -ballSpeedY;
        }
    }

    function gameLoop() {
        draw();
        requestAnimationFrame(gameLoop);
    }

    gameLoop();
});

