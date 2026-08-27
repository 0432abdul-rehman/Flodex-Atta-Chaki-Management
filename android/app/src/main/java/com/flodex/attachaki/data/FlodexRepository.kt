package com.flodex.attachaki.data

import java.time.LocalDateTime

class FlodexRepository(private val db: AppDatabase) {
    suspend fun addOrGetCustomer(name: String, phone: String, address: String): CustomerEntity {
        val existing = db.customerDao().findByPhone(phone)
        if (existing != null) return existing

        val customer = CustomerEntity(
            name = name,
            phone = phone,
            address = address,
            createdAt = LocalDateTime.now().toString(),
        )
        db.customerDao().insert(customer)
        return db.customerDao().findByPhone(phone) ?: customer
    }

    suspend fun addTransaction(customerId: Int, wheat: Double, flour: Double, amount: Double, paymentStatus: String) {
        db.transactionDao().insert(
            TransactionEntity(
                customerId = customerId,
                txnDate = java.time.LocalDate.now().toString(),
                wheatWeight = wheat,
                flourWeight = flour,
                amount = amount,
                paymentStatus = paymentStatus,
            ),
        )
    }

    suspend fun findCustomer(query: String): CustomerEntity? = db.customerDao().findByQuery(query)

    suspend fun todaySummary(): Pair<Double, Double> {
        val day = java.time.LocalDate.now().toString()
        return db.transactionDao().totalWheat(day, day) to db.transactionDao().totalAmount(day, day)
    }
}
