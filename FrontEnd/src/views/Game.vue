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
		
		<!-- Game canvas -->
		<!-- <template v-else-if="gameStarted">
		  <canvas ref="gameCanvas" width="800" height="400"></canvas>
		  <div class="game-info">
			<p class="score">{{ playerScore }} - {{ opponentScore }}</p>
		  </div>
		  <div class="game-controls" v-if="showNewGameButton">
			<button 
			  @click="restartGame" 
			  class="btn primary-btn"
			>
			  Start New Game
			</button>
		  </div>
		</template> -->
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
    players: {
        player1: string;
        player2: string;
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
		const isLocalHost = ref(false);
		const isWaiting = ref(props.isHost);
		const gameStarted = ref(false);
		const gameAccepted = ref(false);
		const gameSocket = ref<WebSocket | null>(null);
		const gameCanvas = ref<HTMLCanvasElement | null>(null);
		const ctx = ref<CanvasRenderingContext2D | null>(null);
		const animationFrame = ref<number>(0);
		const showNewGameButton = ref<boolean>(false);
		const playerScore = ref<number>(0);
		const opponentScore = ref<number>(0);

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
				player: {  
					x: isLocalHost.value ? 50 : CANVAS_WIDTH - 60, 
					y: CANVAS_HEIGHT / 2 - 40 
				},
				opponent: {
					x: isLocalHost.value ? CANVAS_WIDTH - 60 : 50, 
            		y: CANVAS_HEIGHT / 2 - 40
				},
				width: 10,
				height: 80
			},
			score: {
				player: 0,
				opponent: 0
			},
			players: {
				player1: '',
				player2: ''
			}
		});

		const scaleFactor = ref(1);

		// const initGame = () => {
		// 	if (!gameCanvas.value) return;
			
		// 	const container = gameCanvas.value.parentElement;
		// 	if (!container) return;

		// 	// Calculate new scale factor
		// 	const containerWidth = Math.max(MIN_WIDTH, container.clientWidth);
		// 	const containerHeight = container.clientHeight;
		// 	scaleFactor.value = Math.min(
		// 		containerWidth / CANVAS_WIDTH,
		// 		containerHeight / CANVAS_HEIGHT
		// 	);

		// 	// Set the canvas display size
		// 	const scaledWidth = CANVAS_WIDTH * scaleFactor.value;
		// 	const scaledHeight = CANVAS_HEIGHT * scaleFactor.value;

		// 	// Update canvas style dimensions
		// 	gameCanvas.value.style.width = `${scaledWidth}px`;
		// 	gameCanvas.value.style.height = `${scaledHeight}px`;

		// 	// Keep the internal resolution constant
		// 	gameCanvas.value.width = CANVAS_WIDTH;
		// 	gameCanvas.value.height = CANVAS_HEIGHT;

		// 	// Reset context
		// 	ctx.value = gameCanvas.value.getContext('2d');
		// 	if (!ctx.value) return;

		// 	ctx.value.fillStyle = 'white';
		// 	ctx.value.strokeStyle = 'white';
		// };
		const initGame = () => {
			// Wait for canvas to be available
			if (!gameCanvas.value) {
				console.error('Canvas element not found during initialization');
				return false;
			}

			// Log canvas properties
			console.log('Initializing canvas:', {
				width: gameCanvas.value.width,
				height: gameCanvas.value.height,
				offsetWidth: gameCanvas.value.offsetWidth,
				offsetHeight: gameCanvas.value.offsetHeight
			});

			// Get the 2D context with explicit null check
			const context = gameCanvas.value.getContext('2d');
			if (!context) {
				console.error('Failed to get 2D context');
				return false;
			}
			ctx.value = context;

			// Set fixed dimensions
			gameCanvas.value.width = CANVAS_WIDTH;
			gameCanvas.value.height = CANVAS_HEIGHT;

			// Initialize game state
			gameState.value = {
				...gameState.value,
				paddles: {
					player: {
						x: isLocalHost.value ? 50 : CANVAS_WIDTH - 60,
						y: CANVAS_HEIGHT / 2 - 40
					},
					opponent: {
						x: isLocalHost.value ? CANVAS_WIDTH - 60 : 50,
						y: CANVAS_HEIGHT / 2 - 40
					},
					width: 10,
					height: 80
				}
			};

			console.log('Game initialized successfully:', {
				canvas: !!gameCanvas.value,
				context: !!ctx.value,
				width: gameCanvas.value.width,
				height: gameCanvas.value.height,
				gameState: gameState.value
			});

			return true;
		};
		// const gameLoop = () => {
		// 	if (!ctx.value || !gameCanvas.value) return;

		// 	// Clear canvas
		// 	ctx.value.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

		// 	// Update game state
		// 	updateGame();

		// 	// Draw game objects
		// 	drawGame();

		// 	// Continue loop
		// 	animationFrame.value = requestAnimationFrame(gameLoop);
		// };

		const gameLoop = () => {
			if (!gameCanvas.value) {
				console.error('Game loop failed: Canvas element not found');
				return;
			}

			if (!ctx.value) {
				console.error('Game loop failed: Canvas context not found');
				return;
			}

			// Clear previous animation frame if it exists
			if (animationFrame.value) {
				cancelAnimationFrame(animationFrame.value);
			}

			console.log('Game loop running:', {
				canvas: !!gameCanvas.value,
				context: !!ctx.value,
				gameState: {
					ball: gameState.value.ball,
					paddles: gameState.value.paddles
				}
			});

			// Update game state if host
			if (isLocalHost.value) {
				updateGame();
				sendBallUpdate();
			}

			// Draw game objects for both players
			drawGame();

			// Continue loop
			animationFrame.value = requestAnimationFrame(gameLoop);
		};


		// const sendBallUpdate = () => {
		// 	if (gameSocket.value?.readyState === WebSocket.OPEN) {
		// 		gameSocket.value.send(JSON.stringify({
		// 			type: 'ball_update',
		// 			ball: gameState.value.ball,
		// 			score: gameState.value.score
		// 		}));
		// 	}
		// };
		const sendBallUpdate = () => {
			if (gameSocket.value?.readyState === WebSocket.OPEN && isLocalHost.value) {
				console.log('Sending ball update:', {
					ball: gameState.value.ball,
					score: gameState.value.score
				});
				
				gameSocket.value.send(JSON.stringify({
					type: 'ball_update',
					ball: gameState.value.ball,
					score: gameState.value.score
				}));
			}
		};

		const lastUpdate = ref(Date.now());

		const updateGameState = (state: GameState) => {
			gameState.value = state;
		};

		const updateGame = () => {
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

			// Remove AI movement code that was here
		};

		// const drawGame = () => {
		// 	if (!ctx.value) return;
		// 	const { ball, paddles } = gameState.value;

		// 	// Clear the canvas
		// 	ctx.value.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

		// 	// Set styles
		// 	ctx.value.fillStyle = 'white';
		// 	ctx.value.strokeStyle = 'white';

		// 	// Draw paddles
		// 	ctx.value.fillRect(
		// 		paddles.player.x,
		// 		paddles.player.y,
		// 		paddles.width,
		// 		paddles.height
		// 	);
		// 	ctx.value.fillRect(
		// 		paddles.opponent.x,
		// 		paddles.opponent.y,
		// 		paddles.width,
		// 		paddles.height
		// 	);

		// 	// Draw ball
		// 	ctx.value.beginPath();
		// 	ctx.value.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
		// 	ctx.value.fill();
		// };
		const drawGame = () => {
			if (!ctx.value) return;
			
			// Store game state locally
			const { ball, paddles } = gameState.value;

			// Clear the canvas with a dark background
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

			// Log positions for debugging
			console.log('Drawing game objects:', {
				ball: { x: ball.x, y: ball.y },
				player: { x: paddles.player.x, y: paddles.player.y },
				opponent: { x: paddles.opponent.x, y: paddles.opponent.y }
			});

			// Draw paddles with rounded corners
			ctx.value.fillStyle = '#03a670';
			[paddles.player, paddles.opponent].forEach(paddle => {
				ctx.value!.beginPath();
				ctx.value!.roundRect(
					paddle.x, 
					paddle.y, 
					paddles.width, 
					paddles.height, 
					[5]
				);
				ctx.value!.fill();
			});

			// Draw ball with glow effect
			ctx.value.fillStyle = '#ffffff';
			ctx.value.shadowBlur = 15;
			ctx.value.shadowColor = '#03a670';
			ctx.value.beginPath();
			ctx.value.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
			ctx.value.fill();
			ctx.value.shadowBlur = 0;
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
			if (!gameStarted.value) return;
			
			const { paddles } = gameState.value;
			let moved = false;
			
			if (e.key === 'ArrowUp' && paddles.player.y > 0) {
				paddles.player.y = Math.max(0, paddles.player.y - PADDLE_SPEED);
				moved = true;
			}
			if (e.key === 'ArrowDown' && paddles.player.y < CANVAS_HEIGHT - paddles.height) {
				paddles.player.y = Math.min(CANVAS_HEIGHT - paddles.height, paddles.player.y + PADDLE_SPEED);
				moved = true;
			}

			// Only send update if paddle actually moved
			if (moved && gameSocket.value?.readyState === WebSocket.OPEN) {
				sendPaddleUpdate();
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
						console.log('Received game message:', data);
						
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
			console.log('Handling game message:', data);
			
			switch (data.type) {
				case 'game_state':
					if (data.game_status === 'accepted') {
						gameAccepted.value = true;
						isWaiting.value = false;
						
						// Update player names
						if (data.player1_username && data.player2_username) {
							gameState.value.players.player1 = data.player1_username;
							gameState.value.players.player2 = data.player2_username;
						}

						// Set host status based on player role
						isLocalHost.value = data.is_host;
						
						console.log('Game accepted, updated state:', {
							gameAccepted: gameAccepted.value,
							isWaiting: isWaiting.value,
							players: gameState.value.players,
							isHost: isLocalHost.value,
							playerRole: data.player_role
						});
					} else if (data.game_status === 'waiting') {
						isWaiting.value = true;
						gameAccepted.value = false;
						isLocalHost.value = data.is_host;
					} else if (data.game_status === 'started') {
						// Start the game for both players
						gameStarted.value = true;
						gameAccepted.value = true;
						isWaiting.value = false;
						resetBall();
						gameLoop();
						
						console.log('Game started:', {
							gameStarted: gameStarted.value,
							gameAccepted: gameAccepted.value,
							isHost: isLocalHost.value
						});
					}
					break;

				case 'player_joined':
					if (props.isHost) {
						console.log('Player joined, updating game state');
						isWaiting.value = false;
					}
					break;

				case 'game_start':
					console.log('Game starting');
					gameStarted.value = true;
					startGame();
					break;
				
		// 			case 'paddle_move':
        //     if (data.player !== isLocalHost.value) {
        //         gameState.value.paddles.opponent.y = data.y;
        //     }
        //     break;

        // case 'ball_update':
        //     if (!isLocalHost.value) {
        //         gameState.value.ball = data.ball;
        //         gameState.value.score = data.score;
        //         playerScore.value = data.score.player;
        //         opponentScore.value = data.score.opponent;
        //     }
        //     break;	
				// case 'paddle_move':
				// 	if (data.player !== props.isHost) {
				// 		gameState.value.paddles.opponent.y = data.y;
				// 		// Send paddle position to opponent if we're the host
				// 		if (props.isHost && gameSocket.value?.readyState === WebSocket.OPEN) {
				// 			gameSocket.value.send(JSON.stringify({
				// 				type: 'paddle_update',
				// 				y: gameState.value.paddles.player.y
				// 			}));
				// 		}
				// 	}
				// 	break;
				case 'paddle_move':
					if (data.player !== (isLocalHost.value ? 'player1' : 'player2')) {
						gameState.value.paddles.opponent.y = data.y;
					}
					break;


				// case 'ball_update':
				// 	if (!props.isHost) {
				// 		gameState.value.ball = data.ball;
				// 		gameState.value.score = data.score;
				// 		playerScore.value = data.score.player;
				// 		opponentScore.value = data.score.opponent;
				// 	}
				// 	break;

				case 'ball_update':
					if (!isLocalHost.value) {
						console.log('Received ball update:', data.ball);
						gameState.value.ball = data.ball;
						gameState.value.score = data.score;
						playerScore.value = data.score.player;
						opponentScore.value = data.score.opponent;
					}
					break;
				case 'game_over':
					handleGameOver(data);
					break;

				default:
					console.log('Unknown message type:', data.type);
			}
		};


		// const startGame = () => {
		// 	if (!gameSocket.value || gameSocket.value.readyState !== WebSocket.OPEN) {
		// 		console.error('WebSocket not connected');
		// 		return;
		// 	}

		// 	if (isLocalHost.value) {
		// 		console.log('Host starting game...');
				
		// 		// Initialize game before starting loop
		// 		initGame();
				
		// 		if (!ctx.value || !gameCanvas.value) {
		// 			console.error('Failed to initialize game');
		// 			return;
		// 		}

		// 		gameSocket.value.send(JSON.stringify({
		// 			type: 'start_game',
		// 			game_id: props.gameId
		// 		}));

		// 		gameStarted.value = true;
		// 		resetBall();
		// 		gameLoop();
		// 	}
		// };
		const startGame = () => {
			if (!gameSocket.value || gameSocket.value.readyState !== WebSocket.OPEN) {
				console.error('WebSocket not connected');
				return;
			}

			if (isLocalHost.value) {
				console.log('Host starting game...');
				
				gameStarted.value = true; // Set this first so canvas is rendered

				// Wait for next tick to ensure canvas is mounted
				nextTick(() => {
					// Initialize game after canvas is rendered
					if (!initGame()) {
						console.error('Failed to initialize game');
						gameStarted.value = false;
						return;
					}

					gameSocket.value?.send(JSON.stringify({
						type: 'start_game',
						game_id: props.gameId
					}));

					resetBall();
					gameLoop();
				});
			}
		};

		const sendPaddleUpdate = () => {
			if (gameSocket.value?.readyState === WebSocket.OPEN) {
				try {
					gameSocket.value.send(JSON.stringify({
						type: 'paddle_move',
						y: gameState.value.paddles.player.y,
						player: isLocalHost.value ? 'player1' : 'player2'
					}));
				} catch (error) {
					console.error('Error sending paddle update:', error);
				}
			}
		};

		const isConnected = ref(false);
		const checkConnection = () => {
			if (gameSocket.value) {
				isConnected.value = gameSocket.value.readyState === WebSocket.OPEN;
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


		onUnmounted(() => {
			cleanup();
		});

		const cleanup = () => {
			if (gameSocket.value) {
				gameSocket.value.onclose = null; // Prevent reconnection attempts during cleanup
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

		// onMounted(() => {
		// 	initGame();
		// 	initializeGameSocket();
		// 	window.addEventListener('keydown', handleKeyDown);
			
		// 	// Update resize observer to preserve game state
		// 	if (gameCanvas.value) {
		// 		resizeObserver = new ResizeObserver(() => {
		// 			// Store current game state
		// 			const currentState = { ...gameState.value };
					
		// 			// Reinitialize canvas
		// 			initGame();
					
		// 			// Restore game state
		// 			gameState.value = currentState;
		// 		});
		// 		resizeObserver.observe(gameCanvas.value.parentElement as Element);
		// 	}
		// });
		onMounted(() => {
			// Wait for the next tick when the template is rendered
			nextTick(async () => {
				// Wait a small amount of time to ensure canvas is mounted
				await new Promise(resolve => setTimeout(resolve, 100));
				
				if (!gameCanvas.value) {
					console.error('Canvas ref not found after mount');
					return;
				}

				console.log('Canvas element found:', {
					element: gameCanvas.value,
					width: gameCanvas.value.width,
					height: gameCanvas.value.height
				});

				// Initialize game components
				initGame();
				
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