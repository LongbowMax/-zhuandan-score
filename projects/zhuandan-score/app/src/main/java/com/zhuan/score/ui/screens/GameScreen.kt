package com.zhuan.score.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.zhuan.score.model.GameRank
import com.zhuan.score.viewmodel.GameViewModel
import java.util.UUID

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GameScreen(
    viewModel: GameViewModel = viewModel(),
    onNavigateBack: () -> Unit,
    onNavigateToHistory: () -> Unit
) {
    val settings by viewModel.currentRoundSettings.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("本局计分") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                },
                actions = {
                    IconButton(onClick = onNavigateToHistory) {
                        Icon(Icons.Default.History, contentDescription = "历史记录")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 排名设置
            RankSection(viewModel)
            
            // 家族设置
            FamilySection(viewModel)
            
            // 炸和天王炸设置
            ExplosionSection(viewModel)
            
            // 预览得分
            PreviewSection(viewModel)
            
            // 提交按钮
            Button(
                onClick = {
                    viewModel.calculateAndSaveRound()
                    onNavigateToHistory()
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = settings.rankings.size == viewModel.players.size &&
                         settings.families.size == viewModel.players.size
            ) {
                Text("计算并保存")
            }
        }
    }
}

@Composable
private fun RankSection(viewModel: GameViewModel) {
    val settings by viewModel.currentRoundSettings.collectAsState()
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "排名设置",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            viewModel.players.forEach { player ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = player.name,
                        modifier = Modifier.weight(1f)
                    )
                    
                    var expanded by remember { mutableStateOf(false) }
                    Box {
                        OutlinedButton(
                            onClick = { expanded = true }
                        ) {
                            val currentRank = settings.rankings[player.id]
                            Text(currentRank?.displayName ?: "选择排名")
                        }
                        
                        DropdownMenu(
                            expanded = expanded,
                            onDismissRequest = { expanded = false }
                        ) {
                            GameRank.values().forEach { rank ->
                                DropdownMenuItem(
                                    text = { Text(rank.displayName) },
                                    onClick = {
                                        viewModel.setPlayerRank(player.id, rank)
                                        expanded = false
                                    }
                                )
                            }
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
private fun FamilySection(viewModel: GameViewModel) {
    val settings by viewModel.currentRoundSettings.collectAsState()
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "家族设置",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                if (viewModel.players.size == 4) {
                    TextButton(
                        onClick = { viewModel.autoAssignFamilies() }
                    ) {
                        Text("自动分配")
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // 获取所有家族ID
            val familyIds = settings.families.values.toSet().toList()
            
            viewModel.players.forEach { player ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = player.name,
                        modifier = Modifier.weight(1f)
                    )
                    
                    var expanded by remember { mutableStateOf(false) }
                    Box {
                        OutlinedButton(
                            onClick = { expanded = true }
                        ) {
                            val currentFamily = settings.families[player.id]
                            val displayText = when {
                                currentFamily == null -> "选择家族"
                                familyIds.indexOf(currentFamily) == 0 -> "家族1"
                                familyIds.indexOf(currentFamily) == 1 -> "家族2"
                                else -> "新家族"
                            }
                            Text(displayText)
                        }
                        
                        DropdownMenu(
                            expanded = expanded,
                            onDismissRequest = { expanded = false }
                        ) {
                            // 现有家族
                            familyIds.forEachIndexed { index, familyId ->
                                DropdownMenuItem(
                                    text = { Text("家族${index + 1}") },
                                    onClick = {
                                        viewModel.setPlayerFamily(player.id, familyId)
                                        expanded = false
                                    }
                                )
                            }
                            // 新家族选项
                            DropdownMenuItem(
                                text = { Text("+ 新家族") },
                                onClick = {
                                    viewModel.setPlayerFamily(player.id, UUID.randomUUID().toString())
                                    expanded = false
                                }
                            )
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
private fun ExplosionSection(viewModel: GameViewModel) {
    val settings by viewModel.currentRoundSettings.collectAsState()
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "特殊牌型",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // 炸的数量
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("6张以上炸的数量")
                
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    IconButton(
                        onClick = { 
                            if (settings.explosionCount > 0) {
                                viewModel.setExplosionCount(settings.explosionCount - 1)
                            }
                        },
                        enabled = settings.explosionCount > 0
                    ) {
                        Icon(Icons.Default.Remove, contentDescription = "减少")
                    }
                    
                    Text(
                        text = settings.explosionCount.toString(),
                        style = MaterialTheme.typography.titleLarge
                    )
                    
                    IconButton(
                        onClick = { viewModel.setExplosionCount(settings.explosionCount + 1) }
                    ) {
                        Icon(Icons.Default.Add, contentDescription = "增加")
                    }
                }
            }
            
            if (settings.explosionCount > 0) {
                Text(
                    text = "倍数: ${"×".repeat(settings.explosionCount + 1)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // 天王炸
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("是否有天王炸")
                
                Switch(
                    checked = settings.hasTianWangZha,
                    onCheckedChange = { viewModel.setTianWangZha(it) }
                )
            }
            
            if (settings.hasTianWangZha) {
                Text(
                    text = "天王炸额外翻倍",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
private fun PreviewSection(viewModel: GameViewModel) {
    val settings by viewModel.currentRoundSettings.collectAsState()
    
    // 计算预览得分
    val multiplier = (1 shl settings.explosionCount) * (if (settings.hasTianWangZha) 2 else 1)
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "得分预览",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // 基础分
            val baseScore = when {
                settings.rankings.size != viewModel.players.size -> "?"
                settings.families.size != viewModel.players.size -> "?"
                else -> {
                    // 简化计算，实际需要完整数据
                    "根据排名计算"
                }
            }
            
            Text("基础分: 头游+二游=3分 / 头游+三游=2分 / 头游+末游=1分")
            
            if (multiplier > 1) {
                Text(
                    "总倍数: ×$multiplier",
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}
