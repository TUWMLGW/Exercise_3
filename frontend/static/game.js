const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let selectedMode = 'Human Player';
let firstFetch = true;
let gameStarted = false;

// Start screen
document.getElementById('startButton').onclick = function() {
    selectedMode = document.querySelector('input[name="mode"]:checked').value;
    boardWidth = parseInt(document.getElementById('boardWidth').value, 10);
    boardHeight = parseInt(document.getElementById('boardHeight').value, 10);

    canvas.style.display = 'block';
    document.getElementById('resetButton').style.display = 'inline-block';
    document.querySelector('.info').style.display = 'block';
    document.getElementById('startScreen').style.display = 'none';
    gameStarted = true;
    firstFetch = true;
}

// Resetting the game
document.getElementById('resetButton').onclick = function() {
    document.getElementById('startScreen').style.display = 'flex';
    canvas.style.display = 'none';
    document.getElementById('resetButton').style.display = 'none';
    document.querySelector('.info').style.display = 'none';
    gameStarted = false;
    firstFetch = false;
}

// Function to get the game mode (AI Agent or Human Player)
function getGameMode() {
    return selectedMode;
}

// Human player paddle motion
let paddleAction = 0;
// Move paddle left and right using arrows
document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
        paddleAction = -1;
    } else if (event.key === 'ArrowRight') {
        paddleAction = 1;
    }
});
// Halt paddle movement when keys are released
document.addEventListener('keyup', (event) => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        paddleAction = 0;
    }
});

// Function to fetch game state from Python backend
async function fetchGameState() {
    const mode = getGameMode();
    let body = { mode: mode };
    if (mode === 'Human Player') {
        body.action = paddleAction;
    }
    if (firstFetch) {  
        body.boardWidth = boardWidth;
        body.boardHeight = boardHeight;
        firstFetch = false;
    }
    try {
        const response = await fetch('http://127.0.0.1:5000/game_state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await response.json();
        if (data.error) {
            alert(data.error);
            document.getElementById('resetButton').click();
            return null;
        }
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

    // Draw Score
    ctx.save();
    ctx.font = '20px Verdana';
    ctx.fillStyle = 'white';
    ctx.fillText("Score: " + (gameState.score || 0), 15, 25);
    ctx.restore();
}

// Main animation loop
async function gameLoop() {
    if (gameStarted) {
        const gameState = await fetchGameState();
        draw(gameState);
        requestAnimationFrame(gameLoop);
    } else {
        setTimeout(gameLoop, 100);
    }
    
}

gameLoop();
