<template>
  <div class="form-container" v-if="!matches.length">
    <h2>{{ t('localTournament.title') }}</h2>
    <form @submit.prevent="createTournament">
      <div class="form-group">
        <label for="player1">{{ t('localTournament.players.player1') }}</label>
        <input type="text" v-model="player1" id="player1" :placeholder="t('localTournament.players.enterName')" required />
      </div>
      <div class="form-group">
        <label for="player2">{{ t('localTournament.players.player2') }}</label>
        <input type="text" v-model="player2" id="player2" :placeholder="t('localTournament.players.enterName')" required />
      </div>
      <div class="form-group">
        <label for="player3">{{ t('localTournament.players.player3') }}</label>
        <input type="text" v-model="player3" id="player3" :placeholder="t('localTournament.players.enterName')" required />
      </div>
      <div class="form-group">
        <label for="player4">{{ t('localTournament.players.player4') }}</label>
        <input type="text" v-model="player4" id="player4" :placeholder="t('localTournament.players.enterName')" required />
      </div>
      <button type="submit" class="submit-btn">{{ t('localTournament.actions.create') }}</button>
    </form>
  </div>
  <div v-else class="tournament-bracket">
    <h2>{{ t('localTournament.bracket.title') }}</h2>
    <div class="matches-container">
      <div v-for="(match, index) in matches" :key="index" class="match-card">
        <div class="match-header">
          <h3>{{ t('localTournament.bracket.semiFinal', { number: index + 1 }) }}</h3>
        </div>
        <div class="match-content">
          <div class="player">{{ match[`semi_final_${index + 1}`].player1 }}</div>
          <div class="vs">VS</div>
          <div class="player">{{ match[`semi_final_${index + 1}`].player2 }}</div>
        </div>
        <div class="match-footer">
          <button class="start-match-btn" @click="startMatch(index)">
            {{ t('localTournament.actions.startMatch') }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <transition name="fade">
    <div v-if="activeMatch !== null" class="overlay">
      <div class="game-container">
        <div class="game-header">
          <h4 class="game-title">
            {{ t('localTournament.game.title', {
              player1: currentMatch?.player1,
              player2: currentMatch?.player2
            }) }}
          </h4>
          <button @click="closeMatch" class="btn secondary-btn">{{ t('localTournament.actions.close') }}</button>
        </div>
        
        <div class="game-content">
          <canvas 
            ref="gameCanvas"
            :width="800"
            :height="400"
            style="background: #000000"
          ></canvas>

          <div v-if="isGameOver" class="game-end-screen">
            <h2>{{ t('localTournament.game.over') }}</h2>
            <p class="win-message">
              {{ t('localTournament.game.winner', {
                player: gameState.paddles.player1.score > gameState.paddles.player2.score 
                  ? currentMatch?.player1 
                  : currentMatch?.player2
              }) }}
            </p>
            <p class="score-message">
              {{ t('localTournament.game.finalScore', {
                score1: gameState.paddles.player1.score,
                score2: gameState.paddles.player2.score
              }) }}
            </p>
            <button @click="closeMatch" class="btn primary-btn">
              {{ t('localTournament.actions.returnToTournament') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import PongGame from './Game.vue'
import { useI18n } from 'vue-i18n'


const player1 = ref('')
const player2 = ref('')
const player3 = ref('')
const player4 = ref('')
const matches = ref([])
const router = useRouter()
const { t } = useI18n()

const getToken = computed(() => {
  return localStorage.getItem('token');
})

const currentMatch = computed(() => {
  if (activeMatch.value !== null && matches.value[activeMatch.value]) {
    return matches.value[activeMatch.value][`semi_final_${activeMatch.value + 1}`]
  }
  return null
})

const createTournament = async () => {
  try {
    const token = getToken.value;
    const response = await fetch('api/tournament/local-tournament/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        player1: player1.value,
        player2: player2.value,
        player3: player3.value,
        player4: player4.value
      })
    })

    if (response.ok) {
      const data = await response.json()
      matches.value = data.matches
    } else {
      console.error(t('localTournament.errors.createFailed'))
    }
  } catch (error) {
    console.error(t('localTournament.errors.createFailed'), error)
  }
}

const gameCanvas = ref(null)
const activeMatch = ref(null)

const CANVAS_WIDTH = 800
const CANVAS_HEIGHT = 400
const PADDLE_WIDTH = 10
const PADDLE_HEIGHT = 80
const BALL_RADIUS = 8
const INITIAL_BALL_SPEED = 3
const PADDLE_SPEED = 40
const SPEED_REDUCTION = 0.9
const ANGLE_FACTOR = 0.50
const MAX_BALL_SPEED = INITIAL_BALL_SPEED * 1.5
const FRAME_TIME = 1000 / 60
const MAX_DELTA_TIME = 1000 / 30

