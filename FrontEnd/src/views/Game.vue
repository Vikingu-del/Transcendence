<template>
	<div class="game-container">
		<div class="game-header">
            <h4 class="game-title">Game with {{ opponent }}</h4>
            <button @click="$emit('close')" class="btn secondary-btn">Close</button>
        </div>
        
        <div class="game-content">
            <!-- Show waiting message for host -->
            <div v-if="isWaiting && !gameAccepted" class="waiting-screen">
                <h2>Waiting for player to join...</h2>
            </div>
            
            <!-- Show game accepted screen -->
            <div v-else-if="gameAccepted && !gameStarted" class="acceptance-screen">
				<h2>Game Accepted!</h2>
				<p>Starting game with {{ opponent }}...</p>
				<button 
					v-if="isLocalHost"
					@click="startGame" 
					class="btn primary-btn"
				>
					Start Game
				</button>
				<p v-else class="waiting-message">
					Waiting for host to start the game...
				</p>
			</div>
		<canvas 
			ref="gameCanvas"
			:width=800
			:height=400
			:style="{
				display: gameStarted ? 'block' : 'none',
				background: '#000000'
			}"
		></canvas>

		<div v-if="gameStarted" class="game-info">
			<p class="score">{{ playerScore }} - {{ opponentScore }}</p>
		</div>
		
	  </div>
	</div>
</template>
  
<script lang="ts">
import { defineComponent, ref, nextTick } from 'vue';
import { onMounted, onUnmounted, watch } from 'vue';

