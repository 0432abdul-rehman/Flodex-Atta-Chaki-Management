package com.flodex.attachaki.data

import java.time.LocalDate
import java.time.LocalDateTime

class FlodexRepository(private val db: AppDatabase) {
    data class Summary(
        val label: String,
        val wheat: Double,
        val flour: Double,
        val amount: Double,
        val unpaid: Double,
    )

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

    suspend fun addTransaction(
        customerId: Int,
        wheat: Double,
        flour: Double,
        amount: Double,
        paymentStatus: String,
        notes: String = "",
    ) {
        db.transactionDao().insert(
            TransactionEntity(
                customerId = customerId,
                txnDate = LocalDate.now().toString(),
                wheatWeight = wheat,
                flourWeight = flour,
                amount = amount,
                paymentStatus = paymentStatus,
                notes = notes,
            ),
        )
    }

    suspend fun findCustomer(query: String): CustomerEntity? = db.customerDao().findByQuery(query)

    suspend fun summary(period: String): Summary {
        val today = LocalDate.now()
        val start = when (period) {
            "weekly" -> today.minusDays(today.dayOfWeek.value.toLong() - 1)
            "monthly" -> today.withDayOfMonth(1)
            "all" -> LocalDate.of(2000, 1, 1)
            else -> today
        }
        val end = today

        return Summary(
            label = period.replaceFirstChar { it.uppercase() } + " summary",
            wheat = db.transactionDao().totalWheat(start.toString(), end.toString()),
            flour = db.transactionDao().totalFlour(start.toString(), end.toString()),
            amount = db.transactionDao().totalAmount(start.toString(), end.toString()),
            unpaid = db.transactionDao().totalUnpaid(),
        )
    }
}
