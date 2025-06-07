// This script fetches the game state from the Python backend and draws it on a canvas

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let CANVAS_WIDTH = 600;
let CANVAS_HEIGHT = 400;

// Function to fetch game state from Python backend
async function fetchGameState() {
    try {
        const response = await fetch('http://127.0.0.1:5000/game_state');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching game state:', error);
        return null;
    }
}

// Drawing function
function draw(gameState) {
    if (!gameState) return;

    // Ensure canvas matches backend config
    if (canvas.width !== gameState.screen.width) {
        canvas.width = gameState.screen.width;
    }
    if (canvas.height !== gameState.screen.height) {
        canvas.height = gameState.screen.height;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Ball
    ctx.beginPath();
    ctx.arc(gameState.ball.x, gameState.ball.y, gameState.ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
    ctx.closePath();

    // Draw Paddle (using 'paddle' data from backend)
    ctx.fillStyle = 'blue'; // Or another color for the paddle
    ctx.fillRect(gameState.paddle.x, gameState.paddle.y, gameState.paddle.width, gameState.paddle.height);

    // Draw Bricks (using gameState.bricks)
    const rowColors = ['red', 'orange', 'yellow'];
    const borderColor = 'black';
    gameState.bricks.forEach(brick => {
        const color = rowColors[brick.row % rowColors.length];
        ctx.fillStyle = color;
        ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
        ctx.strokeStyle = borderColor;
        ctx.lineWidth = 3;
        ctx.radius = 5;
        ctx.strokeRect(brick.x, brick.y, brick.width, brick.height);
    });
}

// Main animation loop
async function gameLoop() {
    const gameState = await fetchGameState();
    draw(gameState);
    requestAnimationFrame(gameLoop);
}

gameLoop();
