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
import com.zhuan.score.model.Player
import com.zhuan.score.viewmodel.GameViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GameScreen(
    viewModel: GameViewModel = viewModel(),
    onNavigateBack: () -> Unit,
    onNavigateToHistory: () -> Unit
) {
    val settings by viewModel.currentRoundSettings.collectAsState()
    val selectedPlayers = viewModel.getSelectedPlayers()
    
    // 确认选择状态（当玩家>4人时需要手动确认）
    var isSelectionConfirmed by remember { mutableStateOf(false) }
    
    // 是否需要显示玩家选择（玩家>4人且未确认）
    val showPlayerSelection = viewModel.players.size > 4 && !isSelectionConfirmed
    // 是否显示后续设置（玩家<=4人 或 已确认选择）
    val showGameSettings = viewModel.players.size <= 4 || isSelectionConfirmed

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
            // 玩家选择（当总人数超过4人且未确认时显示）
            if (showPlayerSelection) {
                PlayerSelectionSection(
                    viewModel = viewModel,
                    selectedPlayers = selectedPlayers,
                    onConfirm = { isSelectionConfirmed = true }
                )
            }

            // 排名设置
            if (showGameSettings) {
                RankSection(viewModel, selectedPlayers)
            }

            // 家族设置
            if (showGameSettings) {
                FamilySection(viewModel, selectedPlayers)
            }

            // 炸和天王炸设置
            if (showGameSettings) {
                ExplosionSection(viewModel)
            }

            // 预览得分
            if (showGameSettings) {
                PreviewSection(viewModel, selectedPlayers)
            }

            // 提交按钮
            if (showGameSettings) {
                val rankingsForSelected = settings.rankings.filterKeys { id ->
                    selectedPlayers.any { it.id == id }
                }
                val selectedPlayerIds = selectedPlayers.map { it.id }.toSet()
                val family1Count = settings.families.filterKeys { selectedPlayerIds.contains(it) }.values.count { it == "family1" }

                Button(
                    onClick = {
                        viewModel.calculateAndSaveRound()
                        onNavigateToHistory()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = rankingsForSelected.size == 4 &&
                             family1Count == 2 &&
                             selectedPlayers.size == 4
                ) {
                    Text("计算并保存")
                }
            }
        }
    }
}

@Composable
private fun PlayerSelectionSection(
    viewModel: GameViewModel,
    selectedPlayers: List<Player>,
    onConfirm: () -> Unit
) {
    val settings by viewModel.currentRoundSettings.collectAsState()
    // 直接从 settings 获取选择数量，避免延迟
    val selectedCount = settings.selectedPlayerIds.size

    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
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
                    text = "选择本局玩家",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )

                // 显示已选择数量
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = if (selectedCount == 4)
                            MaterialTheme.colorScheme.primary
                        else
                            MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Text(
                        text = "$selectedCount/4",
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                        color = if (selectedCount == 4)
                            MaterialTheme.colorScheme.onPrimary
                        else
                            MaterialTheme.colorScheme.onErrorContainer,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Text(
                text = "请勾选4个玩家参与本局游戏",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 4.dp, bottom = 12.dp)
            )

            // 玩家选择列表
            viewModel.players.forEach { player ->
                val isSelected = settings.selectedPlayerIds.contains(player.id)

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = player.name,
                        modifier = Modifier.weight(1f),
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                    )

                    Checkbox(
                        checked = isSelected,
                        onCheckedChange = {
                            viewModel.togglePlayerSelection(player.id)
                        },
                        enabled = isSelected || selectedCount < 4
                    )
                }

                Spacer(modifier = Modifier.height(4.dp))
            }

            // 确认按钮（选满4人后显示）
            if (selectedCount == 4) {
                Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = onConfirm,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = null,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("确认选择")
                }
            } else {
                Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = { },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = false
                ) {
                    Text("请继续选择玩家 ($selectedCount/4)")
                }
            }
        }
    }
}

@Composable
private fun RankSection(viewModel: GameViewModel, selectedPlayers: List<Player>) {
    val settings by viewModel.currentRoundSettings.collectAsState()
    
    // 获取已被其他玩家选中的排名
    val usedRanks = settings.rankings.values.toSet()

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

            selectedPlayers.forEach { player ->
                // 当前玩家已选的排名
                val currentPlayerRank = settings.rankings[player.id]
                
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
                            Text(currentPlayerRank?.displayName ?: "选择排名")
                        }

                        DropdownMenu(
                            expanded = expanded,
                            onDismissRequest = { expanded = false }
                        ) {
                            GameRank.values().forEach { rank ->
                                // 判断是否可用：未被其他玩家选择，或者是当前玩家已选的
                                val isAvailable = rank !in usedRanks || rank == currentPlayerRank
                                
                                DropdownMenuItem(
                                    text = { 
                                        Text(
                                            rank.displayName,
                                            color = if (isAvailable) 
                                                MaterialTheme.colorScheme.onSurface 
                                            else 
                                                MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
                                        ) 
                                    },
                                    onClick = {
                                        if (isAvailable) {
                                            viewModel.setPlayerRank(player.id, rank)
                                            expanded = false
                                        }
                                    },
                                    enabled = isAvailable
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
private fun FamilySection(viewModel: GameViewModel, selectedPlayers: List<Player>) {
    val settings by viewModel.currentRoundSettings.collectAsState()

    // 只统计选中玩家中家族1的成员数量
    val selectedPlayerIds = selectedPlayers.map { it.id }.toSet()
    val family1Count = settings.families.filterKeys { selectedPlayerIds.contains(it) }.values.count { it == "family1" }
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

                // 自动分配按钮（当选中4人时显示）
                if (selectedPlayers.size == 4) {
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
                val family1Names = selectedPlayers
                    .filter { family1Members.contains(it.id) }
                    .joinToString("、") { it.name }
                val family2Names = selectedPlayers
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

            // 玩家选择（只显示选中的玩家）
            selectedPlayers.forEach { player ->
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
                                    // 如果这是第2个家族1成员，自动将其他玩家设为家族2
                                    if (family1Count + 1 == 2) {
                                        selectedPlayers.forEach { p ->
                                            if (p.id != player.id && settings.families[p.id] != "family1") {
                                                viewModel.setPlayerFamily(p.id, "family2")
                                            }
                                        }
                                    }
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
private fun PreviewSection(viewModel: GameViewModel, selectedPlayers: List<Player>) {
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
            val selectedPlayerIds = selectedPlayers.map { it.id }.toSet()
            val rankingsForSelected = settings.rankings.filterKeys { selectedPlayerIds.contains(it) }
            val familiesForSelected = settings.families.filterKeys { selectedPlayerIds.contains(it) }

            val baseScore = when {
                rankingsForSelected.size != selectedPlayers.size -> "?"
                familiesForSelected.size != selectedPlayers.size -> "?"
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
