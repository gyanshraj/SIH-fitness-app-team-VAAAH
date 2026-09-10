package com.vaaah.fitness.student.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vaaah.fitness.student.ui.viewmodel.StudentFitnessViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StudentFitnessScreen(
    viewModel: StudentFitnessViewModel = remember { StudentFitnessViewModel() }
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(uiState.userMessage) {
        uiState.userMessage?.let { msg ->
            snackbarHostState.showSnackbar(msg)
            viewModel.clearUserMessage()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("EduFit: Student Health", fontWeight = FontWeight.Bold, fontSize = 20.sp)
                        Text(
                            "Study-Safe Exercise & ₹20 Vault",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surfaceColorAtElevation(3.dp)
                )
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {

            // 1. ₹20 Commitment Vault Card
            item {
                CommitmentVaultCard(
                    walletBalance = uiState.vault.walletBalance,
                    lockedPenalty = uiState.vault.lockedPenaltyAmount,
                    canRedeem = uiState.vault.canRedeem,
                    onRedeem = { viewModel.redeemPenaltyRefund() },
                    onSimulateMiss = { viewModel.simulateMissedWorkoutPenalty() }
                )
            }

            // 2. Student Profile & Weight Balance Card
            item {
                StudentProfileCard(
                    bmi = uiState.profile.bmi,
                    waterTargetMl = uiState.profile.dailyWaterTargetMl,
                    workoutTargetMins = uiState.profile.dailyWorkoutTargetMins,
                    calories = uiState.profile.maintenanceCalories,
                    recommendation = uiState.profile.studySafeRecommendation,
                    studyHours = uiState.profile.studyHoursPerDay,
                    weightKg = uiState.profile.weightKg
                )
            }

            // 3. Today's 20-Min Study-Break Workout Card
            item {
                StudyBreakWorkoutCard(
                    targetMins = uiState.profile.dailyWorkoutTargetMins,
                    isCompleted = uiState.isWorkoutCompleted,
                    onComplete = { viewModel.completeWorkout() }
                )
            }

            // 4. Hydration / Water Intake Card
            item {
                HydrationCard(
                    glassesDrunk = uiState.glassesDrunk,
                    targetGlasses = uiState.targetGlasses,
                    targetMl = uiState.profile.dailyWaterTargetMl,
                    onDrinkGlass = { viewModel.logWaterGlass() }
                )
            }
        }
    }
}

@Composable
fun CommitmentVaultCard(
    walletBalance: Double,
    lockedPenalty: Double,
    canRedeem: Boolean,
    onRedeem: () -> Unit,
    onSimulateMiss: () -> Unit
) {
    ElevatedCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.elevatedCardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.AccountBalanceWallet,
                        contentDescription = "Vault",
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("₹20 Commitment Vault", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                }
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = MaterialTheme.colorScheme.primaryContainer
                ) {
                    Text(
                        "Habit Staking",
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Wallet & Penalty balances
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Card(
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                ) {
                    Column(modifier = Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Active Wallet", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text(
                            "₹${walletBalance.toInt()}",
                            fontSize = 26.sp,
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF10B981)
                        )
                    }
                }

                Card(
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                ) {
                    Column(modifier = Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Locked Penalty", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text(
                            "₹${lockedPenalty.toInt()}",
                            fontSize = 26.sp,
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFFEF4444)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                "Missing your daily 20-min workout moves ₹20 to the Locked Vault. Complete the required makeup workout to get your ₹20 refunded!",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(14.dp))

            Button(
                onClick = onRedeem,
                enabled = canRedeem,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF10B981))
            ) {
                Icon(Icons.Default.Savings, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text(if (canRedeem) "Claim ₹20 Refund (Makeup Done)" else "No Penalties to Redeem (₹0)")
            }

            Spacer(modifier = Modifier.height(8.dp))

            OutlinedButton(
                onClick = onSimulateMiss,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.Gavel, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Test: Simulate Missed Day (-₹20 Penalty)")
            }
        }
    }
}

