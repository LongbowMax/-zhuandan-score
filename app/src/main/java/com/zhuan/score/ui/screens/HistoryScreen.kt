package com.zhuan.score.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.zhuan.score.model.GameRound
import com.zhuan.score.model.PlayerSettlement
import com.zhuan.score.viewmodel.GameViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(
    viewModel: GameViewModel = viewModel(),
    onNavigateBack: () -> Unit
) {
    var showDeleteDialog by remember { mutableStateOf<String?>(null) }
    var showSettlementDialog by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("历史记录") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                },
                actions = {
                    if (viewModel.rounds.isNotEmpty()) {
                        IconButton(onClick = { showSettlementDialog = true }) {
                            Icon(Icons.Default.AccountBalanceWallet, contentDescription = "结算")
                        }
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
        ) {
            // 玩家总分统计
            if (viewModel.players.isNotEmpty()) {
                TotalScoreCard(viewModel)
                Spacer(modifier = Modifier.height(16.dp))
            }
            
            // 历史记录列表
            Text(
                text = "本局记录 (${viewModel.rounds.size})",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            if (viewModel.rounds.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "还没有游戏记录",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            } else {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(viewModel.rounds) { round ->
                        RoundCard(
                            round = round,
                            onDelete = { showDeleteDialog = round.id }
                        )
                    }
                }
            }
        }
    }
    
    // 删除确认对话框
    showDeleteDialog?.let { roundId ->
        AlertDialog(
            onDismissRequest = { showDeleteDialog = null },
            title = { Text("确认删除") },
            text = { Text("确定要删除这条游戏记录吗？") },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.deleteRound(roundId)
                        showDeleteDialog = null
                    }
                ) {
                    Text("删除", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteDialog = null }) {
                    Text("取消")
                }
            }
        )
    }
    
    // 结算对话框
    if (showSettlementDialog) {
        SettlementDialog(
            viewModel = viewModel,
            onDismiss = { showSettlementDialog = false }
        )
    }
}

@Composable
private fun SettlementDialog(
    viewModel: GameViewModel,
    onDismiss: () -> Unit
) {
    val settlementSettings = viewModel.settlementSettings.collectAsState()
    var rateText by remember { mutableStateOf(settlementSettings.value.scoreValue.toString()) }
    
    val settlements = remember(rateText) {
        val rate = rateText.toIntOrNull() ?: 100
        viewModel.calculateSettlement(rate)
    }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("结算") },
        text = {
            Column {
                OutlinedTextField(
                    value = rateText,
                    onValueChange = { value: String ->
                        rateText = value.filter { c: Char -> c.isDigit() }
                    },
                    label = { Text("1分 = ?元") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.fillMaxWidth()
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "结算结果",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                settlements.forEachIndexed { index, settlement ->
                    SettlementItem(settlement = settlement, isTop = index == 0)
                    if (index < settlements.size - 1) {
                        Divider(modifier = Modifier.padding(vertical = 8.dp))
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("确定")
            }
        }
    )
}

@Composable
private fun SettlementItem(
    settlement: PlayerSettlement,
    isTop: Boolean
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = if (isTop) "🏆" else "•",
                style = MaterialTheme.typography.bodyMedium
            )
            
            Text(
                text = settlement.playerName,
                style = MaterialTheme.typography.bodyLarge
            )
            
            Text(
                text = "(${settlement.totalScore}分)",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        val amountText = if (settlement.amount >= 0) "+${settlement.amount}" else "${settlement.amount}"
        Text(
            text = "${amountText}元",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = when {
                settlement.amount > 0 -> MaterialTheme.colorScheme.error
                settlement.amount < 0 -> MaterialTheme.colorScheme.primary
                else -> MaterialTheme.colorScheme.onSurface
            }
        )
    }
}

@Composable
private fun TotalScoreCard(viewModel: GameViewModel) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "当前排名",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // 按总分排序
            val sortedPlayers = viewModel.players.sortedByDescending { it.totalScore }
            
            sortedPlayers.forEachIndexed { index, player ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // 排名
                        Surface(
                            shape = MaterialTheme.shapes.small,
                            color = when (index) {
                                0 -> MaterialTheme.colorScheme.error
                                1 -> MaterialTheme.colorScheme.primary
                                2 -> MaterialTheme.colorScheme.tertiary
                                else -> MaterialTheme.colorScheme.surfaceVariant
                            },
                            modifier = Modifier.size(28.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    text = "${index + 1}",
                                    style = MaterialTheme.typography.labelMedium,
                                    color = MaterialTheme.colorScheme.onPrimary
                                )
                            }
                        }
                        
                        Text(
                            text = player.name,
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                    
                    Text(
                        text = "${if (player.totalScore > 0) "+" else ""}${player.totalScore}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = when {
                            player.totalScore > 0 -> MaterialTheme.colorScheme.error
                            player.totalScore < 0 -> MaterialTheme.colorScheme.primary
                            else -> MaterialTheme.colorScheme.onSurface
                        }
                    )
                }
                
                if (index < sortedPlayers.size - 1) {
                    Divider(
                        modifier = Modifier.padding(vertical = 8.dp),
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.2f)
                    )
                }
            }
        }
    }
}

