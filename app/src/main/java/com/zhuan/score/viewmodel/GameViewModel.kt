package com.zhuan.score.viewmodel

import android.app.Application
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.zhuan.score.data.GameDataStore
import com.zhuan.score.model.Family
import com.zhuan.score.model.GameRank
import com.zhuan.score.model.GameRound
import com.zhuan.score.model.Player
import com.zhuan.score.model.PlayerResult
import com.zhuan.score.model.PlayerSettlement
import com.zhuan.score.model.SettlementSettings
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.UUID

class GameViewModel(application: Application) : AndroidViewModel(application) {

    private val dataStore = GameDataStore(application)

    // 玩家列表
    private val _players = mutableStateListOf<Player>()
    val players: List<Player> get() = _players

    // 游戏记录
    private val _rounds = mutableStateListOf<GameRound>()
    val rounds: List<GameRound> get() = _rounds

    // 当前编辑的玩家名
    var newPlayerName = mutableStateOf("")
        private set

    // 当前游戏设置
    private val _currentRoundSettings = MutableStateFlow(RoundSettings())
    val currentRoundSettings: StateFlow<RoundSettings> = _currentRoundSettings.asStateFlow()

    // 结算设置
    private val _settlementSettings = MutableStateFlow(SettlementSettings())
    val settlementSettings: StateFlow<SettlementSettings> = _settlementSettings.asStateFlow()

