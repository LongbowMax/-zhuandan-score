package com.zhuan.score.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.zhuan.score.model.GameRound
import com.zhuan.score.model.Player
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "zhuandan_prefs")

class GameDataStore(private val context: Context) {
    
    private val gson = Gson()
    
    companion object {
        private val PLAYERS_KEY = stringPreferencesKey("players")
        private val ROUNDS_KEY = stringPreferencesKey("rounds")
        private val NEXT_GAME_ID_KEY = intPreferencesKey("next_game_id")
    }
    
    /**
     * 获取所有玩家
     */
    val playersFlow: Flow<List<Player>> = context.dataStore.data
        .map { preferences ->
            val playersJson = preferences[PLAYERS_KEY] ?: "[]"
            val type = object : TypeToken<List<Player>>() {}.type
            gson.fromJson(playersJson, type) ?: emptyList()
        }
    
    /**
     * 保存玩家列表
     */
    suspend fun savePlayers(players: List<Player>) {
        context.dataStore.edit { preferences ->
            preferences[PLAYERS_KEY] = gson.toJson(players)
        }
    }
    
    /**
     * 获取所有游戏记录
     */
    val roundsFlow: Flow<List<GameRound>> = context.dataStore.data
        .map { preferences ->
            val roundsJson = preferences[ROUNDS_KEY] ?: "[]"
            val type = object : TypeToken<List<GameRound>>() {}.type
            gson.fromJson(roundsJson, type) ?: emptyList()
        }
    
    /**
     * 保存游戏记录
     */
    suspend fun saveRounds(rounds: List<GameRound>) {
        context.dataStore.edit { preferences ->
            preferences[ROUNDS_KEY] = gson.toJson(rounds)
        }
    }
    
    /**
     * 添加一局游戏
     */
    suspend fun addRound(round: GameRound) {
        val currentRounds = roundsFlow.map { it.toMutableList() }
        currentRounds.collect { rounds ->
            rounds.add(0, round)  // 新记录放在最前面
            saveRounds(rounds)
        }
    }
    
    /**
     * 删除游戏记录
     */
    suspend fun deleteRound(roundId: String) {
        val currentRounds = roundsFlow.map { it.toMutableList() }
        currentRounds.collect { rounds ->
            rounds.removeAll { it.id == roundId }
            saveRounds(rounds)
        }
    }
    
    /**
     * 清空所有数据
     */
    suspend fun clearAll() {
        context.dataStore.edit { preferences ->
            preferences[PLAYERS_KEY] = "[]"
            preferences[ROUNDS_KEY] = "[]"
        }
    }
}
