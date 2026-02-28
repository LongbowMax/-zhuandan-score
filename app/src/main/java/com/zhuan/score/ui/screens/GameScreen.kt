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
    
    // 统计家族1的成员数量
    val family1Count = settings.families.values.count { it == "family1" }
    val family1Members = settings.families.filter { it.value == "family1" }.keys
    
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
            
            // 提示文字
            Text(
                text = "请选择家族1的2名成员，其余自动归为家族2",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 4.dp, bottom = 12.dp)
            )
            
            // 显示家族分配情况
            if (family1Count == 2) {
                val family1Names = viewModel.players
                    .filter { family1Members.contains(it.id) }
                    .joinToString("、") { it.name }
                val family2Names = viewModel.players
                    .filter { !family1Members.contains(it.id) }
                    .joinToString("、") { it.name }
                
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.secondaryContainer
                    ),
                    modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp)
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text("家族1: $family1Names", style = MaterialTheme.typography.bodyMedium)
                        Text("家族2: $family2Names", style = MaterialTheme.typography.bodyMedium)
                    }
                }
            } else {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    ),
                    modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp)
                ) {
                    Text(
                        text = "已选择 $family1Count/2 人，需要再选择 ${2 - family1Count} 人",
                        modifier = Modifier.padding(12.dp),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onErrorContainer
                    )
                }
            }
            
            // 玩家选择
            viewModel.players.forEach { player ->
                val isFamily1 = settings.families[player.id] == "family1"
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = player.name,
                        modifier = Modifier.weight(1f)
                    )
                    
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("家族1", style = MaterialTheme.typography.bodyMedium)
                        Switch(
                            checked = isFamily1,
                            onCheckedChange = { checked ->
                                if (checked && family1Count < 2) {
                                    viewModel.setPlayerFamily(player.id, "family1")
                                } else if (!checked && isFamily1) {
                                    viewModel.setPlayerFamily(player.id, "family2")
                                }
                            },
                            enabled = !isFamily1 && family1Count < 2 || isFamily1
                        )
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
