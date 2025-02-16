<script>
export default {
    data() {
        return {
            player1: '',
            player2: '',
            score: '',
            winner: '',
            timeEnded: '',
            gameId: '',
        };
    },
    methods: {
        play() {
            const gameId = "fc2c7e7c-4ae6-4d13-b8da-55ed9530b675";  // Replace with actual game ID
            const ws = new WebSocket(`ws://localhost:8000/ws/pong/${gameId}/`);

            let playerNumber = null;  // Store player number

            ws.onmessage = function(event) {
                let data = JSON.parse(event.data);

                if (data.player_number) {
                    playerNumber = data.player_number;  // ✅ Save player number
                    console.log(`🎮 You are Player ${playerNumber}`);
                }

                if (data.game_state) {
                    updateUIWithGameState(data.game_state);
                }
            };

            ws.onopen = function() {
                console.log("Connected to WebSocket!");
                ws.send(JSON.stringify({ type: "get_player_number" }));  // Ask for player number
            };


            function updateUIWithGameState(gameState) {
                // Update paddles and ball position
                document.getElementById("player1-paddle").style.top = gameState.player1_paddle + "px";
                document.getElementById("player2-paddle").style.top = gameState.player2_paddle + "px";
                document.getElementById("ball").style.top = gameState.ball_position.y + "px";
                document.getElementById("ball").style.left = gameState.ball_position.x + "px";

                // Update score
                document.getElementById("score").innerText = `${gameState.player1_score} - ${gameState.player2_score}`;
            }

            // Example: Move paddle for player 1
            document.addEventListener('keydown', function(event) {
                if (playerNumber === null) return;  // Wait until player number is assigned

                let newPosition;
                let paddleId = playerNumber === 1 ? "player1-paddle" : "player2-paddle";  
                let currentPosition = parseInt(document.getElementById(paddleId).style.top || 0);

                if (event.key === 'ArrowUp') {
                    newPosition = currentPosition - 10;
                } else if (event.key === 'ArrowDown') {
                    newPosition = currentPosition + 10;
                } else {
                    return;  // Ignore other keys
                }

                if (newPosition >= 0 && newPosition <= 340) {  // Paddle boundaries
                    movePaddle(playerNumber, newPosition);
                }
            });


            function movePaddle(player, newPosition) {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        'type': 'move_paddle',
                        'player': player,
                        'new_position': newPosition
                    }));
                } else {
                    console.error("WebSocket is not open. Message not sent.");
                }
            }
        }
    }
}
</script>


<template>
    <div id="game-area">
        <div id="player1-paddle" class="paddle"></div>
        <div id="player2-paddle" class="paddle"></div>
        <div id="ball"></div>
    </div>
    <div id="score">0 - 0</div>

</template>


<style scoped>
    body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #222;
            margin: 0;
        }
        #game-area {
            position: relative;
            width: 600px;
            height: 400px;
            background-color: black;
        }
        .paddle {
            position: absolute;
            width: 10px;
            height: 60px;
            background-color: white;
        }
        #player1-paddle {
            left: 20px;
        }
        #player2-paddle {
            right: 20px;
        }
        #ball {
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: white;
            border-radius: 50%;
        }
        #score {
            text-align: center;
            color: white;
            font-size: 24px;
            margin-top: 10px;
        }
</style>