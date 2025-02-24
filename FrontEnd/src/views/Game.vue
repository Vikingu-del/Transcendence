<template>
	<!-- <div class="game-container"> -->
	  <!-- <div class="game-header"> -->
		<!-- <h4 class="game-title">Game with {{ opponent }}</h4> -->
		<!-- <button @click="$emit('close')" class="btn secondary-btn">Close</button> -->
	  <!-- </div> -->
	  
	  <!-- <div class="game-content"> -->
		<!-- Show waiting message for host -->
		<!-- <div v-if="isWaiting" class="waiting-screen"> -->
		  <!-- <h2>Waiting for player to join...</h2> -->
		  <!-- <p>Share this game ID: {{ gameId }}</p> -->
		<!-- </div> -->
		
		<!-- Show join screen for guest -->
		<!-- <div v-else-if="!gameStarted && !isHost" class="join-screen"> -->
		  <!-- <button  -->
			<!-- @click="startGame"  -->
			<!-- class="btn primary-btn" -->
		  <!-- > -->
			<!-- Start Game -->
		  <!-- </button> -->
		<!-- </div> -->
		
		<!-- Game canvas -->
		<!-- <template v-else> -->
		  <!-- <canvas ref="gameCanvas" width="800" height="400"></canvas> -->
		  <!-- <div class="game-info"> -->
			<!-- <p class="score">{{ playerScore }} - {{ opponentScore }}</p> -->
		  <!-- </div> -->
		  <!-- <div class="game-controls" v-if="showNewGameButton"> -->
			<!-- <button  -->
			  <!-- @click="restartGame"  -->
			  <!-- class="btn primary-btn"
			>
			  Start New Game
			</button>
		  </div>
		</template>
	  </div>
	</div> --->
</template>
  
<!-- <script lang="ts">
import { defineComponent, ref } from 'vue';
import { onMounted, onUnmounted } from 'vue';

interface GameState {
	ball: {
		x: number;
		y: number;
		dx: number;
		dy: number;
		radius: number;
	};
	paddles: {
		player: { x: number; y: number; };
		opponent: { x: number; y: number; };
		width: number;
		height: number;
	};
	score: {
		player: number;
		opponent: number;
	};
}

