package com.vaaah.fitness.student.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class StudentProfile(
    val id: Int = 0,
    val userId: Int = 1,
    val age: Int = 19,
    val weightKg: Double = 64.0,
    val heightCm: Double = 172.0,
    val studyHoursPerDay: Double = 6.5,
    val dailyWaterTargetMl: Int = 2550,
    val dailyWorkoutTargetMins: Int = 20,
    val bmi: Double = 21.6,
    val maintenanceCalories: Int = 2180,
    val studySafeRecommendation: String = "Keep workout to 20 mins to protect study energy and cognitive stamina."
)

@Serializable
data class VaultStatus(
    val userId: Int = 1,
    val walletBalance: Double = 100.0,
    val lockedPenaltyAmount: Double = 0.0,
    val totalPenalized: Double = 0.0,
    val totalRefunded: Double = 0.0,
    val canRedeem: Boolean = false,
    val redemptionMessage: String = ""
)

@Serializable
data class StudentDailyLog(
    val id: Int = 0,
    val userId: Int = 1,
    val date: String,
    val workoutMinsCompleted: Int = 0,
    val waterMlCompleted: Int = 0,
    val status: String = "pending", // "pending", "completed", "missed", "redeemed"
    val penaltyCharged: Double = 0.0,
    val refunded: Double = 0.0
)

@Serializable
data class StudentProfilePayload(
    val age: Int,
    val weightKg: Double,
    val heightCm: Double,
    val studyHoursPerDay: Double
)

@Serializable
data class StudentDailyLogPayload(
    val date: String,
    val workoutMinsCompleted: Int,
    val waterMlCompleted: Int
)

@Serializable
data class RedeemPenaltyPayload(
    val date: String,
    val extraWorkoutMins: Int = 20
)

@Serializable
data class PenaltyCheckResponse(
    val penalized: Boolean,
    val amount: Double = 20.0,
    val message: String,
    val lockedPenalty: Double,
    val walletBalance: Double
)

@Serializable
data class RedeemResponse(
    val refunded: Boolean,
    val refundAmount: Double = 20.0,
    val message: String,
    val walletBalance: Double,
    val lockedPenaltyAmount: Double
)