@Composable
fun StudentProfileCard(
    bmi: Double,
    waterTargetMl: Int,
    workoutTargetMins: Int,
    calories: Int,
    recommendation: String,
    studyHours: Double,
    weightKg: Double
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Person, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Student Health & Weight Balance", fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                MetricChip(label = "BMI", value = bmi.toString(), highlight = "Normal")
                MetricChip(label = "Exercise", value = "$workoutTargetMins m", highlight = "Study-Safe")
                MetricChip(label = "Water", value = "$waterTargetMl ml", highlight = "Hydrated")
                MetricChip(label = "Calories", value = "$calories", highlight = "Maintain")
            }

            Spacer(modifier = Modifier.height(12.dp))

            Surface(
                shape = RoundedCornerShape(12.dp),
                color = MaterialTheme.colorScheme.primary.copy(alpha = 0.08.toFloat())
            ) {
                Text(
                    text = recommendation,
                    fontSize = 12.sp,
                    lineHeight = 16.sp,
                    modifier = Modifier.padding(12.dp),
                    color = MaterialTheme.colorScheme.onSurface
                )
            }
        }
    }
}

@Composable
fun MetricChip(label: String, value: String, highlight: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, fontWeight = FontWeight.Bold, fontSize = 16.sp, color = MaterialTheme.colorScheme.primary)
        Text(label, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(highlight, fontSize = 10.sp, color = Color(0xFF10B981), fontWeight = FontWeight.Medium)
    }
}

@Composable
fun StudyBreakWorkoutCard(
    targetMins: Int,
    isCompleted: Boolean,
    onComplete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Timer, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Daily Study Workout ($targetMins Mins)", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                }
                Text(
                    text = if (isCompleted) "✅ Completed" else "⏳ Pending",
                    color = if (isCompleted) Color(0xFF10B981) else Color(0xFFF59E0B),
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp
                )
            }

            Spacer(modifier = Modifier.height(8.dp))
            Text(
                "3 Micro-routines tailored to prevent desk fatigue and safeguard your ₹20 deposit:",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(10.dp))

            RoutineRow("1. Neck & Upper Back Relief", "Relieves study hunch", "5m")
            RoutineRow("2. Brisk Walk / Step Movement", "Sends oxygen to brain", "10m")
            RoutineRow("3. Core Plank & Hamstring Stretch", "Maintains posture strength", "5m")

            Spacer(modifier = Modifier.height(14.dp))

            Button(
                onClick = onComplete,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isCompleted) Color(0xFF10B981) else MaterialTheme.colorScheme.primary
                )
            ) {
                Icon(if (isCompleted) Icons.Default.CheckCircle else Icons.Default.FitnessCenter, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text(if (isCompleted) "Requirement Fulfilled (₹20 Protected!)" else "Complete 20 Mins & Protect ₹20")
            }
        }
    }
}

@Composable
fun RoutineRow(name: String, subtitle: String, duration: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(name, fontSize = 13.sp, fontWeight = FontWeight.Medium)
            Text(subtitle, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        Surface(
            shape = RoundedCornerShape(6.dp),
            color = MaterialTheme.colorScheme.primary.copy(alpha = 0.15.toFloat())
        ) {
            Text(
                duration,
                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
fun HydrationCard(
    glassesDrunk: Int,
    targetGlasses: Int,
    targetMl: Int,
    onDrinkGlass: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.WaterDrop, contentDescription = null, tint = Color(0xFF38BDF8))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Study Hydration Tracker", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                }
                Text(
                    "$glassesDrunk / $targetGlasses Glasses",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF38BDF8)
                )
            }

            Spacer(modifier = Modifier.height(8.dp))
            val progress = (glassesDrunk.toFloat() / targetGlasses.toFloat()).coerceIn(0f, 1f)
            LinearProgressIndicator(
                progress = { progress },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp))
            )

            Spacer(modifier = Modifier.height(12.dp))

            Button(
                onClick = onDrinkGlass,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF0284C7))
            ) {
                Icon(Icons.Default.LocalDrink, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Drink 1 Glass (250ml) During Study Break")
            }
        }
    }
}