interface GameState {
	ball: Float32Array; // [x, y, dx, dy, radius]
	paddles: Float32Array; // [playerX, playerY, opponentX, opponentY, width, height]
	score: Uint8Array; // [player, opponent]
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
		},
		userId: {
			type: Number,
			required: true
		}
	},

	setup(props, { emit }) {
		const initLocalStorage = (gameId: string) => {
			const gameKey = `pong_game_${gameId}`;
			const storedGame = localStorage.getItem(gameKey);
			if (!storedGame) {
				localStorage.setItem(gameKey, JSON.stringify({
				playerScore: 0,
				opponentScore: 0,
				timestamp: Date.now()
				}));
			}
			return gameKey;
		};

		const updateLocalScore = (gameKey: string, playerScore: number, opponentScore: number) => {
			localStorage.setItem(gameKey, JSON.stringify({
				playerScore,
				opponentScore,
				timestamp: Date.now()
			}));
		};

		const getLocalScore = (gameKey: string) => {
			const stored = localStorage.getItem(gameKey);
			if (stored) {
				return JSON.parse(stored);
			}
			return { playerScore: 0, opponentScore: 0 };
		};

		// At the start of your setup function
		// Add new reactive refs
		const isLocalHost = ref<boolean>(props.isHost);
		const isWaiting = ref<boolean>(props.isHost);
		const gameStarted = ref<boolean>(false);
		const gameAccepted = ref<boolean>(false);
		const gameSocket = ref<WebSocket | null>(null);
		const gameCanvas = ref<HTMLCanvasElement | null>(null);
		const ctx = ref<CanvasRenderingContext2D | null>(null);
		const animationFrame = ref<number>(0);
		const showNewGameButton = ref<boolean>(false);
		const playerScore = ref<number>(0);
		const opponentScore = ref<number>(0);
		const gameKey = ref(initLocalStorage(props.gameId));

		const CANVAS_WIDTH = 800;
		const CANVAS_HEIGHT = 400;
		const INITIAL_BALL_SPEED = 3;
		const PADDLE_SPEED = 40;
		const BALL_RADIUS = 8; 
		const SPEED_REDUCTION = 0.9; // New constant for speed reduction on collisions
		const ANGLE_FACTOR = 0.50; // New constant for angle factor on collisions
		const MAX_BALL_SPEED = INITIAL_BALL_SPEED * 1.5;
		const SPEED_INCREASE = 1.05;

		const FRAME_TIME = 1000 / 60;
		const MAX_DELTA_TIME = 1000 / 30; // Cap at 30 FPS minimum
		const SYNC_INTERVAL = 16; 
		const lastFrameTime = ref(0);
		const lastSyncTime = ref(0);
		const PADDLE_UPDATE_INTERVAL = 50; // Send paddle updates every 50ms
		const lastPaddleUpdate = ref(0);
		const pressedKeys = ref<Set<string>>(new Set());
		const playerId = ref<string>('');
		const isHost = ref<boolean>(false);

		const PLAYER_POSITIONS = {
			HOST: {
				PADDLE_X: 50,
				PADDLE_INDEX: 0 // Index 0 and 1 for left paddle position/height
			},
			GUEST: {
				PADDLE_X: CANVAS_WIDTH - 60,
				PADDLE_INDEX: 2 // Index 2 and 3 for right paddle position/height
			}
		};
		
		// Update userPaddleIndex initialization
		const userPaddleIndex = ref(isLocalHost.value ? 
			PLAYER_POSITIONS.HOST.PADDLE_INDEX : 
			PLAYER_POSITIONS.GUEST.PADDLE_INDEX
		);
		

		const gameState = ref<GameState>({
			ball: new Float32Array([
				CANVAS_WIDTH / 2,  // x [0]
				CANVAS_HEIGHT / 2, // y [1]
				INITIAL_BALL_SPEED,// dx [2]
				INITIAL_BALL_SPEED * 0.5, // dy [3]
				BALL_RADIUS       // radius [4]
			]),
			paddles: new Float32Array([
				PLAYER_POSITIONS.HOST.PADDLE_X,    // Host paddle x [0]
				CANVAS_HEIGHT / 2 - 40,           // Host paddle y [1]
				PLAYER_POSITIONS.GUEST.PADDLE_X,   // Guest paddle x [2]
				CANVAS_HEIGHT / 2 - 40,           // Guest paddle y [3]
				10,                               // width [4]
				80                                // height [5]
			]),
			score: new Uint8Array([0, 0]) // [player, opponent]
		});

		const scaleFactor = ref(1);


		const initGame = () => {
			if (!gameCanvas.value) {
				return false;
			}

			const context = gameCanvas.value.getContext('2d');
			if (!context) {
				return false;
			}
			ctx.value = context;

			gameCanvas.value.width = CANVAS_WIDTH;
			gameCanvas.value.height = CANVAS_HEIGHT;

			playerId.value = props.userId.toString();
   			isHost.value = props.isHost;

			// Initialize game state with typed arrays
			gameState.value = {
				ball: new Float32Array([
					CANVAS_WIDTH / 2,  // x [0]
					CANVAS_HEIGHT / 2, // y [1]
					INITIAL_BALL_SPEED,// dx [2]
					INITIAL_BALL_SPEED * 0.5, // dy [3]
					BALL_RADIUS       // radius [4]
				]),
				paddles: new Float32Array([
					isLocalHost.value ? 50 : CANVAS_WIDTH - 60, // player x [0]
					CANVAS_HEIGHT / 2 - 40, // player y [1]
					isLocalHost.value ? CANVAS_WIDTH - 60 : 50, // opponent x [2]
					CANVAS_HEIGHT / 2 - 40, // opponent y [3]
					10,  // width [4]
					80   // height [5]
				]),
				score: new Uint8Array([0, 0]) // [player, opponent]
			};

			return true;
		};
		
		const gameLoop = () => {
			if (!gameCanvas.value || !ctx.value) return;

			const now = performance.now();
			const deltaTime = Math.min(now - lastFrameTime.value, MAX_DELTA_TIME);
			const normalizedDelta = deltaTime / FRAME_TIME;

			if (deltaTime >= FRAME_TIME) {
				// Update paddle position for both players
				updatePaddlePosition(normalizedDelta);

				// Update game state with deltaTime (only for host)
				if (isLocalHost.value) {
					updateGame(normalizedDelta);
					
					// Send ball updates at regular intervals
					const timeSinceLastSync = now - lastSyncTime.value;
					if (timeSinceLastSync >= SYNC_INTERVAL) {
						sendBallUpdate();
						lastSyncTime.value = now;
					}
				}

				// Draw game state for both players
				drawGame();
				lastFrameTime.value = now;
			}

			animationFrame.value = requestAnimationFrame(gameLoop);
		};

		const sendBallUpdate = () => {
			if (gameSocket.value?.readyState === WebSocket.OPEN && isLocalHost.value) {
				const { ball, score } = gameState.value;
				gameSocket.value.send(JSON.stringify({
					type: 'ball_update',
					x: Math.round(ball[0]),     
					y: Math.round(ball[1]),
				}));
			}
		};

		const lastUpdate = ref(Date.now());

		const updateGameState = (state: GameState) => {
			gameState.value = state;
		};

		const updateGame = (delta: number) => {
			const { ball, paddles, score } = gameState.value;

			// Update ball position
			ball[0] += ball[2] * delta; // x += dx
			ball[1] += ball[3] * delta; // y += dy

			// Ball collision with top and bottom walls
			if (ball[1] + ball[4] > CANVAS_HEIGHT) { // y + radius > height
				ball[1] = CANVAS_HEIGHT - ball[4]; // Keep ball within bounds
				ball[3] = -ball[3] * SPEED_REDUCTION; // Reverse and reduce vertical speed
			} else if (ball[1] - ball[4] < 0) { // y - radius < 0
				ball[1] = ball[4]; // Keep ball within bounds
				ball[3] = -ball[3] * SPEED_REDUCTION; // Reverse and reduce vertical speed
			}

			// Ball collision with player paddle
			if (ball[0] - ball[4] <= paddles[0] + paddles[4] && // x - radius <= playerX + width
				ball[1] >= paddles[1] && // y >= playerY
				ball[1] <= paddles[1] + paddles[5] && // y <= playerY + height
				ball[2] < 0) { // Moving left
				
				ball[0] = paddles[0] + paddles[4] + ball[4]; // Prevent sticking
				ball[2] = -ball[2] * SPEED_REDUCTION; // Reverse and reduce horizontal speed
				
				// Add angle based on hit position
				const deltaY = ball[1] - (paddles[1] + paddles[5] / 2);
				ball[3] = deltaY * ANGLE_FACTOR;
			}
			
			// Ball collision with opponent paddle
			else if (ball[0] + ball[4] >= paddles[2] && // x + radius >= opponentX
				ball[1] >= paddles[3] && // y >= opponentY
				ball[1] <= paddles[3] + paddles[5] && // y <= opponentY + height
				ball[2] > 0) { // Moving right
				
				ball[0] = paddles[2] - ball[4]; // Prevent sticking
				ball[2] = -ball[2] * SPEED_REDUCTION; // Reverse and reduce horizontal speed
				
				// Add angle based on hit position
				const deltaY = ball[1] - (paddles[3] + paddles[5] / 2);
				ball[3] = deltaY * ANGLE_FACTOR;
			}

			// Scoring
			if (ball[0] - ball[4] < 0) { // Left boundary
				score[1]++; // Opponent scores
				opponentScore.value = score[1];
				updateLocalScore(gameKey.value, playerScore.value, opponentScore.value);
				resetBall();
				checkGameOver();
			}
			else if (ball[0] + ball[4] > CANVAS_WIDTH) { // Right boundary
				score[0]++; // Player scores
				playerScore.value = score[0];
				updateLocalScore(gameKey.value, playerScore.value, opponentScore.value);
				resetBall();
				checkGameOver();
			}
		};


		const drawGame = () => {
			if (!ctx.value || !gameCanvas.value) return;
			
			const { ball, paddles, score } = gameState.value;

			// Clear canvas
			ctx.value.fillStyle = '#000000';
			ctx.value.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

			// Draw center line
			ctx.value.strokeStyle = '#ffffff';
			ctx.value.setLineDash([5, 15]);
			ctx.value.beginPath();
			ctx.value.moveTo(CANVAS_WIDTH / 2, 0);
			ctx.value.lineTo(CANVAS_WIDTH / 2, CANVAS_HEIGHT);
			ctx.value.stroke();
			ctx.value.setLineDash([]);

			// Draw paddles
			ctx.value.fillStyle = '#03a670';
			
			// Player paddle
			ctx.value.beginPath();
			ctx.value.roundRect(
				paddles[0],  // x
				paddles[1],  // y
				paddles[4],  // width
				paddles[5],  // height
				[5]
			);
			ctx.value.fill();

			// Opponent paddle
			ctx.value.beginPath();
			ctx.value.roundRect(
				paddles[2],  // x
				paddles[3],  // y
				paddles[4],  // width
				paddles[5],  // height
				[5]
			);
			ctx.value.fill();

			// Draw ball with glow effect
			ctx.value.fillStyle = '#ffffff';
			ctx.value.shadowBlur = 15;
			ctx.value.shadowColor = '#03a670';
			ctx.value.beginPath();
			ctx.value.arc(ball[0], ball[1], ball[4], 0, Math.PI * 2);
			ctx.value.fill();
			ctx.value.shadowBlur = 0;
		};


		const checkPaddleCollision = (): boolean => {
			const { ball, paddles } = gameState.value;
			
			// Check collision with player paddle
			if (ball[0] - ball[4] <= paddles[0] + paddles[4] && // x - radius <= playerX + width
				ball[1] >= paddles[1] && // y >= playerY
				ball[1] <= paddles[1] + paddles[5]) { // y <= playerY + height
				
				const deltaY = ball[1] - (paddles[1] + paddles[5] / 2);
				ball[3] = deltaY * ANGLE_FACTOR;
				ball[2] = Math.abs(ball[2]); // Ensure ball moves right
				return true;
			}

			// Check collision with opponent paddle
			if (ball[0] + ball[4] >= paddles[2] && // x + radius >= opponentX
				ball[1] >= paddles[3] && // y >= opponentY
				ball[1] <= paddles[3] + paddles[5]) { // y <= opponentY + height
				
				const deltaY = ball[1] - (paddles[3] + paddles[5] / 2);
				ball[3] = deltaY * ANGLE_FACTOR;
				ball[2] = -Math.abs(ball[2]); // Ensure ball moves left
				return true;
			}

			return false;
		};
		const resetBall = () => {
			const { ball } = gameState.value;
			ball[0] = CANVAS_WIDTH / 2;  // x
			ball[1] = CANVAS_HEIGHT / 2; // y
			ball[2] = INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1); // dx
			ball[3] = INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1) * 0.5; // dy
		};


		const checkGameOver = () => {
			const { score } = gameState.value;
			if (score[0] >= 5 || score[1] >= 5) {
				cancelAnimationFrame(animationFrame.value);
				showNewGameButton.value = true;
				emit('gameOver', {
					winner: score[0] > score[1] ? 'player' : 'opponent',
					playerScore: score[0],
					opponentScore: score[1]
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
				// console.log('Match result saved!', data);
			} catch (error) {
				console.error('Error saving game result:', error);
			}
		};

		const handleKeyDown = (e: KeyboardEvent) => {
			if (!gameStarted.value) return;
			if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
				pressedKeys.value.add(e.key);
			}
		};

		const handleKeyUp = (e: KeyboardEvent) => {
			if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
				pressedKeys.value.delete(e.key);
			}
		};

		const updatePaddlePosition = (delta: number) => {
			if (!gameStarted.value) return;

			const { paddles } = gameState.value;
			const adjustedSpeed = PADDLE_SPEED * delta;
			let paddleChanged = false;
			
			// Get the correct paddle Y index based on whether we're host or guest
			const myPaddleIndex = isLocalHost.value ? 1 : 3; // Index 1 for host, 3 for guest
			let newPosition = paddles[myPaddleIndex];
			
			if (pressedKeys.value.has('ArrowUp')) {
				newPosition = Math.max(0, newPosition - adjustedSpeed);
				paddleChanged = true;
			}
			if (pressedKeys.value.has('ArrowDown')) {
				newPosition = Math.min(CANVAS_HEIGHT - paddles[5], newPosition + adjustedSpeed);
				paddleChanged = true;
			}

			if (paddleChanged) {
				paddles[myPaddleIndex] = newPosition;
				sendPaddleUpdate(newPosition);
			}
		};

		// Update the initializeGameSocket function
		const initializeGameSocket = () => {
			try {
				const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
				const wsHost = window.location.hostname;
				const token = localStorage.getItem('token');
				const wsUrl = `${wsProtocol}//${wsHost}/ws/game/${props.gameId}/?token=${token}`;
				
				console.log('Connecting to WebSocket:', wsUrl);
				
				if (gameSocket.value) {
					gameSocket.value.close();
				}
				
				gameSocket.value = new WebSocket(wsUrl);
				
				// Add connection retry logic
				let retryCount = 0;
        		const maxRetries = 3;

				gameSocket.value.onopen = () => {
					console.log('Game WebSocket connected');
					retryCount = 0; // Reset retry count on successful connection
					
					// Send initial join message
					if (!isLocalHost.value) {
						gameSocket.value?.send(JSON.stringify({
							type: 'join_game',
							gameId: props.gameId
						}));
					}
				};
        
				
				gameSocket.value.onmessage = (event) => {
					try {
						const data = JSON.parse(event.data);
						// console.log('Received game message:', data);
						
						// Handle the message in the next tick to ensure state updates are synchronized
						nextTick(() => {
							handleGameMessage(data);
						});
					} catch (error) {
						console.error('Error parsing game message:', error);
					}
				};
				
				gameSocket.value.onerror = (error) => {
					console.error('Game WebSocket error:', error);
				};
				
				gameSocket.value.onclose = (event) => {
					console.log('Game WebSocket closed:', event);
					
					// Only attempt to reconnect if the game is still active
					if (gameStarted.value && retryCount < maxRetries) {
						console.log(`Attempting to reconnect (${retryCount + 1}/${maxRetries})...`);
						retryCount++;
						setTimeout(initializeGameSocket, 1000 * retryCount);
					} else if (retryCount >= maxRetries) {
						console.log('Max reconnection attempts reached');
						emit('connectionLost');
					}
				};
			} catch (error) {
				console.error('Error initializing game WebSocket:', error);
			}
		};

		const handleGameMessage = (data: any) => {
			switch (data.type) {
				case 'game_state':
					if (data.game_status === 'accepted') {
						gameAccepted.value = true;
						isWaiting.value = false;
						isLocalHost.value = props.isHost;
					} else if (data.game_status === 'waiting') {
						isWaiting.value = true;
						gameAccepted.value = false;
						isLocalHost.value = props.isHost;
					} else if (data.game_status === 'started') {
						if (!initGame()) { return; }
						gameStarted.value = true;
						gameAccepted.value = true;
						isWaiting.value = false;
						resetBall();
						gameLoop();
					} else if (data.game_status === 'ended') {
						handleGameOver(data);
					}
					break;
				
				case 'paddle_move':
					const { paddles } = gameState.value;
					const isHostMessage = String(data.host_id) === String(props.userId);
					
					// Update the opposite paddle from the sender
					// If host sent the message, update index 1 (left paddle)
					// If guest sent the message, update index 3 (right paddle)
					if (isHostMessage) {
						// Message is from host, update left paddle (index 1)
						paddles[1] = data.y;
					} else {
						// Message is from guest, update right paddle (index 3)
						paddles[3] = data.y;
					}
					break;


				case 'ball_update':
					if (!isLocalHost.value) {
					const { ball, score } = data;
					
					if (ball) {
						gameState.value.ball[0] = ball.x;
						gameState.value.ball[1] = ball.y;
						gameState.value.ball[2] = ball.dx;
						gameState.value.ball[3] = ball.dy;
						gameState.value.ball[4] = ball.radius;
					}

					if (Array.isArray(score)) {
						gameState.value.score[0] = score[0];
						gameState.value.score[1] = score[1];
						
						// Update local storage with new scores
						const newPlayerScore = isLocalHost.value ? score[0] : score[1];
						const newOpponentScore = isLocalHost.value ? score[1] : score[0];
						
						playerScore.value = newPlayerScore;
						opponentScore.value = newOpponentScore;
						updateLocalScore(gameKey.value, newPlayerScore, newOpponentScore);
					}
					}
					break;
			}
		};

		const startGame = () => {
			if (!gameSocket.value || gameSocket.value.readyState !== WebSocket.OPEN) {
				console.error('WebSocket not connected');
				return;
			}

			if (isLocalHost.value) {
				console.log('Host starting game...');
				
				// Initialize game first
				if (!initGame()) {
					console.error('Failed to initialize game');
					return;
				}

				// Send start game message
				gameSocket.value.send(JSON.stringify({
					type: 'game_start',
					game_id: props.gameId,
					host_id: props.userId
				}));


			}
		};


		const sendPaddleUpdate = (yPosition: number) => {
			const now = performance.now();
			if (now - lastPaddleUpdate.value >= PADDLE_UPDATE_INTERVAL && 
				gameSocket.value?.readyState === WebSocket.OPEN) {
				
				gameSocket.value.send(JSON.stringify({
					type: 'paddle_move',
					y: yPosition,
					host_id: props.userId,
					timestamp: now,
					is_host: isLocalHost.value // Add this to identify the sender's role
				}));
				lastPaddleUpdate.value = now;
			}
		};


		const isConnected = ref(false);
		const checkConnection = () => {
			if (gameSocket.value) {
				isConnected.value = gameSocket.value.readyState === WebSocket.OPEN;
			}
		};


		// Modify handleGameOver to save final score
		const handleGameOver = async (data: any) => {
			cancelAnimationFrame(animationFrame.value);
			showNewGameButton.value = true;

			// Get final scores from localStorage
			const finalScores = getLocalScore(gameKey.value);

			// Save to database only at game end
			if (gameSocket.value?.readyState === WebSocket.OPEN) {
			gameSocket.value.send(JSON.stringify({
				type: 'game_end',
				winner_id: data.winner === 'player' ? props.userId : data.opponent_id,
				final_score: {
				player1: finalScores.playerScore,
				player2: finalScores.opponentScore
				}
			}));
			}

			// Clear local storage for this game
			localStorage.removeItem(gameKey.value);

			emit('gameOver', {
			winner: data.winner,
			playerScore: finalScores.playerScore,
			opponentScore: finalScores.opponentScore
			});
		};


		onUnmounted(() => {
			cleanup();
			localStorage.removeItem(gameKey.value);
		});

		const cleanup = () => {
			if (gameSocket.value) {
				gameSocket.value.onclose = null;
				gameSocket.value.close();
			}
			cancelAnimationFrame(animationFrame.value);
			window.removeEventListener('keydown', handleKeyDown);
			window.removeEventListener('keyup', handleKeyUp);
			pressedKeys.value.clear();
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
					// Reset local game state
					gameState.value.score.set([0, 0]);
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
			// Wait for the next tick when the template is rendered
			nextTick(async () => {
				// Wait a small amount of time to ensure canvas is mounted
				await new Promise(resolve => setTimeout(resolve, 100));
				
				if (!gameCanvas.value) {
					console.error('Canvas ref not found after mount');
					return;
				}

				// console.log('Canvas element found:', {
				// 	element: gameCanvas.value,
				// 	width: gameCanvas.value.width,
				// 	height: gameCanvas.value.height
				// });

				// Initialize game components
				initGame();

				window.addEventListener('keydown', handleKeyDown);
				window.addEventListener('keyup', handleKeyUp);
				
				if (ctx.value && gameCanvas.value) {
					console.log('Game components initialized successfully');
					initializeGameSocket();
					window.addEventListener('keydown', handleKeyDown);
				} else {
					console.error('Failed to initialize game components:', {
						context: !!ctx.value,
						canvas: !!gameCanvas.value
					});
				}
			});
		});

		watch([isLocalHost, gameAccepted, gameStarted], ([host, accepted, started]) => {
			console.log('Game state changed:', {
				isHost: props.isHost,
				isLocalHost: host,
				gameAccepted: accepted,
				gameStarted: started
			});
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


		return {
			gameCanvas,
			playerScore,
			opponentScore,
			showNewGameButton,
			restartGame,
			isWaiting,
			gameStarted,
			startGame,
			gameAccepted,
			isLocalHost,
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

/* canvas {
  background: black;
  border-radius: 4px;
  max-width: 100%;
  max-height: calc(100% - 80px); 
  width: auto;
  height: auto;
  object-fit: contain;
  margin: auto;
} */

canvas {
    background: #000000;
    border-radius: 4px;
    width: 800px !important;
    height: 400px !important;
    object-fit: contain;
    margin: auto;
    image-rendering: pixelated;
    box-shadow: 0 0 20px rgba(3, 166, 112, 0.2);
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

.waiting-message {
    color: #888;
    background: #2d2d2d;
    padding: 1rem;
    border-radius: 4px;
    font-family: monospace;
    text-align: center;
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
</style>