@Composable
private fun RoundCard(
    round: GameRound,
    onDelete: () -> Unit
) {
    val dateFormat = SimpleDateFormat("MM-dd HH:mm", Locale.getDefault())
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // 头部：时间和删除按钮
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = dateFormat.format(Date(round.timestamp)),
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // 倍数标识
                    if (round.getMultiplier() > 1) {
                        Surface(
                            color = MaterialTheme.colorScheme.error,
                            shape = MaterialTheme.shapes.small
                        ) {
                            Text(
                                text = "×${round.getMultiplier()}",
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                color = MaterialTheme.colorScheme.onError,
                                style = MaterialTheme.typography.labelMedium
                            )
                        }
                    }
                    
                    IconButton(
                        onClick = onDelete,
                        modifier = Modifier.size(32.dp)
                    ) {
                        Icon(
                            Icons.Default.Delete,
                            contentDescription = "删除",
                            tint = MaterialTheme.colorScheme.error,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // 玩家结果
            val sortedResults = round.playerResults.sortedBy { it.rank.rank }
            
            sortedResults.forEach { result ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // 排名标识
                        Surface(
                            shape = MaterialTheme.shapes.extraSmall,
                            color = when (result.rank) {
                                com.zhuan.score.model.GameRank.FIRST -> MaterialTheme.colorScheme.error
                                com.zhuan.score.model.GameRank.SECOND -> MaterialTheme.colorScheme.primary
                                com.zhuan.score.model.GameRank.THIRD -> MaterialTheme.colorScheme.tertiary
                                else -> MaterialTheme.colorScheme.surfaceVariant
                            },
                            modifier = Modifier.size(24.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    text = result.rank.rank.toString(),
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onPrimary
                                )
                            }
                        }
                        
                        Text(
                            text = result.playerName,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                    
                    Text(
                        text = "${if (result.score > 0) "+" else ""}${result.score}",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium,
                        color = when {
                            result.score > 0 -> MaterialTheme.colorScheme.error
                            result.score < 0 -> MaterialTheme.colorScheme.primary
                            else -> MaterialTheme.colorScheme.onSurface
                        }
                    )
                }
                
                if (result != sortedResults.last()) {
                    Spacer(modifier = Modifier.height(4.dp))
                }
            }
            
            // 特殊牌型提示
            if (round.explosionCount > 0 || round.hasTianWangZha) {
                Spacer(modifier = Modifier.height(8.dp))
                
                val specialCards = buildList {
                    if (round.explosionCount > 0) add("${round.explosionCount}炸")
                    if (round.hasTianWangZha) add("天王炸")
                }.joinToString(" + ")
                
                Text(
                    text = "特殊牌型: $specialCards",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}
