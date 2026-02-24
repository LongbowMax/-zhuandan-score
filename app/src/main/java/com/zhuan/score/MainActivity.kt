package com.zhuan.score

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.zhuan.score.ui.screens.GameScreen
import com.zhuan.score.ui.screens.HistoryScreen
import com.zhuan.score.ui.screens.PlayersScreen
import com.zhuan.score.ui.theme.ZhuanDanTheme
import com.zhuan.score.viewmodel.GameViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ZhuanDanTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    ZhuanDanApp()
                }
            }
        }
    }
}

// 导航枚举
enum class Screen {
    PLAYERS,    // 玩家管理
    GAME,       // 游戏计分
    HISTORY     // 历史记录
}

@Composable
fun ZhuanDanApp(
    viewModel: GameViewModel = viewModel()
) {
    var currentScreen by remember { mutableStateOf(Screen.PLAYERS) }
    
    when (currentScreen) {
        Screen.PLAYERS -> {
            PlayersScreen(
                viewModel = viewModel,
                onNavigateToGame = { currentScreen = Screen.GAME },
                onNavigateToHistory = { currentScreen = Screen.HISTORY }
            )
        }
        Screen.GAME -> {
            GameScreen(
                viewModel = viewModel,
                onNavigateBack = { currentScreen = Screen.PLAYERS },
                onNavigateToHistory = { currentScreen = Screen.HISTORY }
            )
        }
        Screen.HISTORY -> {
            HistoryScreen(
                viewModel = viewModel,
                onNavigateBack = { currentScreen = Screen.PLAYERS }
            )
        }
    }
}
