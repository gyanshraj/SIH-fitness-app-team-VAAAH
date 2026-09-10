package com.vaaah.fitness.student.data.network

import com.vaaah.fitness.student.data.model.*
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Query

interface StudentFitnessApi {

    @GET("api/student/profile")
    suspend fun getProfile(
        @Header("x-auth-token") token: String
    ): Response<StudentProfile>

    @POST("api/student/profile")
    suspend fun updateProfile(
        @Header("x-auth-token") token: String,
        @Body payload: StudentProfilePayload
    ): Response<StudentProfile>

    @GET("api/student/vault")
    suspend fun getVaultStatus(
        @Header("x-auth-token") token: String
    ): Response<VaultStatus>

    @GET("api/student/logs")
    suspend fun getLogs(
        @Header("x-auth-token") token: String
    ): Response<List<StudentDailyLog>>

    @POST("api/student/daily-log")
    suspend fun submitDailyLog(
        @Header("x-auth-token") token: String,
        @Body payload: StudentDailyLogPayload
    ): Response<StudentDailyLog>

    @POST("api/student/check-daily-penalty")
    suspend fun checkDailyPenalty(
        @Header("x-auth-token") token: String,
        @Query("date") date: String
    ): Response<PenaltyCheckResponse>

    @POST("api/student/redeem-penalty")
    suspend fun redeemPenalty(
        @Header("x-auth-token") token: String,
        @Body payload: RedeemPenaltyPayload
    ): Response<RedeemResponse>
}