    // 错误信息
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            dataStore.playersFlow.collect { loadedPlayers ->
                _players.clear()
                _players.addAll(loadedPlayers)
            }
        }
        viewModelScope.launch {
            dataStore.roundsFlow.collect { loadedRounds ->
                _rounds.clear()
                _rounds.addAll(loadedRounds)
            }
        }
    }

    /**
     * 添加玩家
     */
    fun addPlayer() {
        val name = newPlayerName.value.trim()
        if (name.isEmpty()) {
            _errorMessage.value = "请输入玩家姓名"
            return
        }
        if (_players.any { it.name == name }) {
            _errorMessage.value = "该玩家已存在"
            return
        }
        if (_players.size >= 10) {
            _errorMessage.value = "最多支持10个玩家"
            return
        }

        val newPlayer = Player(name = name)
        _players.add(newPlayer)
        newPlayerName.value = ""

        viewModelScope.launch {
            dataStore.savePlayers(_players.toList())
        }
    }

    /**
     * 删除玩家
     */
    fun removePlayer(playerId: String) {
        _players.removeAll { it.id == playerId }
        viewModelScope.launch {
            dataStore.savePlayers(_players.toList())
        }
    }

    /**
     * 更新玩家名
     */
    fun updateNewPlayerName(name: String) {
        newPlayerName.value = name
    }

    /**
     * 清除错误信息
     */
    fun clearError() {
        _errorMessage.value = null
    }

    /**
     * 设置玩家排名
     */
    fun setPlayerRank(playerId: String, rank: GameRank) {
        val currentSettings = _currentRoundSettings.value
        val selectedPlayers = getSelectedPlayers()
        
        // 设置当前玩家排名
        val newRankings = currentSettings.rankings.toMutableMap()
        newRankings[playerId] = rank
        
        // 如果已经设置了3个不同排名，自动为剩余玩家分配最后一个排名
        val uniqueRanks = newRankings.values.toSet()
        if (uniqueRanks.size == 3 && selectedPlayers.size == 4) {
            val allRanks = GameRank.values().toSet()
            val remainingRank = (allRanks - uniqueRanks).firstOrNull()
            if (remainingRank != null) {
                // 找到未设置排名的玩家
                val unsetPlayer = selectedPlayers.find { !newRankings.containsKey(it.id) || newRankings[it.id] == null }
                unsetPlayer?.let {
                    newRankings[it.id] = remainingRank
                }
            }
        }
        
        _currentRoundSettings.value = currentSettings.copy(rankings = newRankings)
    }

    /**
     * 设置玩家家族
     */
    fun setPlayerFamily(playerId: String, familyId: String) {
        val currentSettings = _currentRoundSettings.value
        val newFamilies = currentSettings.families.toMutableMap()
        newFamilies[playerId] = familyId
        _currentRoundSettings.value = currentSettings.copy(families = newFamilies)
    }

    /**
     * 切换玩家选择（用于选择本局上台的4人）
     */
    fun togglePlayerSelection(playerId: String) {
        val currentSettings = _currentRoundSettings.value
        val current = currentSettings.selectedPlayerIds.toMutableList()
        if (current.contains(playerId)) {
            // 取消选择时，同时清除该玩家的排名和家族
            current.remove(playerId)
            val newRankings = currentSettings.rankings.toMutableMap()
            val newFamilies = currentSettings.families.toMutableMap()
            newRankings.remove(playerId)
            newFamilies.remove(playerId)
            _currentRoundSettings.value = currentSettings.copy(
                selectedPlayerIds = current,
                rankings = newRankings,
                families = newFamilies
            )
        } else if (current.size < 4) {
            current.add(playerId)
            _currentRoundSettings.value = currentSettings.copy(selectedPlayerIds = current)
        }
    }

    /**
     * 设置炸的数量
     */
    fun setExplosionCount(count: Int) {
        _currentRoundSettings.value = _currentRoundSettings.value.copy(explosionCount = count)
    }

    /**
     * 设置是否有天王炸
     */
    fun setTianWangZha(has: Boolean) {
        _currentRoundSettings.value = _currentRoundSettings.value.copy(hasTianWangZha = has)
    }

    /**
     * 获取本局选中的玩家列表
     */
    fun getSelectedPlayers(): List<Player> {
        val selectedIds = _currentRoundSettings.value.selectedPlayerIds
        // 如果手动选择了玩家，返回选中的
        if (selectedIds.isNotEmpty()) {
            return _players.filter { selectedIds.contains(it.id) }
        }
        // 如果没有选择且总人数为4，自动返回所有玩家
        if (_players.size == 4) {
            return _players.toList()
        }
        return emptyList()
    }

    /**
     * 自动分配家族（随机配对）- 只针对选中的玩家
     */
    fun autoAssignFamilies() {
        val selectedPlayers = getSelectedPlayers()
        if (selectedPlayers.size != 4) {
            _errorMessage.value = "自动分配需要恰好选择4个玩家"
            return
        }

        val shuffled = selectedPlayers.shuffled()

        val newFamilies = _currentRoundSettings.value.families.toMutableMap()
        // 清除之前选中玩家的家族分配
        selectedPlayers.forEach { newFamilies.remove(it.id) }
        // 重新分配
        newFamilies[shuffled[0].id] = "family1"
        newFamilies[shuffled[1].id] = "family1"
        newFamilies[shuffled[2].id] = "family2"
        newFamilies[shuffled[3].id] = "family2"

        _currentRoundSettings.value = _currentRoundSettings.value.copy(families = newFamilies.toMap())
    }

    /**
     * 计算并保存本局游戏
     */
    fun calculateAndSaveRound() {
        val settings = _currentRoundSettings.value
        val selectedPlayers = getSelectedPlayers()

        // 验证数据 - 只针对选中的玩家
        if (selectedPlayers.size != 4) {
            _errorMessage.value = "请选择4个玩家进行游戏"
            return
        }
        if (settings.rankings.size != 4) {
            _errorMessage.value = "请为所有选中的玩家设置排名"
            return
        }
        if (settings.families.size != 4) {
            _errorMessage.value = "请为所有选中的玩家设置家族"
            return
        }

        // 检查是否每个排名都有且只有一个玩家（只检查选中玩家）
        val selectedPlayerIds = selectedPlayers.map { it.id }.toSet()
        val selectedRankings = settings.rankings.filterKeys { selectedPlayerIds.contains(it) }
        val rankCounts = selectedRankings.values.groupingBy { it }.eachCount()
        if (rankCounts.size != 4 || rankCounts.values.any { it != 1 }) {
            _errorMessage.value = "每个排名只能有一个玩家"
            return
        }

        // 检查是否每个家族恰好有2人（只检查选中玩家）
        val selectedFamilies = settings.families.filterKeys { selectedPlayerIds.contains(it) }
        val familyCounts = selectedFamilies.values.groupingBy { it }.eachCount()
        if (familyCounts.size != 2 || familyCounts.values.any { it != 2 }) {
            _errorMessage.value = "每个家族必须有2人"
            return
        }

        // 创建玩家结果 - 只包含选中的玩家
        val playerResults = selectedPlayers.map { player ->
            val rank = settings.rankings[player.id]!!
            val familyId = settings.families[player.id]!!
            PlayerResult(
                playerId = player.id,
                playerName = player.name,
                rank = rank,
                familyId = familyId,
                score = 0  // 临时，稍后计算
            )
        }

        // 创建游戏记录
        val round = GameRound(
            playerResults = playerResults,
            explosionCount = settings.explosionCount,
            hasTianWangZha = settings.hasTianWangZha
        )

        // 计算得分
        val actualScore = round.getActualScore()
        val familyScores = calculateFamilyScores(round, actualScore)

        // 更新玩家结果中的分数
        val finalResults = playerResults.map { result ->
            result.copy(score = familyScores[result.familyId] ?: 0)
        }

        val finalRound = round.copy(playerResults = finalResults)

        // 保存游戏记录
        _rounds.add(0, finalRound)
        viewModelScope.launch {
            dataStore.saveRounds(_rounds.toList())
        }

        // 更新玩家总分
        updatePlayerScores(finalResults)

        // 重置当前设置
        _currentRoundSettings.value = RoundSettings()
    }

    /**
     * 计算每个家族的得分
     */
    private fun calculateFamilyScores(round: GameRound, score: Int): Map<String, Int> {
        val sortedResults = round.playerResults.sortedBy { it.rank.rank }
        val firstFamily = sortedResults[0].familyId
        val secondFamily = sortedResults[1].familyId

        return if (firstFamily == secondFamily) {
            // 头游和二游同一家，赢
            mapOf(
                firstFamily to score,
                sortedResults[2].familyId to -score
            )
        } else if (firstFamily == sortedResults[2].familyId) {
            // 头游和三游同一家，赢
            mapOf(
                firstFamily to score,
                secondFamily to -score
            )
        } else {
            // 头游和末游同一家，赢
            mapOf(
                firstFamily to score,
                secondFamily to -score
            )
        }
    }

    /**
     * 更新玩家总分
     */
    private fun updatePlayerScores(results: List<PlayerResult>) {
        results.forEach { result ->
            val playerIndex = _players.indexOfFirst { it.id == result.playerId }
            if (playerIndex != -1) {
                _players[playerIndex] = _players[playerIndex].copy(
                    totalScore = _players[playerIndex].totalScore + result.score,
                    gamesPlayed = _players[playerIndex].gamesPlayed + 1
                )
            }
        }
        viewModelScope.launch {
            dataStore.savePlayers(_players.toList())
        }
    }

    /**
     * 删除游戏记录
     */
    fun deleteRound(roundId: String) {
        val round = _rounds.find { it.id == roundId }
        round?.let {
            // 回退玩家分数
            it.playerResults.forEach { result ->
                val playerIndex = _players.indexOfFirst { p -> p.id == result.playerId }
                if (playerIndex != -1) {
                    _players[playerIndex] = _players[playerIndex].copy(
                        totalScore = _players[playerIndex].totalScore - result.score,
                        gamesPlayed = _players[playerIndex].gamesPlayed - 1
                    )
                }
            }
            _rounds.removeAll { r -> r.id == roundId }

            viewModelScope.launch {
                dataStore.saveRounds(_rounds.toList())
                dataStore.savePlayers(_players.toList())
            }
        }
    }

    /**
     * 计算结算
     */
    fun calculateSettlement(rate: Int = 100): List<PlayerSettlement> {
        val sortedPlayers = _players.sortedByDescending { it.totalScore }
        return sortedPlayers.mapIndexed { index, player ->
            PlayerSettlement(
                playerId = player.id,
                playerName = player.name,
                totalScore = player.totalScore,
                amount = player.totalScore * rate,
                isTop = index == 0
            )
        }
    }

    /**
     * 更新结算分值
     */
    fun updateSettlementRate(rate: Int) {
        _settlementSettings.value = _settlementSettings.value.copy(scoreValue = rate)
    }

    /**
     * 重置所有数据
     */
    fun resetAll() {
        _players.clear()
        _rounds.clear()
        viewModelScope.launch {
            dataStore.clearAll()
        }
    }
}

/**
 * 单局游戏设置数据类
 */
data class RoundSettings(
    val selectedPlayerIds: List<String> = emptyList(),  // 新增：本局选中的玩家
    val rankings: Map<String, GameRank> = emptyMap(),  // playerId -> rank
    val families: Map<String, String> = emptyMap(),    // playerId -> familyId
    val explosionCount: Int = 0,
    val hasTianWangZha: Boolean = false
)
