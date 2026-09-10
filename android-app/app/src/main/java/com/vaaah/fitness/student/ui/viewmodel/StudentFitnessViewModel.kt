package com.vaaah.fitness.student.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.vaaah.fitness.student.data.model.StudentProfile
import com.vaaah.fitness.student.data.model.VaultStatus
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.math.roundToInt

data class StudentUiState(
    val profile: StudentProfile = StudentProfile(),
    val vault: VaultStatus = VaultStatus(walletBalance = 100.0, lockedPenaltyAmount = 0.0),
    val glassesDrunk: Int = 0,
    val targetGlasses: Int = 10,
    val workoutMinsDone: Int = 0,
    val isWorkoutCompleted: Boolean = false,
    val userMessage: String? = null,
    val isLoading: Boolean = false
)

class StudentFitnessViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(StudentUiState())
    val uiState: StateFlow<StudentUiState> = _uiState.asStateFlow()

    init {
        recalculateTargets()
    }

    private fun getTodayDateString(): String {
        return SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date())
    }

    /**
     * Study-safe calculation:
     * - Hydration: 35ml per kg of weight + 350ml study mental buffer.
     * - Exercise: 20 mins to prevent cognitive fatigue during exam/study periods.
     */
    fun recalculateTargets() {
        val p = _uiState.value.profile
        val heightM = p.heightCm / 100.0
        val bmi = (p.weightKg / (heightM * heightM) * 10.0).roundToInt() / 10.0

        val waterMl = (((p.weightKg * 35.0 + 350.0) / 50.0).roundToInt() * 50)
        val targetGlasses = (waterMl / 250.0).roundToInt().coerceAtLeast(6)
        val workoutMins = if (p.studyHoursPerDay >= 4.0) 20 else 25

        val bmr = 10.0 * p.weightKg + 6.25 * p.heightCm - 5.0 * p.age + 5.0
        val calories = (bmr * 1.35).roundToInt()

        val updatedProfile = p.copy(
            bmi = bmi,
            dailyWaterTargetMl = waterMl,
            dailyWorkoutTargetMins = workoutMins,
            maintenanceCalories = calories,
            studySafeRecommendation = "For ${p.studyHoursPerDay}h study, keep workouts to $workoutMins mins so focus & memory stay sharp without exhaustion."
        )

        _uiState.update { it.copy(profile = updatedProfile, targetGlasses = targetGlasses) }
    }

    fun updateMetrics(age: Int, weightKg: Double, heightCm: Double, studyHours: Double) {
        _uiState.update {
            it.copy(
                profile = it.profile.copy(
                    age = age,
                    weightKg = weightKg,
                    heightCm = heightCm,
                    studyHoursPerDay = studyHours
                )
            )
        }
        recalculateTargets()
        _uiState.update { it.copy(userMessage = "Student profile updated with study-safe targets!") }
    }

    fun logWaterGlass() {
        _uiState.update {
            val next = (it.glassesDrunk + 1).coerceAtMost(it.targetGlasses + 4)
            it.copy(
                glassesDrunk = next,
                userMessage = "Logged 250ml water! Total: ${next * 250}ml / ${it.profile.dailyWaterTargetMl}ml"
            )
        }
    }

    fun completeWorkout() {
        val target = _uiState.value.profile.dailyWorkoutTargetMins
        _uiState.update {
            it.copy(
                workoutMinsDone = target,
                isWorkoutCompleted = true,
                userMessage = "20-minute study break workout completed! Your study focus is primed & your ₹20 is SAFE!"
            )
        }
    }

    /**
     * ₹20 Commitment Vault Logic:
     * Missing daily workout requirement locks ₹20 into penalty vault.
     */
    fun simulateMissedWorkoutPenalty() {
        val currentVault = _uiState.value.vault
        if (currentVault.walletBalance < 20.0) {
            _uiState.update { it.copy(userMessage = "Insufficient balance to penalize.") }
            return
        }

        val nextVault = currentVault.copy(
            walletBalance = currentVault.walletBalance - 20.0,
            lockedPenaltyAmount = currentVault.lockedPenaltyAmount + 20.0,
            totalPenalized = currentVault.totalPenalized + 20.0,
            canRedeem = true
        )

        _uiState.update {
            it.copy(
                vault = nextVault,
                isWorkoutCompleted = false,
                workoutMinsDone = 0,
                userMessage = "Daily workout missed! ₹20 moved to Locked Penalty Vault. Complete makeup workout to redeem!"
            )
        }
    }

    /**
     * Money-Back Refund Logic:
     * Performing required makeup workout unlocks the ₹20 penalty and refunds it to active wallet.
     */
    fun redeemPenaltyRefund() {
        val currentVault = _uiState.value.vault
        if (currentVault.lockedPenaltyAmount < 20.0) {
            _uiState.update { it.copy(userMessage = "No locked penalties available to redeem.") }
            return
        }

        val nextVault = currentVault.copy(
            walletBalance = currentVault.walletBalance + 20.0,
            lockedPenaltyAmount = currentVault.lockedPenaltyAmount - 20.0,
            totalRefunded = currentVault.totalRefunded + 20.0,
            canRedeem = (currentVault.lockedPenaltyAmount - 20.0) >= 20.0
        )

        _uiState.update {
            it.copy(
                vault = nextVault,
                isWorkoutCompleted = true,
                workoutMinsDone = it.profile.dailyWorkoutTargetMins,
                userMessage = "Great job! Makeup workout completed. ₹20 has been refunded back to your wallet!"
            )
        }
    }

    fun clearUserMessage() {
        _uiState.update { it.copy(userMessage = null) }
    }
}