export default defineComponent({
	name: 'Game',
	props: {
		opponent: {
		type: String,
		required: true
		},
		gameId: {
		type: String,
		required: true
		},
		isHost: {
		type: Boolean,
		default: false
		}
	},

	setup(props, { emit }) {
		// Add new reactive refs
		const isWaiting = ref(props.isHost);
		const gameStarted = ref(false);
		const gameSocket = ref<WebSocket | null>(null);
		const gameCanvas = ref<HTMLCanvasElement | null>(null);
		const ctx = ref<CanvasRenderingContext2D | null>(null);
		const animationFrame = ref<number>(0);
		const showNewGameButton = ref<boolean>(false);
		const playerScore = ref<number>(0);
		const opponentScore = ref<number>(0);
		const player1Username = ref<string>("");
		const player2Username = ref<string>("Waiting for Player 2...");

		const INITIAL_BALL_SPEED = 5;
		const CANVAS_WIDTH = 800;
		const CANVAS_HEIGHT = 400;
		const MIN_WIDTH = 450;

		// Add these new constants for game physics
		const MAX_BALL_SPEED = INITIAL_BALL_SPEED * 2;
		const PADDLE_SPEED = 10;
		const SPEED_INCREASE = 1.1;

		const gameState = ref<GameState>({
			ball: {
				x: CANVAS_WIDTH / 2,
				y: CANVAS_HEIGHT / 2,
				dx: INITIAL_BALL_SPEED,
				dy: INITIAL_BALL_SPEED,
				radius: 8
			},
			paddles: {
				player: { x: 50, y: CANVAS_HEIGHT / 2 - 40 },
				opponent: { x: CANVAS_WIDTH - 60, y: CANVAS_HEIGHT / 2 - 40 },
				width: 10,
				height: 80
			},
			score: {
				player: 0,
				opponent: 0
			}
		});

		const scaleFactor = ref(1);

		const initGame = () => {
			if (!gameCanvas.value) return;
			
			const container = gameCanvas.value.parentElement;
			if (!container) return;

			// Calculate new scale factor
			const containerWidth = Math.max(MIN_WIDTH, container.clientWidth);
			const containerHeight = container.clientHeight;
			scaleFactor.value = Math.min(
				containerWidth / CANVAS_WIDTH,
				containerHeight / CANVAS_HEIGHT
			);

			// Set the canvas display size
			const scaledWidth = CANVAS_WIDTH * scaleFactor.value;
			const scaledHeight = CANVAS_HEIGHT * scaleFactor.value;

			// Update canvas style dimensions
			gameCanvas.value.style.width = `${scaledWidth}px`;
			gameCanvas.value.style.height = `${scaledHeight}px`;

			// Keep the internal resolution constant
			gameCanvas.value.width = CANVAS_WIDTH;
			gameCanvas.value.height = CANVAS_HEIGHT;

			// Reset context
			ctx.value = gameCanvas.value.getContext('2d');
			if (!ctx.value) return;

			ctx.value.fillStyle = 'white';
			ctx.value.strokeStyle = 'white';
		};

		const gameLoop = () => {
			if (!ctx.value || !gameCanvas.value) return;

			// Clear canvas
			ctx.value.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

			// Update game state
			updateGame();

			// Draw game objects
			drawGame();

			// Continue loop
			animationFrame.value = requestAnimationFrame(gameLoop);
		};

		const lastUpdate = ref(Date.now());

		const updateGameState = (state: GameState) => {
			gameState.value = state;
		}; -->

		<!-- const updateGame = () => {
			const now = Date.now();
			const deltaTime = (now - lastUpdate.value) / 16.67; // normalize to 60fps
			lastUpdate.value = now;

			const { ball, paddles, score } = gameState.value;

			// Update ball position with deltaTime
			ball.x += ball.dx * deltaTime;
			ball.y += ball.dy * deltaTime;

			// Ball collision with top and bottom walls
			if (ball.y <= ball.radius || ball.y >= CANVAS_HEIGHT - ball.radius) {
				ball.dy *= -1;
			}

			// Ball collision with paddles
			if (checkPaddleCollision()) {
				ball.dx *= -1;
				// Limit maximum ball speed
				const maxSpeed = INITIAL_BALL_SPEED * 2;
				ball.dx = Math.min(Math.abs(ball.dx), maxSpeed) * (ball.dx > 0 ? 1 : -1);
			}

			// Score points
			if (ball.x <= 0) {
				score.opponent++;
				opponentScore.value = score.opponent;
				resetBall();
				checkGameOver();
			} else if (ball.x >= CANVAS_WIDTH) {
				score.player++;
				playerScore.value = score.player;
				resetBall();
				checkGameOver();
			}

			// AI movement
			const aiSpeed = 4;
			if (paddles.opponent.y + paddles.height / 2 < ball.y) {
				paddles.opponent.y = Math.min(paddles.opponent.y + aiSpeed, CANVAS_HEIGHT - paddles.height);
			} else {
				paddles.opponent.y = Math.max(paddles.opponent.y - aiSpeed, 0);
			}
		}; -->

		<!-- const drawGame = () => {
			if (!ctx.value) return;
			const { ball, paddles } = gameState.value;

			// Draw paddles
			ctx.value.fillRect(
				paddles.player.x,
				paddles.player.y,
				paddles.width,
				paddles.height
			);
			ctx.value.fillRect(
				paddles.opponent.x,
				paddles.opponent.y,
				paddles.width,
				paddles.height
			);

			// Draw ball
			ctx.value.beginPath();
			ctx.value.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
			ctx.value.fill();
		};

		const checkPaddleCollision = (): boolean => {
			const { ball, paddles } = gameState.value;
			
			// Check collision with player paddle
			if (
				ball.x - ball.radius <= paddles.player.x + paddles.width &&
				ball.x + ball.radius >= paddles.player.x &&
				ball.y >= paddles.player.y &&
				ball.y <= paddles.player.y + paddles.height
			) {
				// Increase speed but cap it
				ball.dx = Math.min(Math.abs(ball.dx) * SPEED_INCREASE, MAX_BALL_SPEED) * -1;
				return true;
			}

			// Check collision with opponent paddle
			if (
				ball.x + ball.radius >= paddles.opponent.x &&
				ball.x - ball.radius <= paddles.opponent.x + paddles.width &&
				ball.y >= paddles.opponent.y &&
				ball.y <= paddles.opponent.y + paddles.height
			) {
				// Increase speed but cap it
				ball.dx = Math.min(Math.abs(ball.dx) * SPEED_INCREASE, MAX_BALL_SPEED);
				return true;
			}

			return false;
		};

		const resetBall = () => {
			const { ball } = gameState.value;
			ball.x = CANVAS_WIDTH / 2;
			ball.y = CANVAS_HEIGHT / 2;
			ball.dx = INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1);
			ball.dy = INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1);
		};

		const checkGameOver = () => {
			const { score } = gameState.value;
			if (score.player >= 5 || score.opponent >= 5) {
				cancelAnimationFrame(animationFrame.value);
				showNewGameButton.value = true;
				emit('gameOver', {
				winner: score.player > score.opponent ? 'player' : 'opponent',
				playerScore: score.player,
				opponentScore: score.opponent
				});
			}
		};

		const saveGameResult = async (player1Score: number, player2Score: number) => {
			try {
				const response = await fetch(`/pong/game/${props.gameId}/save/`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${localStorage.getItem('token')}`,
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					player1_score: player1Score,
					player2_score: player2Score
				})
				});
				const data = await response.json();
				console.log('Match result saved!', data);
			} catch (error) {
				console.error('Error saving game result:', error);
			}
		};

		const handleKeyDown = (e: KeyboardEvent) => {
			const { paddles } = gameState.value;
			
			if (e.key === 'ArrowUp' && paddles.player.y > 0) {
				paddles.player.y = Math.max(0, paddles.player.y - PADDLE_SPEED);
				sendPaddleUpdate();
			}
			if (e.key === 'ArrowDown' && paddles.player.y < CANVAS_HEIGHT - paddles.height) {
				paddles.player.y = Math.min(CANVAS_HEIGHT - paddles.height, paddles.player.y + PADDLE_SPEED);
				sendPaddleUpdate();
			}
		};

		// Update the initializeGameSocket function
		const initializeGameSocket = () => {
			try {
				const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'; -->
				<!-- const wsHost = window.location.hostname;
				const token = localStorage.getItem('token');
				// Use the UUID directly, no need to clean it
				const wsUrl = `${wsProtocol}//${wsHost}/ws/game/${props.gameId}/?token=${token}`;
				
				console.log('Connecting to WebSocket:', wsUrl);
				
				gameSocket.value = new WebSocket(wsUrl);
				
				gameSocket.value.onopen = () => {
				console.log('Game WebSocket connection established');
				if (!props.isHost) {
					gameSocket.value?.send(JSON.stringify({
					type: 'join_game',
					gameId: props.gameId
					}));
				}
				};
				
				gameSocket.value.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);
					console.log('Received game message:', data);
					handleGameMessage(data);
				} catch (error) {
					console.error('Error parsing game message:', error);
				}
				};
				
				gameSocket.value.onerror = (error) => {
				console.error('Game WebSocket error:', error);
				};
				
				gameSocket.value.onclose = (event) => {
				console.log('Game WebSocket closed:', event);
				if (!event.wasClean && gameStarted.value) {
					console.log('Game connection lost, attempting to reconnect...');
					setTimeout(initializeGameSocket, 3000);
				}
				};
			} catch (error) {
				console.error('Error initializing game WebSocket:', error);
			}
		};

		const handleGameMessage = (data: any) => {
			if (data.player1_username && data.player2_username) {
				// Update player names immediately when received
				player1Username.value = data.player1_username;
				player2Username.value = data.player2_username === "Waiting for Player 2" 
					? "Waiting for Player 2..."
					: data.player2_username;
			}
					: data.player2_username;
			}

			switch (data.type) {
				case 'player_joined':
				if (props.isHost) {
					console.log('Player joined, waiting for them to start');
					isWaiting.value = false;
				}
				break;

				case 'game_start':
				console.log('Game starting');
				gameStarted.value = true;
				startGame();
				break;

				case 'paddle_move':
				if (data.player !== props.isHost) {
					gameState.value.paddles.opponent.y = data.y;
					// Send paddle position to opponent if we're the host
					if (props.isHost && gameSocket.value?.readyState === WebSocket.OPEN) {
					gameSocket.value.send(JSON.stringify({
						type: 'paddle_update',
						y: gameState.value.paddles.player.y
					}));
					}
				}
				break;

				case 'ball_update':
				if (!props.isHost) {
					gameState.value.ball = data.ball;
					gameState.value.score = data.score;
					playerScore.value = data.score.player;
					opponentScore.value = data.score.opponent;
				}
				break;

				case 'game_over':
				handleGameOver(data);
				break;
			}
		};


		const startGame = () => {
			if (!gameSocket.value || gameSocket.value.readyState !== WebSocket.OPEN) {
				console.error('WebSocket not connected');
				return;
			}

			// Only send start_game message if we're not the host
			if (!props.isHost) {
				gameSocket.value.send(JSON.stringify({
				type: 'start_game'
				}));
			}

			gameStarted.value = true;
			resetBall();
			gameLoop();
		};

		const sendPaddleUpdate = () => {
			if (gameSocket.value?.readyState === WebSocket.OPEN) {
				gameSocket.value.send(JSON.stringify({
				type: 'paddle_move',
				y: gameState.value.paddles.player.y
				}));
			}
		};

		

		const handleGameOver = (data: any) => {
			cancelAnimationFrame(animationFrame.value);
			showNewGameButton.value = true;
			emit('gameOver', {
				winner: data.winner,
				playerScore: data.score.player,
				opponentScore: data.score.opponent
			});
		};


		const cleanup = () => {
			if (gameSocket.value) {
				gameSocket.value.close();
			}
			cancelAnimationFrame(animationFrame.value);
			window.removeEventListener('keydown', handleKeyDown);
		};

		const restartGame = async () => {
			try {
				const response = await fetch(`/pong/start-new-game/${props.gameId}/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				}
				});
				const data = await response.json();
				
				if (data.new_game_url) {
				window.location.href = data.new_game_url;
				} else {
				// Reset local game state if no redirect
				gameState.value.score.player = 0;
				gameState.value.score.opponent = 0;
				playerScore.value = 0;
				opponentScore.value = 0;
				showNewGameButton.value = false;
				resetBall();
				gameLoop();
				}
			} catch (error) {
				console.error('Error starting new game:', error);
			}
		};

		let resizeObserver: ResizeObserver | null = null;

		onMounted(() => {
			initGame();
			initializeGameSocket();
			window.addEventListener('keydown', handleKeyDown);
			
			// Update resize observer to preserve game state
			if (gameCanvas.value) {
				resizeObserver = new ResizeObserver(() => {
					// Store current game state
					const currentState = { ...gameState.value };
					
					// Reinitialize canvas
					initGame();
					
					// Restore game state
					gameState.value = currentState;
				});
				resizeObserver.observe(gameCanvas.value.parentElement as Element);
			}
		});		

		onUnmounted(() => {
			cancelAnimationFrame(animationFrame.value);
			window.removeEventListener('keydown', handleKeyDown);
			cleanup();
			
			// Cleanup resize observer
			if (resizeObserver) {
				resizeObserver.disconnect();
			}
		});

			playerScore,
			opponentScore,
			showNewGameButton,
			restartGame,
			isWaiting,
			gameStarted,
			startGame,
			player1Username,
			player2Username,
			gameStarted,
			startGame,
		};
	}
});
</script>
  
<style scoped>
.game-container {
  background: #1a1a1a;
  border-radius: 10px;
  overflow: hidden;
  width: 75%;
  max-width: 1200px;
  min-width: 450px;
  height: 75vh;
  min-height: 500px; /* Add minimum height */
  display: flex;
  flex-direction: column;
  box-shadow: 2px 2px 30px #03a670;
  position: relative; /* Add this */
}

.game-header {
  background: #2d2d2d;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 10px 10px 0 0;
  z-index: 2;
}

.game-title {
  color: white;
  margin: 0;
  font-size: 1.2rem;
}

.game-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  position: relative;
  background: #1a1a1a;
  min-height: 0;
}

canvas {
  background: black;
  border-radius: 4px;
  max-width: 100%;
  max-height: calc(100% - 80px); /* Account for score and buttons */
  width: auto;
  height: auto;
  object-fit: contain;
  margin: auto;
}

.game-info {
  position: absolute;
  top: 1rem;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  z-index: 1;
}

.game-controls {
  position: absolute;
  bottom: 1rem;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  z-index: 1;
}


.score {
  color: white;
  font-size: 2rem;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  margin: 0;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s ease;
  min-width: 120px;
}

.primary-btn {
  background: #03a670;
  color: white;
}

.primary-btn:hover {
  background: #04d38e;
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(3, 166, 112, 0.3);
}

.secondary-btn {
  background: #a60303;
  color: white;
}

.secondary-btn:hover {
  background: #d30404;
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(166, 3, 3, 0.3);
}

.waiting-screen,
.join-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  height: 100%;
  color: white;
}

.waiting-screen h2 {
  color: #03a670;
  margin-bottom: 1rem;
}

.waiting-screen p {
  color: white;
  background: #2d2d2d;
  padding: 1rem;
  border-radius: 4px;
  font-family: monospace;
}

@media (max-width: 768px) {
  .game-container {
    width: 95%;
    min-width: 450px;
  }

  .game-content {
    padding: 0.5rem;
  }

  .score {
    font-size: 1.5rem;
  }

  canvas {
    max-height: calc(100% - 60px); /* Adjust for smaller screens */
  }
}
</style> -->