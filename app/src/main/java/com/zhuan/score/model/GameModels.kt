package com.zhuan.score.model

import java.util.UUID

/**
 * 玩家数据类
 */
data class Player(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    var totalScore: Int = 0,
    var gamesPlayed: Int = 0
) {
    fun copy(): Player {
        return Player(id, name, totalScore, gamesPlayed)
    }
}

/**
 * 游戏结果枚举
 */
enum class GameRank(val displayName: String, val rank: Int) {
    FIRST("头游", 1),
    SECOND("二游", 2),
    THIRD("三游", 3),
    LAST("末游", 4);
    
    companion object {
        fun fromRank(rank: Int): GameRank {
            return values().find { it.rank == rank } ?: LAST
        }
    }
}

/**
 * 单局游戏记录
 */
data class GameRound(
    val id: String = UUID.randomUUID().toString(),
    val timestamp: Long = System.currentTimeMillis(),
    val playerResults: List<PlayerResult>,
    val explosionCount: Int = 0,  // 炸的数量（6张以上）
    val hasTianWangZha: Boolean = false  // 是否有天王炸
) {
    /**
     * 计算本局总倍数
     */
    fun getMultiplier(): Int {
        var multiplier = 1
        // 普通炸（6张以上）
        repeat(explosionCount) {
            multiplier *= 2
        }
        // 天王炸
        if (hasTianWangZha) {
            multiplier *= 2
        }
        return multiplier
    }
    
    /**
     * 获取基础分数
     */
    fun getBaseScore(): Int {
        val sortedResults = playerResults.sortedBy { it.rank.rank }
        val firstPlayerFamily = sortedResults[0].familyId
        val secondPlayerFamily = sortedResults[1].familyId
        val thirdPlayerFamily = sortedResults[2].familyId
        val fourthPlayerFamily = sortedResults[3].familyId
        
        return when {
            // 头游+二游同一家 = 赢3分
            firstPlayerFamily == secondPlayerFamily -> 3
            // 头游+三游同一家 = 赢2分
            firstPlayerFamily == thirdPlayerFamily -> 2
            // 头游+末游同一家 = 赢1分
            firstPlayerFamily == fourthPlayerFamily -> 1
            else -> 0
        }
    }
    
    /**
     * 获取实际得分（考虑倍数）
     */
    fun getActualScore(): Int {
        return getBaseScore() * getMultiplier()
    }
}

/**
 * 玩家单局结果
 */
data class PlayerResult(
    val playerId: String,
    val playerName: String,
    val rank: GameRank,
    val familyId: String,  // 家族ID，同一家的人此值相同
    val score: Int  // 本局得分（正数为赢，负数为输）
)

/**
 * 家族（对家组合）
 */
data class Family(
    val id: String = UUID.randomUUID().toString(),
    val playerIds: List<String>,
    val playerNames: List<String>
) {
    fun containsPlayer(playerId: String): Boolean {
        return playerIds.contains(playerId)
    }
}

/**
 * 结算设置
 */
data class SettlementSettings(
    val scoreValue: Int = 100  // 1分对应的金额（元）
)

/**
 * 玩家结算结果
 */
data class PlayerSettlement(
    val playerId: String,
    val playerName: String,
    val totalScore: Int,
    val amount: Int,  // 正数为应收，负数为应付
    val isTop: Boolean = false  // 是否为第一名
)
