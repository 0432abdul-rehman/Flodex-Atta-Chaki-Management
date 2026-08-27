package com.flodex.attachaki.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query

@Dao
interface TransactionDao {
    @Insert
    suspend fun insert(transaction: TransactionEntity)

    @Query("SELECT * FROM transactions WHERE customerId = :customerId ORDER BY txnDate DESC, id DESC")
    suspend fun listByCustomer(customerId: Int): List<TransactionEntity>

    @Query(
        """
        SELECT COALESCE(SUM(wheatWeight),0) FROM transactions
        WHERE txnDate BETWEEN :startDate AND :endDate
        """
    )
    suspend fun totalWheat(startDate: String, endDate: String): Double

    @Query(
        """
        SELECT COALESCE(SUM(amount),0) FROM transactions
        WHERE txnDate BETWEEN :startDate AND :endDate
        """
    )
    suspend fun totalAmount(startDate: String, endDate: String): Double
}