const gameState = ref({
  ball: {
    x: CANVAS_WIDTH / 2,
    y: CANVAS_HEIGHT / 2,
    dx: INITIAL_BALL_SPEED,
    dy: INITIAL_BALL_SPEED * 0.5,
    radius: BALL_RADIUS
  },
  paddles: {
    player1: {
      x: 50,
      y: CANVAS_HEIGHT / 2 - PADDLE_HEIGHT / 2,
      score: 0
    },
    player2: {
      x: CANVAS_WIDTH - 60,
      y: CANVAS_HEIGHT / 2 - PADDLE_HEIGHT / 2,
      score: 0
    }
  }
})

const pressedKeys = ref(new Set())
const lastFrameTime = ref(0)
const animationFrame = ref(0)
const isGameOver = ref(false)

const handleKeyDown = (e) => {
  pressedKeys.value.add(e.key)
}

const handleKeyUp = (e) => {
  pressedKeys.value.delete(e.key)
}

const updatePaddles = (delta) => {
  const adjustedSpeed = PADDLE_SPEED * delta

  // Player 1 (W/S keys)
  if (pressedKeys.value.has('w')) {
    gameState.value.paddles.player1.y = Math.max(
      0, 
      gameState.value.paddles.player1.y - adjustedSpeed
    )
  }
  if (pressedKeys.value.has('s')) {
    gameState.value.paddles.player1.y = Math.min(
      CANVAS_HEIGHT - PADDLE_HEIGHT,
      gameState.value.paddles.player1.y + adjustedSpeed
    )
  }

  // Player 2 (Arrow keys)
  if (pressedKeys.value.has('ArrowUp')) {
    gameState.value.paddles.player2.y = Math.max(
      0,
      gameState.value.paddles.player2.y - adjustedSpeed
    )
  }
  if (pressedKeys.value.has('ArrowDown')) {
    gameState.value.paddles.player2.y = Math.min(
      CANVAS_HEIGHT - PADDLE_HEIGHT,
      gameState.value.paddles.player2.y + adjustedSpeed
    )
  }
}

const updateBall = (delta) => {
  const { ball, paddles } = gameState.value

  // Update ball position
  ball.x += ball.dx * delta
  ball.y += ball.dy * delta

  // Ball collision with top and bottom walls
  if (ball.y + ball.radius > CANVAS_HEIGHT) {
    ball.y = CANVAS_HEIGHT - ball.radius
    ball.dy = -ball.dy * SPEED_REDUCTION
  } else if (ball.y - ball.radius < 0) {
    ball.y = ball.radius
    ball.dy = -ball.dy * SPEED_REDUCTION
  }

  // Ball collision with paddles
  // Player 1 paddle
  if (ball.x - ball.radius <= paddles.player1.x + PADDLE_WIDTH &&
      ball.y >= paddles.player1.y &&
      ball.y <= paddles.player1.y + PADDLE_HEIGHT &&
      ball.dx < 0) {
    
    ball.x = paddles.player1.x + PADDLE_WIDTH + ball.radius
    ball.dx = -ball.dx * SPEED_REDUCTION
    
    const deltaY = ball.y - (paddles.player1.y + PADDLE_HEIGHT / 2)
    ball.dy = deltaY * ANGLE_FACTOR
  }
  
  // Player 2 paddle
  if (ball.x + ball.radius >= paddles.player2.x &&
      ball.y >= paddles.player2.y &&
      ball.y <= paddles.player2.y + PADDLE_HEIGHT &&
      ball.dx > 0) {
    
    ball.x = paddles.player2.x - ball.radius
    ball.dx = -ball.dx * SPEED_REDUCTION
    
    const deltaY = ball.y - (paddles.player2.y + PADDLE_HEIGHT / 2)
    ball.dy = deltaY * ANGLE_FACTOR
  }

  // Scoring
  if (ball.x - ball.radius < 0) {
    // Player 2 scores
    paddles.player2.score++
    resetBall()
    checkGameOver()
  } else if (ball.x + ball.radius > CANVAS_WIDTH) {
    // Player 1 scores
    paddles.player1.score++
    resetBall()
    checkGameOver()
  }
}

const resetBall = () => {
  const { ball } = gameState.value
  ball.x = CANVAS_WIDTH / 2
  ball.y = CANVAS_HEIGHT / 2
  ball.dx = INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1)
  ball.dy = INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1) * 0.5
}

const checkGameOver = () => {
  const { player1, player2 } = gameState.value.paddles
  if (player1.score >= 5 || player2.score >= 5) {
    isGameOver.value = true
    cancelAnimationFrame(animationFrame.value)
  }
}

const drawGame = (ctx) => {
  const { ball, paddles } = gameState.value

  // Clear canvas
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

  // Draw center line
  ctx.strokeStyle = '#ffffff'
  ctx.setLineDash([5, 15])
  ctx.beginPath()
  ctx.moveTo(CANVAS_WIDTH / 2, 0)
  ctx.lineTo(CANVAS_WIDTH / 2, CANVAS_HEIGHT)
  ctx.stroke()
  ctx.setLineDash([])

  // Draw paddles
  ctx.fillStyle = '#03a670'
  
  // Player 1 paddle
  ctx.beginPath()
  ctx.roundRect(
    paddles.player1.x,
    paddles.player1.y,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
    [5]
  )
  ctx.fill()

  // Player 2 paddle
  ctx.beginPath()
  ctx.roundRect(
    paddles.player2.x,
    paddles.player2.y,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
    [5]
  )
  ctx.fill()

  // Draw ball with glow effect
  ctx.fillStyle = '#ffffff'
  ctx.shadowBlur = 15
  ctx.shadowColor = '#03a670'
  ctx.beginPath()
  ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2)
  ctx.fill()
  ctx.shadowBlur = 0

  // Draw scores
  ctx.fillStyle = '#ffffff'
  ctx.font = '32px Arial'
  ctx.textAlign = 'center'
  ctx.fillText(paddles.player1.score, CANVAS_WIDTH / 4, 50)
  ctx.fillText(paddles.player2.score, (CANVAS_WIDTH / 4) * 3, 50)
}

const gameLoop = () => {
  const now = performance.now()
  const deltaTime = Math.min(now - lastFrameTime.value, MAX_DELTA_TIME)
  const normalizedDelta = deltaTime / FRAME_TIME

  if (deltaTime >= FRAME_TIME) {
    const ctx = gameCanvas.value?.getContext('2d')
    if (ctx) {
      updatePaddles(normalizedDelta)
      updateBall(normalizedDelta)
      drawGame(ctx)
    }
    lastFrameTime.value = now
  }

  if (!isGameOver.value) {
    animationFrame.value = requestAnimationFrame(gameLoop)
  }
}

const startMatch = (matchIndex) => {
  try {
    activeMatch.value = matchIndex
    isGameOver.value = false
    gameState.value.paddles.player1.score = 0
    gameState.value.paddles.player2.score = 0
    resetBall()
    
    // Start game loop in next tick to ensure canvas is ready
    nextTick(() => {
      if (gameCanvas.value) {
        window.addEventListener('keydown', handleKeyDown)
        window.addEventListener('keyup', handleKeyUp)
        lastFrameTime.value = performance.now()
        gameLoop()
      } else {
        console.error(t('localTournament.errors.canvasNotFound'))
      }
    })
  } catch (error) {
    console.error(t('localTournament.errors.startMatchFailed'), error)
  }
}

const closeMatch = () => {
  activeMatch.value = null
  isGameOver.value = false
  cancelAnimationFrame(animationFrame.value)
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)
  pressedKeys.value.clear()
}

onUnmounted(() => {
  closeMatch()
})
</script>

<style scoped>
.form-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

button.submit-btn {
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}

button.submit-btn:hover {
  background-color: #028a5e;
}

.matches {
  margin-top: 2rem;
}

.match {
  margin-bottom: 1rem;
}

.match h3 {
  margin-bottom: 0.5rem;
}

.tournament-bracket {
  margin-top: 3rem;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.matches-container {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: center;
  margin-top: 2rem;
}

.match-card {
  width: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease;
}

.match-card:hover {
  transform: translateY(-5px);
}

.match-header {
  background-color: #4CAF50;
  color: white;
  padding: 1rem;
  text-align: center;
}

.match-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.match-content {
  padding: 1.5rem;
}

.player {
  padding: 0.5rem;
  text-align: center;
  font-weight: bold;
  color: #2c3e50;
}

.vs {
  text-align: center;
  color: #666;
  font-weight: bold;
  margin: 0.5rem 0;
}

.match-footer {
  padding: 1rem;
  text-align: center;
  background-color: #f8f9fa;
}

.start-match-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
}

.start-match-btn:hover {
  background-color: #028a5e;
}

.start-match-btn:active {
  transform: translateY(1px);
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>